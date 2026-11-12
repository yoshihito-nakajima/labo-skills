#!/usr/bin/env python3
"""Check a section record (see reading-reference/references/survey-profile.md).

Usage: check_section_record.py RECORD.json
Exit 0 when there are no errors; warnings do not fail the check.
"""
import json, re, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import code_langs as CL

KINDS = {"author", "official", "lib", "ai", "port", "none"}
LOC = re.compile(r"\bpp?\.\s?\d+")


def chk_notes(i, st, err, warn):
    """Line notes: [first, last, text] ranges that cover the Step's lines exactly once (blank, import and closing-bracket lines may share a note)."""
    rows = st.get("lines") or []
    if not rows: err.append(f"{i}: step {st.get('title')!r} has no line notes; every line needs one (grouping blank/import lines is fine)"); return
    a0, b0 = st.get("first"), st.get("last"); seen = []
    for r in rows:
        if not (isinstance(r, list) and len(r) == 3 and isinstance(r[0], int) and isinstance(r[1], int)):
            err.append(f"{i}: step {st.get('title')!r}: a line note must be [first, last, text]"); return
        a, b, t = r
        if a > b or a < a0 or b > b0: err.append(f"{i}: step {st.get('title')!r}: note range {a}-{b} is outside the Step {a0}-{b0}")
        if len((t or "").strip()) < 12: warn.append(f"{i}: step {st.get('title')!r}: note for lines {a}-{b} is too short to say what the lines are for")
        seen += list(range(a, b + 1))
    if sorted(seen) != list(range(a0, b0 + 1)): err.append(f"{i}: step {st.get('title')!r}: notes must cover lines {a0}-{b0} exactly once")
    if len(rows) * 2 < (b0 - a0 + 1) // 3: warn.append(f"{i}: step {st.get('title')!r}: very few notes for {b0 - a0 + 1} lines")


def chk_also(i, s, err, warn):
    """`also`: the same Step in another language. Every Step must offer each language used in the section; a port says whether it was checked against the original."""
    steps = s.get("steps", []); langs = {}
    for st in steps:
        for n, a in enumerate(st.get("also", [])):
            tag = f"{i}: step {st.get('title')!r} also[{n}]"
            for k in ("file", "first", "last", "kind", "lines"):
                if k not in a: err.append(f"{tag} lacks {k!r}")
            if a.get("kind") not in KINDS: err.append(f"{tag}: kind {a.get('kind')!r}")
            if "file" not in a: continue
            key = CL.lang_of(a["file"]) or a["file"]; langs.setdefault(key, set()).add(st.get("title"))
            if CL.lang_of(a["file"]) is None: warn.append(f"{tag}: unknown code language for {a['file']!r}")
            if CL.lang_of(a["file"]) == CL.lang_of(st.get("file", "")): warn.append(f"{tag}: same language as the main version; a language gets one fold")
            if a.get("kind") == "port" and not a.get("verified"): warn.append(f"{tag}: AI port without 'verified' (state how it was checked against the original, or say it was not)")
            if all(k in a for k in ("first", "last", "lines")): chk_notes(i, dict(title=st.get("title"), first=a["first"], last=a["last"], lines=a["lines"]), err, warn)
    for key, titles in langs.items():
        miss = [st.get("title") for st in steps if st.get("title") not in titles]
        if miss: warn.append(f"{i}: language {key!r} is missing for Steps {miss}; each fold shows 'no version of this Step' there")


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

    for c in rec.get("concepts", []):
        for k in ("gist", "explain", "definition"):
            if not c.get(k): err.append(f"concept {c.get('id')}: '{k}' is required (gist: one or two lines; explain: role, intuition, where it appears; definition: precise)")
        if c.get("explain") and c["explain"].strip() == c.get("definition", "").strip():
            warn.append(f"concept {c['id']}: explain repeats the definition; say what it is for and where it appears")
        if c.get("gist") and len(c["gist"]) > 200: warn.append(f"concept {c['id']}: gist is longer than two lines")
    homed = {r for sec in rec["sections"] for r in sec.get("concepts", [])}
    for c in rec.get("concepts", []):
        if c["id"] not in homed: err.append(f"concept {c['id']}: not listed in any section's 'concepts' (the two ledgers link through the home section)")
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
        cids = {c["id"] for c in rec.get("concepts", [])}
        for r in s.get("concepts", []):
            if r not in cids: err.append(f"{i}: concept {r} is not defined in the record's concepts")
        for x in s.get("claims", []):
            for r in x.get("concepts", []):
                if r not in cids: err.append(f"{i}: claim {x.get('id')} refers to unknown concept {r}")
        for w, d, *_ in s.get("glossary", []):
            if len(d.strip()) < 3 * len(w.strip()): warn.append(f"{i}: glossary term {w!r} is explained in fewer words than a name needs; give one or two lines (what it is, what it is good for)")
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
            for k in ("flow", "why", "after"):
                if not s.get(k):
                    warn.append(f"{i}: code section lacks '{k}' (the goal of the code as a whole / why this tool and not another / what the result means)")
            for st in s.get("steps", []):
                chk_notes(i, st, err, warn)
                if st.get("file") and CL.lang_of(st["file"]) is None:
                    warn.append(f"{i}: step {st.get('title')!r}: unknown code language for {st['file']!r} (add a row to scripts/code_langs.py; it is listed without color until then)")
                for k in ("title", "what", "file", "first", "last", "math"):
                    if k not in st:
                        err.append(f"{i}: step {st.get('title')!r} lacks {k!r}")
            chk_also(i, s, err, warn)
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
        if not (d.get("text") or "").strip():
            warn.append(f"figure {f}: no reading text (what to look at, panel by panel)")
        terms = d.get("terms") or []
        if not terms:
            warn.append(f"figure {f}: no terms for reading it (each as [term, what it is and is good for, basis])")
        for t in terms:
            if not (isinstance(t, list) and len(t) == 3 and all(str(x).strip() for x in t)):
                err.append(f"figure {f}: a term must be [term, explanation, basis] (basis: the caption or text, or 'AI lookup, unchecked')")
                break
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
