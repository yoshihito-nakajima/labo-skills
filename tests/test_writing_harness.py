"""Execute the writing-harness cards.py on a fictional paper (no private material)."""

from pathlib import Path
import json
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
CARDS = ROOT / "skills/writing-harness/scripts/cards.py"
FIXTURE = ROOT / "tests/fixtures/writing-harness"


class WritingHarnessTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.ws = Path(self.tmp.name)
        (self.ws / ".git").mkdir()  # marks the workspace root for graph paths
        self.h = self.ws / "writing/settled/harness"
        shutil.copytree(FIXTURE, self.h)

    def tearDown(self):
        self.tmp.cleanup()

    def run_cards(self, *args, cwd=None):
        return subprocess.run([sys.executable, str(CARDS), *map(str, args)], cwd=cwd or self.h,
                              capture_output=True, text=True)

    def check_json(self):
        r = self.run_cards("check", "--json")
        return r.returncode, json.loads(r.stdout)

    def edit(self, rel, old, new):
        p = self.h / rel
        text = p.read_text()
        self.assertIn(old, text)
        p.write_text(text.replace(old, new))

    def test_fixture_is_clean_and_found_from_subdirectory(self):
        code, out = self.check_json()
        self.assertEqual((code, out["errors"], out["warnings"]), (0, [], []))
        self.assertEqual(out["cards"], 5)
        r = self.run_cards("status", cwd=self.h / "cards/prop")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertRegex(r.stdout, r"gap-free +2\n")
        self.assertIn("[thm-sum-settled]", r.stdout)

    def test_changed_statement_makes_prose_stale_until_anchored(self):
        self.edit("cards/prop/thm-sum-settled.md", r"\le\max", r"\leq\max")
        code, out = self.check_json()
        self.assertEqual(code, 0)
        stale = sorted(w for w in out["warnings"] if w.startswith("STALE"))
        self.assertEqual(len(stale), 2)
        self.assertTrue(all("thm-sum-settled changed" in w for w in stale))
        r = self.run_cards("impact", "lem-tail")
        self.assertIn("facts to recheck: lem-tail, thm-sum-settled", r.stdout)
        self.assertIn("explanations to reread: x-proof-sum, x-why-settled", r.stdout)
        for x in ("x-why-settled", "x-proof-sum"):
            self.assertEqual(self.run_cards("anchor", x).returncode, 0)
        self.assertEqual(self.check_json()[1]["warnings"], [])

    def test_structure_order_and_unused_facts(self):
        self.edit("structure.yaml", "      - lem-tail\n      - thm-sum-settled\n",
                  "      - thm-sum-settled\n      - lem-tail\n")
        warnings = self.check_json()[1]["warnings"]
        self.assertIn("FORWARD thm-sum-settled uses lem-tail (later)", warnings)
        self.edit("structure.yaml", "      - lem-tail\n", "")
        warnings = self.check_json()[1]["warnings"]
        self.assertIn("MISSING thm-sum-settled needs lem-tail, which is not in the structure", warnings)
        self.assertIn("UNUSED fact cards (1): lem-tail", warnings)

    def test_schema_errors(self):
        self.edit("cards/prop/lem-tail.md", "status: gap-free", "status: lean")
        self.edit("cards/def/def-settled.md", "requires: []", "requires: [thm-sum-settled]")
        code, out = self.check_json()
        self.assertEqual(code, 1)
        self.assertIn("lem-tail: status lean but no lean declarations", out["errors"])
        self.assertTrue(any(e.startswith("cycle: ") for e in out["errors"]))

    def test_terms_with_and_without_assumed_profile(self):
        r = self.run_cards("terms", "--json")
        self.assertEqual(r.returncode, 1)
        groups = json.loads(r.stdout)
        self.assertEqual([t["term"] for t in groups["unregistered"]], ["limit", "tail"])
        self.assertEqual([t["term"] for t in groups["undecided"]], ["settling index"])
        self.assertEqual(groups["decided"][0]["info"], "def-settled")
        self.assertEqual([t["term"] for t in groups["standard"]], ["sequence"])
        profile = self.ws / "profile.json"
        # the shape written by exposition-granularity's `profile --out`
        profile.write_text(json.dumps({"assumed": [{"term": "limit", "docs_using": 9, "docs_defining": 0},
                                                   {"term": "tail", "docs_using": 8, "docs_defining": 0},
                                                   {"term": "sequence", "docs_using": 10, "docs_defining": 0}]}))
        r = self.run_cards("terms", "--json", "--assumed", profile)
        self.assertEqual(r.returncode, 0, r.stdout)
        groups = json.loads(r.stdout)
        self.assertEqual([t["term"] for t in groups["assumed"]], ["limit", "tail"])
        self.assertEqual([t["term"] for t in groups["standard"]], ["sequence"])

    def test_graph_passes_the_shared_dependency_checker(self):
        r = self.run_cards("graph")
        self.assertEqual(r.returncode, 0, r.stderr)
        graph = (self.h / "dependencies.yaml").read_text()
        self.assertIn("path: writing/settled/harness/cards/prop/lem-tail.md", graph)
        r = subprocess.run([sys.executable, "-B", str(ROOT / "scripts/labo.py"), "dependencies", "check",
                            "--workspace", str(self.ws), "--graph", "writing/settled/harness/dependencies.yaml"],
                           capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("Topological order: def-settled, lem-tail, thm-sum-settled", r.stdout)

    def test_render_uses_author_proof_refs_and_language(self):
        r = self.run_cards("render")
        self.assertEqual(r.returncode, 0, r.stderr)
        tex = (self.h / "paper/cards.tex").read_text()
        self.assertTrue(tex.startswith("% !TeX program = pdflatex"))
        self.assertIn(r"\begin{lemma}[{Tails}]\label{lem:tail}", tex)
        self.assertIn(r"By \ref{def:settled}", tex)
        self.assertIn(r"\begin{theorem}[{Sums \cite[Lemma~2]{Fictional2001}}]", tex)
        self.assertIn("% agent reference proof (lem-tail)", tex)
        self.assertIn("Beyond the larger of the two indices", tex)  # the author's proof wins
        self.assertNotIn("% agent reference proof (thm-sum-settled)", tex)
        self.assertEqual(tex.count(r"\begin{proof}"), 2)
        self.assertNotEqual(self.run_cards("render", "--out", "main.tex").returncode, 0)
        r = self.run_cards("render", "--sections", "1", "--out", "part1.tex")
        part = (self.h / "paper/part1.tex").read_text()
        self.assertIn(r"\begin{definition}", part)
        self.assertNotIn(r"\begin{lemma}", part)
        self.edit("harness.toml", 'language = "en"', 'language = "ja"')
        self.run_cards("render")
        self.assertIn(r"\documentclass[uplatex,dvipdfmx,11pt]{jsarticle}", (self.h / "paper/cards.tex").read_text())

    @unittest.skipUnless(shutil.which("pdflatex"), "pdflatex not installed")
    def test_rendered_tex_compiles(self):
        self.run_cards("render")
        for _ in range(2):
            r = subprocess.run(["pdflatex", "-interaction=nonstopmode", "-halt-on-error", "cards.tex"],
                               cwd=self.h / "paper", capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, r.stdout[-2000:])
        self.assertNotRegex(r.stdout, r"Reference `[^']*' .*undefined")

    def test_html_viewer(self):
        r = self.run_cards("html")
        self.assertEqual(r.returncode, 0, r.stderr)
        page = (self.h / "html/index.html").read_text()
        self.assertEqual(len(re.findall(r"<article id=", page)), 5)
        self.assertIn('href="#def-settled"', page)
        self.assertIn("Is the bound N(a+b)", page)
        self.assertFalse((self.h / "index.html").exists())  # no list unless asked
        other = self.h / "other"
        other.mkdir()
        (other / "index.html").write_text("x")
        with open(self.h / "harness.toml", "a") as f:
            f.write('\n[html_index]\ntitle = "Viewers"\nlinks = [{ text = "Back", href = "../" }]\n')
        self.assertEqual(self.run_cards("html").returncode, 0)
        index = (self.h / "index.html").read_text()
        self.assertIn('<a href="html/">html</a>', index)
        self.assertIn('<a href="other/">other</a>', index)
        self.assertIn('<a href="../">Back</a>', index)

    def test_reading_page(self):
        r = self.run_cards("read")
        self.assertEqual(r.returncode, 0, r.stderr)
        page = (self.h / "html/read.html").read_text()
        self.assertIn('id="lem-tail"', page)
        self.assertIn('<span class="kname">Lemma 2.1</span>', page)
        self.assertIn('<a class="ref" href="#def-settled">Definition 1.1</a>', page)  # bare card id in a proof
        self.assertIn("Beyond the larger of the two indices", page)  # the author's proof
        self.assertIn("Copy to clipboard", page)  # language en
        self.assertNotIn("{{", page)

    def test_card_ids_resolve_next_to_japanese_text(self):
        # Japanese text carries no space before or after a card id (TeX spaces it).
        sys.path.insert(0, str(CARDS.parent))
        import cards as cards_mod

        class Card:
            def __init__(self, cid):
                self.id, self.is_fact, self.meta = cid, True, {'label': 'x:' + cid}

        found = cards_mod.link_refs('p1-lemとp1-lem．', {'p1-lem': Card('p1-lem')})
        self.assertNotIn('p1-lem と', found)
        self.assertEqual(found.count('\\ref{'), 2, found)

    def test_proof_step_labels_on_display(self):
        sys.path.insert(0, str(CARDS.parent))
        import reader
        plain = "(1) First.\n(2) Second."
        self.assertEqual(reader.proof_display("x", plain, set()), "First.\n\nSecond.")
        cited = "(1) First.\n(2) By (1), done."
        shown = reader.proof_display("x", cited, {"x"})
        self.assertIn("\\emph{Step 2.} By Step 1, done.", shown)
        self.assertEqual(reader.external_steps_display("x proof (2)", {"x"}), "x proof Step 2")

    def test_comment_layer_injects_once(self):
        sys.path.insert(0, str(CARDS.parent))
        import comment_layer
        page = "<html><body><h1>T</h1><p>x</p></body></html>"
        once = comment_layer.inject(page, "ja")
        twice = comment_layer.inject(once, "ja")
        self.assertEqual(once, twice)
        self.assertIn("window.CommentLayer", once)
        self.assertLess(once.index("cl-add"), once.index("</body>"))

    def test_init_scaffolds_and_refuses_overwrite(self):
        new = self.ws / "writing/other/harness"
        r = self.run_cards("init", new, cwd=self.ws)
        self.assertEqual(r.returncode, 0, r.stderr)
        for name in ("harness.toml", "story.md", "vocab.toml", "style.toml", "structure.yaml"):
            self.assertTrue((new / name).is_file(), name)
        self.assertTrue((new / "cards/prop").is_dir())
        self.assertEqual(self.run_cards("check", cwd=new).returncode, 0)
        r = self.run_cards("init", new, cwd=self.ws)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("refusing to overwrite", r.stderr)


if __name__ == "__main__":
    unittest.main()
