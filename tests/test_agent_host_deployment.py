"""Three deployments from the sole distributed policy Git submodule."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import tomllib
import unittest

import yaml


CHECKOUT = Path(__file__).resolve().parents[1]


@unittest.skipUnless(shutil.which("git"), "Git is required for actual submodule tests")
class DistributedHostTests(unittest.TestCase):
    def git(self, cwd, *args):
        return subprocess.run(["git", "-C", str(cwd), "-c", "commit.gpgsign=false",
                               "-c", "user.name=Host Test", "-c", "user.email=host@example.invalid",
                               *args], check=True, capture_output=True, text=True).stdout.strip()

    def invoke(self, workspace, script, cwd, host):
        return subprocess.run([sys.executable, "-B", "-I", str(script), "--workspace", str(workspace),
                               "--host", host, "--model", "gpt-6-astra" if host == "codex" else "claude-opus-5-5",
                               "--effort", "high", "--apply"], cwd=cwd, capture_output=True, text=True)

    def test_native_agents_native_claude_and_whole_directory_alias(self):
        for mode in ("codex", "claude", "both"):
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as directory:
                container = Path(directory)
                source = container / "source"
                shutil.copytree(CHECKOUT, source, ignore=shutil.ignore_patterns(
                    ".git", "__pycache__", ".venv", "*.pyc"))
                self.git(source, "init")
                self.git(source, "add", "-A")
                self.git(source, "commit", "-m", "Distributed policy fixture")
                workspace = container / "host workspace with spaces"
                workspace.mkdir()
                self.git(workspace, "init")
                self.git(workspace, "commit", "--allow-empty", "-m", "Host fixture")
                mount_name = ".claude" if mode == "claude" else ".agents"
                self.git(workspace, "-c", "protocol.file.allow=always", "submodule", "add", str(source), mount_name)
                self.git(workspace, "commit", "-am", "Pin policy")
                policy = workspace / mount_name
                self.assertTrue((policy / ".git").is_file())
                if mode == "both":
                    (workspace / ".claude").symlink_to(".agents", target_is_directory=True)
                self.assertFalse((workspace / ".codex").exists())
                script = policy / "skills/agent-host-setup/scripts/install_roles.py"
                hosts = ("codex", "claude") if mode == "both" else (mode,)
                for host in hosts:
                    result = self.invoke(workspace, script, container, host)
                    self.assertEqual(result.returncode, 0, result.stderr)
                    expected = 3 if host == "codex" else 0  # Claude roles ship natively.
                    self.assertEqual(len(json.loads(result.stdout)["create"]), expected)
                    again = self.invoke(workspace, script, container, host)
                    self.assertEqual(again.returncode, 0, again.stderr)
                    self.assertEqual(json.loads(again.stdout)["create"], [])
                if mode == "codex":
                    self.assertFalse((workspace / ".claude").exists())
                if mode == "claude":
                    self.assertFalse((workspace / ".agents").exists())
                    self.assertFalse((workspace / ".codex").exists())
                if mode in {"claude", "both"}:
                    native = workspace / ".claude"
                    self.assertEqual(native.is_symlink(), mode == "both")
                    self.assertTrue((native / "skills/agent-host-setup/SKILL.md").is_file())
                    self.assertTrue(all(not path.is_symlink() for path in (native / "skills").iterdir()))
                    settings = json.loads((native / "settings.json").read_text())
                    self.assertEqual(settings["env"]["CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH"], "2")
                    for path in (native / "agents").glob("math-*.md"):
                        front, prompt = path.read_text().split("---", 2)[1:]
                        metadata = yaml.safe_load(front)
                        self.assertEqual(metadata["model"], "claude-opus-5-5")
                        self.assertEqual(metadata["skills"], [path.stem])
                        self.assertTrue((native / "skills" / path.stem / "SKILL.md").is_file())
                launcher = policy / "scripts/labo.py"
                run = subprocess.run([sys.executable, "-B", "-I", str(launcher), "--help"],
                                     cwd=container, capture_output=True, text=True)
                self.assertEqual(run.returncode, 0, run.stderr)
                self.assertEqual(self.git(policy, "status", "--porcelain"), "")
                relocated = container / "relocated workspace"
                shutil.move(workspace, relocated)
                # Exercise __file__.resolve() through the alias in combined mode.
                entry = ".claude" if mode == "both" else mount_name
                script = relocated / entry / "skills/agent-host-setup/scripts/install_roles.py"
                for host in hosts:
                    result = self.invoke(relocated, script, container, host)
                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertEqual(json.loads(result.stdout)["create"], [])
                role = relocated / (".claude/agents/math-decomposer.md" if mode == "claude"
                                    else ".codex/agents/math-decomposer.toml")
                if mode != "claude":
                    prompt = tomllib.loads(role.read_text())["developer_instructions"]
                    self.assertIn(".agents/skills/math-decomposer/SKILL.md", prompt)
                    self.assertNotIn(str(workspace), prompt)
                role.write_text("user customized role\n")
                result = self.invoke(relocated, script, container, "claude" if mode == "claude" else "codex")
                self.assertEqual(result.returncode, 2)
                self.assertEqual(role.read_text(), "user customized role\n")
