#!/usr/bin/env python3
"""Build both halves of a pair in the right order and record the build (provisional; see references/pair.md).

  build_pair.py PAIR.json --workspace ROOT [--skip-note]

1. note PDF (the workspace's output build; skip with --skip-note when only the HTML changed)
2. companion HTML from the spec (the PDF's labels and pages are read from its aux, so the PDF comes first)
3. checks: companion, coverage gate, intake, pair; then the build is recorded in PAIR.json.
Stops at the first failing step. Nothing is published or pushed.
"""
import argparse, json, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
RR = os.path.join(HERE, '..', '..', 'reading-reference', 'scripts')


def run(cmd, what):
    print(f'== {what}')
    r = subprocess.run(cmd)
    if r.returncode:
        sys.exit(f'stopped: {what} failed')


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('pair'); ap.add_argument('--workspace', required=True); ap.add_argument('--skip-note', action='store_true')
    a = ap.parse_args()
    ws = os.path.abspath(a.workspace); base = os.path.dirname(os.path.abspath(a.pair)); rel = lambda p: os.path.normpath(os.path.join(base, p))
    P = json.load(open(a.pair, encoding='utf-8')); note, comp = P['note'], P['companion']
    py = sys.executable
    if not a.skip_note:
        labo = os.path.join(ws, '.venv', 'bin', 'python')
        run([labo if os.path.exists(labo) else py, os.path.join(ws, '.agents', 'scripts', 'labo.py'), 'output', 'build', '--source', os.path.relpath(os.path.join(rel(note['source_dir']), 'main.tex'), ws)], 'note PDF')
    cmd = [py, '-I', os.path.join(HERE, 'build_companion.py'), rel(comp['spec']), '--out', rel(comp['html'])]
    if comp.get('template'):
        cmd += ['--template', rel(comp['template'])]
    run(cmd, 'companion HTML')
    run([py, '-I', os.path.join(HERE, 'check_companion.py'), rel(comp['spec']), rel(comp['html']), '--workspace', ws], 'companion check')
    gate = subprocess.run([py, '-I', os.path.join(RR, 'check_coverage.py'), rel(note['coverage']), '--allow-open'])   # a record problem of the note is reported, not a reason to skip the rest
    run([py, '-I', os.path.join(HERE, 'check_pair.py'), a.pair, '--record'] + ['--allow-open'], 'pair record')
    run([py, '-I', os.path.join(HERE, 'check_pair.py'), a.pair, '--allow-open'], 'pair check')
    if gate.returncode:
        sys.exit('built and recorded, but the note\'s coverage gate reports problems (listed above): repair them before review')
    print('built and recorded; archive with archive_pair.py when the pair is reviewed')


if __name__ == '__main__':
    main()
