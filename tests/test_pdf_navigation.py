"""Black-box navigation checks using tiny, fictional PDFs built without TeX.

Run with ``python3 -m unittest discover -s .agents/tests -p test_pdf_navigation.py``.
qpdf is required; rendering tests additionally require pdftoppm. No fixture is
copied from a course, paper, or private review, and no external action is opened.
"""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


CHECKER = Path(__file__).resolve().parents[1] / "skills/mathematical-navigation/scripts/check_pdf.py"


def write_pdf(path, *, links=None, destinations=None, outline=None,
              outline_cycle=False, page_extras=None, content=None, pages=2,
              catalog_extra=""):
    """Write a real PDF with xref offsets, page content, and chosen navigation.

    Values are PDF syntax. @P1@ and @P2@ expand to page object references.
    This deliberately avoids the checker's parser or report model.
    """
    objects = [None, None]  # catalog and page tree

    def add(value):
        objects.append(value)
        return len(objects)

    page_ids = [add(None) for _ in range(pages)]

    def expand(value):
        for number, object_id in enumerate(page_ids, 1):
            value = value.replace(f"@P{number}@", f"{object_id} 0 R")
        return value

    for number, object_id in enumerate(page_ids, 1):
        label = (content or {}).get(number, f"Fictional page {number}")
        stream = f"BT /F1 14 Tf 20 150 Td ({label}) Tj ET\n".encode("ascii")
        content_id = add(b"<< /Length " + str(len(stream)).encode() + b" >>\nstream\n" + stream + b"endstream")
        annotation_ids = [add(expand("<< /Type /Annot /Subtype /Link " + spec + " >>"))
                          for spec in (links or {}).get(number, [])]
        annotations = " ".join(f"{ref} 0 R" for ref in annotation_ids)
        objects[object_id - 1] = (
            f"<< /Type /Page /Parent 2 0 R /Contents {content_id} 0 R "
            "/Resources << /Font << /F1 << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> >> >> "
            f"/Annots [{annotations}] {(page_extras or {}).get(number, '')} >>"
        )

    if destinations is None:
        destinations = [("first", "[@P1@ /Fit]")]
        if pages > 1:
            destinations.append(("second", "[@P2@ /XYZ null 180 null]"))
    names = " ".join(f"({name}) {expand(value)}" for name, value in destinations)
    catalog = f"<< /Type /Catalog /Pages 2 0 R /Names << /Dests << /Names [{names}] >> >> "
    if outline is not None:
        outline_root = add(None)
        outline_item = add(None)
        objects[outline_root - 1] = f"<< /Type /Outlines /First {outline_item} 0 R /Last {outline_item} 0 R /Count 1 >>"
        successor = f" /Next {outline_item} 0 R" if outline_cycle else ""
        objects[outline_item - 1] = expand(
            f"<< /Title (Fictional result) /Parent {outline_root} 0 R {outline}{successor} >>"
        )
        catalog += f"/Outlines {outline_root} 0 R "
    objects[0] = expand(catalog + catalog_extra + " >>")
    kids = " ".join(f"{ref} 0 R" for ref in page_ids)
    objects[1] = f"<< /Type /Pages /Kids [{kids}] /Count {pages} /MediaBox [0 0 200 200] >>"
    data = bytearray(b"%PDF-1.7\n%\xe2\xe3\xcf\xd3\n")
    offsets = [0]
    for number, value in enumerate(objects, 1):
        offsets.append(len(data))
        encoded = value.encode("ascii") if isinstance(value, str) else value
        data.extend(f"{number} 0 obj\n".encode() + encoded + b"\nendobj\n")
    startxref = len(data)
    data.extend(f"xref\n0 {len(objects) + 1}\n0000000000 65535 f \n".encode())
    for offset in offsets[1:]:
        data.extend(f"{offset:010d} 00000 n \n".encode())
    data.extend(f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{startxref}\n%%EOF\n".encode())
    path.write_bytes(data)
    return path


@unittest.skipUnless(shutil.which("qpdf"), "qpdf is required for real PDF checks")
class PDFNavigationTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory(prefix="fictional-navigation-")
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.report_number = 0

    def pdf(self, name="fictional.pdf", **kwargs):
        return write_pdf(self.root / name, **kwargs)

    def cli(self, pdf, report, **options):
        command = [sys.executable, str(CHECKER), str(pdf), "--report", str(report)]
        for key, value in options.items():
            command.extend(["--" + key.replace("_", "-"), str(value)])
        return subprocess.run(command, capture_output=True, text=True, timeout=30)

    def audit(self, pdf, status="pass", **options):
        self.report_number += 1
        report_path = self.root / f"report-{self.report_number}.json"
        process = self.cli(pdf, report_path, **options)
        self.assertTrue(report_path.is_file(), process.stdout + process.stderr)
        report = json.loads(report_path.read_text())
        self.assertEqual(report["status"], status, report["findings"])
        self.assertEqual(process.returncode, {"pass": 0, "fail": 1, "incomplete": 2}[status], process.stderr)
        return report, report_path

    def codes(self, report):
        return {finding["code"] for finding in report["findings"]}

    def expect(self, value, name="expectations.json"):
        path = self.root / name
        path.write_text(json.dumps(value))
        return path

    def test_named_explicit_and_uri_links_and_outline_are_inventoried(self):
        pdf = self.pdf(links={
            1: ["/Rect [20 20 70 35] /Dest (second)",
                "/Rect [20 40 70 55] /A << /S /GoTo /D [@P2@ /XYZ null 180 null] >>",
                "/Rect [20 60 70 75] /A << /S /URI /URI (https://example.invalid/fictional) >>"],
            2: ["/Rect [20 20 70 35] /Dest (first)"]},
            outline="/Dest (second)")
        before = pdf.read_bytes()
        report, _ = self.audit(pdf)
        self.assertEqual(report["counts"], {
            "pages": 2, "links": 4, "outlines": 1, "named_destinations": 2,
            "aux_labels": 0, "link_kinds": {"internal": 3, "uri": 1}})
        self.assertEqual(report["links"][0]["target"]["page"], 2)
        self.assertEqual(report["links"][1]["target"]["coordinates"], [None, 180, None])
        self.assertEqual(report["outlines"][0]["target"]["page"], 2)
        self.assertEqual(report["links"][2]["reachability"], "not_checked")
        self.assertEqual(report["rendering"]["status"], "not_requested")
        self.assertEqual(report["gui"]["status"], "not_performed")
        self.assertEqual(report["external_reachability"]["status"], "not_checked")
        self.assertEqual(report["pdf"]["sha256"], hashlib.sha256(before).hexdigest())
        self.assertEqual(pdf.read_bytes(), before)
        self.assertFalse(list(self.root.rglob("*.png")))

    def test_unresolved_link_stays_in_inventory_and_fails(self):
        pdf = self.pdf(links={1: ["/Rect [20 20 70 35] /Dest (absent)",
                                  "/Rect [20 40 70 55] /Dest (second)"]})
        report, _ = self.audit(pdf, "fail")
        self.assertEqual(report["counts"]["links"], 2)
        self.assertEqual(report["counts"]["link_kinds"], {"unresolved": 1, "internal": 1})
        self.assertIn("malformed_object", self.codes(report))
        self.assertTrue(any(item["location"] == "page 1, link 1" for item in report["findings"]))

    def test_invalid_rectangles_fail_but_clipped_rectangle_warns(self):
        for rect, code, status in [
            ("[20 20 70]", "invalid_rectangle", "fail"),
            ("[20 20 20 35]", "empty_rectangle", "fail"),
            ("[220 20 270 35]", "off_page_rectangle", "fail"),
            ("[-10 20 70 35]", "clipped_rectangle", "pass"),
        ]:
            with self.subTest(rect=rect):
                report, _ = self.audit(self.pdf(links={1: [f"/Rect {rect} /Dest (second)"]}), status)
                self.assertIn(code, self.codes(report))
                self.assertEqual(report["counts"]["links"], 1)

    def test_crop_box_and_rotated_page_use_default_user_coordinates(self):
        extras = {1: "/CropBox [20 10 180 190] /Rotate 90"}
        pdf = self.pdf(links={1: ["/Rect [30 160 80 180] /Dest (second)"]}, page_extras=extras)
        self.audit(pdf)
        pdf = self.pdf(links={1: ["/Rect [0 20 10 35] /Dest (second)"]}, page_extras=extras)
        report, _ = self.audit(pdf, "fail")
        self.assertIn("off_page_rectangle", self.codes(report))

    def test_invalid_destination_arrays_fail_even_without_inbound_links(self):
        for destination in ["[2 0 R /Fit]", "[@P2@ /XYZ 0 100 -1]",
                            "[@P2@ /FitR 20 20 10 30]", "[@P2@ /FitH]"]:
            with self.subTest(destination=destination):
                report, _ = self.audit(self.pdf(destinations=[("broken", destination)]), "fail")
                self.assertEqual(report["counts"]["named_destinations"], 1)
                self.assertNotIn("broken", report["destinations"])

    def test_duplicate_and_cyclic_named_destinations_fail(self):
        report, _ = self.audit(self.pdf(destinations=[("same", "[@P1@ /Fit]"),
                                                     ("same", "[@P2@ /Fit]")]), "fail")
        self.assertIn("duplicate_destination", self.codes(report))
        report, _ = self.audit(self.pdf(destinations=[("alpha", "(beta)"),
                                                     ("beta", "(alpha)")]), "fail")
        self.assertEqual(report["destinations"], {})
        self.assertIn("malformed_object", self.codes(report))

    def test_broken_bookmark_and_cycle_fail(self):
        report, _ = self.audit(self.pdf(outline="/Dest (absent)"), "fail")
        self.assertEqual(report["counts"]["outlines"], 1)
        self.assertEqual(report["outlines"][0]["kind"], "unresolved")
        report, _ = self.audit(self.pdf(outline="/Dest (second)", outline_cycle=True), "fail")
        self.assertIn("malformed_object", self.codes(report))

    def test_unverified_actions_are_incomplete_and_never_report_reachable(self):
        actions = [
            ("/A << /S /JavaScript /JS (fictional_no_op) >>", "unsupported_action", "unsupported"),
            ("/A << /S /GoToR /F (fictional-remote.pdf) /D [0 /Fit] >>", "external_file_action", "GoToR"),
            ("/A << /S /Launch /F (fictional-program) >>", "external_file_action", "Launch"),
            ("/A << /S /GoTo /D (second) /Next << /S /Named /N /NextPage >> >>", "action_chain", "internal"),
            ("/Dest (second) /AA << /E << /S /Named /N /NextPage >> >>", "additional_actions", "internal"),
        ]
        for action, code, kind in actions:
            with self.subTest(action=action):
                report, _ = self.audit(self.pdf(links={1: ["/Rect [20 20 70 35] " + action]}), "incomplete")
                self.assertIn(code, self.codes(report))
                self.assertEqual(report["links"][0]["kind"], kind)
                self.assertEqual(report["external_reachability"]["status"], "not_checked")

    def test_conflicting_actions_and_invalid_http_uri_fail(self):
        for action, code in [
            ("/Dest (second) /A << /S /GoTo /D (first) >>", "conflicting_action"),
            ("/A << /S /URI /URI (https:/missing-host) >>", "malformed_object"),
        ]:
            with self.subTest(action=action):
                report, _ = self.audit(self.pdf(links={1: ["/Rect [20 20 70 35] " + action]}), "fail")
                self.assertIn(code, self.codes(report))

    def test_aux_and_independently_declared_routes(self):
        child = self.root / "chapter.aux"
        child.write_text(r"\newlabel{result:fictional}{{1}{2}{Fictional {nested} title}{second}{}}" + "\n")
        aux = self.root / "main.aux"
        aux.write_text(r"\@input{chapter.aux}" + "\n")
        expected = self.expect({"destinations": [{"name": "second", "page": 2}],
                                "routes": [{"label": "result:fictional", "from_page": 1, "min_count": 2}],
                                "min_links": 2, "min_outlines": 1})
        pdf = self.pdf(links={1: ["/Rect [20 20 70 35] /Dest (second)",
                                  "/Rect [20 40 70 55] /Dest [@P2@ /XYZ null 180 null]"]},
                       outline="/Dest (second)")
        report, _ = self.audit(pdf, aux=aux, expect=expected)
        self.assertEqual(report["counts"]["aux_labels"], 1)
        self.assertEqual({Path(item["path"]).name for item in report["aux_files"]}, {"main.aux", "chapter.aux"})
        self.assertEqual(report["expectations"]["sha256"], hashlib.sha256(expected.read_bytes()).hexdigest())
        # The expected route still exists in the source registry after all links are omitted.
        report, _ = self.audit(self.pdf(outline="/Dest (second)"), "fail", aux=aux, expect=expected)
        self.assertIn("expected_route_missing", self.codes(report))
        self.assertIn("missing_expected_items", self.codes(report))

    def test_expectations_detect_wrong_page_origin_and_missing_outline(self):
        pdf = self.pdf(links={2: ["/Rect [20 20 70 35] /Dest (second)"]})
        expected = self.expect({"destinations": [{"name": "second", "page": 1}],
                                "routes": [{"to": "second", "from_page": 1}], "min_outlines": 1})
        report, _ = self.audit(pdf, "fail", expect=expected)
        self.assertTrue({"expected_destination", "expected_route_missing", "missing_expected_items"} <= self.codes(report))

    def test_aux_missing_destination_and_unsupported_include_are_not_passes(self):
        aux = self.root / "main.aux"
        aux.write_text(r"\newlabel{result:missing}{{1}{2}{}{absent}{}}" + "\n")
        report, _ = self.audit(self.pdf(), "fail", aux=aux)
        self.assertIn("aux_destination_missing", self.codes(report))
        aux.write_text(r"\@input{../fictional-outside.aux}" + "\n")
        report, _ = self.audit(self.pdf(), "incomplete", aux=aux)
        self.assertIn("aux_include_outside_root", self.codes(report))

    def test_missing_requested_input_and_invalid_expectations_are_not_passes(self):
        report, _ = self.audit(self.pdf(), "incomplete", aux=self.root / "missing.aux")
        self.assertIn("tool_or_input_unavailable", self.codes(report))
        expected = self.expect({"routes": [{"to": "second", "min_count": 0}]})
        report, _ = self.audit(self.pdf(), "fail", expect=expected)
        self.assertIn("audit_failed", self.codes(report))

    def test_missing_qpdf_is_incomplete_with_a_fresh_report(self):
        pdf = self.pdf()
        report_path = self.root / "unavailable.json"
        result = subprocess.run([sys.executable, str(CHECKER), str(pdf), "--report", str(report_path)],
                                env={**os.environ, "PATH": str(self.root / "no-tools")},
                                capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode, 2)
        report = json.loads(report_path.read_text())
        self.assertEqual(report["status"], "incomplete")
        self.assertIn("tool_or_input_unavailable", self.codes(report))

    def test_repeated_and_changed_navigation_have_page_scoped_differences(self):
        pdf = self.pdf(links={1: ["/Rect [20 20 70 35] /Dest (second)"]})
        original, baseline = self.audit(pdf)
        repeated, _ = self.audit(pdf, previous=baseline)
        self.assertEqual(repeated["navigation_diff"]["changed_pages"], [])
        self.assertEqual(repeated["navigation_diff"]["comparison"], "same_checker")
        changed_pdf = self.pdf("changed.pdf", links={1: ["/Rect [20 20 70 35] /Dest (first)"]})
        changed, _ = self.audit(changed_pdf, previous=baseline)
        self.assertEqual(changed["navigation_diff"]["changed_pages"], [1])
        self.assertEqual(changed["navigation_diff"]["previous_pdf_sha256"], original["pdf"]["sha256"])
        shorter, _ = self.audit(self.pdf("shorter.pdf", pages=1), previous=baseline)
        self.assertEqual(shorter["navigation_diff"]["removed_pages"], [2])
        original["checker_sha256"] = "fictional-obsolete-checker"
        baseline.write_text(json.dumps(original))
        no_baseline, _ = self.audit(pdf, previous=baseline)
        self.assertEqual(no_baseline["navigation_diff"]["comparison"], "no_comparable_baseline")
        self.assertEqual(no_baseline["navigation_diff"]["changed_pages"], [1, 2])

    @unittest.skipUnless(shutil.which("pdftoppm"), "pdftoppm is required for rendering")
    def test_explicit_rendering_distinguishes_content_and_config_changes(self):
        pdf = self.pdf()
        images = self.root / "render output"
        original, baseline = self.audit(pdf, render_dir=images, dpi=36)
        self.assertEqual(original["rendering"]["status"], "rendered")
        self.assertEqual(original["rendering"]["visual_review"], "not_performed")
        self.assertEqual(original["rendering"]["comparison"], "no_comparable_baseline")
        self.assertEqual(original["rendering"]["changed_pages"], [1, 2])
        for page in original["rendering"]["pages"].values():
            image = Path(page["path"])
            self.assertTrue(image.read_bytes().startswith(b"\x89PNG\r\n\x1a\n"))
            self.assertEqual(page["sha256"], hashlib.sha256(image.read_bytes()).hexdigest())
        repeated, _ = self.audit(pdf, render_dir=images, dpi=36, previous=baseline)
        self.assertEqual(repeated["rendering"]["comparison"], "same_renderer_config")
        self.assertEqual(repeated["rendering"]["changed_pages"], [])
        self.assertTrue(repeated["rendering"]["cache_reused"])
        damaged_image = Path(original["rendering"]["pages"]["1"]["path"])
        damaged_image.write_bytes(b"damaged fictional cache")
        repaired, _ = self.audit(pdf, render_dir=images, dpi=36, previous=baseline)
        self.assertFalse(repaired["rendering"]["cache_reused"])
        self.assertEqual(repaired["rendering"]["changed_pages"], [])
        self.assertTrue(damaged_image.read_bytes().startswith(b"\x89PNG\r\n\x1a\n"))
        changed_pdf = self.pdf("new content.pdf", content={2: "Changed fictional page"})
        changed, _ = self.audit(changed_pdf, render_dir=images, dpi=36, previous=baseline)
        self.assertEqual(changed["navigation_diff"]["changed_pages"], [])
        self.assertEqual(changed["rendering"]["changed_pages"], [2])
        config_changed, _ = self.audit(pdf, render_dir=images, dpi=72, previous=baseline)
        self.assertEqual(config_changed["rendering"]["comparison"], "no_comparable_baseline")
        self.assertEqual(config_changed["rendering"]["changed_pages"], [1, 2])
        self.assertTrue(all(Path(page["path"]).exists() for page in original["rendering"]["pages"].values()))

    def test_cli_does_not_overwrite_direct_inputs_or_follow_report_symlinks(self):
        pdf = self.pdf("input with spaces.pdf")
        aux = self.root / "main.aux"
        aux.write_text(r"\newlabel{result}{{1}{2}{}{second}{}}" + "\n")
        expected = self.expect({"destinations": ["second"]})
        inputs = [pdf, aux, expected]
        for target in inputs:
            with self.subTest(target=target.name):
                before = {path: path.read_bytes() for path in inputs}
                result = self.cli(pdf, target, aux=aux, expect=expected)
                self.assertEqual(result.returncode, 2)
                self.assertEqual({path: path.read_bytes() for path in inputs}, before)
        target = self.root / "keep.txt"
        target.write_text("fictional unrelated data")
        report_link = self.root / "linked-report.json"
        report_link.symlink_to(target)
        result = self.cli(pdf, report_link)
        self.assertEqual(result.returncode, 2)
        self.assertEqual(target.read_text(), "fictional unrelated data")
        self.assertTrue(report_link.is_symlink())

    def test_previous_report_can_be_replaced_after_comparison(self):
        pdf = self.pdf()
        _, baseline = self.audit(pdf)
        result = self.cli(pdf, baseline, previous=baseline)
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(baseline.read_text())
        self.assertEqual(report["navigation_diff"]["changed_pages"], [])

    def test_cli_does_not_overwrite_aux_input_loaded_through_include(self):
        pdf = self.pdf()
        child = self.root / "chapter.aux"
        child.write_text(r"\newlabel{result}{{1}{2}{}{second}{}}" + "\n")
        aux = self.root / "main.aux"
        aux.write_text(r"\@input{chapter.aux}" + "\n")
        before = child.read_bytes()
        result = self.cli(pdf, child, aux=aux)
        self.assertEqual(child.read_bytes(), before, "--report replaced a consumed aux include")
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)

    def test_cli_invalid_dpi_leaves_inputs_and_existing_report_intact(self):
        pdf = self.pdf()
        report = self.root / "existing-report.json"
        report.write_text("fictional existing report")
        before = pdf.read_bytes()
        result = self.cli(pdf, report, dpi=1)
        self.assertEqual(result.returncode, 2)
        self.assertEqual(pdf.read_bytes(), before)
        self.assertEqual(report.read_text(), "fictional existing report")


if __name__ == "__main__":
    unittest.main()
