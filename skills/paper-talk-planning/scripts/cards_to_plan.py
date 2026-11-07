#!/usr/bin/env python3
"""Turn a reading note's background-card data into the talk plan's root list and
motivation-card skeletons (plan-format.md sections 2b and 2c).

  cards_to_plan.py CARDS.json [--units REGEX] [--output PLAN_SKELETON.md]

The data must follow roots-and-lenses.md ("Card data"); it is first checked with
reading-reference/scripts/check_cards.py and nothing is written if that fails. Units
are taken in the file's order; --units keeps only matching unit ids. The skeleton keeps
every source as given; fill the remaining plan fields (problem, idea, computation ...)
from the note and check them against the source pages.
"""
import argparse, json, re, subprocess, sys
from pathlib import Path

CHECK = Path(__file__).resolve().parents[2] / 'reading-reference' / 'scripts' / 'check_cards.py'
LABELS = [('shared', 'Shared example'), ('lens', 'Lens'), ('applied', 'Applied view'),
          ('specific', 'Specific example'), ('limit', 'Limit example')]


def cell(value):
    text = str(value).replace('|', '\\|').replace('\n', ' ')
    return text


def pair(v):
    if v['text'] == '—':
        return cell(v['text'])
    note = ''
    if v.get('searched'):
        found = any(e.get('outcome') == 'states it' for e in v['searched'])
        note = ' [searched: ' + ('found' if found else 'not found') + ']'
    return f"{cell(v['text'])} ({cell(v['source'])}){note}"


def skeleton(data, pattern=None):
    keep = re.compile(pattern) if pattern else None
    units = [u for u in data['nodes'] if not keep or keep.search(u)]
    out = ['## 2c. Root list', '', '| Root | Question | Source | Shared example | Units |', '|---|---|---|---|---|']
    for r in data['roots']:
        listed = [u for u in r['nodes'] if u in units]
        if keep and not listed:
            continue
        out.append(f"| {r['id']} | {cell(r['question'])} | {cell(r['source'])} | {pair(r['shared_example'])} | {', '.join(listed)} |")
    out += ['', '## 2b. Motivation cards', '']
    for u in units:
        c = data['nodes'][u]
        out += [f'### {u}', '', '| Field | Content (source) |', '|---|---|',
                '| Used here | ' + '<br>'.join(cell(x) for x in c['uses']) + ' |',
                '| Root | ' + ', '.join(c['roots']) + ' |']
        out += [f'| {label} | {pair(c[key])} |' for key, label in LABELS]
        out += ['| Problem |  |', '| Why the previous tool is not enough |  |', '| Idea and definition |  |',
                '| Computation (with code) | ' + cell(c.get('code', '')) + ' |', '| What it achieves |  |', '']
    return '\n'.join(out) + '\n'


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('cards')
    ap.add_argument('--units', help='regular expression on unit ids to keep')
    ap.add_argument('--output')
    a = ap.parse_args()
    check = subprocess.run([sys.executable, str(CHECK), a.cards], capture_output=True, text=True)
    if check.returncode:
        sys.stderr.write(check.stdout + check.stderr + 'cards fail check_cards.py; nothing written\n')
        return 1
    with open(a.cards, encoding='utf-8') as fh:
        text = skeleton(json.load(fh), a.units)
    if a.output:
        Path(a.output).write_text(text, encoding='utf-8')
    else:
        sys.stdout.write(text)
    return 0


if __name__ == '__main__':
    sys.exit(main())
