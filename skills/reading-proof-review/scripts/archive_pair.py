#!/usr/bin/env python3
"""Copy the pair (PDF, HTML, source snapshot) into the local-only corpus: see references/pair.md.

  archive_pair.py PAIR.json --workspace ROOT

Refuses unless writing/.corpus is an independent Git without any remote. Never touches the parent repository.
Commit inside the corpus yourself; nothing is pushed.
"""
import argparse, datetime, hashlib, json, os, shutil, subprocess, sys

SKIP_DIRS = {'env', '.temp', '__pycache__', 'data', '.venv', 'node_modules'}
MAX = 30 * 1024 * 1024


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


SHALLOW = {'results'}                 # only the files directly inside (working directories of runs are large)
SKIP_PATHS = {'related/code'}         # clones of other repositories: recoverable from their recorded commits


def snapshot(src, dst, manifest, tag):
    for dp, dn, fs in os.walk(src):
        r = os.path.relpath(dp, src)
        dn[:] = [d for d in dn if d not in SKIP_DIRS and os.path.normpath(os.path.join(r, d)) not in SKIP_PATHS]
        if os.path.basename(dp) in SHALLOW:
            dn[:] = []
        for f in fs:
            p = os.path.join(dp, f)
            if f == '.DS_Store' or os.path.getsize(p) > MAX or f.endswith(('.aux', '.log', '.synctex.gz')):
                continue
            q = os.path.join(dst, tag, os.path.relpath(p, src)); os.makedirs(os.path.dirname(q), exist_ok=True); shutil.copy2(p, q)
            manifest[os.path.relpath(q, dst)] = sha(q)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('pair'); ap.add_argument('--workspace', required=True)
    a = ap.parse_args()
    ws = os.path.abspath(a.workspace); corpus = os.path.join(ws, 'writing', '.corpus')
    if not os.path.isdir(os.path.join(corpus, '.git')):
        sys.exit('refused: writing/.corpus is not an independent Git')
    if subprocess.run(['git', '-C', corpus, 'remote'], capture_output=True, text=True).stdout.strip():
        sys.exit('refused: the corpus has a remote (it must be local only)')
    base = os.path.dirname(os.path.abspath(a.pair)); rel = lambda p: os.path.normpath(os.path.join(base, p))
    P = json.load(open(a.pair, encoding='utf-8')); note, comp = P['note'], P['companion']
    date = datetime.date.today().isoformat(); rel_dir = f"writing/.corpus/method-pairs/{P['slug']}/{date}"
    dst = os.path.join(ws, rel_dir); os.makedirs(dst, exist_ok=True); manifest = {}
    for src, name in ((rel(note['pdf']), 'note.pdf'), (rel(comp['html']), 'companion.html')):
        shutil.copy2(src, os.path.join(dst, name)); manifest[name] = sha(os.path.join(dst, name))
    snapshot(rel(note['source_dir']), dst, manifest, 'source-note')
    snapshot(os.path.dirname(rel(comp['spec'])), dst, manifest, 'source-companion')
    json.dump({'slug': P['slug'], 'paper': P.get('paper'), 'date': date, 'files': manifest}, open(os.path.join(dst, 'MANIFEST.json'), 'w'), indent=1, ensure_ascii=False)
    P.setdefault('corpus', {})['dir'] = rel_dir
    json.dump(P, open(a.pair, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(f'copied {len(manifest)} files to {rel_dir}; commit inside the corpus yourself (no remote, no push)')


if __name__ == '__main__':
    main()
