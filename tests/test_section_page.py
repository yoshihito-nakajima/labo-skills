"""Execution checks for the section-structured companion page, on the bundled fictional record.

Run with ``python3 -m unittest discover -s .agents/tests -p test_section_page.py``.
"""
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SKILL = Path(__file__).resolve().parents[1] / "skills/reading-proof-review"
EXAMPLE = SKILL / "assets/section-record/example.json"


def run(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, "-I", *args], capture_output=True, text=True)


class SectionPageTest(unittest.TestCase):
    def test_example_record_passes_the_checker(self):
        r = run(str(SKILL / "scripts/check_section_record.py"), str(EXAMPLE))
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("0 errors", r.stdout + r.stderr)

    def test_checker_rejects_a_broken_record(self):
        with tempfile.TemporaryDirectory() as d:
            rec = json.loads(EXAMPLE.read_text(encoding="utf-8"))
            rec["sections"][0].pop("question", None)
            rec["sections"][0].pop("answer", None)
            bad = Path(d) / "bad.json"
            bad.write_text(json.dumps(rec), encoding="utf-8")
            r = run(str(SKILL / "scripts/check_section_record.py"), str(bad))
            self.assertNotEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_builder_writes_page_and_tex_parts(self):
        with tempfile.TemporaryDirectory() as d:
            r = run(str(SKILL / "scripts/build_section_page.py"), str(EXAMPLE), "--out", d)
            self.assertEqual(r.returncode, 0, r.stderr)
            html = (Path(d) / "index.html").read_text(encoding="utf-8")
            self.assertIn("Introduction", html)
            self.assertTrue((Path(d) / "lang_defs.tex").exists())


if __name__ == "__main__":
    unittest.main()
