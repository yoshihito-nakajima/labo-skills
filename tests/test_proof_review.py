"""Exercise the fictional proof-review fixtures: ledger, indicator rules, findings, page build and check."""

from pathlib import Path
import io
import json
import shutil
import tarfile
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1] / "skills"
RPR = ROOT / "reading-proof-review"
PAR = ROOT / "proof-adversarial-review"
EXAMPLE = RPR / "assets/example"


class ProofReviewTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.spec = Path(self.tmp.name) / "spec"
        shutil.copytree(EXAMPLE, self.spec)
        self.out = Path(self.tmp.name) / "page.html"

    def tearDown(self):
        self.tmp.cleanup()

    def py(self, script, *args):
        return subprocess.run([sys.executable, str(script), *map(str, args)], capture_output=True, text=True)

    def edit(self, name, fn):
        p = self.spec / name
        d = json.loads(p.read_text())
        fn(d)
        p.write_text(json.dumps(d))

    # ledger
    def test_example_ledger_is_consistent(self):
        r = self.py(RPR / "scripts/check_ledger.py", self.spec / "steps.json")
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertIn("key S4", r.stdout)

    def test_cycle_is_reported(self):
        self.edit("steps.json", lambda d: d["steps"][2].update(deps=["S5"]))  # S2 depends on S5, S5 on S2
        r = self.py(RPR / "scripts/check_ledger.py", self.spec / "steps.json")
        self.assertEqual(r.returncode, 1)
        self.assertIn("cycle", r.stdout)

    def test_key_needs_a_reason(self):
        def f(d):
            for s in d["steps"]:
                if s["id"] == "S4":
                    del s["why_tier"]
        self.edit("steps.json", f)
        r = self.py(RPR / "scripts/check_ledger.py", self.spec / "steps.json")
        self.assertEqual(r.returncode, 1)
        self.assertIn("why_tier", r.stdout)

    def test_steps_the_theorem_does_not_use_are_flagged(self):
        def f(d):
            for s in d["steps"]:
                if s["id"] == "S6":
                    del s["outside"]
        self.edit("steps.json", f)
        r = self.py(RPR / "scripts/check_ledger.py", self.spec / "steps.json")
        self.assertEqual(r.returncode, 1)
        self.assertIn("does not depend on", r.stdout)

    # indicator
    def test_indicator_rules(self):
        r = self.py(RPR / "scripts/indicator.py", self.spec / "review.json")
        self.assertEqual(r.returncode, 0, r.stdout)
        self.edit("review.json", lambda d: d["indicator"].update(verdict="journal"))
        r = self.py(RPR / "scripts/indicator.py", self.spec / "review.json")
        self.assertEqual(r.returncode, 1)
        self.assertIn("exceeds", r.stdout)

    def test_novelty_cannot_be_strong_while_closest_work_is_unread(self):
        def f(d):
            for a in d["indicator"]["axes"]:
                if a["key"] == "novelty":
                    a["level"] = "strong"
        self.edit("review.json", f)
        r = self.py(RPR / "scripts/indicator.py", self.spec / "review.json")
        self.assertEqual(r.returncode, 1)
        self.assertIn("unread", r.stdout)

    def test_no_verdict_without_review(self):
        def f(d):
            d["indicator"]["facts"]["review_done"] = False
        self.edit("review.json", f)
        r = self.py(RPR / "scripts/indicator.py", self.spec / "review.json")
        self.assertEqual(r.returncode, 1)

    # findings
    def test_findings_merge_unions_viewpoints_and_validates(self):
        a, b = PAR / "assets/example/report-a.json", PAR / "assets/example/report-b.json"
        out = Path(self.tmp.name) / "merged.json"
        r = self.py(PAR / "scripts/findings.py", "merge", a, b, "--out", out)
        self.assertEqual(r.returncode, 0, r.stdout)
        merged = json.loads(out.read_text())["findings"]
        self.assertEqual(len(merged), 2)
        f01 = next(f for f in merged if f["id"] == "F01")
        self.assertEqual(sorted(f01["from"]), ["counterexample hunt", "line-by-line"])

    def test_confirmed_finding_needs_evidence(self):
        bad = Path(self.tmp.name) / "bad.json"
        bad.write_text(json.dumps([{"id": "X1", "sev": "major", "status": "confirmed", "short": "s", "from": ["a"], "detail": "d"}]))
        r = self.py(PAR / "scripts/findings.py", "validate", bad)
        self.assertEqual(r.returncode, 1)
        self.assertIn("evidence", r.stdout)

    def test_conflicting_severities_are_not_silently_merged(self):
        a = Path(self.tmp.name) / "a.json"
        b = Path(self.tmp.name) / "b.json"
        base = {"id": "X1", "status": "suspected", "short": "s", "from": ["a"], "detail": "d"}
        a.write_text(json.dumps([dict(base, sev="major")]))
        b.write_text(json.dumps([dict(base, sev="minor", **{"from": ["b"]})]))
        r = self.py(PAR / "scripts/findings.py", "merge", a, b, "--out", Path(self.tmp.name) / "m.json")
        self.assertEqual(r.returncode, 1)
        self.assertIn("rule", r.stdout)

    # page
    def test_page_builds_and_checks_in_both_languages(self):
        for lang in ("en", "ja"):
            r = self.py(RPR / "scripts/build_review_page.py", self.spec, "--out", self.out, "--lang", lang)
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            page = self.out.read_text()
            self.assertIn('id="step-S4"', page)
            self.assertIn("t-keyc", page)            # the key step is styled as key
            import re  # a real KaTeX copy contains "{{" itself; only template placeholders count
            self.assertIsNone(re.search(r"\{\{(BODY|TITLE|LANG|EXTRA_SCRIPT|L:[a-z_]+)\}\}", page))
            c = self.py(RPR / "scripts/check_review_page.py", self.out, "--spec", self.spec)
            self.assertEqual(c.returncode, 0, c.stdout)

    def test_page_refuses_a_verdict_above_the_cap(self):
        self.edit("review.json", lambda d: d["indicator"].update(verdict="journal"))
        r = self.py(RPR / "scripts/build_review_page.py", self.spec, "--out", self.out)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("violates", r.stdout + r.stderr)

    def test_finding_must_name_a_known_step(self):
        self.edit("review.json", lambda d: d["findings"][0].update(steps=["S99"]))
        r = self.py(RPR / "scripts/build_review_page.py", self.spec, "--out", self.out)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("S99", r.stdout + r.stderr)

    def test_checker_catches_a_broken_link(self):
        self.py(RPR / "scripts/build_review_page.py", self.spec, "--out", self.out)
        self.out.write_text(self.out.read_text().replace('id="step-S3"', 'id="step-gone"', 1))
        c = self.py(RPR / "scripts/check_review_page.py", self.out, "--spec", self.spec)
        self.assertEqual(c.returncode, 1)
        self.assertIn("step-S3", c.stdout)

    # KaTeX fetch (no network: a local tarball stands in for the registry)
    def fake_katex_tarball(self, extra=None):
        buf = io.BytesIO()
        with tarfile.open(fileobj=buf, mode="w:gz") as t:
            files = {"package/dist/katex.min.js": b"/*js*/", "package/dist/katex.min.css": b"/*css*/", "package/LICENSE": b"MIT",
                     "package/dist/fonts/KaTeX_Main-Regular.woff2": b"font", "package/dist/fonts/../../evil.txt": b"x",
                     "package/dist/katex.js": b"not wanted"}
            files.update(extra or {})
            for name, data in files.items():
                ti = tarfile.TarInfo(name)
                ti.size = len(data)
                t.addfile(ti, io.BytesIO(data))
        data = buf.getvalue()
        path = Path(self.tmp.name) / "katex.tgz"
        path.write_bytes(data)
        sys.path.insert(0, str(RPR / "scripts"))
        import fetch_katex
        return path, fetch_katex.integrity(data)

    def test_fetch_katex_verifies_and_extracts_only_wanted_files(self):
        tgz, integ = self.fake_katex_tarball()
        dest = Path(self.tmp.name) / "cache"
        r = self.py(RPR / "scripts/fetch_katex.py", "--dest", dest, "--url", tgz.as_uri(), "--sha512", integ)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual(sorted(p.name for p in dest.iterdir()), ["LICENSE", "fonts", "katex.min.css", "katex.min.js"])
        self.assertEqual([p.name for p in (dest / "fonts").iterdir()], ["KaTeX_Main-Regular.woff2"])
        self.assertFalse((Path(self.tmp.name) / "evil.txt").exists())

    def test_fetch_katex_refuses_a_wrong_hash_and_unpacks_nothing(self):
        tgz, _ = self.fake_katex_tarball()
        dest = Path(self.tmp.name) / "cache"
        r = self.py(RPR / "scripts/fetch_katex.py", "--dest", dest, "--url", tgz.as_uri(), "--sha512", "sha512-AAAA")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("integrity mismatch", r.stdout + r.stderr)
        self.assertFalse(dest.exists())

    def test_site_export_writes_a_page_whose_anchors_and_blocks_are_consistent(self):
        import re
        site = Path(self.tmp.name) / "site"
        r = self.py(RPR / "scripts/export_site_page.py", self.spec, "--slug", "example-review", "--out-dir", site, "--lang", "en")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        page = (site / "example-review.md").read_text()
        self.assertTrue(page.startswith('+++\ntitle = "'))
        self.assertIn('slug = "example-review"', page)
        self.assertTrue((site / "figures/example-review/diagram.svg").read_text().startswith("<svg"))
        anchors = re.findall(r"^::: details .* \{#([A-Za-z][A-Za-z0-9_-]*)\}$", page, re.M)
        self.assertEqual(len(anchors), len(set(anchors)))
        for target in re.findall(r"\]\(#([^)]+)\)", page):
            self.assertIn(target, anchors)
        depth = 0
        for line in page.splitlines():
            if line.startswith("::: details "):
                depth += 1
            elif line == ":::":
                depth -= 1
                self.assertGreaterEqual(depth, 0)
        self.assertEqual(depth, 0)
        self.assertNotIn("<span", page)
        self.assertIn("asset:diagram.svg", page)
        self.assertEqual(self.py(RPR / "scripts/export_site_page.py", self.spec, "--slug", "Bad_Slug", "--out-dir", site).returncode, 1)

    def test_prose_page_builds_from_site_dialect_markdown(self):
        import re
        source = RPR / "assets/prose-example/example-prose.md"
        out = Path(self.tmp.name) / "prose.html"
        r = self.py(RPR / "scripts/build_prose_page.py", source, "--out", out)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        page = out.read_text()
        body = page.split("<main>")[1].split("</main>")[0]
        self.assertEqual(len(re.findall(r"<h2 id=", body)), 2)
        self.assertIn('<details class="proof-details" id="why-b">', body)
        self.assertIn('<details class="proof-details" id="check">', body)
        inner = body.index('id="check"')
        self.assertTrue(body.index('id="why-b"') < inner < body.index("Nothing else changes"))
        self.assertIn('<div class="d">', body)
        self.assertEqual(body.count("<table>"), 1)
        self.assertIn("<figure><svg", body)
        self.assertIn('href="#check"', body)
        self.assertIn('<span class="m">x_1,\\dots,x_9</span>', body)
        self.assertIsNone(re.search(r"\{\{(?:[A-Z_]+|L:[a-z_]+)\}\}", page))  # a real KaTeX copy may contain "{{"
        c = self.py(RPR / "scripts/check_review_page.py", out)
        self.assertEqual(c.returncode, 0, c.stdout + c.stderr)

    def test_prose_page_refuses_bad_anchors_raw_blocks_and_missing_figures(self):
        d = Path(self.tmp.name)
        head = '+++\ntitle = "T"\nslug = "t"\nlanguage = "en"\n+++\n\n'
        for name, body in (("anchor", "::: details Bad {#section-1}\n\nx\n\n:::\n"),
                           ("unclosed", "::: details Open\n\nx\n"),
                           ("figure", "![alt](asset:missing.svg)\n"),
                           ("block", "::: widget demo\n")):
            page = d / f"{name}.md"
            page.write_text(head + body)
            r = self.py(RPR / "scripts/build_prose_page.py", page, "--out", d / f"{name}.html")
            self.assertNotEqual(r.returncode, 0, name)
        raw = d / "raw.md"
        raw.write_text(head + "A <script>alert(1)</script> line.\n")
        out = d / "raw.html"
        self.assertEqual(self.py(RPR / "scripts/build_prose_page.py", raw, "--out", out).returncode, 0)
        self.assertNotIn("<script>alert", out.read_text())

    def test_builder_inlines_a_given_katex_directory(self):
        tgz, integ = self.fake_katex_tarball()
        dest = Path(self.tmp.name) / "cache"
        self.py(RPR / "scripts/fetch_katex.py", "--dest", dest, "--url", tgz.as_uri(), "--sha512", integ)
        r = self.py(RPR / "scripts/build_review_page.py", self.spec, "--out", self.out, "--katex-dir", dest)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("/*js*/", self.out.read_text())


