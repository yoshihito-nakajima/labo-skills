#!/usr/bin/env python3
"""Build a single-file companion HTML from companion.json and its result files.

  build_companion.py companion.json --out reading/<slug>-companion/index.html [--template T]

Refuses to build when the spec is incomplete (missing background, provenance, grid points,
code excerpts that do not contain the stated parameter tokens, ...); fix the spec rather than
the page. The page is private: write it to a path the workspace's parent Git ignores.
"""
import argparse, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from companion_lib import load  # noqa: E402

TEMPLATE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'assets', 'companion-template.html')
MARK = '/*__COMPANION_DATA__*/null'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('spec')
    ap.add_argument('--out', required=True)
    ap.add_argument('--template', default=TEMPLATE)
    a = ap.parse_args()
    data, probs = load(a.spec)
    if probs:
        print('\n'.join(probs))
        print(f'{len(probs)} problem(s); not built')
        sys.exit(1)
    tpl = open(a.template, encoding='utf-8').read()
    if MARK not in tpl:
        sys.exit('template has no data marker')
    payload = json.dumps(data, ensure_ascii=False).replace('</', '<\\/')
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    with open(a.out, 'w', encoding='utf-8') as f:
        f.write(tpl.replace(MARK, payload))
    print(f'built {a.out} ({os.path.getsize(a.out) // 1024} KB, {len(data["features"])} feature(s))')


if __name__ == '__main__':
    main()
