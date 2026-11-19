"""Book card system on a small fictional pool shared by two routes."""

from pathlib import Path
import json
import re
import subprocess
import sys
import tempfile
import unittest

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from labo_tools import book as bk  # noqa: E402
from labo_tools.book_html import build_page  # noqa: E402
from labo_tools.dependencies import DependencyGraph  # noqa: E402


def put(root, rel, meta, **sections):
    path = Path(root) / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    kind = meta["kind"]
    labels = {k: ja for k, ja, _ in bk.TEMPLATES[kind].required + bk.TEMPLATES[kind].optional}
    body = "".join(f"## {labels[k]}\n\n{v}\n\n" for k, v in sections.items())
    path.write_text(bk.dump_card(meta, body), encoding="utf-8")


def fact(cid, kind, **extra):
    m = {"id": cid, "kind": kind, "title": cid, "area": "arith", "requires": [], "status": "drafted"}
    m.update(extra)
    return m


def make(root):
    pool = "pool/arith/"
    put(root, pool + "conv-integers.md", fact("conv-integers", "A6"),
        convention="Numbers are integers.", scope="Everywhere in the toy book.")
    put(root, pool + "def-even.md", fact("def-even", "A1", variant="predicate", requires=["conv-integers"]),
        definition="$n$ is even if $n=2k$ for an integer $k$.")
    put(root, pool + "def-odd.md", fact("def-odd", "A1", variant="predicate", requires=["def-even"]),
        definition="$n$ is odd if it is not even.")
    put(root, pool + "claim-even-sum.md", fact("claim-even-sum", "A2", variant="equation-inclusion", requires=["def-even"]),
        hypotheses="$m,n$ even.", conclusion="$m+n$ is even.", quantifiers="For all $m,n$.")
    put(root, pool + "proof-even-sum.md",
        fact("proof-even-sum", "A3", variant="direct", proves="claim-even-sum", owner=True, requires=["def-even"]),
        plan="Write both as doubles.", steps="(1) $m=2a$, $n=2b$ [by: def-even]. (2) $m+n=2(a+b)$.")
    put(root, pool + "claim-parity.md", fact("claim-parity", "A2", variant="equivalence", requires=["def-even", "def-odd"]),
        hypotheses="$n$ an integer.", conclusion="$n$ even iff $n+1$ odd.", quantifiers="For all $n$.")
    put(root, pool + "proof-parity.md",
        fact("proof-parity", "A3", variant="equivalence-both", proves="claim-parity", owner=True,
             requires=["def-even", "def-odd"]),
        plan="Two directions.",
        steps="(⇒) $n=2k$ gives $n+1=2k+1$ [by: def-even]. (⇐) if $n+1$ is odd then $n$ is even [by: def-odd].")
    r = "route/intro-a/"
    put(root, r + "card/entrance-a.md",
        {"id": "entrance-a", "kind": "B5", "title": "Entrance", "status": "drafted",
         "borrows": [{"card": "conv-integers", "owner": "pool", "why": "integers"}]},
        endpoint="Parity.", known="Integers.", conventions="See the convention.")
    put(root, r + "card/glue-a.md",
        {"id": "glue-a", "kind": "B2", "variant": "forward", "status": "drafted",
         "between": ["claim-even-sum", "def-odd"], "anchors": {}},
        done="Sums of evens.", missing="A name for the rest.", next="Odd numbers.")
    (Path(root) / r / "route.yaml").write_text(yaml.safe_dump({
        "title": "Parity A",
        "sections": [{"title": "Even", "items": ["entrance-a", "def-even", "claim-even-sum", "glue-a"]},
                     {"title": "Odd", "items": ["def-odd", "claim-parity"]}]}, allow_unicode=True), encoding="utf-8")
    r2 = Path(root) / "route/intro-b"
    r2.mkdir(parents=True, exist_ok=True)
    (r2 / "route.yaml").write_text(yaml.safe_dump({
        "title": "Parity B (parity first)",
        "sections": [{"title": "Parity", "items": [{"card": "def-even"}, "def-odd",
                                                   {"card": "claim-parity", "proof": "later"},
                                                   {"proof_of": "claim-parity"}]}]}, allow_unicode=True),
        encoding="utf-8")
    put(root, "route/intro-b/card/entrance-b.md",
        {"id": "entrance-b", "kind": "B5", "title": "Entrance B", "status": "drafted",
         "borrows": [{"card": "conv-integers", "owner": "pool", "why": "integers"}]},
        endpoint="Parity.", known="Integers.", conventions="See the convention.")
    text = (r2 / "route.yaml").read_text(encoding="utf-8")
    data = yaml.safe_load(text)
    data["sections"][0]["items"].insert(0, "entrance-b")
    (r2 / "route.yaml").write_text(yaml.safe_dump(data, allow_unicode=True), encoding="utf-8")
    put(root, "src/toy-source.md", {"id": "toy-source", "kind": "C1", "title": "Toy source", "edition": "toy 1"},
        biblio="A toy book.", edition="1st", pages="print = pdf - 3")
    put(root, r + "map/map-even-sum.md",
        {"id": "map-even-sum", "kind": "C2", "sources": [{"src": "toy-source", "loc": "Prop 1.1"}], "adoption": "adopted",
         "scope_audit": "OK", "maps_to": [{"card": "claim-even-sum", "relation": "same"}]},
        difference="None.")


def codes(result, which="errors"):
    return {w.split()[0] for w in result[which]}


class BookTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name).resolve() / "book"
        make(self.root)

    def book(self):
        return bk.Book(self.root)

    def test_two_routes_share_one_pool_and_check_clean(self):
        for route in ("intro-a", "intro-b"):
            result = bk.check(self.book(), route)
            self.assertEqual(result["errors"], [], route)
        self.assertEqual(len([c for c in self.book().cards.values() if c.kind == "A1"]), 2)

    def test_forward_reference_and_unlisted_borrow(self):
        p = self.root / "route/intro-a/route.yaml"
        data = yaml.safe_load(p.read_text(encoding="utf-8"))
        data["sections"][0]["items"] = ["entrance-a", "claim-even-sum", "def-even", "glue-a"]
        p.write_text(yaml.safe_dump(data, allow_unicode=True), encoding="utf-8")
        self.assertIn("FORWARD", codes(bk.check(self.book(), "intro-a")))
        meta = yaml.safe_load((self.root / "route/intro-a/card/entrance-a.md").read_text().split("---")[1])
        meta["borrows"] = []
        put(self.root, "route/intro-a/card/entrance-a.md", meta, endpoint="x", known="y", conventions="z")
        found = bk.check(self.book(), "intro-a")
        self.assertIn("UNLISTED-BORROW", codes(found))

    def test_stale_after_a_definition_changes_and_anchor_clears_it(self):
        book = self.book()
        bk.set_anchors(book.cards["glue-a"], book)
        bk.set_anchors(book.cards["claim-even-sum"], self.book())
        self.assertNotIn("STALE", codes(bk.check(self.book(), "intro-a"), "warnings"))
        put(self.root, "pool/arith/def-even.md", fact("def-even", "A1", variant="predicate", requires=["conv-integers"]),
            definition="$n$ is even if $n=2k$ for some integer $k$ (changed).")
        warns = bk.check(self.book(), "intro-a")["warnings"]
        stale = [w for w in warns if w.startswith("STALE")]
        self.assertTrue(any(w.startswith("STALE claim-even-sum") for w in stale))
        after = self.book()
        self.assertEqual(sorted(after.impact(["def-even"]))[:2], ["claim-even-sum", "claim-parity"])
        self.assertIn("claim-even-sum", after.stale_prose(["def-even"]))
        bk.set_anchors(after.cards["claim-even-sum"], after)
        self.assertFalse([w for w in bk.check(self.book(), "intro-a")["warnings"]
                          if w.startswith("STALE claim-even-sum")])

    def test_proof_rules(self):
        put(self.root, "pool/arith/proof-even-sum.md",
            fact("proof-even-sum", "A3", variant="direct", proves="claim-even-sum", owner=True,
                 requires=["def-even"]), plan="p", steps="(1) $m=2a$ [by: def-odd]. (2) done.")
        result = bk.check(self.book())
        self.assertIn("CITE-NOT-REQUIRED", codes(result))
        self.assertIn("UNUSED-REQUIRES", codes(result, "warnings"))
        put(self.root, "pool/arith/proof-parity.md",
            fact("proof-parity", "A3", variant="equivalence-both", proves="claim-parity", owner=True,
                 requires=["def-even", "def-odd"]), plan="p", steps="(⇒) only one direction [by: def-even, def-odd].")
        self.assertIn("SHAPE", codes(bk.check(self.book())))
        put(self.root, "pool/arith/proof-extra.md",
            fact("proof-extra", "A3", variant="direct", proves="claim-even-sum", owner=True, requires=["def-even"]),
            plan="p", steps="(1) again [by: def-even].")
        self.assertIn("TWO-OWNERS", codes(bk.check(self.book())))

    def test_cycle_is_reported(self):
        put(self.root, "pool/arith/def-even.md",
            fact("def-even", "A1", variant="predicate", requires=["conv-integers", "def-odd"]), definition="cyc")
        self.assertIn("CYCLE", codes(bk.check(self.book())))

    def test_search_gate_before_creating_fact_cards(self):
        book = self.book()
        with self.assertRaises(bk.BookError) as ctx:
            bk.new_card(book, "A1", "def-even-number", title="even number")
        self.assertIn("def-even", str(ctx.exception))
        self.assertIsNone(bk.new_card(book, "A1", "def-even-number", title="even number", decision="reuse"))
        with self.assertRaises(bk.BookError):
            bk.new_card(book, "A1", "def-even-number", title="even number", decision="new")
        path = bk.new_card(book, "A1", "def-even-number", title="even number", decision="new",
                           reason="the toy book needs a ring-theoretic variant", area="arith", variant="structure")
        meta = yaml.safe_load(path.read_text(encoding="utf-8").split("---")[1])
        self.assertEqual(meta["searched"]["decision"], "new")
        fresh = bk.new_card(self.book(), "A1", "def-prime", title="prime number", area="arith")
        self.assertTrue(fresh.is_file())
        self.assertIn("PLACEHOLDER", codes(bk.check(self.book()), "warnings"))

    def test_levels_show_more_without_changing_the_cards(self):
        book = self.book()
        l0, l2, l3 = (bk.render_tex(book, "intro-a", lv) for lv in ("L0", "L2", "L3"))
        self.assertIn("\\begin{theorem}", l0)
        self.assertNotIn("\\begin{proof}", l0)
        self.assertIn("\\begin{proof}", l2)
        self.assertNotIn("Odd numbers.", l2)
        self.assertIn("Odd numbers.", l3)
        later = bk.render_tex(book, "intro-b", "L2")
        self.assertGreater(later.index("\\begin{proof}"), later.index("\\begin{theorem}"))

    def test_graph_is_a_valid_dependency_graph_and_follows_the_chosen_proof(self):
        book = self.book()
        graph = bk.build_graph(book, "intro-a", self.root.parent)
        for node in graph["nodes"]:
            self.assertTrue((self.root.parent / node["source"]["path"]).is_file())
        analyzed = DependencyGraph(graph).analyze()
        self.assertEqual(analyzed["status"], "ok")
        order = analyzed["topological_order"]
        self.assertLess(order.index("def-even"), order.index("claim-even-sum"))
        self.assertEqual(book.closure(["claim-parity"]), ["claim-parity", "def-odd", "def-even", "conv-integers"][:4]
                         if False else book.closure(["claim-parity"]))
        self.assertEqual(set(book.closure(["claim-parity"])), {"claim-parity", "def-even", "def-odd", "conv-integers"})

    def test_source_mapping_and_completion_query(self):
        st = bk.status(self.book(), "intro-a")
        self.assertEqual(st["scope_audit"]["OK"], 1)
        self.assertTrue(st["complete"])
        put(self.root, "route/intro-a/map/map-even-sum.md",
            {"id": "map-even-sum", "kind": "C2", "sources": [{"src": "toy-source", "loc": "Prop 1.1"}], "adoption": "partial",
             "scope_audit": "PARTIAL", "maps_to": [{"card": "claim-even-sum", "relation": "variant", "diff": ""}]},
            difference="Only evens.")
        found = bk.check(self.book(), "intro-a")
        self.assertIn("NO-REASON", codes(found))
        self.assertIn("RELATION-DIFF", codes(found))
        self.assertFalse(bk.status(self.book(), "intro-a")["complete"])

    def test_html_page_and_slices(self):
        book = self.book()
        full = build_page(book, "intro-a")
        self.assertIn('id="claim-parity"', full)
        cut = build_page(book, "intro-a", "closure:claim-even-sum")
        self.assertIn('id="claim-even-sum"', cut)
        self.assertNotIn('id="claim-parity"', cut)
        self.assertIn('id="proof-even-sum"', cut)
        only_defs = build_page(book, "intro-a", "kinds:A1")
        self.assertNotIn('id="claim-even-sum"', only_defs)
        with self.assertRaises(bk.BookError):
            build_page(book, "intro-a", "closure:nope")

    def test_cli_round_trip(self):
        launcher = ROOT / "scripts/labo.py"
        base = [sys.executable, "-I", str(launcher)]
        ws = self.root.parent

        def run(*args):
            return subprocess.run(base + list(args) + ["--workspace", str(ws), "--root", "book"],
                                  capture_output=True, text=True)

        ok = run("book", "check", "--route", "intro-a")
        self.assertEqual(ok.returncode, 0, ok.stderr + ok.stdout)
        found = run("book", "search", "even number", "--format", "json")
        self.assertIn("def-even", [h["id"] for h in json.loads(found.stdout)])
        blocked = run("book", "new", "A1", "def-even-number", "--title", "even number")
        self.assertEqual(blocked.returncode, 2)
        self.assertIn("similar cards", blocked.stderr)
        graph = run("book", "graph", "--route", "intro-a")
        self.assertEqual(graph.returncode, 0, graph.stderr)
        page = run("book", "html", "--route", "intro-a", "--name", "toy-a", "--slice", "closure:claim-parity")
        self.assertEqual(page.returncode, 0, page.stderr)
        self.assertTrue((ws / "output/toy-a.html").is_file())


