#!/usr/bin/env python3
"""Validate, merge and summarize review findings.

Usage:
  findings.py validate FILE [FILE ...]
  findings.py merge FILE [FILE ...] --out MERGED.json
  findings.py summary FILE

A file is a JSON list of findings or {"findings": [...]}. Fields: id, sev (fatal|major|minor|form),
status (confirmed|suspected|unchecked), short, from (list of viewpoints), detail, and optionally steps,
evidence, ruling. A confirmed finding must carry evidence. Merging unions the `from` lists of
findings that share an id; two files giving different severities for one id is an error to be
settled by the parent.
"""
import argparse
import collections
import json
import sys

SEV = ("fatal", "major", "minor", "form")
STATUS = ("confirmed", "suspected", "unchecked")
REQ = ("id", "sev", "status", "short", "from", "detail")


def load(path):
    d = json.load(open(path, encoding="utf-8"))
    return d["findings"] if isinstance(d, dict) else d


def validate(findings, where=""):
    errs, seen = [], set()
    for f in findings:
        i = f.get("id", "?")
        for k in REQ:
            if k not in f:
                errs.append(f"{where}{i}: missing {k}")
        if f.get("sev") not in SEV:
            errs.append(f"{where}{i}: sev must be one of {SEV}")
        if f.get("status") not in STATUS:
            errs.append(f"{where}{i}: status must be one of {STATUS}")
        if f.get("status") == "confirmed" and not f.get("evidence"):
            errs.append(f"{where}{i}: a confirmed finding needs evidence (counterexample or reproducible computation)")
        if not isinstance(f.get("from", []), list) or not f.get("from"):
            errs.append(f"{where}{i}: from must be a non-empty list of viewpoints")
        if i in seen:
            errs.append(f"{where}duplicate id {i}")
        seen.add(i)
    return errs


def merge(lists):
    out = {}
    errs = []
    for findings in lists:
        for f in findings:
            i = f["id"]
            if i not in out:
                out[i] = dict(f)
                out[i]["from"] = list(f["from"])
                continue
            g = out[i]
            for k in ("sev", "status"):
                if g[k] != f[k]:
                    errs.append(f"{i}: {k} differs ({g[k]} vs {f[k]}); the parent must rule")
            for v in f["from"]:
                if v not in g["from"]:
                    g["from"].append(v)
    return list(out.values()), errs


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=["validate", "merge", "summary"])
    ap.add_argument("files", nargs="+")
    ap.add_argument("--out")
    a = ap.parse_args(argv)
    lists = [load(p) for p in a.files]
    errs = []
    for p, fl in zip(a.files, lists):
        errs += validate(fl, where=f"{p}: ")
    if a.cmd == "merge":
        merged, e = merge(lists)
        errs += e
        if not errs and a.out:
            json.dump({"findings": merged}, open(a.out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
            print(f"merged {sum(map(len, lists))} -> {len(merged)} findings into {a.out}")
    if a.cmd == "summary":
        fl = lists[0]
        c = collections.Counter((f["sev"], f["status"]) for f in fl)
        for s in SEV:
            print(s, {st: c[(s, st)] for st in STATUS if c[(s, st)]} or "-")
    for e in errs:
        print("ERROR", e)
    if a.cmd == "validate" and not errs:
        print("findings valid")
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main())
