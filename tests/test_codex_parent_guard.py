import json
from contextlib import closing
import os
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import unittest


SCRIPT = (
    Path(__file__).resolve().parents[1]
    / "skills" / "long-run-rounds" / "scripts" / "check_codex_parent.py"
)
LUNA = "gpt-6-luna"
SOL = "gpt-5.6-sol"


def event(kind, turn_id):
    return {"type": "event_msg", "payload": {"type": kind, "turn_id": turn_id}}


def context(turn_id, model):
    return {"type": "turn_context", "payload": {"turn_id": turn_id, "model": model}}


class CodexParentGuardTest(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.home = Path(temp.name)
        sessions = self.home / "sessions"
        sessions.mkdir()
        self.rollout = sessions / "rollout.jsonl"
        self.marker = self.home / "claimed"
        # The picker is Luna in every case. Authorization comes from the open turn.
        with closing(sqlite3.connect(self.home / "state_5.sqlite")) as conn, conn:
            conn.execute("CREATE TABLE threads (id, rollout_path, model)")
            conn.execute("INSERT INTO threads VALUES (?, ?, ?)", ("parent", str(self.rollout), LUNA))
        with closing(sqlite3.connect(self.home / "goals_1.sqlite")) as conn, conn:
            conn.execute("CREATE TABLE thread_goals (thread_id, status)")
            conn.execute("INSERT INTO thread_goals VALUES (?, ?)", ("parent", "active"))

    def run_guard(self, records, *, goal="active", thread="parent"):
        with closing(sqlite3.connect(self.home / "goals_1.sqlite")) as conn, conn:
            conn.execute("UPDATE thread_goals SET status = ?", (goal,))
        self.rollout.write_text("".join(f"{json.dumps(record)}\n" for record in records))
        self.marker.unlink(missing_ok=True)
        env = dict(os.environ, CODEX_HOME=str(self.home))
        env.pop("CODEX_THREAD_ID", None)
        if thread is not None:
            env["CODEX_THREAD_ID"] = thread
        return subprocess.run(
            [sys.executable, str(SCRIPT), "--require-model", LUNA, "--require-active-goal", "--",
             sys.executable, "-c", "from pathlib import Path; import sys; Path(sys.argv[1]).touch()", str(self.marker)],
            env=env, capture_output=True, text=True,
        )

    def test_saved_luna_and_previous_luna_do_not_allow_running_sol(self):
        result = self.run_guard([
            event("task_started", "earlier"), context("earlier", LUNA), event("task_complete", "earlier"),
            event("task_started", "current"), context("current", SOL),
        ])
        self.assertEqual(result.returncode, 1)
        self.assertIn("PARENT_MODEL_BLOCKED model=gpt-5.6-sol turn=current", result.stdout)
        self.assertFalse(self.marker.exists())

    def test_open_luna_and_active_goal_allow_command(self):
        result = self.run_guard([event("task_started", "current"), context("current", LUNA)])
        self.assertEqual(result.returncode, 0)
        self.assertIn("PARENT_MODEL_OK", result.stdout)
        self.assertTrue(self.marker.exists())

    def test_model_change_within_open_turn_is_rechecked(self):
        result = self.run_guard([event("task_started", "current"), context("current", LUNA), context("current", SOL)])
        self.assertEqual(result.returncode, 1)
        self.assertIn("PARENT_MODEL_BLOCKED", result.stdout)
        self.assertFalse(self.marker.exists())

    def test_completed_aborted_and_mismatched_turns_fail_closed(self):
        outcomes = {
            "completed": [event("task_complete", "old")],
            "aborted": [event("turn_aborted", "old")],
            "mismatched": [event("task_complete", "old"), event("task_started", "current"), context("old", LUNA)],
        }
        for name, later in outcomes.items():
            with self.subTest(name=name):
                result = self.run_guard([event("task_started", "old"), context("old", LUNA), *later])
                self.assertEqual(result.returncode, 2)
                self.assertIn("PARENT_MODEL_UNVERIFIED", result.stdout)
                self.assertFalse(self.marker.exists())

    def test_paused_goal_blocks_even_luna(self):
        result = self.run_guard([event("task_started", "current"), context("current", LUNA)], goal="paused")
        self.assertEqual(result.returncode, 1)
        self.assertIn("PARENT_GOAL_BLOCKED", result.stdout)
        self.assertFalse(self.marker.exists())

    def test_missing_thread_identity_fails_closed(self):
        result = self.run_guard([event("task_started", "current"), context("current", LUNA)], thread=None)
        self.assertEqual(result.returncode, 2)
        self.assertIn("PARENT_MODEL_UNVERIFIED", result.stdout)
        self.assertFalse(self.marker.exists())
