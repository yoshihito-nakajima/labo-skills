"""Execution checks for long-run-rounds round_status.py on a fictional two-volume course.

Run with ``python3 -m unittest discover -s .agents/tests -p test_round_status.py``.
"""
from __future__ import annotations

import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import textwrap
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "skills/long-run-rounds/scripts/round_status.py"

AUDIT = """# V{n} scope audit
| ID | source | content | plan | state | text | note |
|---|---|---|---|---|---|---|
| A1 | 1.1 | toy lemma | 1 | OK | ch.tex:3 | |
| A2 | 1.2 | toy theorem | 2 | {second} | | |
"""

# A stand-in for review_coverage.py: v1 has one result changed after review.
COVERAGE = textwrap.dedent("""
    import json, sys
    rows = [{"group": "v1", "kind": "result", "has_proof": True, "state": "changed", "accepted_repair": False,
             "file": "chapters/toy.tex", "start": 1},
            {"group": "v1", "kind": "result", "has_proof": True, "state": "current", "accepted_repair": True,
             "file": "chapters/toy.tex", "start": 9}]
    args = sys.argv[1:]
    if args[:1] == ["next"]:
        print(json.dumps([{"file": "chapters/toy.tex", "start": 1, "stable": True}]))
    elif "--json" in args:
        print(json.dumps({"rows": rows}))
    else:
        print("== header\\ncases 2\\nv1      results 2：current 1  changed 1  ／defs 0")
""")


class RoundStatusTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        d = Path(self.tmp.name)
        self.root = d / "course"
        for n, second in ((1, "OK"), (2, "MISSING")):
            (self.root / f"volumes/v{n}").mkdir(parents=True)
            (self.root / f"volumes/v{n}/scope-audit.md").write_text(AUDIT.format(n=n, second=second))
        (self.root / "chapters").mkdir()
        (self.root / "chapters/toy.tex").write_text("\\begin{lemma}x\\end{lemma}\n")
        (self.root / "logs").mkdir()
        (self.root / "handoff").mkdir()
        (self.root / "tools").mkdir()
        (self.root / "tools/cov.py").write_text(COVERAGE)
        self.reviews = d / "review"
        self.reviews.mkdir()
        for name, ready, claimed in (("toy-a-v1-2030-01-02", True, True), ("toy-b-v1-2030-01-02", True, True),
                                     ("toy-c-v1-2030-01-02", False, True), ("toy-d-v1-2030-01-02", False, False),
                                     ("toy-old-v1-2029-12-01", True, True)):
            c = self.reviews / name
            (c / "results").mkdir(parents=True)
            if ready:
                (c / "results/READY").write_text("ok\n")
            if claimed:
                (c / "CLAIMED").write_text("R\n")
        (self.root / "queue.json").write_text(json.dumps({"state": "active", "entries": [
            {"id": "toy-a-v1-2030-01-02", "volume": "v1", "author_state": "awaiting"},
            {"id": "toy-b-v1-2030-01-02", "volume": "v1", "author_state": "repaired"},
            {"id": "toy-c-v1-2030-01-02", "volume": "v1", "author_state": "awaiting"}]}))
        self.cfg = self.root / "tools/round-status.json"
        self.cfg.write_text(json.dumps({
            "title": "toy", "root": "..", "reviews_dir": "../review", "case_prefix": "toy-", "since": "2030-01-01",
            "queue": "queue.json", "queue_keys": ["state"],
            "volumes": [{"name": "v1", "dir": "volumes/v1"}, {"name": "v2", "dir": "volumes/v2"}],
            "sources": ["chapters/**/*.tex"], "log_dir": "logs", "handoff_dir": "handoff",
            "lock": "logs/heavy.lock", "capacity_calib": "logs/capacity.json",
            "capacity_projects_dir": str(d / "no-transcripts"),
            "coverage_cmd": ["{python}", "tools/cov.py"], "stray_dirs": ["local/review"]}))

    def tearDown(self):
        self.tmp.cleanup()

    def status(self, role: str) -> str:
        r = subprocess.run([sys.executable, "-I", str(SCRIPT), "--config", str(self.cfg), role],
                           capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)
        return r.stdout

    @staticmethod
    def fp(out: str) -> str:
        return re.search(r"FINGERPRINT: (\w+)", out).group(1)

    def test_case_buckets_audits_and_cursor(self):
        out = self.status("writing")
        self.assertIn("容量の段階: 未較正", out)
        self.assertIn("queue: state=active", out)
        self.assertRegex(out, r"返却済み\(READY\)・作者未閉鎖 1件.*: a-v1")
        self.assertRegex(out, r"修復済み・再確認待ち 1件.*: b-v1")   # repaired is not the producer's job
        self.assertRegex(out, r"claim中・未返却 1件")
        self.assertRegex(out, r"公開・未claim 1件")
        self.assertRegex(out, r"うちqueue未登録 1件.*: d-v1")
        self.assertNotIn("old-v1", out)                              # before `since`
        self.assertIn("v1 照合・補完中  TODO0 MISSING0 PARTIAL0 OK2 OUT0", out)
        self.assertIn("今の冊 v1 の被覆: 未確認 0  確認後に変更 1", out)
        self.assertIn("（軽微修復の記録で確認済み 1）", out)
        self.assertIn("整理（本文側）: 未  ← 確認後に変更が1件以上", out)
        self.assertIn("heavy.lock: なし", out)
        self.assertNotIn("独立数学レビューの被覆", out)              # reviewer only

    def test_fingerprint_moves_with_actionable_changes_only(self):
        fp0 = self.fp(self.status("writing"))
        self.assertEqual(fp0, self.fp(self.status("writing")))
        with (self.root / "logs/writing.md").open("a", encoding="utf-8") as f:
            f.write("01-02 10:00 確認後に変更の整理 v1：記録 1\n")
        out = self.status("writing")
        self.assertIn("整理（本文側）: 済 01-02 10:00", out)
        fp1 = self.fp(out)
        self.assertNotEqual(fp0, fp1)
        stray = self.root / "local/review/toy-e-v1-2030-01-02"
        stray.mkdir(parents=True)
        out = self.status("writing")
        self.assertIn("!! 置き場所違いのcase 1件", out)
        self.assertNotEqual(fp1, self.fp(out))

    def test_closed_volume_moves_cursor_and_reviewer_sees_candidates(self):
        a = self.root / "volumes/v1/scope-audit.md"
        a.write_text("CLOSED: 2030-01-03 toy-scope-v2\n" + a.read_text())
        out = self.status("review")
        self.assertIn("v1 閉鎖 2030-01-03 toy-scope-v2", out)
        self.assertIn("今の冊 v2 の被覆", out)
        self.assertIn("次の候補 1件（うち安定 1件）", out)
        self.assertIn("相手役 writing の引継ぎ", out)


if __name__ == "__main__":
    unittest.main()
