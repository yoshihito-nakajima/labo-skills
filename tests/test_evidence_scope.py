"""Synthetic read-only scope checks, never mathematical review certificates."""

from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from labo_tools.evidence import CHECKOUT, EvidenceError, snapshot  # noqa: E402
from labo_tools.evidence_scope import inspect_scope  # noqa: E402


MAIN = "writing/example/main.tex"


class EvidenceScopeTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name).resolve()
        self.put(MAIN, "A synthetic manuscript.\n")

    def put(self, name, text):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return path

    def inspect(self, **kwargs):
        return inspect_scope(self.root, source=MAIN, **kwargs)

    @staticmethod
    def paths(result):
        return {entry["path"] for entry in result["dependencies"]}

    @staticmethod
    def codes(result):
        return {entry["code"] for entry in result["issues"]}

    def record(self, **kwargs):
        value = snapshot(self.root, kind="writing", **kwargs)
        self.put("reviews/selected.yaml", yaml.safe_dump(value))
        return value

    def test_discovery_only_does_not_invent_coverage_or_approval(self):
        result = inspect_scope(self.root, paper="example")
        self.assertEqual(result["schema_version"], 1)
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["selection"]["mode"], "discovery")
        self.assertEqual(result["omitted"], [])
        self.assertEqual(result["covered"], [])
        self.assertNotIn("complete", result)
        self.assertNotIn("verdict", result)

    def test_explicit_workspace_compilation_root_resolves_workspace_style_inputs(self):
        source = "reading/example/source/main.tex"
        self.put(source, "\\input{reading/example/source/part}\n")
        self.put("reading/example/source/part.tex", "Synthetic only.")
        default = inspect_scope(self.root, source=source)
        self.assertEqual(default["compilation_root"], "reading/example/source")
        self.assertIn("missing-dependency", self.codes(default))
        explicit = inspect_scope(self.root, source=source, compile_root=".")
        self.assertEqual(explicit["compilation_root"], ".")
        self.assertEqual(explicit["status"], "ok", explicit["issues"])
        self.assertIn("reading/example/source/part.tex", self.paths(explicit))

    def test_explicit_source_parent_preserves_existing_default(self):
        self.put(MAIN, "\\input{part}\n")
        self.put("writing/example/part.tex", "")
        self.assertEqual(self.inspect(), self.inspect(compile_root="writing/example"))

    def test_explicit_compilation_root_does_not_hide_source_relative_ambiguity(self):
        self.put(MAIN, "\\input{part}\n")
        self.put("writing/example/part.tex", "")
        self.put("build-cwd/part.tex", "")
        result = self.inspect(compile_root="build-cwd")
        self.assertIn("ambiguous-dependency", self.codes(result))
        self.assertEqual(self.paths(result), {MAIN})

    def test_explicit_compilation_root_keeps_source_relative_fallback_unresolved(self):
        self.put(MAIN, "\\input{part}\n")
        self.put("writing/example/part.tex", "")
        (self.root / "build-cwd").mkdir()
        result = self.inspect(compile_root="build-cwd")
        self.assertIn("source-relative-dependency", self.codes(result))
        self.assertEqual(result["status"], "warning")

    def test_invalid_compilation_roots_are_rejected(self):
        for selected in ("", "/tmp", "C:/build", "D:build", "../outside", "./writing",
                         "writing/../writing", "writing//example", "missing", MAIN):
            with self.subTest(compile_root=selected), self.assertRaises(EvidenceError):
                self.inspect(compile_root=selected)

    def test_symlinked_compilation_roots_and_ancestors_are_rejected(self):
        actual = self.root / "actual"
        (actual / "child").mkdir(parents=True)
        (self.root / "linked").symlink_to(actual, target_is_directory=True)
        for selected in ("linked", "linked/child"):
            with self.subTest(compile_root=selected), self.assertRaises(EvidenceError):
                self.inspect(compile_root=selected)

    def test_compilation_root_cannot_enter_a_policy_checkout(self):
        policy = self.root / "synthetic-policy"
        (policy / "child").mkdir(parents=True)
        with patch("labo_tools.evidence.CHECKOUT", policy):
            for selected in ("synthetic-policy", "synthetic-policy/child"):
                with self.subTest(compile_root=selected), self.assertRaises(EvidenceError):
                    self.inspect(compile_root=selected)

    def test_nested_compile_root_inputs_bibliography_graphics_and_local_packages(self):
        self.put(MAIN, "\\documentclass{custom}\n\\usepackage{local}\n\\input{sections/first}\n")
        self.put("writing/example/custom.cls", "\\RequirePackage{helper}\n")
        self.put("writing/example/local.sty", "")
        self.put("writing/example/helper.sty", "")
        self.put("writing/example/sections/first.tex", "\\include{sections/second}\n")
        self.put("writing/example/sections/second.tex",
                 "\\includegraphics[width=3cm]{images/plot}\n\\bibliography{refs,more.bib}\n")
        self.put("writing/example/images/plot.pdf", "synthetic graphic")
        self.put("writing/example/refs.bib", "synthetic reference")
        self.put("writing/example/more.bib", "synthetic reference")
        result = self.inspect(trees=["writing/example"])
        self.assertEqual(result["status"], "ok", result["issues"])
        self.assertEqual(len(self.paths(result)), 9)
        graphic = next(x for x in result["dependencies"] if x["kind"] == "graphic")
        self.assertEqual(graphic["from"], "writing/example/sections/second.tex")
        self.assertEqual(graphic["line"], 1)
        self.assertEqual(result["omitted"], [])

    def test_actual_utf8_paths_and_spaces_are_literal(self):
        self.put(MAIN, "\\input{sections/証明 α}\n\\addbibresource{資料 β.bib}\n")
        self.put("writing/example/sections/証明 α.tex", "Synthetic only.")
        self.put("writing/example/資料 β.bib", "Synthetic only.")
        result = self.inspect()
        self.assertEqual(result["status"], "ok", result["issues"])
        self.assertIn("writing/example/sections/証明 α.tex", self.paths(result))

    def test_explicit_selected_files_cover_only_the_named_files(self):
        self.put(MAIN, "\\input{part}\n")
        self.put("writing/example/part.tex", "")
        result = self.inspect(files=[MAIN])
        self.assertEqual(result["status"], "warning")
        self.assertEqual(result["omitted"], ["writing/example/part.tex"])
        self.assertEqual(result["suggested_files"], result["omitted"])
        self.assertEqual(result["selection"]["files"], [MAIN])

    def test_record_tree_new_member_is_not_covered_by_directory_prefix(self):
        self.put(MAIN, "\\input{late}\n")
        self.record(trees=["writing/example"])
        self.put("writing/example/late.tex", "A new input after the snapshot.")
        result = self.inspect(record="reviews/selected.yaml")
        self.assertEqual(result["omitted"], ["writing/example/late.tex"])
        self.assertEqual([x["path"] for x in result["covered"]], [MAIN])
        self.assertEqual(result["status"], "warning")

    def test_recorded_changed_bytes_are_warning_not_new_approval(self):
        self.record(files=[MAIN])
        self.put(MAIN, "Changed manuscript.")
        result = self.inspect(record="reviews/selected.yaml")
        self.assertIn("changed-recorded-input", self.codes(result))
        self.assertEqual(result["omitted"], [])
        self.assertEqual(result["status"], "warning")

    def test_claim_file_coverage_requires_exact_recorded_transitive_fingerprint(self):
        self.put("research/example/claims.yaml", yaml.safe_dump({
            "schema_version": 1, "claims": {
                "main-claim": {"statement": "Synthetic claim.", "status": "unverified",
                               "evidence": [MAIN], "dependencies": ["seed-claim"]},
                "seed-claim": {"statement": "Synthetic seed.", "status": "unverified",
                               "evidence": ["research/example/proof.md"]},
            },
        }))
        self.put("research/example/proof.md", "Synthetic note, not a proof.")
        self.record(catalog="research/example/claims.yaml", claim_ids=["main-claim"])
        result = self.inspect(record="reviews/selected.yaml")
        self.assertEqual(result["omitted"], [])
        self.assertTrue(any("record-claim:" in via for x in result["covered"] for via in x["via"]))
        self.put("research/example/proof.md", "Changed transitive evidence.")
        changed = self.inspect(record="reviews/selected.yaml")
        self.assertEqual(changed["omitted"], [MAIN])
        self.assertIn("unresolved-claim-scope", self.codes(changed))

    def test_comments_inline_verbatim_and_environments_are_masked(self):
        self.put(MAIN, "% \\input{missing}\n"
                 "\\verb|\\input{missing}|\n"
                 "\\begin{verbatim}\n\\input{missing}\n\\end{verbatim}\n"
                 "\\begin{lstlisting}\n\\input{missing}\n\\end{lstlisting}\n"
                 "\\% literal percent \\input{real}\n")
        self.put("writing/example/real.tex", "")
        result = self.inspect()
        self.assertEqual(result["status"], "ok", result["issues"])
        item = next(x for x in result["dependencies"] if x["kind"] == "tex")
        self.assertEqual(item["line"], 9)

    def test_escaped_backslash_before_comment_is_not_an_input(self):
        self.put(MAIN, "\\\\% \\input{missing}\n")
        result = self.inspect()
        self.assertEqual(result["status"], "ok")
        self.assertEqual(self.paths(result), {MAIN})

    def test_malformed_verbatim_is_explicitly_unresolved(self):
        self.put(MAIN, "\\begin{verbatim}\n\\input{not-real}\n")
        result = self.inspect()
        self.assertIn("malformed-verbatim", self.codes(result))
        self.assertEqual(result["status"], "warning")

    def test_dynamic_constructs_and_nonliteral_inputs_remain_unresolved(self):
        self.put(MAIN, "\\graphicspath{{figures/}}\n\\import{chapters/}{one}\n"
                 "\\catcode`\\%=12\n\\newcommand{\\file}{secret}\n"
                 "\\iftrue\\input{\\file}\\else\\input{literal}\\fi\n"
                 "\\input unbraced\n")
        self.put("writing/example/literal.tex", "")
        result = self.inspect()
        self.assertIn("dynamic-tex", self.codes(result))
        self.assertIn("nonliteral-dependency", self.codes(result))
        self.assertNotEqual(result["status"], "ok")
        self.assertTrue(result["unresolved"])

    def test_missing_files_and_nonlocal_tex_packages_have_distinct_diagnostics(self):
        self.put(MAIN, "\\documentclass{article}\n\\input{missing}\n")
        result = self.inspect()
        self.assertEqual(result["status"], "error")
        self.assertIn("missing-dependency", self.codes(result))
        self.assertIn("external-tex-dependency", self.codes(result))

    def test_circular_inputs_terminate_with_explicit_cycle(self):
        self.put(MAIN, "\\input{part}\n")
        self.put("writing/example/part.tex", "\\input{main}\n")
        result = self.inspect()
        self.assertIn("dependency-cycle", self.codes(result))
        self.assertEqual(len(result["dependencies"]), 3)
        self.assertEqual(result["status"], "warning")

    def test_extensionless_graphic_variants_are_not_arbitrarily_chosen(self):
        self.put(MAIN, "\\includegraphics{plot}\n")
        for suffix in (".png", ".pdf"):
            self.put("writing/example/plot" + suffix, "")
        result = self.inspect()
        self.assertIn("ambiguous-dependency", self.codes(result))
        self.assertEqual(self.paths(result), {MAIN})
        self.assertEqual(len(result["unresolved"][0]["candidates"]), 2)

    def test_explicit_graphic_extension_disambiguates(self):
        self.put(MAIN, "\\includegraphics*{plot.png}\n")
        self.put("writing/example/plot.png", "")
        self.put("writing/example/plot.pdf", "")
        self.assertEqual(self.inspect()["status"], "ok")

    def test_source_relative_and_compile_root_collision_is_unresolved(self):
        self.put(MAIN, "\\input{sections/chapter}\n")
        self.put("writing/example/sections/chapter.tex", "\\input{part}\n")
        self.put("writing/example/part.tex", "")
        self.put("writing/example/sections/part.tex", "")
        result = self.inspect()
        self.assertIn("ambiguous-dependency", self.codes(result))
        self.assertNotIn("writing/example/part.tex", self.paths(result))
        self.assertNotIn("writing/example/sections/part.tex", self.paths(result))

    def test_unique_source_relative_candidate_stays_explicitly_unconfirmed(self):
        self.put(MAIN, "\\input{sections/chapter}\n")
        self.put("writing/example/sections/chapter.tex", "\\input{part}\n")
        self.put("writing/example/sections/part.tex", "")
        result = self.inspect()
        self.assertIn("source-relative-dependency", self.codes(result))
        self.assertIn("writing/example/sections/part.tex", self.paths(result))
        self.assertEqual(result["status"], "warning")

    def test_dependency_dotdot_inside_workspace_is_resolved_without_escape(self):
        self.put(MAIN, "\\input{../../research/shared}\n")
        self.put("research/shared.tex", "Synthetic source.")
        self.assertIn("research/shared.tex", self.paths(self.inspect()))

    def test_absolute_drive_and_workspace_escape_dependencies_are_errors(self):
        for target in ("/tmp/no", "C:/private/no", "../../../outside", "D:private"):
            with self.subTest(target=target):
                self.put(MAIN, "\\input{" + target + "}\n")
                result = self.inspect()
                self.assertEqual(result["status"], "error", result["issues"])
                self.assertIn("unsafe-dependency", self.codes(result))

    def test_symlink_files_and_directories_are_never_followed(self):
        self.put("actual/part.tex", "\\input{secret}\n")
        (self.root / "writing/example/part.tex").symlink_to(self.root / "actual/part.tex")
        self.put(MAIN, "\\input{part}\n")
        self.assertIn("unsafe-dependency", self.codes(self.inspect()))
        (self.root / "writing/example/link").symlink_to(self.root / "actual", target_is_directory=True)
        self.put(MAIN, "\\input{link/missing}\n")
        self.assertIn("unsafe-dependency", self.codes(self.inspect()))

    def test_policy_checkout_path_is_not_traversed(self):
        (self.root / "writing/example/policy").symlink_to(CHECKOUT, target_is_directory=True)
        self.put(MAIN, "\\input{policy/private}\n")
        self.assertIn("unsafe-dependency", self.codes(self.inspect()))
        with self.assertRaises(EvidenceError):
            inspect_scope(CHECKOUT, source="anything.tex")

    def test_dotdot_does_not_normalize_away_an_unsafe_symlink(self):
        self.put("actual/part.tex", "")
        (self.root / "writing/example/link").symlink_to(self.root / "actual", target_is_directory=True)
        self.put(MAIN, "\\input{link/../main}\n")
        result = self.inspect()
        self.assertEqual(result["status"], "error")
        self.assertIn("unsafe-dependency", self.codes(result))

    def test_selected_tree_does_not_cover_files_in_excluded_cache(self):
        self.put(MAIN, "\\input{build/fragment}\n")
        self.put("writing/example/build/fragment.tex", "")
        result = self.inspect(trees=["writing/example"])
        self.assertEqual(result["omitted"], ["writing/example/build/fragment.tex"])
        explicit = self.inspect(trees=["writing/example"], files=["writing/example/build/fragment.tex"])
        self.assertEqual(explicit["omitted"], [])

    def test_sources_are_bounded_by_byte_file_and_depth_limits(self):
        self.put(MAIN, "\\input{part}\n")
        self.put("writing/example/part.tex", "test")
        with patch("labo_tools.evidence_scope.MAX_FILES", 1):
            self.assertIn("traversal-limit", self.codes(self.inspect()))
        with patch("labo_tools.evidence_scope.MAX_DEPTH", 0):
            self.assertIn("traversal-limit", self.codes(self.inspect()))
        with patch("labo_tools.evidence_scope.MAX_FILE_BYTES", 1):
            self.assertIn("read-limit", self.codes(self.inspect()))
        with patch("labo_tools.evidence_scope.MAX_TOTAL_BYTES", 1):
            self.assertIn("read-limit", self.codes(self.inspect()))

    def test_non_utf8_input_is_an_error_not_silently_skipped(self):
        self.put(MAIN, "\\input{part}\n")
        path = self.put("writing/example/part.tex", "")
        path.write_bytes(b"\xff")
        self.assertIn("unreadable-source", self.codes(self.inspect()))
        self.assertEqual(self.inspect()["status"], "error")

    def test_endinput_and_end_document_stop_literal_scanning(self):
        for stop in ("\\endinput", "\\end{document}"):
            with self.subTest(stop=stop):
                self.put(MAIN, stop + "\n\\input{missing}\n")
                self.assertEqual(self.inspect()["status"], "ok")

    def test_invalid_selection_and_source_arguments_are_rejected(self):
        for kwargs in ({}, {"source": MAIN, "paper": "example"},
                       {"paper": "../escape"}, {"source": "/tmp/test.tex"},
                       {"source": "C:/test.tex"}, {"source": "../escape.tex"},
                       {"source": "missing.tex"}, {"source": "./" + MAIN}):
            with self.subTest(kwargs=kwargs), self.assertRaises(EvidenceError):
                inspect_scope(self.root, **kwargs)
        with self.assertRaises(EvidenceError):
            self.inspect(record="anything.yaml", files=[MAIN])

    def test_inspection_does_not_modify_sources_records_or_scope(self):
        self.put(MAIN, "\\input{late}\n")
        self.record(trees=["writing/example"])
        self.put("writing/example/late.tex", "")
        def state():
            return {p.relative_to(self.root).as_posix(): (p.read_bytes(), p.stat().st_mtime_ns)
                    for p in self.root.rglob("*") if p.is_file()}
        before = state()
        result = self.inspect(record="reviews/selected.yaml")
        self.assertEqual(state(), before)
        self.assertEqual(result["selection"]["files"], [])
        self.assertEqual(result["suggested_files"], ["writing/example/late.tex"])


if __name__ == "__main__":
    unittest.main()
