#!/usr/bin/env python3
"""Estimate how much of the 5-hour usage window long unattended runs have used.

The agent cannot read the account's remaining quota directly.  This script
reads Claude Code transcripts (``~/.claude/projects/**/*.jsonl``, all
projects, including subagent files), sums the token usage of assistant
messages with rough relative weights, and compares the sum in the current
5-hour window with the sums observed at past "You've hit your 5-hour limit"
messages (calibration).  Usage from other devices or claude.ai is not in the
transcripts, so the estimate is a lower bound; the limit message stays the
ground truth.

Stages (thresholds are fractions of the calibrated limit):
  余裕     below --save (default 0.6)
  節約     from --save to --stop (default 0.8)
  停止前   from --stop
  上限中   a limit message whose reset time has not passed yet
  未較正   no calibration yet (raw numbers only; treat as 余裕 but watch)

    usage_window.py [--calib FILE] [--learn] [--json]

``--learn`` adds limit messages seen in the last ``--learn-days`` days to the
calibration file (weighted sum from the window start to the first limit
message of that window).
"""
import argparse
import datetime as dt
import json
import os
import re
import statistics
import sys
from pathlib import Path
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

WINDOW = dt.timedelta(hours=5)
# Relative weights: input-token equivalents per token type, times a model factor.
TOKEN_W = {"input_tokens": 1.0, "cache_creation_input_tokens": 1.25,
           "cache_read_input_tokens": 0.1, "output_tokens": 5.0}
MODEL_W = (("opus", 5.0), ("fable", 5.0), ("sonnet", 3.0), ("haiku", 1.0))
LIMIT_RE = re.compile(r"You've hit your (5-hour|weekly) limit\s*·\s*resets\s+(.+?)\s*\(([^)]+)\)")


def model_factor(model):
    m = (model or "").lower()
    for key, w in MODEL_W:
        if key in m:
            return w
    return 5.0


def parse_ts(s):
    return dt.datetime.fromisoformat(s.replace("Z", "+00:00"))


def parse_reset(hit, text, tzname):
    """Next occurrence of the clock time `text` (e.g. '7:20am') after `hit`."""
    try:
        tz = dt.timezone.utc if tzname == "UTC" else ZoneInfo(tzname)
    except ZoneInfoNotFoundError:
        return None
    m = re.match(r"(?:(\w{3}) (\d+),? )?(\d{1,2})(?::(\d{2}))?\s*([ap]m)", text.strip(), re.I)
    if not m:
        return None
    h = int(m.group(3)) % 12 + (12 if m.group(5).lower() == "pm" else 0)
    mi = int(m.group(4) or 0)
    local = hit.astimezone(tz)
    cand = local.replace(hour=h, minute=mi, second=0, microsecond=0)
    while cand <= local:
        cand += dt.timedelta(days=1)
    return cand.astimezone(dt.timezone.utc)


def scan(root, since):
    """Return (events, limits): events = [(ts, weight, model)], limits = [(hit, kind, reset)]."""
    events, limits, seen = [], [], set()
    cutoff = since.timestamp()
    for p in root.rglob("*.jsonl"):
        try:
            if p.stat().st_mtime < cutoff:
                continue
            fh = p.open("rb")
        except OSError:
            continue
        with fh:
            for raw in fh:
                is_usage = b'"usage"' in raw and b'"assistant"' in raw
                is_limit = b"hit your" in raw
                if not (is_usage or is_limit):
                    continue
                try:
                    d = json.loads(raw)
                except ValueError:
                    continue
                ts = d.get("timestamp")
                msg = d.get("message")
                if not ts or not isinstance(msg, dict):
                    continue
                t = parse_ts(ts)
                if t < since:
                    continue
                if is_limit and d.get("isApiErrorMessage"):
                    c = msg.get("content")
                    text = c[0].get("text", "") if isinstance(c, list) and c and isinstance(c[0], dict) else ""
                    m = LIMIT_RE.search(text)
                    if m:
                        limits.append((t, m.group(1), parse_reset(t, m.group(2), m.group(3))))
                    continue
                if d.get("type") != "assistant" or msg.get("model") == "<synthetic>":
                    continue
                u = msg.get("usage")
                if not isinstance(u, dict):
                    continue
                key = (msg.get("id"), d.get("requestId"))
                if key[0] and key in seen:
                    continue
                seen.add(key)
                w = sum(TOKEN_W[k] * (u.get(k) or 0) for k in TOKEN_W) * model_factor(msg.get("model"))
                events.append((t, w / 1e6, msg.get("model") or "?"))
    events.sort()
    limits.sort(key=lambda limit: limit[0])
    return events, limits


def windows(events, limits, now):
    """Known windows end at reset times; others chain from the first message (5 h each)."""
    known = sorted({(r - WINDOW, r) for _, kind, r in limits if r and kind == "5-hour"})
    blocks, cur = [], None
    for t, w, model in events:
        k = next(((s, e) for s, e in known if s <= t < e), None)
        if k:
            if not cur or cur["start"] != k[0]:
                cur = {"start": k[0], "end": k[1], "w": 0.0, "models": {}, "known": True}
                blocks.append(cur)
        elif not cur or t >= cur["end"]:
            end = t + WINDOW
            nxt = next((s for s, _ in known if t < s < end), None)
            cur = {"start": t, "end": nxt or end, "w": 0.0, "models": {}, "known": False}
            blocks.append(cur)
        cur["w"] += w
        cur["models"][model] = cur["models"].get(model, 0.0) + w
    current = next((b for b in blocks if b["start"] <= now < b["end"]), None)
    return blocks, current


