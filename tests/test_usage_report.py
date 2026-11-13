"""Checks for usage_report.py and label_diff.py on fictional logs and TeX.

Run with ``python3 -m unittest discover -s .agents/tests -p test_usage_report.py``.
"""
from __future__ import annotations

import datetime as dt
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest

SCRIPTS = Path(__file__).resolve().parents[1] / "skills/reading-book/scripts"


def iso(t: float) -> str:
    return dt.datetime.fromtimestamp(t, dt.timezone.utc).isoformat().replace("+00:00", "Z")


def codex_thread(path: Path, sid: str, tid: str, agent: str, opening: str, model: str, samples):
    """samples: list of (seconds ago, input tokens, used_percent)."""
    now, resets = time.time(), time.time() + 3 * 86400
    lines = [{"timestamp": iso(now - 7200), "type": "session_meta",
              "payload": {"session_id": sid, "id": tid, "agent_path": agent}},
             {"timestamp": iso(now - 7200), "type": "turn_context", "payload": {"model": model}},
             {"timestamp": iso(now - 7200), "type": "response_item",
              "payload": {"type": "message", "role": "user", "content": [{"type": "input_text", "text": opening}]}}]
    for ago, tokens, pct in samples:
        lines.append({"timestamp": iso(now - ago), "type": "token_usage_record",
                      "payload": {"session_id": sid, "usage": {"input_tokens": tokens, "cached_input_tokens": tokens // 2,
                                                               "output_tokens": 10, "reasoning_output_tokens": 5}}})
        lines.append({"timestamp": iso(now - ago), "type": "event_msg",
                      "payload": {"type": "token_count", "rate_limits": {"primary": {
                          "used_percent": pct, "window_minutes": 10080, "resets_at": resets}}}})
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(json.dumps(x) for x in lines) + "\n")


class UsageReportTest(unittest.TestCase):
    def test_codex_window_rate_and_threads(self):
        with tempfile.TemporaryDirectory() as t:
            root = Path(t) / "sessions"
            codex_thread(root / "a.jsonl", "S1", "S1", "/root", "please read HANDBACK_WRITING.md", "model-a",
                         [(3600 * 4, 1000, 40.0), (3600 * 2, 1000, 50.0)])
            codex_thread(root / "b.jsonl", "S1", "T2", "/root/worker_x", "task", "model-b", [(3600, 2000, 55.0)])
            codex_thread(root / "c.jsonl", "S2", "S2", "/root", "please read REVIEW_BOOKMARK.md", "model-a",
                         [(1800, 1000, 60.0)])
            threads = Path(t) / "threads.json"
            threads.write_text(json.dumps({"writing": ["HANDBACK_WRITING"], "review": ["REVIEW_BOOKMARK"]}))
            p = subprocess.run([sys.executable, str(SCRIPTS / "usage_report.py"), "codex", "--root", str(root),
                                "--threads", str(threads)], capture_output=True, text=True, timeout=60)
            self.assertEqual(p.returncode, 0, p.stderr)
            out = p.stdout
            self.assertIn("60.0% used of a 7.0-day window", out)
            self.assertIn("burn rate: 5.71%/hour", out)          # 40% -> 60% over 3.5 h
            self.assertIn("WARNING: before the reset", out)
            self.assertIn("80.0%  in 4k", out)                    # writing thread incl. its sub-agent
            self.assertIn("writing / worker_x", out)
            self.assertIn("review", out)


class LabelDiffTest(unittest.TestCase):
    def test_label_level_changes(self):
        old = "\\section{A}\\label{sec:a}\nintro\n\\begin{theorem}\\label{thm:x}\nOld claim.\n\\end{theorem}\n"
        new = old.replace("Old claim.", "New   claim.") + "\\section{B}\\label{sec:b}\n\\begin{lemma}\\label{lem:y}\nZ\n\\end{lemma}\n"
        with tempfile.TemporaryDirectory() as t:
            a, b = Path(t) / "old.tex", Path(t) / "new.tex"
            a.write_text(old)
            b.write_text(new)
            p = subprocess.run([sys.executable, str(SCRIPTS / "label_diff.py"), str(a), str(b)],
                               capture_output=True, text=True, timeout=60)
            self.assertEqual(p.returncode, 0, p.stderr)
            self.assertIn("追加 2、変更 1、削除 0", p.stdout)
            self.assertIn("変更（差 2 行）：`thm:x` theorem", p.stdout)
            self.assertIn("## `sec:b` B（新しい節", p.stdout)
            b.write_text(old.replace("Old claim.", "Old   claim."))  # whitespace only
            p = subprocess.run([sys.executable, str(SCRIPTS / "label_diff.py"), str(a), str(b)],
                               capture_output=True, text=True, timeout=60)
            self.assertIn("追加 0、変更 0", p.stdout)


if __name__ == "__main__":
    unittest.main()
