"""Execution checks for usage_window.py on fictional transcripts.

Run with ``python3 -m unittest discover -s .agents/tests -p test_usage_window.py``.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "skills/reading-book/scripts/usage_window.py"


def assistant(ts, mid, model="claude-sonnet-x", out=0, inp=1_000_000):
    return {"type": "assistant", "timestamp": ts, "requestId": "r" + mid,
            "message": {"id": mid, "model": model, "role": "assistant",
                        "usage": {"input_tokens": inp, "output_tokens": out,
                                  "cache_creation_input_tokens": 0, "cache_read_input_tokens": 0},
                        "content": [{"type": "text", "text": "ok"}]}}


def limit(ts, reset="7:20am"):
    return {"type": "assistant", "timestamp": ts, "isApiErrorMessage": True,
            "message": {"id": "x" + ts, "model": "<synthetic>", "role": "assistant",
                        "usage": {"input_tokens": 0, "output_tokens": 0},
                        "content": [{"type": "text",
                                     "text": f"You've hit your 5-hour limit · resets {reset} (Asia/Tokyo)"}]}}


class UsageWindowTest(unittest.TestCase):
    def run_tool(self, root, now, *extra):
        r = subprocess.run([sys.executable, str(SCRIPT), "--projects-dir", str(root), "--now", now,
                            "--json", *extra], capture_output=True, text=True, check=True)
        return json.loads(r.stdout)

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(os.path.realpath(self.tmp.name)) / "projects" / "p"
        (self.root / "s" / "subagents").mkdir(parents=True)
        self.calib = Path(self.tmp.name) / "cal.json"

    def tearDown(self):
        self.tmp.cleanup()

    def write(self, rel, rows):
        p = self.root / rel
        p.write_text("".join(json.dumps(r) + "\n" for r in rows))

    def test_calibrates_from_limit_message_and_stages_current_window(self):
        # Window 02:20-07:20 JST = 17:20-22:20 UTC. 10 sonnet Mtok (weight 30) then the limit.
        prev = [assistant(f"2026-11-17T18:{i:02d}:00Z", f"a{i}") for i in range(10)]
        self.write("one.jsonl", prev + [limit("2026-11-17T20:51:00Z")])
        # The same message logged twice (streaming) counts once; a subagent file counts too.
        cur = [assistant("2026-11-17T22:30:00Z", "b1"), assistant("2026-11-17T22:30:00Z", "b1")]
        self.write("s/subagents/agent.jsonl", cur + [assistant("2026-11-17T22:40:00Z", "b2", inp=4_000_000)])
        out = self.run_tool(self.root.parent, "2026-11-17T23:00:00Z", "--calib", str(self.calib), "--learn")
        self.assertEqual(out["limit"], 30.0)
        self.assertEqual(out["used"], 15.0)  # (1 + 4) Mtok x sonnet 3
        self.assertEqual(out["stage"], "余裕")
        self.assertTrue(out["window_start"].startswith("2026-11-17T22:30"))
        # Saved calibration is reused without --learn; more use moves to 節約 then 停止前.
        self.write("two.jsonl", [assistant("2026-11-17T22:50:00Z", "c1", inp=1_500_000)])
        self.assertEqual(self.run_tool(self.root.parent, "2026-11-17T23:00:00Z", "--calib", str(self.calib))["stage"], "節約")
        self.write("three.jsonl", [assistant("2026-11-17T22:55:00Z", "d1", inp=2_000_000)])
        self.assertEqual(self.run_tool(self.root.parent, "2026-11-17T23:00:00Z", "--calib", str(self.calib))["stage"], "停止前")

    def test_limit_until_reset_then_new_window(self):
        self.write("one.jsonl", [assistant("2026-11-17T18:00:00Z", "a"), limit("2026-11-17T20:51:00Z")])
        during = self.run_tool(self.root.parent, "2026-11-17T21:00:00Z")
        self.assertEqual(during["stage"], "上限中")
        self.assertTrue(during["active_limit_reset"].startswith("2026-11-17T22:20"))
        after = self.run_tool(self.root.parent, "2026-11-17T22:30:00Z")
        self.assertEqual(after["stage"], "未較正")
        self.assertEqual(after["used"], 0.0)
        self.assertIsNone(after["window_start"])


if __name__ == "__main__":
    unittest.main()
