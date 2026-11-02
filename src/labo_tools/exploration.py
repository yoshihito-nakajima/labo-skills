"""Opt-in exploration metadata; classification is not a proof dependency graph."""

from __future__ import annotations

from collections import Counter
from contextlib import contextmanager
import json
import os
from pathlib import Path, PurePosixPath
import tempfile

from .locking import exclusive_lock
from .plans import SLUG, read_plan


class ExplorationError(ValueError):
    """Invalid exploration metadata, ownership, or stale revision."""


STATES = ("queued", "active", "blocked", "done", "parked")
KINDS = ("category", "question", "definition", "conjecture", "theorem", "lemma", "example", "task")
FIELDS = {"id", "parent", "kind", "title", "summary", "next", "state", "owner",
          "record", "claim_refs", "dependency_refs", "proof_required", "revision"}


def _text(value, label):
    if not isinstance(value, str) or not value.strip() or "\n" in value or "\r" in value:
        raise ExplorationError(f"{label} must be nonempty single-line text")
    return value


def _identifier(value):
    if not isinstance(value, str) or not SLUG.fullmatch(value):
        raise ExplorationError("IDs must use lowercase kebab-case")


def _integer(value, minimum=1):
    return type(value) is int and value >= minimum


def _relative(value, *, fragment=False):
    _text(value, "reference")
    path, marker, locator = value.partition("#")
    parts = PurePosixPath(path).parts
    if (not parts or path != PurePosixPath(path).as_posix() or "\\" in path
            or ":" in path or PurePosixPath(path).is_absolute()
            or any(part in {".", ".."} for part in parts)
            or (marker and (not fragment or not locator or "#" in locator))):
        raise ExplorationError(f"expected normalized workspace-relative path: {value}")
    return path


def _safe_path(workspace, relative):
    path = workspace
    for part in PurePosixPath(relative).parts:
        path = path / part
        if path.is_symlink():
            raise ExplorationError(f"symlinked exploration path is unsupported: {relative}")
    return path


def _paths(workspace, research):
    _identifier(research)
    program = _safe_path(workspace, f"research/{research}")
    if not program.is_dir():
        raise ExplorationError(f"unknown research program: {research}")
    folder = _safe_path(workspace, f"research/{research}/exploration")
    return folder, _safe_path(workspace, f"research/{research}/exploration/tree.json")


def validate(data):
    if (not isinstance(data, dict) or set(data) != {"schema_version", "revision", "settings", "nodes"}
            or type(data["schema_version"]) is not int or data["schema_version"] != 1
            or not _integer(data["revision"], 0)):
        raise ExplorationError("invalid exploration tree header (schema_version=1 required)")
    settings = data["settings"]
    if (not isinstance(settings, dict) or set(settings) != {"mode", "integrator", "max_workers"}
            or not isinstance(settings["mode"], str) or settings["mode"] not in {"sequential", "parallel"}
            or not _integer(settings["max_workers"])):
        raise ExplorationError("invalid settings: mode, integrator and positive max_workers required")
    _text(settings["integrator"], "integrator")
    if not isinstance(data["nodes"], list):
        raise ExplorationError("nodes must be a list")
    nodes = {}
    for node in data["nodes"]:
        if not isinstance(node, dict) or set(node) != FIELDS:
            raise ExplorationError("invalid node fields")
        _identifier(node["id"])
        if node["id"] in nodes:
            raise ExplorationError(f"duplicate node: {node['id']}")
        nodes[node["id"]] = node
        if node["parent"] is not None:
            _identifier(node["parent"])
        if (not isinstance(node["kind"], str) or node["kind"] not in KINDS
                or not isinstance(node["state"], str) or node["state"] not in STATES
                or not _integer(node["revision"])):
            raise ExplorationError(f"invalid kind/state/revision: {node['id']}")
        if (type(node["proof_required"]) is not bool
                or (node["kind"] in {"theorem", "lemma"} and not node["proof_required"])):
            raise ExplorationError("theorem/lemma nodes require proof_required=true; other nodes use a boolean")
        for key in ("title", "summary", "next"):
            _text(node[key], key)
        if node["owner"] is not None:
            _text(node["owner"], "owner")
        if node["record"] is not None:
            _relative(node["record"])
        for key in ("claim_refs", "dependency_refs"):
            refs = node[key]
            if not isinstance(refs, list) or any(not isinstance(ref, str) for ref in refs):
                raise ExplorationError(f"{key} must be a list of references")
            if len(set(refs)) != len(refs):
                raise ExplorationError(f"duplicate {key}")
            for ref in refs:
                _relative(ref, fragment=True)
        if settings["mode"] == "parallel" and node["owner"] is None:
            raise ExplorationError("parallel mode requires every node to have an owner")
    # Iterative parent walks support deep trees without Python recursion limits.
    visited = set()
    for start in sorted(nodes):
        trail = set()
        current = start
        while current is not None and current not in visited:
            if current not in nodes:
                raise ExplorationError(f"missing parent: {current}")
            if current in trail:
                raise ExplorationError(f"hierarchy cycle through: {current}")
            trail.add(current)
            current = nodes[current]["parent"]
        visited.update(trail)
    workers = {node["owner"] for node in nodes.values()
               if node["state"] == "active" and node["owner"] not in {None, settings["integrator"]}}
    if settings["mode"] == "parallel" and len(workers) > settings["max_workers"]:
        raise ExplorationError("active worker owners exceed max_workers")
    return data


