#!/usr/bin/env python3
"""Short status display for the parent threads of an unattended long run (read-only).

    round_status.py --config round-status.json <role>

The parent of each role (producer or reviewer) decides its next action from this output alone.
Every fact the parent needs is one line, and the FINGERPRINT changes exactly when something the
parent could act on changed (see ../references/status-contract.md). Paths in the config are
relative to the config file unless absolute.

Config keys (all optional except ``volumes``):
  title            name shown in the header
  roles            {"producer": "writing", "reviewer": "review"}: role names on the command line
  root             course root; sources, volume dirs and logs are relative to it (default: config dir)
  reviews_dir      directory of review cases
  case_prefix      case directory names start with this; ``short_prefixes`` are stripped for display
  since            YYYY-MM-DD: cases whose name ends with a date from this day on are watched
  queue            JSON with ``entries`` [{id, volume, author_state}], and ``queue_keys`` to print
  role_models      JSON with ``roles`` {name: {agent_type, model, effort}} for the workers
  volumes          [{"name": "v1", "dir": "volumes/v1", "pdf": "output/v1.pdf"}]
  audit_name       scope-audit file in each volume dir (default scope-audit.md)
  sources          globs of canonical sources under root (default chapters/**/*.tex)
  log_dir          one log per role: <log_dir>/<role>.md
  handoff_dir      one handoff per role: <handoff_dir>/<role>.md
  lock             exclusive lock file for the expensive model
  capacity_calib   calibration file for usage_window.py (``capacity_projects_dir`` for tests)
  coverage_cmd     command printing review_coverage.py JSON; ``summary --json`` / ``next -n 5 --json`` are appended
  stray_dirs       directories where cases must not be created
  triage_marker    log text marking the cleanup of "changed after review" for a volume ({cursor} is filled)
"""
from __future__ import annotations

import argparse
import collections
import datetime as dt
import hashlib
import json
import pathlib
import re
import subprocess
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

HERE = pathlib.Path(__file__).resolve().parent
USAGE_WINDOW = HERE.parents[1] / "reading-book" / "scripts" / "usage_window.py"
AUDIT_STATES = ("TODO", "MISSING", "PARTIAL", "OK", "OUT")
CASE_DATE = re.compile(r"-(\d{4}-\d{2}-\d{2})$")
DONE = ("closed", "superseded", "rechecked")
CAPACITY_RULES = {
    "余裕": "通常どおり",
    "未較正": "通常どおり（数を見ておく）",
    "節約": "詰まりを解く仕事だけ（受領・修復・今の冊のレビュー）。次の冊の照合・重いモデルは保留",
    "停止前": "新しいworkerを出さない。記録して待機（残りはユーザーと指示役の分）",
    "上限中": "何も出さない。定期再開は消さない。解除後の最初の回から再開",
}


def mtime(p: pathlib.Path) -> str:
    return dt.datetime.fromtimestamp(p.stat().st_mtime).strftime("%m-%d %H:%M") if p.exists() else "なし"


def pages(p: pathlib.Path) -> str:
    try:
        return subprocess.run(["qpdf", "--show-npages", str(p)], capture_output=True, text=True, timeout=30).stdout.strip() or "?"
    except Exception:
        return "?"


def tail(p: pathlib.Path, n: int) -> list[str]:
    if not p.exists():
        return ["(なし)"]
    lines = [l.rstrip() for l in p.read_text(encoding="utf-8", errors="replace").splitlines() if l.strip()]
    return [l[:220] for l in lines[-n:]]


class Config:
    def __init__(self, path: pathlib.Path):
        self.path = path.resolve()
        self.c = json.loads(path.read_text(encoding="utf-8"))
        base = self.path.parent
        self.root = self.p(self.c.get("root", "."), base)
        roles = self.c.get("roles", {"producer": "writing", "reviewer": "review"})
        self.producer, self.reviewer = roles["producer"], roles["reviewer"]

    def p(self, s: str, base: pathlib.Path | None = None) -> pathlib.Path:
        q = pathlib.Path(s).expanduser()
        return q if q.is_absolute() else ((base or self.path.parent) / q).resolve()

    def opt(self, key: str, base_root=True) -> pathlib.Path | None:
        v = self.c.get(key)
        return self.p(v, self.root if base_root else None) if v else None

    def get(self, key, default=None):
        return self.c.get(key, default)


