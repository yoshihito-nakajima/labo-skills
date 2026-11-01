"""Exact prefix bytes through real pipes and a Windows-like text wrapper."""

from contextlib import redirect_stdout
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from labo_tools.cli import main  # noqa: E402
from labo_tools.reader import start_reading  # noqa: E402


PROJECT = Path(__file__).resolve().parents[1]
SOURCE = "writing/example/source.tex"
SESSION = "reviews/reader.json"
PREFIX = "Visible α.\r\nVisible β.\n".encode("utf-8")


class ReaderCliByteTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        source = self.root / SOURCE
        source.parent.mkdir(parents=True)
        source.write_bytes(PREFIX + b"WITHHELD_SENTINEL\n")
        (self.root / "reviews").mkdir()
        start_reading(self.root, SOURCE, SESSION, "Synthetic reader")

    def arguments(self):
        return ["paper", "reading", "next", "--session", SESSION, "--through-line", "2",
                "--workspace", str(self.root)]

    def test_real_cli_pipe_preserves_mixed_line_endings_and_utf8(self):
        result = subprocess.run([sys.executable, "-B", "-I", str(PROJECT / "scripts/labo.py"),
                                 *self.arguments()], capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, PREFIX)

    def test_windows_style_stdout_translation_cannot_corrupt_prefix(self):
        buffer = io.BytesIO()
        wrapper = io.TextIOWrapper(buffer, encoding="utf-8", newline="\r\n")
        with redirect_stdout(wrapper):
            code = main(self.arguments())
        wrapper.flush()
        self.assertEqual(code, 0)
        self.assertEqual(buffer.getvalue(), PREFIX)

    def test_structured_output_is_utf8_even_with_ascii_text_wrapper(self):
        buffer = io.BytesIO()
        wrapper = io.TextIOWrapper(buffer, encoding="ascii", newline="\r\n")
        with redirect_stdout(wrapper):
            code = main([*self.arguments(), "--format", "json"])
        wrapper.flush()
        self.assertEqual(code, 0)
        result = json.loads(buffer.getvalue().decode("utf-8"))
        self.assertEqual(result["text"].encode("utf-8"), PREFIX)


if __name__ == "__main__":
    unittest.main()
