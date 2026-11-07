"""Execute check_coverage.py on small fictional coverage data."""

from pathlib import Path
import copy
import json
import subprocess
import sys
import tempfile
import unittest

CHECK = Path(__file__).resolve().parents[1] / "skills/reading-reference/scripts/check_coverage.py"

GOOD = {
    "resources": [
        {"id": "S1", "kind": "code", "what": "reference implementation", "status": "read",
         "locator": "repo@abc123", "read_in": "u2"},
        {"id": "S2", "kind": "supplement", "what": "extra plots", "status": "listed",
         "reason": "not cited by the main text and not one of the required kinds"},
    ],
    "comparisons": [
        {"id": "C1", "relation": "inherited", "claim_loc": "Sec. 2, p.3", "unit": "u2",
         "primary": {"work": "Older Method (1999)", "locator": "Alg. 1, p.5", "status": "read"},
         "purpose": "built to order items without a reference point", "place": "family of spectral orderings",
         "inherited": "the graph construction", "changed": "edge weights now depend on density",
         "weakness": "fictional gap shortcuts", "verified": "fictional source inspection",
         "excerpt": True, "translation_needed": True, "translation": True, "code": "diff"},
        {"id": "C2", "relation": "origin", "claim_loc": "Intro, p.1", "unit": "u1",
         "primary": {"work": "Older Method (1999)", "locator": "Sec. 1, p.1", "status": "read"},
         "purpose": "ordering without labels", "place": "unsupervised ordering"},
    ],
    "overview": {
        "lineage_label": "tab:lineage", "values_label": "tab:values",
        "code_notes": [{"unit": "u2", "blocks": [{"lines": "1-3",
                        "does": "build the fictional graph", "source": "fictional example",
                        "difference": "weighted edges"}]}],
        "differences": [{"figure": "fig1", "steps": ["weight edges"],
                         "where": "fictional example lines 1-3", "by": "note"}],
    },
    "units": [
        {"id": "u1", "parent": "root", "needs": ["external:ordering problem"], "produces": ["ordering problem stated"],
         "bridge_in": "We start from the ordering problem and state it."},
        {"id": "u2", "parent": "u1", "needs": ["ordering problem stated"], "produces": ["graph"], "terminal": True,
         "bridge_in": "Given the ordering problem stated above, we build the graph."},
    ],
    "sentences": [
        {"unit": "u1", "n": 1, "kind": "cite", "gloss": {"object": "o", "known": "k", "claim": "c", "benefit": "b", "added": "a"}},
        {"unit": "u1", "n": 2, "kind": "plain"},
    ],
}


class CheckCoverageTests(unittest.TestCase):
    def run_check(self, data, *flags):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "coverage.json"
            path.write_text(json.dumps(data))
            r = subprocess.run([sys.executable, str(CHECK), str(path), "--json", *flags],
                               capture_output=True, text=True)
            return r.returncode, [f'{p["where"]}: {p["problem"]}' for p in json.loads(r.stdout)]

    def test_complete_records_pass(self):
        self.assertEqual(self.run_check(copy.deepcopy(GOOD)), (0, []))

    def test_must_read_supplement_not_read(self):
        d = copy.deepcopy(GOOD)
        d["resources"][0]["status"] = "obtained"
        code, msgs = self.run_check(d)
        self.assertEqual(code, 1)
        self.assertTrue(any("must-read" in m for m in msgs))

    def test_unobtained_needs_tries_and_request_and_stays_open(self):
        d = copy.deepcopy(GOOD)
        d["resources"].append({"id": "S3", "kind": "derivation", "what": "bound", "status": "unobtained"})
        code, msgs = self.run_check(d)
        self.assertEqual(code, 1)
        self.assertTrue(any("places tried" in m for m in msgs))
        self.assertTrue(any("stated request" in m for m in msgs))
        d["resources"][-1].update({"tried": ["publisher page"], "request": "the bound used in Sec. 3",
                                   "stand_in": {"label": "AI-created", "note": "sketch"}})
        code, msgs = self.run_check(d, "--allow-open")
        self.assertEqual(code, 1)  # a stand-in without the user's permission is a record problem
        self.assertTrue(any("permission" in m for m in msgs))
        d["resources"][-1]["stand_in"]["permission"] = "user, 2026-01-02: 'sketch for S3 only'"
        code, msgs = self.run_check(d)
        self.assertEqual(code, 1)  # a stand-in leaves the entry open
        self.assertIn("resource S3: stand-in only", msgs)
        self.assertEqual(self.run_check(d, "--allow-open")[0], 0)
        d["resources"][-1]["stand_in"]["label"] = "author"
        self.assertTrue(any("AI-created" in m for m in self.run_check(d, "--allow-open")[1]))

    def test_treated_comparison_needs_code_and_unread_is_open(self):
        d = copy.deepcopy(GOOD)
        d["comparisons"][0]["code"] = ""
        self.assertTrue(any("code comparison" in m for m in self.run_check(d)[1]))
        d = copy.deepcopy(GOOD)
        d["comparisons"][0]["primary"]["status"] = "unread"
        code, msgs = self.run_check(d)
        self.assertEqual(code, 1)
        self.assertTrue(any("primary unread" in m for m in msgs))

    def test_unit_chain_breaks(self):
        d = copy.deepcopy(GOOD)
        d["units"][1]["needs"] = ["something never produced"]
        msgs = self.run_check(d)[1]
        self.assertTrue(any("not produced" in m for m in msgs))
        d = copy.deepcopy(GOOD)
        d["units"][1]["bridge_in"] = "Now we build the graph."
        self.assertTrue(any("opening does not name" in m for m in self.run_check(d)[1]))

    def test_gloss_parts_required(self):
        d = copy.deepcopy(GOOD)
        d["sentences"][0]["gloss"]["benefit"] = ""
        self.assertTrue(any("benefit" in m for m in self.run_check(d)[1]))

    def test_method_note_skeleton_spec_passes(self):
        spec = Path(__file__).resolve().parents[1] / "skills/reading-reference/assets/method-note/coverage_spec.json"
        r = subprocess.run([sys.executable, str(CHECK), str(spec)], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stdout)


if __name__ == "__main__":
    unittest.main()
