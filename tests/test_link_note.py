"""Execute link_note.py on a small fictional note .aux and deck source."""

from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "skills/deck-from-references/scripts/link_note.py"

AUX = r"""\relax
\newlabel{sec:method}{{2}{5}{Method}{section.2}{}}
\newlabel{eq:score}{{3}{7}{}{equation.3}{}}
\newlabel{sec:bib}{{参考文献}{12}{}{}{}}
\newlabel{cite:a}{{}{9}{}{}{}}
\newlabel{sec:method@x}{{9}{9}{}{}{}}
"""

DECK = r"""\begin{frame}[plain]Title\end{frame}
\begin{frame}\frametitle{1. First}\noteref{sec:method,eq:score}\src{p.1}\end{frame}
\begin{frame}\frametitle{2. Second}\nonote{deck only}\src{p.2}\end{frame}
"""


class LinkNoteTests(unittest.TestCase):
    def run_cli(self, *args):
        return subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True, text=True)

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)
        (self.dir / "n.aux").write_text(AUX)
        (self.dir / "deck.tex").write_text(DECK)

    def tearDown(self):
        self.tmp.cleanup()

    def test_build_writes_labels_with_pages(self):
        r = self.run_cli("build", str(self.dir / "n.aux"), "--pdf", "n.pdf", "--out", str(self.dir / "l.tex"))
        self.assertEqual(r.returncode, 0, r.stderr)
        text = (self.dir / "l.tex").read_text()
        self.assertIn(r"\notedef{sec:method}{\S{}2}{5}", text)
        self.assertIn(r"\notedef{eq:score}{式(3)}{7}", text)
        self.assertIn(r"\notedef{sec:bib}{参考文献}{12}", text)
        self.assertNotIn("cite:a", text)
        self.assertNotIn("@x", text)

    def test_check_passes_and_reports_missing(self):
        ok = self.run_cli("check", str(self.dir / "deck.tex"), "--aux", str(self.dir / "n.aux"))
        self.assertEqual(ok.returncode, 0, ok.stdout)
        (self.dir / "deck.tex").write_text(DECK + r"\begin{frame}\frametitle{3. Third}\src{p.3}\end{frame}"
                                           + r"\begin{frame}\frametitle{4. Fourth}\noteref{sec:nope}\end{frame}")
        bad = self.run_cli("check", str(self.dir / "deck.tex"), "--aux", str(self.dir / "n.aux"))
        self.assertEqual(bad.returncode, 1)
        self.assertIn("page 3: no \\noteref", bad.stdout)
        self.assertIn("sec:nope", bad.stdout)

    def test_reverse_lists_deck_pages(self):
        r = self.run_cli("reverse", str(self.dir / "deck.tex"), "--aux", str(self.dir / "n.aux"),
                         "--out", str(self.dir / "m.tex"))
        self.assertEqual(r.returncode, 0, r.stderr)
        text = (self.dir / "m.tex").read_text()
        self.assertIn("R1", text)
        self.assertNotIn("R2", text)


if __name__ == "__main__":
    unittest.main()
