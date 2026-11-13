"""Checks for the driver trial/audit script, with a fake host on fictional data.

Run with ``python3 -m unittest discover -s .agents/tests -p test_driver_trial.py``.
"""
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

TRIAL = Path(__file__).resolve().parents[1] / "skills/reading-book/scripts/driver_trial.py"

# The fake host reads its behaviour from behaviour.json: per role, extra models it uses, files it touches.
FAKE_HOST = r'''
import datetime, json, os, sys
prompt, model, usage_dir, sid, root = sys.argv[1:6]
role = "review" if "REVIEW.md" in prompt else "writing"
beh = json.load(open(os.path.join(root, "behaviour.json"))).get(role, {})
os.makedirs(os.path.join(usage_dir, sid), exist_ok=True)
for m in [model] + beh.get("extra_models", []):
    rec = {"timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
           "message": {"id": os.urandom(4).hex(), "model": m, "usage": {"output_tokens": beh.get("tokens", 10)}}}
    with open(os.path.join(usage_dir, sid, "s.jsonl"), "a") as f:
        f.write(json.dumps(rec) + "\n")
for rel in beh.get("touch", []):
    p = os.path.join(root, rel); os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "a") as f: f.write("x")
print("NEXT_SLEEP=30\nSTATUS=" + role + " done")
'''


class DriverTrialTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name).resolve()
        (self.root / "usage").mkdir()
        (self.root / "fake_host.py").write_text(FAKE_HOST)
        for f in ("WRITING.md", "REVIEW.md"):
            (self.root / f).write_text("manual")
        (self.root / "text").mkdir()
        (self.root / "text/ch1.tex").write_text("body")
        (self.root / "review/pkt").mkdir(parents=True)
        self.cfg = {
            "workspace": str(self.root), "course_dir": ".", "logs_dir": "logs", "time_scale": 0,
            "hosts": {"fake": {"cmd": [sys.executable, str(self.root / "fake_host.py"), "{prompt}", "{model}",
                                       str(self.root / "usage"), "{session_id}", str(self.root)],
                               "usage": {"format": "jsonl-usage", "dir": str(self.root / "usage")}}},
            "tiers": {"fake": {"upper": "big-model", "normal": "mid-model"}},
            "roles": {"writing": {"host": "fake", "tier": "normal", "effort": "low", "manual": "WRITING.md"},
                      "review": {"host": "fake", "tier": "normal", "effort": "low", "manual": "REVIEW.md"}},
            "usage": {"window_hours": 5, "budget": 100000, "weights": {"output_tokens": 1}},
            "trial": {"record_dir": "records", "unchanged": ["WRITING.md", "REVIEW.md"],
                      "unchanged_by_role": {"review": ["text"]}, "claim_glob": str(self.root / "review/*"),
                      "heavy_cycle_units": 100, "writing_cycles_for_upper_check": 2},
        }

    def tearDown(self):
        self.tmp.cleanup()

    def run_trial(self, behaviour: dict, *args):
        (self.root / "behaviour.json").write_text(json.dumps(behaviour))
        (self.root / "pipeline.json").write_text(json.dumps(self.cfg))
        return subprocess.run([sys.executable, str(TRIAL), "--config", str(self.root / "pipeline.json"), *args],
                              capture_output=True, text=True, timeout=60)

    def last_history(self):
        return json.loads((self.root / "logs/trial-history.jsonl").read_text().splitlines()[-1])

    def test_light_trial_records_and_carries_pending(self):
        p = self.run_trial({}, "--display-before", "8")
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        record = Path(p.stdout.strip().splitlines()[-1]).read_text()
        self.assertIn("配管 writing: 合格", record)
        self.assertIn("|exit / seconds|", record)
        self.assertIn("mid-model:1", record)
        self.assertIn("保護対象：なし", record)
        self.assertIn("- [ ] heavy_cycle", record)
        h = self.last_history()
        self.assertEqual(set(h["pending"]), {"heavy_cycle", "upper_not_from_writing", "upper_from_review", "claim_seen"})
        self.assertTrue((self.root / "logs/usage-readings.jsonl").exists())

    def test_heavy_cycle_upper_and_claim_close_checks(self):
        beh = {"writing": {"tokens": 200},
               "review": {"extra_models": ["big-model"], "touch": ["review/pkt/CLAIMED"]}}
        p = self.run_trial(beh)
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        h = self.last_history()
        self.assertEqual(h["pending"], ["upper_not_from_writing"])
        self.assertIn("- [x] claim_seen", Path(h["record"]).read_text())

    def test_writing_upper_is_a_violation_and_stays_pending(self):
        p = self.run_trial({"writing": {"extra_models": ["big-model"]}})
        h = self.last_history()
        self.assertIn("upper_not_from_writing", h["pending"])
        self.assertTrue(h["found"]["upper_not_from_writing"].startswith("VIOLATION"))

    def test_protected_change_is_reported(self):
        p = self.run_trial({"review": {"touch": ["text/ch1.tex"]}})
        self.assertEqual(p.returncode, 1)
        self.assertIn("text", self.last_history()["changed"])

    def test_stop_file_blocks_trial(self):
        (self.root / "STOP").write_text("")
        p = self.run_trial({})
        self.assertEqual(p.returncode, 4)
        self.assertIn("stop file", p.stdout)

    def test_audit_closes_upper_check_from_logs(self):
        self.run_trial({})
        logs = self.root / "logs"
        with open(logs / "writing-costs.jsonl", "a") as f:
            f.write(json.dumps({"time": "2026-01-01T10:00:00", "cost": 50, "models": {"mid-model": 3}}) + "\n")
        p = subprocess.run([sys.executable, str(TRIAL), "--config", str(self.root / "pipeline.json"), "--audit"],
                           capture_output=True, text=True, timeout=60)
        self.assertEqual(p.returncode, 0, p.stderr)
        h = self.last_history()
        self.assertEqual(h["kind"], "audit")
        self.assertNotIn("upper_not_from_writing", h["pending"])   # 2 writing cycles without the upper tier


if __name__ == "__main__":
    unittest.main()
