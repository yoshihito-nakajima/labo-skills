#!/usr/bin/env python3
"""Check a built companion page against its spec and the privacy rule.

  check_companion.py companion.json index.html [--max-kb 8000] [--workspace ROOT] [--allow-pending]

Reports: spec problems (as build does); code excerpts in the page that no longer match the
source files; any external resource the page would load (script/link/img/iframe src, CSS
url(), fetch/XMLHttpRequest); a page over the size limit; and, with --workspace, an output
path that the workspace's Git does not ignore (companions are private); and figure units still
pending, unless --allow-pending (used while units are built one at a time). Exit 1 on problems.
"""
import argparse, json, os, re, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from companion_lib import load  # noqa: E402

EXTERNAL = [r'<script[^>]+src\s*=\s*["\']?(https?:)?//', r'<link[^>]+href\s*=\s*["\']?(https?:)?//',
            r'<img[^>]+src\s*=\s*["\']?(https?:)?//', r'<iframe[^>]+src\s*=\s*["\']?(https?:)?//',
            r'url\(\s*["\']?(https?:)?//', r'@import', r'\bfetch\s*\(', r'XMLHttpRequest']


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('spec')
    ap.add_argument('html')
    ap.add_argument('--max-kb', type=int, default=8000)
    ap.add_argument('--workspace')
    ap.add_argument('--allow-pending', action='store_true', help='accept figure units not built yet (while building one at a time)')
    a = ap.parse_args()
    data, probs = load(a.spec)
    pend = [g.get('label') for g in data.get('figures', []) if g.get('pending')]
    if pend and not a.allow_pending:
        probs.append(f"figures: {len(pend)} figure unit(s) not built yet: {', '.join(pend)} (every main-text figure needs its unit)")
    page = open(a.html, encoding='utf-8').read()
    m = re.search(r'const DATA = (\{.*?\});\s*\n', page, re.S)
    if not m:
        probs.append('page: no embedded data (was it built by build_companion.py?)')
    else:
        embedded = json.loads(m.group(1).replace('<\\/', '</'))
        now = {f['id']: {s: c.get('sha256') for s, c in f['codes'].items()} for f in data['features']}
        for f in embedded.get('features', []):
            for s, c in f.get('codes', {}).items():
                if 'sha256' in c and now.get(f['id'], {}).get(s) != c['sha256']:
                    probs.append(f"page: feature {f['id']} {s} differs from the current source; rebuild")
    for pat in EXTERNAL:
        if re.search(pat, page, re.I):
            probs.append(f'page: external resource or network call ({pat})')
    kb = os.path.getsize(a.html) // 1024
    if kb > a.max_kb:
        probs.append(f'page: {kb} KB over the {a.max_kb} KB limit')
    if a.workspace:
        r = subprocess.run(['git', '-C', a.workspace, 'check-ignore', '-q', os.path.abspath(a.html)])
        if r.returncode != 0:
            probs.append('page: output path is not ignored by the workspace Git (companions are private)')
    print('\n'.join(probs) if probs else 'ok')
    print(f'{len(probs)} problem(s)')
    sys.exit(1 if probs else 0)


if __name__ == '__main__':
    main()
