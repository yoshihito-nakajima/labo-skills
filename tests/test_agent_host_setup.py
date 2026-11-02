import importlib.util
from pathlib import Path
import tempfile
import tomllib
import unittest

import yaml


CHECKOUT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("install_roles", CHECKOUT / "skills/agent-host-setup/scripts/install_roles.py")
roles = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(roles)


class HostRoleTests(unittest.TestCase):
    def mounted(self, root, mount):
        policy = root / mount
        contract = policy / "skills/research-router/references/mathematical-roles.md"
        contract.parent.mkdir(parents=True)
        contract.write_text("synthetic contract")
        for name in roles.ROLES:
            target = policy / "skills" / name / "SKILL.md"
            target.parent.mkdir(parents=True)
            target.write_text((CHECKOUT / "skills" / name / "SKILL.md").read_text())
        return policy

    def test_native_fields_and_contract_without_settings_mutation(self):
        for mode in ("codex", "claude", "both"):
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                mount = ".claude" if mode == "claude" else ".agents"
                policy = self.mounted(root, mount)
                if mode == "both":
                    (root / ".claude").symlink_to(".agents", target_is_directory=True)
                hosts = ("codex", "claude") if mode == "both" else (mode,)
                for host in hosts:
                    model = "claude-opus-5-5" if host == "claude" else "gpt-6-astra"
                    settings = root / (".claude/settings.json" if host == "claude" else ".codex/config.toml")
                    settings.parent.mkdir(exist_ok=True)
                    settings.write_text("synthetic existing primary and permissions")
                    files = roles.render_roles(root, host, model, "high", policy)
                    for content in files.values():
                        if host == "codex":
                            data = tomllib.loads(content)
                            self.assertEqual(data["model_reasoning_effort"], "high")
                            prompt = data["developer_instructions"]
                        else:
                            data = yaml.safe_load(content.split("---", 2)[1])
                            self.assertEqual(data["effort"], "high")
                            prompt = content.split("---", 2)[2]
                            if data["name"] == "math-verifier":
                                self.assertNotIn("Agent", data["tools"])
                                self.assertNotIn("Write", data["tools"])
                        self.assertEqual(data["model"], model)
                        if host == "claude":
                            self.assertEqual(data["skills"], [data["name"]])
                        else:
                            self.assertIn(f"{mount}/skills/{data['name']}/SKILL.md", prompt)
                    self.assertEqual(len(roles.install(files)), 3)
                    self.assertTrue(all(not path.exists() for path in files))
                    self.assertEqual(len(roles.install(files, apply=True)), 3)
                    self.assertEqual(roles.install(files, apply=True), [])
                    self.assertEqual(settings.read_text(), "synthetic existing primary and permissions")
                if mode == "codex":
                    self.assertFalse((root / ".claude").exists())
                if mode == "claude":
                    self.assertFalse((root / ".agents").exists())
                    self.assertFalse((root / ".codex").exists())

    def test_collision_is_checked_before_any_role_is_written(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            policy = self.mounted(root, ".agents")
            files = roles.render_roles(root, "codex", "gpt-6-astra", "high", policy)
            last = list(files)[-1]
            last.parent.mkdir(parents=True)
            last.write_text("user customized role")
            with self.assertRaisesRegex(ValueError, "preserve existing"):
                roles.install(files, apply=True)
            self.assertEqual(last.read_text(), "user customized role")
            self.assertFalse(list(files)[0].exists())

    def test_adapters_take_description_from_enabled_role_skill(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            policy = self.mounted(root, ".claude")
            path = policy / "skills/math-proof-worker/SKILL.md"
            text = path.read_text()
            front, body = text.split("---", 2)[1:]
            data = yaml.safe_load(front)
            data["description"] = "Synthetic revised task interface"
            path.write_text("---\n" + yaml.safe_dump(data) + "---\n" + body)
            for host, model in (("codex", "gpt-6-astra"), ("claude", "claude-opus-5-5")):
                files = roles.render_roles(root, host, model, "high", policy)
                output = next(value for path, value in files.items() if path.stem == "math-proof-worker")
                adapter = tomllib.loads(output) if host == "codex" else yaml.safe_load(output.split("---", 2)[1])
                self.assertEqual(adapter["description"], data["description"])
            data["disable-model-invocation"] = True
            path.write_text("---\n" + yaml.safe_dump(data) + "---\n" + body)
            with self.assertRaisesRegex(ValueError, "enabled preload"):
                roles.render_roles(root, "claude", "claude-opus-5-5", "high", policy)

    def test_claude_skill_and_native_entry_do_not_select_each_other(self):
        for name in roles.ROLES:
            metadata = yaml.safe_load((CHECKOUT / "skills" / name / "SKILL.md").read_text().split("---", 2)[1])
            self.assertEqual(metadata["context"], "fork")
            self.assertEqual(metadata["agent"], "general-purpose")
            self.assertEqual(metadata["model"], "claude-opus-5-5")
            self.assertEqual(metadata["effort"], "high")
            self.assertNotIn(metadata["agent"], roles.ROLES)
            self.assertIsNot(metadata.get("disable-model-invocation"), True)
            native = yaml.safe_load((CHECKOUT / "agents" / f"{name}.md").read_text().split("---", 2)[1])
            self.assertEqual(native["skills"], [name])
            self.assertNotIn("context", native)
            self.assertEqual(native["description"], metadata["description"])

    def test_claude_generation_preserves_absent_or_unrelated_directory(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            policy = self.mounted(root, ".agents")
            with self.assertRaisesRegex(ValueError, "whole-directory"):
                roles.render_roles(root, "claude", "claude-opus-5-5", "high", policy)
            self.assertFalse((root / ".claude").exists())
            (root / ".claude").mkdir()
            (root / ".claude/user.txt").write_text("preserve me")
            with self.assertRaisesRegex(ValueError, "whole-directory"):
                roles.render_roles(root, "claude", "claude-opus-5-5", "high", policy)
            self.assertEqual((root / ".claude/user.txt").read_text(), "preserve me")

    def test_symlink_escape_and_restricted_model_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory, tempfile.TemporaryDirectory() as outside:
            root = Path(directory)
            policy = self.mounted(root, ".agents")
            for model in ("", "gpt-6-luna"):
                with self.assertRaises(ValueError):
                    roles.render_roles(root, "codex", model, "high", policy)
            files = roles.render_roles(root, "codex", "gpt-6-astra", "high", policy)
            (root / ".codex").mkdir()
            (root / ".codex/agents").symlink_to(outside)
            with self.assertRaisesRegex(ValueError, "escapes"):
                roles.install(files, apply=True)
            self.assertEqual(list(Path(outside).iterdir()), [])
