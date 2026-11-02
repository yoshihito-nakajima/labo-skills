"""Check metadata and portable ownership routes, not narrative quality."""

from pathlib import Path
import re
import shutil
import tempfile
import unittest

import yaml


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills/paper-introduction/SKILL.md"


def targets(path):
    return re.findall(r"\[[^\]\n]+\]\(([^)\s]+)\)", path.read_text(encoding="utf-8"))


class IntroductionRouteTests(unittest.TestCase):
    def test_entry_points_resolve_to_the_new_skill(self):
        for owner in ("README.md", "skills/paper-writing/SKILL.md",
                      "skills/research-router/SKILL.md"):
            with self.subTest(owner=owner):
                source = ROOT / owner
                resolved = [(source.parent / target).resolve() for target in targets(source)
                            if "paper-introduction" in target]
                self.assertEqual(resolved, [SKILL.resolve()])

    def test_owned_workflows_resolve_under_both_mounts(self):
        expected = {
            "skills/research-router/references/consultation.md",
            "skills/research-router/references/editing-capability.md",
            "skills/paper-writing/SKILL.md",
            "skills/reading-reference/SKILL.md",
            "skills/reading-reference/references/research-positioning.md",
            "skills/mathematical-exposition/SKILL.md",
        }
        with tempfile.TemporaryDirectory() as folder:
            for mount in (".agents", ".claude"):
                with self.subTest(mount=mount):
                    checkout = (Path(folder) / mount).resolve()
                    shutil.copytree(ROOT / "skills", checkout / "skills")
                    source = checkout / "skills/paper-introduction/SKILL.md"
                    resolved = set()
                    for target in targets(source):
                        self.assertFalse(Path(target).is_absolute())
                        self.assertNotIn(":", target)
                        self.assertNotIn("\\", target)
                        destination = (source.parent / target).resolve()
                        self.assertTrue(destination.is_relative_to(checkout.resolve()))
                        self.assertTrue(destination.is_file())
                        resolved.add(destination.relative_to(checkout).as_posix())
                    self.assertEqual(resolved, expected)

    def test_metadata_matches_the_skill(self):
        text = SKILL.read_text(encoding="utf-8")
        metadata = yaml.safe_load(text.split("---", 2)[1])
        self.assertEqual(set(metadata), {"name", "description"})
        self.assertEqual(metadata["name"], "paper-introduction")
        self.assertNotIn("TODO", text)
        interface = yaml.safe_load((SKILL.parent / "agents/openai.yaml").read_text(
            encoding="utf-8"))["interface"]
        self.assertIn("$paper-introduction", interface["default_prompt"])
        self.assertTrue(25 <= len(interface["short_description"]) <= 64)


if __name__ == "__main__":
    unittest.main()
