#!/usr/bin/env python3
"""Trial and audit of a course driver set-up (course_driver.py), with a fixed record format.

  python3 driver_trial.py --config <pipeline.json> [--roles writing,review] [--dry-only]
                          [--display-before PCT] [--display-after PCT]
  python3 driver_trial.py --config <pipeline.json> --audit [--since YYYY-MM-DD]

Trial: Step 1 preconditions, Step 2 plumbing (--dry per role), Step 3 one real cycle per role,
Step 4 checks (protected paths, uncommitted state, model mix, claims, usage), Step 5 record.
The trial only runs and records: it never edits the config, manuals, scripts or course text, and it
reports a violation if any of them changed during the trial. Audit reads the driver logs of continuous
running and closes pending checks that the logs already evidence; it starts no cycle.

Course-specific values come from the config's ``trial`` section; see references/driver-trial.md.
"""
from __future__ import annotations

import argparse
import datetime as dt
import glob
import hashlib
import importlib.util
import json
import os
import pathlib
import subprocess
import sys
import time

HERE = pathlib.Path(__file__).resolve().parent

# Checks that a light trial often cannot settle; carried over until evidence closes them.
CHECKS = {
    "heavy_cycle": "a writing cycle that wrote at least one unit (cost above trial.heavy_cycle_units)",
    "upper_not_from_writing": "the writing role never ran the upper tier itself (model mix of writing cycles)",
    "upper_from_review": "the review role ran an upper-tier check (model mix of review cycles)",
    "claim_seen": "a CLAIMED file exists for a verification packet launched by the review role",
}


