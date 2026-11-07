#!/usr/bin/env python3
"""Check, in a talk plan, that every symbol is defined on or before the page that uses it.

The plan follows plan-format.md section 3: one entry per page starting with
`- **n. ...**`, and in each entry the fields

  - **Symbols introduced**: `L` = D - W (survey p.11); `W` = neighbor weights
  - **Symbols used**: `L`, `W`, `y_i`

Symbols are the texts between backticks. Symbols the audience already knows are listed
once, anywhere before the first page, as `**Assumed known**: `R^D`, `x_i``.

  plan_symbols.py PLAN.md [--json]

Reports symbols used before (or without) their introduction, with the page that
introduces them if any, and symbols introduced twice. Exit status 1 when anything is
reported. It checks the plan, not the slides: build the deck from a plan that passes.
"""
import argparse, json, re, sys

ENTRY = re.compile(r'^\s*-\s+\*\*(\d+)\.')
FIELD = re.compile(r'\*\*(Symbols introduced|Symbols used|Assumed known)\*\*\s*:(.*)', re.I)
TICK = re.compile(r'`([^`]+)`')


def parse(text):
    known, pages, current = set(), [], None
    for line in text.splitlines():
        m = ENTRY.match(line)
        if m:
            current = {'page': int(m.group(1)), 'introduced': [], 'used': []}
            pages.append(current)
            continue
        f = FIELD.search(line)
        if not f:
            continue
        kind, rest = f.group(1).lower(), f.group(2)
        if kind == 'assumed known':
            known.update(TICK.findall(rest))
        elif current is not None:
            if kind == 'symbols introduced':
                # only the symbol before "=" or the first ticked name of each item
                for item in rest.split(';'):
                    names = TICK.findall(item)
                    if names:
                        current['introduced'].append(names[0])
            else:
                current['used'].extend(TICK.findall(rest))
    return known, pages


def check(text):
    known, pages = parse(text)
    first_intro = {}
    for p in pages:
        for s in p['introduced']:
            first_intro.setdefault(s, p['page'])
    defined, problems = set(known), []
    for p in pages:
        for s in p['introduced']:
            if s in defined and s not in known and first_intro[s] != p['page']:
                problems.append({'page': p['page'], 'symbol': s, 'problem': 'introduced again',
                                 'first': first_intro[s]})
        defined.update(p['introduced'])
        for s in p['used']:
            if s not in defined:
                later = first_intro.get(s)
                problems.append({'page': p['page'], 'symbol': s,
                                 'problem': 'used before its introduction' if later else 'never introduced',
                                 'introduced_on': later})
    return {'pages': len(pages), 'assumed_known': sorted(known), 'problems': problems}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('plan')
    ap.add_argument('--json', action='store_true')
    a = ap.parse_args()
    with open(a.plan, encoding='utf-8') as fh:
        r = check(fh.read())
    if a.json:
        print(json.dumps(r, ensure_ascii=False, indent=2))
    else:
        print(f"{a.plan}: {r['pages']} pages, {len(r['problems'])} problem(s)")
        for p in r['problems']:
            extra = f" (introduced on page {p['introduced_on']})" if p.get('introduced_on') else ''
            extra = extra or (f" (first on page {p['first']})" if p.get('first') else '')
            print(f"  page {p['page']}: `{p['symbol']}` {p['problem']}{extra}")
    return 1 if r['problems'] else 0


if __name__ == '__main__':
    sys.exit(main())
