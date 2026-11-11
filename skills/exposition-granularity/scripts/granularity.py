#!/usr/bin/env python3
"""Estimate the exposition granularity of a text corpus and check an artifact against it.

  granularity.py profile FILE... --out profile.json [--report profile.md] [--min-docs N]
  granularity.py check PROFILE.json ARTIFACT
  granularity.py loo FILE... [--min-docs N]

English prose only (.txt, .md, .tex). The profile records, from the corpus alone,
  assumed  : technical terms used in many documents and almost never defined there;
  defined  : terms that the documents themselves usually define when they use them;
  density  : explicit naming phrases (called, we say, \\emph, ...) and parenthetical remarks per 1000 words; the first counts only explicit cues, not every definition (Let, Put, write), so read it as a rough guide, as quartiles.
The numbers are descriptive cues about what these authors do, not rules about what is right.
"""
import argparse
import collections
import json
import pathlib
import re
import statistics
import sys

STOP = set("""a an the of in on at to for and or is are be was were this that these those it its by with as from we our
which such if then than so not no can may let has have had there here also any all each every some one two three whose
where when while into onto over under between among about more most less least only both either neither other another same
given following thus hence therefore since because however moreover note recall suppose assume denote define defined called say
said theorem proof lemma corollary definition remark proposition example section paper obtain prove follow follows implie
implies hold holds case see take first respectively satisfy satisfying exist using use respect many complete completes call fact
result results above below next finally already show shown give gives write put now way but does mean consider based second
third particular author authors arxiv journal""".split())
OPS = set("inf sup lim liminf limsup max min".split())
DEF_RE = re.compile(
    r"\b(?:is called|are called|we call|is said to be|are said to be|we say that|is termed|we define|is defined as|"
    r"will be called|so-called|called)\b\s+(?:a |an |the )?([A-Za-z][A-Za-z\-]*(?:\s+[A-Za-z\-]+){0,3})", re.I)
# "we call <object> a <term> if ..." : the defined term follows the object
CALL_OBJ_RE = re.compile(
    r"\bwe call\b[^.;]{1,40}?\b(?:a|an|the)\s+([A-Za-z\-]+(?:\s+[A-Za-z\-]+){0,2}?)(?=\s+(?:if|when|provided|whenever|that|which)\b|[,.;])", re.I)
CUT = {"if", "when", "provided", "whenever", "that", "which", "for", "by", "with", "of", "and", "or", "in", "on", "at",
       "to", "is", "are", "where", "such", "as"}
EMPH_RE = re.compile(r"\\(?:emph|textit|defn|defterm)\{([^{}]{2,60})\}")
PAREN_RE = re.compile(r"\([^()]{6,}\)")
TOK_RE = re.compile(r"[A-Za-z][A-Za-z\-]*")
CJK_RE = re.compile(r"[\u3040-\u30ff\u3400-\u9fff]")


def read_text(path):
    t = pathlib.Path(path).read_text(encoding="utf-8", errors="ignore")
    if str(path).endswith(".tex"):
        t = re.sub(r"(?<!\\)%.*", "", t)
        t = re.sub(r"\$\$.*?\$\$|\\\[.*?\\\]|\$[^$]*\$", " ", t, flags=re.S)  # drop math
        t = re.sub(r"\\(?:begin|end|usepackage|documentclass|newcommand|newtheorem)\b(?:\[[^\]]*\])?(?:\{[^{}]*\})*", " ", t)
        t = re.sub(r"\\(?!(?:emph|textit|defn|defterm)\{)[A-Za-z]+\*?", " ", t)
    t = re.sub(r"-\n(?=[a-z])", "", t)
    return re.sub(r"\s+", " ", t)


def norm(w):
    return w[:-1] if len(w) > 4 and w.endswith("s") and not w.endswith("ss") else w


def words(t):
    return [norm(w.lower()) for w in TOK_RE.findall(t)]


def ngrams(ws, n):
    return [" ".join(ws[i:i + n]) for i in range(len(ws) - n + 1)]


