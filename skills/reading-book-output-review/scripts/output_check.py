#!/usr/bin/env python3
"""Machine-first output check for a frozen course PDF; page images only on request.

  output_check.py --pdf PDF --out DIR [--previous OLD_PDF] [--log MAIN_LOG] [--check-cmd CMD] [--render N] [--dpi 60]

Runs qpdf, scans the TeX log, runs mathematical-navigation's check_pdf.py (with --previous when given), lists pages
whose text changed against the previous PDF, and renders at most N changed pages at low resolution.
Writes DIR/machine_report.txt (printed) and DIR/changed_pages.txt. Never modifies the PDF or any source.
"""
from __future__ import annotations
import argparse, hashlib, json, pathlib, re, shlex, shutil, subprocess

CHECK_PDF = pathlib.Path(__file__).resolve().parents[2] / 'mathematical-navigation/scripts/check_pdf.py'


def run(cmd: list[str] | str, shell: bool = False) -> tuple[int, str]:
    r = subprocess.run(cmd, shell=shell, capture_output=True, text=True, errors='ignore')
    return r.returncode, (r.stdout + r.stderr)


def page_texts(pdf: str) -> list[str]:
    return subprocess.run(['pdftotext', '-layout', pdf, '-'], capture_output=True, text=True, errors='ignore').stdout.split('\f')


def changed_pages(pdf: str, previous: str) -> list[int]:
    old = {hashlib.sha1(t.encode()).hexdigest() for t in page_texts(previous)}
    return [i + 1 for i, t in enumerate(page_texts(pdf)) if t.strip() and hashlib.sha1(t.encode()).hexdigest() not in old]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--pdf', required=True)
    ap.add_argument('--out', required=True, type=pathlib.Path)
    ap.add_argument('--previous')
    ap.add_argument('--log', type=pathlib.Path)
    ap.add_argument('--check-cmd', help='optional storage/build check command, e.g. book_materials.py check ...')
    ap.add_argument('--render', type=int, default=0)
    ap.add_argument('--dpi', type=int, default=60)
    a = ap.parse_args(argv)
    a.out.mkdir(parents=True, exist_ok=True)
    rep = [f'pdf: {a.pdf} sha256 {hashlib.sha256(pathlib.Path(a.pdf).read_bytes()).hexdigest()}']
    if a.check_cmd:
        rc, _ = run(shlex.split(a.check_cmd))
        rep.append(f'check-cmd exit {rc}')
    if shutil.which('qpdf'):
        rc, out = run(['qpdf', '--check', a.pdf])
        rep.append(f'qpdf exit {rc}: {out.strip().splitlines()[-1] if out.strip() else ""}')
    if a.log and a.log.exists():
        log = a.log.read_text(errors='ignore')
        rep.append('log: undefined refs {}, undefined cites {}, overfull {}, multiply defined {}'.format(
            len(re.findall(r'Reference .* undefined', log)), len(re.findall(r'Citation .* undefined', log)),
            log.count('Overfull'), log.count('multiply defined')))
    cmd = ['python3', str(CHECK_PDF), a.pdf, '--report', str(a.out / 'check_pdf.json')]
    if a.previous:
        cmd += ['--previous', a.previous]
    rc, _ = run(cmd)
    rep.append(f'check_pdf.py exit {rc}: {a.out / "check_pdf.json"}')
    try:
        data = json.loads((a.out / 'check_pdf.json').read_text())
        findings = data.get('findings', [])
        rep.append(f'  findings: {len(findings)}')
        rep += [f'   - {json.dumps(f, ensure_ascii=False)[:200]}' for f in findings[:15]]
    except Exception as exc:  # report stays usable even if the checker failed
        rep.append(f'  report not parsed: {exc}')
    if a.previous and shutil.which('pdftotext'):
        ch = changed_pages(a.pdf, a.previous)
        (a.out / 'changed_pages.txt').write_text(' '.join(map(str, ch)))
        rep.append(f'changed pages vs previous: {len(ch)}: {ch[:40]}')
        for p in ch[:max(a.render, 0)]:
            run(['pdftoppm', '-r', str(a.dpi), '-png', '-f', str(p), '-l', str(p), a.pdf, str(a.out / f'page-{p}')])
            rep.append(f'  rendered page {p} at {a.dpi} dpi')
    (a.out / 'machine_report.txt').write_text('\n'.join(rep) + '\n')
    print('\n'.join(rep))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
