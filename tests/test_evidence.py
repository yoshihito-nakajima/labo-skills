"""Black-box evidence checks on synthetic host data, not mathematical verification."""

from datetime import date
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import yaml


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CATALOG = "research/example/claims.yaml"
RECORD = "research/example/reviews/review.yaml"
REPORT = "research/example/reviews/report.md"


class EvidenceCliTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.workspace = self.root / "private workspace"
        self.workspace.mkdir()
        self.cwd = self.root / "unrelated cwd"
        self.cwd.mkdir()
        self.program = self.workspace / "research/example"
        self.program.mkdir(parents=True)

    def cli(self, *args):
        return subprocess.run(
            [sys.executable, "-B", "-I", str(PROJECT_ROOT / "scripts/labo.py"),
             "evidence", *args, "--workspace", str(self.workspace)],
            cwd=self.cwd, capture_output=True, text=True,
        )

    def put(self, relative, content):
        path = self.workspace / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return path

    def dump(self, relative, value):
        return self.put(relative, yaml.safe_dump(value, sort_keys=False, allow_unicode=True))

    def catalog(self):
        claims = {}
        for name, dependencies in (
            ("seed-bound", []), ("middle-bound", ["seed-bound"]),
            ("main-bound", ["middle-bound"]), ("unrelated-claim", []),
        ):
            evidence = f"research/example/{name}.md"
            self.put(evidence, f"Synthetic evidence for {name}; not a mathematical proof.\n")
            claims[name] = {
                "statement": f"Synthetic scoped statement: {name}.",
                "status": "proved/agent", "evidence": [evidence],
                "dependencies": dependencies,
            }
        value = {"schema_version": 1, "claims": claims}
        self.dump(CATALOG, value)
        return value

    def snapshot(self, *args):
        result = self.cli("snapshot", *args)
        self.assertEqual(result.returncode, 0, result.stderr)
        value = yaml.safe_load(result.stdout)
        self.assertIsInstance(value, dict)
        self.assertEqual(value["verdict"], "pending")
        return value

    def proof_snapshot(self, kind="proof"):
        return self.snapshot("--kind", kind, "--catalog", CATALOG, "--claim", "main-bound")

    def review(self, snapshot, verdict="pass"):
        # These are fictional test records, never assertions that a review occurred.
        report = self.put(REPORT, "Synthetic review fixture; establishes no mathematical result.\n")
        value = dict(snapshot)
        value.update({
            "verdict": verdict, "reviewer": "Synthetic fixture reviewer",
            "mode": snapshot.get("mode", "single-context"),
            "reviewed_at": date.today().isoformat(), "report": REPORT,
            "report_sha256": hashlib.sha256(report.read_bytes()).hexdigest(),
        })
        self.dump(RECORD, value)
        return value

    def check(self, *args, code=0, status="ok", state=None):
        result = self.cli("check", *args, "--format", "json")
        self.assertEqual(result.returncode, code, result.stderr or result.stdout)
        value = json.loads(result.stdout)
        self.assertNotIn(str(self.workspace), result.stdout)
        self.assertEqual(value["schema_version"], 1)
        self.assertEqual(value["status"], status)
        self.assertIsInstance(value["issues"], list)
        self.assertIsInstance(value["records"], list)
        for issue in value["issues"]:
            self.assertGreaterEqual(set(issue), {"severity", "code", "path", "message"})
            for key in ("severity", "code", "path", "message"):
                self.assertIsInstance(issue[key], str)
        if status != "ok":
            self.assertTrue(value["issues"])
        for record in value["records"]:
            self.assertIn(record["state"], {"current", "stale", "pending", "failed", "invalid"})
            self.assertIsInstance(record["path"], str)
        if state is not None:
            self.assertEqual(value["records"], [{"path": RECORD, "state": state}])
        return value

    def current(self):
        return self.check("--record", RECORD, state="current")

    def stale(self):
        self.check("--record", RECORD, status="warning", state="stale")
        self.check("--record", RECORD, "--strict", code=1, status="warning", state="stale")

    def workspace_bytes(self):
        return {
            path.relative_to(self.workspace).as_posix(): path.read_bytes()
            for path in self.workspace.rglob("*") if path.is_file()
        }

    def test_init_dry_run_template_and_existing_catalog_preservation(self):
        original = self.put("research/example/plan.md", "Private research story stays intact.\n")
        before = self.workspace_bytes()
        result = self.cli("init", "--catalog", CATALOG, "--dry-run")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.workspace_bytes(), before)
        result = self.cli("init", "--catalog", CATALOG)
        self.assertEqual(result.returncode, 0, result.stderr)
        expected = (PROJECT_ROOT / "skills/research-management/assets/claims.yaml").read_bytes()
        target = self.workspace / CATALOG
        self.assertEqual(target.read_bytes(), expected)
        target.write_bytes(b"# Existing private catalog\n")
        for flags in ((), ("--dry-run",)):
            result = self.cli("init", "--catalog", CATALOG, *flags)
            self.assertEqual(result.returncode, 2, result.stderr)
            self.assertEqual(target.read_bytes(), b"# Existing private catalog\n")
        self.assertEqual(original.read_text(), "Private research story stays intact.\n")
        self.assertFalse((self.workspace / "src").exists())
        self.assertFalse((self.workspace / "scripts").exists())

    def test_init_does_not_create_a_research_program(self):
        result = self.cli("init", "--catalog", "research/missing/claims.yaml")
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertFalse((self.workspace / "research/missing").exists())

    def test_named_claims_survive_reordering_and_unrelated_claim_changes(self):
        catalog = self.catalog()
        self.check("--catalog", CATALOG)
        self.review(self.proof_snapshot())
        catalog["claims"] = dict(reversed(list(catalog["claims"].items())))
        catalog["claims"]["unrelated-claim"]["statement"] = "Different unrelated scope."
        self.dump(CATALOG, catalog)
        self.put("research/example/unrelated-claim.md", "Changed unrelated evidence.\n")
        self.current()

    def test_unknown_dependencies_cycles_and_unstable_ids_are_check_errors(self):
        for kind in ("unknown", "cycle", "unstable-id"):
            with self.subTest(kind=kind):
                catalog = self.catalog()
                if kind == "unknown":
                    catalog["claims"]["seed-bound"]["dependencies"] = ["missing-bound"]
                elif kind == "cycle":
                    catalog["claims"]["seed-bound"]["dependencies"] = ["main-bound"]
                else:
                    catalog["claims"]["Claim 1"] = catalog["claims"].pop("unrelated-claim")
                self.dump(CATALOG, catalog)
                self.check("--catalog", CATALOG, code=1, status="error")
                result = self.cli("snapshot", "--kind", "proof", "--catalog", CATALOG,
                                  "--claim", "main-bound")
                self.assertEqual(result.returncode, 2, result.stderr)

    def test_proved_claims_cannot_promote_unresolved_or_merely_computed_dependencies(self):
        for status in ("open", "unverified", "disputed", "refuted", "verified-computationally"):
            with self.subTest(status=status):
                catalog = self.catalog()
                catalog["claims"]["seed-bound"]["status"] = status
                self.dump(CATALOG, catalog)
                self.check("--catalog", CATALOG, code=1, status="error")

    def test_lifecycle_statuses_are_not_evidence_and_checked_claims_need_inputs(self):
        for status in ("completed", "in_progress", "proved"):
            with self.subTest(status=status):
                catalog = self.catalog()
                catalog["claims"]["main-bound"]["status"] = status
                self.dump(CATALOG, catalog)
                self.check("--catalog", CATALOG, code=1, status="error")
        for status in ("proved/agent", "proved/literature", "verified-computationally", "refuted"):
            with self.subTest(status=status, evidence=[]):
                catalog = self.catalog()
                catalog["claims"]["main-bound"].update({"status": status, "evidence": []})
                self.dump(CATALOG, catalog)
                self.check("--catalog", CATALOG, code=1, status="error")

    def test_snapshot_is_read_only_pending_and_does_not_invent_review_metadata(self):
        self.catalog()
        before = self.workspace_bytes()
        snapshot = self.proof_snapshot()
        self.assertEqual(self.workspace_bytes(), before)
        for key in ("reviewer", "reviewed_at", "report", "report_sha256"):
            self.assertIsNone(snapshot.get(key))
        self.dump(RECORD, snapshot)
        self.check("--record", RECORD, status="warning", state="pending")
        self.check("--record", RECORD, "--strict", code=1, status="warning", state="pending")

    def test_repeated_named_claim_scope_is_supported(self):
        self.catalog()
        snapshot = self.snapshot("--kind", "proof", "--catalog", CATALOG,
                                 "--claim", "main-bound", "--claim", "unrelated-claim")
        self.review(snapshot)
        self.current()
        self.put("research/example/unrelated-claim.md", "New bytes in selected input.\n")
        self.stale()

    def test_statement_status_and_transitive_evidence_changes_are_stale(self):
        for change in ("statement", "status", "transitive-evidence", "dependencies"):
            with self.subTest(change=change):
                catalog = self.catalog()
                self.review(self.proof_snapshot())
                if change == "statement":
                    catalog["claims"]["main-bound"]["statement"] += " Changed scope."
                elif change == "status":
                    catalog["claims"]["seed-bound"]["status"] = "proved/literature"
                elif change == "dependencies":
                    catalog["claims"]["main-bound"]["dependencies"] = ["seed-bound"]
                else:
                    self.put("research/example/seed-bound.md", "Changed uncommitted dependency input.\n")
                self.dump(CATALOG, catalog)
                self.stale()

    def test_writing_tracks_only_explicit_files_and_does_not_resolve_markdown_links(self):
        self.put("writing/example/main.tex", "Synthetic text.\\input{not-in-scope}\n")
        self.put("reference/source.md", "Synthetic source [unchecked link](missing.md).\n")
        self.put("writing/example/other.tex", "Outside explicit file scope.\n")
        snapshot = self.snapshot("--kind", "writing", "--file", "writing/example/main.tex",
                                 "--file", "reference/source.md",
                                 "--policy-file", "skills/mathematical-exposition/SKILL.md")
        self.review(snapshot)
        self.put("writing/example/other.tex", "Unrelated text changed.\n")
        self.current()
        self.put("reference/source.md", "Changed selected external source record.\n")
        self.stale()

    def test_writing_tree_tracks_edits_additions_and_removals(self):
        for change in ("edit", "add", "remove"):
            with self.subTest(change=change):
                selected = self.put("writing/example/main.tex", "Original text.\n")
                added = self.workspace / "writing/example/new.tex"
                if added.exists():
                    added.unlink()
                self.review(self.snapshot("--kind", "writing", "--tree", "writing/example"))
                if change == "edit":
                    selected.write_text("Changed text.\n", encoding="utf-8")
                elif change == "add":
                    self.put("writing/example/new.tex", "New tree member.\n")
                else:
                    selected.unlink()
                self.stale()

    def test_tree_cache_exclusions_and_unrelated_files_do_not_stale(self):
        self.put("writing/example/main.tex", "Selected text.\n")
        self.review(self.snapshot("--kind", "writing", "--tree", "writing/example"))
        for excluded in (".git", ".lake", ".temp", ".venv", ".uv-cache", "__pycache__",
                         "build", "dist", "output"):
            self.put(f"writing/example/{excluded}/generated.txt", "Excluded bytes.\n")
        self.put("research/unrelated/note.md", "Not selected by this review.\n")
        self.current()

    def test_report_hash_is_required_and_report_edits_invalidate_review(self):
        self.catalog()
        record = self.review(self.proof_snapshot())
        self.current()
        self.check("--record", RECORD, "--strict", state="current")
        self.put(REPORT, "Edited substantive report after confirmation.\n")
        self.stale()
        record.pop("report_sha256")
        self.dump(RECORD, record)
        self.check("--record", RECORD, code=1, status="error", state="invalid")

    def test_passing_record_requires_valid_scoped_review_metadata(self):
        self.catalog()
        snapshot = self.proof_snapshot()
        for key, bad in (("reviewer", None), ("reviewed_at", "not-a-date"),
                         ("mode", "automatic-approval"), ("report_sha256", "not-a-hash"),
                         ("report", "../outside.md")):
            with self.subTest(key=key):
                record = self.review(snapshot)
                record[key] = bad
                self.dump(RECORD, record)
                self.check("--record", RECORD, code=1, status="error", state="invalid")

    def test_failed_review_fails_in_both_modes_even_with_matching_inputs(self):
        self.catalog()
        self.review(self.proof_snapshot(), verdict="fail")
        for flags in ((), ("--strict",)):
            self.check("--record", RECORD, *flags, code=1, status="error", state="failed")

    def test_invalid_unquoted_yaml_date_returns_structured_error(self):
        self.catalog()
        self.review(self.proof_snapshot())
        path = self.workspace / RECORD
        source = path.read_text(encoding="utf-8")
        source = "\n".join("reviewed_at: 2026-02-30" if line.startswith("reviewed_at:")
                           else line for line in source.splitlines()) + "\n"
        self.put(RECORD, source)
        self.check("--record", RECORD, code=1, status="error", state="invalid")

    def test_missing_and_malformed_structural_inputs_are_check_errors(self):
        for option, relative in (("--catalog", CATALOG), ("--record", RECORD)):
            for content in (None, "schema_version: [unterminated", "schema_version: 1\n"):
                with self.subTest(option=option, content=content):
                    path = self.workspace / relative
                    if path.exists():
                        path.unlink()
                    if content is not None:
                        self.put(relative, content)
                    kwargs = {"state": "invalid"} if option == "--record" else {}
                    self.check(option, relative, code=1, status="error", **kwargs)

    def test_duplicate_yaml_keys_are_rejected_not_silently_overwritten(self):
        self.catalog()
        path = self.workspace / CATALOG
        path.write_text(path.read_text() + "schema_version: 1\n", encoding="utf-8")
        self.check("--catalog", CATALOG, code=1, status="error")
        self.catalog()
        self.review(self.proof_snapshot())
        path = self.workspace / RECORD
        path.write_text(path.read_text() + "verdict: pass\n", encoding="utf-8")
        self.check("--record", RECORD, code=1, status="error", state="invalid")

    def test_invalid_snapshot_scopes_are_usage_errors(self):
        self.catalog()
        self.put("writing/example/main.tex", "Synthetic text.\n")
        requests = (
            ("--kind", "proof", "--catalog", CATALOG),
            ("--kind", "owner", "--catalog", CATALOG),
            ("--kind", "formal", "--catalog", CATALOG, "--claim", "main-bound"),
            ("--kind", "proof", "--catalog", CATALOG, "--claim", "missing-bound"),
            ("--kind", "writing"),
            ("--kind", "writing", "--file", "writing/missing.tex"),
            ("--kind", "writing", "--file", "../outside.md"),
            ("--kind", "writing", "--tree", "writing/../writing/example"),
            ("--kind", "writing", "--file", "writing/example/main.tex",
             "--policy-file", "../outside.md"),
        )
        before = self.workspace_bytes()
        for args in requests:
            with self.subTest(args=args):
                result = self.cli("snapshot", *args)
                self.assertEqual(result.returncode, 2, result.stderr)
                self.assertEqual(self.workspace_bytes(), before)

    def test_catalog_input_paths_reject_escape_absolute_urls_and_missing_files(self):
        outside = self.root / "outside.md"
        outside.write_text("Outside workspace.\n", encoding="utf-8")
        for path in ("../outside.md", str(outside), "https://example.invalid/evidence.md",
                     "research/example/../example/main-bound.md", "research/example/missing.md"):
            with self.subTest(path=path):
                catalog = self.catalog()
                catalog["claims"]["main-bound"]["evidence"] = [path]
                self.dump(CATALOG, catalog)
                self.check("--catalog", CATALOG, code=1, status="error")

    def test_drive_qualified_paths_are_rejected_before_native_path_join(self):
        for value in ("C:/outside.md", "D:/outside.md", "C:outside.md"):
            with self.subTest(path=value):
                result = self.cli("snapshot", "--kind", "writing", "--file", value)
                self.assertEqual(result.returncode, 2, result.stderr)
                self.assertIn("normalized and relative", result.stderr)
                self.assertNotIn("Traceback", result.stderr)

    def test_symlinked_files_directories_and_policy_inputs_are_rejected(self):
        source = self.put("writing/example/main.tex", "Original selected bytes.\n")
        try:
            (self.workspace / "linked.tex").symlink_to(source)
            (self.workspace / "linked-writing").symlink_to(source.parent, target_is_directory=True)
            (self.workspace / "policy").symlink_to(PROJECT_ROOT, target_is_directory=True)
        except (OSError, NotImplementedError) as exc:
            self.skipTest(f"symlinks unavailable: {exc}")
        for option, path in (("--file", "linked.tex"), ("--tree", "linked-writing"),
                             ("--file", "policy/skills/research-management/SKILL.md")):
            with self.subTest(path=path):
                result = self.cli("snapshot", "--kind", "writing", option, path)
                self.assertEqual(result.returncode, 2, result.stderr)
        (source.parent / "linked-child.tex").symlink_to(source)
        result = self.cli("snapshot", "--kind", "writing", "--tree", "writing/example")
        self.assertEqual(result.returncode, 2, result.stderr)
        catalog = self.catalog()
        catalog["claims"]["main-bound"]["evidence"] = ["linked.tex"]
        self.dump(CATALOG, catalog)
        self.check("--catalog", CATALOG, code=1, status="error")
        (self.workspace / "linked-catalog.yaml").symlink_to(self.workspace / CATALOG)
        self.check("--catalog", "linked-catalog.yaml", code=1, status="error")
        result = self.cli("init", "--catalog", "linked-writing/claims.yaml")
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertFalse((source.parent / "claims.yaml").exists())

    def formal_catalog(self):
        catalog = self.catalog()
        self.put("lean/example/Example.lean", "-- Synthetic source; no checked theorem.\n")
        self.put("lean/example/Helper.lean", "-- Additional production input.\n")
        self.put("lean/example/lean-toolchain", "leanprover/lean4:v4.0.0\n")
        self.put("lean/example/lakefile.lean", "import Lake\nopen Lake DSL\npackage example\n")
        self.put("lean/example/lake-manifest.json", '{"version":"1.1.0","packages":[]}\n')
        self.put("lean/example/verification.txt", "Synthetic kernel report, not a Lean execution.\n")
        self.put("research/example/formal-alignment.md", "Synthetic alignment report.\n")
        catalog["claims"]["main-bound"].update({
            "status": "verified-formally",
            "formal": {
                "project": "lean/example", "source": "lean/example/Example.lean",
                "declaration": "Example.fixture_only",
                "kernel": {"verdict": "pass", "report": "lean/example/verification.txt"},
                "alignment": {"verdict": "pass", "report": "research/example/formal-alignment.md"},
            },
        })
        self.dump(CATALOG, catalog)
        return catalog

    def test_formal_records_check_shape_and_pins_not_lean_truth(self):
        self.formal_catalog()
        # Deliberately contains no proved declaration: this checker must not claim to run Lean.
        self.check("--catalog", CATALOG)
        self.review(self.proof_snapshot(kind="formal"))
        self.current()
        self.put("lean/example/.lake/build/generated.lean", "-- Excluded cache.\n")
        self.current()
        self.put("lean/example/Helper.lean", "-- Changed production source.\n")
        self.stale()

    def test_formal_environment_and_source_inventory_changes_are_stale(self):
        for change in ("lean-toolchain", "lakefile.lean", "lake-manifest.json", "new-source",
                       "remove-source"):
            with self.subTest(change=change):
                self.formal_catalog()
                extra = self.workspace / "lean/example/Added.lean"
                if extra.exists():
                    extra.unlink()
                self.review(self.proof_snapshot(kind="formal"))
                if change == "new-source":
                    self.put("lean/example/Added.lean", "-- Newly selected project source.\n")
                elif change == "remove-source":
                    (self.workspace / "lean/example/Helper.lean").unlink()
                else:
                    path = self.workspace / "lean/example" / change
                    path.write_text(path.read_text() + "\n", encoding="utf-8")
                self.stale()

    def test_explicit_formal_source_is_hashed_even_below_excluded_directory(self):
        catalog = self.formal_catalog()
        source = "lean/example/build/Production.lean"
        self.put(source, "-- Explicit production source in an otherwise excluded tree.\n")
        catalog["claims"]["main-bound"]["formal"]["source"] = source
        self.dump(CATALOG, catalog)
        self.review(self.proof_snapshot(kind="formal"))
        self.current()
        self.put(source, "-- Changed explicit production source.\n")
        self.stale()

    def test_formally_verified_requires_both_reports_pins_and_project_source(self):
        for defect in ("pending-alignment", "failed-kernel", "missing-report",
                       "missing-manifest", "outside-source"):
            with self.subTest(defect=defect):
                catalog = self.formal_catalog()
                formal = catalog["claims"]["main-bound"]["formal"]
                if defect == "pending-alignment":
                    formal["alignment"] = {"verdict": "pending", "report": None}
                elif defect == "failed-kernel":
                    formal["kernel"]["verdict"] = "fail"
                elif defect == "missing-report":
                    formal["kernel"]["report"] = "lean/example/missing.txt"
                elif defect == "missing-manifest":
                    (self.workspace / "lean/example/lake-manifest.json").unlink()
                else:
                    formal["source"] = "research/example/main-bound.md"
                self.dump(CATALOG, catalog)
                self.check("--catalog", CATALOG, code=1, status="error")

    def test_owner_checked_requires_actual_local_confirmation_record(self):
        catalog = self.catalog()
        catalog["claims"]["main-bound"]["status"] = "proved/owner-checked"
        self.dump(CATALOG, catalog)
        self.check("--catalog", CATALOG, code=1, status="error")
        self.put("research/example/owner-confirmation.md", "Synthetic scoped confirmation fixture.\n")
        catalog["claims"]["main-bound"]["owner_check"] = "research/example/owner-confirmation.md"
        self.dump(CATALOG, catalog)
        self.check("--catalog", CATALOG)
        snapshot = self.proof_snapshot(kind="owner")
        self.review(snapshot)
        self.current()
        self.put("research/example/owner-confirmation.md", "Changed scoped confirmation fixture.\n")
        self.stale()


if __name__ == "__main__":
    unittest.main()