def load_driver_module():
    spec = importlib.util.spec_from_file_location("course_driver", HERE / "course_driver.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def fingerprint(base: pathlib.Path, rel: str) -> str:
    """Cheap fingerprint of a file or tree: paths, sizes and modification times."""
    p = (base / rel)
    files = [p] if p.is_file() else sorted(x for x in p.rglob("*") if x.is_file()) if p.exists() else []
    parts = [f"{x.relative_to(base)}:{x.stat().st_size}:{x.stat().st_mtime_ns}" for x in files]
    return hashlib.sha1("\n".join(parts).encode()).hexdigest()[:12] if parts else "absent"


class Trial:
    def __init__(self, config: pathlib.Path):
        self.config = config.resolve()
        self.mod = load_driver_module()
        self.cfg = json.loads(self.config.read_text())
        self.trial = self.cfg.get("trial") or {}
        any_role = next(iter(self.cfg["roles"]))
        self.base = self.mod.Driver(self.config, any_role)
        self.course, self.logs = self.base.course, self.base.logs
        self.record_dir = (self.course / self.trial.get("record_dir", self.cfg.get("logs_dir", "logs"))).resolve()
        self.history = self.logs / "trial-history.jsonl"

    # Step 1 -------------------------------------------------------------------
    def preconditions(self) -> list[str]:
        problems = []
        ps = subprocess.run(["ps", "-ax", "-o", "command"], capture_output=True, text=True).stdout
        if any("course_driver.py" in line and str(self.config) in line for line in ps.splitlines()):
            problems.append("another driver with this config is running")
        for stop in self.course.glob("STOP*"):
            problems.append(f"stop file present: {stop.name}")
        return problems

    def protected(self) -> dict[str, str]:
        rels = [self.config.name, *self.trial.get("unchanged", [])]
        for role in self.cfg["roles"]:
            rels += self.trial.get("unchanged_by_role", {}).get(role, [])
        return {r: fingerprint(self.course, r) for r in dict.fromkeys(rels)}

    # Step 2 and 3 -------------------------------------------------------------
    def run_role(self, role: str, dry: bool) -> dict:
        d = self.mod.Driver(self.config, role, dry=dry)
        before = d.cost_history()
        t0 = time.time()
        d.loop(1)
        last = (d.logs / f"{role}-driver.log").read_text().splitlines()[-1]
        after = d.cost_history()
        entry = {}
        costs = d.logs / f"{role}-costs.jsonl"
        if not dry and len(after) > len(before):
            entry = json.loads(costs.read_text().splitlines()[-1])
        return {"role": role, "dry": dry, "seconds": round(time.time() - t0), "log": last,
                "ok": "cycle end exit=0" in last, "cost": entry.get("cost"), "models": entry.get("models", {}),
                "dirty": d.dirty_state()}

    # Step 4 -------------------------------------------------------------------
    def upper_model(self, role: str) -> str | None:
        host = self.cfg["roles"][role]["host"]
        return (self.cfg.get("tiers", {}).get(host) or {}).get("upper")

    def evidence(self, runs: list[dict], since: float) -> dict[str, str]:
        """Pending-check id -> evidence string, for checks the given cycles settle."""
        found: dict[str, str] = {}
        heavy = float(self.trial.get("heavy_cycle_units", 200000))
        for r in runs:
            if r.get("dry") or r.get("cost") is None:
                continue
            up = self.upper_model(r["role"])
            uses_upper = bool(up) and any(up in m for m in r["models"])
            if r["role"] == "writing":
                if r["cost"] >= heavy:
                    found.setdefault("heavy_cycle", f"writing cycle {r.get('time', '')} cost={r['cost']}")
                if uses_upper:
                    found["upper_not_from_writing"] = f"VIOLATION: writing cycle {r.get('time', '')} used {up}"
            if r["role"] == "review" and uses_upper:
                found.setdefault("upper_from_review", f"review cycle {r.get('time', '')} used {up}")
        claims = [c for c in glob.glob(os.path.expanduser(self.trial.get("claim_glob", "")) + "/CLAIMED")
                  if os.path.getmtime(c) >= since] if self.trial.get("claim_glob") else []
        if claims:
            found["claim_seen"] = f"{claims[0]}: {pathlib.Path(claims[0]).read_text().strip()}"
        writing = [r for r in runs if r["role"] == "writing" and not r.get("dry") and r.get("cost") is not None]
        if len(writing) >= int(self.trial.get("writing_cycles_for_upper_check", 10)) and \
                not found.get("upper_not_from_writing", "").startswith("VIOLATION"):
            found["upper_not_from_writing"] = f"{len(writing)} writing cycles without the upper tier"
        return found

    def pending(self) -> list[str]:
        if not self.history.exists():
            return list(CHECKS)
        lines = self.history.read_text().splitlines()
        return json.loads(lines[-1]).get("pending", list(CHECKS)) if lines else list(CHECKS)

    # Step 5 -------------------------------------------------------------------
    def write_record(self, kind: str, runs: list[dict], problems: list[str], changed: list[str],
                     usage: dict, found: dict[str, str]) -> pathlib.Path:
        pending_before = self.pending()
        pending = [c for c in pending_before if c not in found or found[c].startswith("VIOLATION")]
        now = dt.datetime.now()
        self.record_dir.mkdir(parents=True, exist_ok=True)
        path = self.record_dir / f"TRIAL-{now:%Y%m%d-%H%M}.md"
        real = [r for r in runs if not r.get("dry")]
        rows = [("exit / seconds", lambda r: f"{'0' if r['ok'] else 'FAIL'} / {r['seconds']}"),
                ("cost / models", lambda r: f"{r['cost']} / {', '.join(f'{k}:{v}' for k, v in r['models'].items()) or '-'}"),
                ("driver line", lambda r: r["log"].split("] ", 1)[-1][:160]),
                ("uncommitted state", lambda r: ", ".join(r["dirty"]) or "none")]
        out = [f"# driver {kind}（{now:%Y-%m-%d %H:%M}）", "",
               "実行と記録だけ。設定・運転書・スクリプト・本文は変更していない（下の「約束」で機械的に確認）。", ""]
        out += ["## 前提と配管", ""] + [f"- {p}" for p in problems or ["前提：問題なし"]]
        out += [f"- 配管 {r['role']}: {'合格' if r['ok'] else '不合格'}" for r in runs if r.get("dry")] + [""]
        if real:
            out += ["## 本番の周", "", "|項目|" + "|".join(r["role"] for r in real) + "|",
                    "|---|" + "---|" * len(real)]
            out += [f"|{name}|" + "|".join(f(r) for r in real) + "|" for name, f in rows]
            out += ["|やった仕事・判断（記入）|" + "|" * len(real), ""]
        out += ["## 消費の照合", ""]
        out += [f"- {k}: {v}" for k, v in usage.items()]
        out += ["- 較正は時間枠の合計で行う（`course_driver.py usage --reading/--calibrate`）。一周の差では決めない。", ""]
        out += ["## 約束", "", f"- 試験中に変わった保護対象：{', '.join(changed) if changed else 'なし'}", ""]
        out += ["## 未検証の項目（次回へ引継ぎ）", ""]
        out += [f"- [x] {c}: {found[c]}" for c in pending_before if c in found and c not in pending]
        out += [f"- [ ] {c}: {CHECKS[c]}" + (f" — {found[c]}" if c in found else "") for c in pending]
        out += ["", "## 判断（記入）", "", "- 連続運転に進んでよいか：", "- 理由：", "- 不具合と直し方の案：", ""]
        path.write_text("\n".join(out))
        with open(self.history, "a") as f:
            f.write(json.dumps({"time": now.isoformat(timespec="seconds"), "kind": kind, "record": str(path),
                                "runs": [{k: r.get(k) for k in ("role", "dry", "ok", "seconds", "cost", "models")} for r in runs],
                                "usage": usage, "changed": changed, "found": found, "pending": pending},
                               ensure_ascii=False) + "\n")
        return path

    # entry points -------------------------------------------------------------
    def run(self, roles: list[str], dry_only: bool, before: float | None, after: float | None) -> int:
        problems = self.preconditions()                                  # Step 1
        if problems:
            print("\n".join(problems))
            return 4
        start, prot = time.time(), self.protected()
        est_before = self.base.usage_units()
        runs = [self.run_role(r, dry=True) for r in roles]               # Step 2
        if not dry_only and all(r["ok"] for r in runs):
            runs += [self.run_role(r, dry=False) for r in roles]         # Step 3
        changed = [k for k, v in self.protected().items() if prot.get(k) != v]   # Step 4
        est_after = self.base.usage_units()
        budget = (self.cfg.get("usage") or {}).get("budget")
        usage = {}
        if est_before is not None and budget:
            usage["driver window estimate before → after"] = f"{100 * est_before / budget:.1f}% → {100 * est_after / budget:.1f}%"
        if before is not None:
            usage["host display before → after"] = f"{before}% → {after if after is not None else '?'}%"
        for pct in (before, after):
            if pct is not None:
                self.mod.usage_command(self.base, pct, False)
        for r in runs:
            r["time"] = dt.datetime.now().strftime("%H:%M")
        found = self.evidence(runs, start)
        path = self.write_record("trial", runs, [], changed, usage, found)   # Step 5
        print(path)
        return 0 if all(r["ok"] for r in runs) and not changed else 1

    def audit(self, since: str | None) -> int:
        t0 = dt.datetime.fromisoformat(since).timestamp() if since else 0.0
        runs = []
        for role in self.cfg["roles"]:
            f = self.logs / f"{role}-costs.jsonl"
            for line in (f.read_text().splitlines() if f.exists() else []):
                e = json.loads(line)
                if dt.datetime.fromisoformat(e["time"]).timestamp() >= t0:
                    runs.append({"role": role, "dry": False, "ok": True, "seconds": None, "cost": e["cost"],
                                 "models": e.get("models", {}), "time": e["time"], "log": "", "dirty": []})
        found = self.evidence(runs, t0)
        usage = {f"{role} cycles / mean cost": (lambda c: f"{len(c)} / {sum(c) / len(c):.0f}" if c else "0")(
            [r["cost"] for r in runs if r["role"] == role]) for role in self.cfg["roles"]}
        path = self.write_record("audit", [], [], [], usage, found)
        print(path)
        return 0


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--config", required=True, type=pathlib.Path)
    ap.add_argument("--roles", help="comma-separated roles (default: all roles in the config)")
    ap.add_argument("--dry-only", action="store_true")
    ap.add_argument("--display-before", type=float)
    ap.add_argument("--display-after", type=float)
    ap.add_argument("--audit", action="store_true")
    ap.add_argument("--since")
    a = ap.parse_args(argv)
    t = Trial(a.config)
    if a.audit:
        return t.audit(a.since)
    roles = a.roles.split(",") if a.roles else list(t.cfg["roles"])
    return t.run(roles, a.dry_only, a.display_before, a.display_after)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
