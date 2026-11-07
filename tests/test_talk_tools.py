"""Execute the talk helper scripts on a small fictional PDF (needs poppler and a TeX engine)."""

import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

CHECKOUT = Path(__file__).resolve().parents[1]
AUDIT = CHECKOUT / "skills/deck-from-references/scripts/deck_audit.py"
SHEET = CHECKOUT / "skills/deck-from-references/scripts/contact_sheet.py"
EXTRACT = CHECKOUT / "skills/deck-from-references/scripts/extract_code.py"
CROP = CHECKOUT / "skills/deck-from-references/scripts/crop_source.py"
MAP = CHECKOUT / "skills/paper-talk-planning/scripts/source_map.py"
NOTES = CHECKOUT / "skills/paper-talk-planning/scripts/notes_map.py"
SYMBOLS = CHECKOUT / "skills/paper-talk-planning/scripts/plan_symbols.py"
CARDS_TO_PLAN = CHECKOUT / "skills/paper-talk-planning/scripts/cards_to_plan.py"
PLAN = """**Assumed known**: `R^D`

- **1. [problem] Points near a curve**
- **Symbols introduced**: `x_i` = data points in `R^D` (p.3)
- **Symbols used**: `x_i`, `R^D`
- **2. [idea] A penalty**
- **Symbols used**: `L`, `x_i`
- **3. [computation] The Laplacian**
- **Symbols introduced**: `L` = D - W (p.11); `W` = weights (p.7)
- **Symbols used**: `L`, `W`, `y_i`
"""
TEX = r"""\documentclass[12pt]{article}
\begin{document}
\section{Introduction}
Some text about a fictional method with enough words to count on this page.
\begin{equation}x=1\end{equation}
\newpage
\subsection{Neighbor graphs}
Figure 1: A caption of the fictional figure.

Algorithm 1: Fictional procedure.
\end{document}
"""


NOTES_TEX = r"""\documentclass[12pt]{article}
\pagestyle{empty}
\begin{document}
\noindent Contents\par
\noindent 1\hspace{1em}Introduction \dotfill\ 2\par
\noindent 1.1\hspace{1em}Neighbor graphs \dotfill\ 2\par
\noindent 1.2\hspace{1em}Local charts \dotfill\ 3\par
\noindent 2\hspace{1em}Methods \dotfill\ 3\par
\noindent 2.1\hspace{1em}Spectral method \dotfill\ 3\par
\newpage
\noindent 1\hspace{1em}Introduction\par
\noindent 1.1\hspace{1em}Neighbor graphs\par
Background \textbar{} what a neighbor graph asks on the running example.\par
Source PDF p.4: the fictional survey, graphs.\par
84 t = np.linspace(0, 1, 5)\par
\newpage
\noindent 1.2\hspace{1em}Local charts\par
Background \textbar{} glue local charts. Added explanation: the speaker's reading.\par
\noindent 2\hspace{1em}Methods\par
\noindent 2.1\hspace{1em}Spectral method\par
Implementation \textbar{} the code. Written by AI for teaching.\par
\end{document}
"""


@unittest.skipUnless(all(shutil.which(x) for x in ("pdftotext", "pdfimages", "pdflatex")),
                     "needs poppler and pdflatex")
class TalkToolTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.dir = Path(tmp.name)
        (self.dir / "doc.tex").write_text(TEX)
        subprocess.run(["pdflatex", "-interaction=nonstopmode", "doc.tex"], cwd=self.dir,
                       capture_output=True, check=True)
        self.pdf = str(self.dir / "doc.pdf")

    def test_source_map_finds_headings_captions_equations(self):
        out = subprocess.run([sys.executable, str(MAP), self.pdf, "--json"],
                             capture_output=True, text=True, check=True).stdout
        pages = json.loads(out)
        self.assertEqual(len(pages), 2)
        self.assertIn("1 Introduction", pages[0]["headings"])
        self.assertEqual(pages[0]["equations"], [1])
        self.assertTrue(any(c.startswith("Figure 1") for c in pages[1]["captions"]))
        self.assertTrue(any(c.startswith("Algorithm 1") for c in pages[1]["captions"]))

    def test_cards_to_plan_writes_skeleton_only_for_checked_cards(self):
        def pair(t, s):
            return {"text": t, "source": s}
        cards = {"roots": [{"id": "R1", "question": "measure along the set", "source": "Survey 2020, p.4",
                            "shared_example": pair("rolled sheet", "Survey 2020, Fig.5"), "nodes": ["m-a"]}],
                 "nodes": {"m-a": {"uses": ["previous result"], "roots": ["R1"],
                                   "shared": pair("rolled sheet", "Survey 2020, Fig.5"),
                                   "lens": pair("geodesics", "Survey 2020, p.10"),
                                   "applied": pair("unrolled", "Survey 2020, Fig.5(a)"),
                                   "specific": pair("digits", "Author 1999, Fig.1"),
                                   "limit": dict(pair("dense", "speaker's reading"),
                                                 searched=[{"where": "Survey 2020, §5",
                                                            "outcome": "not found in the searched scope"}]),
                                   "code": "m-a code"}}}
        path = self.dir / "cards.json"
        path.write_text(json.dumps(cards))
        out = subprocess.run([sys.executable, str(CARDS_TO_PLAN), str(path)], capture_output=True, text=True)
        self.assertEqual(out.returncode, 0, out.stderr)
        self.assertIn("| Lens | geodesics (Survey 2020, p.10) |", out.stdout)
        self.assertIn("| R1 | measure along the set |", out.stdout)
        self.assertIn("dense (speaker's reading) [searched: not found]", out.stdout)
        cards["nodes"]["m-a"]["specific"] = pair("digits", "詳細版の応用例")
        path.write_text(json.dumps(cards))
        bad = subprocess.run([sys.executable, str(CARDS_TO_PLAN), str(path)], capture_output=True, text=True)
        self.assertEqual(bad.returncode, 1)
        self.assertEqual(bad.stdout, "")

    def test_plan_symbols_reports_use_before_introduction(self):
        plan = self.dir / "plan.md"
        plan.write_text(PLAN)
        result = subprocess.run([sys.executable, str(SYMBOLS), str(plan), "--json"],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 1)
        problems = {(p["page"], p["symbol"]): p for p in json.loads(result.stdout)["problems"]}
        self.assertEqual(problems[(2, "L")]["introduced_on"], 3)
        self.assertEqual(problems[(3, "y_i")]["problem"], "never introduced")
        self.assertNotIn((1, "R^D"), problems)

    def test_deck_audit_reports_words_drawn_over_each_other(self):
        (self.dir / "over.tex").write_text(
            "\\documentclass{article}\\pagestyle{empty}\\begin{document}\n"
            "Clean line of ordinary words.\\par\n"
            "\\makebox[0pt][l]{OBSTACLE}Overprinted text here.\n\\end{document}\n")
        subprocess.run(["pdflatex", "-interaction=nonstopmode", "over.tex"], cwd=self.dir,
                       capture_output=True, check=True)
        result = subprocess.run([sys.executable, str(AUDIT), str(self.dir / "over.pdf"), "--json"],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 1)
        report = json.loads(result.stdout)
        self.assertEqual(report["summary"]["overlap_pages"], [1])
        clean = subprocess.run([sys.executable, str(AUDIT), self.pdf, "--json"], capture_output=True, text=True)
        self.assertEqual(json.loads(clean.stdout)["summary"]["overlap_pages"], [])

    def test_notes_map_uses_contents_and_reports_roles_and_markers(self):
        (self.dir / "notes.tex").write_text(NOTES_TEX)
        subprocess.run(["pdflatex", "-interaction=nonstopmode", "notes.tex"], cwd=self.dir,
                       capture_output=True, check=True)
        out = subprocess.run([sys.executable, str(NOTES), str(self.dir / "notes.pdf"), "--json"],
                             capture_output=True, text=True, check=True).stdout
        subs = {x["id"]: x for x in json.loads(out)}
        self.assertEqual(list(subs), ["1", "1.1", "1.2", "2", "2.1"])  # code line "84 t = ..." rejected
        self.assertEqual(subs["1.1"]["roles"][0]["role"], "Background")
        self.assertIn("4", subs["1.1"]["source_pages"])
        self.assertIn("Added explanation", subs["1.2"]["markers"])
        self.assertIn("written by AI", subs["2.1"]["markers"])
        cards = subprocess.run([sys.executable, str(NOTES), str(self.dir / "notes.pdf"), "--cards"],
                               capture_output=True, text=True, check=True).stdout
        self.assertIn("### 1.1 Neighbor graphs", cards)
        self.assertIn("Root (ID from the root list)", cards)
        for field in ("Shared example", "Lens", "Applied view", "Specific example", "Limit example"):
            self.assertIn(field, cards)

    def test_crop_source_keeps_source_and_records_manifest(self):
        try:
            import PIL  # noqa: F401
        except ImportError:
            self.skipTest("needs Pillow")
        before = Path(self.pdf).read_bytes()
        out = self.dir / "fig.png"
        man = self.dir / "manifest.json"
        r = subprocess.run([sys.executable, str(CROP), self.pdf, "--page", "1", "--dpi", "100", "--box", "50,50,500,400",
                            "--trim", "--out", str(out), "--manifest", str(man)], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(Path(self.pdf).read_bytes(), before)  # the source is untouched
        entry = json.loads(man.read_text())[0]
        self.assertEqual(entry["page"], 1)
        self.assertEqual(entry["box"], [50, 50, 500, 400])
        self.assertEqual(len(entry["source_sha256"]), 64)
        bad = subprocess.run([sys.executable, str(CROP), self.pdf, "--page", "1", "--dpi", "100", "--box", "0,0,99999,99999",
                              "--out", str(self.dir / "bad.png")], capture_output=True, text=True)
        self.assertNotEqual(bad.returncode, 0)

    def test_deck_audit_counts_words_and_text_size(self):
        out = subprocess.run([sys.executable, str(AUDIT), self.pdf, "--json", "--max-words", "10"],
                             capture_output=True, text=True, check=True).stdout
        r = json.loads(out)
        self.assertEqual(r["summary"]["pages"], 2)
        self.assertIn(1, r["summary"]["heavy_pages"])  # page 1 has more than 10 words
        self.assertGreater(r["pages"][0]["median_height_over_width"], 0)

    @unittest.skipUnless(shutil.which("pdftoppm"), "needs pdftoppm")
    def test_contact_sheet_writes_png(self):
        try:
            import PIL  # noqa: F401
        except ImportError:
            self.skipTest("needs Pillow")
        out = self.dir / "sheet.png"
        subprocess.run([sys.executable, str(SHEET), str(out), f"{self.pdf}:1-2", "--cols", "2", "--width", "200"],
                       capture_output=True, text=True, check=True)
        self.assertGreater(out.stat().st_size, 1000)


class ExtractCodeTests(unittest.TestCase):
    SRC = 'def f(x):\n    """doc"""\n    y = x + 1\n    return y\n\n\ndef g(x):\n    return x\n'

    def run_tool(self, *extra):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        d = Path(tmp.name)
        (d / "m.py").write_text(self.SRC)
        r = subprocess.run([sys.executable, str(EXTRACT), str(d / "m.py"), "--functions", "f", "--out", str(d / "o.py"), *extra],
                           capture_output=True, text=True)
        return r, d

    def test_drops_docstring_and_places_marker(self):
        r, d = self.run_tool("--mark", "2:1:x + 1")
        self.assertEqual(r.returncode, 0, r.stderr)
        out = (d / "o.py").read_text()
        self.assertNotIn("doc", out)
        self.assertIn("y = x + 1(*@\\mkr{fix}{1}@*)", out)
        self.assertIn("f: L1-4", r.stdout)

    def test_line_range_excerpt_with_dedent(self):
        r, d = self.run_tool("--mark", "1:1:y")  # sanity: function mode still works
        self.assertNotEqual(r.returncode, 0)  # line 1 is the def line, no 'y' in it
        src = d / "m.py"
        out = d / "e.py"
        r2 = subprocess.run([sys.executable, str(EXTRACT), str(src), "--lines", "3-4", "--dedent", "--out", str(out)],
                            capture_output=True, text=True)
        self.assertEqual(r2.returncode, 0, r2.stderr)
        self.assertEqual(out.read_text(), "y = x + 1\nreturn y\n")
        self.assertIn("L3-4", r2.stdout)

    def test_roles_inherited_and_tidy(self):
        r, d = self.run_tool("--mark", "2:1:x + 1:inherited", "--mark", "3:0:return y:tidy")
        self.assertEqual(r.returncode, 0, r.stderr)
        out = (d / "o.py").read_text()
        self.assertIn("(*@\\mkr{inherited}{1}@*)", out)
        self.assertIn("@!    return y!@", out)

    def test_marker_on_changed_line_fails(self):
        r, _ = self.run_tool("--mark", "2:1:no such text")
        self.assertNotEqual(r.returncode, 0)


if __name__ == "__main__":
    unittest.main()
