"""Check portable instruction links, not agents' literature-search quality."""

from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = ROOT / "skills/reading-reference/references/research-positioning.md"
TEMPLATE = ROOT / "skills/reading-reference/assets/research-positioning.md"
OWNER_ROUTES = (
    "skills/reading-reference/SKILL.md",
    "skills/research-router/SKILL.md",
    "skills/research-management/SKILL.md",
    "skills/research-management/references/research-policy.md",
    "skills/paper-writing/SKILL.md",
    "skills/paper-referee/SKILL.md",
    "skills/paper-referee/references/standards.md",
    "skills/slide-authoring/SKILL.md",
    "skills/reading-reference/references/source-rules.md",
    "skills/reading-reference/references/research-program-synthesis.md",
    "README.md",
)


def markdown_targets(path):
    return re.findall(r"\[[^\]\n]+\]\(([^)\s]+)\)", path.read_text(encoding="utf-8"))


def heading_anchors(path):
    # These two resources deliberately use simple, distinct English headings.
    headings = re.findall(r"^#{1,6} (.+)$", path.read_text(encoding="utf-8"), re.MULTILINE)
    return {re.sub(r"[^\w -]", "", title.lower()).replace(" ", "-") for title in headings}


class PositioningRouteTests(unittest.TestCase):
    def test_owners_route_to_one_checkout_local_protocol(self):
        self.assertTrue(PROTOCOL.is_file())
        for relative in OWNER_ROUTES:
            with self.subTest(owner=relative):
                owner = ROOT / relative
                targets = [target for target in markdown_targets(owner)
                           if target.split("#", 1)[0].endswith((
                               "references/research-positioning.md",
                               "assets/research-positioning.md",
                               "../research-positioning.md",
                               )) or target == "research-positioning.md"]
                self.assertTrue(targets, "Positioning route is missing")
                resolved = []
                for target in targets:
                    path = target.split("#", 1)[0]
                    self.assertFalse(Path(path).is_absolute())
                    self.assertNotIn(":", path, "Route must not depend on a URL or drive")
                    self.assertNotIn("\\", path)
                    resolved.append((owner.parent / path).resolve())
                self.assertIn(PROTOCOL.resolve(), resolved)
                self.assertTrue(all(path in (PROTOCOL.resolve(), TEMPLATE.resolve())
                                    for path in resolved))

    def test_protocol_links_resolve_and_reuse_the_owned_template(self):
        targets = markdown_targets(PROTOCOL)
        self.assertIn("../assets/research-positioning.md", targets)
        for target in targets:
            with self.subTest(target=target):
                path, _, anchor = target.partition("#")
                destination = (PROTOCOL.parent / path).resolve() if path else PROTOCOL
                self.assertTrue(destination.is_relative_to(ROOT.resolve()))
                self.assertTrue(destination.is_file())
                if anchor:
                    self.assertIn(anchor, heading_anchors(destination))

    def test_memo_can_be_copied_without_checkout_relative_links(self):
        self.assertTrue(TEMPLATE.is_file())
        # The populated memo belongs to the consuming research workspace. Its
        # starter navigation must not assume the policy is mounted at .agents.
        for target in markdown_targets(TEMPLATE):
            with self.subTest(target=target):
                self.assertTrue(target.startswith("#"))
                self.assertIn(target[1:], heading_anchors(TEMPLATE))


if __name__ == "__main__":
    unittest.main()