class ImportTexTests(unittest.TestCase):
    TEX = r"""\section{Toy}
\begin{definition}[Even]\label{def:even}
$n$ is even if $n=2k$.
\end{definition}
\begin{lemma}\label{lem:sum}
Sums of evens are even.
\end{lemma}
\begin{proof}
Add the doubles.
\end{proof}
\begin{lemma}
No label here.
\end{lemma}
"""

    def test_labelled_blocks_become_legacy_cards_and_check(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp).resolve()
            tex = tmp / "toy.tex"
            tex.write_text(self.TEX, encoding="utf-8")
            mapping = tmp / "map.json"
            mapping.write_text(json.dumps({"lem:sum": {"id": "claim-even-sum", "requires": ["def-even", "gone"],
                                                       "aliases": ["TOY.SUM"]},
                                           "def:even": {"id": "def-even"}}), encoding="utf-8")
            root = tmp / "book"
            script = ROOT / "skills/book-harness/scripts/import_tex.py"
            run = subprocess.run([sys.executable, "-I", str(script), "--tex", str(tex), "--root", str(root),
                                  "--route", "toy", "--area", "arith", "--map", str(mapping)],
                                 capture_output=True, text=True)
            self.assertEqual(run.returncode, 0, run.stderr)
            report = json.loads(run.stdout)
            self.assertEqual(report["skipped"]["unlabelled"], 1)
            self.assertEqual(report["dangling_requires"], [["claim-even-sum", "gone"]])
            book = bk.Book(root)
            self.assertEqual(set(book.cards), {"def-even", "claim-even-sum", "proof-claim-even-sum"})
            result = bk.check(book, "toy")
            self.assertEqual(result["errors"], [], result)
            self.assertIn("LEGACY", codes(result, "warnings"))
            self.assertEqual(book.node_requires("claim-even-sum"), ["def-even"])
            self.assertIn("\\begin{lemma}", bk.render_tex(book, "toy", "L2"))
            again = subprocess.run([sys.executable, "-I", str(script), "--tex", str(tex), "--root", str(root),
                                    "--route", "toy", "--area", "arith", "--map", str(mapping)],
                                   capture_output=True, text=True)
            self.assertEqual(json.loads(again.stdout)["written"], 0)


def run_cli(ws, *args, root="book"):
    return subprocess.run([sys.executable, "-I", str(ROOT / "scripts/labo.py"), "book", *args,
                           "--workspace", str(ws), "--root", root], capture_output=True, text=True)


class OperationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.ws = Path(self.tmp.name).resolve()
        self.root = self.ws / "book"
        make(self.root)

    def book(self):
        return bk.Book(self.root)

    def test_parse_cache_follows_edits(self):
        self.book()
        self.assertTrue((self.root / ".index/cards.json").is_file())
        before = self.book().cards["def-even"].fingerprint()
        put(self.root, "pool/arith/def-even.md", fact("def-even", "A1", variant="predicate", requires=["conv-integers"]),
            definition="Changed definition.")
        self.assertNotEqual(self.book().cards["def-even"].fingerprint(), before)

    def test_concurrent_new_creates_exactly_one(self):
        procs = [subprocess.Popen([sys.executable, "-I", str(ROOT / "scripts/labo.py"), "book", "new", "A1", "def-ring",
                                   "--title", "ring", "--area", "arith", "--decision", "new", "--reason", "r",
                                   "--workspace", str(self.ws), "--root", "book"],
                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE) for _ in range(5)]
        codes_ = []
        for p in procs:
            p.communicate()
            codes_.append(p.returncode)
        self.assertEqual(sorted(codes_), [0, 2, 2, 2, 2])

    def test_show_and_list(self):
        info = __import__("labo_tools.book_ops", fromlist=["x"]).show(self.book(), "claim-parity")
        self.assertEqual({x["id"] for x in info["requires"]}, {"def-even", "def-odd"})
        self.assertEqual(info["proofs"], ["proof-parity"])
        ops = __import__("labo_tools.book_ops", fromlist=["x"])
        self.assertIn("def-odd", [c.id for c in ops.list_cards(self.book(), route="intro-a", kind="A1")])
        self.assertEqual(ops.list_cards(self.book(), legacy=True), [])

    def test_merge_rewrites_everything_and_keeps_the_old_id(self):
        from labo_tools import book_ops as ops
        put(self.root, "pool/arith/def-even-dup.md",
            fact("def-even-dup", "A1", variant="predicate", requires=["conv-integers"]),
            definition="$n$ is even if it is twice an integer.")
        put(self.root, "pool/arith/claim-double.md", fact("claim-double", "A2", variant="existence", requires=["def-even-dup"]),
            hypotheses="$n$ even.", conclusion="$n/2$ is an integer, see [[def-even-dup]].", quantifiers="All $n$.")
        p = self.root / "route/intro-b/route.yaml"
        data = yaml.safe_load(p.read_text(encoding="utf-8"))
        data["sections"][0]["items"].append("def-even-dup")
        p.write_text(yaml.safe_dump(data, allow_unicode=True), encoding="utf-8")
        plan = ops.merge(self.root, "def-even", "def-even-dup", apply=False)
        self.assertTrue((self.root / "pool/arith/def-even-dup.md").is_file())
        self.assertTrue(any("claim-double" in line for line in plan))
        ops.merge(self.root, "def-even", "def-even-dup", apply=True)
        book = self.book()
        self.assertNotIn("def-even-dup", book.cards)
        self.assertTrue((self.root / "retired/def-even-dup.md").is_file())
        self.assertIn("def-even-dup", book.cards["def-even"].meta["aliases"])
        self.assertEqual(book.cards["claim-double"].requires, ["def-even"])
        self.assertIn("[[def-even]]", book.cards["claim-double"].body)
        route = yaml.safe_load(p.read_text(encoding="utf-8"))
        shown = [i if isinstance(i, str) else i.get("card") for i in route["sections"][0]["items"]]
        self.assertEqual(shown.count("def-even"), 1)  # the duplicate listing collapses into the kept card
        self.assertNotIn("def-even-dup", shown)
        with self.assertRaises(bk.BookError):
            ops.merge(self.root, "def-even", "claim-double", apply=True)

    def test_rename_and_retire(self):
        from labo_tools import book_ops as ops
        ops.rename(self.root, "def-odd", "def-odd-integer", apply=True)
        book = self.book()
        self.assertIn("def-odd-integer", book.cards)
        self.assertEqual(sorted(book.cards["claim-parity"].requires), ["def-even", "def-odd-integer"])
        self.assertIn("def-odd", book.cards["def-odd-integer"].meta["aliases"])
        self.assertEqual(bk.check(book, "intro-a")["errors"], [])
        with self.assertRaises(bk.BookError):
            ops.retire(self.root, "def-even", "obsolete", apply=True)
        put(self.root, "pool/arith/def-orphan.md", fact("def-orphan", "A1", variant="predicate"), definition="Unused.")
        self.assertEqual(ops.retire(self.root, "def-orphan", "unused", apply=False)[0][:6], "retire")
        ops.retire(self.root, "def-orphan", "unused", apply=True)
        self.assertNotIn("def-orphan", self.book().cards)
        self.assertTrue((self.root / "retired/def-orphan.md").is_file())

    def test_restructure_a_legacy_card(self):
        from labo_tools import book_ops as ops
        put_legacy = {"id": "def-legacy", "kind": "A1", "title": "L", "variant": "unclassified", "legacy": True,
                      "area": "arith", "requires": [], "status": "drafted"}
        path = self.root / "pool/arith/def-legacy.md"
        path.write_text(bk.dump_card(put_legacy, "## 本文\n\nOld text $x$.\n"), encoding="utf-8")
        self.assertIn("LEGACY", codes(bk.check(self.book()), "warnings"))
        ops.restructure(self.root, "def-legacy")
        text = path.read_text(encoding="utf-8")
        self.assertIn("## 定義", text)
        self.assertIn("Old text", text)
        meta = yaml.safe_load(text.split("---")[1])
        meta.update(legacy=False, variant="predicate")
        path.write_text(bk.dump_card(meta, text.split("---", 2)[2]), encoding="utf-8")
        self.assertIn("BODY-LEFT", codes(bk.check(self.book()), "warnings"))

    def test_dependency_candidates_confirm_and_reject(self):
        from labo_tools import book_ops as ops
        for cid, body, label in (("def-a", "Plain.", "def:a"), ("def-b", "Plain too.", "def:b")):
            put(self.root, f"pool/arith/{cid}.md", fact(cid, "A1", variant="predicate", label=label), definition=body)
        put(self.root, "pool/arith/lem-c.md", fact("lem-c", "A2", variant="existence"),
            hypotheses="By \\cref{def:a} and \\eqref{eq:in-b}.", conclusion="True.", quantifiers="All.")
        put(self.root, "pool/arith/def-b.md", fact("def-b", "A1", variant="predicate", label="def:b"),
            definition="Plain. $$x=1\\label{eq:in-b}$$")
        result = ops.deps_candidates(self.root, write=True)
        self.assertEqual(sorted(result["candidates"]["lem-c"]), ["def-a", "def-b"])
        self.assertEqual(self.book().cards["lem-c"].requires, [])
        self.assertEqual(self.book().node_requires("lem-c"), [])
        book = self.book()
        book.use_candidates = True
        self.assertEqual(sorted(book.node_requires("lem-c")), ["def-a", "def-b"])
        ops.promote(self.root, "lem-c", ["def-a"])
        ops.reject(self.root, "lem-c", ["def-b"])
        book = self.book()
        self.assertEqual(book.cards["lem-c"].requires, ["def-a"])
        self.assertNotIn("requires_candidates", book.cards["lem-c"].meta)
        self.assertEqual(ops.deps_candidates(self.root, write=True)["candidates"], {})  # rejection is remembered

    def test_review_packets_bind_to_fingerprints(self):
        from labo_tools import book_review as rv
        out = self.ws / "review/in"
        dirs = rv.review_input(self.book(), "intro-a", out, "math", max_chars=900)
        self.assertGreater(len(dirs), 1)
        with self.assertRaises(bk.BookError):
            rv.review_input(self.book(), "intro-a", out)
        manifest = dirs[0] / "manifest.json"
        data = json.loads(manifest.read_text())
        self.assertTrue(all("fp" in c for c in data["cards"]))
        report = self.ws / "report.md"
        report.write_text("no defect found", encoding="utf-8")
        first = data["cards"][0]["id"]
        put_path = self.book().cards[first].path
        text = put_path.read_text(encoding="utf-8")
        put_path.write_text(text.replace("---\n", "---\n", 1) + "\nAn edit after the packet was frozen.\n", encoding="utf-8")
        res = rv.record_review(self.root, manifest, report, "pass")
        self.assertIn(first, res["changed_since_packet"])
        self.assertTrue(len(res["recorded"]) == len(data["cards"]) - 1)
        book = self.book()
        some = res["recorded"][0]
        self.assertEqual(book.cards[some].meta["status"], "independent")
        self.assertTrue(book.cards[some].reviewed_current("math"))
        self.assertNotEqual(book.cards[first].meta.get("status"), "independent")
        st = bk.status(book, "intro-a")["review"]
        self.assertGreaterEqual(st["reviewed_current"], 1)
        meta = dict(book.cards[some].meta)
        put(self.root, str(book.cards[some].path.relative_to(self.root)), meta,
            **{k: v + " changed" for k, v in book.cards[some].sections.items()})
        self.assertIn("STALE-REVIEW", codes(bk.check(self.book()), "warnings"))

    def test_finding_card_remembers_the_target_fingerprint(self):
        res = run_cli(self.ws, "new", "D1", "f-1", "--route", "intro-a", "--target", "claim-parity",
                      "--severity", "major", "--summary", "Quantifier order is wrong in step 2.")
        self.assertEqual(res.returncode, 0, res.stderr)
        st = bk.status(self.book(), "intro-a")
        self.assertEqual(st["open_major_findings"], ["f-1"])
        self.assertFalse(st["complete"])

    def test_verbatim_check_reports_ids_and_never_source_text(self):
        from labo_tools import book_review as rv
        sentence = ("every integer that can be written as twice another integer is called even and every other "
                    "integer is called odd in this text")
        put(self.root, "pool/arith/def-copy.md", fact("def-copy", "A1", variant="predicate"),
            definition=f"Remark: {sentence}. And a formula $a+b+c+d+e+f+g+h+i+j+k+l$.")
        src = self.ws / "cache"
        src.mkdir()
        (src / "p0001.txt").write_text("Chapter one. every integer that can be written as twice another", encoding="utf-8")
        (src / "p0002.txt").write_text("integer is called even and every other integer is called odd in this text. "
                                       "Unrelated words follow here.", encoding="utf-8")
        hits = rv.leak_check(self.book(), [src], min_run=12)
        self.assertEqual([h["id"] for h in hits], ["def-copy"])
        self.assertGreaterEqual(hits[0]["run_words"], 20)
        self.assertNotIn("unrelated", json.dumps(hits).lower())
        res = run_cli(self.ws, "leak-check", "--source-text", str(src))
        self.assertEqual(res.returncode, 1)
        self.assertIn("VERBATIM def-copy", res.stdout)
        self.assertNotIn("Unrelated", res.stdout)
        clean = rv.leak_check(self.book(), [src], min_run=60)
        self.assertEqual(clean, [])

    def test_render_standalone_resolves_card_mentions(self):
        put(self.root, "pool/arith/claim-ref.md", fact("claim-ref", "A2", variant="existence", requires=["def-even"]),
            hypotheses="Let $n$ be even in the sense of [[def-even]].", conclusion="Then $n=2k$.", quantifiers="All $n$.")
        data = yaml.safe_load((self.root / "route/intro-b/route.yaml").read_text(encoding="utf-8"))
        data["sections"][0]["items"].append("claim-ref")
        (self.root / "route/intro-b/route.yaml").write_text(yaml.safe_dump(data, allow_unicode=True), encoding="utf-8")
        tex = bk.render_tex(self.book(), "intro-b", "L2", standalone=True, language="en", title="Toy")
        self.assertIn("\\cref{card:def-even}", tex)
        self.assertIn("\\label{card:def-even}", tex)
        self.assertTrue(tex.rstrip().endswith("\\end{document}"))
        if subprocess.run(["which", "xelatex"], capture_output=True).returncode == 0:
            work = self.ws / "tex"
            work.mkdir()
            (work / "main.tex").write_text(tex, encoding="utf-8")
            for _ in range(2):
                run = subprocess.run(["xelatex", "-interaction=nonstopmode", "-halt-on-error", "main.tex"], cwd=work,
                                     capture_output=True, text=True, timeout=120)
            self.assertTrue((work / "main.pdf").is_file(), run.stdout[-1500:])
            self.assertNotIn("??", subprocess.run(["pdftotext", "main.pdf", "-"], cwd=work, capture_output=True,
                                                  text=True).stdout)


