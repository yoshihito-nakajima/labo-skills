#!/usr/bin/env python3
"""Read-only usage report for long agent work: limit window, burn rate, and who used what.

  python3 usage_report.py codex [--hours 24] [--rate-hours 6] [--threads threads.json] [--root DIR]
  python3 usage_report.py claude [--hours 5] [--root DIR]

codex  : reads the Codex session logs (default ~/.codex/sessions). The logs carry the host's own
         rate-limit state, so the window usage is exact: used percent, window length, reset time, the
         burn rate over the last --rate-hours and the projected time the window would be exhausted.
         Usage is grouped by root thread (a thread and all its sub-agents), by agent path and by model.
claude : reads Claude Code session logs (default ~/.claude/projects); groups tokens by session and model.
         Claude logs have no limit state; use course_driver.py usage for window estimates.

--threads maps names to keywords found in a root thread's first user message, e.g.
{"writing": ["RESTART_C32"], "review": ["BOOKMARK"]}; unmatched threads are listed by their opening words.
The report never changes anything and imposes no limit.
"""
from __future__ import annotations

import argparse
import collections
import datetime as dt
import glob
import json
import os
import pathlib
import sys
import time


def ts(s: str) -> float:
    return dt.datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp()


def fmt_tokens(n: float) -> str:
    return f"{n / 1e6:.2f}M" if n >= 1e6 else f"{n / 1e3:.0f}k"


def first_user_text(rec: dict) -> str | None:
    p = rec.get("payload") or {}
    if rec.get("type") == "response_item" and p.get("type") == "message" and p.get("role") == "user":
        for c in p.get("content") or []:
            t = c.get("text") or ""
            if t and not t.lstrip().startswith("<"):
                return " ".join(t.split())
    return None


# Step 1: read Codex logs ---------------------------------------------------------
def read_codex(root: pathlib.Path, since: float):
    usage = []          # (time, root_session, agent_path, model, usage dict)
    limits = []         # (time, used_percent, window_minutes, resets_at)
    openings: dict[str, str] = {}
    for f in glob.glob(str(root / "**" / "*.jsonl"), recursive=True):
        if os.path.getmtime(f) < since:
            continue
        meta, model = {}, "?"
        with open(f, errors="ignore") as fh:
            for i, line in enumerate(fh):
                if i == 0 and '"session_meta"' in line or (i == 0 and '"session_id"' in line and not meta):
                    try:
                        meta = json.loads(line).get("payload") or {}
                    except ValueError:
                        meta = {}
                    continue
                if '"turn_context"' in line:
                    try:
                        model = (json.loads(line).get("payload") or {}).get("model") or model
                    except ValueError:
                        pass
                    continue
                if '"token_usage_record"' in line:
                    try:
                        rec = json.loads(line)
                    except ValueError:
                        continue
                    t = ts(rec["timestamp"])
                    if t >= since:
                        p = rec["payload"]
                        usage.append((t, p.get("session_id") or meta.get("session_id") or f,
                                      meta.get("agent_path") or "/root", model, p.get("usage") or {}))
                    continue
                if '"rate_limits"' in line and '"used_percent"' in line:
                    try:
                        rec = json.loads(line)
                    except ValueError:
                        continue
                    rl = (rec.get("payload") or {}).get("rate_limits") or {}
                    prim = rl.get("primary") or {}
                    if "used_percent" in prim:
                        limits.append((ts(rec["timestamp"]), float(prim["used_percent"]),
                                       prim.get("window_minutes"), prim.get("resets_at")))
                    continue
                sid = meta.get("session_id")
                if sid and meta.get("id") == sid and sid not in openings and '"user"' in line:
                    try:
                        txt = first_user_text(json.loads(line))
                    except ValueError:
                        txt = None
                    if txt:
                        openings[sid] = txt
    return usage, sorted(limits), openings


# Step 2: window state and burn rate ----------------------------------------------
def window_report(limits, rate_hours: float) -> list[str]:
    if not limits:
        return ["limit window: no rate-limit records in the period"]
    t_now, used, minutes, resets = limits[-1]
    out = [f"limit window: {used:.1f}% used of a {minutes / 1440:.1f}-day window"
           + (f", resets {dt.datetime.fromtimestamp(resets):%m-%d %H:%M}" if resets else "")
           + f" (as of {dt.datetime.fromtimestamp(t_now):%m-%d %H:%M})"]
    recent = [x for x in limits if x[0] >= t_now - rate_hours * 3600 and (not resets or abs((x[3] or 0) - resets) < 600)]
    if len(recent) >= 2 and recent[-1][0] > recent[0][0]:
        rate = (recent[-1][1] - recent[0][1]) / ((recent[-1][0] - recent[0][0]) / 3600)
        line = f"burn rate: {rate:.2f}%/hour over the last {(recent[-1][0] - recent[0][0]) / 3600:.1f} h"
        if rate > 0:
            empty = t_now + (100 - used) / rate * 3600
            line += f"; at this rate the window is exhausted {dt.datetime.fromtimestamp(empty):%m-%d %H:%M}"
            if resets and empty < resets:
                line += f"  WARNING: before the reset ({(resets - empty) / 3600:.0f} h early)"
        out.append(line)
    else:
        out.append("burn rate: not enough samples yet")
    return out


