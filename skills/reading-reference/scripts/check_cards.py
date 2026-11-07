#!/usr/bin/env python3
"""Check a background-card data file (roots-and-lenses.md, "Card data").

  check_cards.py CARDS.json [--json]
  check_cards.py CARDS.json --todo [--target "Author Year"]

Reports, per unit: a missing field, a lens field that is not a {text, source} pair, an
empty source, a source that only points into the reading note itself, the writer's
reading without a recorded search, malformed search records, and roots that are unknown
or that list units which do not exist. Exit status 1 when anything is reported.

--todo lists the open questions instead (roots-and-lenses.md, "Let the card decide what
to search"): fields whose source is the writer's reading, and, with --target, strength,
limit and example fields that rest only on the target paper.
"""
import argparse, json, re, sys

LENS = ('shared', 'lens', 'applied', 'specific', 'limit')
SPEAKER = re.compile(r"^(speaker's reading|発表者の読み)$")
OUTCOMES = {'states it', 'found, does not state it', 'inaccessible', 'not found in the searched scope'}
RESERVED = re.compile(r"^(speaker's reading|発表者の読み|AI-created|AI 作成|AI作成|n/a:\s*\S.*|該当なし[:：]\s*\S.*)$")
# A source that names only a place inside the note (not the work the note took it from).
NOTE_ONLY = re.compile(r'^(?:詳細版|本資料|本教材|教材)|^(?:this note|the note|reading note|note)\b', re.I)


def check(data):
    problems = []
    roots = {r.get('id'): r for r in data.get('roots', [])}
    nodes = data.get('nodes', {})
    for rid, r in roots.items():
        for key in ('question', 'source', 'shared_example', 'nodes'):
            if not r.get(key):
                problems.append((f'root {rid}', f'missing {key}'))
        for n in r.get('nodes', []):
            if n not in nodes:
                problems.append((f'root {rid}', f'lists unknown unit {n}'))
        se = r.get('shared_example')
        if se is not None:
            problems += [(f'root {rid}', p) for p in pair_problems('shared_example', se)]
    for uid, card in nodes.items():
        if not card.get('uses'):
            problems.append((uid, 'missing uses'))
        if not card.get('roots'):
            problems.append((uid, 'missing roots'))
        for rid in card.get('roots', []):
            if rid not in roots:
                problems.append((uid, f'unknown root {rid}'))
        for field in LENS:
            if field not in card:
                problems.append((uid, f'missing {field}'))
            else:
                problems += [(uid, p) for p in pair_problems(field, card[field])]
    return problems


def pair_problems(field, value):
    if not isinstance(value, dict) or 'text' not in value or 'source' not in value:
        return [f'{field} is not a {{text, source}} pair']
    text, source = str(value['text']).strip(), str(value['source']).strip()
    out = []
    if not text:
        out.append(f'{field} has no text')
    if not source:
        out.append(f'{field} has no source')
    elif NOTE_ONLY.match(source) and not RESERVED.match(source):
        out.append(f'{field} source points into the note itself ({source}); name the original work')
    searched = value.get('searched')
    if SPEAKER.match(source) and not searched:
        out.append(f"{field} is the writer's reading without a recorded search (add 'searched')")
    for entry in searched or []:
        if not isinstance(entry, dict) or not str(entry.get('where', '')).strip() or entry.get('outcome') not in OUTCOMES:
            out.append(f'{field} has a search record without where/outcome ({entry})')
    return out


def todo(data, target=None):
    """Open questions: the writer's reading, and fields resting only on the target paper."""
    items = []
    for uid, card in data.get('nodes', {}).items():
        for field in LENS:
            value = card.get(field)
            if not isinstance(value, dict) or str(value.get('text', '')).strip() == '—':
                continue
            source = str(value.get('source', ''))
            if SPEAKER.match(source):
                items.append((uid, field, "writer's reading", value.get('text', '')))
            elif target and field in ('lens', 'limit', 'specific') and source.startswith(target) and ';' not in source and not value.get('searched'):
                items.append((uid, field, 'rests only on the target paper', value.get('text', '')))
    return items


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('cards')
    ap.add_argument('--json', action='store_true')
    ap.add_argument('--todo', action='store_true', help='list open questions for the literature search')
    ap.add_argument('--target', help='name of the target paper as written in sources (for --todo)')
    a = ap.parse_args()
    with open(a.cards, encoding='utf-8') as fh:
        data = json.load(fh)
    if a.todo:
        items = todo(data, a.target)
        if a.json:
            print(json.dumps([{'unit': u, 'field': f, 'why': w, 'text': t} for u, f, w, t in items],
                             ensure_ascii=False, indent=2))
        else:
            for u, f, w, t in items:
                print(f'{u} / {f}: {w}: {t}')
            print(f'{len(items)} open question(s)', file=sys.stderr)
        return 0
    problems = check(data)
    if a.json:
        print(json.dumps([{'unit': u, 'problem': p} for u, p in problems], ensure_ascii=False, indent=2))
    else:
        for u, p in problems:
            print(f'{u}: {p}')
        print(f'{len(problems)} problem(s)', file=sys.stderr)
    return 1 if problems else 0


if __name__ == '__main__':
    sys.exit(main())
