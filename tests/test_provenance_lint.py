"""Execute provenance_lint.py on small fictional files."""

from pathlib import Path
import json
import subprocess
import sys
import tempfile
import unittest

LINT = Path(__file__).resolve().parents[1] / "skills/reading-reference/scripts/provenance_lint.py"


class ProvenanceLintTests(unittest.TestCase):
    def run_lint(self, *args):
        return subprocess.run([sys.executable, str(LINT), *args], capture_output=True, text=True)

    def test_finds_english_and_japanese_self_attribution(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "notes.tex").write_text("この図は自作のコードで描いた。\n")
            (root / "impl.py").write_text("x = 1  # the coefficient is our stated setting\n")
            (root / "talk.tex").write_text("How do we get a global map?\n")
            (root / "fine.py").write_text("x = 2  # AI-created teaching code\n")
            result = self.run_lint(str(root), "--json")
            self.assertEqual(result.returncode, 1)
            hits = json.loads(result.stdout)
            self.assertEqual(sorted(Path(h["file"]).name for h in hits), ["impl.py", "notes.tex"])
            broad = json.loads(self.run_lint(str(root), "--broad", "--json").stdout)
            self.assertIn("talk.tex", [Path(h["file"]).name for h in broad])

    def test_ignore_marker_and_excluded_paths_are_skipped(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "quote.tex").write_text("The authors write: we prove. % provenance-lint: ignore\n")
            source = root / "source"
            source.mkdir()
            (source / "original.tex").write_text("In this paper we show the result.\n")
            result = self.run_lint(str(root), "--exclude", "*/source/*")
            self.assertEqual(result.returncode, 0, result.stdout)


if __name__ == "__main__":
    unittest.main()