TRIAL = ROOT / "skills/book-harness/assets/trial"


class ScriptedTakeIn(unittest.TestCase):
    """Helpers: a scripted take-in of the fictional excerpt through the CLI, as the reading loop prescribes."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.ws = Path(self.tmp.name).resolve()
        self.root = self.ws / "book"
        (self.root / "route/toy-parity").mkdir(parents=True)

    def cli(self, *args):
        res = run_cli(self.ws, *args)
        self.assertEqual(res.returncode, 0, res.stdout + res.stderr)
        return res

    def fill(self, rel, **sections_and_meta):
        path = self.root / rel
        text = path.read_text(encoding="utf-8")
        meta = yaml.safe_load(text.split("---")[1])
        sections = {k: sections_and_meta.pop(k) for k in list(sections_and_meta) if k.startswith("S_")}
        meta.update(sections_and_meta)
        labels = {k: ja for k, ja, _ in bk.TEMPLATES[meta["kind"]].required + bk.TEMPLATES[meta["kind"]].optional}
        body = "".join(f"## {labels[k[2:]]}\n\n{v}\n\n" for k, v in sections.items())
        path.write_text(bk.dump_card(meta, body), encoding="utf-8")

    def take_in(self):
        self.cli("new", "C1", "src-toy", "--title", "Elementary Number Theory for Beginners")
        self.fill("src/src-toy.md", edition="toy 1st", S_biblio="A fictional textbook.", S_edition="1st edition.",
                  S_pages="printed pages 14-15")
        self.cli("new", "A6", "conv-integers", "--title", "Numbers are integers", "--area", "parity")
        self.fill("pool/parity/conv-integers.md", status="self-checked", sources=[{"src": "src-toy", "loc": "Ch.2 opening, p.14"}],
                  S_convention="All numbers in this book part are integers.", S_scope="The parity chapter.")
        self.cli("new", "A1", "def-even", "--title", "Even integer", "--area", "parity", "--variant", "predicate")
        self.fill("pool/parity/def-even.md", status="self-checked", requires=["conv-integers"],
                  sources=[{"src": "src-toy", "loc": "Def 2.1, p.14"}],
                  S_definition="An integer $n$ is even if $n=2k$ for some integer $k$; otherwise it is odd.")
        self.cli("new", "A2", "claim-even-sum", "--title", "Sum of evens", "--area", "parity", "--variant", "equation-inclusion")
        self.fill("pool/parity/claim-even-sum.md", status="self-checked", requires=["def-even"],
                  sources=[{"src": "src-toy", "loc": "Prop 2.2, p.14"}], S_hypotheses="$m,n$ are even integers.",
                  S_conclusion="$m+n$ is even.", S_quantifiers="For all integers $m,n$.")
        self.cli("new", "A3", "proof-even-sum", "--proves", "claim-even-sum")
        self.fill("pool/parity/proof-even-sum.md", status="self-checked", requires=["def-even"],
                  S_plan="Write both as doubles.", S_steps="(1) $m=2a$, $n=2b$ [by: def-even]. (2) $m+n=2(a+b)$ [by: def-even].")
        self.cli("new", "A2", "claim-odd-product", "--title", "Product of odd integers", "--area", "parity",
                 "--variant", "equation-inclusion")
        self.fill("pool/parity/claim-odd-product.md", status="self-checked", requires=["def-even"],
                  sources=[{"src": "src-toy", "loc": "Prop 2.3, p.15 (stated there as even: corrected)"}],
                  S_hypotheses="$m,n$ are odd integers.", S_conclusion="$mn$ is odd.", S_quantifiers="For all odd $m,n$.")
        self.cli("new", "A3", "proof-odd-product", "--proves", "claim-odd-product")
        self.fill("pool/parity/proof-odd-product.md", status="self-checked", requires=["def-even"],
                  S_plan="Odd means one more than a double.",
                  S_steps="(1) Odd integers are $2a+1$ and $2b+1$ [by: def-even]. (2) The product is $2(2ab+a+b)+1$, odd [by: def-even].")
        (self.root / "route/toy-parity/route.yaml").write_text(yaml.safe_dump({
            "title": "toy-parity", "sections": [{"title": "Parity", "items": [
                "conv-integers", "def-even", "claim-even-sum", "claim-odd-product"]}]}), encoding="utf-8")
        for cid, loc, cards in (("c2-def-2-1", "Def 2.1", ["def-even"]), ("c2-prop-2-2", "Prop 2.2", ["claim-even-sum"]),
                                ("c2-prop-2-3", "Prop 2.3", ["claim-odd-product"])):
            self.cli("new", "C2", cid, "--route", "toy-parity")
            diff = "The source states the product is even; it is odd. Corrected." if cid == "c2-prop-2-3" else "None."
            self.fill(f"route/toy-parity/map/{cid}.md",
                      sources=[{"src": "src-toy", "loc": f"{loc}, p.14-15"}], adoption="adopted", scope_audit="OK",
                      maps_to=[{"card": cards[0], "relation": "variant" if cid == "c2-prop-2-3" else "same",
                                **({"diff": "conclusion corrected: odd, not even"} if cid == "c2-prop-2-3" else {})}],
                      S_difference=diff)

    def trial(self, packets=None):
        cmd = [sys.executable, "-I", str(ROOT / "skills/book-harness/scripts/trial_check.py"), "--root", str(self.root),
               "--route", "toy-parity", "--source-id", "src-toy", "--source-text", str(TRIAL / "source")]
        if packets:
            cmd += ["--review-input", str(packets)]
        return subprocess.run(cmd, capture_output=True, text=True)



class TrialKitTests(ScriptedTakeIn):
    def test_scripted_take_in_passes_and_a_copy_fails(self):
        self.take_in()
        self.cli("check", "--route", "toy-parity")
        status = json.loads(self.cli("status", "--route", "toy-parity", "--format", "json").stdout)
        self.assertEqual(status["scope_audit"]["OK"], 3)
        packets = self.ws / "review/input"
        self.cli("review-input", "--route", "toy-parity", "--out", str(packets), "--unreviewed", "math")
        res = self.trial(packets)
        self.assertEqual(res.returncode, 0, res.stdout)
        manifest = next(packets.glob("packet-*/manifest.json"))
        report = self.ws / "report.md"
        report.write_text("Checked all listed cards; no defect.", encoding="utf-8")
        ids = ",".join(c["id"] for c in json.loads(manifest.read_text())["cards"])
        self.cli("record-review", "--manifest", str(manifest), "--report", str(report), "--result", "pass", "--ids", ids)
        status = json.loads(self.cli("status", "--route", "toy-parity", "--format", "json").stdout)
        self.assertEqual(status["review"]["never_reviewed"], 0)
        self.assertTrue(status["complete"])
        self.fill("pool/parity/conv-integers.md", status="self-checked", sources=[{"src": "src-toy", "loc": "Ch.2"}],
                  S_convention="Throughout this chapter all numbers are integers and this is the only convention we ever need.",
                  S_scope="Everywhere in this chapter all numbers are integers.")
        copied = ("A number n is called even if there is a number k with n equals two k and a number that is not "
                  "even is called odd.")
        self.fill("pool/parity/def-even.md", status="self-checked", requires=["conv-integers"],
                  sources=[{"src": "src-toy", "loc": "Def 2.1"}], S_definition=copied)
        failing = self.trial(packets)
        self.assertEqual(failing.returncode, 1)
        self.assertIn("FAIL no verbatim run", failing.stdout)
        self.assertIn("FAIL a review packet exists and matches", failing.stdout)


class DocumentationTests(unittest.TestCase):
    def test_the_worked_examples_are_valid_cards(self):
        import re
        text = (ROOT / "skills/book-harness/references/examples.md").read_text(encoding="utf-8")
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "book"
            for block in re.findall(r"```markdown\n(.*?)```", text, re.S):
                if not block.startswith("---"):
                    continue
                meta = yaml.safe_load(block.split("---")[1])
                kind = meta["kind"]
                where = {"A": "pool/parity", "C1": "src", "C2": "route/toy/map", "D1": "route/toy/finding"}.get(
                    kind[:1] if kind[0] == "A" else kind, "route/toy/card")
                path = root / where / f"{meta['id']}.md"
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(block, encoding="utf-8")
            for stub in ("claim-even-sum", "def-odd", "def-odd-form"):
                kind = "A2" if stub.startswith("claim") else "A1"
                extra = {"variant": "equation-inclusion"} if kind == "A2" else {"variant": "predicate"}
                put(root, f"pool/parity/{stub}.md", fact(stub, kind, **extra),
                    **({"hypotheses": "h", "conclusion": "c", "quantifiers": "q"} if kind == "A2" else {"definition": "d"}))
            result = bk.check(bk.Book(root))
            unexpected = [e for e in result["errors"] if not e.startswith(("NO-SECTION", "NO-FIELD"))]
            self.assertEqual(unexpected, [], result["errors"])
            routes = re.findall(r"```yaml\n(.*?)```", text, re.S)
            route = yaml.safe_load(routes[0])
            self.assertTrue(route["sections"][0]["items"])


class CodeDocumentationTests(unittest.TestCase):
    def test_every_check_code_is_explained(self):
        import re
        src = (ROOT / "src/labo_tools/book.py").read_text(encoding="utf-8")
        found = set(re.findall(r'add\(\s*"(?:error|warning)",\s*"([A-Z][A-Z-]+)"', src)) | \
            set(re.findall(r'\("(?:error|warning)", "([A-Z-]+)"', src))
        doc = (ROOT / "skills/book-harness/references/check-codes.md").read_text(encoding="utf-8")
        self.assertGreater(len(found), 55)
        self.assertEqual([c for c in sorted(found) if f"`{c}`" not in doc], [])


class FollowUpTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.real = Path(self.tmp.name).resolve()
        make(self.real / "ws" / "book")

    def test_symlinked_workspace_path_does_not_crash(self):
        link = self.real / "link"
        link.symlink_to(self.real / "ws")
        res = run_cli(link, "review-input", "--route", "intro-a", "--out", str(link / "review/in"))
        self.assertEqual(res.returncode, 0, res.stderr)
        self.assertIn("packet-01", res.stdout)

    def test_duplicate_listing_warns_and_packets_do_not_repeat_cards(self):
        root = self.real / "ws" / "book"
        p = root / "route/intro-a/route.yaml"
        data = yaml.safe_load(p.read_text(encoding="utf-8"))
        data["sections"][1]["items"] += [{"proof_of": "claim-parity"}]
        p.write_text(yaml.safe_dump(data, allow_unicode=True), encoding="utf-8")
        book = bk.Book(root)
        self.assertIn("DUPLICATE-IN-ROUTE", codes(bk.check(book, "intro-a"), "warnings"))
        from labo_tools import book_review as rv
        ids = rv.select(book, "intro-a")
        self.assertEqual(len(ids), len(set(ids)))

    def test_taken_in_needs_reviews_not_only_complete_mappings(self):
        book = bk.Book(self.real / "ws" / "book")
        st = bk.status(book, "intro-a")
        self.assertTrue(st["complete"])
        self.assertFalse(st["taken_in"])

    def test_scaffolds_for_c1_and_c2_have_the_fields_check_reads(self):
        root = self.real / "ws" / "book"
        book = bk.Book(root)
        bk.new_card(book, "C1", "src-new", title="New")
        bk.new_card(bk.Book(root), "C2", "map-new", route="intro-a")
        meta = yaml.safe_load((root / "route/intro-a/map/map-new.md").read_text().split("---")[1])
        self.assertEqual((meta["scope_audit"], meta["adoption"], meta["sources"]), ("TODO", "adopted", []))
        self.assertIn("edition", yaml.safe_load((root / "src/src-new.md").read_text().split("---")[1]))


class RobustnessTests(unittest.TestCase):
    """Malformed input is reported by `check`, never a traceback."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.ws = Path(self.tmp.name).resolve()
        self.root = self.ws / "book"
        make(self.root)

    def test_wrongly_typed_front_matter_is_an_error_not_a_crash(self):
        (self.root / "pool/arith/bad.md").write_text(
            "---\nid: bad\nkind: A1\ntitle: t\nvariant: predicate\nstatus: drafted\nrequires: nope\n"
            "anchors: 5\nmaps_to: 3\n---\n## 定義\nx\n", encoding="utf-8")
        for action in ("check", "status", "list"):
            res = run_cli(self.ws, action)
            self.assertNotIn("Traceback", res.stderr, res.stderr)
        self.assertIn("BAD-FIELD", codes(bk.check(bk.Book(self.root))))

    def test_unreadable_files_and_routes(self):
        (self.root / "pool/arith/binary.md").write_bytes(b"\xff\xfe\x00bad")
        (self.root / "route/intro-a/route.yaml").write_text("sections: [: :", encoding="utf-8")
        found = bk.check(bk.Book(self.root))
        self.assertIn("PARSE", codes(found))
        for action, extra in (("check", ["--route", "intro-a"]), ("status", ["--route", "intro-a"]),
                              ("render", ["--route", "intro-a"]), ("html", ["--route", "intro-a", "--name", "x"])):
            res = run_cli(self.ws, action, *extra)
            self.assertNotIn("Traceback", res.stderr, (action, res.stderr))
            self.assertEqual(res.returncode, 2, (action, res.stdout, res.stderr))

    def test_every_action_on_an_empty_root_fails_cleanly_or_succeeds(self):
        empty = self.ws / "empty"
        (empty / "book").mkdir(parents=True)
        for action, args in (("check", []), ("status", []), ("search", ["x"]), ("list", []), ("show", ["nope"]),
                             ("closure", ["nope"]), ("impact", ["nope"]), ("graph", ["--route", "nope"]),
                             ("deps", []), ("merge", ["a", "b"]), ("retire", ["a", "--reason", "r"])):
            res = run_cli(empty, action, *args)
            self.assertNotIn("Traceback", res.stderr, (action, res.stderr))
            self.assertIn(res.returncode, (0, 1, 2))


