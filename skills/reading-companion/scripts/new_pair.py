#!/usr/bin/env python3
"""Start a note + companion pair (provisional foundation; see references/pair.md).

  new_pair.py SLUG --workspace ROOT [--paper "citation"]

Creates reading/SLUG/ (note skeleton, intake record, coverage data, PAIR.json) and
reading/SLUG-companion/ (an empty companion spec that lists what is still to be filled).
Refuses when a directory exists, or when the parent Git does not ignore /reading/ (the pair is private).
"""
import argparse, json, os, shutil, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
SKEL = os.path.join(HERE, '..', '..', 'reading-reference', 'assets', 'method-note')


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('slug'); ap.add_argument('--workspace', required=True); ap.add_argument('--paper', default='TODO: citation')
    a = ap.parse_args()
    ws = os.path.abspath(a.workspace); note = os.path.join(ws, 'reading', a.slug); comp = note + '-companion'
    for d in (note, comp):
        if os.path.exists(d):
            sys.exit(f'refused: {d} exists')
    probe = os.path.join('reading', a.slug, 'main.tex')
    if subprocess.run(['git', '-C', ws, 'check-ignore', '-q', probe]).returncode != 0:
        sys.exit('refused: the parent Git does not ignore reading/ (the pair embeds the paper\'s figures and code; it is private)')
    for d in ('orig', 'code', 'figures', 'related/papers'):
        os.makedirs(os.path.join(note, d))
    for src, dst in (('main.tex', 'main.tex'), ('macros.tex', 'macros.tex'), ('coverage_spec.json', 'coverage.json'), ('intake.json', 'intake.json')):
        s = open(os.path.join(SKEL, src), encoding='utf-8').read().replace('reading/example-note', f'reading/{a.slug}')
        open(os.path.join(note, dst), 'w', encoding='utf-8').write(s)
    for d in ('results', 'assets', 'tools'):
        os.makedirs(os.path.join(comp, d))
    todo = 'TODO'
    spec = {"title": todo, "lang": "ja", "paper": {"citation": a.paper, "main_figures": 0}, "note": {"pdf": f"../../output/{a.slug}.pdf", "aux": f"../{a.slug}/.temp/{a.slug}-main.aux"},
            "background": {"picture": todo, "summary": todo, "question": todo, "context": todo, "terms": []},
            "lineage": {"families": [], "entries": []}, "overview": [], "methods": {"author": {}, "prior": []}, "datasets": [], "requests": [], "unobtained": [],
            "code_map": None, "figures": [], "features": []}
    json.dump(spec, open(os.path.join(comp, 'companion.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    pair = {"slug": a.slug, "paper": a.paper, "note": {"pdf": f"../../output/{a.slug}.pdf", "source_dir": ".", "coverage": "coverage.json", "aux": f".temp/{a.slug}-main.aux"},
            "companion": {"html": f"../{a.slug}-companion/index.html", "spec": f"../{a.slug}-companion/companion.json"}, "intake": "intake.json", "not_in_companion": []}
    json.dump(pair, open(os.path.join(note, 'PAIR.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(f'created reading/{a.slug}/ and reading/{a.slug}-companion/\nnext: put the paper PDF in inbox/, fill intake.json (literature-intake.md), write the note, then the companion spec; build with build_pair.py')


if __name__ == '__main__':
    main()