def _unique_pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ExplorationError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _load(path):
    if not path.is_file():
        raise ExplorationError("exploration is not enabled; use research exploration init")
    try:
        return validate(json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=_unique_pairs))
    except (json.JSONDecodeError, TypeError) as exc:
        raise ExplorationError(f"invalid exploration JSON: {exc}") from exc


def _write(path, data):
    validate(data)
    fd, temporary = tempfile.mkstemp(prefix=".tree-", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(data, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


@contextmanager
def _transaction(workspace, research, *, create=False):
    folder, path = _paths(workspace, research)
    if create:
        read_plan(folder.parent)
        folder.mkdir(exist_ok=True)
    if not folder.is_dir():
        raise ExplorationError("exploration is not enabled; use research exploration init")
    lock = _safe_path(workspace, f"research/{research}/exploration/.lock")
    # Retain the lock inode; readers need no lock because tree.json is replaced atomically.
    with lock.open("a+b") as stream, exclusive_lock(stream):
        yield path


def initialize(workspace, research, *, mode="sequential", integrator="primary", max_workers=2,
               if_missing=False):
    with _transaction(workspace, research, create=True) as path:
        if path.exists():
            if if_missing:
                return _load(path)
            raise ExplorationError("exploration already enabled; use configure to change settings")
        data = {"schema_version": 1, "revision": 0,
                "settings": {"mode": mode, "integrator": integrator, "max_workers": max_workers},
                "nodes": []}
        _write(path, data)
        return data


def _authorize(data, actor, node=None):
    settings = data["settings"]
    if settings["mode"] == "sequential":
        return
    _text(actor, "actor in parallel mode")
    if actor != settings["integrator"] and (node is None or node["owner"] != actor):
        raise ExplorationError("actor must be the integrator or the node's recorded owner")


def add(workspace, research, *, actor=None, **fields):
    with _transaction(workspace, research) as path:
        data = _load(path)
        nodes = {node["id"]: node for node in data["nodes"]}
        if fields["id"] in nodes:
            raise ExplorationError(f"node already exists: {fields['id']}")
        parent = nodes.get(fields.get("parent"))
        _authorize(data, actor, parent)
        if data["settings"]["mode"] == "parallel" and actor != data["settings"]["integrator"]:
            if fields.get("owner") != actor:
                raise ExplorationError("workers may add only their own child nodes")
        node = dict(parent=None, state="queued", owner=None, record=None,
                    claim_refs=[], dependency_refs=[], proof_required=fields.get("kind") in {"theorem", "lemma"})
        node.update(fields, revision=1)
        data["nodes"].append(node)
        data["revision"] += 1
        validate(data)
        _completion_gate(workspace, research, node)
        _write(path, data)
        return {"revision": data["revision"], "node": node}


def update(workspace, research, node_id, *, expect_revision, actor=None, **changes):
    with _transaction(workspace, research) as path:
        data = _load(path)
        node = next((node for node in data["nodes"] if node["id"] == node_id), None)
        if node is None:
            raise ExplorationError(f"unknown node: {node_id}")
        _authorize(data, actor, node)
        if node["revision"] != expect_revision:
            raise ExplorationError(f"stale node revision: expected {expect_revision}, current {node['revision']}; reread before retry")
        if not changes or set(changes) - (FIELDS - {"id", "revision"}):
            raise ExplorationError("supply at least one editable node field")
        if data["settings"]["mode"] == "parallel" and actor != data["settings"]["integrator"]:
            if {"owner", "parent"} & changes.keys():
                raise ExplorationError("only the integrator may reassign owners or parents")
        if changes.get("kind") in {"theorem", "lemma"} and "proof_required" not in changes:
            changes["proof_required"] = True
        node.update(changes)
        node["revision"] += 1
        data["revision"] += 1
        validate(data)
        _completion_gate(workspace, research, node)
        _write(path, data)
        return {"revision": data["revision"], "node": node}


def configure(workspace, research, *, expect_revision, actor, **changes):
    with _transaction(workspace, research) as path:
        data = _load(path)
        if actor != data["settings"]["integrator"]:
            raise ExplorationError("only the current integrator may configure exploration")
        if data["revision"] != expect_revision:
            raise ExplorationError("stale tree revision; reread before retry")
        if not changes or set(changes) - {"mode", "integrator", "max_workers"}:
            raise ExplorationError("supply exploration settings to change")
        data["settings"].update(changes)
        data["revision"] += 1
        _write(path, data)
        return data


def _completion_gate(workspace, research, node):
    if node["state"] == "done" and node["proof_required"]:
        from .exploration_evidence import guarantee
        result = guarantee(workspace, research, [node])[node["id"]]
        if result["state"] != "current_records":
            raise ExplorationError(f"proof task cannot be done: {result['state']}; " + "; ".join(result["reasons"]))


def inspect(workspace, research, *, action="tree", node_id=None, depth=None, details=False, with_evidence=False):
    _, path = _paths(workspace, research)
    if not path.exists():
        if action in {"tree", "check"}:
            return {"schema_version": 1, "research": research, "adoption": "not_enabled", "nodes": []}
        raise ExplorationError("exploration is not enabled")
    data = _load(path)
    nodes = {node["id"]: node for node in data["nodes"]}
    if node_id is not None and node_id not in nodes:
        raise ExplorationError(f"unknown node: {node_id}")
    result = {"schema_version": 1, "research": research, "adoption": "enabled",
              "revision": data["revision"], "settings": data["settings"]}
    if action == "show":
        if node_id is None:
            raise ExplorationError("show requires a node")
        result["node"] = nodes[node_id]
        if with_evidence:
            from .exploration_evidence import guarantee
            result["node"] = dict(nodes[node_id], guarantee=guarantee(workspace, research, [nodes[node_id]])[node_id])
        if details:
            record = nodes[node_id]["record"]
            if record is None:
                raise ExplorationError("selected node has no detail record")
            source = _safe_path(workspace, record)
            if source.stat().st_size > 1_048_576:
                raise ExplorationError("detail record exceeds 1 MiB; read a selected passage directly")
            result["details"] = source.read_text(encoding="utf-8")
        return result
    if action == "check":
        issues = []
        for node in data["nodes"]:
            for ref in ([node["record"]] if node["record"] else []) + node["claim_refs"] + node["dependency_refs"]:
                target = _safe_path(workspace, _relative(ref, fragment=True))
                if not target.is_file():
                    issues.append(f"{node['id']}: missing referenced file: {ref}")
        from .exploration_evidence import guarantee
        guarantees = guarantee(workspace, research, data["nodes"])
        for node in data["nodes"]:
            if node["state"] == "done" and node["proof_required"] and guarantees[node["id"]]["state"] != "current_records":
                issues.append(f"{node['id']}: done proof task needs rechecking: {guarantees[node['id']]['state']}")
        result.update(status="error" if issues else "ok", node_count=len(nodes), issues=issues, guarantees=guarantees)
        return result
    if depth is not None and depth < 0:
        raise ExplorationError("depth must be at least 0")
    children = {}
    for node in data["nodes"]:
        children.setdefault(node["parent"], []).append(node["id"])
    roots = [node_id] if node_id else sorted(children.get(None, []))
    stack = [(key, 0) for key in reversed(roots)]
    selected = []
    subtree_nodes = []
    all_states = Counter()
    while stack:
        key, level = stack.pop()
        node = nodes[key]
        subtree_nodes.append(node)
        all_states[node["state"]] += 1
        if depth is None or level <= depth:
            selected.append(dict(node, depth=level))
        stack.extend((child, level + 1) for child in reversed(sorted(children.get(key, []))))
    result.update(nodes=selected, subtree=node_id, depth=depth,
                  counts={state: all_states[state] for state in STATES},
                  total=sum(all_states.values()), visible=len(selected))
    if with_evidence:
        from .exploration_evidence import guarantee
        guarantees = guarantee(workspace, research, subtree_nodes)
    else:
        guarantees = {node["id"]: {"state": "not_checked" if node["proof_required"] else "not_required", "reasons": []}
                      for node in subtree_nodes}
    result["evidence_checked"] = with_evidence
    result["proof_targets"] = sum(node["proof_required"] for node in subtree_nodes)
    result["guarantee_counts"] = dict(sorted(Counter(value["state"] for value in guarantees.values()).items()))
    result["nodes"] = [dict(node, guarantee=guarantees[node["id"]]) for node in selected]
    return result


def render(result):
    if result["adoption"] == "not_enabled":
        return f"research/{result['research']}: exploration not enabled"
    head = f"research/{result['research']} — {result['settings']['mode']} exploration; tree revision={result['revision']}"
    if "node" in result:
        node = result["node"]
        lines = [head, json.dumps(node, ensure_ascii=False, indent=2)]
        if "details" in result:
            lines.append(result["details"])
        return "\n".join(lines)
    if "issues" in result:
        return "\n".join([head, f"{result['status'].upper()}: {result['node_count']} nodes; structure and recorded formal-evidence freshness",
                          *(f"{key}: formal records={value['state']}" for key, value in result["guarantees"].items()), *result["issues"]])
    if "counts" not in result:
        return head
    lines = [head, f"Work states in selected subtree (all depths): {result['counts']}; visible={result['visible']}/{result['total']}",
             f"Proof targets: {result['proof_targets']}; formal record states (all depths): {result['guarantee_counts']}"]
    for node in result["nodes"]:
        indent = "  " * node["depth"]
        lines.extend([f"{indent}{node['id']} [{node['kind']}; {node['state']}; formal-records={node['guarantee']['state']}; owner={node['owner'] or '-'}; rev={node['revision']}] {node['title']}",
                      f"{indent}  {node['summary']}", f"{indent}  Next: {node['next']}"])
    lines.append("Formal record freshness is not mathematical certification; default tree does not inspect evidence.")
    return "\n".join(lines)
