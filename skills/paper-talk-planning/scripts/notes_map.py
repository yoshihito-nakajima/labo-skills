#!/usr/bin/env python3
"""Map a detailed reading-note PDF by source subsection, for slide planning.

For every numbered section/subsection of the note it lists the page span, the role
headings inside it ("Background | question", "Method | computation", ...), the
source-page references the note makes, and counts of provenance markers (added
explanation, AI-written code ...) per page. `--cards` writes a Markdown skeleton of
the background / reason cards to fill in from the note and check against the source.

  notes_map.py notes.pdf [--roles a,b,...] [--marker TEXT ...] [--json | --cards]

Needs `pdftotext` (poppler). Detection is regex-based: role headings must be
`LABEL | text` (full-width or ASCII bar); numbered headings `1.2.3 Title` on their own
line; table-of-contents lines are skipped and, when the note has a table of contents
(5 or more entries in its first 12 pages), only headings that repeat a contents entry's
id and title are taken, which rejects code line numbers and an embedded source's own
headings. A page that displays the source itself (marked by `--source-page-mark`)
contributes no headings. Check the result against the rendered pages; the output is a locator index, not a reading.
"""
import argparse, json, re, subprocess

ROLES = ('背景,方法・実装,原文との対応,忠実な日本語訳,Background,Method,Implementation,'
         'Correspondence,Translation')
MARKERS = ('読解の補足,読解補足,教材関数,AI 作成,AI作成,AI-written,written by AI,Added explanation')
ID = r'(?:[A-Z]\.\d+|\d+)(?:\.\d+){0,3}'
SECTION = re.compile(r'^\s*(' + ID + r')\s+(\S.{1,90}?)\s*$')
TOC_LINE = re.compile(r'^\s*(' + ID + r')\s+(\S.*?)[\s.]*\s(\d+)\s*$')
SOURCE_PAGE = re.compile(r'(?:英語原文|原文|Source|English original)\s*PDF\s*p\.(\d+(?:[–-]\d+)?)')


def pages_of(pdf):
    text = subprocess.run(['pdftotext', '-layout', pdf, '-'], capture_output=True,
                          text=True, check=True).stdout
    pages = text.split('\f')
    return pages[:-1] if pages and not pages[-1].strip() else pages


def is_toc(line):
    return bool(re.search(r'\.\s?\.\s?\.', line) or re.search(r'\s{3,}\d+\s*$', line))


def norm(t):
    return re.sub(r'\s+', '', t)


def toc_of(pages):
    """id -> title from the table-of-contents lines near the front (dot leaders or wide gaps)."""
    toc = {}
    for page in pages[:12]:
        for line in page.splitlines():
            m = TOC_LINE.match(line)
            if m and is_toc(line):
                toc.setdefault(m.group(1), re.sub(r'[\s.]+$', '', m.group(2)))
    return toc


def build(pdf, roles, markers, skip_marks=()):
    role_re = re.compile(r'^\s*(' + '|'.join(re.escape(r) for r in roles) + r')\s*[｜|]\s*(\S.*)$')
    subs, cur = [], None
    allpages = pages_of(pdf)
    toc = toc_of(allpages)
    use_toc = len(toc) >= 5
    for no, page in enumerate(allpages, 1):
        # a page that displays the source itself (its own headings in its text layer)
        shows_source = any(mark in page for mark in skip_marks)
        for line in page.splitlines():
            if not is_toc(line) and not shows_source:
                m = SECTION.match(line)
                sid = title = None
                if m and use_toc:
                    want = norm(toc.get(m.group(1), ''))[:8]
                    # same id AND the table of contents' own title: rejects code line numbers
                    # and headings of an embedded source in another language
                    if want and norm(m.group(2)).startswith(want):
                        sid, title = m.group(1), toc[m.group(1)]
                elif m and len(m.group(2).split()) <= 14 and not re.match(r'^\d+\s+\d', line.strip()):
                    sid, title = m.group(1), m.group(2)
                if sid and (cur is None or cur['id'] != sid):
                    cur = {'id': sid, 'title': title, 'first': no, 'last': no, 'roles': [],
                           'source_pages': [], 'markers': {}}
                    subs.append(cur)
                    continue
            if cur is None:
                continue
            cur['last'] = no
            m = role_re.match(line)
            if m:
                cur['roles'].append({'page': no, 'role': m.group(1), 'title': m.group(2).strip()})
            for m in SOURCE_PAGE.finditer(line):
                if m.group(1) not in cur['source_pages']:
                    cur['source_pages'].append(m.group(1))
            for mk in markers:
                n = line.lower().count(mk.lower())
                if n:
                    cur['markers'].setdefault(mk, {})
                    cur['markers'][mk][no] = cur['markers'][mk].get(no, 0) + n
    return subs


def cards(subs):
    out = []
    for s in subs:
        bg = [r for r in s['roles'] if r['role'] in ('背景', 'Background')]
        out.append(f"### {s['id']} {s['title']}  (notes pp.{s['first']}-{s['last']}; "
                   f"source pages {', '.join(s['source_pages']) or '-'})")
        out.append('- Background pages: ' + ('; '.join(f"p.{r['page']} {r['title']}" for r in bg) or '(none found)'))
        out.append('- Used here (with person, publication, title, page): ')
        out.append('- Root (ID from the root list): ')
        out.append('- Shared example (same figure for the whole root): ')
        out.append('- Lens (what it attends to; strength and weakness, with source): ')
        out.append('- Applied view (this method on the shared example): ')
        out.append('- Specific example (where the lens is visible, and why): ')
        out.append('- Limit example (stated failure -> next subsection): ')
        meth = [r for r in s['roles'] if r['role'] not in ('背景', 'Background')]
        out.append('- Other role pages: ' + ('; '.join(f"p.{r['page']} {r['role']}" for r in meth) or '-'))
        flags = '; '.join(f"{k} x{sum(v.values())} (pp.{','.join(map(str, v))})" for k, v in s['markers'].items())
        out.append('- Provenance flags to classify: ' + (flags or '-'))
        out.append('- Code reason cards: step / reason / lines / provenance: ')
        out.append('')
    return '\n'.join(out)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('pdf')
    ap.add_argument('--roles', default=ROLES, help='comma-separated role labels before the bar')
    ap.add_argument('--marker', action='append', help='provenance marker text to count (repeatable)')
    ap.add_argument('--source-page-mark', action='append',
                    help='text that marks a page displaying the source itself; headings there are ignored '
                         '(default: 英語原文｜, Original page)')
    g = ap.add_mutually_exclusive_group()
    g.add_argument('--json', action='store_true')
    g.add_argument('--cards', action='store_true')
    a = ap.parse_args()
    markers = a.marker or MARKERS.split(',')
    subs = build(a.pdf, [r for r in a.roles.split(',') if r], markers,
                 a.source_page_mark or ['英語原文｜', 'Original page'])
    if a.json:
        print(json.dumps(subs, indent=2, ensure_ascii=False))
    elif a.cards:
        print(cards(subs))
    else:
        for s in subs:
            print(f"{s['id']} {s['title']}  pp.{s['first']}-{s['last']}  src {', '.join(s['source_pages']) or '-'}")
            for r in s['roles']:
                print(f"    p.{r['page']}  {r['role']} | {r['title']}")
            for k, v in s['markers'].items():
                print(f"    [{k}] x{sum(v.values())} on pp.{','.join(map(str, v))}")


if __name__ == '__main__':
    main()
