from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from labo_tools.build import run_source_build, source_build_command  # noqa: E402
from labo_tools.paper import PaperError  # noqa: E402


class SourceBuildTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name).resolve()
        self.folder = self.root / "writing" / "sample-paper"
        self.folder.mkdir(parents=True)
        self.source = self.folder / "sample-paper_en.tex"
        self.source.write_text("\\documentclass{article}\n\\begin{document}\nExample.\\end{document}\n")

    def test_imported_layout_honors_workspace_config_without_moving_sources(self):
        (self.root / ".latexmkrc").write_text("$pdf_mode = 3;\n")
        command, cwd, cache, output, stem = source_build_command(self.root, self.source)
        self.assertEqual(cwd, self.root)
        self.assertEqual(cache, self.folder / ".temp")
        self.assertEqual(output, self.root / "output")
        self.assertEqual(stem, "sample-paper_en")
        self.assertFalse(any(x in command for x in ("-pdf", "-lualatex", "-xelatex")))
        self.assertIn(str(self.source), command)
        self.assertFalse(cache.exists())

    def test_engine_directive_and_xecjk_take_priority_over_fontspec(self):
        self.source.write_text("\\documentclass{beamer}\n\\usepackage{fontspec,xeCJK}\n\\begin{document}\n")
        self.assertIn("-xelatex", source_build_command(self.root, self.source)[0])
        self.source.write_text("% !TeX program = lualatex\n" + self.source.read_text())
        self.assertIn("-lualatex", source_build_command(self.root, self.source)[0])
        self.assertIn("-xelatex", source_build_command(self.root, self.source, "xelatex")[0])

    def test_standard_main_keeps_paper_job_name_and_local_include_directory(self):
        main = self.folder / "main.tex"
        main.write_text(self.source.read_text())
        command, cwd, _, output, stem = source_build_command(self.root, main)
        self.assertEqual(cwd, self.folder)
        self.assertEqual(stem, "sample-paper")
        self.assertIn(f"-outdir={output}", command)

    def test_generic_entry_names_do_not_collide_across_papers(self):
        for slug in ("first-paper", "second-paper"):
            source = self.root / "writing" / slug / "talk.tex"
            source.parent.mkdir()
            source.write_text(self.source.read_text())
            self.assertEqual(source_build_command(self.root, source)[-1], f"{slug}-talk")

    def test_section_and_outside_workspace_sources_are_rejected(self):
        section = self.folder / "section.tex"
        section.write_text("\\section{Example}\n")
        with self.assertRaisesRegex(PaperError, "document root"):
            source_build_command(self.root, section)
        with self.assertRaisesRegex(PaperError, "inside the workspace"):
            source_build_command(self.root / "another-workspace", self.source)

    def test_build_failure_preserves_previously_published_pair(self):
        output = self.root / "output"
        output.mkdir()
        pdf = output / "sample-paper.pdf"
        sync = output / "sample-paper.synctex.gz"
        pdf.write_bytes(b"previous PDF")
        sync.write_bytes(b"previous SyncTeX")
        with patch("labo_tools.build.subprocess.run"):
            with self.assertRaisesRegex(PaperError, "output PDF"):
                run_source_build(self.root, self.source, None, False)
        self.assertEqual(pdf.read_bytes(), b"previous PDF")
        self.assertEqual(sync.read_bytes(), b"previous SyncTeX")

    def test_build_publishes_pdf_and_synctex_but_leaves_auxiliary_files_in_cache(self):
        def build(command, **kwargs):
            cache = self.folder / ".temp"
            (cache / "sample-paper_en.pdf").write_bytes(b"new PDF")
            (cache / "sample-paper_en.synctex.gz").write_bytes(b"new SyncTeX")
            (cache / "sample-paper_en.aux").write_bytes(b"auxiliary data")
        with patch("labo_tools.build.subprocess.run", side_effect=build):
            run_source_build(self.root, self.source, None, False)
        self.assertEqual(
            sorted(p.name for p in (self.root / "output").iterdir()),
            ["sample-paper.pdf", "sample-paper.synctex.gz"],
        )
        self.assertTrue((self.folder / ".temp/sample-paper_en.aux").exists())


if __name__ == "__main__":
    unittest.main()
