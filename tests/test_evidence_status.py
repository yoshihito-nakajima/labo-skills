"""Inventories on synthetic research data; these fixtures are not proof reviews."""

import hashlib
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from labo_tools.evidence import EvidenceError, snapshot  # noqa: E402
from labo_tools.evidence_status import evidence_status  # noqa: E402


CATALOG = "research/example/claims.yaml"
REVIEWS = "research/example/reviews"


class EvidenceStatusTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.put("research/example/plan.md", "Synthetic private research program.\n")

    def put(self, name, content):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return path

    def dump(self, name, data):
        return self.put(name, yaml.safe_dump(data, sort_keys=False))

    def catalog(self, *names):
        claims = {}
        for name in names or ("example-claim",):
            evidence = f"research/example/{name}.md"
            self.put(evidence, "Synthetic evidence; establishes no mathematical result.\n")
            claims[name] = {"statement": f"Synthetic statement for {name}.",
                            "status": "proved/agent", "evidence": [evidence], "dependencies": []}
        value = {"schema_version": 1, "claims": claims}
        self.dump(CATALOG, value)
        return value

    def record(self, name, *, claims=None, kind="proof", verdict="pass", extra=None):
        selected = claims or ["example-claim"]
        value = snapshot(self.root, kind=kind, catalog=CATALOG, claim_ids=selected,
                         files=[extra] if extra else [])
        report = f"{REVIEWS}/{name}.md"
        path = self.put(report, "Fictional review fixture, not an actual review.\n")
        if verdict != "pending":
            value.update(verdict=verdict, reviewer="Synthetic fixture reviewer", reviewed_at="2026-01-01",
                         report=report, report_sha256=hashlib.sha256(path.read_bytes()).hexdigest())
        return self.dump(f"{REVIEWS}/{name}.yaml", value).relative_to(self.root).as_posix()

    def status(self, **kwargs):
        return evidence_status(self.root, research="example", **kwargs)

    @staticmethod
    def codes(result):
        return {issue["code"] for issue in result["issues"]}

    def bytes(self):
        return {path.relative_to(self.root).as_posix(): path.read_bytes()
                for path in self.root.rglob("*") if path.is_file()}

    def test_opt_in_absence_is_not_an_empty_proof_certificate_or_a_migration(self):
        before = self.bytes()
        result = self.status()
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["adoption"], "not-adopted")
        self.assertEqual(result["summary"]["claim_count"], 0)
        self.assertIsNone(result["catalog"])
        self.assertEqual(self.bytes(), before)
        self.assertFalse((self.root / REVIEWS).exists())

    def test_claim_status_and_review_coverage_are_distinct_and_read_only(self):
        self.catalog()
        before = self.bytes()
        result = self.status()
        self.assertEqual(result["status"], "warning")
        row = result["claims"][0]
        self.assertEqual(row["evidence_status"], "proved/agent")
        self.assertFalse(row["has_current_proof_review"])
        self.assertIn("unreviewed-established-claim", self.codes(result))
        self.assertEqual(self.bytes(), before)
        self.record("proof")
        before = self.bytes()
        result = self.status()
        self.assertEqual(result["status"], "ok", result["issues"])
        self.assertEqual(result["claims"][0]["current_reviews_by_kind"], {"proof": 1})
        self.assertEqual(self.bytes(), before)
        self.assertNotIn("certified", result)

    def test_writing_review_does_not_grant_proof_coverage(self):
        self.catalog()
        self.record("writing", kind="writing")
        result = self.status()
        row = result["claims"][0]
        self.assertEqual(row["current_reviews_by_kind"], {"writing": 1})
        self.assertFalse(row["has_current_proof_review"])
        self.assertEqual(result["status"], "warning")

    def test_transitive_claims_do_not_inherit_direct_review_coverage(self):
        catalog = self.catalog("seed-claim", "main-claim")
        catalog["claims"]["main-claim"]["dependencies"] = ["seed-claim"]
        self.dump(CATALOG, catalog)
        self.record("main", claims=["main-claim"])
        rows = {row["id"]: row for row in self.status()["claims"]}
        self.assertTrue(rows["main-claim"]["has_current_proof_review"])
        self.assertFalse(rows["seed-claim"]["has_current_proof_review"])
        self.put("research/example/seed-claim.md", "Changed transitive evidence.\n")
        result = self.status()
        self.assertEqual(result["records"][0]["state"], "stale")
        self.assertEqual(result["summary"]["claims_with_current_proof_review"], 0)

    def test_current_stale_pending_failed_and_invalid_records_are_all_retained(self):
        self.catalog()
        extra = "research/example/extra.md"
        self.put(extra, "Original.\n")
        self.record("current")
        self.record("stale", extra=extra)
        self.record("pending", verdict="pending")
        self.record("failed", verdict="fail")
        self.put(f"{REVIEWS}/invalid.yaml", "schema_version: [1]\n")
        self.put(extra, "Changed.\n")
        result = self.status()
        self.assertEqual(result["summary"]["review_states"],
                         {"current": 1, "failed": 1, "invalid": 1, "pending": 1, "stale": 1})
        self.assertEqual(result["status"], "error")
        self.assertTrue(result["claims"][0]["has_current_proof_review"])
        self.assertEqual(len(result["claims"][0]["reviews"]), 4)

    def test_explicit_selection_is_deduplicated_and_replaces_discovery(self):
        self.catalog()
        current = self.record("current")
        self.put(f"{REVIEWS}/invalid.yaml", "not a valid record\n")
        self.put("research/unrelated/claims.yaml", "do not inspect this program\n")
        result = self.status(records=[current, current])
        self.assertEqual(result["status"], "ok", result["issues"])
        self.assertEqual(result["selection"], "explicit-records")
        self.assertIsNone(result["reviews_directory"])
        self.assertEqual(result["summary"]["record_count"], 1)

    def test_foreign_catalog_record_is_reported_without_inspecting_foreign_inputs(self):
        self.catalog()
        name = self.record("foreign")
        value = yaml.safe_load((self.root / name).read_text(encoding="utf-8"))
        value["catalog"] = "research/other/claims.yaml"
        self.dump(name, value)
        with patch("labo_tools.evidence_status._check_record", side_effect=AssertionError("foreign read")):
            result = self.status()
        self.assertEqual(result["records"][0]["state"], "out-of-scope")
        self.assertIn("foreign-catalog", self.codes(result))
        self.assertEqual(result["claims"][0]["reviews"], [])

    def test_records_without_catalog_can_describe_explicit_file_reviews(self):
        name = "writing/example/main.tex"
        self.put(name, "Synthetic manuscript.\n")
        value = snapshot(self.root, kind="writing", files=[name])
        self.dump(f"{REVIEWS}/writing.yaml", value)
        result = self.status()
        self.assertEqual(result["adoption"], "records-only")
        self.assertEqual(result["records"][0]["state"], "pending")
        self.assertEqual(result["claims"], [])

    def test_open_and_disputed_work_is_visible_without_becoming_a_mandatory_gate(self):
        catalog = self.catalog("open-claim", "disputed-claim")
        for name, state in (("open-claim", "open"), ("disputed-claim", "disputed")):
            catalog["claims"][name]["status"] = state
        self.dump(CATALOG, catalog)
        result = self.status()
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["summary"]["evidence_statuses"], {"disputed": 1, "open": 1})
        self.assertTrue(all("no-current-proof-review" in row["attention"] for row in result["claims"]))

    def test_invalid_claim_structure_is_retained_but_not_silently_approved(self):
        catalog = self.catalog()
        catalog["claims"]["example-claim"]["dependencies"] = ["missing-claim"]
        self.dump(CATALOG, catalog)
        result = self.status()
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["claims"][0]["structure"], "invalid")
        self.assertIn("invalid-claim", self.codes(result))

    def test_malformed_formal_fields_do_not_crash_or_infer_alignment(self):
        catalog = self.catalog()
        catalog["claims"]["example-claim"]["formal"] = {
            "declaration": "Example.claim", "kernel": {"verdict": "pass"}, "alignment": "malformed",
        }
        self.dump(CATALOG, catalog)
        result = self.status()
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["claims"][0]["formal"]["kernel"], "pass")
        self.assertIsNone(result["claims"][0]["formal"]["alignment"])
        self.assertEqual(result["summary"]["formal_mappings_needing_attention"], 1)

    def test_missing_explicit_paths_are_errors_not_unadopted_success(self):
        for kwargs in ({"catalog": CATALOG}, {"reviews": REVIEWS},
                       {"records": [f"{REVIEWS}/missing.yaml"]}):
            with self.subTest(kwargs=kwargs):
                self.assertEqual(self.status(**kwargs)["status"], "error")

    def test_program_and_discovery_paths_cannot_escape_selected_program(self):
        for kwargs in ({"catalog": "research/other/claims.yaml"},
                       {"reviews": "research/other/reviews"},
                       {"reviews": "research/example/../other"},
                       {"reviews": REVIEWS, "records": ["x.yaml"]}):
            with self.subTest(kwargs=kwargs), self.assertRaises(EvidenceError):
                self.status(**kwargs)
        for research in ("../example", "Example", "", "missing"):
            with self.subTest(research=research), self.assertRaises(EvidenceError):
                evidence_status(self.root, research=research)

    def test_bounded_discovery_ignores_caches_and_reports_limits(self):
        self.catalog()
        self.record("one")
        self.record("two")
        self.put(f"{REVIEWS}/.git/ignored.yaml", "ignored invalid bytes\n")
        self.put(f"{REVIEWS}/report.md", "not a record\n")
        result = self.status()
        self.assertEqual(result["summary"]["record_count"], 2)
        with patch("labo_tools.evidence_status.MAX_RECORDS", 1):
            result = self.status()
            self.assertIn("record-limit", self.codes(result))
            self.assertEqual(len(result["records"]), 1)
        self.put(f"{REVIEWS}/nested/deeper/record.yaml", "unreached\n")
        with patch("labo_tools.evidence_status.MAX_REVIEW_DEPTH", 0):
            self.assertIn("unsafe-review-directory", self.codes(self.status()))

    def test_symlinked_discovery_is_rejected_without_traversing(self):
        target = self.root / "outside"
        target.mkdir()
        link = self.root / REVIEWS
        try:
            link.symlink_to(target, target_is_directory=True)
        except OSError:
            self.skipTest("native symlink creation is unavailable")
        result = self.status()
        self.assertEqual(result["status"], "error")
        self.assertIn("invalid-review-directory", self.codes(result))
        self.assertEqual(result["records"], [])


if __name__ == "__main__":
    unittest.main()
