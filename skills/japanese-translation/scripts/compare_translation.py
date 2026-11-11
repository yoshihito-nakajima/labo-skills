#!/usr/bin/env python3
"""Compare a LaTeX source with its Japanese translation for literal fidelity.

  compare_translation.py SOURCE.tex TRANSLATION.tex [--json] [--strict]

A literal translation changes the language and nothing else, so these should agree:
  * the mathematical formulas (inline and display), compared as multisets after whitespace normalization;
  * the sequence of structural environments (theorem-like, proof, lists, figures);
  * sections, citations (keys), labels and references;
  * the amount of parenthetical remarks, and the translated length relative to the source.
Differences are hints for a human, not verdicts: macros, reordered items or legitimate rephrasing
can produce them. With --strict the exit status is 1 when formulas, environments, citations or
references differ.
"""
import argparse
import collections
import difflib
import json
import pathlib
import re
import sys

ENVS = ("theorem lemma proposition corollary definition remark example conjecture claim fact notation assumption "
        "proof itemize enumerate description figure table abstract").split()
MATH_ENVS = "equation align gather multline eqnarray flalign alignat".split()
DROP = re.compile(r"\\left|\\right|\\displaystyle|\\textstyle|\\,|\;|\\!|\\:|\\quad|\\qquad|\\ |\\label\{[^{}]*\}|\\nonumber|\\notag|\s+")
CITE = re.compile(r"\\(?:cite[a-zA-Z]*|nocite)(?:\[[^\]]*\])*\{([^{}]*)\}")
REF = re.compile(r"\\(?:eqref|ref|cref|Cref|autoref|pageref)\{([^{}]*)\}")
LABEL = re.compile(r"\\label\{([^{}]*)\}")
SECTION = re.compile(r"\\(?:section|subsection|subsubsection|paragraph)\*?\b")
CJK = re.compile(r"[\u3040-\u30ff\u3400-\u9fff]")


MACRO = re.compile(r"\\(?:re)?newcommand\*?\{(\\[A-Za-z]+)\}\{((?:[^{}]|\{[^{}]*\})*)\}|\\DeclareMathOperator\*?\{(\\[A-Za-z]+)\}\{([^{}]*)\}")


def expand_macros(t):
    """Expand argument-free macros so that \\R and \\mathbb R compare equal."""
    macros = {}
    for m in MACRO.finditer(t):
        if m.group(1):
            macros[m.group(1)] = m.group(2)
        else:
            macros[m.group(3)] = "\\operatorname{" + m.group(4) + "}"
    for _ in range(3):
        for name, body in macros.items():
            t = re.sub(re.escape(name) + r"(?![A-Za-z])", lambda _m, b=body: b, t)
    return t


def read(path):
    t = pathlib.Path(path).read_text(encoding="utf-8", errors="ignore")
    return expand_macros(re.sub(r"(?<!\\)%.*", "", t))


def math_items(t):
    items = []
    pat = [r"\$\$(.+?)\$\$", r"(?<!\\)\\\[(.+?)\\\]"] + [rf"\\begin\{{{e}\*?\}}(.+?)\\end\{{{e}\*?\}}" for e in MATH_ENVS]
    for p in pat:
        for m in re.finditer(p, t, flags=re.S):
            items.append(m.group(1))
        t = re.sub(p, " ", t, flags=re.S)
    for m in re.finditer(r"(?<!\\)\$([^$]+?)(?<!\\)\$", t):
        items.append(m.group(1))
    t = re.sub(r"(?<!\\)\$([^$]+?)(?<!\\)\$", " ", t)
    items = [DROP.sub("", re.sub(r"\\(?:text|textrm|mbox|mathrm\{text)\{[^{}]*\}", r"\\text{}", x)).rstrip(".,;") for x in items]
    return [x for x in items if x], t


def prose(t):
    t = re.sub(r"\\begin\{(?:%s)\*?\}.*?\\end\{(?:%s)\*?\}" % ("|".join(MATH_ENVS), "|".join(MATH_ENVS)), " ", t, flags=re.S)
    t = re.sub(r"\\[A-Za-z]+\*?(?:\[[^\]]*\])?", " ", t)
    return re.sub(r"[{}]", " ", t)


def multiset_diff(a, b):
    ca, cb = collections.Counter(a), collections.Counter(b)
    return sorted((ca - cb).elements()), sorted((cb - ca).elements())


def env_sequence(t):
    return [m.group(1) for m in re.finditer(r"\\begin\{(%s)\*?\}" % "|".join(ENVS), t)]


