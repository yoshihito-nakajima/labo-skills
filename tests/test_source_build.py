from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import json  # noqa: E402

from labo_tools.build import (  # noqa: E402
    copy_html, record_postprocess, run_postprocess, run_source_build, source_build_command, verify_current,
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
        pdf = output / "sample-paper_en.pdf"
        sync = output / "sample-paper_en.synctex.gz"
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
            ["sample-paper_en.pdf", "sample-paper_en.synctex.gz"],
        )
        self.assertTrue((self.folder / ".temp/sample-paper_en.aux").exists())
        self.audit.assert_called_once_with(
            self.root / "output/sample-paper_en.pdf", self.folder / ".temp", "sample-paper_en",
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
        record = json.loads((self.folder / ".temp/sample-paper_en.build.json").read_text())
        self.assertEqual(record["status"], "ok")
        ok, message = verify_current(self.root, source=self.source)
        self.assertTrue(ok, message)

    def test_failed_build_marks_the_kept_pdf_as_stale(self):
        self._successful_build()
        with patch("labo_tools.build.subprocess.run"):
            (self.folder / ".temp/sample-paper_en.pdf").unlink()
            with self.assertRaises(PaperError):
                run_source_build(self.root, self.source, None, False)
        self.assertEqual((self.root / "output/sample-paper_en.pdf").read_bytes(), b"new PDF")
        ok, message = verify_current(self.root, source=self.source)
        self.assertFalse(ok)
        self.assertIn("stale", message)

    def test_another_source_in_same_folder_cannot_reuse_the_build_record(self):
        # Two roots whose job names coincide share one output name; the record belongs to the one built.
        self.source.unlink()
        self.source = self.folder / "sample-paper-talk.tex"
        self.source.write_text("\\documentclass{article}\n\\begin{document}\nExample.\\end{document}\n")
        (self.root / "output").mkdir(exist_ok=True)

        def build(command, **kwargs):
            cache = self.folder / ".temp"
            (cache / "sample-paper-talk.pdf").write_bytes(b"new PDF")
            (cache / "sample-paper-talk.synctex.gz").write_bytes(b"new SyncTeX")
        with patch("labo_tools.build.subprocess.run", side_effect=build):
            run_source_build(self.root, self.source, None, False)
        other = self.folder / "talk.tex"
        other.write_text(self.source.read_text())
        self.assertEqual(source_build_command(self.root, other)[-1], "sample-paper-talk")
        ok, message = verify_current(self.root, source=other)
        self.assertFalse(ok)
        self.assertIn("different source", message)
        ok, message = verify_current(self.root, source=self.source.relative_to(self.root))
        self.assertTrue(ok, message)

    def test_main_tex_under_reading_publishes_as_the_slug_with_its_job_name_unchanged(self):
        folder = self.root / "reading" / "demo-paper"
        folder.mkdir(parents=True)
        main = folder / "main.tex"
        main.write_text(self.source.read_text())
        command, _cwd, cache, output, job = source_build_command(self.root, main)
        self.assertEqual(job, "demo-paper-main")
        self.assertIn("-jobname=demo-paper-main", command)

        def build(command, **kwargs):
            (cache / "demo-paper-main.pdf").write_bytes(b"main PDF")
            (cache / "demo-paper-main.synctex.gz").write_bytes(b"sync")
        with patch("labo_tools.build.subprocess.run", side_effect=build):
            self.assertEqual(run_source_build(self.root, main, None, False)[1], "demo-paper")
        self.assertEqual((output / "demo-paper.pdf").read_bytes(), b"main PDF")
        self.assertFalse((output / "demo-paper-main.pdf").exists())
        ok, message = verify_current(self.root, source=main)
        self.assertTrue(ok, message)
        self.audit.assert_called_with(output / "demo-paper.pdf", cache, "demo-paper-main", cache / "demo-paper-main.aux", source=main)

    def test_roots_in_one_folder_publish_separate_pairs(self):
        translation = self.folder / "sample-paper_ja.tex"
        notes = self.folder / "notes.tex"
        for path in (translation, notes):
            path.write_text(self.source.read_text())

        def build(command, **kwargs):
            job = next(a.split("=", 1)[1] for a in command if a.startswith("-jobname="))
            cache = self.folder / ".temp"
            (cache / f"{job}.pdf").write_bytes(job.encode())
            (cache / f"{job}.synctex.gz").write_bytes(b"sync")
        with patch("labo_tools.build.subprocess.run", side_effect=build):
            self.assertEqual(run_source_build(self.root, translation, None, False)[1], "sample-paper_ja")
            self.assertEqual(run_source_build(self.root, notes, None, False)[1], "sample-paper-notes")
        self.assertEqual((self.root / "output/sample-paper_ja.pdf").read_bytes(), b"sample-paper_ja")
        self.assertEqual((self.root / "output/sample-paper-notes.pdf").read_bytes(), b"sample-paper-notes")
        for path in (translation, notes):
            ok, message = verify_current(self.root, source=path)
            self.assertTrue(ok, message)

    def test_copy_html_keeps_the_master_and_names_the_copy_like_a_root(self):
        page = self.root / "reading" / "demo-paper" / "companion" / "index.html"
        page.parent.mkdir(parents=True)
        page.write_text("<!doctype html><title>x</title>")
        target = copy_html(self.root, page)
        self.assertEqual(target, self.root / "output" / "demo-paper-companion.html")
        self.assertEqual(target.read_text(), page.read_text())
        self.assertTrue(page.exists())
        named = self.root / "reading" / "demo-paper" / "demo-paper-review.html"
        named.write_text("<p>review</p>")
        self.assertEqual(copy_html(self.root, named).name, "demo-paper-review.html")
        other = self.root / "reading" / "demo-paper" / "notes.html"
        other.write_text("<p>notes</p>")
        self.assertEqual(copy_html(self.root, other).name, "demo-paper-notes.html")

    def test_copy_html_refuses_pages_outside_a_source_directory(self):
        stray = self.root / "page.html"
        stray.write_text("<p>x</p>")
        with self.assertRaisesRegex(PaperError, "under writing/<slug>/ or reading/<slug>/"):
            copy_html(self.root, stray)
        not_html = self.folder / "notes.txt"
        not_html.write_text("x")
        with self.assertRaisesRegex(PaperError, ".html file"):
            copy_html(self.root, not_html)

    def test_replaced_pdf_is_not_the_current_build(self):
        self._successful_build()
        (self.root / "output/sample-paper_en.pdf").write_bytes(b"some other PDF")
        ok, message = verify_current(self.root, source=self.source)
        self.assertFalse(ok)
        self.assertIn("differs", message)

    def test_recorded_postprocessing_keeps_the_pdf_current_only_after_success(self):
        self._successful_build()
        (self.root / "output/sample-paper_en.pdf").write_bytes(b"normalized PDF")
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
        step = f"{Path(sys.executable).as_posix()} -c \"open('output/sample-paper_en.pdf','wb').write(b'normalized')\""
        run_postprocess(self.root, [step], source=self.source)
        self.assertEqual((self.root / "output/sample-paper_en.pdf").read_bytes(), b"normalized")
        ok, message = verify_current(self.root, source=self.source)
        self.assertTrue(ok, message)
        record = json.loads((self.folder / ".temp/sample-paper_en.build.json").read_text())
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
