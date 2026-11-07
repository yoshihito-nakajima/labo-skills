#!/usr/bin/env python3
"""Check a proof-step ledger: schema, acyclicity, reachability, key impact.

Usage: check_ledger.py LEDGER.json [--json]
Exit status 0 when the ledger is consistent, 1 otherwise.
"""
import argparse
import collections
import json
import sys

TIERS = ("key", "semi", "standard")
ORIGINS = ("inherited", "standard", "adapted", "new")
REQUIRED = ("id", "title", "statement", "deps", "loc", "origin", "tier", "role")


def load(path):
    data = json.load(open(path, encoding="utf-8"))
    meta = data.get("_meta", {})
    return meta, data["steps"]


def check(meta, steps):
    errors = []
    by_id = {}
    for s in steps:
        for k in REQUIRED:
            if k not in s:
                errors.append(f"{s.get('id', '?')}: missing field {k}")
        if s.get("id") in by_id:
            errors.append(f"duplicate id {s['id']}")
        by_id[s.get("id")] = s
        if s.get("tier") not in TIERS:
            errors.append(f"{s.get('id')}: tier must be one of {TIERS}")
        if s.get("origin") not in ORIGINS:
            errors.append(f"{s.get('id')}: origin must be one of {ORIGINS}")
        if s.get("tier") == "key" and not s.get("why_tier"):
            errors.append(f"{s.get('id')}: a key step needs why_tier (why it is both necessary and not in the literature)")
    target = meta.get("target", "T")
    if target not in by_id:
        errors.append(f"target step {target!r} not found")
    for s in steps:
        for d in s.get("deps", []):
            if d not in by_id:
                errors.append(f"{s['id']}: unknown dependency {d}")
    if errors:
        return errors, None
    indeg = {k: 0 for k in by_id}
    out = collections.defaultdict(list)
    for k, s in by_id.items():
        for d in s["deps"]:
            out[d].append(k)
            indeg[k] += 1
    queue = sorted(k for k in by_id if indeg[k] == 0)
    order = []
    while queue:
        k = queue.pop(0)
        order.append(k)
        for y in sorted(out[k]):
            indeg[y] -= 1
            if indeg[y] == 0:
                queue.append(y)
    if len(order) != len(by_id):
        errors.append("dependency cycle among: " + ", ".join(sorted(set(by_id) - set(order))))
        return errors, None

    def closure(start, edges):
        seen, stack = set(), [start]
        while stack:
            x = stack.pop()
            for y in edges(x):
                if y not in seen:
                    seen.add(y)
                    stack.append(y)
        return seen

    needed = closure(target, lambda x: by_id[x]["deps"])
    unreached = sorted(k for k in by_id if k != target and k not in needed and not by_id[k].get("outside"))
    if unreached:
        errors.append("steps the target does not depend on (mark them \"outside\": true if intentional): " + ", ".join(unreached))
    impact = {k: sorted(closure(k, lambda x: out[x])) for k, s in by_id.items() if s["tier"] == "key"}
    counts = collections.Counter(s["tier"] for s in steps if s["id"] != target)
    return errors, {"order": order, "key_impact": impact, "tiers": dict(counts), "target": target}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("ledger")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    meta, steps = load(a.ledger)
    errors, info = check(meta, steps)
    if a.json:
        print(json.dumps({"errors": errors, "info": info}, ensure_ascii=False, indent=1))
    else:
        for e in errors:
            print("ERROR", e)
        if info:
            print(f"{len(steps)} steps, acyclic. tiers: {info['tiers']}")
            print("order:", " ".join(info["order"]))
            for k, v in info["key_impact"].items():
                print(f"key {k}: if it fails, affected -> {', '.join(v) or '(none)'}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
