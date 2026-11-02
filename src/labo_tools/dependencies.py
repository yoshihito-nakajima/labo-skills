"""Deterministic checks of an explicitly sourced mathematical dependency graph."""

from __future__ import annotations

from collections import deque
import heapq
from pathlib import Path

from .evidence import (
    EvidenceError, _digest_file, _load, _mapping, _path, _strings, _text, _workspace,
)
from .plans import PlanError, SLUG


NODE_KINDS = frozenset({"definition", "assumption", "construction", "lemma", "theorem", "external"})
LIMITS = (
    "Checks cover all declared requires edges; references do not constrain proof order.",
    "Source locations and coverage are author-supplied. Extraction completeness, locator accuracy, "
    "mathematical correctness, and applicability of cited results require source review.",
    "Source hashes identify current inputs; they do not establish a previous review or its freshness.",
)


class DependencyError(EvidenceError):
    """Malformed graph or invalid dependency query."""


def _ids(value: object, name: str) -> list[str]:
    items = _strings(value, name)
    if any(not SLUG.fullmatch(item) for item in items):
        raise DependencyError(f"{name} IDs must be lowercase kebab-case")
    return items


class DependencyGraph:
    def __init__(self, data: object):
        graph = _mapping(data, "graph", {"schema_version", "scope", "coverage", "nodes"})
        if type(graph["schema_version"]) is not int or graph["schema_version"] != 1:
            raise DependencyError("schema_version must be 1")
        self.scope = _text(graph["scope"], "scope")
        self.coverage = _mapping(graph["coverage"], "coverage", {"status", "note"})
        if self.coverage["status"] not in ("partial", "source-reviewed"):
            raise DependencyError("coverage.status must be partial or source-reviewed")
        _text(self.coverage["note"], "coverage.note")
        if not isinstance(graph["nodes"], list):
            raise DependencyError("nodes must be a list")
        self.nodes: dict[str, dict] = {}
        for index, raw in enumerate(graph["nodes"]):
            name = f"nodes[{index}]"
            node = _mapping(raw, name, {"id", "kind", "statement", "source", "requires"}, {"references"})
            key = _ids([node["id"]], name + ".id")[0]
            if key in self.nodes:
                raise DependencyError(f"duplicate node ID: {key}")
            if not isinstance(node["kind"], str) or node["kind"] not in NODE_KINDS:
                raise DependencyError(f"{name}.kind must be one of {', '.join(sorted(NODE_KINDS))}")
            _text(node["statement"], name + ".statement")
            source = _mapping(node["source"], name + ".source", {"path", "locator"})
            _text(source["path"], name + ".source.path")
            _text(source["locator"], name + ".source.locator")
            self.nodes[key] = dict(node, requires=_ids(node["requires"], name + ".requires"),
                                   references=_ids(node.get("references", []), name + ".references"))
        for key, node in self.nodes.items():
            for field in ("requires", "references"):
                for target in node[field]:
                    if target not in self.nodes:
                        raise DependencyError(f"{key}.{field} names missing node: {target}")
                    if target == key:
                        raise DependencyError(f"{key}.{field} contains a self edge")
            if set(node["requires"]) & set(node["references"]):
                raise DependencyError(f"{key}: an edge must be either requires or references")
        self.requires = {key: sorted(node["requires"]) for key, node in sorted(self.nodes.items())}
        self.dependents: dict[str, list[str]] = {key: [] for key in self.requires}
        for key, dependencies in self.requires.items():
            for dependency in dependencies:
                self.dependents[dependency].append(key)

    def _components(self) -> list[list[str]]:
        """Iterative Kosaraju: long proof chains must not exhaust Python's stack."""
        seen: set[str] = set()
        finished: list[str] = []
        for root in self.requires:
            if root in seen:
                continue
            seen.add(root)
            stack = [(root, iter(self.requires[root]))]
            while stack:
                key, children = stack[-1]
                child = next(children, None)
                if child is None:
                    finished.append(key)
                    stack.pop()
                elif child not in seen:
                    seen.add(child)
                    stack.append((child, iter(self.requires[child])))
        seen.clear()
        components = []
        for root in reversed(finished):
            if root in seen:
                continue
            seen.add(root)
            component = []
            pending = [root]
            while pending:
                key = pending.pop()
                component.append(key)
                for child in self.dependents[key]:
                    if child not in seen:
                        seen.add(child)
                        pending.append(child)
            if len(component) > 1:  # Self edges were rejected during validation.
                components.append(sorted(component))
        return sorted(components)

    def _cycle_witness(self, component: list[str]) -> list[str]:
        # Pick one dependency of the first vertex and find a return path inside
        # its strongly connected component. Every adjacent pair is a real edge.
        members = set(component)
        root = component[0]
        first = next(key for key in self.requires[root] if key in members)
        parents: dict[str, str | None] = {first: None}
        pending = deque([first])
        while pending:
            key = pending.popleft()
            if key == root:
                route = []
                current: str | None = root
                while current is not None:
                    route.append(current)
                    current = parents[current]
                return [root, *reversed(route)]
            for child in self.requires[key]:
                if child in members and child not in parents:
                    parents[child] = key
                    pending.append(child)
        raise AssertionError("strongly connected component has no return path")

    def analyze(self) -> dict:
        degree = {key: len(dependencies) for key, dependencies in self.requires.items()}
        ready = [key for key, count in degree.items() if count == 0]
        heapq.heapify(ready)
        order = []
        while ready:
            key = heapq.heappop(ready)
            order.append(key)
            for dependent in self.dependents[key]:
                degree[dependent] -= 1
                if degree[dependent] == 0:
                    heapq.heappush(ready, dependent)
        components = self._components()
        cyclic = {key for component in components for key in component}
        return {
            "status": "error" if components else "ok",
            "topological_order": order,
            "order_complete": len(order) == len(self.nodes),
            "cyclic_components": components,
            "cycle_witnesses": [self._cycle_witness(component) for component in components],
            "cyclic_nodes": sorted(cyclic),
            "blocked_nodes": sorted(key for key, count in degree.items() if count and key not in cyclic),
        }

    def check_order(self, proposed: list[str]) -> dict:
        if not isinstance(proposed, list) or any(not isinstance(key, str) for key in proposed):
            raise DependencyError("proposed order must be a list of node IDs")
        seen = set()
        duplicates = set()
        for key in proposed:
            if key in seen:
                duplicates.add(key)
            seen.add(key)
        positions = {key: index for index, key in enumerate(proposed)}
        violations = [
            {"node": key, "requires": dependency}
            for key, dependencies in self.requires.items() for dependency in dependencies
            if key in positions and dependency in positions and positions[dependency] >= positions[key]
        ]
        missing = sorted(set(self.nodes) - seen)
        unknown = sorted(seen - set(self.nodes))
        return {"valid": not (duplicates or missing or unknown or violations),
                "missing": missing, "unknown": unknown, "duplicates": sorted(duplicates),
                "violations": violations}

    def _reach(self, selected: list[str], adjacency: dict[str, list[str]]) -> list[str]:
        _ids(selected, "selection")
        if not selected:
            raise DependencyError("selection must contain at least one node ID")
        unknown = sorted(set(selected) - set(self.nodes))
        if unknown:
            raise DependencyError("unknown selected nodes: " + ", ".join(unknown))
        seen = set(selected)
        pending = list(selected)
        while pending:
            for key in adjacency[pending.pop()]:
                if key not in seen:
                    seen.add(key)
                    pending.append(key)
        return sorted(seen)

    def closure(self, targets: list[str]) -> list[str]:
        """Targets plus their transitive hard prerequisites."""
        return self._reach(targets, self.requires)

    def impact(self, changed: list[str]) -> list[str]:
        """Changed nodes plus all declared hard dependents requiring reinspection."""
        return self._reach(changed, self.dependents)