def short(cfg: Config, name: str) -> str:
    for pre in cfg.get("short_prefixes", [cfg.get("case_prefix", "")]):
        if pre:
            name = name.removeprefix(pre)
    return CASE_DATE.sub("", name)


def recent_cases(cfg: Config, q: dict) -> dict[str, list[str]]:
    """Watched cases by state: directory contents plus the author's queue state."""
    entries = q.get("entries", [])
    done = {e["id"] for e in entries if e.get("author_state") in DONE}
    repaired = {e["id"] for e in entries if e.get("author_state") == "repaired"}
    reg = {e["id"] for e in entries}
    out: dict[str, list[str]] = {"returned": [], "repaired": [], "claimed": [], "open": [], "unregistered": []}
    reviews = cfg.opt("reviews_dir")
    since = cfg.get("since", "0000-00-00")
    if not reviews or not reviews.exists():
        return out
    for d in sorted(reviews.glob(cfg.get("case_prefix", "") + "*")):
        m = CASE_DATE.search(d.name)
        if not d.is_dir() or not m or m.group(1) < since or d.name in done:
            continue
        if d.name not in reg:
            out["unregistered"].append(d.name)
        if (d / "results" / "READY").exists():
            out["repaired" if d.name in repaired else "returned"].append(d.name)
        elif (d / "CLAIMED").exists():
            out["claimed"].append(d.name)
        else:
            out["open"].append(d.name)
    return out


def scope_audits(cfg: Config) -> list[tuple[str, str, dict]]:
    out = []
    for v in cfg.get("volumes", []):
        p = cfg.root / v["dir"] / cfg.get("audit_name", "scope-audit.md")
        if not p.exists():
            out.append((v["name"], "未作成", {}))
            continue
        t = p.read_text(encoding="utf-8", errors="replace")
        c = {k: len(re.findall(rf"\|\s*{k}\s*\|", t)) for k in AUDIT_STATES}
        m = re.search(r"^CLOSED:\s*(.+)$", t, re.M)
        out.append((v["name"], f"閉鎖 {m.group(1).strip()[:40]}" if m else "照合・補完中", c))
    return out


