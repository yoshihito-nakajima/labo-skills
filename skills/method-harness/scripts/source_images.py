"""Build optional section-level facsimiles from a version-pinned local PDF."""

from hashlib import sha256
from html import escape
import json
from math import ceil, floor, isfinite
from pathlib import Path, PurePosixPath
import re
import subprocess
from tempfile import TemporaryDirectory

from PIL import Image


class SourceImages:
    """Render ordered PDF regions whose coordinates are points from the top left."""

    ASSETS = PurePosixPath("assets/original-sections")
    SCALE = 2  # 144 DPI = 2 pixels per PDF point.

    def __init__(self, root, manifest, output, pdf_href, section_pages):
        data = json.loads((root.root / manifest).read_text(encoding="utf-8"))
        source = root.cards[data["source"]]
        pdf = (root.root / source.get("file")).resolve(strict=True)
        if not source.get("sha256") == data["sha256"] == sha256(pdf.read_bytes()).hexdigest():
            raise ValueError(f"{manifest}: 原著 PDF の指紋が一致しない")
        sections = data["sections"]
        if sections.keys() != section_pages.keys():
            raise ValueError(f"{manifest}: 原文画像と通読の節が一致しない")
        destination = output / self.ASSETS
        destination.mkdir(parents=True, exist_ok=True)
        self.pdf_href = pdf_href
        self.fragments = {section: [] for section in sections}
        by_page = {}
        for section, regions in sections.items():
            if not re.fullmatch(r"[a-z]+|\d+(?:\.\d+)*", section):
                raise ValueError(f"{manifest}: 不正な節 ID {section}")
            previous = section_pages[section]
            for index, (page, left, top, right, bottom) in enumerate(regions, 1):
                if (type(page) is not int or page < 1 or page < previous
                        or (index == 1 and page != previous)):
                    raise ValueError(f"{manifest}: {section} の原著 PDF ページ順が不正")
                if (not all(type(v) in {int, float} and isfinite(v)
                            for v in (left, top, right, bottom))
                        or not (0 <= left < right and 0 <= top < bottom)):
                    raise ValueError(f"{manifest}: {section} p.{page} の範囲が不正")
                name = f"{section.replace('.', '-')}-{index}.png"
                rect = (floor(left * self.SCALE), floor(top * self.SCALE),
                        ceil(right * self.SCALE), ceil(bottom * self.SCALE))
                self.fragments[section].append((page, name, rect[2] - rect[0], rect[3] - rect[1]))
                by_page.setdefault(page, []).append((name, rect))
                previous = page
            if not regions:
                raise ValueError(f"{manifest}: {section} に原文画像がない")

        with TemporaryDirectory(prefix="method-source-") as tmp:
            prefix = Path(tmp) / "page"
            subprocess.run(
                ["pdftoppm", "-hide-annotations", "-f", str(min(by_page)), "-l", str(max(by_page)),
                 "-r", str(72 * self.SCALE), "-png", str(pdf), str(prefix)], check=True,
            )
            rendered = {int(path.stem.rsplit("-", 1)[1]): path for path in prefix.parent.glob("page-*.png")}
            for page, regions in by_page.items():
                if page not in rendered:
                    raise ValueError(f"{manifest}: 原著 PDF に p.{page} がない")
                with Image.open(rendered[page]) as image:
                    for name, rect in regions:
                        if rect[2] > image.width or rect[3] > image.height:
                            raise ValueError(f"{manifest}: {name} が原著 PDF p.{page} の範囲外")
                        image.crop(rect).save(destination / name)

    def html(self, section):
        fragments = self.fragments[section]
        start, end = fragments[0][0], fragments[-1][0]
        pages = f"p.{start}" if start == end else f"pp.{start}–{end}"
        anchor = "ja-source-" + section.replace(".", "-")
        images = []
        for index, (page, name, width, height) in enumerate(fragments, 1):
            label = f"原著 PDF p.{page}"
            if len(fragments) > 1:
                label += f"（{index}/{len(fragments)}）"
            href = escape(self.pdf_href, quote=True) + f"#page={page}"
            images.append(
                f'<figure data-original-page="{page}">'
                f'<figcaption><a href="{href}">{label}</a></figcaption>'
                f'<img src="{self.ASSETS / name}" alt="{label}の該当箇所" loading="lazy" '
                f'width="{width}" height="{height}"></figure>'
            )
        return (
            f'<details class="original-section" id="{anchor}" data-original-section="{section}">'
            f'<summary>原文画像（{pages}）</summary>{"".join(images)}</details>'
        )

    def links(self, section):
        """The same regions as plain links that open each image by itself, for a reading without folds."""
        fragments = self.fragments[section]
        anchor = "ja-source-" + section.replace(".", "-")
        items = []
        for index, (page, name, width, height) in enumerate(fragments, 1):
            label = f"p.{page}" + (f"（{index}/{len(fragments)}）" if len(fragments) > 1 else "")
            items.append(f'<a href="{self.ASSETS / name}" target="_blank" rel="noopener" '
                         f'data-original-page="{page}" data-size="{width}x{height}">{label}</a>')
        return (f'<p class="source-page original-links" id="{anchor}" data-original-section="{section}">'
                f'原文画像 {" ".join(items)}</p>')