def inspect_dependencies(workspace: Path, *, graph: str, action: str = "check",
                         nodes: list[str] | None = None) -> dict:
    root = _workspace(workspace)
    graph_path = _path(root, graph)
    try:
        dependency_graph = DependencyGraph(_load(graph_path))
    except PlanError as exc:  # Shared YAML loader rejects duplicate keys.
        raise DependencyError(f"invalid dependency YAML: {exc}") from exc
    source_inputs = {}
    for node in dependency_graph.nodes.values():
        name = node["source"]["path"]
        if name not in source_inputs:
            source_inputs[name] = _digest_file(_path(root, name))
    result = {
        "schema_version": 1, "graph": graph, "graph_sha256": _digest_file(graph_path),
        "scope": dependency_graph.scope, "recorded_coverage": dependency_graph.coverage,
        "source_inputs": dict(sorted(source_inputs.items())),
        "node_count": len(dependency_graph.nodes),
        "requires_count": sum(len(items) for items in dependency_graph.requires.values()),
        "reference_count": sum(len(node["references"]) for node in dependency_graph.nodes.values()),
        **dependency_graph.analyze(), "limits": list(LIMITS),
    }
    selected = nodes if nodes is not None else []
    if action == "order":
        result["proposed_order"] = selected
        result["order_check"] = dependency_graph.check_order(selected)
        if not result["order_check"]["valid"]:
            result["status"] = "error"
    elif action in {"closure", "impact"}:
        included = dependency_graph.closure(selected) if action == "closure" else dependency_graph.impact(selected)
        result["selected"] = sorted(selected)
        result["included"] = included
        included_set = set(included)
        result["selection_order"] = [key for key in result["topological_order"] if key in included_set]
        result["selection_order_complete"] = len(result["selection_order"]) == len(included)
    elif action not in {"check", "sort"}:
        raise DependencyError(f"unknown dependency action: {action}")
    return result
