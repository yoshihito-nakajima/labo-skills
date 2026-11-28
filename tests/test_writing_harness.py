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

    def test_evidence_from_another_harness_makes_text_stale(self):
        fps = self.h / "fps.json"
        fps.write_text(json.dumps({"code-a": "11111111"}))
        (self.h / "producer.py").write_text("import pathlib\nprint(pathlib.Path('fps.json').read_text())\n")
        with (self.h / "harness.toml").open("a") as f:
            f.write('\n[evidence.lab]\ncommand = ["{python}", "producer.py"]\n')
        self.edit("cards/expl/x-why-settled.md", "anchors:", "evidence:\n- lab:code-a\nanchors:")
        code, out = self.check_json()
        self.assertIn("x-why-settled: no anchor for evidence lab:code-a (run anchor)", out["warnings"])
        r = self.run_cards("anchor", "x-why-settled")
        self.assertEqual(r.returncode, 0, r.stderr)
        code, out = self.check_json()
        self.assertEqual((out["errors"], out["warnings"]), ([], []))
        fps.write_text(json.dumps({"code-a": "22222222"}))
        code, out = self.check_json()
        self.assertEqual(out["warnings"],
                         ["STALE x-why-settled: evidence lab:code-a changed since this text was written"])
        self.edit("cards/expl/x-why-settled.md", "- lab:code-a", "- lab:code-b")
        code, out = self.check_json()
        self.assertIn("x-why-settled: evidence lab:code-b not found", out["errors"])

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

    def test_section_labels_and_cref(self):
        self.edit("structure.yaml", "  - title: Definitions\n", "  - title: Definitions\n    label: sec:defs\n")
        self.edit("structure.yaml", "      - x-why-settled\n", "      - {subsection: Why, label: sec:why}\n      - x-why-settled\n")
        self.run_cards("render")
        tex = (self.h / "paper/cards.tex").read_text()
        self.assertIn(r"\section{Definitions}\label{sec:defs}", tex)
        self.assertIn(r"\subsection{Why}\label{sec:why}", tex)
        self.assertIn(r"By \ref{def:settled}", tex)
        p = self.h / "harness.toml"
        p.write_text(p.read_text() + '\nref_command = "Cref"\n')
        self.run_cards("render")
        self.assertIn(r"By \Cref{def:settled}", (self.h / "paper/cards.tex").read_text())

    def add_notes_section(self, title):
        (self.h / "cards/expl/x-notes.md").write_text(
            "---\nid: x-notes\nkind: explanation\nrole: remark\nexplains: []\n---\n"
            "By \\eqref{eq:bound} and \\Cref{sec:defs}, the index is controlled.\n"
            "\\[\nN(a+b)\\le\\max\\{N(a),N(b)\\}\\label{eq:bound}\n\\]\n"
            "Compare the named display \\eqref{eq:named}.\n"
            "\\[\na_n=a_M\\tag{S}\\label{eq:named}\n\\]\n")
        self.edit("structure.yaml", "  - title: Definitions\n", "  - title: Definitions\n    label: sec:defs\n")
        with open(self.h / "structure.yaml", "a") as f:
            f.write(f"  - title: '{title}'\n    items:\n      - x-notes\n")

    def test_labelled_displays_and_references_in_headings(self):
        self.add_notes_section(r"Notes on \Cref{thm:sum}")
        with open(self.h / "harness.toml", "a") as f:
            f.write('ref_command = "Cref"\n')
        (self.h / "macros.tex").write_text("\\usepackage[capitalize,noabbrev]{cleveref}\n")
        code, out = self.check_json()
        self.assertEqual((code, out["warnings"]), (0, []))
        self.assertEqual(self.run_cards("render").returncode, 0)
        tex = (self.h / "paper/cards.tex").read_text()
        self.assertIn(r"\section{\texorpdfstring{Notes on \Cref{thm:sum}}{Notes on Theorem 2.2}}", tex)
        self.assertIn("\\tag{3.1}\\label{eq:bound}", tex)
        self.assertIn(r"a_n=a_M\tag{S}\label{eq:named}", tex)  # a named display keeps its name
        self.assertEqual(self.run_cards("read").returncode, 0)
        page = (self.h / "html/read.html").read_text()
        self.assertIn("3　Notes on Theorem 2.2</h2>", page)
        self.assertIn('<a class="ref" href="#x-notes">(3.1)</a>', page)
        self.assertIn('<a class="ref" href="#x-notes">(S)</a>', page)
        self.assertIn('<a class="ref" href="#sec-1">Section 1</a>', page)
        self.assertIn("\\tag{3.1}", page)
        self.assertNotIn("label{eq:bound}", page)
        if shutil.which("pdflatex"):
            for _ in range(2):
                r = subprocess.run(["pdflatex", "-interaction=nonstopmode", "-halt-on-error", "cards.tex"],
                                   cwd=self.h / "paper", capture_output=True, text=True)
                self.assertEqual(r.returncode, 0, r.stdout[-2000:])
            self.assertNotRegex(r.stdout, r"Reference `[^']*' .*undefined")
            aux = (self.h / "paper/cards.aux").read_text()
            self.assertRegex(aux, r"\\newlabel\{eq:bound\}\{\{\{3\.1\}\}")
            self.assertIn("[equation]", aux)  # cleveref sees an equation

    def test_check_warns_about_hand_typed_numbers_and_unknown_labels(self):
        self.add_notes_section("Proof of Theorem 2.2")
        self.edit("cards/expl/x-why-settled.md", "form a vector space.",
                  "form a vector space (Section 2 and (2.1); compare [3, Theorem 2.1] and \\Cref{sec:none}).\n"
                  "\\[\nx=y\\tag{2.1}\n\\]")
        code, out = self.check_json()
        self.assertEqual(code, 0)
        warns = out["warnings"]
        hand = sorted(w for w in warns if w.startswith("HANDNUM"))
        self.assertEqual(len(hand), 4, hand)
        for n in ('"Section 2"', '"(2.1)"', '"\\tag{2.1}"', 'structure: "Theorem 2.2"'):
            self.assertTrue(any(n in w for w in hand), (n, hand))
        self.assertFalse(any("Theorem 2.1" in w for w in hand))  # a citation locator
        self.assertTrue(any(w.startswith("UNRESOLVED x-why-settled") and "sec:none" in w for w in warns), warns)

    def test_reference_with_several_labels(self):
        self.edit("cards/expl/x-why-settled.md", "form a vector space.",
                  "form a vector space (see \\Cref{lem:tail,lem:none}).")
        code, out = self.check_json()
        unresolved = [w for w in out["warnings"] if w.startswith("UNRESOLVED")]
        self.assertEqual(len(unresolved), 1, unresolved)
        self.assertIn("lem:none", unresolved[0])
        self.assertEqual(self.run_cards("read").returncode, 0)
        page = (self.h / "html/read.html").read_text()
        self.assertNotIn("lem:tail,", page)

    def test_phrase_table_and_exemplar_comparison(self):
        self.edit("cards/expl/x-why-settled.md", "form a vector space.",
                  "form a vector space. The bound gives the claim, and one has $x=y$.")
        with open(self.h / "style.toml", "a") as f:
            f.write("\n[[phrase]]\navoid = '\\bgives?\\b'\nuse = 'it follows from ... that'\n"
                    "basis = 'fictional exemplar'\n")
        code, out = self.check_json()
        self.assertEqual(code, 0)
        phrase = [w for w in out["warnings"] if w.startswith("PHRASE")]
        self.assertEqual(len(phrase), 1, phrase)
        self.assertIn("x-why-settled", phrase[0])
        self.assertIn("it follows from ... that", phrase[0])
        ex = self.ws / "exemplar.tex"
        ex.write_text("Let $x$ be given. Then it holds that $x=y$. It follows from (1) that $y=x$.\n" * 5)
        r = self.run_cards("exemplar", ex, "--min", "1")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertRegex(r.stdout, r"\\bgives\?\\b +0\.0 / +[1-9]")
        self.assertIn("never in the exemplar", r.stdout)
        self.assertIn("one has M", r.stdout)

    def test_unnumbered_trailing_section(self):
        with open(self.h / "structure.yaml", "a") as f:
            f.write("  - title: References\n    numbered: false\n    label: sec:refs\n    items:\n      - x-why-settled\n")
        self.edit("structure.yaml", "      - x-why-settled\n      - lem-tail\n", "      - lem-tail\n")
        self.assertEqual(self.run_cards("render").returncode, 0)
        tex = (self.h / "paper/cards.tex").read_text()
        self.assertIn("\\section*{References}", tex)
        self.assertNotIn("\\label{sec:refs}", tex)
        self.assertEqual(self.run_cards("read").returncode, 0)
        page = (self.h / "html/read.html").read_text()
        self.assertIn(">References</h2>", page)
        self.assertIn(">2　Results</h2>", page)

    def test_placement_of_lemmas_by_first_use(self):
        (self.h / "cards/prop/lem-head.md").write_text(
            "---\nid: lem-head\nkind: lemma\nlabel: lem:head\nstatus: stated\nrequires: []\n---\n"
            "## Statement\nEvery settled sequence has a first term.\n")
        self.edit("cards/prop/lem-tail.md", "requires: [def-settled]", "requires: [def-settled, lem-head]")
        self.edit("structure.yaml", "      - def-settled\n", "      - def-settled\n      - lem-head\n")
        code, out = self.check_json()
        placement = [w for w in out["warnings"] if w.startswith("PLACEMENT")]
        self.assertEqual(placement, ["PLACEMENT lem-head is first used by lem-tail in another section; "
                                     "place it just before that use"])
        # The closing lemma of a section of devices may serve the theorem of a later section.
        self.edit("structure.yaml", "      - def-settled\n      - lem-head\n",
                  "      - def-settled\n  - title: Devices\n    items:\n      - lem-head\n      - lem-tail\n")
        self.edit("structure.yaml", "      - x-why-settled\n      - lem-tail\n", "      - x-why-settled\n")
        code, out = self.check_json()
        self.assertEqual([w for w in out["warnings"] if w.startswith("PLACEMENT")], [], out["warnings"])

    def test_placement_allows_tools_of_the_main_proof(self):
        (self.h / "cards/prop/lem-head.md").write_text(
            "---\nid: lem-head\nkind: lemma\nlabel: lem:head\nstatus: stated\nrequires: []\n---\n"
            "## Statement\nEvery settled sequence has a first term.\n")
        self.edit("cards/prop/lem-tail.md", "requires: [def-settled]", "requires: [def-settled, lem-head]")
        self.edit("structure.yaml", "      - def-settled\n",
                  "      - def-settled\n  - title: Devices\n    items:\n      - lem-head\n      - x-head-note\n")
        (self.h / "cards/expl/x-head-note.md").write_text(
            "---\nid: x-head-note\nkind: explanation\nrole: transition\nexplains: []\n---\nWe now turn to the results.\n")
        code, out = self.check_json()
        self.assertEqual([w for w in out["warnings"] if w.startswith("PLACEMENT")],
                         ["PLACEMENT lem-head is first used by lem-tail in another section; "
                          "place it just before that use"])
        # Used by two results of the section that proves the theorem: a tool of the main proof.
        self.edit("cards/prop/thm-sum-settled.md", "requires: [def-settled, lem-tail]",
                  "requires: [def-settled, lem-tail, lem-head]")
        code, out = self.check_json()
        self.assertEqual([w for w in out["warnings"] if w.startswith("PLACEMENT")], [], out["warnings"])

    def test_proof_load_names_and_symbols(self):
        (self.h / "cards/prop/lem-load.md").write_text(
            "---\nid: lem-load\nkind: lemma\nlabel: lem:load\nstatus: drafted\nrequires: []\n---\n"
            "## Statement\nThe sum is finite.\n\n## Proof\n"
            "We set $\\nu\\coloneqq a+b$. The sum is a number. It is real. Then $\\nu$ is finite, and $\\nu+\\nu$ is finite. "
            "Let $c\\coloneqq 2$. By Fatou's lemma, the sum is finite. This completes the proof.\n")
        self.edit("structure.yaml", "      - def-settled\n", "      - def-settled\n      - lem-load\n")
        code, out = self.check_json()
        self.assertEqual([w for w in out["warnings"] if w.split()[0] in ("NAMEFIRST", "ONCESYMBOL")], [])
        text = subprocess.run([sys.executable, str(CARDS), "--root", str(self.h), "load"],
                              capture_output=True, text=True).stdout
        self.assertIn("NAMEFIRST", text)
        self.assertIn("ONCESYMBOL [c]", text)
        r = subprocess.run([sys.executable, str(CARDS), "--root", str(self.h), "load", "--json"],
                           capture_output=True, text=True)
        rows = {x["id"]: x for x in json.loads(r.stdout)}
        self.assertEqual(rows["lem-load"]["symbols"], [["\\nu", 3], ["c", 0]])
        self.assertEqual(rows["lem-load"]["tools"], ["Fatou's lemma"])
        self.assertEqual(rows["lem-load"]["named_ahead"], ["\\nu"])

    def test_prose_in_displays_is_reported(self):
        self.edit("cards/prop/lem-tail.md", "## Statement\n",
                  "## Statement\n\\[\na_n\\to a\\quad\\text{at each point }n\\text{ of the tail set}\n\\]\n"
                  "\\[\na_n=a\\quad\\text{for all }n\\geq N\n\\]\n")
        code, out = self.check_json()
        shown = [w for w in out["warnings"] if w.startswith("DISPLAYTEXT")]
        self.assertEqual(len(shown), 1, out["warnings"])
        self.assertIn("lem-tail", shown[0])

    def test_remark_card_is_numbered_without_proof(self):
        (self.h / "cards/prop/rem-tail.md").write_text(
            "---\nid: rem-tail\nkind: remark\nlabel: rem:tail\nstatus: drafted\nrequires: [lem-tail]\n---\n"
            "## Statement\nBy \\Cref{lem:tail}, the tail is constant. In particular, it is bounded.\n")
        self.edit("structure.yaml", "      - lem-tail\n", "      - lem-tail\n      - rem-tail\n")
        with open(self.h / "style.toml", "a") as f:
            f.write("\n[[phrase]]\navoid = '\\bIn particular\\b'\nsection = 'Statement'\n"
                    "use = 'a separate assertion'\nbasis = 'fictional rule'\n")
        code, out = self.check_json()
        self.assertEqual(code, 0, out)
        phrase = [w for w in out["warnings"] if w.startswith("PHRASE")]
        self.assertEqual(len(phrase), 1, phrase)
        self.assertIn("rem-tail", phrase[0])
        self.assertEqual(self.run_cards("render").returncode, 0)
        tex = (self.h / "paper/cards.tex").read_text()
        self.assertIn("\\begin{remark}\\label{rem:tail}", tex)
        self.assertEqual(self.run_cards("read").returncode, 0)
        self.assertIn("Remark 2.2", (self.h / "html/read.html").read_text())

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
        math = "(1) First.\n(2) By (1), $o(1)+\\lambda^{(2)}$ and \\[f(1)\\]."
        shown = reader.proof_display("x", math, {"x"})
        self.assertIn("By Step 1, $o(1)+\\lambda^{(2)}$ and \\[f(1)\\].", shown)

    def test_statement_first_proof_later(self):
        self.edit("structure.yaml", "      - lem-tail\n      - thm-sum-settled\n",
                  "      - {card: thm-sum-settled, proof: later}\n      - lem-tail\n      - {proof_of: thm-sum-settled}\n")
        code, data = self.check_json()
        self.assertEqual(code, 0, data)
        self.assertFalse([w for w in data["warnings"] if w.startswith("FORWARD thm-sum-settled")])
        self.assertEqual(self.run_cards("render").returncode, 0)
        tex = (self.h / "paper/cards.tex").read_text()
        self.assertLess(tex.index(r"\begin{theorem}"), tex.index(r"\begin{lemma}"))
        self.assertLess(tex.index(r"\begin{lemma}"), tex.index("% proof of thm-sum-settled"))
        self.assertIn(r"\begin{proof}[{Proof of Theorem~\ref{", tex)
        self.assertEqual(self.run_cards("read").returncode, 0)
        self.edit("structure.yaml", "      - {proof_of: thm-sum-settled}\n", "")
        self.assertNotEqual(self.check_json()[0], 0)

    def test_subsection_items(self):
        self.edit("structure.yaml", "      - lem-tail\n", "      - {subsection: Proofs}\n      - lem-tail\n")
        code, data = self.check_json()
        self.assertEqual(code, 0, data)
        self.assertEqual(self.run_cards("render").returncode, 0)
        tex = (self.h / "paper/cards.tex").read_text()
        self.assertLess(tex.index(r"\section{Results}"), tex.index(r"\subsection{Proofs}"))
        self.assertLess(tex.index(r"\subsection{Proofs}"), tex.index(r"\begin{lemma}"))
        self.assertEqual(self.run_cards("read").returncode, 0)

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

    # ------------------------------------------------------------ outputs, templates, hook, editor

    def test_build_records_outputs_and_check_reports_outdated(self):
        r = self.run_cards("build", "--no-pdf")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        for out in ("paper/cards.tex", "html/index.html", "html/read.html"):
            self.assertTrue((self.h / out).is_file(), out)
        self.assertNotIn("{proof}", (self.h / "html/read.html").read_text())
        stamps = json.loads((self.h / "paper/.build.json").read_text())["outputs"]
        self.assertEqual(set(stamps), {"tex:cards.tex", "html", "read"})
        self.assertEqual(self.check_json()[1]["warnings"], [])
        self.edit("cards/def/def-settled.md", "A real sequence", "A sequence of reals")
        outdated = [w for w in self.check_json()[1]["warnings"] if w.startswith("OUTDATED")]
        self.assertEqual(len(outdated), 3)
        self.assertIn("outdated", self.run_cards("status").stdout)
        self.assertEqual(self.run_cards("build", "--no-pdf").returncode, 0)
        self.assertEqual(self.check_json()[1]["warnings"], [])

    def test_build_stops_on_errors_and_keeps_outputs(self):
        self.assertEqual(self.run_cards("build", "--no-pdf").returncode, 0)
        before = (self.h / "paper/cards.tex").read_text()
        self.edit("cards/prop/lem-tail.md", "requires: [def-settled]", "requires: [def-missing]")
        r = self.run_cards("build", "--no-pdf")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("build stopped", r.stdout)
        self.assertEqual((self.h / "paper/cards.tex").read_text(), before)

    def test_pdf_command_from_settings(self):
        with open(self.h / "harness.toml", "a") as f:
            f.write('\n[build]\ntex = ["full.tex"]\n'
                    'pdf_command = ["{python}", "-c", "import sys; open(sys.argv[1] + \'.pdf\', \'w\').write(\'x\')", "{tex}"]\n')
        r = self.run_cards("build")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertTrue((self.h / "paper/full.tex.pdf").is_file())
        stamps = json.loads((self.h / "paper/.build.json").read_text())["outputs"]
        self.assertTrue(stamps["pdf:full.tex"]["ok"])

    def test_new_card_from_template(self):
        r = self.run_cards("new", "lemma", "lem-extra", "--title", "Extra", "--requires", "lem-tail")
        self.assertEqual(r.returncode, 0, r.stderr)
        text = (self.h / "cards/prop/lem-extra.md").read_text()
        self.assertIn("kind: lemma", text)
        self.assertIn("requires: [lem-tail]", text)
        r = self.run_cards("new", "explanation", "x-extra", "--explains", "lem-extra")
        self.assertEqual(r.returncode, 0, r.stderr)
        code, out = self.check_json()
        self.assertEqual(out["errors"], [])
        self.assertFalse([w for w in out["warnings"] if "x-extra" in w and "STALE" in w])
        self.assertNotEqual(self.run_cards("new", "lemma", "lem-extra").returncode, 0)
        self.assertNotEqual(self.run_cards("new", "lemma", "Bad_Id").returncode, 0)
        (self.h / "templates").mkdir()
        (self.h / "templates/definition.md").write_text("---\nid: {id}\nkind: definition\nstatus: stated\n---\n## Statement\nOWN\n")
        self.assertEqual(self.run_cards("new", "definition", "def-own").returncode, 0)
        self.assertIn("OWN", (self.h / "cards/def/def-own.md").read_text())

    def test_hook_builds_in_background_only_for_sources(self):
        with open(self.h / "harness.toml", "a") as f:
            f.write("\n[build]\npdf = false\nquiet = 0.2\n")
        def hook(path):
            return subprocess.run([sys.executable, str(CARDS), "hook"], input=json.dumps(
                {"tool_name": "Edit", "tool_input": {"file_path": str(path)}}), capture_output=True, text=True)
        self.assertEqual(hook(self.ws / "elsewhere.md").returncode, 0)
        self.assertEqual(hook(self.h / "story.md").returncode, 0)
        self.assertFalse((self.h / "paper/.dirty").exists())
        self.edit("cards/def/def-settled.md", "A real sequence", "A sequence of reals")
        self.assertEqual(hook(self.h / "cards/def/def-settled.md").returncode, 0)
        import time
        for _ in range(100):
            if (self.h / "html/read.html").exists() and not (self.h / "paper/.dirty").exists():
                break
            time.sleep(0.1)
        self.assertTrue((self.h / "html/read.html").exists())
        self.assertEqual(self.check_json()[1]["warnings"], [])

    def test_editor_saves_with_conflict_check(self):
        sys.path.insert(0, str(CARDS.parent))
        import cards as C
        import editor
        app = editor.App(C.Harness(self.h), build=False)
        p = self.h / "cards/prop/lem-tail.md"
        text = p.read_text()
        base = editor.sha(text)
        self.assertIn("Lemma", app.preview("lem-tail", text)["html"])
        self.assertIn("error", app.preview("lem-tail", "no front matter"))
        self.assertTrue(app.save("lem-tail", text, "0" * 16).get("conflict"))
        self.assertFalse(app.save("lem-tail", "broken", base)["ok"])
        self.assertFalse(app.save("lem-tail", text.replace("id: lem-tail", "id: lem-other"), base)["ok"])
        changed = text.replace(r"N(a)", r"N(a)\,", 1)
        res = app.save("lem-tail", changed, base)
        self.assertTrue(res["ok"], res)
        self.assertEqual(p.read_text(), changed)
        self.assertIn("thm-sum-settled", res["impact"]["facts"])
        self.assertTrue(app.new("lemma", "lem-web", "")["ok"])
        self.assertTrue((self.h / "cards/prop/lem-web.md").exists())
        res = app.comments("Lemma 2.1\n「quote」\n→ fix this")
        self.assertTrue((self.h / res["path"].split("settled/harness/")[-1]).read_text().strip().endswith("fix this"))
        for page in (app.page_read(), app.page_cards(), app.page_edit("lem-tail")):
            self.assertIn("</html>", page)
        self.assertIn("saveUrl", app.page_read())


if __name__ == "__main__":
    unittest.main()
