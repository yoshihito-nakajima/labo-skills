"""Checks for the host-neutral course driver and packet claims, with a fake host on fictional data.

Run with ``python3 -m unittest discover -s .agents/tests -p test_course_driver.py``.
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPTS = Path(__file__).resolve().parents[1] / "skills/reading-book/scripts"
DRIVER = SCRIPTS / "course_driver.py"
CLAIM = SCRIPTS / "claim_packet.py"

FAKE_HOST = r'''
import datetime, json, os, sys
prompt, model, effort, usage_dir, mode, sid = sys.argv[1:7]
with open(os.path.join(usage_dir, "calls.txt"), "a") as f:
    f.write(json.dumps({"model": model, "effort": effort, "prompt": prompt}) + "\n")
rec = {"timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
       "message": {"id": os.urandom(4).hex(), "model": model, "usage": {"input_tokens": 100, "output_tokens": 10}}}
os.makedirs(os.path.join(usage_dir, sid), exist_ok=True)
with open(os.path.join(usage_dir, sid, "session.jsonl"), "a") as f:
    f.write(json.dumps(rec) + "\n")
# a concurrent, unrelated session writing at the same time must not count toward this cycle
other = dict(rec, message=dict(rec["message"], id=os.urandom(4).hex(), model="big-model"))
with open(os.path.join(usage_dir, "other-session.jsonl"), "a") as f:
    f.write(json.dumps(other) + "\n")
if mode == "limit":
    print("ERROR: You've hit your usage limit.")
else:
    print("work done\nNEXT_SLEEP=30\nSTATUS=wrote unit A")
'''


def load_driver():
    spec = importlib.util.spec_from_file_location("course_driver", DRIVER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class CourseDriverTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name).resolve()
        (self.root / "usage").mkdir()
        (self.root / "fake_host.py").write_text(FAKE_HOST)

    def tearDown(self):
        self.tmp.cleanup()

    def config(self, mode="ok", budget=1_000_000, **extra):
        cfg = {
            "workspace": str(self.root), "course_dir": ".", "logs_dir": "logs", "time_scale": 0,
            "hosts": {"fakehost": {"cmd": [sys.executable, str(self.root / "fake_host.py"), "{prompt}", "{model}",
                                            "{effort}", str(self.root / "usage"), mode, "{session_id}"],
                                    "usage": {"format": "jsonl-usage", "dir": str(self.root / "usage")}}},
            "tiers": {"fakehost": {"upper": "big-model", "normal": "mid-model", "light": "small-model"}},
            "roles": {"writing": {"host": "fakehost", "tier": "normal", "effort": "low", "manual": "MANUAL.md",
                                  "status_cmd": "status writing", "units": "1 unit", "budget_share": 0.5,
                                  "state_files": ["progress.md"]}},
            "usage": {"window_hours": 5, "budget": budget, "pause_at_fraction": 0.8,
                      "weights": {"input_tokens": 1, "output_tokens": 5}, "model_weights": {"big": 2.0}},
        }
        cfg.update(extra)
        path = self.root / "pipeline.json"
        path.write_text(json.dumps(cfg))
        return path

    def run_driver(self, *args):
        return subprocess.run([sys.executable, str(DRIVER), "--config", str(self.root / "pipeline.json"), *args],
                              capture_output=True, text=True, timeout=60)

    def calls(self):
        f = self.root / "usage/calls.txt"
        return [json.loads(x) for x in f.read_text().splitlines()] if f.exists() else []

    def test_three_cycles_resolve_tier_and_effort(self):
        self.config()
        p = self.run_driver("writing", "--max-cycles", "3")
        self.assertEqual(p.returncode, 0, p.stderr)
        calls = self.calls()
        self.assertEqual(len(calls), 3)
        self.assertTrue(all(c["model"] == "mid-model" and c["effort"] == "low" for c in calls))
        self.assertIn("MANUAL.md", calls[0]["prompt"])
        self.assertIn("upper=big-model", calls[0]["prompt"])
        log = (self.root / "logs/writing-driver.log").read_text()
        self.assertEqual(log.count("cycle end exit=0"), 3)
        self.assertIn("cost=150 ", log)          # own session only; the concurrent 300-unit session is excluded
        self.assertIn("models=mid-model:1", log)
        self.assertIn("mean=150", log)
        self.assertIn("status=wrote unit A", log)

    def test_moving_average_and_dirty_state(self):
        self.config()
        subprocess.run(["git", "init", "-q"], cwd=self.root, check=True)
        (self.root / "progress.md").write_text("x")
        logs = self.root / "logs"
        logs.mkdir()
        (logs / "writing-costs.jsonl").write_text("\n".join(json.dumps({"cost": c}) for c in (1000, 2000)) + "\n")
        self.run_driver("writing", "--once")
        log = (logs / "writing-driver.log").read_text()
        self.assertIn("mean=1050", log)        # (1000 + 2000 + 150) / 3
        self.assertIn("dirty=progress.md", log)

    def test_usage_reading_and_calibration(self):
        self.config(budget=1000)
        self.run_driver("writing", "--once")   # 450 units in the window (own 150 + other 300)
        for pct in (10, 30):
            p = self.run_driver("usage", "--reading", str(pct))
            self.assertEqual(p.returncode, 0, p.stderr)
        p = self.run_driver("usage", "--calibrate")
        self.assertEqual(p.returncode, 1)
        self.assertIn("not enough readings", p.stdout)
        self.run_driver("usage", "--reading", "45")
        p = self.run_driver("usage", "--calibrate")
        self.assertEqual(p.returncode, 0, p.stdout)
        self.assertIn("proposed budget: 1500", p.stdout)  # median of 4500, 1500, 1000
        self.assertEqual(json.loads((self.root / "pipeline.json").read_text())["usage"]["budget"], 1000)

    def test_stop_file(self):
        self.config()
        (self.root / "STOP_writing").write_text("")
        p = self.run_driver("writing", "--max-cycles", "3")
        self.assertEqual(p.returncode, 0)
        self.assertEqual(self.calls(), [])
        self.assertIn("STOP file found", p.stdout)

    def test_host_limit_is_detected(self):
        self.config(mode="limit")
        self.run_driver("writing", "--once")
        self.assertIn("host reports a usage limit", (self.root / "logs/writing-driver.log").read_text())

    def test_pause_above_budget_fraction(self):
        self.config(budget=100)  # one fake cycle (150 + 300 concurrent units) already exceeds 80%
        self.run_driver("writing", "--once")
        self.run_driver("writing", "--max-cycles", "1")
        self.assertEqual(len(self.calls()), 1)
        self.assertIn("of window budget; waiting", (self.root / "logs/writing-driver.log").read_text())

    def test_pacing_interval(self):
        mod = load_driver()
        d = mod.Driver(self.config(budget=1000), "writing")
        # 5h window, budget 1000, 80% usable, half share -> 400 units per window; 40 per cycle -> 10 cycles.
        self.assertAlmostEqual(d.pacing_interval(40.0), 5 * 3600 / 10)
        d2 = mod.Driver(self.config(pacing={"cycles_per_window": 10}), "writing")
        d2.cfg["usage"] = {}
        self.assertAlmostEqual(d2.pacing_interval(None), 5 * 3600 / 5)

    def test_dry_prompt(self):
        self.config()
        self.run_driver("writing", "--dry")
        self.assertIn("dry run ok", self.calls()[0]["prompt"])


class ClaimPacketTest(unittest.TestCase):
    def test_exclusive_claim(self):
        with tempfile.TemporaryDirectory() as t:
            pkt = Path(t) / "packet"
            pkt.mkdir()
            first = subprocess.run([sys.executable, str(CLAIM), str(pkt), "review-side"], capture_output=True, text=True)
            second = subprocess.run([sys.executable, str(CLAIM), str(pkt), "writing-side"], capture_output=True, text=True)
            show = subprocess.run([sys.executable, str(CLAIM), str(pkt), "--show"], capture_output=True, text=True)
            self.assertEqual(first.returncode, 0)
            self.assertEqual(second.returncode, 3)
            self.assertIn("review-side", second.stdout)
            self.assertIn("review-side", show.stdout)


if __name__ == "__main__":
    unittest.main()