def wait_hours(log: pathlib.Path, now: dt.datetime) -> int:
    """Hours since the last WAIT line; in the fingerprint, so a waiting parent wakes once an hour."""
    if not log.exists():
        return 0
    for l in reversed(log.read_text(encoding="utf-8", errors="replace").splitlines()):
        m = re.match(r"\s*(\d\d-\d\d \d\d:\d\d) .*\bWAIT FP=", l)
        if m:
            t = dt.datetime.strptime(f"{now.year}-{m.group(1)}", "%Y-%m-%d %H:%M")
            return max(0, int((now - t).total_seconds() // 3600))
    return 0


def capacity(cfg: Config) -> dict:
    """Stage of the 5-hour window (reading-book usage_window.py); never stops the display."""
    cmd = [sys.executable, "-X", "utf8", str(USAGE_WINDOW), "--learn", "--json"]
    calib = cfg.opt("capacity_calib")
    if calib:
        cmd += ["--calib", str(calib)]
    if cfg.get("capacity_projects_dir"):
        cmd += ["--projects-dir", str(cfg.opt("capacity_projects_dir"))]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", timeout=120)
        return json.loads(r.stdout)
    except Exception as e:
        return {"stage": "未較正", "error": str(e)}


def hm(iso: str | None) -> str:
    return dt.datetime.fromisoformat(iso).astimezone().strftime("%m-%d %H:%M") if iso else "-"


def coverage(cfg: Config, *args: str) -> str:
    cmd = cfg.get("coverage_cmd")
    if not cmd:
        return ""
    cmd = [item for c in cmd for item in ([sys.executable, "-X", "utf8"] if c == "{python}" else [c])]
    return subprocess.run([*cmd, *args], capture_output=True, text=True, encoding="utf-8", timeout=120, cwd=cfg.root).stdout


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--config", required=True, type=pathlib.Path)
    ap.add_argument("role")
    a = ap.parse_args(argv)
    cfg = Config(a.config)
    role = a.role
    if role not in (cfg.producer, cfg.reviewer):
        ap.error(f"role は {cfg.producer} か {cfg.reviewer}")
    other = cfg.reviewer if role == cfg.producer else cfg.producer
    now = dt.datetime.now()
    print(f"== {cfg.get('title', '')} {role} 親 状況  {now.strftime('%Y-%m-%d %H:%M')}")

    cap = capacity(cfg)
    st = cap.get("stage", "未較正")
    frac = f"{cap['fraction']:.0%}" if cap.get("fraction") is not None else "較正なし"
    print(f"-- 容量の段階: {st}  （5時間窓の推定 {frac}、窓の終わり {hm(cap.get('window_end'))}）→ {CAPACITY_RULES.get(st, '')}")
    if cap.get("active_limit_reset"):
        print(f"   上限に到達中。解除 {hm(cap['active_limit_reset'])}")
    elif cap.get("last_limit"):
        print(f"   最後の上限: {hm(cap['last_limit']['hit'])} → 解除 {hm(cap['last_limit']['reset'])}")
    if cap.get("error"):
        print(f"   容量の推定に失敗: {cap['error'][:120]}")

    models = cfg.opt("role_models")
    if models and models.exists():
        print("-- worker役割（Agentに必ず明示で渡す。親のモデルを継承させない）")
        for k, v in json.loads(models.read_text(encoding="utf-8"))["roles"].items():
            print(f"   {k:26s} type={v['agent_type']:18s} model={v['model']:7s} effort={v['effort']}")

    qpath = cfg.opt("queue")
    q = json.loads(qpath.read_text(encoding="utf-8")) if qpath and qpath.exists() else {"entries": []}
    keys = cfg.get("queue_keys", [])
    print("-- queue: " + " ".join(f"{k}={q.get(k)}" for k in keys))
    ret = collections.defaultdict(list)
    for e in q.get("entries", []):
        if e.get("author_state") in ("received", "repaired", "rechecked"):
            ret[e.get("volume")].append(e.get("author_state"))
    print("   作者側未閉鎖(received/repaired/rechecked): " + ", ".join(f"{v}:{len(s)}" for v, s in sorted(ret.items(), key=lambda x: str(x[0]))))

    rc = recent_cases(cfg, q)

    def show(key: str, label: str, note: str) -> None:
        xs = rc[key]
        print(f"   {label} {len(xs)}件{note}" + (": " + ", ".join(short(cfg, x) for x in xs[:10])
                                                + (f" ほか{len(xs) - 10}件" if len(xs) > 10 else "") if xs else ""))
    print(f"-- {cfg.get('since', '')}以降のcase（実物。queueで closed/superseded/rechecked のものは除く）")
    show("returned", "返却済み(READY)・作者未閉鎖", "  ← 本文側の仕事（受領・修復・queue登録）。1件以上あれば本文側はWAITにしない")
    show("repaired", "修復済み・再確認待ち", "  ← 本文側は待つだけ（重大・中を直した結果。レビュー側が被覆表の「確認後に変更」から再確認する）")
    show("claimed", "claim中・未返却", "")
    show("open", "公開・未claim", "  ← レビュー側の仕事（古い版なら本文側がqueueでsupersededにする）")
    show("unregistered", "うちqueue未登録", "  ← 本文側がqueueに登録する")

    audits = scope_audits(cfg)
    print("-- 採用範囲の完了照合（TODO=未照合 MISSING=無い PARTIAL=不足 OK=本文あり OUT=計画で採用外）")
    for vol, state, c in audits:
        print(f"   {vol} {state}" + ("  " + " ".join(f"{k}{c[k]}" for k in AUDIT_STATES) if c else ""))

    pdfs = [(v["name"], cfg.p(v["pdf"], cfg.root)) for v in cfg.get("volumes", []) if v.get("pdf")]
    if pdfs:
        print("-- 公式出力（mtime / 頁 / sha先頭）")
        for name, p in pdfs:
            if p.exists():
                print(f"   {name} {mtime(p)} {pages(p):>4s}p {hashlib.sha256(p.read_bytes()).hexdigest()[:12]}")
    srcs = [p for g in cfg.get("sources", ["chapters/**/*.tex"]) for p in cfg.root.glob(g) if p.is_file()]
    last = max(srcs, key=lambda p: p.stat().st_mtime) if srcs else None
    print(f"-- 正本の最終書込: " + (f"{mtime(last)} {last.relative_to(cfg.root)}" if last else "なし"))
    lock = cfg.opt("lock")
    if lock:
        print(f"-- {lock.name}: {lock.read_text(encoding='utf-8').strip() if lock.exists() else 'なし（重いモデル使用可）'}  (mtime {mtime(lock)})")

    cov_fp = ""
    cursor = next((v for v, state, _ in audits if not state.startswith("閉鎖")), None)
    log_dir = cfg.opt("log_dir") or cfg.root
    if cfg.get("coverage_cmd") and cursor:
        try:
            rows = json.loads(coverage(cfg, "summary", "--json"))["rows"]
            res = [r for r in rows if r["group"] == cursor and r["kind"] == "result" and r["has_proof"]]
            cc = {k: sum(r["state"] == k for r in res) for k in ("unreviewed", "changed", "in-review")}
            acc = sum(r["state"] == "current" and r.get("accepted_repair") for r in res)
            marker = cfg.get("triage_marker", "確認後に変更の整理 {cursor}").format(cursor=cursor)
            plog = log_dir / f"{cfg.producer}.md"
            tri = [l[:11] for l in (plog.read_text(encoding="utf-8", errors="replace").splitlines() if plog.exists() else [])
                   if marker in l or marker.replace(cursor, cursor.upper()) in l]
            print(f"-- 今の冊 {cursor} の被覆: 未確認 {cc['unreviewed']}  確認後に変更 {cc['changed']}  確認中 {cc['in-review']}"
                  f"  （軽微修復の記録で確認済み {acc}）")
            print("   確認後に変更の整理（本文側）: " + (f"済 {tri[-1]}" if tri else "未")
                  + ("  ← 確認後に変更が1件以上で「未」なら、本文側はWAITにせず整理する" if cc["changed"] and not tri else ""))
            cov_fp += f"cursor={cursor}:{cc}:{acc}:{bool(tri)}"
        except Exception as e:  # display aid only
            print(f"-- 今の冊の被覆の表示に失敗: {e}")
    since = cfg.get("since", "0000-00-00")
    stray = []
    for d in cfg.get("stray_dirs", []):
        sd = cfg.p(d, cfg.root)
        if sd.exists():
            for p in sd.glob(cfg.get("case_prefix", "") + "*"):
                m = CASE_DATE.search(p.name)
                day = m.group(1) if m else dt.datetime.fromtimestamp(p.stat().st_mtime).strftime("%Y-%m-%d")
                if p.is_dir() and day >= since:
                    stray.append(p.name)
    if stray:
        print(f"!! 置き場所違いのcase {len(stray)}件（被覆表に数えられない）← 作った役が {cfg.opt('reviews_dir')}/ へ mv -n で移す: "
              + ", ".join(stray[:5]))
        cov_fp += "stray=" + ",".join(sorted(stray))
    if role == cfg.reviewer and cfg.get("coverage_cmd"):
        try:
            summ = coverage(cfg)
            cand = json.loads(coverage(cfg, "next", "-n", "5", "--json") or "[]")
            print("-- 独立数学レビューの被覆（冊ごと。詳細は選定workerが被覆の道具で見る）")
            for l in summ.splitlines()[2:]:
                print("   " + l.split("  ／")[0])
            print(f"   次の候補 {len(cand)}件（うち安定 {sum(c['stable'] for c in cand)}件）")
            cov_fp += json.dumps([[c["file"], c["start"], c["stable"]] for c in cand])
        except Exception as e:
            print(f"-- 被覆表示に失敗: {e}")

    hand = cfg.opt("handoff_dir") or cfg.root
    other_p = hand / f"{other}.md"
    fp_src = "|".join([
        hashlib.sha256(qpath.read_bytes()).hexdigest() if qpath and qpath.exists() else "",
        str(other_p.stat().st_mtime if other_p.exists() else 0),
        str(last.stat().st_mtime if last else 0),
        *[str(p.stat().st_mtime) for _, p in pdfs if p.exists()],
        cov_fp,
        json.dumps(rc),
        json.dumps(audits),
        f"capacity={st}",
        f"wait-hours={wait_hours(log_dir / f'{role}.md', now)}",
    ])
    print(f"FINGERPRINT: {hashlib.sha256(fp_src.encode()).hexdigest()[:10]}  （WAITの行に記録し、再開時に同じならworkerを出さない。WAITから1時間ごとに必ず変わる）")
    print(f"-- {role} の記録の末尾")
    for l in tail(log_dir / f"{role}.md", 6):
        print("   " + l)
    print(f"-- 相手役 {other} の引継ぎの末尾（新着確認用）  mtime {mtime(other_p)}")
    for l in tail(other_p, 3):
        print("   " + l)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
