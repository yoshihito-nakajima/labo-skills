"""Declared graph invariants on synthetic statements, not proof certificates."""

from copy import deepcopy
import hashlib
import itertools
import json
from pathlib import Path
import random
import subprocess
import sys
import tempfile
import unittest

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from labo_tools.dependencies import DependencyGraph, inspect_dependencies  # noqa: E402
from labo_tools.evidence import EvidenceError  # noqa: E402


def node(key, requires=(), references=()):
    return {"id": key, "kind": "lemma", "statement": f"Synthetic statement {key}.",
            "source": {"path": "research/example/source.md", "locator": f"Claim {key}"},
            "requires": list(requires), "references": list(references)}


def graph(*nodes):
    return {"schema_version": 1, "scope": "Synthetic selected argument.",
            "coverage": {"status": "partial", "note": "Synthetic declarations only."},
            "nodes": list(nodes)}


def example():
    return graph(node("conclusion", ["estimate"]), node("estimate", ["ambient", "uniform"]),
                 node("uniform", ["ambient"]), node("ambient", references=["conclusion"]),
                 node("unrelated"))


class DependencyAlgorithmTests(unittest.TestCase):
    def test_deterministic_sort_and_narrative_cycle(self):
        data = example()
        expected = ["ambient", "uniform", "estimate", "conclusion", "unrelated"]
        rng = random.Random(1729)
        for _ in range(25):
            rng.shuffle(data["nodes"])
            for item in data["nodes"]:
                rng.shuffle(item["requires"])
            analyzed = DependencyGraph(data).analyze()
            self.assertEqual(analyzed["topological_order"], expected)
            self.assertEqual(analyzed["status"], "ok")
            self.assertTrue(analyzed["order_complete"])
            self.assertEqual(analyzed["cyclic_nodes"], [])

    def test_cycles_have_actual_witnesses_and_separate_downstream_nodes(self):
        data = graph(node("a", ["b", "c"]), node("b", ["a"]), node("c", ["a"]),
                     node("d", ["a"]), node("e", ["d"]), node("free"),
                     node("g", ["h"]), node("h", ["g"]))
        result = DependencyGraph(data).analyze()
        self.assertEqual(result["topological_order"], ["free"])
        self.assertFalse(result["order_complete"])
        self.assertEqual(result["cyclic_components"], [["a", "b", "c"], ["g", "h"]])
        self.assertEqual(result["cycle_witnesses"], [["a", "b", "a"], ["g", "h", "g"]])
        self.assertEqual(result["cyclic_nodes"], ["a", "b", "c", "g", "h"])
        self.assertEqual(result["blocked_nodes"], ["d", "e"])

    def test_exhaustive_four_vertex_cycle_and_blocking_classification(self):
        keys = list("abcd")
        possible = [(a, b) for a in keys for b in keys if a != b]
        for flags in itertools.product((False, True), repeat=len(possible)):
            adjacency = {key: [] for key in keys}
            for (a, b), selected in zip(possible, flags):
                if selected:
                    adjacency[a].append(b)
            # Independent brute-force reachability gives cycle membership and
            # downstream blocking, including nodes absent from a chosen witness.
            reachable = {}
            for key in keys:
                seen, pending = set(), list(adjacency[key])
                while pending:
                    child = pending.pop()
                    if child not in seen:
                        seen.add(child)
                        pending.extend(adjacency[child])
                reachable[key] = seen
            cyclic = {key for key in keys if key in reachable[key]}
            blocked = {key for key in keys if key not in cyclic and reachable[key] & cyclic}
            result = DependencyGraph(graph(*(node(key, adjacency[key]) for key in keys))).analyze()
            self.assertEqual(set(result["cyclic_nodes"]), cyclic)
            self.assertEqual(set(result["blocked_nodes"]), blocked)
            self.assertEqual(set(result["topological_order"]), set(keys) - cyclic - blocked)
            positions = {key: index for index, key in enumerate(result["topological_order"])}
            for key in positions:
                for dependency in adjacency[key]:
                    self.assertLess(positions[dependency], positions[key])
            for witness in result["cycle_witnesses"]:
                self.assertEqual(witness[0], witness[-1])
                for a, b in zip(witness, witness[1:]):
                    self.assertIn(b, adjacency[a])

    def test_deep_chain_is_iterative(self):
        keys = [f"node-{index}" for index in range(2000)]
        data = graph(*(node(key, [] if index == 0 else [keys[index - 1]])
                       for index, key in enumerate(keys)))
        harness = DependencyGraph(data)
        self.assertEqual(harness.analyze()["topological_order"], keys)
        self.assertEqual(set(harness.closure([keys[-1]])), set(keys))
        self.assertEqual(set(harness.impact([keys[0]])), set(keys))

    def test_full_order_checks_missing_unknown_duplicates_and_each_edge(self):
        harness = DependencyGraph(example())
        good = ["unrelated", "ambient", "uniform", "estimate", "conclusion"]
        self.assertTrue(harness.check_order(good)["valid"])
        self.assertEqual(harness.check_order(good[:-1])["missing"], ["conclusion"])
        self.assertEqual(harness.check_order(good + ["ghost"])["unknown"], ["ghost"])
        self.assertEqual(harness.check_order(good + ["ambient"])["duplicates"], ["ambient"])
        bad = harness.check_order(["conclusion", "estimate", "uniform", "ambient", "unrelated"])
        self.assertFalse(bad["valid"])
        self.assertEqual(len(bad["violations"]), 4)

    def test_closure_and_impact_exclude_narrative_links(self):
        harness = DependencyGraph(example())
        self.assertEqual(harness.closure(["estimate"]), ["ambient", "estimate", "uniform"])
        self.assertEqual(harness.closure(["ambient"]), ["ambient"])
        self.assertEqual(harness.impact(["uniform"]), ["conclusion", "estimate", "uniform"])
        self.assertEqual(harness.impact(["unrelated"]), ["unrelated"])
        self.assertEqual(harness.closure(["estimate", "unrelated"]),
                         ["ambient", "estimate", "uniform", "unrelated"])
        for selection in ([], ["missing"], ["ambient", "ambient"]):
            with self.subTest(selection=selection), self.assertRaises(EvidenceError):
                harness.closure(selection)

    def test_empty_graph_is_structurally_valid_without_coverage_claim(self):
        harness = DependencyGraph(graph())
        self.assertEqual(harness.analyze()["topological_order"], [])
        self.assertTrue(harness.analyze()["order_complete"])
        self.assertTrue(harness.check_order([])["valid"])

    def test_schema_rejects_ambiguous_or_malformed_graphs(self):
        mutations = [
            lambda d: d.update(schema_version=True),
            lambda d: d.update(schema_version=2),
            lambda d: d.update(extra="unknown"),
            lambda d: d.update(scope=" "),
            lambda d: d.update(coverage="complete"),
            lambda d: d["coverage"].update(status="complete"),
            lambda d: d["coverage"].update(note=""),
            lambda d: d.update(nodes={}),
            lambda d: d["nodes"].append(deepcopy(d["nodes"][0])),
            lambda d: d["nodes"][0].update(id="Bad_ID"),
            lambda d: d["nodes"][0].update(id=True),
            lambda d: d["nodes"][0].update(kind=[]),
            lambda d: d["nodes"][0].update(kind="conjecture"),
            lambda d: d["nodes"][0].update(statement=""),
            lambda d: d["nodes"][0].update(unknown="field"),
            lambda d: d["nodes"][0].update(source={"path": "missing"}),
            lambda d: d["nodes"][0]["source"].update(locator=""),
            lambda d: d["nodes"][0].update(requires="estimate"),
            lambda d: d["nodes"][0].update(requires=["estimate", "estimate"]),
            lambda d: d["nodes"][0].update(requires=["ghost"]),
            lambda d: d["nodes"][0].update(requires=["conclusion"]),
            lambda d: d["nodes"][0].update(references=["conclusion"]),
            lambda d: d["nodes"][0].update(references=["ghost"]),
            lambda d: d["nodes"][0].update(references=["estimate"]),
        ]
        for index, mutation in enumerate(mutations):
            data = example()
            mutation(data)
            with self.subTest(mutation=index), self.assertRaises(EvidenceError):
                DependencyGraph(data)


class DependencyFileAndCliTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.workspace = self.root / "private workspace"
        self.workspace.mkdir()
        self.unrelated = self.root / "unrelated cwd"
        self.unrelated.mkdir()
        self.graph_name = "research/example/dependencies.yaml"
        self.source = self.put("research/example/source.md", "Synthetic source α → β.\n")
        self.dump(example())

    def put(self, name, text):
        path = self.workspace / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return path

    def dump(self, data):
        return self.put(self.graph_name, yaml.safe_dump(data, sort_keys=False))

    def cli(self, action, *args):
        return subprocess.run(
            [sys.executable, "-B", "-I", str(ROOT / "scripts/labo.py"), "dependencies", action,
             "--graph", self.graph_name, "--workspace", str(self.workspace), *args],
            cwd=self.unrelated, capture_output=True, text=True,
        )

    def inspect(self, **kwargs):
        return inspect_dependencies(self.workspace, graph=self.graph_name, **kwargs)

    def test_read_only_cli_sort_order_closure_impact_and_input_identity(self):
        before = {path: path.read_bytes() for path in self.workspace.rglob("*") if path.is_file()}
        for action, args in (("check", []), ("sort", []), ("closure", ["--node", "estimate"]),
                             ("impact", ["--node", "uniform"]),
                             ("order", sum((["--node", key] for key in
                                            ["ambient", "uniform", "estimate", "conclusion", "unrelated"]), []))):
            with self.subTest(action=action):
                process = self.cli(action, *args, "--format", "json")
                self.assertEqual(process.returncode, 0, process.stderr)
                result = json.loads(process.stdout)
                self.assertEqual(result["source_inputs"], {
                    "research/example/source.md": hashlib.sha256(self.source.read_bytes()).hexdigest(),
                })
                self.assertEqual(result["recorded_coverage"]["status"], "partial")
                self.assertEqual(result["reference_count"], 1)
                self.assertTrue(result["order_complete"])
        self.assertEqual(before, {path: path.read_bytes() for path in self.workspace.rglob("*") if path.is_file()})
        old_hash = self.inspect()["source_inputs"]
        self.source.write_text("Changed source; extraction needs reinspection.\n", encoding="utf-8")
        self.assertNotEqual(self.inspect()["source_inputs"], old_hash)
        self.assertEqual(self.inspect()["status"], "ok")  # No invented stale-review gate.

    def test_proposed_order_errors_return_one_and_readable_details(self):
        process = self.cli("order", "--node", "conclusion", "--node", "conclusion", "--node", "ghost")
        self.assertEqual(process.returncode, 1, process.stderr)
        self.assertIn("invalid", process.stdout)
        for diagnostic in ("missing:", "unknown:", "duplicates:"):
            self.assertIn(diagnostic, process.stdout)

    def test_global_cycle_and_unaffected_selection_have_distinct_completeness(self):
        data = example()
        data["nodes"] += [node("cycle-a", ["cycle-b"]), node("cycle-b", ["cycle-a"]),
                          node("blocked", ["cycle-a"])]
        self.dump(data)
        process = self.cli("closure", "--node", "estimate", "--format", "json")
        self.assertEqual(process.returncode, 1, process.stderr)
        result = json.loads(process.stdout)
        self.assertFalse(result["order_complete"])
        self.assertTrue(result["selection_order_complete"])
        self.assertEqual(result["selection_order"], ["ambient", "uniform", "estimate"])
        self.assertEqual(result["blocked_nodes"], ["blocked"])
        cyclic = self.inspect(action="closure", nodes=["blocked"])
        self.assertFalse(cyclic["selection_order_complete"])
        self.assertEqual(cyclic["included"], ["blocked", "cycle-a", "cycle-b"])
        process = self.cli("sort")
        self.assertIn("Partial topological order", process.stdout)
        self.assertIn("cycle-a -> cycle-b -> cycle-a", process.stdout)
        self.assertIn("Blocked downstream: blocked", process.stdout)

    def test_duplicate_keys_unsafe_yaml_bad_bytes_and_invalid_selection_fail_cleanly(self):
        valid = (self.workspace / self.graph_name).read_text(encoding="utf-8")
        malformed = [valid + "scope: duplicate\n", "!!python/object/apply:os.system ['false']",
                     "schema_version: 1\nscope: [\n", valid.replace("partial", "2000-99-99", 1)]
        for text in malformed:
            with self.subTest(text=text[:40]):
                self.put(self.graph_name, text)
                process = self.cli("check", "--format", "json")
                self.assertEqual(process.returncode, 2, process.stderr)
                self.assertIn("error:", process.stderr)
                self.assertNotIn("Traceback", process.stderr)
        self.dump(example())
        process = self.cli("impact", "--node", "ghost")
        self.assertEqual(process.returncode, 2, process.stderr)
        self.assertIn("unknown selected nodes", process.stderr)
        (self.workspace / self.graph_name).write_bytes(b"\xff")
        self.assertEqual(self.cli("check").returncode, 2)

    def test_source_existence_path_normalization_and_policy_boundary(self):
        for name in ("missing.md", "../outside.md", "/absolute.md", "C:/absolute.md",
                     "research/./example/source.md", "research\\example\\source.md"):
            with self.subTest(name=name):
                data = example()
                data["nodes"][0]["source"]["path"] = name
                self.dump(data)
                with self.assertRaises(EvidenceError):
                    self.inspect()
        self.dump(example())
        with self.assertRaises(EvidenceError):
            inspect_dependencies(self.workspace, graph="../outside.yaml")
        with self.assertRaises(EvidenceError):
            inspect_dependencies(ROOT, graph="skills/knowledge-dependencies/assets/example.yaml")

    def test_symlinked_graph_source_and_parent_rejected(self):
        link = self.workspace / "linked.md"
        try:
            link.symlink_to(self.source)
        except (OSError, NotImplementedError) as exc:
            self.skipTest(f"symlinks unavailable: {exc}")
        data = example()
        data["nodes"][0]["source"]["path"] = "linked.md"
        self.dump(data)
        with self.assertRaises(EvidenceError):
            self.inspect()
        self.dump(example())
        graph_link = self.workspace / "linked.yaml"
        graph_link.symlink_to(self.workspace / self.graph_name)
        with self.assertRaises(EvidenceError):
            inspect_dependencies(self.workspace, graph="linked.yaml")
        parent_link = self.workspace / "linked-dir"
        parent_link.symlink_to(self.source.parent, target_is_directory=True)
        data["nodes"][0]["source"]["path"] = "linked-dir/source.md"
        self.dump(data)
        with self.assertRaises(EvidenceError):
            self.inspect()

    def test_bundled_fixture_runs_after_only_workspace_path_adaptation(self):
        assets = ROOT / "skills/knowledge-dependencies/assets"
        self.put("research/example/example-source.md", (assets / "example-source.md").read_text(encoding="utf-8"))
        self.put(self.graph_name, (assets / "example.yaml").read_text(encoding="utf-8"))
        result = self.inspect()
        self.assertEqual(result["topological_order"], ["ambient", "uniform", "estimate", "conclusion"])
        self.assertEqual(self.inspect(action="closure", nodes=["estimate"])["included"],
                         ["ambient", "estimate", "uniform"])
        self.assertEqual(self.inspect(action="impact", nodes=["uniform"])["included"],
                         ["conclusion", "estimate", "uniform"])


if __name__ == "__main__":
    unittest.main()
