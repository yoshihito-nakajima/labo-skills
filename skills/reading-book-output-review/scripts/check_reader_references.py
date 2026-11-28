#!/usr/bin/env python3
"""Check numbered targets and index routes in a built card book (requires pypdf)."""

import argparse
from collections import Counter
from html.parser import HTMLParser
import json
from pathlib import Path
import re

from pypdf import PdfReader


class Reader(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = Counter()
        self.links = {}
        self.index_links = {}
        self.current_index = None
        self.link = None

    def handle_starttag(self, tag, attributes):
        attrs = dict(attributes)
        if key := attrs.get("id"):
            self.ids[key] += 1
        if tag == "h2":
            self.current_index = attrs.get("id")
        if tag == "a" and attrs.get("href", "").startswith("#"):
            self.link = (attrs["href"][1:], [])

    def handle_data(self, data):
        if self.link:
            self.link[1].append(data)

    def handle_endtag(self, tag):
        if tag == "a" and self.link:
            target, content = self.link
            text = "".join(content).strip()
            self.links.setdefault(target, set()).add(text)
            if self.current_index:
                self.index_links.setdefault(self.current_index, Counter())[target] += 1
            self.link = None


def require(condition, message):
    if not condition:
        raise ValueError(message)


def inspect(directory):
    labels = json.loads((directory / "reference-labels.json").read_text(encoding="utf-8"))
    registrations = json.loads((directory / "index-registrations.json").read_text(encoding="utf-8"))
    pdf = PdfReader(directory / "main.pdf")
    named = pdf.named_destinations
    pdf_links = Counter()
    links_per_page = []
    for page in pdf.pages:
        links = Counter()
        for obj in page.get("/Annots", []):
            ann = obj.get_object()
            if ann.get("/Subtype") != "/Link":
                continue
            action = ann.get("/A")
            if action and action.get("/S") != "/GoTo":
                continue
            target = action.get("/D") if action else ann.get("/Dest")
            if isinstance(target, str):
                require(target in named, f"Undefined PDF destination: {target}")
                links[target] += 1
        pdf_links.update(links)
        links_per_page.append(links)

    html = Reader()
    html.feed((directory / "reader.html").read_text(encoding="utf-8"))
    require(all(count == 1 for count in html.ids.values()), "Duplicate HTML ids")
    missing = html.links.keys() - html.ids.keys()
    require(not missing, f"Missing HTML fragment targets: {sorted(missing)}")
    # Catalog destinations must occur on the printed catalog pages, even if the
    # same label is also reached by a body reference.
    bookmarks = {item.title: pdf.get_destination_page_number(item)
                 for item in pdf.outline if not isinstance(item, list)}
    titles = {"terms": "用語索引", "formulas": "記号・主要式索引",
              "statements": "定義・定理・演習一覧", "equations": "数式番号一覧"}

    def section_links(group):
        start = bookmarks[titles[group]]
        end = min((page for page in bookmarks.values() if page > start), default=len(pdf.pages))
        found = Counter()
        for page in links_per_page[start:end]:
            found.update(page)
        return found

    directory_links = {group: section_links(group) for group in ("statements", "equations") if titles[group] in bookmarks}
    aux = (directory / "main.aux").read_text(encoding="utf-8")
    for key, stamp in labels.items():
        number, kind = stamp["number"], stamp["kind"]
        html_id, dest = stamp["html_id"], stamp["destination"]
        equation = kind == "equation"
        group = "equations" if equation else "statements"
        require(dest in directory_links.get(group, {}), f"Missing PDF catalog link: {key} -> {dest}")
        require(pdf.get_destination_page_number(named[dest]) + 1 == int(stamp["page"]),
                f"Wrong PDF target page for {key}: {dest}")
        require(re.search(r"^\\newlabel\{" + re.escape(key) + r"@cref\}\{\{\[" + kind + r"\]", aux, re.M),
                f"Wrong cleveref type for {key}: expected {kind}")
        last_index = "equation-index" if equation else "statement-index"
        require(html_id in html.index_links.get(last_index, {}), f"Missing HTML catalog link: {key}")
        require(any(text.endswith(number) or text.endswith(f"({number})") for text in html.links[html_id]),
                f"Wrong HTML reference number for {key}: expected {number}")

    aux_dests = dict(re.findall(
        r"^\\newlabel\{([^{}]+)\}\{\{[^{}]*\}\{[^{}]+\}\{.*\}\{([^{}]+)\}\{[^{}]*\}\}$", aux, re.M))
    for group, key, macro, html_group in (
        ("terms", "index", "indexref", "term-index"),
        ("formulas", "formula_index", "formulaindexref", "formula-index"),
    ):
        entries = [entry for entry in registrations if entry["kind"] == key]
        if not entries:
            continue
        wanted = Counter(entry["label"] for entry in entries)
        idx = (directory / f"{group}.idx").read_text(encoding="utf-8")
        ind = (directory / f"{group}.ind").read_text(encoding="utf-8")
        generated = Counter(re.findall(r"\|" + macro + r"\{([^{}]+)\}", idx))
        printed = set(re.findall(r"\\" + macro + r"\{([^{}]+)\}", ind))
        require(wanted <= generated, f"Some {group} registrations never reached the index")
        require(wanted.keys() <= printed, f"Some {group} labels were omitted from the built index")
        page_links = section_links(group)
        for entry in entries:
            label = entry["label"]
            dest = aux_dests.get(label)
            require(dest in page_links, f"Missing PDF index link: {entry['term']} -> {label}")
            require(entry["html_id"] in html.index_links.get(html_group, {}),
                    f"Missing HTML index link: {entry['term']} -> {entry['html_id']}")
            if group == "formulas":
                require(labels.get(label, {}).get("kind") == "equation",
                        f"Formula index points outside the equation: {entry['term']} -> {label}")

    return {"pages": len(pdf.pages), "numbered_objects": dict(Counter(s["kind"] for s in labels.values())),
            "index_entries": dict(Counter(r["kind"] for r in registrations)),
            "pdf_named_links": sum(pdf_links.values()), "html_targets": len(html.links)}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--build", type=Path, required=True, help="directory containing matching TeX, PDF and HTML outputs")
    args = parser.parse_args()
    try:
        print(json.dumps(inspect(args.build), ensure_ascii=False, indent=2))
    except (KeyError, ValueError, OSError) as exc:
        parser.exit(1, f"{exc}\n")
