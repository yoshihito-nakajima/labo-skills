from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from labo_tools.cli import main  # noqa: E402
from labo_tools.paper import PaperError, map_openings, read_section  # noqa: E402


class PaperBuildTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name).resolve()
        self.paper = self.root / "writing" / "story-paper"
        self.sections = self.paper / "sections"
        self.sections.mkdir(parents=True)
        (self.paper / "main.tex").write_text(
            "\\input{sections/01-introduction}\n\\input{sections/02-example}\n"
        )
        (self.sections / "01-introduction.tex").write_text(
            "\\section{Introduction}\nOur question matters.\n"
            "% LABO:INTRO-END\n"
            "\\begin{theorem} Deep private theorem body \\end{theorem}\n"
        )
        (self.sections / "02-example.tex").write_bytes(
            b"\\section{Example}\nA concrete obstruction.\n"
            b"% LABO:INTRO-END\n" + b"\xff" * 100
        )

    def cli(self, *args):
        out, err = StringIO(), StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            status = main([*args, "--workspace", str(self.root)])
        return status, out.getvalue(), err.getvalue()

    def test_map_only_openings_does_not_read_body(self):
        openings = map_openings(self.root, "story-paper")
        self.assertEqual([x.section for x in openings], ["01-introduction", "02-example"])
        self.assertNotIn("private theorem", openings[0].opening)
        status, output, error = self.cli("paper", "map", "--paper", "story-paper", "--format", "json")
        self.assertEqual(status, 0, error)
        self.assertEqual(len(json.loads(output)["sections"]), 2)

    def test_section_reads_one_file_only(self):
        local = read_section(self.root, "story-paper", "01-introduction")
        self.assertIn("Deep private theorem", local)
        status, output, error = self.cli("paper", "section", "--paper", "story-paper",
                                         "--name", "01-introduction")
        self.assertEqual(status, 0, error)
        self.assertNotIn("concrete obstruction", output)

    def test_map_uses_declared_order_and_excludes_unused_sections(self):
        (self.paper / "main.tex").write_text(
            "\\include{sections/02-example}\n\\input{sections/01-introduction.tex}\n"
        )
        (self.sections / "03-unused.tex").write_bytes(b"\xff")
        self.assertEqual(
            [item.section for item in map_openings(self.root, "story-paper")],
            ["02-example", "01-introduction"],
        )

    def test_map_ignores_commented_input_and_handles_escaped_percent(self):
        (self.paper / "main.tex").write_text(
            "% \\input{sections/99-missing}\n"
            "\\input{sections/01-introduction} % \\input{sections/98-missing}\n"
            "\\% a literal percent; \\input{sections/02-example}\n"
        )
        self.assertEqual(
            [item.section for item in map_openings(self.root, "story-paper")],
            ["01-introduction", "02-example"],
        )

    def test_map_stops_at_end_of_document(self):
        (self.paper / "main.tex").write_text(
            "\\begin{document}\n\\input{sections/01-introduction}\n"
            "\\end{document}\n\\input{sections/99-trailing-scratch}\n"
        )
        self.assertEqual(
            [item.section for item in map_openings(self.root, "story-paper")],
            ["01-introduction"],
        )

    def test_map_rejects_unresolvable_or_dynamic_inputs(self):
        for source in (
            "\\input{sections/99-missing}\n",
            "\\input{\\sectionpath}\n",
            "\\input sections/01-introduction\n",
            "\\newcommand{\\chapterinput}{\\input{sections/01-introduction}}\n",
            "\\iftrue\\input{sections/01-introduction}\\fi\n",
            "\\includeonly{sections/01-introduction}\n\\include{sections/02-example}\n",
        ):
            with self.subTest(source=source):
                (self.paper / "main.tex").write_text(source)
                with self.assertRaises(PaperError):
                    map_openings(self.root, "story-paper")

    def test_missing_marker_is_failure(self):
        (self.sections / "01-introduction.tex").write_text("\\section{Introduction}\nNo delimiter")
        with self.assertRaisesRegex(PaperError, "marker"):
            map_openings(self.root, "story-paper")

    def test_build_dry_run_has_two_destinations_without_writes(self):
        status, output, error = self.cli("build", "--paper", "story-paper", "--dry-run")
        self.assertEqual(status, 0, error)
        self.assertIn("-synctex=1", output)
        self.assertIn("-jobname=story-paper", output)
        self.assertIn("-auxdir=" + str(self.paper / ".temp"), output)
        self.assertIn("-outdir=" + str(self.root / "output"), output)
        self.assertFalse((self.paper / ".temp").exists())
        self.assertFalse((self.root / "output").exists())

    @patch("labo_tools.build.subprocess.run")
    def test_build_invokes_latexmk_without_shell(self, run):
        def create_outputs(*args, **kwargs):
            output = self.root / "output"
            (output / "story-paper.pdf").write_bytes(b"PDF fixture")
            (output / "story-paper.synctex.gz").write_bytes(b"SyncTeX fixture")

        run.side_effect = create_outputs
        status, output, error = self.cli("build", "--paper", "story-paper")
        self.assertEqual(status, 0, error)
        args, kwargs = run.call_args
        self.assertEqual(args[0][0], "latexmk")
        self.assertEqual(kwargs["cwd"], self.paper)
        self.assertTrue(kwargs["check"])
        self.assertTrue((self.paper / ".temp").is_dir())
        self.assertTrue((self.root / "output" / "story-paper.pdf").is_file())
        self.assertFalse((self.root / "output" / "story-paper").exists())
        self.assertEqual(run.call_count, 1)

    @patch("labo_tools.build.subprocess.run")
    def test_build_recovers_missing_synctex_with_one_forced_rebuild(self, run):
        def create_outputs(command, **kwargs):
            output = self.root / "output"
            (output / "story-paper.pdf").write_bytes(b"PDF fixture")
            if "-g" in command:
                (output / "story-paper.synctex.gz").write_bytes(b"SyncTeX fixture")

        run.side_effect = create_outputs
        status, _, error = self.cli("build", "--paper", "story-paper")
        self.assertEqual(status, 0, error)
        self.assertEqual(run.call_count, 2)
        self.assertNotIn("-g", run.call_args_list[0].args[0])
        self.assertIn("-g", run.call_args_list[1].args[0])

    @patch("labo_tools.build.subprocess.run")
    def test_build_fails_when_successful_process_produces_no_pdf(self, run):
        status, output, error = self.cli("build", "--paper", "story-paper")
        self.assertEqual(status, 2)
        self.assertNotIn("Build finished", output)
        self.assertIn("output PDF", error)
        self.assertEqual(run.call_count, 1)

    @patch("labo_tools.build.subprocess.run")
    def test_build_missing_synctex_failure_is_bounded(self, run):
        def create_pdf_only(*args, **kwargs):
            (self.root / "output" / "story-paper.pdf").write_bytes(b"PDF fixture")

        run.side_effect = create_pdf_only
        status, output, error = self.cli("build", "--paper", "story-paper")
        self.assertEqual(status, 2)
        self.assertNotIn("Build finished", output)
        self.assertIn("SyncTeX", error)
        self.assertEqual(run.call_count, 2)

    def test_build_rejects_symlinked_cache(self):
        (self.paper / ".temp").symlink_to(self.root, target_is_directory=True)
        code, _, error = self.cli("build", "--paper", "story-paper")
        self.assertEqual(code, 2)
        self.assertIn("symlinks", error)


if __name__ == "__main__":
    unittest.main()
