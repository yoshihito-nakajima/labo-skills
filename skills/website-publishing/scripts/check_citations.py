#!/usr/bin/env python3
"""Check that every numbered citation on a Markdown page resolves to a reference entry.

  check_citations.py PAGE.md [PAGE.md ...] [--previous OLD.md | --previous-rev REV]

A citation is a bracketed number not used as a link label, e.g. "[8]", "[8, Theorem 6.22]",
"[4, §8]" or "[1, 3]". A reference entry is a line starting with "[n]" or "- [n]" (also
"n. " inside a section headed 参考文献/References/文献/Bibliography).

Reports, per page: citations with no entry (dangling), entries never cited (unused, a
warning), and, with --previous / --previous-rev, entries present in the earlier version but
missing now (dropped). --previous-rev REV reads each page at REV from Git (run inside the
repository). Exit 1 if any page has dangling citations or dropped entries.
"""
import argparse, re, subprocess, sys
from pathlib import Path

CITE = re.compile(r'(?<![\\!\]])\[(\d+(?:\s*[,–-]\s*\d+)*)(?:\s*,\s*[^\]\[]*)?\](?![(\[:])')
ENTRY = re.compile(r'^\s*(?:[-*]\s*)?\[(\d+)\]\s+\S')
HEAD = re.compile(r'^#+\s*(参考文献|文献|References|Bibliography)\b', re.I)
NUMBERED = re.compile(r'^\s*(\d+)\.\s+\S')
FENCE = re.compile(r'^\s*(```|~~~)')


def numbers(group):
    out = set()
    for part in re.split(r'\s*,\s*', group):
        m = re.match(r'(\d+)\s*[–-]\s*(\d+)$', part)
        if m and int(m.group(2)) - int(m.group(1)) < 50:
            out.update(range(int(m.group(1)), int(m.group(2)) + 1))
        elif part.isdigit():
            out.add(int(part))
    return out


def scan(text):
    cites, entries, in_bib, in_code, in_math = {}, set(), False, False, False
    for no, line in enumerate(text.splitlines(), 1):
        if FENCE.match(line):
            in_code = not in_code
            continue
        if in_code:
            continue
        parts = line.split('$$')
        if in_math or len(parts) > 1:  # drop display math, possibly spanning lines
            kept = [seg for i, seg in enumerate(parts) if (i % 2 == 0) != in_math]
            in_math = in_math != (len(parts) % 2 == 0)
            line = ' '.join(kept)
        if line.startswith('#'):
            in_bib = bool(HEAD.match(line))
        m = ENTRY.match(line) or (in_bib and NUMBERED.match(line))
        if m:
            entries.add(int(m.group(1)))
            continue
        body = re.sub(r'\$[^$]*\$', '', line)  # skip inline math such as $[0,1]$
        for c in CITE.finditer(body):
            for n in numbers(c.group(1)) - {0}:
                cites.setdefault(n, no)
    return cites, entries


def previous_text(page, a):
    if a.previous:
        return Path(a.previous).read_text(encoding='utf-8')
    if a.previous_rev:
        root = subprocess.run(['git', 'rev-parse', '--show-toplevel'], capture_output=True, text=True).stdout.strip()
        rel = Path(page).resolve().relative_to(Path(root).resolve())
        r = subprocess.run(['git', 'show', f'{a.previous_rev}:{rel.as_posix()}'], capture_output=True, text=True)
        return r.stdout if r.returncode == 0 else None
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('pages', nargs='+')
    g = ap.add_mutually_exclusive_group()
    g.add_argument('--previous')
    g.add_argument('--previous-rev')
    a = ap.parse_args()
    if a.previous and len(a.pages) != 1:
        ap.error('--previous takes exactly one page')
    bad = False
    for page in a.pages:
        cites, entries = scan(Path(page).read_text(encoding='utf-8'))
        dangling = sorted(n for n in cites if n not in entries)
        unused = sorted(entries - set(cites))
        lines = []
        if dangling:
            lines.append('  dangling: ' + ', '.join(f'[{n}] (line {cites[n]})' for n in dangling))
        if unused:
            lines.append('  unused (warning): ' + ', '.join(f'[{n}]' for n in unused))
        old = previous_text(page, a)
        if old is not None:
            dropped = sorted(scan(old)[1] - entries)
            if dropped:
                lines.append('  dropped since previous: ' + ', '.join(f'[{n}]' for n in dropped))
                bad = True
        bad = bad or bool(dangling)
        print(f'{page}: {len(cites)} cited, {len(entries)} entries' + (' — ok' if not lines else ''))
        print('\n'.join(lines)) if lines else None
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