if __name__ == "__main__":
    unittest.main()


class ProofBookTests(unittest.TestCase):
    """Fictional two-block example: source parsing, numbering, TeX generation and (when tools exist) the full build."""

    @classmethod
    def setUpClass(cls):
        sys.path.insert(0, str(RPR / "scripts"))
        import proof_book
        cls.pb = proof_book
        cls.example = RPR / "assets/proof-book-example"

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.proj = Path(self.tmp.name) / "proj"
        shutil.copytree(self.example, self.proj)

    def tearDown(self):
        self.tmp.cleanup()

    def test_numbering_numbers_only_cited_lines_and_citations_resolve(self):
        self.pb.load_project(self.proj)
        q = self.pb.parse(self.pb.BLOCKS_DIR / "Q.txt")
        refs, nums = self.pb.numbering(q)
        self.assertEqual(refs, {"Q.1.1"})
        self.assertEqual(nums, {"Q.1.1": "Q.1.1"})
        p = self.pb.parse(self.pb.BLOCKS_DIR / "P.txt")
        self.assertEqual(self.pb.numbering(p)[1], {"P.1.1": "P.1.1"})

    def test_review_json_renders_in_tex_and_html_and_is_checked(self):
        self.pb.load_project(self.proj)
        self.assertEqual(self.pb.review_problems(json.loads((self.proj / "book.json").read_text(encoding="utf-8"))), [])
        q = self.pb.parse(self.pb.BLOCKS_DIR / "P.txt")
        self.pb.USES.clear(); self.pb.USED_BY.clear()
        tex = self.pb.rv_tex_chapter(["P", "Q"])
        self.assertTrue(any("find-V1" in x for x in tex) and any("risk-R1" in x for x in tex))
        self.assertIn("未実施", self.pb.rv_step_html("Q.1", True))
        self.assertIn("実施（違反なし）", self.pb.rv_step_html("P.1", True))
        self.assertIn('id="find-V1"', self.pb.rv_front_html(["P", "Q"], True))
        self.pb.REVIEW["findings"][0]["where"] = ["P.9"]
        self.assertTrue(self.pb.review_problems(json.loads((self.proj / "book.json").read_text(encoding="utf-8"))))

    def test_citing_a_fine_line_is_refused(self):
        self.pb.load_project(self.proj)
        f = self.pb.BLOCKS_DIR / "P.txt"
        f.write_text(f.read_text(encoding="utf-8").replace("(P.1.1) を $n=2", "(P.1.3) を $n=2"), encoding="utf-8")
        with self.assertRaises(SystemExit):
            self.pb.numbering(self.pb.parse(f))

    def test_cross_block_citation_becomes_a_link_in_tex_and_html(self):
        self.pb.load_project(self.proj)
        self.assertIn(r"\hyperref[P.1]{ブロック~P・段~1}", self.pb.to_tex("ブロック P・段 1 の公式"))
        self.assertIn('href="example-block-P.html#P.1"', self.pb.to_html("ブロック P・段 1 の公式"))

    def test_tex_uses_block_ids_as_section_names_and_has_context_boxes(self):
        self.pb.load_project(self.proj)
        blocks = [self.pb.parse(self.pb.BLOCKS_DIR / f"{b}.txt") for b in ("P", "Q")]
        uses, used_by = self.pb.usage()
        refs = set()
        for b in blocks:
            refs |= self.pb.numbering(b)[0]
        tex = self.pb.render_tex_all(blocks, "/x/example.html", refs, uses, used_by, ["P", "Q"], "見本")
        self.assertIn(r"\renewcommand{\thesection}{P}", tex)
        self.assertIn(r"\renewcommand{\thesection}{Q}", tex)
        self.assertIn(r"\label{Q.1.1}", tex)
        self.assertNotIn(r"\label{Q.1.2}", tex)
        self.assertIn("使われる先", tex)
        self.assertEqual(used_by.get("P.1"), ["Q.1"])

    @unittest.skipUnless(shutil.which("latexmk") and shutil.which("lualatex"), "LuaLaTeX not installed")
    def test_full_build_has_matching_numbers(self):
        try:
            self.pb.find_katex()
        except Exception:
            self.skipTest("KaTeX not available")
        r = subprocess.run([sys.executable, str(RPR / "scripts/proof_book.py"), "build", str(self.proj)], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stdout[-800:] + r.stderr[-800:])
        out = self.proj / "out"
        for name in ("example.pdf", "example.html", "example-index.html", "example-block-P.html", "pages.json"):
            self.assertTrue((out / name).exists(), name)
        self.assertIn("equations numbered: 2", r.stdout)
