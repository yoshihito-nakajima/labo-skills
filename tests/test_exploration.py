"""Synthetic exploration fixtures; report strings here certify no mathematics."""

import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from labo_tools import exploration as e
from labo_tools.evidence import snapshot


class ExplorationTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.plan = self.put("research/example/plan.md", "---\ntitle: Synthetic\nsummary: Synthetic exploration\nstatus: in_progress\n---\nPRIVATE PLAN BODY\n")
        self.path = self.root / "research/example/exploration/tree.json"

    def put(self, name, text):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return path

    def dump(self, name, data):
        return self.put(name, yaml.safe_dump(data, sort_keys=False))

    def init(self, **kwargs):
        return e.initialize(self.root, "example", **kwargs)

    def add(self, key="route", **kwargs):
        values = dict(id=key, kind="category", title="Synthetic route", summary="A scoped question.", next="Inspect the assumptions.")
        values.update(kwargs)
        return e.add(self.root, "example", **values)

    def update(self, key="route", revision=1, **kwargs):
        return e.update(self.root, "example", key, expect_revision=revision, **kwargs)

    def inspect(self, **kwargs):
        return e.inspect(self.root, "example", **kwargs)

    def cli(self, *args):
        return subprocess.run([sys.executable, "-I", str(ROOT / "scripts/labo.py"), "research", "exploration", *args,
                               "--research", "example", "--workspace", str(self.root), "--format", "json"],
                              cwd="/tmp", capture_output=True, text=True)

    def formal_fixture(self, *, status="verified-formally", review_kind="formal", local=False):
        project = "lean/synthetic"
        self.put(f"{project}/Main.lean", "-- Synthetic source; no actual mathematical assertion.\n")
        self.put(f"{project}/lean-toolchain", "leanprover/lean4:v4.19.0\n")
        self.put(f"{project}/lakefile.toml", 'name = "synthetic"\n')
        self.put(f"{project}/lake-manifest.json", json.dumps({"packages": [{"name": "local", "type": "path", "dir": "../shared"}] if local else []}))
        if local:
            self.put("lean/shared/lake-manifest.json", '{"packages": []}')
            self.put("lean/shared/Shared.lean", "-- Synthetic local dependency.\n")
        kernel = self.put("research/example/kernel.md", "Fictional kernel fixture; no Lean execution.\n")
        alignment = self.put("research/example/alignment.md", "Fictional alignment fixture; no actual proof review.\n")
        claim = {"statement": "Synthetic claim fixture.", "status": status,
                 "evidence": ["research/example/kernel.md"], "dependencies": [],
                 "formal": {"project": project, "source": f"{project}/Main.lean", "declaration": "Synthetic.result",
                            "kernel": {"verdict": "pass", "report": kernel.relative_to(self.root).as_posix()},
                            "alignment": {"verdict": "pass", "report": alignment.relative_to(self.root).as_posix()}}}
        self.dump("research/example/claims.yaml", {"schema_version": 1, "claims": {"result": claim}})
        self.review(review_kind)
        return claim

    def review(self, kind="formal", *, trees=None, verdict="pass", empty=False):
        record = snapshot(self.root, kind=kind, catalog="research/example/claims.yaml", claim_ids=["result"], trees=trees)
        report = self.put(f"research/example/reviews/{kind}.md", "" if empty else "Synthetic report fixture, not a real review.\n")
        record.update(verdict=verdict, reviewer="Synthetic fixture reviewer", reviewed_at="2026-11-02",
                      report=report.relative_to(self.root).as_posix(), report_sha256=hashlib.sha256(report.read_bytes()).hexdigest())
        self.dump(f"research/example/reviews/{kind}.yaml", record)

    def test_unadopted_reads_do_not_create_or_migrate(self):
        before = self.plan.read_bytes()
        for action in ("tree", "check"):
            self.assertEqual(self.inspect(action=action)["adoption"], "not_enabled")
        self.assertFalse(self.path.parent.exists())
        self.assertEqual(self.plan.read_bytes(), before)

    def test_layout_migration_preserves_legacy_bytes_and_reuses_current_task(self):
        self.put("research/example/claims.yaml", "schema_version: 1\nclaims: {}\n# Preserve historical catalog\n")
        self.put("research/example/proof.md", "Historical proof and [existing link](source.md).\r\n")
        original = {path: path.read_bytes() for path in self.plan.parent.iterdir() if path.is_file()}
        for _ in range(2):
            self.init(if_missing=True)
            current = self.inspect()
            if "current-task" not in {node["id"] for node in current["nodes"]}:
                self.add("current-task", kind="task")
        self.assertEqual(self.inspect()["total"], 1)
        self.assertEqual(self.inspect()["revision"], 1)
        for path, content in original.items():
            self.assertEqual(path.read_bytes(), content)

    def test_if_missing_preserves_existing_parallel_settings_and_invalid_tree(self):
        self.init(mode="parallel", integrator="lead", max_workers=3)
        self.add(actor="lead", owner="a")
        frozen = self.path.read_bytes()
        reused = self.init(if_missing=True)
        self.assertEqual(reused["settings"], {"mode": "parallel", "integrator": "lead", "max_workers": 3})
        self.assertEqual(self.path.read_bytes(), frozen)
        self.path.write_text("{invalid json}")
        with self.assertRaises(e.ExplorationError):
            self.init(if_missing=True)
        self.assertEqual(self.path.read_text(), "{invalid json}")

    def test_concurrent_if_missing_initializers_preserve_existing_nodes(self):
        command = [sys.executable, "-I", str(ROOT / "scripts/labo.py"), "research", "exploration", "init",
                   "--if-missing", "--research", "example", "--workspace", str(self.root)]
        for round_number in range(2):
            frozen = self.path.read_bytes() if self.path.exists() else None
            processes = [subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True) for _ in range(8)]
            for process in processes:
                _, stderr = process.communicate(timeout=20)
                self.assertEqual(process.returncode, 0, stderr)
            if frozen is not None:
                self.assertEqual(self.path.read_bytes(), frozen)
            if round_number == 0:
                self.add("current-task", kind="task")
        self.assertEqual(self.inspect()["total"], 1)

    def test_deterministic_subtrees_and_counts_include_hidden_nodes(self):
        self.init()
        self.add("z-root")
        self.add("a-root")
        self.add("child", parent="a-root", state="blocked")
        self.add("grandchild", parent="child", state="done")
        all_nodes = self.inspect()
        self.assertEqual([n["id"] for n in all_nodes["nodes"]], ["a-root", "child", "grandchild", "z-root"])
        subtree = self.inspect(node_id="a-root", depth=0)
        self.assertEqual(subtree["total"], 3)
        self.assertEqual(subtree["visible"], 1)
        self.assertEqual(subtree["counts"]["done"], 1)
        self.assertEqual(self.inspect(node_id="child")["nodes"][0]["depth"], 0)

    def test_tree_and_metadata_show_never_read_detail_or_claim_bodies(self):
        self.init()
        self.add(kind="theorem", record="research/example/absent.md", claim_refs=["research/example/absent.yaml#claim"])
        with patch("labo_tools.exploration_evidence.guarantee", side_effect=AssertionError("expensive evidence read")):
            self.assertEqual(self.inspect()["nodes"][0]["guarantee"]["state"], "not_checked")
            self.inspect(action="show", node_id="route")
        self.assertEqual(self.inspect(action="check")["status"], "error")

    def test_show_details_selects_only_the_record(self):
        self.init()
        self.put("research/example/note.md", "SELECTED DETAIL\n")
        self.add(record="research/example/note.md")
        result = self.inspect(action="show", node_id="route", details=True)
        self.assertEqual(result["details"], "SELECTED DETAIL\n")
        self.assertNotIn("PRIVATE PLAN BODY", json.dumps(result))

    def test_stale_update_and_invalid_hierarchy_preserve_bytes(self):
        self.init()
        self.add()
        self.add("child", parent="route")
        self.update(summary="New scoped evidence.")
        frozen = self.path.read_bytes()
        for changes in ({"summary": "Stale overwrite."}, {"parent": "child"}, {"parent": "absent"}):
            with self.assertRaises(e.ExplorationError):
                self.update(revision=1 if "summary" in changes else 2, **changes)
            self.assertEqual(self.path.read_bytes(), frozen)

    def test_failed_atomic_replace_preserves_old_tree(self):
        self.init()
        self.add()
        frozen = self.path.read_bytes()
        with patch("labo_tools.exploration.os.replace", side_effect=OSError("synthetic write failure")):
            with self.assertRaises(OSError):
                self.update(summary="Should not persist.")
        self.assertEqual(self.path.read_bytes(), frozen)
        self.assertEqual(list(self.path.parent.glob(".tree-*.tmp")), [])

    def test_parallel_ownership_workers_children_and_active_bound(self):
        self.init(mode="parallel", integrator="lead", max_workers=1)
        self.add(actor="lead", owner="a")
        self.add("other", actor="lead", owner="b")
        self.update(actor="a", state="active")
        self.add("child", actor="a", owner="a", parent="route", state="active")
        frozen = self.path.read_bytes()
        for fn in (lambda: self.update(actor="b", revision=2, summary="Wrong owner."),
                   lambda: self.update("other", actor="b", state="active"),
                   lambda: self.update(actor="a", revision=2, owner="b"),
                   lambda: self.add("root", actor="a", owner="a")):
            with self.assertRaises(e.ExplorationError):
                fn()
            self.assertEqual(self.path.read_bytes(), frozen)

    def test_configuration_switch_retains_nodes_and_requires_owned_parallel_nodes(self):
        self.init()
        self.add()
        with self.assertRaises(e.ExplorationError):
            e.configure(self.root, "example", actor="primary", expect_revision=1, mode="parallel")
        self.update(owner="a")
        data = e.configure(self.root, "example", actor="primary", expect_revision=2, mode="parallel")
        self.assertEqual(data["nodes"][0]["id"], "route")
        with self.assertRaises(e.ExplorationError):
            e.configure(self.root, "example", actor="a", expect_revision=3, mode="sequential")

    def test_concurrent_process_additions_and_disjoint_updates_survive(self):
        self.init()
        def command(*args):
            return [sys.executable, "-I", str(ROOT / "scripts/labo.py"), "research", "exploration", *args,
                    "--research", "example", "--workspace", str(self.root)]
        processes = [subprocess.Popen(command("add", "--node", f"node-{key}", "--kind", "task", "--title", "Synthetic",
                                              "--summary", "Concurrent addition", "--next", "Inspect result"),
                                      stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True) for key in range(8)]
        for process in processes:
            _, stderr = process.communicate(timeout=20)
            self.assertEqual(process.returncode, 0, stderr)
        self.assertEqual(self.inspect()["total"], 8)
        processes = [subprocess.Popen(command("update", "--node", f"node-{key}", "--expect-revision", "1", "--state", "done"),
                                      stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True) for key in range(8)]
        for process in processes:
            _, stderr = process.communicate(timeout=20)
            self.assertEqual(process.returncode, 0, stderr)
        self.assertEqual(self.inspect()["counts"]["done"], 8)

    def test_cli_roundtrip_and_revision_error(self):
        self.assertEqual(self.cli("init").returncode, 0)
        result = self.cli("add", "--node", "question", "--kind", "question", "--title", "Question",
                          "--summary", "Open", "--next", "Investigate")
        self.assertEqual(result.returncode, 0, result.stderr)
        result = self.cli("update", "--node", "question", "--expect-revision", "0", "--state", "done")
        self.assertEqual(result.returncode, 2)
        self.assertIn("stale", result.stderr)
        result = self.cli("tree", "--depth", "0")
        self.assertEqual(json.loads(result.stdout)["nodes"][0]["id"], "question")

    def test_unsafe_paths_duplicate_json_and_malformed_types_are_rejected(self):
        self.init()
        for reference in ("../outside", "/absolute", "research//example/file", "research/example/../file", "C:/file"):
            with self.assertRaises(e.ExplorationError):
                self.add(record=reference)
        original = json.loads(self.path.read_text())
        for change in ({"settings": {"mode": [], "integrator": "a", "max_workers": 1}}, {"revision": True}):
            value = dict(original, **change)
            self.path.write_text(json.dumps(value))
            with self.assertRaises(e.ExplorationError):
                self.inspect()
        self.path.write_text('{"schema_version":1,"schema_version":1}')
        with self.assertRaises(e.ExplorationError):
            self.inspect()

    def test_symlinked_paths_never_escape_workspace(self):
        self.init()
        self.add()
        external = self.put("outside.md", "Outside.\n")
        link = self.root / "research/example/link.md"
        try:
            link.symlink_to(external)
        except OSError:
            self.skipTest("symlinks unavailable")
        self.update(record="research/example/link.md")
        with self.assertRaises(e.ExplorationError):
            self.inspect(action="show", node_id="route", details=True)

    def test_empty_tree_has_no_proof_targets(self):
        self.init()
        result = self.inspect(with_evidence=True)
        self.assertEqual(result["proof_targets"], 0)
        self.assertEqual(result["nodes"], [])

    def test_proof_gate_rejects_empty_refs_unknown_claim_and_other_review_kinds(self):
        self.init()
        self.add(kind="theorem")
        with self.assertRaises(e.ExplorationError):
            self.update(state="done")
        self.formal_fixture(review_kind="proof")
        self.update(claim_refs=["research/example/claims.yaml#absent"])
        self.assertEqual(self.inspect(with_evidence=True)["nodes"][0]["guarantee"]["state"], "unregistered")
        self.update(revision=2, claim_refs=["research/example/claims.yaml#result"])
        with self.assertRaises(e.ExplorationError):
            self.update(revision=3, state="done")
        self.review("owner")
        with self.assertRaises(e.ExplorationError):
            self.update(revision=3, state="done")

    def test_current_formal_records_allow_done_and_changes_force_recheck(self):
        self.init()
        self.formal_fixture()
        self.add(kind="lemma", claim_refs=["research/example/claims.yaml#result"], state="done")
        self.assertEqual(self.inspect(action="check")["status"], "ok")
        self.put("lean/synthetic/NewModule.lean", "-- New module invalidates whole-project snapshot.\n")
        result = self.inspect(action="check")
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["guarantees"]["route"]["state"], "stale")
        self.assertEqual(self.inspect()["nodes"][0]["state"], "done")

    def test_non_theorem_proof_targets_and_mandatory_theorem_flag(self):
        self.init()
        self.add(kind="example", proof_required=True)
        with self.assertRaises(e.ExplorationError):
            self.update(state="done")
        with self.assertRaises(e.ExplorationError):
            self.add("bad", kind="lemma", proof_required=False)

    def test_formal_pending_failed_empty_and_unformalized_records(self):
        self.init()
        claim = self.formal_fixture(status="unverified")
        self.add(kind="theorem", claim_refs=["research/example/claims.yaml#result"])
        for kind, verdict, expected in (("kernel", "pending", "execution_pending"), ("alignment", "pending", "alignment_pending"), ("kernel", "fail", "failed")):
            changed = copy.deepcopy(claim)
            changed["formal"][kind]["verdict"] = verdict
            self.dump("research/example/claims.yaml", {"schema_version": 1, "claims": {"result": changed}})
            self.assertEqual(self.inspect(with_evidence=True)["nodes"][0]["guarantee"]["state"], expected)
        self.formal_fixture()
        self.put("research/example/kernel.md", " \n")
        self.assertEqual(self.inspect(with_evidence=True)["nodes"][0]["guarantee"]["state"], "invalid")
        self.put("research/example/kernel.md", "pass\n")
        self.assertEqual(self.inspect(with_evidence=True)["nodes"][0]["guarantee"]["state"], "invalid")

    def test_direct_review_required_for_claim_dependencies(self):
        self.init()
        claim = self.formal_fixture()
        main = copy.deepcopy(claim)
        main["dependencies"] = ["helper"]
        self.dump("research/example/claims.yaml", {"schema_version": 1, "claims": {"result": main, "helper": claim}})
        self.review()
        self.add(kind="theorem", claim_refs=["research/example/claims.yaml#result"])
        result = self.inspect(with_evidence=True)["nodes"][0]["guarantee"]
        self.assertEqual(result["state"], "review_pending")
        self.assertIn("helper", result["reasons"][0])

    def test_local_path_dependencies_need_explicit_current_tree_snapshot(self):
        self.init()
        self.formal_fixture(local=True)
        self.add(kind="theorem", claim_refs=["research/example/claims.yaml#result"])
        self.assertEqual(self.inspect(with_evidence=True)["nodes"][0]["guarantee"]["state"], "scope_pending")
        self.review(trees=["lean/shared"])
        self.update(state="done")
        self.put("lean/shared/Shared.lean", "-- Changed local dependency.\n")
        self.assertEqual(self.inspect(action="check")["guarantees"]["route"]["state"], "stale")


if __name__ == "__main__":
    unittest.main()
