#!/usr/bin/env python3
"""Download a pinned KaTeX release (MIT licence) into a local cache so the review page can inline it.

Usage: fetch_katex.py [--dest DIR] [--url URL --sha512 INTEGRITY]

The default is the official npm tarball of a pinned version, verified against its published sha512
integrity before anything is unpacked. Only katex.min.js, katex.min.css, the .woff2 fonts and the
licence file are extracted, each to a fixed name inside DEST (no member path is trusted). Nothing is
installed system-wide and nothing is bundled into this skill. The cache directory is the default
place `build_review_page.py` looks in.
"""
import argparse
import base64
import hashlib
import io
import pathlib
import sys
import tarfile
import urllib.request

VERSION = "0.19.1"
URL = f"https://registry.npmjs.org/katex/-/katex-{VERSION}.tgz"
INTEGRITY = "sha512-jG8uKntjSEcm2EpQOh0XturpPuuC9r3Sq5HLHdsFdWZT27E672SF19QEi+of0/YeOy15lDgRhKvr5614uRrEfA=="


def default_dest():
    return pathlib.Path.home() / ".cache" / "labo-skills" / "katex" / VERSION


def integrity(data):
    return "sha512-" + base64.b64encode(hashlib.sha512(data).digest()).decode()


def unpack(data, dest):
    """Extract the wanted files by fixed names; refuse anything else. Returns the list written."""
    dest = pathlib.Path(dest)
    (dest / "fonts").mkdir(parents=True, exist_ok=True)
    wanted = {"package/dist/katex.min.js": "katex.min.js", "package/dist/katex.min.css": "katex.min.css", "package/LICENSE": "LICENSE"}
    written = []
    with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as t:
        for m in t.getmembers():
            if not m.isfile():
                continue
            if m.name in wanted:
                target = dest / wanted[m.name]
            elif m.name.startswith("package/dist/fonts/") and m.name.endswith(".woff2") and "/" not in m.name[len("package/dist/fonts/"):]:
                target = dest / "fonts" / m.name.rsplit("/", 1)[1]
            else:
                continue
            target.write_bytes(t.extractfile(m).read())
            written.append(target.name)
    missing = [w for w in ("katex.min.js", "katex.min.css") if w not in written]
    if missing:
        raise SystemExit("archive lacks " + ", ".join(missing))
    return written


def fetch(dest=None, url=URL, expected=INTEGRITY):
    dest = pathlib.Path(dest) if dest else default_dest()
    if (dest / "katex.min.js").exists() and (dest / "katex.min.css").exists():
        return dest
    with urllib.request.urlopen(url, timeout=60) as r:
        data = r.read()
    got = integrity(data)
    if got != expected:
        raise SystemExit(f"integrity mismatch: expected {expected}, got {got}; nothing was unpacked")
    unpack(data, dest)
    return dest


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dest")
    ap.add_argument("--url", default=URL)
    ap.add_argument("--sha512", default=INTEGRITY, help="expected integrity string (sha512-...) for --url")
    a = ap.parse_args(argv)
    dest = fetch(a.dest, a.url, a.sha512)
    print(dest)
    return 0


if __name__ == "__main__":
    sys.exit(main())