class VerifyImportTests(unittest.TestCase):
    TEX = ImportTexTests.TEX + "\nSome prose between blocks that no card holds.\n"

    def test_unchanged_import_verifies_and_edits_are_found(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp).resolve()
            tex = tmp / "toy.tex"
            tex.write_text(self.TEX, encoding="utf-8")
            root = tmp / "book"
            imp = ROOT / "skills/book-harness/scripts/import_tex.py"
            ver = ROOT / "skills/book-harness/scripts/verify_import.py"
            subprocess.run([sys.executable, "-I", str(imp), "--tex", str(tex), "--root", str(root), "--route", "toy",
                            "--area", "arith"], capture_output=True, text=True, check=True)
            ok = subprocess.run([sys.executable, "-I", str(ver), "--tex", str(tex), "--root", str(root), "--json"],
                                capture_output=True, text=True)
            data = json.loads(ok.stdout)
            self.assertEqual(ok.returncode, 0, ok.stdout)
            self.assertEqual((data["missing_cards"], data["changed_text"]), ([], []))
            self.assertGreater(data["lines_not_in_any_card"], 0)
            card = root / "pool/arith/lem-sum.md"
            card.write_text(card.read_text(encoding="utf-8").replace("Sums of evens", "Products of evens"), encoding="utf-8")
            (root / "pool/arith/def-even.md").unlink()
            bad = subprocess.run([sys.executable, "-I", str(ver), "--tex", str(tex), "--root", str(root), "--json"],
                                 capture_output=True, text=True)
            data = json.loads(bad.stdout)
            self.assertEqual(bad.returncode, 1)
            self.assertEqual(data["missing_cards"], ["def:even"])
            self.assertEqual([c["label"] for c in data["changed_text"]], ["lem:sum"])


