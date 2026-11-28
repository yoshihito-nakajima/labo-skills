#!/usr/bin/env python3
"""Wait locally for a Codex worker or a weekly usage boundary using read-only state."""
from __future__ import annotations

import argparse
from contextlib import closing
from datetime import datetime
from functools import lru_cache
import json
import math
import mmap
import os
from pathlib import Path
import sqlite3
import time
from uuid import UUID

CODEX = Path(os.environ.get("CODEX_HOME") or Path.home() / ".codex").resolve()
TAIL_BYTES = 512 * 1024
WEEKLY_RESET_TOLERANCE_SECONDS = 60
TURN_STATES = {"task_started": "ターン進行中", "task_complete": "ターン返却", "turn_aborted": "ターン中断"}


def connect(name: str) -> sqlite3.Connection:
    return sqlite3.connect((CODEX / name).as_uri() + "?mode=ro", uri=True, timeout=1)


def tail(path: Path) -> tuple[bytes, ...]:
    info = path.stat()
    return cached_tail(path, info.st_size, info.st_mtime_ns)


@lru_cache(maxsize=12)
def cached_tail(path: Path, size: int, _modified: int) -> tuple[bytes, ...]:
    with path.open("rb") as file:
        start = max(0, size - TAIL_BYTES)
        file.seek(start)
        if start:
            file.readline()
        return tuple(file.read().splitlines())


def latest_turn(path: Path) -> tuple[str, str]:
    if not path.is_file():
        return "履歴準備中", ""
    info = path.stat()
    if not info.st_size:
        return "履歴準備中", ""
    return cached_latest_turn(path, info.st_size, info.st_mtime_ns)


@lru_cache(maxsize=12)
def cached_latest_turn(path: Path, _size: int, _modified: int) -> tuple[str, str]:
    with path.open("rb") as file, mmap.mmap(file.fileno(), 0, access=mmap.ACCESS_READ) as history:
        end = len(history)
        while end:
            match = max(history.rfind(f'"type":"{event}"'.encode(), 0, end) for event in TURN_STATES)
            if match < 0:
                break
            start = history.rfind(b"\n", 0, match) + 1
            stop = history.find(b"\n", match)
            end = start
            if stop < 0:
                continue
            try:
                record = json.loads(history[start:stop])
            except ValueError:
                continue
            event = record.get("payload", {}).get("type")
            if record.get("type") == "event_msg" and event in TURN_STATES:
                timestamp = datetime.fromisoformat(record["timestamp"]).astimezone().strftime("%m/%d %H:%M:%S")
                return TURN_STATES[event], timestamp
    return "ターン状態未確認", ""


def usage_paths(thread_id: str) -> tuple[Path, ...]:
    with closing(connect("state_5.sqlite")) as threads:
        parent = threads.execute("SELECT rollout_path FROM threads WHERE id = ?",
                                 (thread_id,)).fetchone()
        if not parent or not parent[0]:
            raise ValueError("指定スレッドの履歴を取得できません")
        children = threads.execute("""
            SELECT t.rollout_path
              FROM thread_spawn_edges e JOIN threads t ON t.id = e.child_thread_id
             WHERE e.parent_thread_id = ?
             ORDER BY t.updated_at DESC LIMIT 3
        """, (thread_id,)).fetchall()
    return tuple(Path(path) for path in (parent[0], *(child[0] for child in children)) if path)


def same_weekly_window(first: datetime, second: datetime) -> bool:
    # Parent and worker reports can round the same server deadline differently.
    return abs((first - second).total_seconds()) <= WEEKLY_RESET_TOLERANCE_SECONDS


def weekly_usage(paths: tuple[Path, ...]) -> tuple[float, datetime, datetime]:
    samples = []
    for path in paths:
        if not path.is_file():
            continue
        for line in reversed(tail(path)):
            if b'"rate_limits"' not in line or b'"used_percent"' not in line:
                continue
            try:
                record = json.loads(line)
                limits = record["payload"]["rate_limits"]
                if limits.get("limit_id") != "codex":
                    continue
                window = next((part for part in (limits.get("primary"), limits.get("secondary"))
                               if part and part.get("window_minutes") == 10080), None)
                if window is None:
                    continue
                used = float(window["used_percent"])
                if not math.isfinite(used) or not 0 <= used <= 100:
                    continue
                samples.append((datetime.fromisoformat(record["timestamp"]), used,
                                datetime.fromtimestamp(window["resets_at"]).astimezone()))
                break
            except (KeyError, TypeError, ValueError, OverflowError):
                continue
    if not samples:
        raise ValueError("週枠の実測値がありません")
    observed, _, reset = max(samples)
    used = max(sample_used for _, sample_used, sample_reset in samples
               if same_weekly_window(sample_reset, reset))
    return 100 - used, observed, reset


