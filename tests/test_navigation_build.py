"""Exercise actual mounted launchers and artifact/check separation with fictional TeX."""

import json
from contextlib import redirect_stdout, redirect_stderr
from io import StringIO
from pathlib import Path
import runpy
import shutil
import subprocess
import sys
import tempfile
import unittest

CHECKOUT = Path(__file__).resolve().parents[1]
TEX = r"""\documentclass{article}
\usepackage{hyperref}
\begin{document}
\tableofcontents
\section{First}\label{sec:first}
See Section~\ref{sec:second}.
\newpage
\section{Second}\label{sec:second}
Return to Section~\ref{sec:first}.
\end{document}
"""


@unittest.skipUnless(shutil.which("qpdf"), "qpdf is required")
class NavigationBridgeTests(unittest.TestCase):
    def test_config_changes_and_invalid_baselines_cannot_leave_stale_pass(self):
        fixture = runpy.run_path(str(CHECKOUT / "tests/test_pdf_navigation.py"))["write_pdf"]
        bridge = runpy.run_path(str(CHECKOUT / "src/labo_tools/navigation.py"))["check_navigation"]
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            pdf = fixture(root / "fictional.pdf")
            source = root / "main.tex"
            source.write_text("fictional source identity")
            report = root / "navigation-main.json"
            with redirect_stdout(StringIO()), redirect_stderr(StringIO()):
                bridge(pdf, root, "main", source=source)
                initial = json.loads(report.read_text())
                self.assertEqual(initial["expectations"]["status"], "not_supplied")
                source.with_suffix(".navigation.json").write_text('{"min_links": 1}')
                bridge(pdf, root, "main", source=source)
                self.assertEqual(json.loads(report.read_text())["status"], "fail")
                # A partially damaged old report must not abort a fresh audit.
                report.write_text('{"rendering": {"status": "rendered"}}')
                source.with_suffix(".navigation.json").write_text('{"min_links": 0}')
                bridge(pdf, root, "main", source=source)
                self.assertEqual(json.loads(report.read_text())["status"], "pass")
                source.with_suffix(".navigation.json").write_text('invalid json')
                bridge(pdf, root, "main", source=source)
                self.assertEqual(json.loads(report.read_text())["status"], "fail")
                self.assertTrue(pdf.exists())


@unittest.skipUnless(all(shutil.which(x) for x in ("qpdf", "latexmk", "pdflatex", "xelatex")),
                     "integration needs qpdf and TeX engines")
class NavigationBuildTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.base = Path(tmp.name).resolve()

    def invoke(self, script, *args, expected_status=0):
        result = subprocess.run([sys.executable, str(script), *map(str, args)], cwd=self.base,
                                capture_output=True, text=True, timeout=60)
        self.assertEqual(result.returncode, expected_status, result.stdout[-3000:] + result.stderr[-3000:])
        return result

    def test_both_mount_names_build_reading_and_courses_from_outside_workspace(self):
        for mount in (".agents", ".claude"):
            with self.subTest(mount=mount):
                workspace = self.base / mount[1:]
                workspace.mkdir()
                (workspace / mount).symlink_to(CHECKOUT, target_is_directory=True)
                source = workspace / "reading/fictional/main.tex"
                source.parent.mkdir(parents=True)
                source.write_text(TEX)
                requirements = {"min_outlines": 2,
                                "routes": [{"from_page": 2, "label": "sec:first"}]}
                source.with_suffix(".navigation.json").write_text(json.dumps(requirements))
                script = workspace / mount / "scripts/labo.py"
                result = self.invoke(script, "output", "build", "--workspace", workspace, "--source", source)
                self.assertIn("Navigation pass:", result.stdout)
                report_path = source.parent / ".temp/navigation-fictional-main.json"
                report = json.loads(report_path.read_text())
                self.assertEqual(report["status"], "pass")
                self.assertGreater(report["counts"]["links"], 0)
                self.assertEqual(report["counts"]["aux_labels"], 2)
                self.assertEqual(report["expectations"]["status"], "checked")
                self.assertEqual(sorted(p.name for p in (workspace / "output").iterdir()),
                                 ["fictional.pdf", "fictional.synctex.gz"])
                # Exercise rendering -> actual build -> rendering, not just
                # repeated calls to either half in isolation.
                checker = workspace / mount / "skills/mathematical-navigation/scripts/check_pdf.py"
                render_args = [workspace / "output/fictional.pdf", "--report", report_path,
                               "--render-dir", source.parent / ".temp/render", "--dpi", "36"]
                if shutil.which("pdftoppm"):
                    self.invoke(checker, *render_args)
                    baseline_path = report_path.with_name(report_path.stem + ".render.json")
                    baseline_bytes = baseline_path.read_bytes()
                # Repeat build carries structural baseline but never invents GUI evidence.
                self.invoke(script, "output", "build", "--workspace", workspace, "--source", source)
                repeated = json.loads(report_path.read_text())
                self.assertEqual(repeated["navigation_diff"]["changed_pages"], [])
                self.assertEqual(repeated["gui"]["status"], "not_performed")
                if shutil.which("pdftoppm"):
                    self.assertEqual(baseline_path.read_bytes(), baseline_bytes)
                    self.assertEqual(repeated["rendering"]["status"], "not_requested")
                    self.invoke(checker, *render_args)
                    rerendered = json.loads(report_path.read_text())
                    self.assertTrue(rerendered["rendering"]["cache_reused"])
                    self.assertEqual(rerendered["rendering"]["changed_pages"], [])
                    self.assertEqual(rerendered["rendering"]["visual_review"], "not_performed")

                source.write_text(TEX.replace(r"Return to Section~\ref{sec:first}.", "Return omitted."))
                broken = self.invoke(script, "output", "build", "--workspace", workspace, "--source", source)
                failure = json.loads(report_path.read_text())
                self.assertEqual(failure["status"], "fail")
                self.assertIn("expected_route_missing", [f["code"] for f in failure["findings"]])
                self.assertIn("Navigation fail:", broken.stderr)
                self.assertTrue((workspace / "output/fictional.pdf").is_file())
                # A changed PDF must compare against the old images, never inherit
                # their current-version status merely because paths are the same.
                if shutil.which("pdftoppm"):
                    self.assertEqual(baseline_path.read_bytes(), baseline_bytes)
                    self.invoke(checker, *render_args, expected_status=1)
                    changed = json.loads(report_path.read_text())
                    self.assertEqual(changed["status"], "fail")
                    self.assertFalse(changed["rendering"]["cache_reused"])
                    self.assertEqual(changed["rendering"]["changed_pages"], [2])

                # These distinct document roots deliberately share a build stem.
                other_source = source.with_name("fictional-main.tex")
                other_source.write_text(source.read_text())
                other_source.with_suffix(".navigation.json").write_text('{"min_outlines": 1}')
                self.invoke(script, "output", "build", "--workspace", workspace, "--source", other_source)
                other = json.loads(report_path.read_text())
                self.assertEqual(other["document_source"], str(other_source.resolve()))
                self.assertEqual(other["navigation_diff"]["comparison"], "no_comparable_baseline")
                if shutil.which("pdftoppm"):
                    self.invoke(checker, *render_args)
                    other = json.loads(report_path.read_text())
                    self.assertEqual(other["rendering"]["comparison"], "no_comparable_baseline")
                    self.assertFalse(other["rendering"]["cache_reused"])

                books = self.base / (mount[1:] + "-books")
                book_script = workspace / mount / "scripts/book_materials.py"
                self.invoke(book_script, "install", "--root", books, "--workspace", workspace)
                book_source = books / "materials/courses/fictional/main.tex"
                book_source.parent.mkdir(parents=True)
                book_source.write_text(TEX)
                book_source.with_suffix(".navigation.json").write_text(json.dumps(requirements))
                result = self.invoke(book_script, "build", "--root", books, "--workspace", workspace,
                                     "--course", "fictional")
                self.assertIn("Navigation pass:", result.stdout)
                book_report = json.loads((books / "cache/fictional/navigation-main.json").read_text())
                self.assertEqual(book_report["status"], "pass")
                self.assertEqual(book_report["expectations"]["status"], "checked")
                self.assertFalse(list((books / "materials").rglob("navigation-*.json")))
                book_source.write_text(TEX.replace(r"Return to Section~\ref{sec:first}.", "Return omitted."))
                broken_book = self.invoke(book_script, "build", "--root", books, "--workspace", workspace,
                                         "--course", "fictional")
                book_report = json.loads((books / "cache/fictional/navigation-main.json").read_text())
                self.assertEqual(book_report["status"], "fail")
                self.assertIn("Navigation fail:", broken_book.stderr)


if __name__ == "__main__":
    unittest.main()