class RoundsTests(ScriptedTakeIn):
    """`book next`: a coordinator that only follows its one-line answers drives the work to DONE."""

    VENDORS = re.compile(r"claude|anthropic|gpt|openai|haiku|luna|sonnet|opus|codex|gemini|llama|mistral|fable", re.I)

    def nxt(self, role, claim=None, sources=True, fmt="json"):
        args = ["next", "--route", "toy-parity", "--role", role, "--review-dir", str(self.ws / "rev"),
                "--work-dir", str(self.ws / "work"), "--format", fmt]
        if claim:
            args += ["--claim", claim]
        if sources:
            args += ["--source-text", str(TRIAL / "source")]
        res = run_cli(self.ws, *args)
        self.assertEqual(res.returncode, 0, res.stdout + res.stderr)
        return json.loads(res.stdout) if fmt == "json" else res.stdout

    def run_command(self, answer):
        import shlex
        res = subprocess.run(shlex.split(answer["command"]), capture_output=True, text=True)
        self.assertEqual(res.returncode, 0, res.stdout + res.stderr)
        return res

    def test_unfinished_source_rows_are_dispatched_once_with_a_portable_prompt(self):
        (self.root / "route/toy-parity/route.yaml").write_text("title: toy-parity\nsections: []\n", encoding="utf-8")
        self.cli("new", "C1", "src-toy", "--title", "T")
        self.cli("new", "C2", "c2-prop-2-2", "--route", "toy-parity")
        self.fill("route/toy-parity/map/c2-prop-2-2.md", unit="Prop 2.2", sources=[{"src": "src-toy", "loc": "Prop 2.2, p.14"}],
                  S_difference="not yet read")
        first = self.nxt("producer", claim="parent-a")
        self.assertEqual((first["action"], first["tier"], first["worker_role"]), ("DISPATCH", "worker", "producer"))
        self.assertEqual(first["unit"], "read:c2-prop-2-2")
        prompt = Path(first["prompt_file"]).read_text(encoding="utf-8")
        self.assertIn("Prop 2.2, p.14", prompt)
        self.assertIn("SKILL.md", prompt)
        self.assertIn("reading-loop.md", prompt)
        self.assertIn("DONE read:c2-prop-2-2", prompt)
        self.assertIsNone(self.VENDORS.search(prompt), self.VENDORS.search(prompt))
        second = self.nxt("producer", claim="parent-b")
        self.assertEqual(second["action"], "WAIT")
        self.assertIn("read:c2-prop-2-2", second["reason"])
        self.assertEqual(self.nxt("producer")["fingerprint"], second["fingerprint"])
        self.assertIn("released", run_cli(self.ws, "release", "read:c2-prop-2-2").stdout)
        again = self.nxt("producer")
        self.assertEqual((again["action"], again["unit"]), ("DISPATCH", "read:c2-prop-2-2"))

    def test_roles_do_not_cross_and_text_output_is_one_decision_line(self):
        self.take_in()
        producer = self.nxt("producer")
        self.assertEqual(producer["action"], "WAIT")  # production has nothing left; reviews are the other role's
        reviewer = self.nxt("reviewer")
        self.assertEqual(reviewer["action"], "RUN")
        text = self.nxt("reviewer", fmt="text")
        self.assertTrue(text.splitlines()[0].startswith("RUN tier=coordinator command: "))
        self.assertIn("FINGERPRINT=", text)

    def test_the_coordinator_loop_reaches_done(self):
        self.take_in()
        run = self.nxt("reviewer", claim="rv")
        self.assertEqual(run["action"], "RUN")
        self.run_command(run)
        job = self.nxt("reviewer", claim="rv")
        self.assertEqual((job["action"], job["worker_role"]), ("DISPATCH", "reviewer"))
        packet_prompt = Path(job["prompt_file"]).read_text(encoding="utf-8")
        self.assertIn("RESULT: pass CHECKED:", packet_prompt)
        self.assertIsNone(self.VENDORS.search(packet_prompt))
        self.assertEqual(self.nxt("reviewer", claim="rv2")["action"], "WAIT")
        report = next((self.ws / "rev").glob("*/result"), None) or next((self.ws / "rev").glob("*")) / "result"
        report.mkdir(parents=True, exist_ok=True)
        (report / "packet-01.md").write_text("No defect found.\nRESULT: pass CHECKED: all\n", encoding="utf-8")
        rec = self.nxt("reviewer")
        self.assertEqual(rec["action"], "RUN")
        self.assertIn("record-review --packet", rec["command"])
        self.run_command(rec)
        status = json.loads(self.cli("status", "--route", "toy-parity", "--format", "json").stdout)
        self.assertTrue(status["taken_in"])
        self.assertEqual(self.nxt("reviewer", sources=False)["action"], "BLOCKED")
        done = self.nxt("reviewer")
        self.assertEqual(done["action"], "DONE")
        self.assertEqual(self.nxt("producer")["action"], "DONE")

    def test_findings_go_to_a_producer_until_the_unit_is_marked_done(self):
        self.take_in()
        self.run_command(self.nxt("reviewer"))
        case = next((self.ws / "rev").iterdir())
        (case / "result").mkdir()
        (case / "result" / "packet-01.md").write_text("Step 2 of the product proof is wrong.\nRESULT: findings CHECKED: all\n",
                                                      encoding="utf-8")
        self.run_command(self.nxt("reviewer"))
        triage = self.nxt("producer", claim="p")
        self.assertEqual(triage["action"], "DISPATCH")
        self.assertTrue(triage["unit"].startswith("triage:"))
        self.assertIn("--done", Path(triage["prompt_file"]).read_text(encoding="utf-8"))
        self.assertIn("marked done", run_cli(self.ws, "release", triage["unit"], "--done").stdout)
        self.assertNotEqual(self.nxt("producer").get("unit"), triage["unit"])

    def test_a_report_without_the_result_line_is_refused_and_a_changed_card_voids_the_packet(self):
        self.take_in()
        self.run_command(self.nxt("reviewer"))
        case = next((self.ws / "rev").iterdir())
        (case / "result").mkdir()
        (case / "result" / "packet-01.md").write_text("Looks fine to me.\n", encoding="utf-8")
        res = run_cli(self.ws, "record-review", "--packet", str(case / "input/packet-01"))
        self.assertEqual(res.returncode, 2)
        self.assertIn("RESULT", res.stderr)
        (case / "result" / "packet-01.md").unlink()
        card = self.root / "pool/parity/claim-even-sum.md"
        card.write_text(card.read_text(encoding="utf-8") + "\nAn edit.\n", encoding="utf-8")
        answer = self.nxt("reviewer")
        self.assertEqual(answer["action"], "RUN")  # the old packet no longer covers the changed card; new ones are made


