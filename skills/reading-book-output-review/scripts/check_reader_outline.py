#!/usr/bin/env python3
"""Compare a chaptered route with PDF and HTML navigation."""
from __future__ import annotations

import argparse
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
import re
import subprocess
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "src"))

from labo_tools.book import Book, route_outline
from labo_tools.book_reader import NAMES


class Reader(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = Counter()
        self.links = []
        self.toc = []
        self.headings = []
        self.heading = None

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if target := attrs.get("id"):
            self.ids[target] += 1
            if tag in ("h2", "h3") and target.startswith(("chapter-", "sec-")):
                self.heading = (target, [])
        if (href := attrs.get("href", "")).startswith("#"):
            self.links.append(href[1:])
            if attrs.get("class") in ("toc-chapter", "toc-section"):
                self.toc.append(href[1:])

    def handle_data(self, data):
        if self.heading:
            self.heading[1].append(data)

    def handle_endtag(self, tag):
        if self.heading and tag in ("h2", "h3"):
            target, text = self.heading
            self.headings.append((target, compact("".join(text))))
            self.heading = None


def compact(text):
    return "".join(text.split()).replace(r'\"', '"')


# Ignore printed page numbers, index headings and any deeper subsection rows.
# The bare chapter form is used by the standard English book class.
TOC_NUMBER = re.compile(
    r"^[ \t]*(?:第\s*(\d+)\s*章|(?:Chapter|Appendix|付録)\s*([A-Z]|\d+)"
    r"|([A-Z]\.\d+|\d+\.\d+|[A-Z]|\d+))(?=[ \t]+\S)", re.M
)


def check_printed_toc(pdf, pages, expected):
    first, last = pages
    text = subprocess.run(["pdftotext", "-f", str(first), "-l", str(last), "-layout", str(pdf), "-"],
                          capture_output=True, text=True, check=True).stdout
    actual = [next(group for group in match.groups() if group is not None)
              for match in TOC_NUMBER.finditer(text)]
    if actual != expected:
        for position, (wanted, got) in enumerate(zip(expected, actual), start=1):
            if wanted != got:
                raise ValueError(f"Printed PDF TOC entry {position}: expected {wanted}, found {got}")
        raise ValueError(f"Printed PDF TOC: expected {len(expected)} numbered entries, found {len(actual)}")


def check_outline(book, slug, pdf, html, language, toc_pages=None):
    data = book.load_route(slug)
    if not data.get("hierarchical"):
        raise ValueError(f"{slug}: expected a chaptered route")
    entries = [x for x in book.sequence(data)
               if x["id"] in book.cards and book.cards[x["id"]].kind.startswith(("A", "B"))]
    rows = route_outline(data, (entry["section"] for entry in entries)).values()
    expected_html, expected_pdf, expected_numbers = [], [], []
    for row in rows:
        if chapter := row.get("chapter"):
            number = chapter["number"]
            expected_numbers.append(number)
            appendix = chapter.get("appendix")
            if appendix:
                prefix = f"{NAMES[language]['appendix']} {number}"
            else:
                prefix = f"第{number}章" if language == "ja" else f"Chapter {number}"
            title = compact(prefix + (chapter["title"] or ""))
            expected_html.append((f"chapter-{chapter['id']}", title))
            destination = f"{'appendix' if appendix else 'chapter'}.{number}"
            chapter_title = compact(chapter["title"] or "")
            expected_pdf.append((destination, {title, chapter_title, number + chapter_title}))
        section_title = compact(row["title"] or ("補足資料" if language == "ja" else "Supplement"))
        title = row["number"] + section_title
        expected_numbers.append(row["number"])
        expected_html.append((row["id"], title))
        expected_pdf.append((f"section.{row['number']}", {title, section_title}))

    reader = Reader()
    reader.feed(html.read_text(encoding="utf-8"))
    if reader.headings != expected_html or reader.toc != [key for key, _ in expected_html]:
        raise ValueError("HTML heading titles, order or TOC differs from the route")
    duplicates = sorted(key for key, count in reader.ids.items() if count > 1)
    missing = sorted(set(reader.links) - reader.ids.keys())
    if duplicates or missing:
        raise ValueError(f"HTML anchors: duplicate {duplicates}, missing {missing}")

    outline = subprocess.run(["mutool", "show", str(pdf), "outline"],
                             capture_output=True, text=True, check=True).stdout
    # Glossaries and indexes also have bookmarks. The numbered route hierarchy uses
    # chapter.*, appendix.* and section.* destinations, distinct from those unnumbered entries.
    pdf_headings = [(destination, compact(title)) for title, destination in re.findall(
        r'"(.*)"\s+#nameddest=((?:chapter|appendix|section)\.[\w.]+)\s*$', outline, flags=re.M)]
    if (len(pdf_headings) != len(expected_pdf)
            or any(actual_id != expected_id or actual_title not in titles
                   for (actual_id, actual_title), (expected_id, titles) in zip(pdf_headings, expected_pdf))):
        raise ValueError(f"PDF bookmark titles or order differs from the route: {len(pdf_headings)} "
                         f"found, {len(expected_pdf)} expected")
    if toc_pages:
        check_printed_toc(pdf, toc_pages, expected_numbers)
    return len(expected_pdf), len(reader.links)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--route", required=True)
    parser.add_argument("--pdf", type=Path, required=True)
    parser.add_argument("--html", type=Path, required=True)
    parser.add_argument("--language", choices=("ja", "en"), default="ja")
    parser.add_argument("--toc-pages", type=int, nargs=2, metavar=("FIRST", "LAST"),
                        help="inclusive physical pages of the printed PDF contents (requires pdftotext)")
    args = parser.parse_args()
    if args.toc_pages and not 1 <= args.toc_pages[0] <= args.toc_pages[1]:
        parser.error("--toc-pages expects positive physical page numbers in ascending order")
    try:
        headings, links = check_outline(Book(args.root, use_cache=False), args.route,
                                        args.pdf, args.html, args.language, args.toc_pages)
    except (ValueError, OSError, subprocess.CalledProcessError) as exc:
        parser.exit(1, f"{exc}\n")
    prints = ", printed PDF TOC numbering matches" if args.toc_pages else ""
    print(f"{args.route}: {headings} matching chapter/section headings, {links} valid HTML fragments{prints}")


if __name__ == "__main__":
    main()
