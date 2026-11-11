"""Exercise the literal-fidelity comparison on a fictional English/Japanese pair."""

from pathlib import Path
import json
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "skills/japanese-translation/scripts/compare_translation.py"

EN = r"""
\newcommand{\R}{\mathbb R}
\section{Setting}
Let $f:\R\to\R$ be a tame function (see \cite{zed}). We call $f$ a glimmer if $f(0)=0$.
\begin{theorem}\label{thm:a} Every glimmer satisfies \[ f(x)\le 2|x|. \] \end{theorem}
\begin{proof} By \eqref{thm:a} and the definition. \end{proof}
"""
JA_OK = r"""
\newcommand{\R}{\mathbb{R}}
\section{設定}
$f:\mathbb R\to\mathbb R$ を穏やかな関数とする（\cite{zed}を見よ）。$f(0)=0$ のとき $f$ を glimmer と呼ぶ。
\begin{theorem}\label{thm:a} 任意の glimmer は \[ f(x) \le 2 |x| \] を満たす。 \end{theorem}
\begin{proof} \eqref{thm:a} と定義による。 \end{proof}
"""
JA_BAD = r"""
\newcommand{\R}{\mathbb{R}}
\section{設定}
$f:\R\to\R$ を穏やかな関数（つまり，連続で，原点の近くで滑らかなもの）とする。$f(0)=0$ のとき $f$ を glimmer と呼ぶ。
\begin{theorem}\label{thm:a} 任意の glimmer は \[ f(x)\le 3|x| \] を満たす。 \end{theorem}
"""


def run(*args):
    return subprocess.run([sys.executable, str(SCRIPT), *map(str, args)], capture_output=True, text=True)


class CompareTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        d = Path(self.tmp.name)
        self.en, self.ok, self.bad = d / "en.tex", d / "ok.tex", d / "bad.tex"
        self.en.write_text(EN, encoding="utf-8")
        self.ok.write_text(JA_OK, encoding="utf-8")
        self.bad.write_text(JA_BAD, encoding="utf-8")

    def tearDown(self):
        self.tmp.cleanup()

    def test_faithful_translation_passes_strict(self):
        r = run(self.en, self.ok, "--strict")
        self.assertEqual(r.returncode, 0, r.stdout)

    def test_changed_formula_dropped_proof_citation_and_added_gloss_are_flagged(self):
        r = run(self.en, self.bad, "--json", "--strict")
        self.assertEqual(r.returncode, 1)
        out = json.loads(r.stdout)
        self.assertTrue(out["formulas"]["only_in_source"] and out["formulas"]["only_in_translation"])
        self.assertTrue(out["environment_sequence"]["differences"])
        self.assertTrue(out["citations"]["only_in_source"])
        self.assertEqual(out["parentheticals"]["translation_japanese_only"], 1)

    def test_words_inside_text_in_math_are_not_compared(self):
        en = Path(self.tmp.name) / "en2.tex"
        ja = Path(self.tmp.name) / "ja2.tex"
        en.write_text(r"Let $h \text{ be bounded}$ here.", encoding="utf-8")
        ja.write_text(r"ここで $h \text{ は有界}$ とする。", encoding="utf-8")
        self.assertEqual(run(en, ja, "--strict").returncode, 0)

    def test_macros_are_expanded_before_comparison(self):
        out = json.loads(run(self.en, self.ok, "--json").stdout)
        self.assertEqual(out["formulas"]["only_in_source"], [])


if __name__ == "__main__":
    unittest.main()
