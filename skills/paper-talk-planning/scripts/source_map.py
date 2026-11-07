#!/usr/bin/env python3
"""Page-level map of a paper PDF: headings, figure/table/algorithm captions,
displayed equation numbers, images, and word counts. Use it as the locator index
of a talk plan; always check the entries against the rendered page.

  source_map.py paper.pdf [--json]

Needs `pdftotext` and `pdfimages` (poppler). Detection is regex-based and
heuristic (two-column layouts, unusual numbering and OCR text may be missed).
"""
import argparse, json, re, subprocess, sys

HEADING = re.compile(r'^\s*((?:\d+|[A-Z])(?:\.\d+)*)\.?\s{1,6}([A-Z\u201c"][^\n]{2,70})$')
CAPTION = re.compile(r'^\s*((?:Figure|Fig\.|Table|Algorithm)\s+\d+[a-z]?)[.:]\s*(.{0,90})')
EQNUM = re.compile(r'\((\d{1,3})\)\s*$')


def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True, check=True).stdout


def page_count(pdf):
    return int(re.search(r'Pages:\s+(\d+)', run(['pdfinfo', pdf])).group(1))


def image_pages(pdf):
    counts = {}
    for line in run(['pdfimages', '-list', pdf]).splitlines()[2:]:
        f = line.split()
        if len(f) > 3 and f[0].isdigit() and f[2] == 'image':
            counts[int(f[0])] = counts.get(int(f[0]), 0) + 1
    return counts


def build(pdf):
    imgs = image_pages(pdf)
    pages = []
    for i in range(1, page_count(pdf) + 1):
        text = run(['pdftotext', '-f', str(i), '-l', str(i), '-layout', pdf, '-'])
        lines = text.splitlines()
        pages.append({
            'page': i, 'words': len(text.split()), 'images': imgs.get(i, 0),
            'headings': [f'{m.group(1)} {m.group(2).strip()}' for l in lines if (m := HEADING.match(l)) and '. . .' not in l and len(m.group(2).split()) <= 10],
            'captions': [f'{m.group(1)}: {m.group(2).strip()}' for l in lines if (m := CAPTION.match(l))],
            'equations': sorted({int(m.group(1)) for l in lines if (m := EQNUM.search(l))}),
        })
    return pages


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('pdf'); ap.add_argument('--json', action='store_true')
    a = ap.parse_args()
    pages = build(a.pdf)
    if a.json:
        print(json.dumps(pages, indent=2, ensure_ascii=False)); return
    for p in pages:
        parts = [f"p.{p['page']}  {p['words']}w  img {p['images']}"]
        parts += [f"  # {h}" for h in p['headings']] + [f"  [{c}]" for c in p['captions']]
        if p['equations']:
            parts.append('  eq ' + ','.join(map(str, p['equations'])))
        print('\n'.join(parts))


if __name__ == '__main__':
    sys.exit(main())