def proper_nouns(texts):
    cap, low = collections.Counter(), collections.Counter()
    for t in texts:
        for m in TOK_RE.finditer(t):
            w, i = m.group(0), m.start()
            before = t[max(0, i - 2):i].strip()
            start = i == 0 or before == "" or before.endswith(".")
            if w[0].isupper() and not start:
                cap[w.lower()] += 1
            elif w[0].islower():
                low[w] += 1
    return {w for w, c in cap.items() if c >= 3 and c > 2 * low.get(w, 0)}


def term_ok(parts, proper):
    return not (parts[0] in STOP or parts[-1] in STOP or any(len(x) < 3 or x in OPS or x in proper for x in parts))


def cut(ph):
    for i, w in enumerate(ph):
        if w in CUT:
            return ph[:i]
    return ph


def definitions(t):
    out = set()
    for m in list(DEF_RE.finditer(t)) + list(CALL_OBJ_RE.finditer(t)):
        ph = cut(words(m.group(1)))
        for n in (1, 2, 3):
            out.update(ngrams(ph, n))
    for m in EMPH_RE.finditer(t):
        ph = words(m.group(1))
        for n in (1, 2, 3):
            out.update(ngrams(ph, n))
    return out


def density(t):
    n = max(1, len(t.split()))
    return {
        "words": n,
        "naming_phrases_per_1k": round(1000 * (len(DEF_RE.findall(t)) + len(CALL_OBJ_RE.findall(t)) + len(EMPH_RE.findall(t))) / n, 2),
        "parentheticals_per_1k": round(1000 * len(PAREN_RE.findall(t)) / n, 1),
    }


def quartiles(xs):
    if len(xs) < 4:
        return None
    q = statistics.quantiles(xs, n=4)
    return {"q1": round(q[0], 2), "median": round(q[1], 2), "q3": round(q[2], 2), "min": min(xs), "max": max(xs)}


def build_profile(paths, min_docs=None, assumed_max=0.1, defined_min=0.4):
    texts = [read_text(p) for p in paths]
    n = len(texts)
    need = min_docs if min_docs else max(4, round(0.4 * n))
    proper = proper_nouns(texts)
    use = collections.defaultdict(collections.Counter)
    defd = collections.defaultdict(set)
    for i, t in enumerate(texts):
        ws = words(t)
        for k in (1, 2, 3):
            for g in ngrams(ws, k):
                if term_ok(g.split(), proper):
                    use[g][i] += 1
        for g in definitions(t):
            defd[g].add(i)
    rows = []
    for g, c in use.items():
        dfu = sum(1 for k in c.values() if k >= 2)
        if dfu >= need:
            rows.append({"term": g, "docs_using": dfu, "docs_defining": len(defd.get(g, ()))})

    def maximal(rs):
        return [r for r in rs if not any(o is not r and r["term"] in o["term"] and len(o["term"]) > len(r["term"])
                                         and o["docs_using"] >= r["docs_using"] - 1 for o in rs)]
    assumed = maximal([r for r in rows if r["docs_defining"] / r["docs_using"] <= assumed_max])
    defined = maximal([r for r in rows if r["docs_defining"] / r["docs_using"] >= defined_min])
    assumed.sort(key=lambda r: -r["docs_using"])
    defined.sort(key=lambda r: -r["docs_defining"])
    dens = [density(t) for t in texts]
    vocab = sorted({w for t in texts for w in words(t) if len(w) >= 4})
    return {
        "schema": 2, "n_docs": n, "min_docs_using": need, "vocabulary": vocab,
        "warning": "fewer than 8 documents: treat every list as anecdotal" if n < 8 else "",
        "assumed": assumed[:80], "defined": defined[:60],
        "density": {k: quartiles([d[k] for d in dens]) for k in ("naming_phrases_per_1k", "parentheticals_per_1k")},
        "limits": "Candidate terms are n-grams after a small English stoplist; screen the lists by hand. Descriptive of "
                  "these documents only. Definition cues: called/we call/we say/is said to be/we define/termed, and emphasis markup (\\emph, \\textit).",
    }


def band(value, q):
    if q is None:
        return "no band (too few documents)"
    if value > q["q3"] + 1.5 * (q["q3"] - q["q1"]):
        return f"above the corpus range (corpus max {q['max']})"
    if value > q["max"]:
        return f"above every document in the corpus (corpus max {q['max']})"
    if value < q["q1"] - 1.5 * (q["q3"] - q["q1"]):
        return f"below the corpus range (corpus min {q['min']})"
    return "within the corpus range"


