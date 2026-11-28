# -*- coding: utf-8 -*-
"""Regression tests for the method-harness scripts on fictional data."""
import contextlib
import io
import json
import os
import sys
import tempfile
import unittest
from base64 import b64decode
from pathlib import Path

sys.dont_write_bytecode = True
SCRIPTS = Path(__file__).resolve().parents[1] / "skills/method-harness/scripts"
sys.path.insert(0, str(SCRIPTS))
import method as M  # noqa: E402
from passages import check_code_reason, check_reader_fact, reading_blocks


def w(p, text):
    p.parent.mkdir(parents=True, exist_ok=True); p.write_text(text, encoding="utf-8")


def fixture(tmp):
    r = Path(os.path.realpath(tmp)) / "root"
    code = Path(os.path.realpath(tmp)) / "codes"
    w(code / "toy.py", "a = 1\nb = a + 1\nprint(a, b)\n")
    w(r / "harness.toml", 'language = "ja"\n')
    w(r / "src/s1.md", "---\nid: s1\nkind: source\ntitle: Toy paper\nsha256: abc\ncode_root: ../codes\nstatus: stated\n---\n\n## 書誌\n架空の論文\n")
    w(r / "pool/x/c-one.md", "---\nid: c-one\nkind: claim\ntitle: One\nstatus: stated\nrequires: []\n---\n\n## 内容\nOne is one.\n")
    w(r / "pool/x/c-two.md", "---\nid: c-two\nkind: claim\ntitle: Two\nstatus: stated\nrequires: [c-one]\n---\n\n## 内容\nTwo is after one.\n")
    w(r / "pool/x/st-toy.md", "---\nid: st-toy\nkind: step\ntitle: Toy step\nlang: python\nstatus: stated\norigin: original\n"
      "code: {src: s1, file: toy.py, lines: [1, 2]}\nrealizes: [c-one]\nrequires: [c-two]\nevidence: [run-toy]\n---\n\n## 説明\nSets a and b.\n\n## 行説明\n1: a is one\n2: b is a plus one\n")
    w(r / "pool/x/run-toy.md", "---\nid: run-toy\nkind: run\ntitle: Toy run\nstatus: stated\nsrc: s1\ncommand: '{python} toy.py'\ncwd: .\nfiles: [toy.py]\n---\n\n## 内容\nRuns toy.py.\n")
    w(r / "pool/x/fig-toy.md", "---\nid: fig-toy\nkind: figure\ntitle: Toy figure\nstatus: stated\npage: 4\nshows: [c-one]\nproduced_by: [run-toy]\n---\n\n## 何を示すか\nA line.\n")
    w(r / "route/strict/route.yaml", "title: Strict\norder: strict\nsections:\n- title: S\n  items: [st-toy, c-one, c-two, fig-toy, run-toy]\n")
    w(r / "route/free/route.yaml", "title: Free\norder: free\nsections:\n- title: S\n  items: [st-toy, c-one, c-two, fig-toy, run-toy]\n")
    w(r / "route/ok/route.yaml", "title: Ok\norder: strict\nsections:\n- title: S\n  items: [c-one, c-two, st-toy, fig-toy, run-toy]\n")
    return r, code


def run(*args):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        try:
            M.main(list(args))
            code = 0
        except SystemExit as e:
            code = e.code if isinstance(e.code, int) else 1
    return code, buf.getvalue()


