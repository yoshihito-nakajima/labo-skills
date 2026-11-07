#!/usr/bin/env python3
"""Extract functions from a Python file for a slide listing, verbatim except that
docstrings are dropped, and optionally append numbered markers at chosen lines.

  extract_code.py SOURCE.py --functions f,g --out out.py \
      [--mark 5:1:'dist <= radius' --mark 9:2:'fill_diagonal'] [--ascii]
  extract_code.py SOURCE.py --lines 280-291 --dedent --out excerpt.py [--mark ...]

--lines A-B takes that verbatim line range of the source (comments kept), for an
excerpt of someone else's published code; several ranges `A-B,C,D-E` are joined by a
gap line (--gap, default `...`); --dedent removes the common indentation of each range separately.

--mark LINE:NUMBER:SUBSTRING[:ROLE] appends a marker NUMBER after line LINE (1-based,
counted in the extracted output) and fails if that line does not contain SUBSTRING, so a
legend written for the old code cannot silently describe changed code. ROLE is one of
fix, aim, inherited, forward, tidy (default fix): the marker is written as a listings escape
`(*@\\mkr{ROLE}{NUMBER}@*)`; a tidy line is wrapped in `@!...!@` (dimmed by the listing style, up to --comment if given, because a listing comment would swallow the closing delimiter) and not numbered. The clean text
without markers is written to OUT with the suffix `.clean`. The report prints the source line ranges, to
be quoted in the source tag, and never a line count to be used in a title.
"""
import argparse, ast, sys
from pathlib import Path


def extract(src_path, names):
    text = Path(src_path).read_text()
    lines = text.splitlines()
    funcs = {n.name: n for n in ast.parse(text).body if isinstance(n, ast.FunctionDef)}
    parts, ranges = [], []
    for name in names:
        if name not in funcs:
            sys.exit(f'function not found: {name}')
        n = funcs[name]
        keep = list(range(n.lineno - 1, n.end_lineno))
        b = n.body[0]
        if isinstance(b, ast.Expr) and isinstance(getattr(b, 'value', None), ast.Constant) and isinstance(b.value.value, str):
            drop = set(range(b.lineno - 1, b.end_lineno))
            keep = [i for i in keep if i not in drop]
        parts.append('\n'.join(lines[i] for i in keep))
        ranges.append((name, n.lineno, n.end_lineno))
    return '\n\n'.join(parts) + '\n', ranges


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('source'); ap.add_argument('--functions'); ap.add_argument('--lines'); ap.add_argument('--comment', default='', help='comment character (e.g. %% or #): a tidy line is dimmed only up to it'); ap.add_argument('--gap', default='...'); ap.add_argument('--dedent', action='store_true'); ap.add_argument('--out', required=True)
    ap.add_argument('--mark', action='append', default=[]); ap.add_argument('--ascii', action='store_true')
    a = ap.parse_args()
    if a.lines:
        import textwrap
        allsrc = Path(a.source).read_text().splitlines()
        pieces, ranges = [], []
        for part in a.lines.split(','):
            lo, _, hi = part.partition('-')
            lo, hi = int(lo), int(hi or lo)
            pieces.append(allsrc[lo - 1:hi]); ranges.append(('lines', lo, hi))
        flat = []
        for k, piece in enumerate(pieces):
            if k:
                flat.append(a.gap)
            flat += (textwrap.dedent('\n'.join(piece)).split('\n') if a.dedent else piece)
        code = '\n'.join(flat) + '\n'
        ranges = ranges
    elif a.functions:
        code, ranges = extract(a.source, a.functions.split(','))
    else:
        sys.exit('give --functions or --lines')
    if a.ascii and not code.isascii():
        sys.exit('non-ASCII characters in the extracted code')
    out = code.splitlines()
    marked = list(out)
    ROLES = ('fix', 'aim', 'inherited', 'forward', 'tidy')
    for spec in a.mark:
        parts = spec.split(':')
        role = 'fix'
        if len(parts) >= 4 and parts[-1] in ROLES:
            role = parts.pop()
        line, num, sub = parts[0], parts[1], ':'.join(parts[2:])
        i = int(line) - 1
        if not (0 <= i < len(out)) or sub not in out[i]:
            sys.exit(f'mark {spec!r}: line {line} is {out[i] if 0 <= i < len(out) else None!r}')
        if role == 'tidy':
            line_text = marked[i]
            cut = line_text.find(a.comment) if a.comment else -1
            code_part, tail = (line_text[:cut], line_text[cut:]) if cut > 0 else (line_text, '')
            marked[i] = '@!' + code_part.rstrip() + '!@' + (' ' + tail if tail else '')
        else:
            mk = f'(*@\\mkr{{{role}}}{{{num}}}@*)'
            cut = marked[i].find(a.comment) if a.comment else -1
            marked[i] = (marked[i][:cut].rstrip() + mk + ' ' + marked[i][cut:]) if cut > 0 else marked[i] + mk
    Path(a.out).write_text('\n'.join(marked) + '\n')
    Path(a.out + '.clean').write_text(code)
    print('source ranges:', '; '.join(f'{n}: L{s}-{e}' for n, s, e in ranges))


if __name__ == '__main__':
    main()