def parens(t, ja):
    out = []
    for m in re.finditer(r"[（(]([^（）()]{6,}?)[）)]", prose(t)):
        s = m.group(1).strip()
        if ja and not CJK.search(s):
            continue
        out.append(s)
    return out


def compare(src_path, tr_path):
    src, tr = read(src_path), read(tr_path)
    ms, rest_s = math_items(src)
    mt, rest_t = math_items(tr)
    miss, add = multiset_diff(ms, mt)
    es, et = env_sequence(src), env_sequence(tr)
    sm = difflib.SequenceMatcher(a=es, b=et, autojunk=False)
    env_diffs = [f"{tag} source[{i1}:{i2}]={es[i1:i2]} translation[{j1}:{j2}]={et[j1:j2]}"
                 for tag, i1, i2, j1, j2 in sm.get_opcodes() if tag != "equal"]
    cs = [k.strip() for m in CITE.finditer(src) for k in m.group(1).split(",")]
    ct = [k.strip() for m in CITE.finditer(tr) for k in m.group(1).split(",")]
    cmiss, cadd = multiset_diff(cs, ct)
    rs, rt = [m.group(1) for m in REF.finditer(src)], [m.group(1) for m in REF.finditer(tr)]
    rmiss, radd = multiset_diff(rs, rt)
    ls, lt = [m.group(1) for m in LABEL.finditer(src)], [m.group(1) for m in LABEL.finditer(tr)]
    lmiss, ladd = multiset_diff(ls, lt)
    ps, pt = parens(src, False), parens(tr, True)
    en_words = len(prose(rest_s).split())
    ja_chars = len(re.sub(r"\s", "", prose(rest_t)))
    return {
        "formulas": {"source": len(ms), "translation": len(mt), "only_in_source": miss[:15], "only_in_translation": add[:15]},
        "environment_sequence": {"source": len(es), "translation": len(et), "differences": env_diffs[:10]},
        "sections": {"source": len(SECTION.findall(src)), "translation": len(SECTION.findall(tr))},
        "citations": {"source": len(cs), "translation": len(ct), "only_in_source": cmiss[:10], "only_in_translation": cadd[:10]},
        "references": {"only_in_source": rmiss[:10], "only_in_translation": radd[:10]},
        "labels": {"only_in_source": lmiss[:10], "only_in_translation": ladd[:10]},
        "parentheticals": {"source": len(ps), "translation_japanese_only": len(pt), "examples": pt[:8]},
        "length": {"source_words": en_words, "translation_chars": ja_chars,
                   "chars_per_word": round(ja_chars / max(1, en_words), 2)},
    }


def strict_ok(r):
    return not (r["formulas"]["only_in_source"] or r["formulas"]["only_in_translation"] or r["environment_sequence"]["differences"]
                or r["citations"]["only_in_source"] or r["citations"]["only_in_translation"]
                or r["references"]["only_in_source"] or r["references"]["only_in_translation"])


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("source"); ap.add_argument("translation")
    ap.add_argument("--json", action="store_true"); ap.add_argument("--strict", action="store_true")
    a = ap.parse_args(argv)
    r = compare(a.source, a.translation)
    if a.json:
        print(json.dumps(r, indent=1, ensure_ascii=False))
    else:
        f = r["formulas"]
        print(f"formulas: {f['source']} vs {f['translation']}; only in source {len(f['only_in_source'])}, only in translation {len(f['only_in_translation'])}")
        for x in f["only_in_source"][:5]:
            print("  - source only:", x[:90])
        for x in f["only_in_translation"][:5]:
            print("  + translation only:", x[:90])
        e = r["environment_sequence"]
        print(f"environments: {e['source']} vs {e['translation']}; differences {len(e['differences'])}")
        for x in e["differences"][:5]:
            print("  ", x)
        print(f"sections: {r['sections']['source']} vs {r['sections']['translation']}")
        c = r["citations"]
        print(f"citations: {c['source']} vs {c['translation']}; refs differ: {len(r['references']['only_in_source']) + len(r['references']['only_in_translation'])}")
        p = r["parentheticals"]
        print(f"parentheticals: source {p['source']}, Japanese-only in translation {p['translation_japanese_only']}")
        print(f"length: {r['length']['translation_chars']} chars / {r['length']['source_words']} words = {r['length']['chars_per_word']}")
    return 1 if a.strict and not strict_ok(r) else 0


if __name__ == "__main__":
    sys.exit(main())
