#!/usr/bin/env python3
"""Add the comment layer (assets/comment-layer.js) to an HTML page.

    python3 comment_layer.py page.html [--lang ja] [--out other.html]

The script is inlined, so the page stays a single file. Running it twice on the
same page replaces the earlier copy.
"""
import argparse
import json
import re
from pathlib import Path

ASSET = Path(__file__).resolve().parents[1] / 'assets' / 'comment-layer.js'
MARK = '<!-- comment-layer -->'


def script(lang=None, extra=None):
    opts = {**({'lang': lang} if lang else {}), **(extra or {})}
    cfg = f'<script>window.CommentLayer={json.dumps(opts, ensure_ascii=False)};</script>' if opts else ''
    return f'{MARK}{cfg}<script>\n{ASSET.read_text(encoding="utf-8")}</script>{MARK}'


def inject(html, lang=None, extra=None):
    html = re.sub(re.escape(MARK) + r'.*?' + re.escape(MARK), '', html, flags=re.S)
    tag = script(lang, extra)
    i = html.lower().rfind('</body>')
    return html[:i] + tag + html[i:] if i >= 0 else html + tag


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('page')
    ap.add_argument('--lang')
    ap.add_argument('--out')
    a = ap.parse_args()
    src = Path(a.page)
    out = Path(a.out) if a.out else src
    out.write_text(inject(src.read_text(encoding='utf-8'), a.lang), encoding='utf-8')
    print(f'-> {out}')


if __name__ == '__main__':
    main()
