import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

import yaml


PROJECT_ROOT = Path(__file__).resolve().parents[1]


@unittest.skipUnless(shutil.which("git"), "Git is required for actual submodule tests")
class SubmoduleRuntimeTests(unittest.TestCase):
    mount_name = ".agents"

    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.source = self.root / "policy-source"
        self.source.mkdir()
        shutil.copytree(
            PROJECT_ROOT / "src", self.source / "src",
            ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
        )
        shutil.copytree(PROJECT_ROOT / "skills", self.source / "skills")
        (self.source / "scripts").mkdir()
        shutil.copyfile(PROJECT_ROOT / "scripts" / "labo.py", self.source / "scripts" / "labo.py")
        cli = self.source / "src" / "labo_tools" / "cli.py"
        source = cli.read_text(encoding="utf-8")
        self.assertIn('prog="labo"', source)
        cli.write_text(source.replace('prog="labo"', 'prog="pinned-checkout-labo"', 1), encoding="utf-8")
        self.git(self.source, "init")
        self.commit_all(self.source, "Policy source fixture")

        self.workspace = self.root / "private-labo"
        self.workspace.mkdir()
        self.put_plan(self.workspace, "private-project")
        self.git(self.workspace, "init")
        self.commit_all(self.workspace, "Private workspace fixture")
        self.git(
            self.workspace, "-c", "protocol.file.allow=always", "submodule", "add",
            str(self.source), self.mount_name,
        )
        self.commit_all(self.workspace, "Pin policy submodule")
        self.mount = self.workspace / self.mount_name
        self.assertTrue((self.mount / ".git").is_file())
        self.launcher = self.mount / "scripts" / "labo.py"
        self.unrelated = self.root / "unrelated-directory"
        self.unrelated.mkdir()

    def git(self, cwd, *args):
        result = subprocess.run(
            ["git", "-C", str(cwd), "-c", "commit.gpgsign=false", *args],
            check=True, capture_output=True, text=True,
        )
        return result.stdout.strip()

    def commit_all(self, cwd, message):
        self.git(cwd, "add", "-A")
        self.git(
            cwd, "-c", "user.name=Runtime Test", "-c", "user.email=runtime@example.invalid",
            "commit", "-m", message,
        )

    def put_plan(self, workspace, slug):
        folder = workspace / "research" / slug
        folder.mkdir(parents=True)
        (folder / "plan.md").write_text(
            f"---\ntitle: {slug}\nsummary: Synthetic private research fixture\nstatus: in_progress\n---\n",
            encoding="utf-8",
        )

    def invoke(self, cwd, *args, launcher=None, isolated=True, env=None):
        command = [sys.executable, "-B"]
        if isolated:
            command.append("-I")
        command.extend([str(launcher or self.launcher), *args])
        return subprocess.run(command, cwd=cwd, env=env, capture_output=True, text=True)

    def test_default_workspace_is_superproject_from_any_working_directory(self):
        for cwd in (
            self.workspace,
            self.mount,
            self.mount / "skills" / "research-management",
            self.unrelated,
        ):
            with self.subTest(cwd=cwd):
                result = self.invoke(cwd, "research", "list", "--format", "json")
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(
                    [item["slug"] for item in json.loads(result.stdout)["research"]],
                    ["private-project"],
                )

    def test_explicit_workspace_overrides_superproject(self):
        alternate = self.root / "alternate workspace"
        self.put_plan(alternate, "other-project")
        result = self.invoke(
            self.mount, "research", "list", "--format", "json", "--workspace", str(alternate),
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["research"][0]["slug"], "other-project")

    def test_real_skill_directory_resolves_through_user_chosen_symlink(self):
        skill_link = self.workspace / "reading" / self.mount_name / "skills" / "research-management"
        skill_link.parent.mkdir(parents=True)
        try:
            skill_link.symlink_to(self.mount / "skills" / "research-management", target_is_directory=True)
        except (OSError, NotImplementedError) as exc:
            self.skipTest(f"directory symlinks are unavailable: {exc}")
        real_skill_directory = (skill_link / "SKILL.md").resolve().parent
        launcher = (real_skill_directory / ".." / ".." / "scripts" / "labo.py").resolve()
        self.assertEqual(launcher, self.launcher.resolve())
        result = self.invoke(self.unrelated, "research", "list", "--format", "json", launcher=launcher)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["research"][0]["slug"], "private-project")

    def test_copied_policy_tree_cannot_borrow_an_enclosing_submodule(self):
        copied = self.mount / "copied-policy"
        shutil.copytree(self.source / "src", copied / "src")
        shutil.copytree(self.source / "scripts", copied / "scripts")
        launcher = copied / "scripts" / "labo.py"
        result = self.invoke(self.unrelated, "research", "check", launcher=launcher)
        self.assertEqual(result.returncode, 2)
        self.assertIn("not its own Git checkout root", result.stderr)
        self.assertIn("--workspace", result.stderr)
        result = self.invoke(
            self.unrelated, "research", "check", "--workspace", str(self.workspace), launcher=launcher,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("1 research plan", result.stdout)

    def test_standalone_checkout_requires_explicit_workspace(self):
        standalone = self.source / "scripts" / "labo.py"
        result = self.invoke(self.workspace, "research", "check", launcher=standalone)
        self.assertEqual(result.returncode, 2)
        self.assertIn("--workspace", result.stderr)
        self.assertIn("not a Git submodule", result.stderr)
        result = self.invoke(
            self.unrelated, "research", "check", "--workspace", str(self.workspace), launcher=standalone,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("1 research plan", result.stdout)

    def test_launcher_uses_pinned_checkout_not_updated_origin_or_shadow_package(self):
        source_cli = self.source / "src" / "labo_tools" / "cli.py"
        source_cli.write_text(
            source_cli.read_text(encoding="utf-8").replace("pinned-checkout-labo", "new-origin-labo"),
            encoding="utf-8",
        )
        self.commit_all(self.source, "Advance origin without updating submodule")
        self.assertNotEqual(self.git(self.source, "rev-parse", "HEAD"), self.git(self.mount, "rev-parse", "HEAD"))
        shadow = self.root / "shadow-package" / "labo_tools"
        shadow.mkdir(parents=True)
        (shadow / "__init__.py").write_text("", encoding="utf-8")
        (shadow / "cli.py").write_text(
            'def main(*args, **kwargs):\n    print("wrong-environment-package")\n    return 0\n',
            encoding="utf-8",
        )
        env = dict(os.environ, PYTHONPATH=str(shadow.parent))
        result = self.invoke(self.unrelated, "--help", isolated=False, env=env)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("pinned-checkout-labo", result.stdout)
        self.assertNotIn("new-origin-labo", result.stdout)
        self.assertNotIn("wrong-environment-package", result.stdout)

    def test_module_command_still_works_with_explicit_workspace(self):
        env = dict(os.environ, PYTHONPATH=str(self.mount / "src"))
        command = [sys.executable, "-B", "-m", "labo_tools", "research", "check"]
        result = subprocess.run(
            [*command, "--workspace", str(self.workspace)],
            cwd=self.unrelated, env=env, capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        result = subprocess.run(command, cwd=self.workspace, env=env, capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)
        self.assertIn("--workspace", result.stderr)

    def test_layout_creation_uses_dependency_mount_without_host_runtime_copies(self):
        self.assertTrue((self.mount / "skills/labo-layout/SKILL.md").is_file())
        result = self.invoke(self.unrelated, "layout", "init")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((self.workspace / "inbox").is_dir())
        result = self.invoke(
            self.unrelated, "layout", "new", "research", "new-program",
            "--title", "Synthetic question", "--summary", "Synthetic context",
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((self.workspace / "research/new-program/plan.md").is_file())
        result = self.invoke(self.unrelated, "research", "check")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("2 research plan", result.stdout)
        self.assertEqual((self.workspace / "AGENTS.md").read_bytes(), b"")
        for name in ("scripts", "src", "skills", ".agents", ".claude"):
            if name != self.mount_name:
                with self.subTest(absent_host_copy=name):
                    self.assertFalse((self.workspace / name).exists())
        self.assertEqual(self.git(self.mount, "status", "--porcelain"), "")

    def test_evidence_workflow_uses_mounted_policy_and_private_workspace(self):
        catalog = "research/private-project/claims.yaml"
        evidence = "research/private-project/evidence.md"
        record = "research/private-project/review.yaml"
        result = self.invoke(self.unrelated, "evidence", "init", "--catalog", catalog)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(
            (self.workspace / catalog).read_bytes(),
            (self.mount / "skills/research-management/assets/claims.yaml").read_bytes(),
        )
        (self.workspace / evidence).write_text("Synthetic evidence, not a checked proof.\n", encoding="utf-8")
        (self.workspace / catalog).write_text(yaml.safe_dump({
            "schema_version": 1,
            "claims": {"scoped-example": {
                "statement": "Synthetic scoped claim.", "status": "unverified",
                "evidence": [evidence], "dependencies": [],
            }},
        }), encoding="utf-8")
        result = self.invoke(
            self.unrelated, "evidence", "snapshot", "--kind", "proof",
            "--catalog", catalog, "--claim", "scoped-example", "--file", evidence,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn(str(self.workspace), result.stdout)
        snapshot = yaml.safe_load(result.stdout)
        self.assertEqual(snapshot["verdict"], "pending")
        self.assertEqual(snapshot["catalog"], catalog)
        self.assertEqual(set(snapshot["claims"]), {"scoped-example"})
        self.assertEqual(snapshot["files"], {
            evidence: hashlib.sha256((self.workspace / evidence).read_bytes()).hexdigest(),
        })
        policy = "skills/research-management/references/evidence.md"
        standards = "skills/paper-referee/references/standards.md"
        self.assertEqual(snapshot["policy_inputs"], {
            path: hashlib.sha256((self.mount / path).read_bytes()).hexdigest()
            for path in (policy, standards)
        })
        for path in (snapshot["catalog"], *snapshot["files"], *snapshot["policy_inputs"]):
            self.assertFalse(Path(path).is_absolute())
            self.assertNotIn(self.mount_name, Path(path).parts)
        self.assertFalse((self.workspace / record).exists())
        (self.workspace / record).write_text(result.stdout, encoding="utf-8")

        def check_record(state, strict=False):
            result = self.invoke(
                self.unrelated, "evidence", "check", "--record", record, "--format", "json",
                *(("--strict",) if strict else ()),
            )
            self.assertEqual(result.returncode, 1 if strict else 0, result.stderr)
            checked = json.loads(result.stdout)
            self.assertEqual(checked["status"], "warning")
            self.assertEqual(checked["records"], [{"path": record, "state": state}])

        check_record("pending")
        policy_file = self.mount / policy
        original = policy_file.read_bytes()
        try:
            policy_file.write_bytes(original + b"\nSynthetic temporary policy change.\n")
            check_record("stale")
            check_record("stale", strict=True)
        finally:
            policy_file.write_bytes(original)
        check_record("pending")
        self.assertEqual(self.git(self.mount, "status", "--porcelain"), "")
        for name in ("scripts", "src", "skills", ".agents", ".claude"):
            if name != self.mount_name:
                self.assertFalse((self.workspace / name).exists())

    def test_scope_inventory_and_replay_plan_use_mount_without_host_runtime_writes(self):
        def put(name, text):
            path = self.workspace / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")

        main = "writing/example/main.tex"
        part = "writing/example/part.tex"
        catalog = "research/private-project/claims.yaml"
        put(main, "\\input{part}\n")
        put(part, "Synthetic private manuscript.\n")
        put("lean/example/Example.lean", "theorem Example.ok : True := True.intro\n")
        put("lean/example/lean-toolchain", "leanprover/lean4:v4.19.0\n")
        put("lean/example/lakefile.toml", 'name = "example"\n')
        put("lean/example/lake-manifest.json", '{"packages": []}\n')
        put(catalog, yaml.safe_dump({"schema_version": 1, "claims": {"example-claim": {
            "statement": "Synthetic fixture, not a checked research claim.", "status": "unverified",
            "formal": {"project": "lean/example", "source": "lean/example/Example.lean",
                       "declaration": "Example.ok", "kernel": {"verdict": "pending", "report": None},
                       "alignment": {"verdict": "pending", "report": None}},
        }}}))
        before = {
            path.relative_to(self.workspace).as_posix(): path.read_bytes()
            for directory in ("research", "writing", "lean")
            for path in (self.workspace / directory).rglob("*") if path.is_file()
        }
        result = self.invoke(self.unrelated, "evidence", "scope", "--paper", "example", "--format", "json")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual({item["path"] for item in json.loads(result.stdout)["dependencies"]}, {main, part})
        result = self.invoke(self.unrelated, "evidence", "scope", "--source", main,
                             "--file", main, "--strict")
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertIn("not covered by selected inputs: " + part, result.stdout)
        result = self.invoke(self.unrelated, "evidence", "status", "--research", "private-project",
                             "--format", "json")
        self.assertEqual(result.returncode, 0, result.stderr)
        inventory = json.loads(result.stdout)
        self.assertEqual(inventory["adoption"], "catalog")
        self.assertEqual(inventory["claims"][0]["id"], "example-claim")
        self.assertFalse(inventory["claims"][0]["has_current_proof_review"])
        result = self.invoke(self.unrelated, "evidence", "replay", "--catalog", catalog,
                             "--claim", "example-claim", "--toolchain-dir", str(self.root / "not-installed"),
                             "--format", "json")
        self.assertEqual(result.returncode, 0, result.stderr)
        plan = json.loads(result.stdout)
        self.assertEqual(plan["status"], "plan")
        self.assertFalse(plan["executed"])
        self.assertTrue(all(command["status"] == "not-run" for command in plan["commands"]))
        self.assertEqual(plan["approval"], "not-granted")
        after = {
            path.relative_to(self.workspace).as_posix(): path.read_bytes()
            for directory in ("research", "writing", "lean")
            for path in (self.workspace / directory).rglob("*") if path.is_file()
        }
        self.assertEqual(after, before)
        self.assertFalse((self.workspace / "research/private-project/reviews").exists())
        self.assertEqual(self.git(self.mount, "status", "--porcelain"), "")
        for name in ("scripts", "src", "skills", ".agents", ".claude", "policy-runtime"):
            if name != self.mount_name:
                self.assertFalse((self.workspace / name).exists())

    def test_staged_reading_uses_private_session_under_each_mount(self):
        source = "writing/example/reader.tex"
        session = "research/private-project/reviews/reader.json"
        spoiler = "MOUNTED_FUTURE_SPOILER_SENTINEL"
        path = self.workspace / source
        path.parent.mkdir(parents=True)
        original = "Visible first question.\nVisible second relation.\n" + spoiler + "\n"
        path.write_text(original, encoding="utf-8", newline="")
        target = self.workspace / session
        target.parent.mkdir()
        result = self.invoke(self.unrelated, "paper", "reading", "start", "--source", source,
                             "--session", session, "--reader", "Synthetic mount reader", "--format", "json")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["through_line"], 0)
        self.assertNotIn(spoiler, result.stdout)
        result = self.invoke(self.unrelated, "paper", "reading", "next", "--session", session,
                             "--through-line", "1")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "Visible first question.\n")
        frozen = target.read_bytes()
        result = self.invoke(self.unrelated, "paper", "reading", "next", "--session", session,
                             "--through-line", "2")
        self.assertEqual(result.returncode, 2)
        self.assertEqual(target.read_bytes(), frozen)
        result = self.invoke(self.unrelated, "paper", "reading", "observe", "--session", session,
                             "--understanding", "The visible text asks a question.",
                             "--confusion", "The object is unspecified.", "--format", "json")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(json.loads(result.stdout)["awaiting_observation"])
        result = self.invoke(self.unrelated, "paper", "reading", "next", "--session", session,
                             "--through-line", "2", "--format", "json")
        self.assertEqual(result.returncode, 0, result.stderr)
        exposed = json.loads(result.stdout)
        self.assertEqual(exposed["text"], "Visible first question.\nVisible second relation.\n")
        self.assertNotIn(spoiler, result.stdout)
        frozen = target.read_bytes()
        result = self.invoke(self.unrelated, "paper", "reading", "status", "--session", session)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("context independence is not certified", result.stdout)
        self.assertNotIn(spoiler, result.stdout)
        self.assertEqual(target.read_bytes(), frozen)
        self.assertEqual(path.read_text(encoding="utf-8"), original)
        self.assertEqual(self.git(self.mount, "status", "--porcelain"), "")
        for name in ("scripts", "src", "skills", ".agents", ".claude", "policy-runtime"):
            if name != self.mount_name:
                self.assertFalse((self.workspace / name).exists())


class ClaudeSubmoduleRuntimeTests(SubmoduleRuntimeTests):
    mount_name = ".claude"


class NamedSubmoduleRuntimeTests(SubmoduleRuntimeTests):
    # Git metadata, not a recognized agent-host directory name, identifies the workspace.
    mount_name = "policy-runtime"


if __name__ == "__main__":
    unittest.main()
