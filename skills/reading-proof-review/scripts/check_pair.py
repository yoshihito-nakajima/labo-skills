#!/usr/bin/env python3
"""Check the pair of a detailed note (PDF) and its companion (HTML): see references/pair.md.

  check_pair.py PAIR.json [--record] [--require-corpus] [--allow-open]
"""
import argparse, hashlib, json, os, sys, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
TREATED = {'inherited', 'baseline', 'criticised', 'encompassing', 'encompassed', 'prior-version'}


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('pair'); ap.add_argument('--record', action='store_true'); ap.add_argument('--require-corpus', action='store_true'); ap.add_argument('--allow-open', action='store_true')
    a = ap.parse_args()
    base = os.path.dirname(os.path.abspath(a.pair))
    rel = lambda p: os.path.normpath(os.path.join(base, p))
    P = json.load(open(a.pair, encoding='utf-8')); probs = []
    note, comp = P.get('note') or {}, P.get('companion') or {}
    files = {'note pdf': rel(note.get('pdf', '')), 'companion html': rel(comp.get('html', '')), 'companion spec': rel(comp.get('spec', '')), 'coverage': rel(note.get('coverage', ''))}
    for k, f in files.items():
        if not os.path.isfile(f):
            probs.append(f'{k}: file not found ({f})')
    if probs:
        print('\n'.join(probs)); sys.exit(1)
    built = P.setdefault('built', {})
    now = {'note_sha256': sha(files['note pdf']), 'companion_sha256': sha(files['companion html'])}
    if a.record:
        built.update(now, date=datetime.date.today().isoformat()); json.dump(P, open(a.pair, 'w', encoding='utf-8'), ensure_ascii=False, indent=1); print('recorded', now)
    else:
        for k in now:
            if built.get(k) != now[k]:
                probs.append(f'{k} differs from the recorded build (rebuilt since? run with --record after checking both)')
    spec = json.load(open(files['companion spec'], encoding='utf-8')); cov = json.load(open(files['coverage'], encoding='utf-8'))
    # treated comparisons <-> lineage cards
    carded = {c for e in ((spec.get('lineage') or {}).get('entries') or []) for c in (e.get('comparisons') or [])}
    waived = {x.get('comparison'): x.get('reason') for x in P.get('not_in_companion') or []}
    for c in cov.get('comparisons', []):
        if c.get('relation') in TREATED and (c.get('primary') or {}).get('status') == 'read' and c['id'] not in carded:
            if not waived.get(c['id']):
                probs.append(f"comparison {c['id']}: in the note but neither in a companion lineage card (comparisons: [...]) nor in not_in_companion with a reason")
    for cid in carded:
        if cid not in {c['id'] for c in cov.get('comparisons', [])}:
            probs.append(f'lineage card cites comparison {cid}, which is not in the note')
    # figure differences
    comp_figs = {g.get('label'): g for g in spec.get('figures', [])}
    with_diff = {g['label'] for g in spec.get('figures', []) if g.get('difference')}
    noted = {d.get('figure') for d in (cov.get('overview') or {}).get('differences', [])}
    for lab in sorted(with_diff - noted):
        probs.append(f'{lab}: the companion has a difference the note does not (add it to the note first)')
    for lab in sorted(noted - with_diff):
        probs.append(f'{lab}: the note has a difference the companion lacks')
    # intake
    if P.get('intake'):
        sys.path.insert(0, os.path.join(HERE, '..', '..', 'reading-reference', 'scripts'))
        import check_intake
        ip, io = check_intake.check(json.load(open(rel(P['intake']), encoding='utf-8')))
        probs += [f'intake {w}: {p}' for w, p in ip]
        if io and not a.allow_open:
            probs += [f'intake {w}: OPEN ({p})' for w, p in io]
    # corpus
    cd = (P.get('corpus') or {}).get('dir')
    if cd:
        root = os.path.normpath(os.path.join(base, '..', '..', cd))
        for k, f in (('note.pdf', files['note pdf']), ('companion.html', files['companion html'])):
            q = os.path.join(root, k)
            if not os.path.isfile(q) or sha(q) != sha(f):
                (probs.append if a.require_corpus else print)(f'corpus copy {k} is missing or stale ({root})')
    elif a.require_corpus:
        probs.append('no corpus copy recorded (run archive_pair.py)')
    print('\n'.join(probs)); print(f'{len(probs)} problem(s)'); sys.exit(1 if probs else 0)


if __name__ == '__main__':
    main()
