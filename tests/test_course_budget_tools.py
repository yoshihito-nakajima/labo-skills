"""Execution checks for the long-course budget helpers, on fictional data only.

Run with ``python3 -m unittest discover -s .agents/tests -p test_course_budget_tools.py``.
PDF cases need poppler (pdftotext, pdfinfo); they are skipped when it is missing.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

SKILLS = Path(__file__).resolve().parents[1] / "skills"
MAKE_PACKET = SKILLS / "reading-book/scripts/make_packet.py"
SOURCE_CACHE = SKILLS / "reading-book/scripts/source_text_cache.py"
OUTPUT_CHECK = SKILLS / "reading-book-output-review/scripts/output_check.py"


def text_pdf(path: Path, pages: list[str]) -> None:
    """Write a small valid PDF whose pages carry the given ASCII text in Helvetica."""
    objs = ["<< /Type /Catalog /Pages 2 0 R >>", None, "<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>"]
    kids = []
    for text in pages:
        stream = f"BT /F1 18 Tf 72 700 Td ({text}) Tj ET".encode()
        objs.append(f"<< /Length {len(stream)} >>\nstream\n{stream.decode()}\nendstream")
        objs.append(f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 3 0 R >> >> /Contents {len(objs)} 0 R >>")
        kids.append(f"{len(objs)} 0 R")
    objs[1] = f"<< /Type /Pages /Kids [{' '.join(kids)}] /Count {len(pages)} >>"
    out, offsets = b"%PDF-1.4\n", []
    for i, body in enumerate(objs, 1):
        offsets.append(len(out))
        out += f"{i} 0 obj\n{body}\nendobj\n".encode()
    xref = len(out)
    out += f"xref\n0 {len(objs) + 1}\n0000000000 65535 f \n".encode()
    out += "".join(f"{o:010d} 00000 n \n" for o in offsets).encode()
    out += f"trailer\n<< /Size {len(objs) + 1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n".encode()
    path.write_bytes(out)


def run(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, "-I", *args], capture_output=True, text=True)


COURSE = r"""\chapter{Toy}
\begin{definition}\label{def:toy}
A toy is a set with one point.
\end{definition}
\begin{proof}
hidden proof text that must not travel
\end{proof}
\begin{lemma}\label{lem:toy}
Every toy is finite.
\end{lemma}
\begin{proof}
By \cref{def:toy}. secret lemma proof
\end{proof}
\begin{theorem}\label{thm:main}
By \cref{lem:toy,def:toy} and \cref{lem:absent}, toys are compact.
\end{theorem}
"""


class MakePacketTest(unittest.TestCase):
    def test_packet_contains_unit_statements_and_missing_labels(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d) / "course"
            (root / "chapters").mkdir(parents=True)
            (root / "chapters/toy.tex").write_text(COURSE)
            cache = Path(d) / "cache/book"
            cache.mkdir(parents=True)
            (cache / "p0003.txt").write_text("Original page three.")
            out = Path(d) / "packet"
            r = run(str(MAKE_PACKET), "--root", str(root), "--file", "chapters/toy.tex", "--lines", "14-16",
                    "--out", str(out), "--kind", "verify", "--source-cache", str(Path(d) / "cache"), "--src", "book:3-4")
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertIn("thm:main", (out / "unit.tex").read_text())
            deps = (out / "deps.tex").read_text()
            self.assertIn("A toy is a set with one point.", deps)
            self.assertIn("Every toy is finite.", deps)
            self.assertNotIn("secret lemma proof", deps)
            self.assertNotIn("hidden proof text", deps)
            self.assertIn("NOT FOUND: lem:absent", deps)
            man = json.loads((out / "manifest.json").read_text())
            self.assertEqual(man["deps_missing"], ["lem:absent"])
            self.assertEqual(man["source_pages"], ["book-p0003.txt"])
            for line in (out / "SHA256SUMS").read_text().splitlines():
                digest, name = line.split("  ", 1)
                self.assertEqual(hashlib.sha256((out / name).read_bytes()).hexdigest(), digest)

    def test_rejects_range_outside_file(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "chapters").mkdir()
            (root / "chapters/toy.tex").write_text(COURSE)
            r = run(str(MAKE_PACKET), "--root", str(root), "--file", "chapters/toy.tex", "--lines", "10-999",
                    "--out", str(root / "p"))
            self.assertEqual(r.returncode, 2)


@unittest.skipUnless(shutil.which("pdftotext") and shutil.which("pdfinfo"), "poppler not installed")
class PdfToolsTest(unittest.TestCase):
    def test_source_cache_writes_pages_and_index(self):
        with tempfile.TemporaryDirectory() as d:
            src = Path(d) / "src"
            src.mkdir()
            text_pdf(src / "Toy Book.pdf", ["First page of the fictional book", "Second page text"])
            r = run(str(SOURCE_CACHE), "--src-dir", str(src), "--out-dir", str(Path(d) / "cache"))
            self.assertEqual(r.returncode, 0, r.stderr)
            idx = json.loads((Path(d) / "cache/index.json").read_text())
            self.assertEqual(idx["Toy-Book"]["pages"], 2)
            self.assertIn("Second page text", (Path(d) / "cache/Toy-Book/p0002.txt").read_text())
            again = run(str(SOURCE_CACHE), "--src-dir", str(src), "--out-dir", str(Path(d) / "cache"))
            self.assertNotIn("Toy-Book:", again.stdout)  # unchanged source is skipped

    def test_output_check_lists_changed_pages(self):
        with tempfile.TemporaryDirectory() as d:
            old, new = Path(d) / "old.pdf", Path(d) / "new.pdf"
            text_pdf(old, ["Alpha page", "Beta page", "Gamma page"])
            text_pdf(new, ["Alpha page", "Beta page revised", "Gamma page"])
            out = Path(d) / "out"
            r = run(str(OUTPUT_CHECK), "--pdf", str(new), "--previous", str(old), "--out", str(out))
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertEqual((out / "changed_pages.txt").read_text().split(), ["2"])
            self.assertTrue((out / "machine_report.txt").exists())
            self.assertFalse(list(out.glob("page-*.png")))  # nothing rendered unless asked


if __name__ == "__main__":
    unittest.main()
