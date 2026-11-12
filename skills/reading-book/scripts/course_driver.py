#!/usr/bin/env python3
"""Host-neutral driver for long course production: one fresh, conversation-free run per cycle.

  python3 course_driver.py --config <pipeline.json> <role> [--once] [--dry] [--max-cycles N]

Each cycle starts a new headless agent process (command taken from the config, never from this script),
asks it to perform one cycle of the role's manual, and reads the last ``NEXT_SLEEP=<s>`` and
``STATUS=<line>`` lines of its output. Between cycles the driver

- stops when ``STOP_<role>`` or ``STOP`` exists in the course directory;
- waits when the host reports a usage limit (patterns from the config);
- estimates usage of the current window from the host's session logs (when a reader exists for that
  host) and waits above ``usage.pause_at_fraction``;
- paces cycles so that the role's share of the window budget is not exceeded (``pacing``).

Model names and reasoning settings live only in the config: roles name a capability tier
(``upper``/``normal``/``light``) and an effort (``high``/``medium``/``low``); ``tiers.<host>`` maps tiers
to that host's models. The prompt passes the tier mapping on, so manuals can stay host-neutral.
"""
from __future__ import annotations

import argparse
import datetime as dt
import glob
import json
import os
import pathlib
import re
import subprocess
import sys
import time

DEFAULT_PROMPT = """{manual} の一周の手順を、ヘッドレス実行の規則で一周分だけ実行してください。
作業フォルダ: {course}
- これは一回きりの実行で、次の周は driver が新しい文脈で起動する。自己予約・ループ・常駐監視は使わない。
- 状況は `{status_cmd}` だけで見る。大きなファイルを丸ごと読まない。
- worker（subagent）は前景で起動し、返却を受け取ってから終える。一周で出す仕事は {units} まで。
- worker を起動するときは能力の段階を明示する。このホストでの対応：{tier_map}。
  上位の段階は運転書がそう定める仕事（新しい証明とその独立確認）だけに使う。独立確認は受付の印を置いてから。
- 終わる前に運転書どおり状態ファイルを更新する。
- 最後の 2 行に必ず次を書く：
NEXT_SLEEP=<次の周まで待つ秒数。すぐ次へ進めるなら 30、ビルド待ちなら 300、相手の返却待ちだけなら 900>
STATUS=<この周でしたことと次の一手を一行で>
"""
DRY_PROMPT = "Do nothing else. Print exactly two lines:\nNEXT_SLEEP=5\nSTATUS=dry run ok"
DEFAULT_LIMIT_PATTERNS = [r"hit your .*limit", r"usage limit", r"rate limit"]