def pending_escalation(rollout: Path, seen: set[str]) -> str | None:
    pending: dict[str, datetime] = {}
    for line in tail(rollout):
        if b'"call_id"' not in line and b'"task_started"' not in line:
            continue
        try:
            record = json.loads(line)
            payload = record.get("payload") or {}
            event = payload.get("type")
            call_id = payload.get("call_id")
            if event == "task_started":
                pending.clear()
            elif event in ("function_call_output", "custom_tool_call_output"):
                pending.pop(call_id, None)
            elif event in ("function_call", "custom_tool_call") and isinstance(call_id, str):
                code = str(payload.get("input") or payload.get("arguments") or "")
                if "sandbox_permissions" in code and "require_escalated" in code:
                    pending[call_id] = datetime.fromisoformat(record["timestamp"])
        except (KeyError, TypeError, ValueError):
            continue
    now = datetime.now().astimezone()
    for call_id, started in pending.items():
        if call_id not in seen and (now - started).total_seconds() >= 45:
            return call_id
    return None


def worker_rollout(thread_id: str, worker: str) -> Path:
    with closing(connect("state_5.sqlite")) as threads:
        row = threads.execute("""
            SELECT t.rollout_path
              FROM thread_spawn_edges e JOIN threads t ON t.id = e.child_thread_id
             WHERE e.parent_thread_id = ? AND (t.id = ? OR t.agent_path = ?)
             ORDER BY t.created_at DESC, t.id DESC LIMIT 1
        """, (thread_id, worker, worker)).fetchone()
    if not row or not row[0]:
        raise ValueError(f"この親の担当履歴が未登録: {worker}")
    return Path(row[0])


def wait_for_worker(thread_id: str, worker: str, stop_at: float, deadline_seconds: int,
                    seen: set[str]) -> tuple[int, str]:
    deadline = time.monotonic() + deadline_seconds
    rollout = worker_rollout(thread_id, worker)
    paths = usage_paths(thread_id)
    window = None
    while True:
        with closing(connect("goals_1.sqlite")) as goals:
            goal = goals.execute("SELECT status FROM thread_goals WHERE thread_id = ?", (thread_id,)).fetchone()
        if goal != ("active",):
            return 5, f"GOAL_INACTIVE goal={goal[0] if goal else 'missing'}"

        remaining, _, reset = weekly_usage(paths)
        status = f"worker={worker} remaining={remaining:g}%"
        if window is None:
            window = reset
        if not same_weekly_window(reset, window) or datetime.now().astimezone() >= window:
            return 3, f"WEEKLY_RESET {status} expected={window.isoformat()} observed={reset.isoformat()}"
        if remaining <= stop_at:
            return 3, f"WEEKLY_STOP {status}"

        state, _ = latest_turn(rollout)
        if state == TURN_STATES["task_complete"]:
            return 0, f"WORKER_RETURNED {status}"
        if state == TURN_STATES["turn_aborted"]:
            return 4, f"WORKER_INTERRUPTED {status}"
        if state == TURN_STATES["task_started"] and (request := pending_escalation(rollout, seen)):
            return 4, f"ESCALATION_PENDING {status} request={request}"

        until_deadline = deadline - time.monotonic()
        if until_deadline <= 0:
            return 0, f"WAITING {status}"
        time.sleep(min(5, until_deadline))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--thread", default=os.environ.get("CODEX_THREAD_ID"), type=UUID)
    parser.add_argument("--weekly-remaining", action="store_true")
    parser.add_argument("--stop-at-remaining", type=float)
    parser.add_argument("--wait-for-worker")
    parser.add_argument("--max-wait-seconds", type=int, default=240)
    parser.add_argument("--seen-request", action="append", default=[])
    args = parser.parse_args()
    if args.thread is None:
        parser.error("--thread または CODEX_THREAD_ID が必要です")
    thread_id = str(args.thread)
    if args.wait_for_worker:
        if args.stop_at_remaining is None or not 0 <= args.stop_at_remaining <= 100:
            parser.error("--wait-for-worker には週枠の停止点 --stop-at-remaining が必要です")
        if args.max_wait_seconds <= 0:
            parser.error("--max-wait-seconds は正の秒数が必要です")
        try:
            code, message = wait_for_worker(thread_id, args.wait_for_worker, args.stop_at_remaining,
                                            args.max_wait_seconds, set(args.seen_request))
        except (ValueError, OSError, sqlite3.Error) as error:
            code, message = 2, f"WAIT_UNVERIFIED {error}"
        print(message)
        raise SystemExit(code)
    if not args.weekly_remaining:
        parser.error("--weekly-remaining または --wait-for-worker が必要です")
    if args.stop_at_remaining is not None and not 0 <= args.stop_at_remaining <= 100:
        parser.error("--stop-at-remaining は0から100の値を指定してください")
    if args.weekly_remaining:
        try:
            remaining, observed, reset = weekly_usage(usage_paths(thread_id))
            if datetime.now().astimezone() >= reset:
                raise ValueError("リセット後の新しい実測値がありません")
        except (ValueError, OSError, sqlite3.Error) as error:
            print(f"WEEKLY_UNVERIFIED {error}")
            raise SystemExit(2)
        stopped = args.stop_at_remaining is not None and remaining <= args.stop_at_remaining
        status = "WEEKLY_STOP" if stopped else "WEEKLY_OK"
        print(f"{status} remaining={remaining:g}% observed={observed.astimezone().isoformat(timespec='seconds')} "
              f"reset={reset.isoformat(timespec='seconds')}")
        raise SystemExit(3 if stopped else 0)


if __name__ == "__main__":
    main()