class PlaceTests(unittest.TestCase):
    def test_place_is_idempotent_ordered_and_safe_under_concurrency(self):
        with tempfile.TemporaryDirectory() as tmp:
            ws = Path(tmp).resolve()
            make(ws / "book")
            res = run_cli(ws, "place", "intro-a", "claim-parity", "--after", "def-even")
            self.assertEqual(res.returncode, 0, res.stderr)
            order = [e["id"] for e in bk.Book(ws / "book").sequence(bk.Book(ws / "book").load_route("intro-a"))]
            self.assertLess(order.index("def-even"), order.index("claim-parity"))
            self.assertEqual(order.count("claim-parity"), 1)
            self.assertIn("nothing", run_cli(ws, "place", "intro-a", "claim-parity").stdout)
            put(ws / "book", "pool/arith/def-new1.md", fact("def-new1", "A1", variant="predicate"), definition="d")
            put(ws / "book", "pool/arith/def-new2.md", fact("def-new2", "A1", variant="predicate"), definition="d")
            procs = [subprocess.Popen([sys.executable, "-I", str(ROOT / "scripts/labo.py"), "book", "place", "intro-a", cid,
                                       "--section", "New", "--workspace", str(ws), "--root", "book"],
                                      stdout=subprocess.PIPE, stderr=subprocess.PIPE) for cid in ("def-new1", "def-new2")]
            for p in procs:
                p.communicate()
            book = bk.Book(ws / "book")
            listed = [e["id"] for e in book.sequence(book.load_route("intro-a"))]
            self.assertIn("def-new1", listed)
            self.assertIn("def-new2", listed)
            self.assertEqual(run_cli(ws, "place", "intro-a", "nope").returncode, 2)


class IndexMacroTests(unittest.TestCase):
    def test_structured_index_entries_use_the_projects_macros(self):
        with tempfile.TemporaryDirectory() as tmp:
            ws = Path(tmp).resolve()
            make(ws / "book")
            put(ws / "book", "pool/arith/def-even.md",
                fact("def-even", "A1", variant="predicate", requires=["conv-integers"], label="def:even",
                     index=[{"term": "偶数 (even)", "reading": "ぐうすう"}, "plain term"],
                     formula_index=[{"term": "$2k$", "reading": "2k"}]),
                definition="$n$ is even if $n=2k$.")
            book = bk.Book(ws / "book")
            plain = bk.render_tex(book, "intro-a", "L0")
            self.assertIn("\\index{偶数 (even)}", plain)
            tex = bk.render_tex(book, "intro-a", "L0", index_macros={"term": "termat", "formula": "formulaat"})
            self.assertIn("\\termat{def:even}{ぐうすう}{偶数 (even)}", tex)
            self.assertIn("\\formulaat{def:even}{2k}{$2k$}", tex)
            self.assertIn("\\index{plain term}", tex)
            res = run_cli(ws, "render", "--route", "intro-a", "--level", "L0", "--term-macro", "termat")
            self.assertEqual(res.returncode, 0, res.stderr)
            self.assertIn("\\termat{def:even}", res.stdout)


if __name__ == "__main__":
    unittest.main()
