#!/usr/bin/env python3
"""Add the shared reader comment layer to an HTML page.

    python3 comment_layer.py page.html [--lang ja] [--out other.html]

The script is inlined, so the page stays a single file. Running it twice on the
same page replaces the earlier copy.
"""
import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "src"))
from labo_tools.reading_page import COMMENT_MARK as MARK, comment_script as script


def inject(html, lang=None, extra=None):
    html = re.sub(re.escape(MARK) + r'.*?' + re.escape(MARK), '', html, flags=re.S)
    tag = script(lang, extra=extra)
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
