#!/usr/bin/env python3
"""Find self-attribution in material that contains AI-created parts.

Scans the given files or directories (TeX, Markdown, Python, MATLAB, R, Julia, JSON,
C/C++) for words that present AI-created code, figures or text as the writer's own: "our/my"
near a word for code, experiments, figures or settings, "we wrote/ran/computed...",
"own code", 自作, 自前, 我々の, 私たちの. `--broad` also reports every bare our/we/my
(useful for code comments; too noisy for talk prose, where "how do we..." is normal). Replace each hit with the
provenance class (for example "AI-created"); see reading-reference source rules R5a.

  provenance_lint.py PATH... [--term REGEX ...] [--exclude GLOB ...] [--json]

Text inside \\begin{quote}...\\end{quote} (quoted sources) and lines containing
`provenance-lint: ignore` are skipped (for example a line that quotes a
source's own "we"). Quoted sources should be excluded by path (--exclude) rather than
line by line. Exit status 1 when anything is found, 0 otherwise.
"""
import argparse, fnmatch, json, re, sys
from pathlib import Path

SUFFIXES = {'.tex', '.md', '.py', '.m', '.r', '.R', '.jl', '.json', '.c', '.cc', '.cpp', '.h', '.sty', '.txt'}
WORK = r'(?:code|implementation|program|script|experiment|figure|plot|computation|calculation|setting|choice|example|demonstration|kernel|run|result|version|own)s?'
DEFAULT_TERMS = [
    r'\b(?:our|my)\s+(?:\w+\s+){0,2}' + WORK + r'\b',          # "our stated setting", "my own code"
    r'\bwe\s+(?:wrote|implemented|coded|ran|computed|made|built|programmed)\b',
    r'\bown\s+(?:code|implementation|experiment|figure)s?\b',
    r'自作', r'自前', r'我々の', r'私たちの',
]
BROAD_TERMS = [r'\b(?:our|ours|we|my)\b', r'自作', r'自前', r'我々の', r'私たちの']
IGNORE = 'provenance-lint: ignore'
QUOTE = re.compile(r'\\+begin\{quote\}.*?\\+end\{quote\}', re.S)


def files(paths, excludes):
    for path in paths:
        path = Path(path)
        candidates = [path] if path.is_file() else sorted(p for p in path.rglob('*') if p.is_file())
        for p in candidates:
            if p.suffix not in SUFFIXES:
                continue
            if any(fnmatch.fnmatch(str(p), g) or fnmatch.fnmatch(p.name, g) for g in excludes):
                continue
            yield p


def scan(paths, terms, excludes):
    pattern = re.compile('|'.join(f'(?:{t})' for t in terms), re.IGNORECASE)
    hits = []
    for p in files(paths, excludes):
        try:
            text = p.read_text(encoding='utf-8')
        except UnicodeDecodeError:
            continue
        # Quotations of sources keep their authors' "we"; blank them, keeping line numbers.
        text = QUOTE.sub(lambda m: re.sub(r'[^\n]', ' ', m.group(0)), text)
        for no, line in enumerate(text.splitlines(), 1):
            if IGNORE in line:
                continue
            for m in pattern.finditer(line):
                hits.append({'file': str(p), 'line': no, 'term': m.group(0), 'text': line.strip()[:160]})
    return hits


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('paths', nargs='+')
    ap.add_argument('--term', action='append', help='regular expression to search (replaces the defaults)')
    ap.add_argument('--exclude', action='append', default=[], help='path or file-name glob to skip')
    ap.add_argument('--broad', action='store_true', help='report every bare our/ours/we/my as well')
    ap.add_argument('--json', action='store_true')
    a = ap.parse_args()
    hits = scan(a.paths, a.term or (BROAD_TERMS if a.broad else DEFAULT_TERMS), a.exclude)
    if a.json:
        print(json.dumps(hits, ensure_ascii=False, indent=2))
    else:
        for h in hits:
            print(f"{h['file']}:{h['line']}: {h['term']}: {h['text']}")
        print(f'{len(hits)} self-attribution hit(s)', file=sys.stderr)
    return 1 if hits else 0


if __name__ == '__main__':
    sys.exit(main())
