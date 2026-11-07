#!/usr/bin/env python3
"""Measure how heavy and how small each page of a slide PDF is.

Words per page (Latin tokens + CJK characters / 2), the median height of body
words relative to the page width, words drawn over each other (a label printed on
text, an overflowing box) and words outside the page, so decks with different paper sizes compare.
Suggested defaults are a 150-word page limit and a minimum median body word
height of 1.75 percent of page width. Calibrate these for the audience and format;
they are starting points, not measurements of reference decks.
Needs `pdftotext` (poppler) only.

  deck_audit.py deck.pdf [--max-words 150] [--min-median 0.0175] [--json]
  deck_audit.py deck.pdf --example example.pdf [--size-tol 0.10] [--words-factor 1.2] [--previous earlier.pdf]

With --example the deck is compared with the user's own example deck instead of the suggested defaults:
a page whose words exceed --words-factor times the example's maximum per page is a problem (a page far
above the example's word count is the usual sign that it is not in the user's manner); a page whose median
body word height / page width differs from the example's median by more than --size-tol is a NOTE only
(sizes by role are defaults and a page may change them; length is the constraint). With --previous the
median size is compared with an earlier build of the same deck (previous chunk) and a drift is a NOTE, so
that a change of size is a choice, not an accident. The deck's own overall median is reported against both.
"""
import argparse, json, os, re, statistics, subprocess, sys
from xml.etree import ElementTree

CJK = re.compile(r'[぀-ヿ一-鿿]')
LATIN = re.compile(r'[A-Za-z0-9]+')


PAGE = re.compile(r'<page width="([\d.]+)" height="([\d.]+)">(.*?)</page>', re.S)
WORD = re.compile(r'<word xMin="([\d.]+)" yMin="([\d.]+)" xMax="([\d.]+)" yMax="([\d.]+)">(.*?)</word>', re.S)


def bbox_pages(pdf):
    out = subprocess.run(['pdftotext', '-bbox', pdf, '-'], capture_output=True, text=True, check=True).stdout
    for m in PAGE.finditer(out):
        words = [(t, float(x0), float(y0), float(x1), float(y1)) for x0, y0, x1, y1, t in WORD.findall(m.group(3))]
        yield float(m.group(1)), float(m.group(2)), words


LINE = re.compile(r'<line xMin="([\d.]+)" yMin="[\d.]+" xMax="([\d.]+)" yMax="[\d.]+">(.*?)</line>', re.S)
BLOCK = re.compile(r'<block xMin="[\d.]+" yMin="[\d.]+" xMax="([\d.]+)" yMax="[\d.]+">(.*?)</block>', re.S)
BREAK_OK = '、。，．,.;:；：）)」』?!？！'


def mid_phrase_breaks(pdf, fill=0.94):
    """Lines that wrap inside a phrase: in a block of two or more lines, a line that runs to the block's full width (so it was
    wrapped, not a short deliberate line) must end at a comma, a full stop or a closing bracket (the user's rule: a break only
    after 、 or 。). Returns [(page, end of the line)]."""
    out = subprocess.run(['pdftotext', '-bbox-layout', pdf, '-'], capture_output=True, text=True, check=True).stdout
    res = []
    for pi, pg in enumerate(re.split(r'<page ', out)[1:], 1):
        for bx1, blk in BLOCK.findall(pg):
            lines = []
            for x0, x1, ln in LINE.findall(blk):
                toks = re.findall(r'>([^<]*)</word>', ln)
                lines.append((float(x0), float(x1), ''.join(toks) if all(CJK.search(t) or not LATIN.search(t) for t in toks) else ' '.join(toks)))
            if len(lines) < 2:
                continue
            left, right = min(l[0] for l in lines), max(l[1] for l in lines)
            for x0, x1, t in lines[:-1]:
                if t and t[-1] not in BREAK_OK and (x1 - left) >= fill * (right - left):
                    res.append((pi, t[-24:]))
    return res