class Driver:
    def __init__(self, config_path: pathlib.Path, role: str, dry: bool = False):
        self.cfg = json.loads(config_path.read_text())
        self.base = config_path.resolve().parent
        self.course = (self.base / self.cfg.get("course_dir", ".")).resolve()
        self.role = role
        self.r = self.cfg["roles"][role]
        self.host_name = self.r["host"]
        self.host = self.cfg["hosts"][self.host_name]
        tiers = self.cfg.get("tiers", {}).get(self.host_name, {})
        self.model = self.r.get("model") or tiers.get(self.r.get("tier", "normal"), "")
        self.tier_map = ", ".join(f"{k}={v}" for k, v in tiers.items()) or "(ホストの既定)"
        self.dry = dry
        self.logs = self.course / self.cfg.get("logs_dir", "logs")
        self.logs.mkdir(parents=True, exist_ok=True)
        self.scale = float(self.cfg.get("time_scale", 1))

    # -- usage -----------------------------------------------------------------
    def usage_units(self) -> float | None:
        """Weighted usage within the window, from the host's session logs; None if unreadable."""
        u = self.cfg.get("usage") or {}
        reader = self.host.get("usage") or {}
        if reader.get("format") != "jsonl-usage" or not reader.get("dir"):
            return None
        since = time.time() - float(u.get("window_hours", 5)) * 3600
        weights = u.get("weights", {"input_tokens": 1, "output_tokens": 1})
        model_w = u.get("model_weights", {})
        total = 0.0
        pattern = os.path.join(os.path.expanduser(reader["dir"]), "**", "*.jsonl")
        for f in glob.glob(pattern, recursive=True):
            if os.path.getmtime(f) < since:
                continue
            seen: set[str] = set()
            for line in open(f, errors="ignore"):
                if '"usage"' not in line:
                    continue
                try:
                    rec = json.loads(line)
                except ValueError:
                    continue
                ts = rec.get("timestamp")
                msg = rec.get("message") if isinstance(rec.get("message"), dict) else {}
                us = msg.get("usage")
                if not ts or not isinstance(us, dict):
                    continue
                if dt.datetime.fromisoformat(ts.replace("Z", "+00:00")).timestamp() < since:
                    continue
                mid = msg.get("id")
                if mid:
                    if mid in seen:
                        continue
                    seen.add(mid)
                model = msg.get("model") or ""
                mw = next((w for k, w in model_w.items() if k in model), 1.0)
                total += mw * sum(float(us.get(k) or 0) * w for k, w in weights.items())
        return total

    def usage_fraction(self) -> float | None:
        units = self.usage_units()
        budget = (self.cfg.get("usage") or {}).get("budget")
        return None if units is None or not budget else units / float(budget)

    def pacing_interval(self, cycle_units: float | None) -> float:
        """Minimum seconds between cycle starts so this role stays within its share of the window."""
        p = self.cfg.get("pacing") or {}
        u = self.cfg.get("usage") or {}
        window = float(u.get("window_hours", 5)) * 3600
        share = float(self.r.get("budget_share", p.get("default_share", 1.0)))
        if cycle_units is not None and u.get("budget"):
            allowed = float(u["budget"]) * float(u.get("pause_at_fraction", 0.8)) * share
            return window * cycle_units / allowed if allowed > 0 else 0.0
        cycles = p.get("cycles_per_window")
        return window / (float(cycles) * share) if cycles else 0.0

    # -- running ---------------------------------------------------------------
    def prompt(self) -> str:
        if self.dry:
            return DRY_PROMPT
        tpl = self.cfg.get("prompt_template") or DEFAULT_PROMPT
        if tpl.endswith((".md", ".txt")) and (self.base / tpl).exists():
            tpl = (self.base / tpl).read_text()
        return tpl.format(manual=self.r["manual"], course=self.course, status_cmd=self.r.get("status_cmd", "(なし)"),
                          units=self.r.get("units", "1 単位"), tier_map=self.tier_map)

    def run_cycle(self) -> tuple[int, str]:
        fields = {"prompt": self.prompt(), "model": self.model, "effort": self.r.get("effort", "medium"),
                  "workspace": self.cfg.get("workspace", str(self.course))}
        cmd = [c.format(**fields) for c in self.host["cmd"]]
        log = self.logs / f"{self.role}-{dt.datetime.now():%Y%m%d-%H%M%S}.log"
        try:
            p = subprocess.run(cmd, cwd=fields["workspace"], capture_output=True, text=True,
                               stdin=subprocess.DEVNULL, timeout=self.cfg.get("cycle_timeout_sec", 5400))
            out, code = p.stdout + "\n" + p.stderr, p.returncode
        except subprocess.TimeoutExpired as e:
            out, code = f"TIMEOUT\n{e.stdout or ''}", 124
        log.write_text(out)
        return code, out

    def note(self, msg: str) -> None:
        line = f"{dt.datetime.now():%Y-%m-%d %H:%M} [{self.role}] {msg}"
        print(line, flush=True)
        with open(self.logs / f"{self.role}-driver.log", "a") as f:
            f.write(line + "\n")

    def sleep(self, seconds: float) -> None:
        if self.scale > 0:
            time.sleep(seconds * self.scale)

    def stopped(self) -> bool:
        return (self.course / f"STOP_{self.role}").exists() or (self.course / "STOP").exists()

    def loop(self, max_cycles: int | None) -> int:
        cycles = 0
        limit_wait = float(self.cfg.get("limit_wait_sec", 1800))
        pause = float((self.cfg.get("usage") or {}).get("pause_at_fraction", 0.8))
        patterns = self.host.get("limit_patterns", DEFAULT_LIMIT_PATTERNS)
        while max_cycles is None or cycles < max_cycles:
            if self.stopped():
                self.note("STOP file found; exiting")
                return 0
            before = self.usage_units()
            frac = self.usage_fraction()
            if frac is not None and frac >= pause:
                self.note(f"usage {frac:.0%} of window budget; waiting {limit_wait:.0f}s")
                self.sleep(limit_wait)
                cycles += 1 if self.scale == 0 else 0  # tests: avoid spinning forever
                continue
            started = time.time()
            self.note(f"cycle start (host={self.host_name}, tier={self.r.get('tier')}, effort={self.r.get('effort')}, "
                      f"usage={'?' if frac is None else f'{frac:.0%}'})")
            code, out = self.run_cycle()
            cycles += 1
            if any(re.search(p, out, re.I) for p in patterns):
                self.note("host reports a usage limit; waiting")
                self.sleep(limit_wait)
                continue
            after = self.usage_units()
            cost = None if before is None or after is None else max(after - before, 0.0)
            ns = re.findall(r"NEXT_SLEEP=(\d+)", out)
            st = re.findall(r"STATUS=(.*)", out)
            want = int(ns[-1]) if ns else int(self.cfg.get("default_sleep_sec", 60))
            if code != 0 and not ns:
                want = max(want, 300)
            pace = self.pacing_interval(cost) - (time.time() - started)
            wait = min(max(want, pace, 10), 3600)
            cost_txt = "?" if cost is None else f"{cost:.0f}"
            self.note(f"cycle end exit={code} cost={cost_txt} sleep={wait:.0f}s (asked {want}, pace {max(pace, 0):.0f}) "
                      f"status={st[-1].strip() if st else '(no STATUS line)'}")
            if max_cycles is not None and cycles >= max_cycles:
                break
            self.sleep(wait)
        return 0


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--config", required=True, type=pathlib.Path)
    ap.add_argument("role")
    ap.add_argument("--once", action="store_true")
    ap.add_argument("--dry", action="store_true", help="check the plumbing with a trivial prompt")
    ap.add_argument("--max-cycles", type=int)
    a = ap.parse_args(argv)
    d = Driver(a.config, a.role, dry=a.dry)
    return d.loop(1 if (a.once or a.dry) else a.max_cycles)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
