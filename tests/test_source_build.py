from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import json  # noqa: E402

from labo_tools.build import (  # noqa: E402
    record_postprocess, run_postprocess, run_source_build, source_build_command, verify_current,
)
from labo_tools.paper import PaperError  # noqa: E402


class SourceBuildTests(unittest.TestCase):
    def setUp(self):
        audit = patch("labo_tools.build.check_navigation")
        self.audit = audit.start()
        self.addCleanup(audit.stop)
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
        self.audit.assert_called_once_with(
            self.root / "output/sample-paper.pdf", self.folder / ".temp", "sample-paper_en",
            self.folder / ".temp/sample-paper_en.aux",
            source=self.source,
        )


    def _successful_build(self):
        def build(command, **kwargs):
            cache = self.folder / ".temp"
            (cache / "sample-paper_en.pdf").write_bytes(b"new PDF")
            (cache / "sample-paper_en.synctex.gz").write_bytes(b"new SyncTeX")
        with patch("labo_tools.build.subprocess.run", side_effect=build):
            run_source_build(self.root, self.source, None, False)

    def test_successful_build_records_a_stamp_that_verify_current_accepts(self):
        self._successful_build()
        record = json.loads((self.folder / ".temp/sample-paper.build.json").read_text())
        self.assertEqual(record["status"], "ok")
        ok, message = verify_current(self.root, source=self.source)
        self.assertTrue(ok, message)

    def test_failed_build_marks_the_kept_pdf_as_stale(self):
        self._successful_build()
        with patch("labo_tools.build.subprocess.run"):
            (self.folder / ".temp/sample-paper_en.pdf").unlink()
            with self.assertRaises(PaperError):
                run_source_build(self.root, self.source, None, False)
        self.assertEqual((self.root / "output/sample-paper.pdf").read_bytes(), b"new PDF")
        ok, message = verify_current(self.root, source=self.source)
        self.assertFalse(ok)
        self.assertIn("stale", message)

    def test_another_source_in_same_folder_cannot_reuse_the_build_record(self):
        self._successful_build()
        other = self.source.with_name("another.tex")
        other.write_text(self.source.read_text())
        ok, message = verify_current(self.root, source=other)
        self.assertFalse(ok)
        self.assertIn("different source", message)
        ok, message = verify_current(self.root, source=self.source.relative_to(self.root))
        self.assertTrue(ok, message)

    def test_replaced_pdf_is_not_the_current_build(self):
        self._successful_build()
        (self.root / "output/sample-paper.pdf").write_bytes(b"some other PDF")
        ok, message = verify_current(self.root, source=self.source)
        self.assertFalse(ok)
        self.assertIn("differs", message)

    def test_recorded_postprocessing_keeps_the_pdf_current_only_after_success(self):
        self._successful_build()
        (self.root / "output/sample-paper.pdf").write_bytes(b"normalized PDF")
        record_postprocess(self.root, "normalize_pdf.py", source=self.source)
        ok, message = verify_current(self.root, source=self.source)
        self.assertTrue(ok, message)
        with patch("labo_tools.build.subprocess.run"):
            (self.folder / ".temp/sample-paper_en.pdf").unlink()
            with self.assertRaises(PaperError):
                run_source_build(self.root, self.source, None, False)
        with self.assertRaisesRegex(PaperError, "failed"):
            record_postprocess(self.root, "normalize_pdf.py", source=self.source)

    def test_postprocess_option_runs_and_records_each_step(self):
        self._successful_build()
        step = f"{Path(sys.executable).as_posix()} -c \"open('output/sample-paper.pdf','wb').write(b'normalized')\""
        run_postprocess(self.root, [step], source=self.source)
        self.assertEqual((self.root / "output/sample-paper.pdf").read_bytes(), b"normalized")
        ok, message = verify_current(self.root, source=self.source)
        self.assertTrue(ok, message)
        record = json.loads((self.folder / ".temp/sample-paper.build.json").read_text())
        self.assertEqual(record["postprocessed"][0]["step"], step)

    def test_failing_postprocess_makes_the_pdf_not_current(self):
        self._successful_build()
        with self.assertRaisesRegex(PaperError, "post-processing failed"):
            run_postprocess(self.root, [f"{sys.executable} -c \"raise SystemExit(3)\""], source=self.source)
        ok, message = verify_current(self.root, source=self.source)
        self.assertFalse(ok)
        self.assertIn("post-processing failed", message)

    def test_no_record_means_not_verified(self):
        ok, message = verify_current(self.root, source=self.source)
        self.assertFalse(ok)
        self.assertIn("build first", message)


if __name__ == "__main__":
    unittest.main()