# Step 3: group usage ------------------------------------------------------------
def group_report(usage, openings, threads: dict[str, list[str]]) -> list[str]:
    def name(sid):
        txt = openings.get(sid, "")
        for n, kws in threads.items():
            if any(k in txt for k in kws):
                return n
        return (txt[:50] + "…") if txt else sid[:8]

    keys = ("input_tokens", "cached_input_tokens", "output_tokens", "reasoning_output_tokens")
    by_root, by_model, by_agent = (collections.defaultdict(collections.Counter) for _ in range(3))
    for _, sid, agent, model, u in usage:
        c = collections.Counter({k: u.get(k) or 0 for k in keys})
        by_root[name(sid)] += c
        by_model[model] += c
        by_agent[(name(sid), agent.split("/")[2] if agent.count("/") >= 2 else "root")] += c
    total = sum(c["input_tokens"] for c in by_root.values()) or 1
    out = [f"records: {len(usage)}; input {fmt_tokens(total)} (of which cached "
           f"{fmt_tokens(sum(c['cached_input_tokens'] for c in by_root.values()))}), output "
           f"{fmt_tokens(sum(c['output_tokens'] for c in by_root.values()))}", "", "by thread (input share, output):"]
    for n, c in sorted(by_root.items(), key=lambda x: -x[1]["input_tokens"]):
        out.append(f"  {100 * c['input_tokens'] / total:5.1f}%  in {fmt_tokens(c['input_tokens'])}  out {fmt_tokens(c['output_tokens'])}"
                   f" (reasoning {fmt_tokens(c['reasoning_output_tokens'])})  {n}")
    out += ["", "by model:"]
    for m, c in sorted(by_model.items(), key=lambda x: -x[1]["input_tokens"]):
        out.append(f"  {100 * c['input_tokens'] / total:5.1f}%  in {fmt_tokens(c['input_tokens'])}  out {fmt_tokens(c['output_tokens'])}  {m}")
    out += ["", "largest sub-agents:"]
    for (n, a), c in sorted(by_agent.items(), key=lambda x: -x[1]["input_tokens"])[:10]:
        out.append(f"  {100 * c['input_tokens'] / total:5.1f}%  in {fmt_tokens(c['input_tokens'])}  {n} / {a}")
    return out


def claude_report(root: pathlib.Path, since: float) -> list[str]:
    by_sess, by_model = collections.Counter(), collections.Counter()
    for f in glob.glob(str(root / "**" / "*.jsonl"), recursive=True):
        if os.path.getmtime(f) < since:
            continue
        seen = set()
        for line in open(f, errors="ignore"):
            if '"usage"' not in line:
                continue
            try:
                rec = json.loads(line)
            except ValueError:
                continue
            m = rec.get("message") if isinstance(rec.get("message"), dict) else {}
            u = m.get("usage")
            if not u or not rec.get("timestamp") or ts(rec["timestamp"]) < since or m.get("id") in seen:
                continue
            seen.add(m.get("id"))
            n = sum(u.get(k) or 0 for k in ("input_tokens", "cache_read_input_tokens", "cache_creation_input_tokens"))
            by_sess[pathlib.Path(f).parts[-3 if "subagents" in f else -1][:8]] += n
            by_model[m.get("model") or "?"] += n
    out = ["by session (context tokens read):"]
    out += [f"  {fmt_tokens(v)}  {k}" for k, v in by_sess.most_common(10)]
    out += ["by model:"] + [f"  {fmt_tokens(v)}  {k}" for k, v in by_model.most_common()]
    return out


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("host", choices=["codex", "claude"])
    ap.add_argument("--hours", type=float)
    ap.add_argument("--rate-hours", type=float, default=6)
    ap.add_argument("--threads", type=pathlib.Path)
    ap.add_argument("--root", type=pathlib.Path)
    a = ap.parse_args(argv)
    if a.host == "codex":
        root = a.root or pathlib.Path("~/.codex/sessions").expanduser()
        since = time.time() - (a.hours or 24) * 3600
        usage, limits, openings = read_codex(root, since)
        threads = json.loads(a.threads.read_text()) if a.threads else {}
        print("\n".join(window_report(limits, a.rate_hours) + [""] + group_report(usage, openings, threads)))
    else:
        root = a.root or pathlib.Path("~/.claude/projects").expanduser()
        print("\n".join(claude_report(root, time.time() - (a.hours or 5) * 3600)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