class T(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.r, self.code = fixture(self.tmp.name)
        self.a = ["--root", str(self.r)]

    def codes(self, route=None):
        root = M.Root(self.r)
        return [(s, c, i) for s, c, i, _ in M.check(root, route)]

    def test_claim_reading_covers_passages_and_checks_dependencies(self):
        from claim_readings import ClaimReadings

        w(self.r / "harness.toml", '[reader]\nclaim_readings = "claims.yaml"\n')
        w(self.r / "claims.yaml", r"""toy-passage:
  - id: first
    kind: definition
    title: An assumption
    statement: 'Let $x\in\mathbb R$. If $x\ne0$, then $|x|>0$.'
    reason: It is nonzero
    formula: 'x:\mathbb{R} :: @x\ne0\implies |@x|>0'
  - id: second
    kind: code
    title: Normalize
    statement: 'For $x\in\mathbb R\setminus\{0\}$, the normalization returns $x/|x|$, whose absolute value is $1$.'
    reason: Divide by its norm
    formula: 'x:\mathbb{R} :: @x\ne0\implies |@x/|@x||=1'
    requires: [first]
    basis: [normalize]
""")
        readings = ClaimReadings(self.r)
        passage = {"id": "toy-passage", "reading": [{"ref": "normalize"}],
                   "links": [{"key": "normalize", "role": "code"}]}
        self.assertEqual(readings.check([passage]), [])
        first = readings.entries["toy-passage"][0]
        formula = first.pop("formula")
        self.assertIn(("toy-passage", "first: 閉論理式が必要"), readings.check([passage]))
        first["formula"] = formula
        statement = first["statement"]
        first["statement"] = r"\all{x}{\mathbb{R}}{@x=0}"
        self.assertIn(("toy-passage", "first: 言明本文には通常の数学の記法を使う"),
                      readings.check([passage]))
        first["statement"] = statement
        self.assertIn(("uncovered", "詳読の言明が未登録"),
                      readings.check([passage, {**passage, "id": "uncovered"}]))
        self.assertTrue(readings.check([{**passage, "links": [{"key": "normalize", "role": "figure"}]}]))
        readings.entries["toy-passage"].reverse()
        self.assertTrue(readings.check([passage]))
        path = self.r / "claims.yaml"
        path.write_text(path.read_text().replace("    formula:", "    formula: '0=0'\n    formula:", 1))
        with self.assertRaisesRegex(M.yaml.YAMLError, "重複したキー"):
            ClaimReadings(self.r)

    def test_closed_formula_checks_scope_and_bound_domains(self):
        from closed_formula import closed_tex

        result = closed_tex(r"n:\mathbb{N}; A:\mathbb{R}^{@n} :: \some{k}{\mathbb{N}}{@k\ge @n}")
        self.assertIn(r"\forall A\in \mathbb{R}^{{n}}", result)
        self.assertIn(r"\exists k\in \mathbb{N}", result)
        self.assertIn(r"\forall X", closed_tex(r"X:* :: \all{x}{@X}{@x\in @X}"))
        for formula in (
            r"@y=1",
            r"n:\mathbb{R}^{@n} :: @n=0",
            r"\all{x}{\mathbb{R}}{@x=0}\wedge @x=1",
            r"\all{x}{\mathbb{R}}{@x+1}",
            r"\setof{x}{\mathbb{R}}{@x>0}",
            r"x=0",
            r"0=",
            r"\pred{Placeholder}",
            r"n:\mathbb{N} :: \some{n}{\mathbb{N}}{@n=0}",
        ):
            with self.subTest(formula=formula), self.assertRaises(ValueError):
                closed_tex(formula)

    def test_ordered_reading_preserves_mixed_order_and_checks_references(self):
        math = {"role": "math", "key": "fact"}
        figure = {"role": "figure", "key": "figure"}
        reading = [{"ref": "figure"}, {"text": "Connection."}, {"ref": "fact"},
                   {"ref": "fact", "part": "code"}]
        passage = {"links": [math, figure], "reading": reading}
        self.assertEqual(reading_blocks(passage), [
            ("link", figure), ("text", "Connection."), ("link", math), ("fact-code", math),
        ])
        for sections, reason in (
            ([reading[0], reading[2], {"ref": "missing"}], "見つからない"),
            ([reading[0], reading[3], reading[2]], "数学の参照が出た後"),
            ([reading[0]], "現れない参照"),
            ([reading[0], reading[0], reading[2]], "重複"),
        ):
            with self.subTest(reason=reason):
                with self.assertRaisesRegex(ValueError, reason):
                    reading_blocks({**passage, "reading": sections})

    def test_code_design_requires_derivation(self):
        step = M.Root(self.r).cards["st-toy"]
        with self.assertRaisesRegex(ValueError, "導出"):
            check_code_reason(step)
        step.secs.update({"設計の主張": "b=a+1", "導出": "代入する。", "コードへの移し方": "二行目で実装する。"})
        check_code_reason(step)
        with self.assertRaisesRegex(ValueError, "導出/local-fit"):
            check_code_reason(step, "local-fit")

    def test_clean_pool_warns_only_about_code_fp(self):
        got = self.codes()
        self.assertEqual([x for x in got if x[0] == "ERR"], [])
        self.assertEqual({x[1] for x in got if x[0] == "WARN"}, {"NO-CODE-FP"})

    def test_forward_strict_error_free_info_ok_route_clean(self):
        self.assertIn(("ERR", "FORWARD", "st-toy"), self.codes("strict"))
        self.assertIn(("INFO", "FORWARD-OK", "st-toy"), self.codes("free"))
        self.assertNotIn("FORWARD", [c for _, c, _ in self.codes("ok")])

    def test_unlisted_borrow(self):
        w(self.r / "route/ok/route.yaml", "title: Ok\norder: strict\nsections:\n- title: S\n  items: [c-two]\n")
        self.assertIn(("ERR", "UNLISTED-BORROW", "c-two"), self.codes("ok"))

    def test_unknown_ref_cycle_bad_id(self):
        w(self.r / "pool/x/c-one.md", "---\nid: c-one\nkind: claim\ntitle: One\nstatus: stated\nrequires: [c-two, nope]\n---\n\n## 内容\nx\n")
        w(self.r / "pool/x/Bad.md", "---\nid: Bad\nkind: claim\ntitle: B\n---\n\n## 内容\nx\n")
        got = self.codes()
        self.assertIn(("ERR", "UNKNOWN-REF", "c-one"), got)
        self.assertTrue(any(c == "CYCLE" for _, c, _ in got))
        self.assertTrue(any(c == "BAD-ID" for _, c, _ in got))

    def test_line_note_out_of_range(self):
        p = self.r / "pool/x/st-toy.md"
        p.write_text(p.read_text(encoding="utf-8").replace("2: b is", "3: b is"), encoding="utf-8")
        self.assertIn(("ERR", "BAD-LINE-NOTE", "st-toy"), self.codes())

    def test_ladder_needs_a_valid_run_record(self):
        code, out = run(*self.a, "set-status", "st-toy", "reproduced")
        self.assertNotEqual(code, 0)                        # 記録なし
        c, o = run(*self.a, "run", "run-toy")
        self.assertEqual(c, 0, o)
        c, o = run(*self.a, "set-status", "st-toy", "reproduced")
        self.assertEqual(c, 0, o)
        self.assertEqual(M.Root(self.r).cards["st-toy"].get("status"), "reproduced")
        self.assertFalse([x for x in self.codes() if x[0] == "ERR"])

    def test_reproduced_without_record_is_an_error(self):
        p = self.r / "pool/x/st-toy.md"
        p.write_text(p.read_text(encoding="utf-8").replace("status: stated", "status: reproduced", 1), encoding="utf-8")
        self.assertIn(("ERR", "NO-RUN-RECORD", "st-toy"), self.codes())

    def test_code_change_makes_things_stale(self):
        run(*self.a, "run", "run-toy")
        run(*self.a, "anchor", "st-toy")
        run(*self.a, "set-status", "st-toy", "reproduced")
        w(self.r / "route/ok/card/br.md", "---\nid: br\nkind: bridge\ntitle: B\nbetween: [c-two, st-toy]\nanchors: {}\n---\n\n## 済んだこと\na\n\n## 足りないこと\nb\n\n## 次にすること\nc\n")
        run(*self.a, "anchor", "br", "--to", "c-two", "st-toy")
        self.assertFalse([x for x in self.codes() if x[1] in ("STALE", "CODE-CHANGED", "STALE-RUN")])
        w(self.code / "toy.py", "a = 1\nb = a + 2\nprint(a, b)\n")          # コードを変える
        got = self.codes()
        self.assertIn(("WARN", "CODE-CHANGED", "st-toy"), got)
        self.assertIn(("WARN", "STALE-RUN", "st-toy"), got)
        self.assertIn(("WARN", "STALE", "br"), got)                          # step に anchor した つなぎ
        run(*self.a, "run", "run-toy"); run(*self.a, "anchor", "st-toy"); run(*self.a, "anchor", "br")
        self.assertFalse([x for x in self.codes() if x[1] in ("STALE", "CODE-CHANGED", "STALE-RUN")])

    def test_fingerprints_follow_code_and_run_results(self):
        def fps():
            code, out = run(*self.a, "fingerprints")
            self.assertEqual(code, 0, out)
            return json.loads(out)
        before = fps()
        self.assertTrue({"st-toy", "run-toy", "fig-toy"} <= set(before))
        run(*self.a, "run", "run-toy")
        after_run = fps()
        self.assertNotEqual(before["run-toy"], after_run["run-toy"])    # 実行結果が指紋に入る
        self.assertEqual(before["st-toy"], after_run["st-toy"])
        w(self.code / "toy.py", "a = 1\nb = a + 2\nprint(a, b)\n")
        changed = fps()
        self.assertNotEqual(after_run["st-toy"], changed["st-toy"])     # コードが変わる
        self.assertNotEqual(after_run["run-toy"], changed["run-toy"])   # 記録が古くなる

    def test_lineage_of_code_cards(self):
        card = self.r / "pool/x/st-toy.md"
        text = card.read_text(encoding="utf-8")
        lineage = ('lineage: {"proposal": {"src": "s1", "loc": "§2"}, "intent": "Add one.", "code": "ai", '
                   '"differences": "None.", "status": "checked"}\n')
        card.write_text(text.replace("---\n\n", lineage + "---\n\n", 1), encoding="utf-8")
        self.assertFalse([x for x in self.codes() if x[1] == "LINEAGE"])
        for old, new in (('"code": "ai"', '"code": "mine"'), ('"src": "s1"', '"src": "c-one"'),
                         ('"intent": "Add one.", ', '')):
            with self.subTest(old=old):
                card.write_text(text.replace("---\n\n", lineage.replace(old, new) + "---\n\n", 1), encoding="utf-8")
                self.assertIn(("ERR", "LINEAGE", "st-toy"), self.codes())

    def test_changed_run_command_invalidates_record(self):
        code, out = run(*self.a, "run", "run-toy")
        self.assertEqual(code, 0, out)
        self.assertEqual(M.Root(self.r).record_state("run-toy"), "ok")
        card = self.r / "pool/x/run-toy.md"
        card.write_text(card.read_text().replace("toy.py'", "toy.py --changed'"), encoding="utf-8")
        self.assertEqual(M.Root(self.r).record_state("run-toy"), "stale")

    def test_anchor_rewrite_keeps_front_matter_closed(self):
        run(*self.a, "anchor", "st-toy")
        raw = (self.r / "pool/x/st-toy.md").read_text(encoding="utf-8")
        self.assertIn("\n---\n\n## 説明", raw)
        M.parse(self.r / "pool/x/st-toy.md")
        with self.assertRaises(ValueError):
            M.set_block("no front matter", "k", 1)

    def test_passage_detects_math_and_code_changes(self):
        w(self.r / "harness.toml", 'language = "ja"\n[writing_harnesses]\nnotes = "writer"\n')
        fact = self.r / "writer/cards/prop/prop-source.md"
        w(fact, "---\nid: prop-source\nkind: proposition\n---\n\n## Statement\nOne.\n\n## Proof\nBy definition.\n")
        from passages import load_writing_fact
        fingerprint = load_writing_fact(self.r, M.WRITING_CARDS, "notes:prop-source", {"notes": "writer"}).fingerprint()
        root = M.Root(self.r)
        code_anchor = root.fingerprint(root.cards["st-toy"])
        passage = self.r / "route/ok/map/map-toy.md"
        w(passage, f"""---
id: map-toy
kind: map
title: A source passage
anchors: {{st-toy: "{code_anchor}"}}
passages:
- id: toy-step
  at: {{section: "1.2", algorithm: 1, step: 1}}
  summary: Context
  links:
  - {{role: math, card: "notes:prop-source", fingerprint: "{fingerprint}", text: Proof}}
  - {{role: code, card: st-toy, line: 2, text: Reason}}
---

## 対応
Example.
""")
        self.assertFalse([code for code in self.codes() if code[2] == "map-toy"])
        fact.write_text(fact.read_text().replace("One.", "Two."), encoding="utf-8")
        self.assertIn(("WARN", "STALE-PASSAGE", "map-toy"), self.codes())
        w(self.code / "toy.py", "a = 3\nb = a + 1\nprint(a, b)\n")
        self.assertIn(("WARN", "STALE", "map-toy"), self.codes())
        code, _ = run(*self.a, "anchor", "map-toy")
        self.assertEqual(code, 0)
        self.assertFalse([code for code in self.codes() if code[2] == "map-toy"])
        passage.write_text(passage.read_text().replace("line: 2", "line: 3"), encoding="utf-8")
        self.assertIn(("ERR", "PASSAGE-REF", "map-toy"), self.codes())

    def test_code_walkthrough_checks_the_bridge_and_tracks_changes_to_the_proof(self):
        w(self.r / "harness.toml", '[reader]\nclaim_readings = "claims.yaml"\n')
        claims = self.r / "claims.yaml"
        w(claims, r"""toy-step:
- id: code-update
  kind: code
  title: Update
  statement: The second line assigns the value of a plus one to b.
  reason: It reads a and adds one.
  formula: 'x:\mathbb{R} :: \op{ReturnedValue}(@x)=@x+1'
  basis: [update]
- id: math-increase
  kind: math
  title: Increase
  statement: Adding one strictly increases a real number.
  reason: One is positive.
  formula: 'x:\mathbb{R} :: @x<@x+1'
""")
        root = M.Root(self.r)
        anchor = root.fingerprint(root.cards["st-toy"])
        mapping = self.r / "route/ok/map/map-toy.md"
        w(mapping, f"""---
id: map-toy
kind: map
title: A source passage
anchors: {{st-toy: "{anchor}"}}
passages:
- id: toy-step
  at: {{section: "1", paragraph: 1}}
  summary: Context
  links:
  - role: code
    card: st-toy
    key: update
    line: 2
    text: Update.
    walkthrough:
      claim: code-update
      bridge: |-
        Let the program variable a represent a real number.
        Then the code returns the sum of that number and one in b.
      math: [math-increase]
  reading:
  - ref: update
---

## 対応
Example.
""")
        valid = mapping.read_text()
        warning = ("WARN", "STALE-PASSAGE", "map-toy")
        self.assertIn(warning, self.codes())
        code, _ = run(*self.a, "anchor", "map-toy")
        self.assertEqual(code, 0)
        self.assertNotIn(warning, self.codes())
        w(claims, claims.read_text().replace("One is positive.", "One belongs to the positive reals."))
        self.assertIn(warning, self.codes())
        code, _ = run(*self.a, "anchor", "map-toy")
        self.assertEqual(code, 0)
        self.assertNotIn(warning, self.codes())
        for old, new in (
            ("claim: code-update", "claim: math-increase"),
            ("math: [math-increase]", "math: [code-update]"),
            ("math: [math-increase]", "math: [math-increase, math-increase]"),
            ("bridge: |-\n        Let the program variable a represent a real number.\n"
             "        Then the code returns the sum of that number and one in b.", "bridge: ''"),
        ):
            with self.subTest(old=old, new=new):
                w(mapping, valid.replace(old, new))
                self.assertIn(("ERR", "CLAIM-READING", "toy-step"), self.codes())
        w(self.r / "harness.toml", '[reader]\nclaim_readings = "claims.yaml"\nrequire_code_walkthroughs = true\n')
        w(mapping, valid.split("    walkthrough:\n")[0] + "  reading:\n" + valid.split("  reading:\n")[1])
        self.assertIn(("ERR", "CLAIM-READING", "toy-step"), self.codes())

    def test_points_realizations_and_appendices(self):
        w(self.r / "harness.toml", '[reader]\nclaim_readings = "claims.yaml"\nappendices = true\n'
          'require_points = true\nrequire_realizations = true\n')
        claims = self.r / "claims.yaml"
        w(claims, r"""toy-step:
- id: code-update
  kind: code
  title: Update
  statement: The second line assigns the value of a plus one to b.
  reason: It reads a and adds one.
  formula: 'x:\mathbb{R} :: \op{ReturnedValue}(@x)=@x+1'
  basis: [update]
- id: math-increase
  kind: math
  title: Increase
  point: Positivity of one is the only fact used.
  statement: Adding one strictly increases a real number.
  reason: One is positive.
  formula: 'x:\mathbb{R} :: @x<@x+1'
""")
        root = M.Root(self.r)
        anchor = root.fingerprint(root.cards["st-toy"])
        mapping = self.r / "route/ok/map/map-toy.md"
        w(mapping, f"""---
id: map-toy
kind: map
title: A source passage
anchors: {{st-toy: "{anchor}"}}
passages:
- id: toy-step
  at: {{section: "1", paragraph: 1}}
  summary: Context
  links:
  - role: code
    card: st-toy
    key: update
    line: 2
    text: Update the value.
    walkthrough:
      claim: code-update
      bridge: The variable a represents a real number, and b holds that number plus one.
      math: [math-increase]
      realization:
      - math: the sum x plus one
        code: line 2
        kind: equality
        holds: a holds a real number.
  reading:
  - ref: update
---

## 対応
Example.
""")
        code, out = run(*self.a, "anchor", "map-toy")
        self.assertEqual(code, 0, out)
        self.assertEqual([c for c in self.codes() if c[0] == "ERR" or c[1] == "STALE-PASSAGE"], [])
        valid_claims, valid_map = claims.read_text(), mapping.read_text()
        for target, old, new in (
            (claims, "  point: Positivity of one is the only fact used.\n", ""),
            (mapping, "kind: equality", "kind: guess"),
            (mapping, "kind: equality", "kind: approximation"),
            (mapping, "        holds: a holds a real number.\n", ""),
        ):
            with self.subTest(old=old, new=new):
                target.write_text((valid_claims if target == claims else valid_map).replace(old, new))
                self.assertIn(("ERR", "CLAIM-READING", "toy-step"), self.codes())
                claims.write_text(valid_claims); mapping.write_text(valid_map)
        mapping.write_text(valid_map.replace("code: line 2", "code: line two"))
        self.assertIn(("WARN", "STALE-PASSAGE", "map-toy"), self.codes())
        mapping.write_text(valid_map)

        from importlib.util import module_from_spec, spec_from_file_location
        spec = spec_from_file_location("method_reader", SCRIPTS / "reader.py")
        reader = module_from_spec(spec)
        spec.loader.exec_module(reader)
        claims.write_text(valid_claims.replace("  kind: math\n", "  kind: math\n  main: true\n"))
        self.assertEqual([c for c in self.codes() if c[0] == "ERR"], [])
        claims.write_text(valid_claims.replace("  kind: code\n", "  kind: code\n  main: true\n"))
        self.assertIn(("ERR", "CLAIM-READING", "toy-step"), self.codes())
        claims.write_text(valid_claims.replace("  kind: math\n", "  kind: math\n  main: true\n"))
        views = reader.PassageViews(self.r, Path(self.tmp.name) / "web", code_route="ok")
        latex = lambda text: f"<p>{text}</p>"
        main = views.insert("1", "<p>Source paragraph.</p>\n", latex, {})
        self.assertNotIn("<details", main)
        self.assertIn('data-main-claim="toy-step--claim--math-increase"', main)
        self.assertIn("<strong>命題 1.1</strong>", main)
        self.assertIn("Positivity of one is the only fact used.", main)
        self.assertNotIn("One is positive.", main)
        self.assertIn('href="proofs.html#toy-step--claim--math-increase"', main)
        self.assertIn('data-sketch="toy-step--claim--math-increase"', main)
        self.assertIn('data-code-flow="toy-step"', main)
        self.assertIn('href="methods.html#toy-step--update--walkthrough">Toy step（B.1.1）', main)
        [(number, _, proofs)] = views.proofs_sections([("1", "1 S")], latex)
        self.assertEqual(number, "1")
        self.assertNotIn("<details", proofs)
        self.assertIn('data-appendix-claim="toy-step--claim--math-increase"', proofs)
        self.assertIn("One is positive.", proofs)
        self.assertIn('href="index.html#toy-step--claim--math-increase"', proofs)
        self.assertIn('data-code-flow="toy-step"', proofs)
        self.assertNotIn("Positivity of one is the only fact used.", proofs)
        self.assertIn('href="methods.html#toy-step--update--walkthrough"', proofs)
        [(number, _, methods)] = views.methods_sections([("1", "1 S")], latex)
        self.assertEqual(number, "1")
        self.assertIn('id="B-st-toy"', methods)
        self.assertIn("Positivity of one is the only fact used.", methods)
        self.assertNotIn("<details", methods)
        self.assertEqual(methods.count('data-realization="toy-step--update"'), 1)
        for stage in ("toy-step--claim--code-update", "toy-step--update--walkthrough", "toy-step--update--realization",
                      "toy-step--update--math", "toy-step--update--bridge", "toy-step--update--code"):
            self.assertIn(f'id="{stage}"', methods)
        self.assertIn('href="proofs.html#toy-step--claim--math-increase"', methods)
        self.assertEqual(views.outside_theory(latex), "")
        self.assertIn('href="proofs.html#A-toy-step"', views.relink('<a href="#toy-step">x</a>', "methods.html"))

    def test_cost_and_cited_statements_and_paragraph_ledger(self):
        w(self.r / "harness.toml", '[reader]\nclaim_readings = "claims.yaml"\nappendices = true\n'
          'paragraph_ledger = "ledger.yaml"\n')
        claims = self.r / "claims.yaml"
        valid = r"""toy-step:
- id: cost-floyd
  kind: cost
  title: Floyd
  model: Count additions and comparisons on a graph with n vertices.
  point: Each of n relays updates all n squared pairs once.
  statement: The algorithm uses n cubed updates.
  reason: Three nested loops of length n.
  origin: {src: s1, loc: "p.2", relation: agrees}
- id: cited-claim
  kind: cited
  title: Cited
  statement: The cited paper states a bound.
  reason: Read on page 3.
  origin: {cite: "Someone (2000)", relation: stronger, note: The survey drops a hypothesis.}
"""
        w(claims, valid)
        mapping = self.r / "route/ok/map/map-toy.md"
        anchor = M.Root(self.r).fingerprint(M.Root(self.r).cards["c-one"])
        w(mapping, f"""---
id: map-toy
kind: map
title: A source passage
anchors: {{c-one: "{anchor}"}}
passages:
- id: toy-step
  at: {{section: "1", paragraph: 2}}
  summary: Cost
  links:
  - role: claim
    card: c-one
    key: one
    text: The section claim.
  reading:
  - text: The cost of the step.
  - ref: one
---

## 対応
Example.
""")
        self.assertEqual([c for c in self.codes() if c[0] == "ERR"], [])
        for old, new in (("  model: Count additions and comparisons on a graph with n vertices.\n", ""),
                         ("  origin: {cite: \"Someone (2000)\", relation: stronger, note: The survey drops a hypothesis.}\n", ""),
                         ("relation: agrees", "relation: maybe"),
                         (", note: The survey drops a hypothesis.", ""),
                         ("src: s1", "src: c-one"),
                         ('cite: "Someone (2000)"', 'cite: "Someone (2000)", substitute: Paywalled original')):
            with self.subTest(old=old):
                claims.write_text(valid.replace(old, new))
                self.assertIn("toy-step", [c[2] for c in self.codes() if c[0] == "ERR"])
        claims.write_text(valid)
        from importlib.util import module_from_spec, spec_from_file_location
        spec = spec_from_file_location("method_reader2", SCRIPTS / "reader.py")
        reader = module_from_spec(spec); spec.loader.exec_module(reader)
        rendered = "<p>Intro.</p>\n<p>Cost text.</p>\n<p>Outlook.</p>\n"
        w(self.r / "ledger.yaml", "")
        views = reader.PassageViews(self.r, Path(self.tmp.name) / "web", code_route="ok")
        errors = views.check_paragraphs([("1", rendered)])
        self.assertEqual(len([e for e in errors if "詳読も記録もない" in e]), 2)
        texts, _ = views.paragraph_texts(rendered)
        fp1, fp3 = views.paragraph_fp(texts[0]), views.paragraph_fp(texts[2])
        w(self.r / "ledger.yaml", f'"1":\n  1: {{none: Introduction, fp: {fp1}}}\n  3: {{none: Outlook, fp: {fp3}}}\n')
        views = reader.PassageViews(self.r, Path(self.tmp.name) / "web", code_route="ok")
        self.assertEqual(views.check_paragraphs([("1", rendered)]), [])
        changed = rendered.replace("Outlook.", "Outlook changed.")
        self.assertTrue(any("指紋" in e for e in views.check_paragraphs([("1", changed)])))
        w(self.r / "ledger.yaml", f'"1":\n  1: {{none: Introduction, fp: {fp1}}}\n  2: {{none: Twice}}\n  3: {{none: Outlook, fp: {fp3}}}\n')
        views = reader.PassageViews(self.r, Path(self.tmp.name) / "web", code_route="ok")
        self.assertTrue(any("記録は不要" in e for e in views.check_paragraphs([("1", rendered)])))
        latex = lambda text: f"<p>{text}</p>"
        views = reader.PassageViews(self.r, Path(self.tmp.name) / "web", code_route="ok")
        [(_, _, proofs)] = views.proofs_sections([("1", "1 S")], latex)
        self.assertIn('data-claim-model="1"', proofs)
        self.assertIn('data-origin-relation="agrees"', proofs)
        self.assertIn('data-origin-relation="stronger"', proofs)
        claims.write_text(valid.replace("relation: agrees}", "relation: agrees, substitute: The original is paywalled.}"))
        self.assertEqual([c for c in self.codes() if c[0] == "ERR"], [])
        views = reader.PassageViews(self.r, Path(self.tmp.name) / "web", code_route="ok")
        [(_, _, proofs)] = views.proofs_sections([("1", "1 S")], latex)
        self.assertIn('data-origin-substitute="1"', proofs)
        self.assertIn("計算量 A.1", proofs)

    def test_book_passage_rechecks_a_changed_proof(self):
        from unittest.mock import patch

        from book_links import BookReferences, book_card_html

        workspace = self.r.parent
        book = workspace / "local/book"
        (self.r / "harness.toml").write_text(
            '[book_harnesses.notes]\nroot = "local/book"\nroute = "notes"\n',
            encoding="utf-8",
        )
        w(book / "pool/basic/prop-toy.md", """---
id: prop-toy
kind: A2
title: A toy result
---
## Hypotheses
Let x be real. 日本語の仮定。
## Conclusion
x = x.
## Quantifiers
For every x.
""")
        proof = book / "pool/basic/proof-toy.md"
        proof_text = """---
id: proof-toy
kind: A3
proves: prop-toy
title: A toy proof
---
## Plan
Use equality.
## Steps
By reflexivity. $x=x$.
"""
        w(proof, proof_text)
        w(book / "route/notes/route.yaml", "title: Notes\nsections:\n- title: Basics\n  items: [prop-toy, proof-toy]\n")
        with patch("book_links.WORKSPACE", workspace):
            selection = BookReferences(self.r).resolve("notes:prop-toy")
            self.assertEqual(selection.proof.id, "proof-toy")
            self.assertIn("Let x be real.", book_card_html(selection, selection.card))
            self.assertIn("日本語の仮定。", book_card_html(selection, selection.card))
            proof_html = book_card_html(selection, selection.proof)
            self.assertIn("By reflexivity.", proof_html)
            self.assertIn("<math", proof_html)
            self.assertNotIn("href=", proof_html)
            w(self.r / "route/ok/map/map-toy.md", f"""---
id: map-toy
kind: map
title: An application
passages:
- id: toy-section
  at: {{section: "1", heading: true}}
  summary: Context
  links:
  - {{role: book, card: "notes:prop-toy", version: "{selection.version}", text: Apply reflexivity}}
---
## 対応
Example.
""")
            self.assertFalse([code for code in self.codes() if code[2] == "map-toy"])
            w(proof, proof_text.replace("By reflexivity.", "Use the reflexive law for equality."))
            self.assertIn(("WARN", "STALE-PASSAGE", "map-toy"), self.codes())
            code, _ = run(*self.a, "anchor", "map-toy")
            self.assertEqual(code, 0)
            self.assertFalse([code for code in self.codes() if code[2] == "map-toy"])

    def test_source_passage_requires_open_access_and_terms(self):
        from passages import check_link

        root = M.Root(self.r)
        source = root.cards["s1"]
        source.fm.update(access="open", edition="2026", license="CC BY 4.0",
                         checked="2026-11-25", url="https://example.org/chapter",
                         license_url="https://example.org/terms")
        link = {"role": "source", "card": "s1", "text": "Projection", "loc": "§2"}
        check_link(root, None, {}, link)
        source.fm["access"] = "paywalled"
        with self.assertRaisesRegex(ValueError, "公開資料"):
            check_link(root, None, {}, link)
        source.fm["access"] = "open"
        source.fm.pop("license_url")
        with self.assertRaisesRegex(ValueError, "license_url"):
            check_link(root, None, {}, link)

    def test_structured_fact_requires_purpose_proof_and_real_code_line(self):
        from passages import load_writing_fact

        path = self.r / "writer/cards/prop/prop-source.md"
        markdown = """---
id: prop-source
kind: proposition
reader_code: [{card: st-toy, line: 2}]
---
## Setup
Two integers.
## Goal
Predict b.
## Statement
b = a + 1.
## Proof
Read the assignment.
## In code
Line 2 adds one.
"""
        w(path, markdown)
        root = M.Root(self.r)

        def check():
            fact = load_writing_fact(self.r, M.WRITING_CARDS, "notes:prop-source", {"notes": "writer"})
            check_reader_fact(root, fact)

        check()
        for before, after, error in (
            ("Predict b.", "", "Goal"),
            ("Read the assignment.", "", "Proof"),
            ("line: 2", "line: 3", "コード範囲外"),
        ):
            with self.subTest(error=error):
                w(path, markdown.replace(before, after))
                with self.assertRaisesRegex(ValueError, error):
                    check()

    def test_new_pool_first(self):
        code, out = run(*self.a, "new", "claim", "c-one-copy", "--title", "One is one", "--area", "x")
        self.assertEqual(code, 2); self.assertIn("c-one", out)
        self.assertFalse((self.r / "pool/x/c-one-copy.md").exists())
        code, out = run(*self.a, "new", "claim", "c-one-copy", "--title", "One is one", "--area", "x", "--decision", "reuse")
        self.assertEqual(code, 0); self.assertFalse((self.r / "pool/x/c-one-copy.md").exists())
        code, out = run(*self.a, "new", "claim", "c-one-v", "--title", "One is one", "--area", "x", "--decision", "variant:c-one")
        self.assertEqual(code, 0); self.assertIn("type: variant", (self.r / "pool/x/c-one-v.md").read_text(encoding="utf-8"))

    def test_html_has_ids_modes_and_code(self):
        run(*self.a, "run", "run-toy")
        out = Path(self.tmp.name) / "o.html"
        code, o = run(*self.a, "html", "--route", "ok", "--out", str(out))
        self.assertEqual(code, 0, o)
        h = out.read_text(encoding="utf-8")
        for s in ('data-card-id="st-toy"', 'data-card-id="fig-toy"', 'data-m="overview"', "a is one", "実行記録"):
            self.assertIn(s, h)
        self.assertEqual(h.count((self.code / "toy.py").as_uri()), 2)
        self.assertNotIn('data-m="dig"', h)
        self.assertIn('id: \'cl-add\'', h)

        route = self.r / "route/ok/route.yaml"
        route.write_text(route.read_text().replace("order: strict", "order: strict\nshow: gist"), encoding="utf-8")
        self.assertIn('data-m="dig"', M.build_html(M.Root(self.r), "ok"))

    def test_html_embeds_local_figure_and_links_to_pdf_page(self):
        figure = self.r / "pool/x/fig-toy.md"
        figure.write_text(figure.read_text(encoding="utf-8").replace(
            "page: 4\n", 'page: 4\nimage: toy.png\nalt: A & B\nsources: [{src: s1, loc: Fig. 1, pdf_page: 3}]\n'
        ), encoding="utf-8")
        source = self.r / "src/s1.md"
        source.write_text(source.read_text(encoding="utf-8").replace(
            "sha256: abc\n", "sha256: abc\nfile: toy paper.pdf\n"
        ), encoding="utf-8")
        png = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+jJqkAAAAASUVORK5CYII="
        (self.r / "toy.png").write_bytes(b64decode(png))
        pdf = self.r / "toy paper.pdf"
        pdf.touch()
        rendered = M.build_html(M.Root(self.r), "ok")
        self.assertIn(f'src="data:image/png;base64,{png}" alt="A &amp; B"', rendered)
        self.assertIn(f'href="{pdf.as_uri()}#page=3"', rendered)

    def test_closure_and_impact(self):
        root = M.Root(self.r)
        self.assertEqual(M.closure(root, ["st-toy"]), ["c-two", "c-one"])
        self.assertIn("st-toy", M.impact(root, ["c-one"]))


if __name__ == "__main__":
    unittest.main(verbosity=1)