def text_over_images(pdf, min_share=0.5, min_len=3):
    """Text lying on an image (poppler `pdftohtml -xml`, which gives the positions of text and images): a text box with at least
    `min_share` of its area inside an image box. Texts shorter than `min_len` characters (numbered marks) are not reported."""
    import tempfile, html
    with tempfile.TemporaryDirectory() as d:
        subprocess.run(['pdftohtml', '-xml', '-q', pdf, os.path.join(d, 'o')], capture_output=True, check=True)
        xml = open(os.path.join(d, 'o.xml'), encoding='utf-8', errors='replace').read()
    res = []
    for pm in re.finditer(r'<page number="(\d+)"(.*?)</page>', xml, re.S):
        body = pm.group(2)
        imgs = [tuple(map(float, m)) for m in re.findall(r'<image top="([\d.]+)" left="([\d.]+)" width="([\d.]+)" height="([\d.]+)"', body)]
        for t, l, w, h, txt in re.findall(r'<text top="([\d.]+)" left="([\d.]+)" width="([\d.]+)" height="([\d.]+)"[^>]*>(.*?)</text>', body):
            t, l, w, h = map(float, (t, l, w, h)); txt = html.unescape(re.sub(r'<[^>]+>', '', txt)).strip()
            if len(txt) < min_len or w * h == 0:
                continue
            for it, il, iw, ih in imgs:
                ow, oh = min(l + w, il + iw) - max(l, il), min(t + h, it + ih) - max(t, it)
                if ow > 0 and oh > 0 and ow * oh / (w * h) >= min_share:
                    res.append((int(pm.group(1)), txt[:30])); break
    return res


def collisions(words, w, h, min_share=0.4):
    """Words drawn over each other, and words reaching outside the page.

    Two word boxes collide when their intersection covers at least `min_share` of the
    smaller box; words of one or two characters are ignored (math limits and
    sub/superscripts touch legitimately).
    """
    outside = [t for t, x0, y0, x1, y1 in words if x0 < 0 or y0 < 0 or x1 > w or y1 > h]
    boxes = [(t, x0, y0, x1, y1) for t, x0, y0, x1, y1 in words if len(t) > 2]
    hits = []
    for i in range(len(boxes)):
        t, a0, b0, a1, b1 = boxes[i]
        for u, c0, d0, c1, d1 in boxes[i + 1:]:
            iw, ih = min(a1, c1) - max(a0, c0), min(b1, d1) - max(b0, d0)
            if iw <= 0 or ih <= 0:
                continue
            small = min((a1 - a0) * (b1 - b0), (c1 - c0) * (d1 - d0))
            if small > 0 and iw * ih / small >= min_share:
                hits.append((t, u))
    return hits, outside