def load_calib(path):
    if path and path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except ValueError:
            pass
    return {"observed": []}


def learn(calib, root, now, days):
    events, limits = scan(root, now - dt.timedelta(days=days) - WINDOW)
    have = {o["reset"] for o in calib["observed"]}
    first_hit = {}
    for hit, kind, reset in limits:
        if kind == "5-hour" and reset and reset.isoformat() not in have:
            first_hit.setdefault(reset, hit)
    for reset, hit in sorted(first_hit.items()):
        start = reset - WINDOW
        w = sum(x for t, x, _ in events if start <= t <= hit)
        if w > 0:
            calib["observed"].append({"reset": reset.isoformat(), "hit": hit.isoformat(),
                                      "weighted": round(w, 3)})
    return calib


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--projects-dir", default=str(Path.home() / ".claude" / "projects"))
    ap.add_argument("--calib", help="calibration JSON (created by --learn)")
    ap.add_argument("--learn", action="store_true")
    ap.add_argument("--learn-days", type=float, default=3)
    ap.add_argument("--save", type=float, default=0.6)
    ap.add_argument("--stop", type=float, default=0.8)
    ap.add_argument("--tz", help="display timezone (defaults to the system timezone)")
    ap.add_argument("--now")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    root = Path(os.path.expanduser(a.projects_dir))
    now = parse_ts(a.now) if a.now else dt.datetime.now(dt.timezone.utc)
    try:
        tz = (dt.timezone.utc if a.tz == "UTC" else ZoneInfo(a.tz)) if a.tz else None
    except ZoneInfoNotFoundError:
        ap.error(f"timezone data unavailable for {a.tz!r}")
    calib_path = Path(a.calib) if a.calib else None
    calib = load_calib(calib_path)
    if a.learn:
        calib = learn(calib, root, now, a.learn_days)
        if calib_path:
            calib_path.parent.mkdir(parents=True, exist_ok=True)
            calib_path.write_text(json.dumps(calib, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

    events, limits = scan(root, now - dt.timedelta(hours=24))
    blocks, cur = windows(events, limits, now)
    used = cur["w"] if cur else 0.0
    obs = [o["weighted"] for o in calib["observed"]]
    limit = statistics.median(obs[-5:]) if obs else None
    active = [(h, r) for h, kind, r in limits if r and r > now]
    if active:
        stage = "上限中"
    elif limit is None:
        stage = "未較正"
    else:
        frac = used / limit
        stage = "停止前" if frac >= a.stop else "節約" if frac >= a.save else "余裕"
    # Report the first limit message of the latest window (later ones are wake-ups that also failed).
    last = next((x for x in limits if x[2] == limits[-1][2]), None) if limits else None

    def hm(t, fmt="%m-%d %H:%M"):
        return t.astimezone(tz).strftime(fmt) if t else "-"

    out = {"stage": stage, "used": round(used, 3), "limit": limit,
           "fraction": round(used / limit, 3) if limit else None,
           "window_start": cur["start"].isoformat() if cur else None,
           "window_end": cur["end"].isoformat() if cur else None,
           "active_limit_reset": active[-1][1].isoformat() if active else None,
           "last_limit": {"hit": last[0].isoformat(), "kind": last[1],
                          "reset": last[2].isoformat() if last[2] else None} if last else None,
           "calibration": calib["observed"][-5:]}
    if a.json:
        print(json.dumps(out, ensure_ascii=False))
        return 0
    print("== 容量（5時間窓の推定。全プロジェクトのClaude Code記録から。他端末・claude.aiの使用は入らないので下限の目安）")
    if cur:
        left = cur["end"] - now
        print(f"窓 {hm(cur['start'])}–{hm(cur['end'], '%H:%M')}（残り {int(left.total_seconds() // 3600)}:{int(left.total_seconds() % 3600 // 60):02d}）"
              f"  推定消費 {used:.1f}" + (f" / 較正上限 {limit:.1f}（{used / limit:.0%}）" if limit else "（較正なし）")
              + f"  段階 {stage}")
        top = sorted(cur["models"].items(), key=lambda x: -x[1])[:3]
        print("   内訳 " + "、".join(f"{m} {w:.1f}" for m, w in top))
    else:
        print(f"窓 なし（次の使用から新しい5時間窓）  段階 {stage}")
    if active:
        print(f"上限中: {hm(active[-1][0])} に到達、解除 {hm(active[-1][1])}")
    elif last:
        print(f"最後の上限: {hm(last[0])}（{last[1]}）→ 解除 {hm(last[2])}")
    if obs:
        print("較正（上限到達時の推定消費）: " + "、".join(
            f"{hm(parse_ts(o['hit']))} {o['weighted']:.1f}" for o in calib["observed"][-5:])
              + f"  → 中央値 {limit:.1f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
