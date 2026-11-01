"""Synthetic replay observations; mocked outputs are not mathematical evidence."""

import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import yaml


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))
from labo_tools import formal_replay as replay_module  # noqa: E402
from labo_tools.evidence import EvidenceError  # noqa: E402


class FormalReplayTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name).resolve()
        self.workspace = self.root / "private workspace"
        self.project = self.workspace / "lean/example"
        self.project.mkdir(parents=True)
        self.toolchain = self.root / "toolchain"
        (self.toolchain / "bin").mkdir(parents=True)
        (self.toolchain / "lib/lean").mkdir(parents=True)
        # An intentionally unusable ELF-like fixture: _run_command is mocked.
        # Tests never present it as an actual Lean installation or proof.
        binary = self.toolchain / "bin" / ("lean.exe" if replay_module.WINDOWS else "lean")
        binary.write_bytes((b"MZ00" if replay_module.WINDOWS else b"\x7fELF") + b"synthetic fixture, not Lean")
        binary.chmod(0o700)
        (self.toolchain / "lib/lean/Init.olean").write_bytes(b"synthetic Init")
        (self.project / "lean-toolchain").write_text("leanprover/lean4:v4.19.0\n")
        (self.project / "lakefile.toml").write_text('name = "example"\n[[lean_lib]]\nname = "Example"\n')
        (self.project / "lake-manifest.json").write_text(json.dumps({"version": "1.1.0", "packages": []}))
        self.source = self.project / "Example.lean"
        self.source.write_text("theorem Example.ok : True := True.intro\n")
        self.catalog = {"schema_version": 1, "claims": {"example-claim": {
            "statement": "Synthetic test claim, not a research result.", "status": "unverified",
            "formal": {"project": "lean/example", "source": "lean/example/Example.lean",
                       "declaration": "Example.ok", "kernel": {"verdict": "pending", "report": None},
                       "alignment": {"verdict": "pending", "report": None}},
        }}}
        self.save_catalog()

    def save_catalog(self):
        (self.workspace / "claims.yaml").write_text(yaml.safe_dump(self.catalog))

    def call(self, **kwargs):
        return replay_module.replay(self.workspace, catalog="claims.yaml", claim="example-claim",
                                    toolchain_dir=self.toolchain, **kwargs)

    @staticmethod
    def compact_report(report):
        """Failure diagnostics must not dump multi-megabyte input manifests."""
        audit = report.get("axiom_audit", {})
        return {"status": report.get("status"), "failure": report.get("failure"),
                "preflight": report.get("preflight"),
                "axiom_audit": {key: value[:4000] if isinstance(value, str) else value
                                for key, value in audit.items()},
                "commands": [{"argv": command["argv"], "status": command["status"],
                              "exit_code": command["exit_code"],
                              "stdout": command["stdout"][:200 if "--help" in command["argv"] else 4000],
                              "stderr": command["stderr"][:4000]}
                             for command in report.get("commands", [])]}

    def fake_run(self, command, timeout):
        argv = command["argv"]
        output = ""
        if "--version" in argv:
            output = "Lean (version 4.19.0, x86_64-linux, commit fixture, Release)\n"
        elif "--help" in argv:
            output = "--trust=num --stdin --root=dir"
        elif "-o" in argv:
            Path(argv[argv.index("-o") + 1]).write_bytes(b"synthetic selected artifact")
        else:
            output = "Example.ok : True\ntheorem Example.ok : True := True.intro\n'Example.ok' does not depend on any axioms\n"
        command.update(status="completed", exit_code=0, stdout=output, stderr="", duration_seconds=0.0)
        return True

    def execute(self, runner=None):
        with patch.object(replay_module, "_run_command", side_effect=runner or self.fake_run) as mocked:
            report = self.call(execute=True)
        return report, mocked

    def test_plan_is_read_only_and_invokes_nothing(self):
        before = {str(p): p.read_bytes() for p in self.root.rglob("*") if p.is_file()}
        with patch.object(subprocess, "Popen", side_effect=AssertionError("plan must not execute")):
            report = self.call()
        after = {str(p): p.read_bytes() for p in self.root.rglob("*") if p.is_file()}
        self.assertEqual(before, after)
        self.assertEqual(report["status"], "plan")
        self.assertFalse(report["executed"])
        self.assertTrue(report["preflight"]["ready"])
        self.assertTrue(all(c["status"] == "not-run" for c in report["commands"]))
        self.assertIsNone(report["inputs_after"])
        self.assertNotIn("lake", [Path(c["argv"][0]).name for c in report["commands"]])

    def test_execute_records_actual_commands_type_axioms_and_hashes(self):
        report, mocked = self.execute()
        self.assertEqual(mocked.call_count, 4)
        self.assertEqual(report["status"], "completed", self.compact_report(report))
        self.assertFalse(report["inputs_changed"])
        self.assertEqual(report["axiom_audit"]["axioms"], [])
        self.assertIn("Example.ok : True", report["axiom_audit"]["raw_output"])
        self.assertEqual(report["alignment"], "not-assessed")
        self.assertEqual(report["approval"], "not-granted")
        for command in report["commands"]:
            self.assertEqual(command["cwd"], str(self.project))
            self.assertNotIn("<temporary-replay>", " ".join(command["argv"]))
            self.assertEqual(command["exit_code"], 0)
        self.assertFalse(Path(report["commands"][2]["argv"][4]).exists())
        self.assertEqual(yaml.safe_load((self.workspace / "claims.yaml").read_text()), self.catalog)
        self.assertEqual(report["inputs_before"], report["inputs_after"])

    def test_audit_uses_registered_lean_4_19_prettyprinter_options(self):
        # Regression for pp.maxDepth: unlike pp.maxSteps it is not registered
        # in the official Lean 4.19 Delaborator/Options.lean. pp.all already
        # enables deep-term printing through getPPDeepTerms in that source.
        audit = self.call()["commands"][3]["stdin"]
        self.assertEqual(re.findall(r"set_option (\S+) (\S+)", audit), [
            ("pp.all", "true"), ("pp.maxSteps", "1000000"), ("pp.all", "false"),
        ])
        self.assertNotIn("pp.maxDepth", audit)

    def test_compact_failure_diagnostics_omit_hash_manifests_and_bound_output(self):
        report = self.call()
        report["commands"][0]["stdout"] = "x" * 100000
        report["commands"][1]["stdout"] = "y" * 100000
        report["axiom_audit"]["raw_output"] = "z" * 100000
        compact = self.compact_report(report)
        self.assertNotIn("inputs_before", compact)
        self.assertNotIn("inputs_after", compact)
        self.assertLess(len(json.dumps(compact)), 20000)

    def test_unavailable_binary_does_not_attempt_install_or_execute(self):
        (self.toolchain / "bin" / ("lean.exe" if replay_module.WINDOWS else "lean")).unlink()
        with patch.object(replay_module, "_run_command", side_effect=AssertionError("unavailable")):
            report = self.call(execute=True)
        self.assertEqual(report["status"], "unavailable")
        self.assertFalse(report["executed"])

    def test_shim_script_rejected(self):
        (self.toolchain / "bin" / ("lean.exe" if replay_module.WINDOWS else "lean")).write_text("#!/bin/sh\nexit 0\n")
        report = self.call(execute=True)
        self.assertEqual(report["status"], "unavailable")

    def test_explicit_pin_and_direct_installed_discovery(self):
        elan = self.root / "elan"
        installed = elan / "toolchains/leanprover--lean4---v4.19.0"
        installed.parent.mkdir(parents=True)
        self.toolchain.rename(installed)
        with patch.dict(os.environ, {"ELAN_HOME": str(elan)}):
            report = replay_module.replay(self.workspace, catalog="claims.yaml", claim="example-claim")
        self.assertTrue(report["preflight"]["ready"])
        self.assertEqual(report["commands"][0]["argv"][0], str(installed / "bin" / ("lean.exe" if replay_module.WINDOWS else "lean")))

    def test_native_windows_selection_and_timeout_caveat(self):
        (self.toolchain / "bin/lean.exe").write_bytes(b"MZ00synthetic native fixture")
        (self.toolchain / "bin/lean.exe").chmod(0o700)
        with patch.object(replay_module, "WINDOWS", True):
            report = self.call()
        self.assertTrue(report["preflight"]["ready"])
        self.assertTrue(report["commands"][0]["argv"][0].endswith("lean.exe"))
        self.assertTrue(any("descendant termination is not guaranteed" in warning for warning in report["warnings"]))

    def test_windows_timeout_uses_direct_process_kill_without_shell(self):
        command = replay_module._command(["synthetic-lean.exe"], self.project, {})
        process = unittest.mock.Mock()
        process.communicate.side_effect = [subprocess.TimeoutExpired("synthetic-lean.exe", 1), (None, None)]
        process.returncode = -1
        with patch.object(replay_module, "WINDOWS", True), patch.object(subprocess, "Popen", return_value=process) as mocked:
            self.assertFalse(replay_module._run_command(command, 1))
        process.kill.assert_called_once()
        self.assertFalse(mocked.call_args.kwargs.get("shell", False))
        self.assertFalse(mocked.call_args.kwargs["start_new_session"])
        self.assertEqual(command["status"], "timeout")

    def test_stable_pin_required_even_with_explicit_toolchain(self):
        (self.project / "lean-toolchain").write_text("leanprover/lean4:nightly\n")
        self.assertEqual(self.call(execute=True)["status"], "unavailable")

    def test_version_mismatch_stops_before_build(self):
        def runner(command, timeout):
            result = self.fake_run(command, timeout)
            command["stdout"] = "Lean (version 4.20.0, fixture)"
            return result
        report, mocked = self.execute(runner)
        self.assertEqual(mocked.call_count, 1)
        self.assertEqual(report["status"], "failed")
        self.assertEqual(report["commands"][2]["status"], "not-run")

    def test_missing_flags_stop_before_build(self):
        def runner(command, timeout):
            result = self.fake_run(command, timeout)
            if "--help" in command["argv"]:
                command["stdout"] = "unsupported help"
            return result
        report, mocked = self.execute(runner)
        self.assertEqual(mocked.call_count, 2)
        self.assertEqual(report["status"], "failed")

    def test_transitive_sorry_ax_is_failure(self):
        def runner(command, timeout):
            result = self.fake_run(command, timeout)
            if "--stdin" in command["argv"]:
                command["stdout"] = "'Example.ok' depends on axioms: [propext, sorryAx]"
            return result
        report, _ = self.execute(runner)
        self.assertEqual(report["status"], "failed")
        self.assertTrue(report["axiom_audit"]["sorry_ax"])

    def test_custom_axioms_are_exposed_not_approved(self):
        def runner(command, timeout):
            result = self.fake_run(command, timeout)
            if "--stdin" in command["argv"]:
                command["stdout"] = "'Example.ok' depends on axioms:\n [Classical.choice, Example.assumption]"
            return result
        report, _ = self.execute(runner)
        self.assertEqual(report["status"], "completed")
        self.assertEqual(report["axiom_audit"]["axioms"], ["Classical.choice", "Example.assumption"])
        self.assertTrue(report["axiom_audit"]["review_required"])
        self.assertEqual(report["approval"], "not-granted")

    def test_missing_or_ambiguous_axiom_output_is_not_success(self):
        for output in ["", "'Example.other' does not depend on any axioms", "'Example.ok' depends on axioms: [«odd name»]",
                       "'Example.ok' does not depend on any axioms\n'Example.ok' depends on axioms: [sorryAx]"]:
            def runner(command, timeout):
                result = self.fake_run(command, timeout)
                if "--stdin" in command["argv"]:
                    command["stdout"] = output
                return result
            with self.subTest(output=output):
                report, _ = self.execute(runner)
                self.assertEqual(report["status"], "failed")
                self.assertEqual(report["axiom_audit"]["status"], "unavailable")

    def test_failed_build_stops_audit(self):
        def runner(command, timeout):
            if "-o" in command["argv"]:
                command.update(status="failed", exit_code=1, stderr="synthetic type error")
                return False
            return self.fake_run(command, timeout)
        report, mocked = self.execute(runner)
        self.assertEqual(mocked.call_count, 3)
        self.assertEqual(report["status"], "failed")
        self.assertEqual(report["commands"][3]["status"], "not-run")
        self.assertEqual(report["axiom_audit"]["status"], "not-run")

    def test_failed_audit_is_not_labelled_not_run(self):
        def runner(command, timeout):
            if "--stdin" in command["argv"]:
                command.update(status="failed", exit_code=1, stderr="unknown declaration")
                return False
            return self.fake_run(command, timeout)
        report, _ = self.execute(runner)
        self.assertEqual(report["axiom_audit"]["status"], "failed")

    def test_changed_source_invalidates_success(self):
        def runner(command, timeout):
            result = self.fake_run(command, timeout)
            if "--stdin" in command["argv"]:
                self.source.write_text("-- changed during replay\n")
            return result
        report, _ = self.execute(runner)
        self.assertTrue(report["inputs_changed"])
        self.assertEqual(report["status"], "failed")

    def test_prepared_artifacts_and_source_are_hashed(self):
        library = self.project / ".lake/build/lib/lean"
        library.mkdir(parents=True)
        (library / "Imported.olean").write_bytes(b"prepared artifact")
        (library / "Imported.ilean").write_bytes(b"prepared metadata")
        report = self.call()
        files = report["inputs_before"]["project_files"]
        self.assertIn(".lake/build/lib/lean/Imported.olean", files)
        self.assertIn(".lake/build/lib/lean/Imported.ilean", files)
        self.assertIn("Example.lean", files)
        self.assertIn("lake-manifest.json", files)

    def dependency(self, *, revision="a" * 40, head=None):
        dependency = self.project / ".lake/packages/dep"
        (dependency / ".git").mkdir(parents=True)
        (dependency / ".git/HEAD").write_text(head or revision)
        (dependency / ".lake/build/lib/lean").mkdir(parents=True)
        (dependency / ".lake/build/lib/lean/Imported.olean").write_bytes(b"dependency fixture")
        (self.project / "lake-manifest.json").write_text(json.dumps({"packages": [
            {"name": "dep", "type": "git", "rev": revision, "subDir": None}]}))
        return dependency

    def test_pinned_prepared_dependency_is_inventoried(self):
        self.dependency()
        report = self.call()
        self.assertTrue(report["preflight"]["ready"])
        self.assertEqual(report["dependencies"][0]["actual_head"], "a" * 40)
        self.assertIn(".lake/packages/dep/.lake/build/lib/lean/Imported.olean", report["inputs_before"]["project_files"])

    def test_dependency_head_change_during_execution_is_failure(self):
        dependency = self.dependency()
        def runner(command, timeout):
            result = self.fake_run(command, timeout)
            if "--stdin" in command["argv"]:
                (dependency / ".git/HEAD").write_text("b" * 40)
            return result
        report, _ = self.execute(runner)
        self.assertEqual(report["status"], "failed")
        self.assertTrue(report["inputs_changed"])

    def test_missing_unpinned_or_wrong_revision_dependencies_never_fetch(self):
        for revision, head in [("main", None), ("a" * 40, "b" * 40)]:
            with self.subTest(revision=revision):
                directory = self.project / ".lake/packages/dep"
                if directory.exists():
                    # Fixtures are fresh between cases without destructive tree removal.
                    (directory / ".git/HEAD").write_text(head or revision)
                    (self.project / "lake-manifest.json").write_text(json.dumps({"packages": [
                        {"name": "dep", "type": "git", "rev": revision}]}))
                else:
                    self.dependency(revision=revision, head=head)
                self.assertEqual(self.call(execute=True)["status"], "unavailable")

    def test_ambiguous_dependency_module_is_unavailable(self):
        self.dependency()
        local = self.project / ".lake/build/lib/lean"
        local.mkdir(parents=True)
        (local / "Imported.olean").write_bytes(b"collision")
        self.assertEqual(self.call(execute=True)["status"], "unavailable")

    def test_symlinked_inputs_are_rejected(self):
        self.source.unlink()
        try:
            self.source.symlink_to(self.project / "lean-toolchain")
        except OSError as exc:
            self.skipTest(f"test host does not permit symlink creation: {exc}")
        with self.assertRaises(EvidenceError):
            self.call()

    def test_declaration_command_injection_and_escaped_names_rejected(self):
        for declaration in ["Example.ok\n#eval 1", "Example.ok;foo", "«name»", "Example.ok--", "_root_.Example.ok "]:
            with self.subTest(declaration=declaration):
                self.catalog["claims"]["example-claim"]["formal"]["declaration"] = declaration
                self.save_catalog()
                with self.assertRaises(EvidenceError):
                    self.call()

    def test_timeout_must_be_finite_positive(self):
        for timeout in [0, -1, float("inf"), float("nan"), True]:
            with self.subTest(timeout=timeout), self.assertRaises(EvidenceError):
                self.call(timeout=timeout)

    def test_real_subprocess_capture_no_shell_and_timeout(self):
        command = replay_module._command([sys.executable, "-c", "import sys; print('fixture stdout'); print('fixture stderr', file=sys.stderr)"], self.project, dict(os.environ))
        self.assertTrue(replay_module._run_command(command, 5))
        self.assertEqual(command["exit_code"], 0)
        self.assertIn("fixture stderr", command["stderr"])
        timeout = replay_module._command([sys.executable, "-c", "import time; time.sleep(10)"], self.project, dict(os.environ))
        self.assertFalse(replay_module._run_command(timeout, 0.05))
        self.assertEqual(timeout["status"], "timeout")

    def test_optional_real_lean_smoke(self):
        selected = os.environ.get("LABO_REPLAY_TOOLCHAIN_DIR")
        if not selected:
            if os.environ.get("LABO_REQUIRE_REAL_LEAN") == "1":
                self.fail("LABO_REQUIRE_REAL_LEAN=1 requires LABO_REPLAY_TOOLCHAIN_DIR")
            self.skipTest("prepared real Lean toolchain not selected; mock tests are not real Lean evidence")
        directory = Path(selected)
        version = subprocess.run([str(directory / "bin" / ("lean.exe" if replay_module.WINDOWS else "lean")), "--version"], capture_output=True, text=True, timeout=20, check=True)
        match = re.search(r"version (4\.[0-9]+\.[0-9]+)", version.stdout)
        self.assertIsNotNone(match)
        (self.project / "lean-toolchain").write_text(f"leanprover/lean4:v{match[1]}\n")
        for source, expected, axioms in [
            ("theorem Example.ok : True := True.intro\n", "completed", []),
            ("theorem Example.helper : True := by sorry\ntheorem Example.ok : True := Example.helper\n", "failed", ["sorryAx"]),
            ("axiom Example.assumption : True\ntheorem Example.ok : True := Example.assumption\n", "completed", ["Example.assumption"]),
        ]:
            with self.subTest(source=source):
                self.source.write_text(source)
                report = replay_module.replay(self.workspace, catalog="claims.yaml", claim="example-claim",
                                             toolchain_dir=directory, execute=True, timeout=120)
                self.assertEqual(report["status"], expected, self.compact_report(report))
                self.assertEqual(report["axiom_audit"]["axioms"], axioms, self.compact_report(report))


if __name__ == "__main__":
    unittest.main()
