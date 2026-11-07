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
            self.assertNotIn("{{", page)
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

    def test_builder_inlines_a_given_katex_directory(self):
        tgz, integ = self.fake_katex_tarball()
        dest = Path(self.tmp.name) / "cache"
        self.py(RPR / "scripts/fetch_katex.py", "--dest", dest, "--url", tgz.as_uri(), "--sha512", integ)
        r = self.py(RPR / "scripts/build_review_page.py", self.spec, "--out", self.out, "--katex-dir", dest)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("/*js*/", self.out.read_text())


if __name__ == "__main__":
    unittest.main()
