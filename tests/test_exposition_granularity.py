"""Exercise the granularity profile on a fictional corpus (no private material)."""

from pathlib import Path
import json
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "skills/exposition-granularity/scripts/granularity.py"


def doc(i):
    filler = " ".join(f"Section {j}: for the case {i} we obtain a bound on the quantity number {i * 7 + j}." for j in range(12))
    return (
        f"Let X be a tessellated manifold. A tessellated manifold has a boundary map. "
        f"We call a map f a wrenched index if f preserves the tessellated manifold structure. "
        f"Every wrenched index extends to the tessellated manifold, and a wrenched index is unique. "
        + filler
    )


def run(*args):
    return subprocess.run([sys.executable, str(SCRIPT), *map(str, args)], capture_output=True, text=True)


class GranularityTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)
        self.files = []
        for i in range(10):
            p = self.dir / f"d{i}.txt"
            p.write_text(doc(i), encoding="utf-8")
            self.files.append(p)
        self.profile = self.dir / "profile.json"
        r = run("profile", *self.files, "--out", self.profile)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.p = json.loads(self.profile.read_text(encoding="utf-8"))

    def tearDown(self):
        self.tmp.cleanup()

    def test_profile_separates_assumed_and_defined_terms(self):
        assumed = {r["term"] for r in self.p["assumed"]}
        defined = {r["term"] for r in self.p["defined"]}
        self.assertIn("tessellated manifold", assumed)
        self.assertIn("wrenched index", defined)
        self.assertNotIn("wrenched index", assumed)
        self.assertEqual(self.p["warning"], "")

    def test_check_flags_over_explanation_and_missing_definition(self):
        art = self.dir / "art.txt"
        art.write_text("We call a space a tessellated manifold if it has tiles. "
                       "Every wrenched index is stable, and a wrenched index commutes with itself.", encoding="utf-8")
        r = run("check", self.profile, art)
        self.assertEqual(r.returncode, 0, r.stderr)
        out = json.loads(r.stdout)
        self.assertIn("tessellated manifold", out["possibly_over_explained"])
        self.assertIn("wrenched index", out["possibly_undefined"])

    def test_japanese_artifact_is_not_measured(self):
        art = self.dir / "ja.txt"
        art.write_text("これは日本語の文章です。定義を与えます。" * 20, encoding="utf-8")
        out = json.loads(run("check", self.profile, art).stdout)
        self.assertTrue(any("literal translation" in n for n in out["notes"]))

    def test_words_not_in_corpus_are_listed(self):
        art = self.dir / "odd.txt"
        art.write_text("Every tessellated manifold has a gloomy representative, and a gloomy representative is unique.",
                       encoding="utf-8")
        out = json.loads(run("check", self.profile, art).stdout)
        words = {w["word"] for w in out["words_not_in_corpus"]}
        self.assertIn("gloomy", words)
        self.assertNotIn("tessellated", words)

    def test_tex_markup_is_not_read_as_vocabulary(self):
        art = self.dir / "a.tex"
        art.write_text("\\begin{itemize}\\item Let $\\mathcal G$ be a tessellated manifold. \\textbf{Gloomy} things.\\end{itemize}",
                       encoding="utf-8")
        out = json.loads(run("check", self.profile, art).stdout)
        words = {w["word"] for w in out["words_not_in_corpus"]}
        self.assertNotIn("mathcal", words)
        self.assertNotIn("itemize", words)

    def test_density_above_every_document_is_reported(self):
        art = self.dir / "dense.txt"
        art.write_text(" ".join("We call a thing a widget number %d." % i for i in range(40)), encoding="utf-8")
        out = json.loads(run("check", self.profile, art).stdout)
        self.assertIn("above", out["density"]["naming_phrases_per_1k"]["verdict"])

    def test_refuses_too_few_documents(self):
        r = run("profile", self.files[0], self.files[1], "--out", self.dir / "x.json")
        self.assertNotEqual(r.returncode, 0)

    def test_leave_one_out_reports_every_document(self):
        r = run("loo", *self.files)
        self.assertEqual(r.returncode, 0, r.stderr)
        rows = json.loads(r.stdout)
        self.assertEqual(len(rows), 10)
        self.assertTrue(all(x["own_definitions_on_assumed_terms"] == 0 for x in rows))


if __name__ == "__main__":
    unittest.main()
