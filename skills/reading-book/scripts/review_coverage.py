#!/usr/bin/env python3
"""Show which labelled results of a long course have an independent math review, recomputed from records.

This is a view, not a ledger: every run reads the current canonical TeX and the review cases, so it
cannot drift from them. See ../references/token-budget.md (rule 7). Only ``record-repair`` writes,
and only one file into one case.

  review_coverage.py --root COURSE --files 'chapters/*.tex' [...] --reviews REVIEW_DIR \
      [--case-glob 'slug-*'] [--groups groups.json] [--exclude names.txt] [--stable-minutes 30] \
      [--max-lines 600] [summary | next [-n 3] | list [--group G] [--state S]] [--json]
  review_coverage.py record-repair --case NAME --severity minor [--note TEXT] --root COURSE --reviews REVIEW_DIR

Blocks (statement + following proof) are cut by tex_blocks.py, the same rule make_packet.py uses.
A result counts as reviewed by a case when the case is a math review with a ``READY`` (in
``results/``, the case root, or a math sub-review of older layouts) and

- its manifest lists the label in ``target_labels`` (packets from make_packet.py), or
- it has ``unit.tex`` (older make_packet packets) and the complete block is in it, or
- otherwise (other packet layouts) the block appears in the case's frozen TeX *with its proof*;
  premises are passed as statements without proofs, so they do not count.

States: ``current`` (reviewed block hash equals the canonical one), ``in-review`` (case with
``CLAIMED`` but no READY), ``changed`` (reviewed, but the canonical block changed since),
``unreviewed``. Unclaimed packets without READY are ignored (published or abandoned, not reviewed).
Results without a proof in the canonical text are reported separately and are not proposed by
``next``. Definitions are counted only from exact targets (manifest or unit.tex).

Minor repairs do not need a recheck. After repairing a returned case whose findings were all minor
(no major or medium finding), the author runs ``record-repair``: it writes ``AUTHOR_REPAIR.json`` into
the case with the current hashes of the case's target results, and those hashes then count as
``current`` (reported as accepted minor repairs). A later change of the block makes it ``changed``
again. Repairs of major or medium findings are not recorded this way; they get a recheck.

``--groups`` JSON: {"groups": [{"name": "f06", "spans": [{"file": "chapters/x.tex", "start": 1,
"end": 400, "priority": false}], "stable_with": ["volumes/x/preliminaries.tex"]}]}. With groups,
blocks outside every span are ignored. ``priority`` spans (e.g. new proofs) are proposed first.
A chunk is stable when its file and every ``stable_with`` file were last written at least
``--stable-minutes`` ago. ``next`` proposes contiguous results of one state (``unreviewed``, then
``changed``: a recheck of the changed results only) within one section, ordered by priority,
stability, state and size (``--group-order``: earlier groups first); its line range can be passed to make_packet.py.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import tex_blocks  # noqa: E402

RANK = {"current": 3, "in-review": 2, "changed": 1, "unreviewed": 0}


def case_kind(name: str, man: dict) -> str:
    k = str(man.get("kind") or man.get("review_type") or "").lower()
    probe = k or name.lower()
    if "math" in probe or "verify" in probe:
        return "math"
    if any(w in probe for w in ("output", "source", "correspondence", "navigation", "index", "scope")):
        return "other"
    return "math"


def is_ready(case: pathlib.Path) -> bool:
    """READY in the case, results/ or a math sub-review (older layouts), not in an output/source sub-review."""
    for p in case.glob("**/READY"):
        rel = p.relative_to(case).parts[:-1]
        if len(rel) <= 2 and not any(w in part for part in rel for w in ("output", "source")):
            return True
    return False


def guess_file(path: pathlib.Path, canon: set[str]) -> str | None:
    """Canonical file a copied TeX file stands for: path suffix, else a unique base name."""
    s = path.as_posix()
    hits = [c for c in canon if s.endswith("/" + c)] or [c for c in canon if pathlib.PurePath(c).name == path.name]
    return hits[0] if len(hits) == 1 else None


def read_cases(reviews: pathlib.Path, pattern: str, exclude: set[str], canon: set[str]) -> tuple[dict, dict]:
    """label -> list of {case, hash, ready, exact}; and counts for the report."""
    seen: dict[str, list[dict]] = {}
    stats = {"cases": 0, "math": 0, "excluded": 0, "ready": 0, "exact": 0, "unit": 0, "heuristic": 0, "repairs": 0}
    for case in sorted(p for p in reviews.glob(pattern) if p.is_dir()):
        stats["cases"] += 1
        if case.name in exclude:
            stats["excluded"] += 1
            continue
        try:
            man = json.loads((case / "manifest.json").read_text(encoding="utf-8"))
            man = man if isinstance(man, dict) else {}
        except (OSError, ValueError):
            man = {}
        if case_kind(case.name, man) != "math":
            continue
        stats["math"] += 1
        ready = is_ready(case)
        claimed = (case / "CLAIMED").exists()
        stats["ready"] += ready
        if not ready and not claimed:
            continue  # published but unclaimed, or abandoned: nobody is reviewing it
        found: dict[str, tuple[str, bool, str | None]] = {}
        mfile = man.get("file") if isinstance(man.get("file"), str) else None
        targets = man.get("target_labels")
        if isinstance(targets, dict) and targets:
            stats["exact"] += 1
            found = {lab: (h, True, mfile) for lab, h in targets.items()}
        elif (case / "unit.tex").exists():
            stats["unit"] += 1
            for b in tex_blocks.blocks(tex_blocks.strip_line_numbers(
                    (case / "unit.tex").read_text(encoding="utf-8", errors="ignore"))):
                if b["label"] and b["complete"]:
                    found.setdefault(b["label"], (b["hash"], True, mfile))
        else:
            stats["heuristic"] += 1
            for p in sorted(case.rglob("*.tex")):
                if "results" in p.relative_to(case).parts:
                    continue
                for b in tex_blocks.blocks(tex_blocks.strip_line_numbers(p.read_text(encoding="utf-8", errors="ignore"))):
                    if b["label"] and b["complete"] and b["has_proof"]:
                        found.setdefault(b["label"], (b["hash"], False, guess_file(p, canon)))
        for lab, (h, exact, f) in found.items():
            seen.setdefault(lab, []).append({"case": case.name, "hash": h, "ready": ready, "exact": exact, "file": f})
        rec = read_repair(case) if ready else None
        if rec:
            stats["repairs"] += 1
            for lab, h in rec["labels"].items():
                seen.setdefault(lab, []).append({"case": case.name, "hash": h, "ready": True, "exact": True,
                                                 "file": rec.get("file") or mfile, "repair": True})
    return seen, stats


REPAIR = "AUTHOR_REPAIR.json"


def read_repair(case: pathlib.Path) -> dict | None:
    """The author's record of a minor-only repair, if well formed."""
    try:
        rec = json.loads((case / REPAIR).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    if not isinstance(rec, dict) or rec.get("severity") != "minor" or not isinstance(rec.get("labels"), dict):
        return None
    return rec


def load_groups(root: pathlib.Path, path: pathlib.Path | None, files: list[pathlib.Path]) -> list[dict]:
    if path is None:
        return [{"name": str(f.relative_to(root)), "spans": [{"file": str(f.relative_to(root)), "start": 1,
                 "end": 10 ** 9, "priority": False}], "stable_with": []} for f in files]
    return json.loads(path.read_text(encoding="utf-8"))["groups"]


def same_file(a: str, b: str) -> bool:
    a, b = a.lstrip("./"), b.lstrip("./")
    return a == b or a.endswith("/" + b) or b.endswith("/" + a)


def state_of(block: dict, reviews: list[dict]) -> tuple[str, list[str], bool]:
    """State, the cases giving it, and whether ``current`` rests only on recorded minor repairs."""
    by_state: dict[str, set[str]] = {}
    repaired_only = True
    for r in reviews:
        if not r["exact"] and not block["has_proof"]:
            continue
        if r["file"] and not same_file(r["file"], block["file"]):
            continue  # the same label restated in another file (e.g. a volume's preliminaries)
        if r["ready"]:
            st = "current" if r["hash"] == block["hash"] else "changed"
        else:
            st = "in-review"
        if st == "current" and not r.get("repair"):
            repaired_only = False
        by_state.setdefault(st, set()).add(r["case"])
    if not by_state:
        return "unreviewed", [], False
    best = max(by_state, key=RANK.__getitem__)
    return best, sorted(by_state[best]), best == "current" and repaired_only


def collect(a) -> tuple[list[dict], dict, list[dict]]:
    root = a.root
    files = sorted({p for g in a.files for p in root.glob(g) if p.is_file()})
    groups = load_groups(root, a.groups, files)
    canon = {sp["file"] for g in groups for sp in g["spans"]} | {str(f.relative_to(root)) for f in files}
    seen, stats = read_cases(a.reviews, a.case_glob, set(a.exclude_names), canon)
    now = time.time()
    texts: dict[str, list[dict]] = {}
    rows: list[dict] = []
    for g in groups:
        stable_with = [root / s for s in g.get("stable_with", [])]
        for sp in g["spans"]:
            rel = sp["file"]
            path = root / rel
            if not path.exists():
                continue
            if rel not in texts:
                texts[rel] = tex_blocks.blocks(path.read_text(encoding="utf-8", errors="ignore"))
            ages = [(now - p.stat().st_mtime) / 60 for p in [path, *stable_with] if p.exists()]
            age = min(ages) if ages else 0.0
            for b in texts[rel]:
                if not (sp["start"] <= b["start"] <= sp["end"]):
                    continue
                kind = "result" if b["env"] in tex_blocks.RESULT_ENVS else "definition"
                st, cases, acc = (state_of({**b, "file": rel}, seen.get(b["label"], [])) if b["label"]
                                  else ("unreviewed", [], False))
                if kind == "definition" and not any(r["exact"] for r in seen.get(b["label"], [])):
                    st, cases, acc = "unreviewed", [], False
                rows.append({"group": g["name"], "file": rel, "label": b["label"], "env": b["env"], "kind": kind,
                             "start": b["start"], "end": b["end"], "section": b["section"],
                             "has_proof": b["has_proof"], "state": st, "cases": cases, "accepted_repair": acc,
                             "priority": bool(sp.get("priority")), "age_min": round(age, 1),
                             "stable": age >= a.stable_minutes})
    return rows, stats, groups


def chunks(rows: list[dict], max_lines: int, order: list[str] | None = None) -> list[dict]:
    out: list[dict] = []
    cur: list[dict] = []

    def flush():
        if cur:
            out.append({"group": cur[0]["group"], "file": cur[0]["file"], "section": cur[0]["section"],
                        "state": cur[0]["state"],
                        "start": cur[0]["start"], "end": cur[-1]["end"], "count": len(cur),
                        "labels": [r["label"] or f"(無ラベル L{r['start']})" for r in cur],
                        "priority": any(r["priority"] for r in cur), "stable": all(r["stable"] for r in cur),
                        "age_min": min(r["age_min"] for r in cur)})
        cur.clear()

    for r in rows:
        if r["kind"] != "result":
            continue
        target = r["state"] in ("unreviewed", "changed") and r["has_proof"]
        if cur and (not target or r["group"] != cur[0]["group"] or r["file"] != cur[0]["file"]
                    or r["priority"] != cur[0]["priority"] or r["state"] != cur[0]["state"]
                    or r["section"] != cur[0]["section"] or r["end"] - cur[0]["start"] + 1 > max_lines):
            flush()
        if target:
            cur.append(r)
    flush()
    rank = {g: i for i, g in enumerate(order or [])}
    out.sort(key=lambda c: (rank.get(c["group"], 0), not c["priority"], not c["stable"], c["state"] != "unreviewed",
                            -c["count"], c["group"], c["file"], c["start"]))
    return out


def summary(rows: list[dict], stats: dict, groups: list[dict]) -> str:
    lines = ["== 独立数学レビューの被覆（記録から再計算。台帳ではない）",
             f"cases {stats['cases']}（数学 {stats['math']}、READYあり {stats['ready']}、除外 {stats['excluded']}；"
             f"判定 manifest {stats['exact']}／unit.tex {stats['unit']}／本文推定 {stats['heuristic']}；"
             f"軽微修復の記録 {stats['repairs']}）"]
    for g in groups:
        rs = [r for r in rows if r["group"] == g["name"]]
        res = [r for r in rs if r["kind"] == "result" and r["has_proof"]]
        nop = [r for r in rs if r["kind"] == "result" and not r["has_proof"]]
        defs = [r for r in rs if r["kind"] == "definition"]
        c = {s: sum(r["state"] == s for r in res) for s in RANK}
        unl = sum(r["label"] is None for r in res)
        pri = sum(r["state"] == "unreviewed" and r["priority"] for r in res)
        acc = sum(r["state"] == "current" and r["accepted_repair"] for r in res)
        lines.append(f"{g['name']:<8} 証明つき結果 {len(res)}：現行版で確認済 {c['current']}（うち軽微修復 {acc}）  確認中 {c['in-review']}  "
                     f"確認後に変更 {c['changed']}  未確認 {c['unreviewed']}（優先span {pri}、無ラベル {unl}）"
                     f"  ／証明なし {len(nop)}  定義 {len(defs)}（確認済 {sum(r['state'] == 'current' for r in defs)}）")
    return "\n".join(lines)


def record_repair(a) -> int:
    """Write AUTHOR_REPAIR.json: the current hashes of the case's target results after a minor-only repair."""
    case = a.reviews / a.case
    if not case.is_dir():
        print(f"case がない: {case}", file=sys.stderr)
        return 2
    if not is_ready(case):
        print(f"READY がない（返却前）: {a.case}", file=sys.stderr)
        return 2
    try:
        man = json.loads((case / "manifest.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        man = {}
    rel = man.get("file") if isinstance(man, dict) else None
    targets = man.get("target_labels") if isinstance(man, dict) else None
    if isinstance(targets, dict) and targets:
        old = dict(targets)
    elif (case / "unit.tex").exists():
        old = {b["label"]: b["hash"] for b in tex_blocks.blocks(tex_blocks.strip_line_numbers(
            (case / "unit.tex").read_text(encoding="utf-8", errors="ignore"))) if b["label"] and b["complete"]}
    else:
        old = {}
    if not rel or not old:
        print("manifest の file と対象ラベルが読めない case には記録できない（再確認に回す）", file=sys.stderr)
        return 2
    path = a.root / rel
    if not path.exists():
        print(f"正本がない: {path}", file=sys.stderr)
        return 2
    now = {b["label"]: b["hash"] for b in tex_blocks.blocks(path.read_text(encoding="utf-8", errors="ignore"))
           if b["label"]}
    missing = sorted(set(old) - set(now))
    if missing:
        print(f"正本に無いラベル（改名・削除。再確認に回す）: {', '.join(missing)}", file=sys.stderr)
        return 2
    labels = {lab: now[lab] for lab in old}
    rec = {"severity": "minor", "recorded": time.strftime("%Y-%m-%dT%H:%M:%S"), "file": rel, "labels": labels}
    if a.note:
        rec["note"] = a.note
    (case / REPAIR).write_text(json.dumps(rec, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    changed = [lab for lab in labels if labels[lab] != old[lab]]
    print(f"{a.case}: 軽微修復を記録 {len(labels)}件（うち本文が変わった {len(changed)}件"
          + (f": {', '.join(changed)}" if changed else "") + "）")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("command", nargs="?", default="summary", choices=["summary", "next", "list", "record-repair"])
    ap.add_argument("--root", required=True, type=pathlib.Path)
    ap.add_argument("--files", nargs="+", default=["chapters/*.tex"])
    ap.add_argument("--reviews", required=True, type=pathlib.Path)
    ap.add_argument("--case-glob", default="*")
    ap.add_argument("--groups", type=pathlib.Path)
    ap.add_argument("--exclude", type=pathlib.Path, help="file with one case directory name per line")
    ap.add_argument("--stable-minutes", type=float, default=30.0)
    ap.add_argument("--max-lines", type=int, default=600)
    ap.add_argument("-n", type=int, default=3)
    ap.add_argument("--group")
    ap.add_argument("--state", choices=list(RANK))
    ap.add_argument("--group-order", action="store_true",
                    help="propose earlier groups first (the order of --groups), e.g. to finish volumes front to back")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--case", help="record-repair: case directory name under --reviews")
    ap.add_argument("--severity", choices=["minor"],
                    help="record-repair: required; only repairs of minor findings are accepted without a recheck")
    ap.add_argument("--note")
    a = ap.parse_args(argv)
    if a.command == "record-repair":
        if not a.case or a.severity != "minor":
            ap.error("record-repair には --case と --severity minor が要る")
        return record_repair(a)
    a.exclude_names = []
    if a.exclude:
        a.exclude_names = [x.split("#")[0].strip() for x in a.exclude.read_text(encoding="utf-8").splitlines()
                           if x.split("#")[0].strip()]
    rows, stats, groups = collect(a)
    if a.command == "summary":
        if a.json:
            print(json.dumps({"stats": stats, "rows": rows}, ensure_ascii=False))
        else:
            print(summary(rows, stats, groups))
    elif a.command == "next":
        cs = chunks(rows, a.max_lines, [g["name"] for g in groups] if a.group_order else None)[: a.n]
        if a.json:
            print(json.dumps(cs, ensure_ascii=False))
        else:
            print("-- 次の候補（未確認または確認後に変更された証明つき結果の連続。優先span→安定→未確認→件数の順）")
            for i, c in enumerate(cs, 1):
                shown = ", ".join(c["labels"][:4]) + (f" ほか{c['count'] - 4}件" if c["count"] > 4 else "")
                kind = "未確認" if c["state"] == "unreviewed" else "確認後に変更（変わった結果だけ再確認）"
                print(f"{i}. {c['group']} {c['file']} L{c['start']}-{c['end']}  節 {c['section']}  {kind} {c['count']}件 [{shown}]"
                      f"  {'安定' if c['stable'] else '未安定'}（最終書込 {c['age_min']:.0f}分前）{'  優先span' if c['priority'] else ''}")
            if not cs:
                print("（候補なし）")
    else:
        sel = [r for r in rows if (not a.group or r["group"] == a.group) and (not a.state or r["state"] == a.state)]
        if a.json:
            print(json.dumps(sel, ensure_ascii=False))
        else:
            for r in sel:
                print(f"{r['group']}\t{r['state']}\t{r['env']}\t{r['label']}\t{r['file']}:{r['start']}-{r['end']}"
                      f"\t{','.join(r['cases'][:2])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
