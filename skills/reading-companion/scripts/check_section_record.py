#!/usr/bin/env python3
"""Check a section record (see reading-reference/references/survey-profile.md).

Usage: check_section_record.py RECORD.json
Exit 0 when there are no errors; warnings do not fail the check.
"""
import json, re, sys

KINDS = {"author", "official", "lib", "ai", "none"}
LOC = re.compile(r"\bpp?\.\s?\d+")


def check(rec):
    err, warn = [], []
    secs = {s["id"]: s for s in rec["sections"]}
    figs = rec.get("figures", {})
    if len(secs) != len(rec["sections"]):
        err.append("duplicate section ids")

    def ancestors(i):
        out, p = [], secs[i].get("parent")
        while p:
            out.append(p)
            p = secs[p].get("parent")
        return out

    for a, b, what in rec.get("edges", []):
        if a not in secs or b not in secs:
            err.append(f"edge {a}->{b}: unknown section")
            continue
        if a in ancestors(b) or b in ancestors(a):
            warn.append(f"edge {a}->{b}: structure (ancestor/descendant), show as position")
            continue
        if not what or len(what.strip()) < 4 or what.strip() in (secs[b]["title"], b):
            err.append(f"edge {a}->{b}: label must state what is passed, not the target's name")

    used = set()
    for s in rec["sections"]:
        i = s["id"]
        if not s.get("evidence") or not LOC.search(s["evidence"]):
            err.append(f"{i}: evidence lacks a page locator (p. N)")
        for k in ("lead", "bridge"):
            if not s.get(k) and not (k == "bridge" and not any(e[0] == i for e in rec.get("edges", []))):
                warn.append(f"{i}: no '{k}' paragraph (entrance and bridge carry the connections)")
        if not s.get("glossary") and s.get("weights", [1])[0] + s.get("weights", [0, 1])[1] > 0:
            warn.append(f"{i}: no glossary (terms and what they are good for)")
        if not s.get("answer") or not s.get("question"):
            err.append(f"{i}: question and answer are required")
        a, b = s["pages"]
        if a > b:
            err.append(f"{i}: bad pages")
        for f in s.get("figures", []):
            used.add(f)
            if f not in figs:
                err.append(f"{i}: unknown figure {f}")
        codes = [c for c in s.get("code", []) if c.get("kind") != "none"]
        for c in codes:
            if c["kind"] not in KINDS:
                err.append(f"{i}: code kind {c['kind']!r}")
            if c["kind"] == "ai" and not c.get("labelled_standin"):
                err.append(f"{i}: AI code {c['name']!r} must be labelled as a stand-in")
        for c in s.get("code", []):
            if c["kind"] not in KINDS:
                err.append(f"{i}: code kind {c['kind']!r}")
        if codes:
            if not s.get("steps"):
                err.append(f"{i}: a code section needs Steps")
            if not s.get("comparison") and not s.get("no_comparison_reason"):
                err.append(f"{i}: needs a comparison or a reasoned 'no_comparison_reason'")
            for k in ("flow", "after"):
                if not s.get(k):
                    warn.append(f"{i}: code section lacks '{k}' (what the code solves / what the result means)")
            for st in s.get("steps", []):
                if not st.get("lines"):
                    warn.append(f"{i}: step {st.get('title')!r} has no line-by-line reading")
                for k in ("title", "what", "file", "first", "last", "math"):
                    if k not in st:
                        err.append(f"{i}: step {st.get('title')!r} lacks {k!r}")
            for r in (s.get("comparison") or {}).get("rows", []):
                if r.get("status") not in ("same", "changed", "only_left", "only_right"):
                    err.append(f"{i}: comparison row status {r.get('status')!r}")
                if not r.get("why"):
                    err.append(f"{i}: comparison row {r.get('label')!r} lacks a reason")
    for f, d in figs.items():
        if f not in used:
            err.append(f"figure {f} is not used by any section")
        if not d.get("color_checked"):
            err.append(f"figure {f}: colour legend not checked against the image and caption")
    return err, warn


def main(argv):
    if len(argv) != 2:
        print(__doc__)
        return 2
    err, warn = check(json.load(open(argv[1], encoding="utf-8")))
    for w in warn:
        print("warning:", w)
    for e in err:
        print("ERROR:", e)
    print(f"{len(err)} errors, {len(warn)} warnings")
    return 1 if err else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