def audit(pdf, max_words=150, min_median=0.0175, min_height=0.014, header=0.09, footer=0.07):
    pages = []
    for i, (w, h, words) in enumerate(bbox_pages(pdf), 1):
        text = ' '.join(t for t, *_ in words)
        count = len(LATIN.findall(text)) + len(CJK.findall(text)) / 2
        body = [(t, y1 - y0) for t, x0, y0, x1, y1 in words if header * h < y0 and y1 < (1 - footer) * h]
        small = [t for t, ht in body if ht / w < min_height]
        overlaps, outside = collisions(words, w, h)
        pages.append({'page': i, 'words': round(count, 1), 'body_words': len(body), 'small_body_words': len(small),
                      'small_share': round(len(small) / len(body), 2) if body else 0.0,
                      'median_height_over_width': round(statistics.median(ht for _, ht in body) / w, 4) if body else None,
                      'upper_median_height_over_width': round(statistics.median([ht for _, ht in body if ht >= statistics.median(x for _, x in body)]) / w, 4) if body else None,
                      'overlaps': [' / '.join(p) for p in overlaps[:5]], 'outside': outside[:5]})
    counts = [p['words'] for p in pages]
    summary = {'pages': len(pages), 'median_words': statistics.median(counts) if counts else 0,
               'max_words': max(counts) if counts else 0,
               'heavy_pages': [p['page'] for p in pages if p['words'] > max_words],
               'small_text_pages': [p['page'] for p in pages
                                    if p['median_height_over_width'] is not None and p['median_height_over_width'] < min_median],
               'overlap_pages': [p['page'] for p in pages if p['overlaps']],
               'outside_pages': [p['page'] for p in pages if p['outside']]}
    return {'summary': summary, 'pages': pages}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('pdf'); ap.add_argument('--max-words', type=float, default=150)
    ap.add_argument('--min-median', type=float, default=0.0175, help='floor of the page median of word-box height / page width')
    ap.add_argument('--min-height', type=float, default=0.014, help='words below this are counted in small_share (captions, tags)')
    ap.add_argument('--json', action='store_true')
    ap.add_argument('--overlaps', action='store_true', help='report text lying on an image (poppler pdftohtml)')
    ap.add_argument('--wraps', action='store_true', help='report lines that wrap inside a phrase (breaks are allowed only after 、 or 。)')
    ap.add_argument('--example', help="the user's example deck (PDF): calibrate size and words against it")
    ap.add_argument('--previous', help='an earlier build of this deck (PDF): a size drift is noted')
    ap.add_argument('--size-tol', type=float, default=0.10); ap.add_argument('--words-factor', type=float, default=1.2)
    a = ap.parse_args()
    r = audit(a.pdf, a.max_words, a.min_median, a.min_height)
    cmp_problems, notes = [], []
    def med_size(rr):
        v = [p['upper_median_height_over_width'] for p in rr['pages'] if p['upper_median_height_over_width'] is not None]   # the larger half of the words: small roles (notes, labels, citations) do not pull the size down
        return statistics.median(v) if v else None
    if a.example:
        ex = audit(a.example, a.max_words, a.min_median, a.min_height); es = med_size(ex); ms = med_size(r)
        lim = ex['summary']['max_words'] * a.words_factor
        print(f"example {a.example}: median size {es}, median words {ex['summary']['median_words']}, max words {ex['summary']['max_words']}")
        print(f"this deck: median size {ms} ({ms / es:.2f} of the example's), median words {r['summary']['median_words']}")
        for p in r['pages']:
            h = p['upper_median_height_over_width']
            if h is not None and abs(h / es - 1) > a.size_tol:
                notes.append(f"p{p['page']}: text size {h / es:.2f} of the example's (tolerance +-{a.size_tol:.0%})")
            if p['words'] > lim:
                cmp_problems.append(f"p{p['page']}: {p['words']} words, above {lim:.0f} (= {a.words_factor} x the example's maximum): not in the example's manner")
    if a.overlaps:
        for pg, t in text_over_images(a.pdf):
            cmp_problems.append(f'p{pg}: text lies on an image: {t}')
    if a.wraps:
        for pg, t in mid_phrase_breaks(a.pdf):
            notes.append(f'p{pg}: a line wraps inside a phrase: ...{t}')
    if a.previous:
        pv = audit(a.previous, a.max_words, a.min_median, a.min_height); ps, ms = med_size(pv), med_size(r)
        print(f"previous {a.previous}: median size {ps}; this deck {ms} ({ms / ps:.2f} of the previous)")
        if abs(ms / ps - 1) > a.size_tol:
            notes.append(f"median text size is {ms / ps:.2f} of the previous build's (tolerance +-{a.size_tol:.0%}): a deliberate change?")
    if a.json:
        print(json.dumps(r, indent=2, ensure_ascii=False))
        return 1 if r['summary']['overlap_pages'] or r['summary']['outside_pages'] else 0
    s = r['summary']
    for c in notes:
        print('NOTE:', c)
    for c in cmp_problems:
        print('COMPARE:', c)
    print(f"{a.pdf}: {s['pages']} pages, median {s['median_words']} words, max {s['max_words']}")
    print('heavy pages (> %g words):' % a.max_words, s['heavy_pages'] or 'none')
    print('pages whose median body text is below %g of the page width:' % a.min_median, s['small_text_pages'] or 'none')
    print('pages with words drawn over each other:', s['overlap_pages'] or 'none')
    print('pages with words outside the page:', s['outside_pages'] or 'none')
    for p in r['pages']:
        if p['overlaps'] or p['outside']:
            print(f"  p{p['page']}: overlaps {p['overlaps']} outside {p['outside']}")
    return 1 if s['overlap_pages'] or s['outside_pages'] or cmp_problems else 0
    for p in r['pages']:
        print(f"  p{p['page']:>3}  words {p['words']:>6}  small {p['small_share']:.2f}  median-h/w {p['median_height_over_width']}")


if __name__ == '__main__':
    sys.exit(main())
