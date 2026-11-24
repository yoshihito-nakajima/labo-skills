#!/usr/bin/env python3
"""Make a commentable HTML viewer of a slide PDF.

    python3 <skill>/scripts/slide_comment_view.py output/deck.pdf <out-dir> \
        [--tex <deck>.tex] [--title "..."] [--lang ja] [--dpi 110]

Each page is shown as an image with an invisible text layer taken from
`pdftotext -bbox-layout`, so text can be selected on the slide itself. The comment
layer of writing-harness (`assets/comment-layer.js`) is inlined: select text, add a
comment, and copy all comments ("Slide N: title / quote / comment") to paste
back to the agent. Comments live in the browser tab, as on the paper's reading page.

With --tex, frame titles are read from \\frametitle{...} in order (one page per
frame; decks with overlays need the labels checked).
"""
import argparse
import html
import re
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

SKILLS = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(SKILLS / 'writing-harness' / 'scripts'))
from comment_layer import inject  # noqa: E402


WORDS = {'ja': {'slide': 'スライド', 'title': '表紙', 'comments': 'コメント', 'copy': 'コピー'},
         'en': {'slide': 'Slide', 'title': 'Title page', 'comments': 'Comments', 'copy': 'Copy'}}


def frame_titles(tex, untitled='表紙'):
    src = Path(tex).read_text(encoding='utf-8')
    src = re.sub(r'(?<!\\)%.*', '', src)
    out = []
    for body in re.findall(r'\\begin\{frame\}(.*?)\\end\{frame\}', src, flags=re.S):
        m = re.search(r'\\frametitle\{', body)
        if not m:
            out.append(untitled)
            continue
        i, depth, j = m.end(), 1, m.end()
        while depth and j < len(body):
            depth += {'{': 1, '}': -1}.get(body[j], 0)
            j += 1
        out.append(body[i:j - 1].strip())
    return out


def text_layers(pdf):
    xml = subprocess.run(['pdftotext', '-bbox-layout', str(pdf), '-'],
                         capture_output=True, text=True, check=True).stdout
    xml = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', '', xml)
    xml = re.sub(r'<!DOCTYPE[^>]*>', '', xml)
    xml = re.sub(r'\sxmlns="[^"]*"', '', xml)
    pages = []
    for page in ET.fromstring(xml).iter('page'):
        W, H = float(page.get('width')), float(page.get('height'))
        lines = []
        for line in page.iter('line'):
            words = [w.text or '' for w in line.iter('word')]
            x0, y0 = float(line.get('xMin')), float(line.get('yMin'))
            x1, y1 = float(line.get('xMax')), float(line.get('yMax'))
            text = ''
            for w in words:
                if text and not (ord(text[-1]) > 0x2e7f and ord(w[:1] or 'a') > 0x2e7f):
                    text += ' '
                text += w
            lines.append((x0 / W, y0 / H, (x1 - x0) / W, (y1 - y0) / H, text))
        pages.append((W, H, lines))
    return pages


CSS = """
:root{color-scheme:light dark}
body{margin:0;background:#1b1f24;color:#e6e9ec;font-family:system-ui,sans-serif}
header{position:sticky;top:0;z-index:5;background:#1b1f24ee;padding:8px 16px;border-bottom:1px solid #333;display:flex;gap:12px;align-items:center}
header h1{font-size:15px;margin:0;flex:1}
header button{font-size:13px}
main{max-width:1100px;margin:0 auto;padding:12px 16px 80px}
section{margin:18px 0 28px}
section h2{font-size:12px;color:#9aa8b6;font-weight:normal;margin:0 0 4px}
.slide{position:relative;container-type:inline-size;width:100%;box-shadow:0 1px 6px #0008}
.slide img{display:block;width:100%;height:auto;user-select:none;-webkit-user-select:none}
.tl{position:absolute;inset:0}
.tl span{position:absolute;color:transparent;white-space:pre;line-height:1;cursor:text;transform-origin:0 0}
.tl span::selection{background:rgba(232,163,61,.45);color:transparent}
"""

FIT = """<script>
function fit(){document.querySelectorAll('.tl span').forEach(s=>{s.style.transform='';
const w=s.parentElement.clientWidth*parseFloat(s.dataset.w)/100;const r=s.scrollWidth;
if(r>0)s.style.transform='scaleX('+(w/r)+')';});}
window.addEventListener('load',fit);window.addEventListener('resize',fit);
</script>"""


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('pdf')
    ap.add_argument('out')
    ap.add_argument('--tex')
    ap.add_argument('--title')
    ap.add_argument('--lang', default='ja')
    ap.add_argument('--dpi', type=int, default=110)
    a = ap.parse_args()
    out = Path(a.out)
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    subprocess.run(['pdftoppm', '-r', str(a.dpi), '-png', a.pdf, str(out / 'p')], check=True)
    imgs = sorted(out.glob('p-*.png'))
    layers = text_layers(a.pdf)
    words = WORDS['ja' if a.lang.startswith('ja') else 'en']
    titles = frame_titles(a.tex, words['title']) if a.tex else []
    if titles and len(titles) != len(layers):
        print(f'warning: {len(titles)} frames, {len(layers)} pages; labels may be off', file=sys.stderr)
    title = a.title or Path(a.pdf).stem
    parts = [f'<!doctype html><html lang="{a.lang}"><head><meta charset="utf-8">'
             f'<meta name="viewport" content="width=device-width,initial-scale=1">'
             f'<title>{html.escape(title)}</title><style>{CSS}</style></head><body>'
             f'<header><h1>{html.escape(title)}</h1>'
             f'<button id="bcom">{words["comments"]} <span id="ccount">0</span></button>'
             f'<button id="bcopy">{words["copy"]}</button></header><main>']
    for n, (img, (W, H, lines)) in enumerate(zip(imgs, layers), 1):
        t = titles[n - 1] if n <= len(titles) else ''
        label = f'{words["slide"]} {n}' + (f': {t}' if t else '')
        spans = []
        for x, y, w, h, text in lines:
            spans.append(
                f'<span data-w="{w*100:.3f}" style="left:{x*100:.3f}%;top:{y*100:.3f}%;'
                f'font-size:{h*H/W*100:.3f}cqw">{html.escape(text)}</span>')
        parts.append(
            f'<section id="s{n}" data-comment-label="{html.escape(label)}">'
            f'<h2>{html.escape(label)}</h2><div class="slide">'
            f'<img src="{img.name}" alt="{html.escape(label)}" loading="lazy">'
            f'<div class="tl">{"".join(spans)}</div></div></section>')
    parts.append('</main>' + FIT + '</body></html>')
    page = inject(''.join(parts), a.lang)
    (out / 'index.html').write_text(page, encoding='utf-8')
    print(f'-> {out / "index.html"} ({len(imgs)} pages)')


if __name__ == '__main__':
    main()
