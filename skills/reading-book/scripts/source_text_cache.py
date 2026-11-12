#!/usr/bin/env python3
"""Extract source PDFs once into per-page text files, so workers read text slices instead of page images.

  source_text_cache.py --src-dir ORIGINALS --out-dir CACHE [--ocr] [--force] [NAME_SUBSTRING ...]

CACHE/<slug>/p0001.txt ... and CACHE/index.json (file, sha256, pages, pages without text).
--ocr runs tesseract (if installed) on pages whose text layer is empty. Needs pdfinfo/pdftotext (poppler).
The cache holds source text: keep it outside every Git repository, like the originals.
"""
from __future__ import annotations
import argparse, hashlib, json, pathlib, re, shutil, subprocess, tempfile


def slug(name: str) -> str:
    return re.sub(r'[^A-Za-z0-9]+', '-', pathlib.Path(name).stem).strip('-')[:60] or hashlib.sha1(name.encode()).hexdigest()[:10]


def page_count(pdf: pathlib.Path) -> int:
    m = re.search(r'Pages:\s+(\d+)', subprocess.run(['pdfinfo', str(pdf)], capture_output=True, text=True).stdout)
    return int(m.group(1)) if m else 0


def ocr_page(pdf: pathlib.Path, page: int) -> str:
    with tempfile.TemporaryDirectory() as d:
        subprocess.run(['pdftoppm', '-r', '200', '-gray', '-png', '-f', str(page), '-l', str(page), str(pdf), f'{d}/pg'],
                       capture_output=True)
        imgs = sorted(pathlib.Path(d).glob('pg*.png'))
        if not imgs:
            return ''
        subprocess.run(['tesseract', str(imgs[0]), f'{d}/out'], capture_output=True)
        out = pathlib.Path(d) / 'out.txt'
        return out.read_text(errors='ignore') if out.exists() else ''


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--src-dir', required=True, type=pathlib.Path)
    ap.add_argument('--out-dir', required=True, type=pathlib.Path)
    ap.add_argument('--ocr', action='store_true')
    ap.add_argument('--force', action='store_true')
    ap.add_argument('names', nargs='*')
    a = ap.parse_args(argv)
    a.out_dir.mkdir(parents=True, exist_ok=True)
    idx_path = a.out_dir / 'index.json'
    index = json.loads(idx_path.read_text()) if idx_path.exists() else {}
    can_ocr = a.ocr and shutil.which('tesseract') and shutil.which('pdftoppm')
    for pdf in sorted(a.src_dir.glob('*.pdf')):
        if a.names and not any(n in pdf.name for n in a.names):
            continue
        s, digest = slug(pdf.name), hashlib.sha256(pdf.read_bytes()).hexdigest()
        if not a.force and index.get(s, {}).get('sha256') == digest:
            continue
        d = a.out_dir / s
        d.mkdir(exist_ok=True)
        n = page_count(pdf)
        pages = subprocess.run(['pdftotext', '-layout', str(pdf), '-'], capture_output=True, text=True,
                               errors='ignore').stdout.split('\f')
        empty, ocred = [], []
        for i in range(1, n + 1):
            t = pages[i - 1] if i - 1 < len(pages) else ''
            if len(t.strip()) < 40 and can_ocr:
                t = ocr_page(pdf, i)
                ocred.append(i)
            if len(t.strip()) < 40:
                empty.append(i)
            (d / f'p{i:04d}.txt').write_text(t, encoding='utf-8')
        index[s] = {'file': pdf.name, 'sha256': digest, 'pages': n, 'ocr_pages': ocred, 'pages_without_text': empty}
        idx_path.write_text(json.dumps(index, ensure_ascii=False, indent=1), encoding='utf-8')
        print(f'{s}: {n} pages, {len(ocred)} OCR, {len(empty)} without text', flush=True)
    print(f'index: {len(index)} sources')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
