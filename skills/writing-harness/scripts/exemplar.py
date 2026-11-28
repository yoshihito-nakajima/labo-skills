"""Measure the paper's prose against an exemplar the author asked it to follow.

`style.toml` may record a phrase table from the exemplar:

    [[phrase]]
    avoid = 'one has'                 # regex, matched in prose outside math
    use = 'it holds that'             # what the exemplar writes in that role
    basis = 'exemplar, statements of lemmas'

`check` reports every `avoid` match as a PHRASE warning; a rule with
`section = "Statement"` is matched only in that section of the cards. `cards.py exemplar`
compares the cards with the exemplar files named in `harness.toml`
(`exemplar = ["..."]`, relative to the harness) or on the command line: the rate
per thousand words of each phrase of the table and of a few common markers, and the
word n-grams the cards use repeatedly that never occur in the exemplar.
"""
import collections
import re
from pathlib import Path

MATH_ENVS = r'equation|align|gather|aligned|gathered|multline|eqnarray'
MARKERS = [r'\bgives?\b', r'\bwe have\b', r'\bwe obtain\b', r'\bit holds that\b', r'\bit follows\b',
           r'\bwe deduce\b', r'\bThen\b', r'\bHence\b', r'\bThus\b', r'\bTherefore\b', r'\bMoreover\b',
           r'\bFurthermore\b', r'\bSince\b', r'\bsuch that\b', r'\bsatisfying\b', r'\bthe following\b',
           r'\bcompletes the proof\b']


def prose(tex):
    """Words outside math, with M for a formula and R for a reference or citation."""
    t = re.sub(r'(?m)(?<!\\)%.*$', '', tex)
    t = re.sub(r'\\begin\{thebibliography\}.*', '', t, flags=re.S)
    t = re.sub(r'\\begin\{(' + MATH_ENVS + r')\*?\}.*?\\end\{\1\*?\}', ' M ', t, flags=re.S)
    t = re.sub(r'\\\[.*?\\\]|\$\$.*?\$\$', ' M ', t, flags=re.S)
    t = re.sub(r'\$[^$]*\$|\\\(.*?\\\)', ' M ', t, flags=re.S)
    t = re.sub(r'\\(?:[Cc]ref|eqref|ref|cite)(?:\[[^\]]*\])?\{[^}]*\}', ' R ', t)
    t = re.sub(r'\\[a-zA-Z]+\*?', ' ', t)
    return re.sub(r'[{}~]', ' ', t)


def card_prose(c):
    body = re.sub(r'(?ms)^## (?:Shortcuts|Notes)\b.*?(?=^## |\Z)', '', c.body)
    return prose(re.sub(r'(?m)^## .*$', '', body))


def phrase_rules(h):
    import tomllib
    p = h.root / 'style.toml'
    return tomllib.loads(p.read_text(encoding='utf-8')).get('phrase', []) if p.exists() else []


def warnings(h, cards):
    out = []
    for rule in phrase_rules(h):
        rx = re.compile(rule['avoid'])
        section = rule.get('section')
        for c in cards.values():
            text = prose(c.sec(section)) if section else card_prose(c)
            for m in rx.finditer(text):
                out.append(f'PHRASE {c.id}: "{m.group(0)}"; the exemplar writes: {rule.get("use", "?")}')
    return out


def grams(text, n):
    out = collections.Counter()
    for s in re.split(r'[.;:]\s', text):
        w = [x if x in ('M', 'R') else x.lower() for x in re.findall(r"[A-Za-z][A-Za-z'-]*|M|R", s)]
        for i in range(len(w) - n + 1):
            g = w[i:i + n]
            if sum(x in ('M', 'R') for x in g) <= 1:
                out[' '.join(g)] += 1
    return out


def compare(h, cards, paths, n=3, min_count=3):
    ex = '\n'.join(prose(Path(p).read_text(encoding='utf-8')) for p in paths)
    ours = '\n'.join(card_prose(c) for c in cards.values())
    we, wo = max(1, len(ex.split())), max(1, len(ours.split()))
    lines = [f'words: exemplar {we}, cards {wo}', 'rate per 1000 words (exemplar / cards):']
    pats = [r['avoid'] for r in phrase_rules(h)] + MARKERS
    for p in dict.fromkeys(pats):
        a, b = len(re.findall(p, ex)), len(re.findall(p, ours))
        flag = '  <--' if (a == 0 and b) or (a and b and not 0.33 < (b / wo) / (a / we) < 3) else ''
        lines.append(f'  {p:32s} {1000 * a / we:5.1f} / {1000 * b / wo:5.1f}{flag}')
    ge, go = grams(ex, n), grams(ours, n)
    absent = sorted(((v, g) for g, v in go.items() if v >= min_count and not ge[g]), reverse=True)
    lines.append(f'{n}-grams used at least {min_count} times in the cards and never in the exemplar:')
    lines += [f'  {v:3d}  {g}' for v, g in absent[:60]]
    return '\n'.join(lines)
