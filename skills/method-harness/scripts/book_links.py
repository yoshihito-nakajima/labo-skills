"""Resolve and render authored book cards at their point of use."""

from __future__ import annotations

from dataclasses import dataclass
from functools import cache
from pathlib import Path
import re
import subprocess
import sys
import tomllib
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from labo_tools.book import Book, Card


# The workspace holding local/ book roots: the nearest ancestor of the harness root with .agents or .git.
# Tests may set WORKSPACE directly.
WORKSPACE = None
LABO_LIBRARY = Path(__file__).resolve().parents[3] / "src"


def find_workspace(root):
    root = Path(root).resolve()
    for directory in (root, *root.parents):
        if (directory / ".agents").is_dir() or (directory / ".git").exists():
            return directory
    return root
NAME = re.compile(r"[a-z][a-z0-9-]*")
BOOK_VERSION = re.compile(r"sha256:[0-9a-f]{64}")


@dataclass(frozen=True)
class BookSelection:
    version: str
    route: str
    book: Book
    card: Card
    proof: Card | None


class BookReferences:
    def __init__(self, root):
        self.configs = tomllib.loads((Path(root) / "harness.toml").read_text(encoding="utf-8")).get(
            "book_harnesses", {}
        )
        self.snapshots = {}
        self.route_ids = {}
        self.workspace = WORKSPACE or find_workspace(root)

    def resolve(self, ref):
        namespace, separator, card = ref.partition(":")
        if not separator or not NAME.fullmatch(card) or namespace not in self.configs:
            raise ValueError(f"未登録の本のカード参照 {ref}")
        config = self.configs[namespace]
        route, location = config.get("route"), config.get("root")
        if (not isinstance(route, str) or not NAME.fullmatch(route)
                or not isinstance(location, str) or not location.strip()):
            raise ValueError(f"{namespace}: 本の root と route が必要")
        root = (self.workspace / location).resolve()
        if not root.is_relative_to(self.workspace / "local"):
            raise ValueError(f"{namespace}: 本のカードルートは workspace の local/ 内に置く")
        if namespace not in self.snapshots:
            library = str(LABO_LIBRARY)
            if library not in sys.path:
                sys.path.insert(0, library)
            from labo_tools.book import Book
            from labo_tools.book_borrows import BorrowSnapshots

            book = Book(root, use_cache=False)
            self.snapshots[namespace] = BorrowSnapshots(book)
            self.route_ids[namespace] = {item["id"] for item in book.sequence(book.load_route(route))}
        snapshots = self.snapshots[namespace]
        version = snapshots.version(route, card)
        book = snapshots.book
        proof = next((p for p in book.proofs_of(card) if p.id in self.route_ids[namespace]), None)
        return BookSelection(version, route, book, book.cards[card], proof)


@cache
def book_markdown_html(content: str) -> str:
    rendered = subprocess.run(
        ["pandoc", "--from=markdown+tex_math_single_backslash-raw_html-raw_tex-auto_identifiers",
         "--to=html", "--mathml", "--wrap=none"],
        input=content, text=True, encoding="utf-8", capture_output=True, check=True,
    ).stdout
    return re.sub(r"(?:</?a|<img)\b[^>]*>", "", rendered)


def book_card_html(selection: BookSelection, card: Card) -> str:
    """Use the card's own text and show citations as titles without opening a book page."""
    from labo_tools.book import BY_RE, MENTION_RE
    from labo_tools.book_equations import LABEL, MATH, TEX_REF
    from labo_tools.book_html import INDEX_MACROS

    def title(card_id):
        referenced = selection.book.cards.get(card_id)
        return str(referenced.meta.get("title") or card_id) if referenced else card_id

    def reference(match):
        labels = (label.strip() for label in match[2].split(","))
        return "、".join("「" + title(label.split(":")[1]) + "」の式" if label.startswith("eq:")
                        else "「" + title(label) + "」" for label in labels)

    def math(match):
        display, dollars, env, _, native, inline, single = match.groups()
        value = next(item for item in (display, dollars, native, inline, single) if item is not None)
        value = LABEL.sub("", value).strip()
        if env == "align":
            value = r"\begin{aligned}" + value + r"\end{aligned}"
        elif env in {"gather", "multline"}:
            value = r"\begin{gathered}" + value + r"\end{gathered}"
        if any(item is not None for item in (display, dollars, env)):
            return f"\n\n$$\n{value}\n$$\n\n"
        return f"${value}$"

    if card.legacy:
        fields = (("body", "", ""),)
    else:
        fields = card.template.required + card.template.optional
    sections = []
    for key, heading, _ in fields:
        text = card.sections.get(key)
        if not text:
            continue
        text = BY_RE.sub(lambda m: "（" + "・".join(title(cid.strip()) for cid in m[1].split(",")) + "）", text)
        text = MENTION_RE.sub(lambda m: "「" + title(m[1]) + "」", text)
        text = TEX_REF.sub(reference, text)
        text = MATH.sub(math, INDEX_MACROS.sub("", text))
        sections.append((f"**{heading}**\n\n" if heading else "") + text)
    if not sections:
        raise ValueError(f"{card.id}: 表示する本文がない")
    return book_markdown_html("\n\n".join(sections))
