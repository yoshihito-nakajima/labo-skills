#!/usr/bin/env python3
"""Build a small, self-contained packet for one bounded unit of a long course.

A worker reads only the packet (the exact lines, the statements of every label they cite, and cached source text),
instead of opening whole chapter files. See ../references/token-budget.md.

  make_packet.py --root COURSE --file chapters/x.tex --lines 120-260 --out PACKET_DIR
                 [--kind math|verify|output|write] [--search 'chapters/*.tex']
                 [--source-cache CACHE --src SLUG:P1-P2 ...] [--role-card PATH] [--note TEXT]

Writes PACKET_DIR/{unit.tex,deps.tex,source/,manifest.json,request.md,SHA256SUMS}. Prints one summary line.
"""
from __future__ import annotations
import argparse, datetime, hashlib, json, pathlib, re, sys

STATEMENT_ENVS = 'theorem|lemma|proposition|corollary|definition|remark|example|exercise|assumption|notation|conjecture'
REF = re.compile(r'\\(?:c?ref|Cref|eqref|pageref|autoref)\*?\{([^}]+)\}')
LABEL = re.compile(r'\\label\{([^}]+)\}')
BEGIN = re.compile(r'\s*\\begin\{(%s)\*?\}' % STATEMENT_ENVS)
END = re.compile(r'\s*\\end\{(%s)\*?\}' % STATEMENT_ENVS)


def sha(p: pathlib.Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def statement_for(lines: list[str], i: int, back: int = 40, fwd: int = 60) -> tuple[int, int]:
    """Return (start, end) of the statement environment containing line i; the label line alone if none."""
    j = i
    while j >= 0 and i - j <= back and not BEGIN.match(lines[j]):
        if END.match(lines[j]) and j != i:
            return i, i
        j -= 1
    if j < 0 or i - j > back:
        return i, i
    k = i
    while k < len(lines) and k - i <= fwd and not END.match(lines[k]):
        k += 1
    return j, min(k, len(lines) - 1)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--root', required=True, type=pathlib.Path)
    ap.add_argument('--file', required=True)
    ap.add_argument('--lines', required=True)
    ap.add_argument('--out', required=True, type=pathlib.Path)
    ap.add_argument('--kind', default='math', choices=['math', 'verify', 'output', 'write'])
    ap.add_argument('--search', default='chapters/*.tex')
    ap.add_argument('--source-cache', type=pathlib.Path)
    ap.add_argument('--src', nargs='*', default=[])
    ap.add_argument('--role-card', default='')
    ap.add_argument('--note', default='')
    a = ap.parse_args(argv)
    src_file = a.root / a.file
    text = src_file.read_text(encoding='utf-8').split('\n')
    s, e = (int(x) for x in a.lines.split('-'))
    if not (1 <= s <= e <= len(text)):
        print(f'line range {s}-{e} outside 1-{len(text)}', file=sys.stderr)
        return 2
    out = a.out
    (out / 'source').mkdir(parents=True, exist_ok=True)
    unit = '\n'.join(text[s - 1:e])
    (out / 'unit.tex').write_text(unit, encoding='utf-8')
    wanted = {x.strip() for g in REF.findall(unit) for x in g.split(',')} - set(LABEL.findall(unit))
    deps = []
    for ch in sorted(a.root.glob(a.search)):
        lines = ch.read_text(encoding='utf-8', errors='ignore').split('\n')
        for i, line in enumerate(lines):
            for lab in LABEL.findall(line):
                if lab in wanted:
                    j, k = statement_for(lines, i)
                    deps.append(f'%% {lab}  ({ch.relative_to(a.root)}:{j + 1}-{k + 1})\n' + '\n'.join(lines[j:k + 1]))
                    wanted.discard(lab)
    missing = sorted(wanted)
    (out / 'deps.tex').write_text('\n\n'.join(deps) + (f'\n\n%% NOT FOUND: {", ".join(missing)}\n' if missing else '\n'),
                                  encoding='utf-8')
    copied = []
    for spec in a.src:
        if not a.source_cache:
            print('--src needs --source-cache', file=sys.stderr)
            return 2
        slug, _, rng = spec.partition(':')
        p1, _, p2 = rng.partition('-')
        for p in range(int(p1), int(p2 or p1) + 1):
            page = a.source_cache / slug / f'p{p:04d}.txt'
            if page.exists():
                dst = out / 'source' / f'{slug}-p{p:04d}.txt'
                dst.write_text(page.read_text(encoding='utf-8', errors='ignore'), encoding='utf-8')
                copied.append(dst.name)
    man = {'kind': a.kind, 'created': datetime.datetime.now().isoformat(timespec='seconds'),
           'file': a.file, 'lines': [s, e], 'file_sha256': sha(src_file), 'unit_sha256': sha(out / 'unit.tex'),
           'deps_found': len(deps), 'deps_missing': missing, 'source_pages': copied, 'note': a.note}
    (out / 'manifest.json').write_text(json.dumps(man, ensure_ascii=False, indent=1), encoding='utf-8')
    (out / 'request.md').write_text(
        f'# {out.name} ({a.kind})\n'
        f'Role card: {a.role_card or "(given by the coordinator)"} - read only this card and this packet.\n'
        f'Target: {a.file} L{s}-{e} (unit.tex, sha {man["unit_sha256"][:12]}; whole file sha {man["file_sha256"][:12]}).\n'
        f'Premises: deps.tex (statements of cited labels, no proofs). Missing: {", ".join(missing) or "none"}.\n'
        f'Source: source/ ({len(copied)} cached text pages). Open a page image only when its text is unreadable.\n'
        f'Write: results/report.md, then results/READY. Note: {a.note}\n', encoding='utf-8')
    files = sorted(p for p in out.rglob('*') if p.is_file() and p.name != 'SHA256SUMS' and 'results' not in p.parts)
    (out / 'SHA256SUMS').write_text(''.join(f'{sha(p)}  {p.relative_to(out)}\n' for p in files), encoding='utf-8')
    approx = sum(len(p.read_text(encoding='utf-8', errors='ignore')) for p in files) // 3
    print(f'{out} unit={man["unit_sha256"][:12]} deps={len(deps)} missing={len(missing)} src={len(copied)}p ~{approx // 1000}k tokens')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
