#!/usr/bin/env python3
"""Gate an unattended Codex operation on the model of this thread's open turn."""

from __future__ import annotations

import argparse
from contextlib import closing
import json
import os
from pathlib import Path
import sqlite3
import subprocess


class UnverifiedTurn(Exception):
    pass


def lookup(database: Path, sql: str, thread_id: str) -> str | None:
    with closing(sqlite3.connect(f"{database.as_uri()}?mode=ro", uri=True, timeout=1)) as db:
        row = db.execute(sql, (thread_id,)).fetchone()
    return row[0] if row else None


def running_turn(rollout: Path) -> tuple[str, str]:
    turn_id = None
    model = None
    with rollout.open("rb") as events:
        for line in events:
            if not line.endswith(b"\n"):
                raise UnverifiedTurn("incomplete rollout record")
            if not any(kind in line for kind in (
                b'"task_started"', b'"task_complete"', b'"turn_aborted"', b'"turn_context"',
            )):
                continue
            record = json.loads(line)
            payload = record.get("payload") or {}
            if record.get("type") == "event_msg":
                event = payload.get("type")
                if event == "task_started":
                    turn_id, model = payload.get("turn_id"), None
                elif event in {"task_complete", "turn_aborted"} and payload.get("turn_id") == turn_id:
                    turn_id, model = None, None
            elif record.get("type") == "turn_context" and turn_id and payload.get("turn_id") == turn_id:
                model = payload.get("model")

    if not isinstance(turn_id, str) or not turn_id or not isinstance(model, str) or not model:
        raise UnverifiedTurn("no open turn with a matching execution model")
    return turn_id, model


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--require-model", required=True, help="exact model ID chosen for the coordinator")
    parser.add_argument("--require-active-goal", action="store_true")
    parser.add_argument("command", nargs=argparse.REMAINDER, help="optional command after --, run only on allow")
    args = parser.parse_args()
    command = args.command[1:] if args.command[:1] == ["--"] else args.command
    try:
        thread_id = os.environ.get("CODEX_THREAD_ID")
        if not thread_id:
            raise UnverifiedTurn("CODEX_THREAD_ID is missing")
        codex_home = Path(os.environ.get("CODEX_HOME") or Path.home() / ".codex").resolve()
        path = lookup(codex_home / "state_5.sqlite", "SELECT rollout_path FROM threads WHERE id = ?", thread_id)
        if not path:
            raise UnverifiedTurn("the current thread has no indexed rollout")
        rollout = Path(path).resolve()
        if not rollout.is_relative_to((codex_home / "sessions").resolve()):
            raise UnverifiedTurn("the current thread's rollout is outside the sessions directory")
        turn_id, model = running_turn(rollout)
        if model != args.require_model:
            print(f"PARENT_MODEL_BLOCKED model={model} turn={turn_id} expected={args.require_model}")
            return 1
        if args.require_active_goal:
            status = lookup(codex_home / "goals_1.sqlite",
                            "SELECT status FROM thread_goals WHERE thread_id = ?", thread_id)
            if status != "active":
                print(f"PARENT_GOAL_BLOCKED model={model} turn={turn_id} goal={status or 'missing'}")
                return 1
    except (UnverifiedTurn, OSError, sqlite3.Error, ValueError, AttributeError, TypeError) as error:
        print(f"PARENT_MODEL_UNVERIFIED {error}")
        return 2

    print(f"PARENT_MODEL_OK model={model} turn={turn_id}", flush=True)
    if command:
        return subprocess.call(command)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
