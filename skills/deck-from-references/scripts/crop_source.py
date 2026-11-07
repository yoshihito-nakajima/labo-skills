#!/usr/bin/env python3
"""Cut a figure out of a source PDF without touching the source.

The PDF is only read: its page is rendered and a box is cut out into a NEW image.
Allowed operations: cut a box, trim blank margins, render at a higher resolution
(enlargement without resampling). Forbidden (not offered): retouching, recoloring,
removing labels, changing the aspect ratio. Every cut is recorded in a manifest
(source file and sha256, page, dpi, box, trim, output and its sha256), so the figure
can be reproduced and checked against the source.

  crop_source.py SOURCE.pdf --page 19 --box 150,150,1130,665 --dpi 150 \
      --out figs/figure.png [--trim] [--manifest figs/MANIFEST.json]

--box is x0,y0,x1,y1 in pixels of the page rendered at --dpi (use --show to write the
whole page with a pixel grid next to the output, to choose the box). Needs pdftoppm and Pillow.
"""
import argparse, hashlib, json, subprocess, sys, tempfile
from pathlib import Path


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    try:
        from PIL import Image, ImageChops, ImageDraw
    except ImportError:
        sys.exit('crop_source.py needs Pillow (pip install pillow)')
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('source'); ap.add_argument('--page', type=int, required=True)
    ap.add_argument('--box'); ap.add_argument('--dpi', type=int, default=150)
    ap.add_argument('--out', required=True); ap.add_argument('--trim', action='store_true')
    ap.add_argument('--pad', type=int, default=6); ap.add_argument('--manifest')
    ap.add_argument('--show', action='store_true', help='also write OUT.page.png: the full page with a pixel grid')
    a = ap.parse_args()
    src_hash = sha(a.source)
    with tempfile.TemporaryDirectory() as tmp:
        stem = Path(tmp) / 'page'
        subprocess.run(['pdftoppm', '-png', '-r', str(a.dpi), '-f', str(a.page), '-l', str(a.page), '-singlefile', a.source, str(stem)], check=True)
        page = Image.open(f'{stem}.png').convert('RGB')
    if a.show:
        g = page.copy(); d = ImageDraw.Draw(g)
        for y in range(0, g.height, 50):
            d.line([(0, y), (40, y)], fill=(255, 0, 0)); d.text((44, y - 5), str(y), fill=(255, 0, 0))
        for x in range(0, g.width, 100):
            d.line([(x, 0), (x, 30)], fill=(0, 0, 255)); d.text((x + 2, 32), str(x), fill=(0, 0, 255))
        g.save(a.out + '.page.png')
        print(f'wrote {a.out}.page.png ({page.width}x{page.height} at {a.dpi} dpi)'); return
    if not a.box:
        sys.exit('give --box x0,y0,x1,y1 (use --show to see the page with a grid)')
    x0, y0, x1, y1 = (int(v) for v in a.box.split(','))
    if not (0 <= x0 < x1 <= page.width and 0 <= y0 < y1 <= page.height):
        sys.exit(f'box outside the page ({page.width}x{page.height})')
    img = page.crop((x0, y0, x1, y1))
    trimmed = None
    if a.trim:
        bg = Image.new('RGB', img.size, (255, 255, 255))
        diff = ImageChops.difference(img, bg).convert('L').point(lambda v: 255 if v > 12 else 0)
        bb = diff.getbbox()
        if bb:
            bb = (max(bb[0] - a.pad, 0), max(bb[1] - a.pad, 0), min(bb[2] + a.pad, img.width), min(bb[3] + a.pad, img.height))
            img = img.crop(bb); trimmed = list(bb)
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    img.save(a.out)
    entry = {'source': str(a.source), 'source_sha256': src_hash, 'page': a.page, 'dpi': a.dpi, 'box': [x0, y0, x1, y1],
             'trim_box_within_box': trimmed, 'out': str(a.out), 'out_sha256': sha(a.out), 'size': list(img.size)}
    if sha(a.source) != src_hash:
        sys.exit('the source changed while cutting')
    if a.manifest:
        mp = Path(a.manifest)
        data = json.loads(mp.read_text()) if mp.exists() else []
        data = [e for e in data if e.get('out') != str(a.out)] + [entry]
        mp.write_text(json.dumps(data, indent=2))
    print(f'wrote {a.out} {img.size[0]}x{img.size[1]}')


if __name__ == '__main__':
    main()
