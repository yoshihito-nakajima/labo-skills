#!/usr/bin/env python3
"""Tile pages of one or more PDFs into one PNG, to compare a draft with reference decks.

  contact_sheet.py out.png draft.pdf:1-5 reference.pdf:8,17 [--cols 3] [--width 640]

Needs `pdftoppm` (poppler) and Pillow. A page spec is `file.pdf` (all pages),
`file.pdf:3`, `file.pdf:1-5` or a comma list of those.
"""
import argparse, subprocess, sys, tempfile
from pathlib import Path


def parse(spec):
    path, _, pages = spec.partition(':')
    if not pages:
        n = int([l for l in subprocess.run(['pdfinfo', path], capture_output=True, text=True, check=True).stdout.splitlines()
                 if l.startswith('Pages:')][0].split()[1])
        return path, list(range(1, n + 1))
    out = []
    for part in pages.split(','):
        a, _, b = part.partition('-')
        out += list(range(int(a), int(b or a) + 1))
    return path, out


def main():
    try:
        from PIL import Image, ImageDraw
    except ImportError:
        sys.exit('contact_sheet.py needs Pillow (pip install pillow)')
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('out'); ap.add_argument('specs', nargs='+')
    ap.add_argument('--cols', type=int, default=3); ap.add_argument('--width', type=int, default=640)
    a = ap.parse_args()
    tiles = []
    with tempfile.TemporaryDirectory() as tmp:
        for spec in a.specs:
            path, pages = parse(spec)
            for p in pages:
                stem = Path(tmp) / f'{len(tiles)}'
                subprocess.run(['pdftoppm', '-png', '-r', '90', '-f', str(p), '-l', str(p), '-singlefile', path, str(stem)], check=True)
                im = Image.open(f'{stem}.png').convert('RGB')
                im = im.resize((a.width, round(im.height * a.width / im.width)))
                ImageDraw.Draw(im).text((6, 4), f'{Path(path).name} p{p}', fill=(255, 0, 0))
                tiles.append(im)
        h = max(t.height for t in tiles)
        rows = -(-len(tiles) // a.cols)
        sheet = Image.new('RGB', (a.cols * (a.width + 6) + 6, rows * (h + 6) + 6), (60, 60, 60))
        for i, t in enumerate(tiles):
            sheet.paste(t, (6 + (i % a.cols) * (a.width + 6), 6 + (i // a.cols) * (h + 6)))
        sheet.save(a.out)
    print(f'wrote {a.out}: {len(tiles)} pages')


if __name__ == '__main__':
    main()