def check(profile, path):
    if profile.get("schema") != 2:
        sys.exit("profile has an old or unknown schema; rebuild it with the profile command")
    t = read_text(path)
    out = {"artifact": str(path), "notes": []}
    cjk = len(CJK_RE.findall(t)) / max(1, len(t))
    if cjk > 0.2:
        out["notes"].append("The artifact is mostly Japanese/Chinese. The profile describes English prose; a Japanese deliverable "
                            "must be a literal translation of an English original: judge the English text, and require that "
                            "the translation adds or drops no definitions, glosses or parentheticals. Measurements below "
                            "are not meaningful for this text.")
    d = density(t)
    out["density"] = {k: {"value": d[k], "verdict": band(d[k], profile["density"][k])} for k in profile["density"]}
    proper = set()
    own_defs = definitions(t)
    assumed = {r["term"] for r in profile["assumed"]}
    defined = {r["term"] for r in profile["defined"]}
    ws = words(t)
    counts = collections.Counter(g for k in (1, 2, 3) for g in ngrams(ws, k) if term_ok(g.split(), proper))
    vocab = set(profile.get("vocabulary", ()))
    wc = collections.Counter(w for w in ws if len(w) >= 4 and w not in STOP)
    out["words_not_in_corpus"] = [{"word": w, "count": c} for w, c in wc.most_common() if w not in vocab][:40]
    out["possibly_over_explained"] = sorted(g for g in own_defs if g in assumed)
    out["possibly_undefined"] = sorted(g for g in defined if counts.get(g, 0) >= 2 and g not in own_defs)
    return out


def loo(paths, min_docs=None):
    rows = []
    for i, p in enumerate(paths):
        rest = [q for j, q in enumerate(paths) if j != i]
        prof = build_profile(rest, min_docs)
        r = check(prof, p)
        rows.append({"doc": str(p), **{k: v["verdict"] for k, v in r["density"].items()},
                     "own_definitions_on_assumed_terms": len(r["possibly_over_explained"])})
    return rows


def report_md(p):
    out = [f"# Granularity profile ({p['n_docs']} documents)", ""]
    if p["warning"]:
        out += [f"**{p['warning']}**", ""]
    out += ["## Assumed vocabulary (used, almost never defined)"]
    out += [f"- {r['term']} ({r['docs_using']} docs; defined in {r['docs_defining']})" for r in p["assumed"][:40]]
    out += ["", "## Usually defined by the authors"]
    out += [f"- {r['term']} ({r['docs_using']} docs; defined in {r['docs_defining']})" for r in p["defined"][:30]]
    out += ["", "## Density"]
    for k, q in p["density"].items():
        out.append(f"- {k}: {q if q else 'too few documents'}")
    out += ["", f"Limits: {p['limits']}"]
    return "\n".join(out) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("profile"); a.add_argument("files", nargs="+"); a.add_argument("--out", required=True)
    a.add_argument("--report"); a.add_argument("--min-docs", type=int)
    b = sub.add_parser("check"); b.add_argument("profile"); b.add_argument("artifact")
    c = sub.add_parser("loo"); c.add_argument("files", nargs="+"); c.add_argument("--min-docs", type=int)
    args = ap.parse_args(argv)
    if args.cmd == "profile":
        if len(args.files) < 3:
            sys.exit("need at least 3 documents to estimate anything")
        p = build_profile(args.files, args.min_docs)
        pathlib.Path(args.out).write_text(json.dumps(p, indent=1, ensure_ascii=False), encoding="utf-8")
        if args.report:
            pathlib.Path(args.report).write_text(report_md(p), encoding="utf-8")
        print(f"wrote {args.out} ({p['n_docs']} docs, {len(p['assumed'])} assumed, {len(p['defined'])} defined)")
    elif args.cmd == "check":
        prof = json.loads(pathlib.Path(args.profile).read_text(encoding="utf-8"))
        print(json.dumps(check(prof, args.artifact), indent=1, ensure_ascii=False))
    else:
        if len(args.files) < 4:
            sys.exit("need at least 4 documents for leave-one-out")
        print(json.dumps(loo(args.files, args.min_docs), indent=1, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
