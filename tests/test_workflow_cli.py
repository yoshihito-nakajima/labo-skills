"""Black-box workflows on synthetic private fixtures, never review certificates."""

import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import yaml


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CATALOG = "research/example/claims.yaml"
MAIN = "writing/example/main.tex"
PART = "writing/example/part.tex"
SESSION = "research/example/reviews/first-reader.json"
SPOILER = "EXPLICIT_FUTURE_SPOILER_SENTINEL"


class WorkflowCliTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.workspace = self.root / "private workspace"
        self.workspace.mkdir()
        self.unrelated = self.root / "unrelated cwd"
        self.unrelated.mkdir()
        (self.workspace / "research/example/reviews").mkdir(parents=True)
        self.put(MAIN, "\\input{part}\n")
        self.put(PART, "Visible question.\nVisible relation α → β.\n" + SPOILER + "\n")

    def put(self, name, content):
        path = self.workspace / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8", newline="")
        return path

    def cli(self, *args, env=None):
        return subprocess.run(
            [sys.executable, "-B", "-I", str(PROJECT_ROOT / "scripts/labo.py"),
             *args, "--workspace", str(self.workspace)],
            cwd=self.unrelated, env=env, capture_output=True, text=True,
        )

    def expect(self, *args, code=0, env=None):
        result = self.cli(*args, env=env)
        self.assertEqual(result.returncode, code, result.stderr or result.stdout)
        self.assertNotIn("Traceback", result.stderr)
        return result.stdout

    def structured(self, *args, code=0, env=None):
        value = json.loads(self.expect(*args, "--format", "json", code=code, env=env))
        self.assertEqual(value["schema_version"], 1)
        return value

    def state(self):
        return {
            path.relative_to(self.workspace).as_posix(): path.read_bytes() if path.is_file() else None
            for path in self.workspace.rglob("*")
        }

    def catalog(self, *, formal=False):
        self.put("research/example/evidence.md", "Synthetic evidence fixture; not a checked proof.\n")
        claim = {"statement": "Synthetic claim, not a research result.", "status": "proved/agent",
                 "evidence": ["research/example/evidence.md"], "dependencies": []}
        if formal:
            self.put("lean/example/lean-toolchain", "leanprover/lean4:v4.19.0\n")
            self.put("lean/example/lakefile.toml", 'name = "example"\n')
            self.put("lean/example/lake-manifest.json", '{"packages": []}\n')
            self.put("lean/example/Example.lean", "theorem Example.ok : True := True.intro\n")
            claim["formal"] = {
                "project": "lean/example", "source": "lean/example/Example.lean",
                "declaration": "Example.ok", "kernel": {"verdict": "pending", "report": None},
                "alignment": {"verdict": "pending", "report": None},
            }
        self.put(CATALOG, yaml.safe_dump({"schema_version": 1, "claims": {"example-claim": claim}}))

    def record(self, name, *, verdict="pass", extra_file=None):
        args = ["evidence", "snapshot", "--kind", "proof", "--catalog", CATALOG,
                "--claim", "example-claim"]
        if extra_file is not None:
            args.extend(["--file", extra_file])
        captured = yaml.safe_load(self.expect(*args))
        report = f"research/example/reviews/{name}-report.md"
        path = self.put(report, f"Synthetic {name} report; no mathematical result established.\n")
        captured.update(verdict=verdict, reviewer="Synthetic fixture reviewer", reviewed_at="2026-01-01",
                        report=report, report_sha256=hashlib.sha256(path.read_bytes()).hexdigest())
        record = f"research/example/reviews/{name}.yaml"
        self.put(record, yaml.safe_dump(captured))
        return record

    def test_scope_text_json_selection_and_strict_warning_do_not_expand_inputs(self):
        captured = yaml.safe_load(self.expect("evidence", "snapshot", "--kind", "writing", "--file", MAIN))
        saved = "research/example/reviews/writing.yaml"
        self.put(saved, yaml.safe_dump(captured))
        before = self.state()
        discovery = self.structured("evidence", "scope", "--paper", "example")
        self.assertEqual(discovery["status"], "ok")
        self.assertEqual({item["path"] for item in discovery["dependencies"]}, {MAIN, PART})
        self.assertEqual(discovery["selection"]["mode"], "discovery")
        self.assertEqual(discovery["omitted"], [])
        selected = self.structured("evidence", "scope", "--source", MAIN, "--record", saved)
        self.assertEqual(selected["status"], "warning")
        self.assertEqual(selected["omitted"], [PART])
        strict = self.structured("evidence", "scope", "--source", MAIN, "--record", saved, "--strict", code=1)
        self.assertEqual(strict, selected)
        text = self.expect("evidence", "scope", "--source", MAIN, "--file", MAIN)
        self.assertIn("WARNING", text)
        self.assertIn("not covered by selected inputs: " + PART, text)
        self.assertIn("does not expand a snapshot", text)
        self.assertIn("limit: Literal, bounded diagnostics only", text)
        self.assertEqual(sum(line.startswith("limit:") for line in text.splitlines()), 1)
        self.assertLess(len(text.splitlines()), 20)
        self.assertNotIn(SPOILER, text)
        self.assertEqual(self.state(), before)

    def test_scope_missing_dependency_is_error_even_without_strict(self):
        self.put(MAIN, "\\input{missing}\n")
        before = self.state()
        value = self.structured("evidence", "scope", "--paper", "example", code=1)
        self.assertEqual(value["status"], "error")
        self.assertIn("missing-dependency", {issue["code"] for issue in value["issues"]})
        self.assertEqual(self.state(), before)

    def test_scope_can_select_workspace_root_build_convention(self):
        self.put(MAIN, "\\input{writing/example/part}\n")
        before = self.state()
        value = self.structured("evidence", "scope", "--source", MAIN,
                                "--compile-root", ".", "--file", MAIN, "--file", PART, "--strict")
        self.assertEqual(value["status"], "ok", value["issues"])
        self.assertEqual(value["compilation_root"], ".")
        self.assertEqual(value["omitted"], [])
        self.assertEqual(self.state(), before)

    def test_status_retains_current_stale_and_failed_records_and_strict_warnings(self):
        self.catalog()
        changed = "research/example/stale-extra.md"
        self.put(changed, "Original explicitly captured input.\n")
        current = self.record("current")
        stale = self.record("stale", extra_file=changed)
        failed = self.record("failed", verdict="fail")
        self.put(changed, "Changed after synthetic review fixture was captured.\n")
        before = self.state()
        discovered = self.structured("evidence", "status", "--research", "example", code=1)
        self.assertEqual(discovered["status"], "error")
        self.assertEqual({row["path"]: row["state"] for row in discovered["records"]}, {
            current: "current", stale: "stale", failed: "failed",
        })
        self.assertEqual(discovered["summary"]["review_states"], {"current": 1, "failed": 1, "stale": 1})
        claim = discovered["claims"][0]
        self.assertEqual(claim["current_reviews_by_kind"], {"proof": 1})
        self.assertTrue(claim["has_current_proof_review"])
        self.assertEqual(len(claim["reviews"]), 3)
        selected = self.structured("evidence", "status", "--research", "example", "--record", current)
        self.assertEqual(selected["status"], "ok")
        warning = self.structured("evidence", "status", "--research", "example", "--record", stale)
        self.assertEqual(warning["status"], "warning")
        strict = self.structured("evidence", "status", "--research", "example", "--record", stale,
                                 "--strict", code=1)
        self.assertEqual(strict, warning)
        text = self.expect("evidence", "status", "--research", "example", code=1)
        for state, path in (("current", current), ("stale", stale), ("failed", failed)):
            self.assertIn(f"[{state}] {path}", text)
        self.assertIn("Recorded evidence statuses are assertions", text)
        self.assertEqual(self.state(), before)

    def test_status_program_without_catalog_remains_unmigrated(self):
        self.put("research/unadopted/plan.md", "A pre-existing private research plan.\n")
        before = self.state()
        value = self.structured("evidence", "status", "--research", "unadopted", "--strict")
        self.assertEqual(value["status"], "ok")
        self.assertEqual(value["adoption"], "not-adopted")
        self.assertIsNone(value["catalog"])
        self.assertEqual(value["claims"], [])
        self.assertEqual(value["records"], [])
        text = self.expect("evidence", "status", "--research", "unadopted")
        self.assertIn("No catalog claims recorded", text)
        self.assertIn("not a statement about the research's completeness", text)
        self.assertEqual(self.state(), before)

    def test_replay_default_plan_never_runs_native_fixture_or_promotes_claim(self):
        self.catalog(formal=True)
        toolchain = self.root / "synthetic-toolchain"
        (toolchain / "bin").mkdir(parents=True)
        (toolchain / "lib/lean").mkdir(parents=True)
        # Native magic satisfies preflight; these bytes cannot execute Lean.
        binary = toolchain / "bin" / ("lean.exe" if os.name == "nt" else "lean")
        binary.write_bytes((b"MZ00" if os.name == "nt" else b"\x7fELF") + b"not a real Lean binary")
        binary.chmod(0o700)
        (toolchain / "lib/lean/Init.olean").write_bytes(b"synthetic compiled artifact")
        before = self.state()
        args = ("evidence", "replay", "--catalog", CATALOG, "--claim", "example-claim",
                "--toolchain-dir", str(toolchain))
        value = self.structured(*args)
        self.assertEqual(value["status"], "plan")
        self.assertTrue(value["preflight"]["ready"], value["preflight"])
        self.assertFalse(value["executed"])
        self.assertEqual(value["approval"], "not-granted")
        self.assertEqual(value["alignment"], "not-assessed")
        self.assertTrue(all(command["status"] == "not-run" for command in value["commands"]))
        self.assertTrue(all(Path(command["argv"][0]) == binary for command in value["commands"]))
        text = self.expect(*args)
        self.assertIn("PLAN: selected-source Lean replay", text)
        self.assertIn("not informal alignment", text)
        self.assertIn("not-run", text)
        self.assertIn("Full input manifests", text)
        self.assertNotIn('"project_files":', text)
        unavailable = self.structured("evidence", "replay", "--catalog", CATALOG, "--claim", "example-claim",
                                      "--toolchain-dir", str(self.root / "not-installed"), "--execute", code=1)
        self.assertEqual(unavailable["status"], "unavailable")
        self.assertFalse(unavailable["executed"])
        self.assertTrue(all(command["status"] == "not-run" for command in unavailable["commands"]))
        self.assertEqual(self.state(), before)

    def test_staged_cli_text_json_gating_and_append_only_recovery(self):
        source_before = (self.workspace / PART).read_bytes()
        started = self.structured("paper", "reading", "start", "--source", PART,
                                  "--session", SESSION, "--reader", "Fixture reader")
        self.assertEqual(started["mode"], "single-context")
        self.assertEqual(started["through_line"], 0)
        self.assertNotIn(SPOILER, json.dumps(started))
        prefix = self.expect("paper", "reading", "next", "--session", SESSION, "--through-line", "1")
        self.assertEqual(prefix, "Visible question.\n")
        before = self.state()
        blocked = self.cli("paper", "reading", "next", "--session", SESSION, "--through-line", "2")
        self.assertEqual(blocked.returncode, 2, blocked.stderr)
        self.assertIn("initial understanding and first confusion", blocked.stderr)
        self.assertNotIn(SPOILER, blocked.stderr + blocked.stdout)
        self.assertEqual(self.state(), before)
        observed = self.structured("paper", "reading", "observe", "--session", SESSION,
                                   "--understanding", "The visible text asks a question.",
                                   "--confusion", "The object is unspecified.")
        self.assertFalse(observed["awaiting_observation"])
        original = json.loads((self.workspace / SESSION).read_text())["events"][1]
        text = self.expect("paper", "reading", "observe", "--session", SESSION,
                           "--understanding", "A supplied reference later explains the object.",
                           "--confusion", "The initial gap is now resolved.", "--rescue")
        self.assertIn("context independence is not certified", text)
        self.assertEqual(json.loads((self.workspace / SESSION).read_text())["events"][1], original)
        exposed = self.structured("paper", "reading", "next", "--session", SESSION, "--through-line", "2")
        self.assertEqual(exposed["text"], "Visible question.\nVisible relation α → β.\n")
        self.assertNotIn(SPOILER, json.dumps(exposed))
        before = self.state()
        status = self.structured("paper", "reading", "status", "--session", SESSION)
        self.assertEqual(status["through_line"], 2)
        self.assertNotIn("text", status)
        self.assertNotIn(SPOILER, json.dumps(status))
        self.assertEqual(self.state(), before)
        self.assertEqual((self.workspace / PART).read_bytes(), source_before)

    def test_changed_source_cli_rejects_without_mutating_session(self):
        self.expect("paper", "reading", "start", "--source", PART, "--session", SESSION,
                    "--reader", "Fixture", "--mode", "independent")
        self.expect("paper", "reading", "next", "--session", SESSION, "--through-line", "1")
        self.put(PART, "Changed source.\n" + SPOILER + "\n")
        before = self.state()
        for args in (("status",), ("next", "--through-line", "2")):
            result = self.cli("paper", "reading", *args, "--session", SESSION, "--format", "json")
            self.assertEqual(result.returncode, 2)
            self.assertIn("reading source changed", result.stderr)
            self.assertNotIn(SPOILER, result.stderr + result.stdout)
        self.assertEqual(self.state(), before)

    def test_ordinary_paper_map_and_section_do_not_opt_into_staging(self):
        section = "writing/ordinary/sections/01-introduction.tex"
        self.put("writing/ordinary/main.tex", "\\input{sections/01-introduction}\n")
        self.put(section, "An ordinary opening.\n% LABO:INTRO-END\n" + SPOILER + "\n")
        before = self.state()
        mapped = self.structured("paper", "map", "--paper", "ordinary")
        self.assertEqual(mapped["sections"][0]["opening"], "An ordinary opening.")
        self.assertNotIn(SPOILER, json.dumps(mapped))
        complete = self.expect("paper", "section", "--paper", "ordinary", "--name", "01-introduction")
        self.assertIn(SPOILER, complete)
        self.assertEqual(self.state(), before)
        self.assertFalse((self.workspace / SESSION).exists())


if __name__ == "__main__":
    unittest.main()
