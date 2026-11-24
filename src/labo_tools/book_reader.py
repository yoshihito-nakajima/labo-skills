"""Reader-facing HTML assembled from a book route."""

from __future__ import annotations

import hashlib
import html
import re
from collections import Counter
from itertools import groupby
from pathlib import Path

from .book import (BOLD_MD, BY_RE, LIST_LINE, MENTION_RE, Book, Card, card_environment, card_label,
                   require_route_dependencies, route_outline)
from .book_html import INDEX_MACROS, MATHJAX
from .book_review import MATH
from .book_equations import Equations, TEX_REF, display_math, fields
from .reading_page import render_reading_page

FRAGMENT_ASSET = Path(__file__).resolve().parent / "assets/book_reader_links.js"

NAMES = {
    "ja": {"axiom": "公理", "corollary": "系", "definition": "定義", "example": "例", "exercise": "演習",
           "lemma": "補題", "proposition": "命題", "theorem": "定理", "convention": "規約", "proof": "証明",
           "solution": "解答", "appendix": "付録"},
    "en": {"axiom": "Axiom", "corollary": "Corollary", "definition": "Definition", "example": "Example",
           "exercise": "Exercise", "lemma": "Lemma", "proposition": "Proposition", "theorem": "Theorem",
           "convention": "Convention", "proof": "Proof", "solution": "Solution", "appendix": "Appendix"},
}
BODY_FIELDS = {
    "A5": ("question",),
}


def _plain(text: str, link, label_to_id: dict[str, str]) -> str:
    text = html.escape(text, quote=False)
    text = BOLD_MD.sub(r"<strong>\1</strong>", text)
    text = re.sub(r"\\textbf\{([^{}]*)\}", r"<strong>\1</strong>", text)
    text = re.sub(r"\\emph\{([^{}]*)\}", r"<em>\1</em>", text)
    text = BY_RE.sub(lambda m: "（" + "、".join(link(cid.strip()) for cid in m[1].split(",")) + "）", text)
    text = MENTION_RE.sub(lambda m: link(m[1]), text)

    def tex_ref(match):
        labels = match[2].split(",")
        if all(label.strip() in label_to_id for label in labels):
            return "、".join(link(label_to_id[label.strip()], match[1]) for label in labels)
        return match[0]

    return TEX_REF.sub(tex_ref, text)


def _blocks(text: str, link, label_to_id: dict[str, str], math_nodes=()) -> str:
    """Format the card's paragraphs and lists while keeping TeX math opaque."""
    math = []

    def hold_math(match):
        math.append(html.escape(match[0], quote=False))
        return f"\x00{len(math) - 1}\x00"

    text = INDEX_MACROS.sub("", MATH.sub(hold_math, text))
    out, lines, items, list_tag = [], [], [], ""

    def inline(value):
        value = _plain(value, link, label_to_id)
        value = re.sub(r"\x00(\d+)\x00", lambda m: math[int(m[1])], value)
        return re.sub(r"\x01(\d+)\x01", lambda m: math_nodes[int(m[1])], value)

    def flush_paragraph():
        if lines:
            out.append(f'<p>{inline(" ".join(lines))}</p>')
            lines.clear()

    def flush_list():
        if items:
            out.append(f"<{list_tag}>" + "".join(f"<li>{inline(item)}</li>" for item in items) + f"</{list_tag}>")
            items.clear()

    for line in text.splitlines():
        match = LIST_LINE.match(line)
        if match and not line.startswith("\\"):
            flush_paragraph()
            tag = "ol" if match[1] else "ul"
            if tag != list_tag:
                flush_list()
                list_tag = tag
            items.append(match[2])
        elif items and line.strip() and line.startswith((" ", "\t")):
            items[-1] += " " + line.strip()
        else:
            flush_list()
            if line.strip():
                lines.append(line.strip())
            else:
                flush_paragraph()
    flush_list()
    flush_paragraph()
    return "".join(out)


def _identity(card: Card, seen: set[str]) -> str:
    cid = html.escape(card.id)
    anchor = "" if card.id in seen else f' id="{cid}"'
    seen.add(card.id)
    return f'{anchor} data-card="{cid}"'


def build_reader(book: Book, route: str, *, language: str = "ja", mathjax_bundle: str | None = None,
                 tex_numbers: dict[str, str] | None = None) -> str:
    """Use the L4 reading order, with the same shared counter as the default TeX build."""
    names = NAMES[language]
    data = book.load_route(route)
    cards = book.cards
    sequence = book.sequence(data)
    require_route_dependencies(book, data, sequence)
    entries = [e for e in sequence if e["id"] in cards and cards[e["id"]].kind.startswith(("A", "B"))]
    shown = {e["id"] for e in entries}
    labels = {card_label(cards[cid]): cid for cid in shown}
    typed = data.get("typed_navigation", False)
    equations = Equations([cards[e["id"]] for e in entries], strict=typed, enabled=typed)
    labels.update({label: label for label in equations.selected})
    tex_numbers = tex_numbers or {}
    outline = route_outline(data, (e["section"] for e in entries))
    numbers = Counter()
    refs = {}
    eq_numbers, equation_count = {}, Counter()
    for entry in entries:
        section = entry["section"]
        for formula in equations.by_card[entry["id"]]:
            label = formula.label
            if label in equations.selected and label not in eq_numbers:
                equation_count[section] += 1
                eq_numbers[label] = tex_numbers.get(label, f"{outline[section]['number']}.{equation_count[section]}")
    for entry in entries:
        card = cards[entry["id"]]
        section = entry["section"]
        env = card_environment(card)
        if env:
            numbers[section] += 1
            prefix = outline[section]["number"]
            number = tex_numbers.get(card_label(card), f"{prefix}.{numbers[section]}")
            refs.setdefault(card.id, f"{names.get(env, env)} {number}")
        elif card.kind == "A6":
            refs[card.id] = str(card.meta.get("title") or names["convention"])

    def link(cid, style="cref"):
        if cid in eq_numbers:
            number = eq_numbers[cid]
            label = number if style == "ref" else f"({number})" if style == "eqref" else (
                f"式({number})" if language == "ja" else f"Equation ({number})")
        else:
            label = refs.get(cid, str(cards[cid].meta.get("title") or cid) if cid in cards else cid)
        label = html.escape(label)
        return f'<a class="ref" href="#{html.escape(cid)}">{label}</a>' if cid in shown or cid in eq_numbers else label

    def content(card, keys):
        marked = []

        def emit(formula):
            kind = "display" if formula.display else "inline"
            math = display_math(formula)
            def ref_in_math(match):
                ids = [label.strip() for label in match[2].split(",")]
                if not all(label in eq_numbers for label in ids):
                    return match[0]
                return r",\ ".join(r"\href{#" + label + "}{" +
                    (f"({eq_numbers[label]})" if match[1] != "ref" else eq_numbers[label]) + "}" for label in ids)
            math = html.escape(TEX_REF.sub(ref_in_math, math), quote=False)
            left, right = (r"\[", r"\]") if formula.display else (r"\(", r"\)")
            id_attr = f' id="{formula.label}"' if formula.label not in seen_equations else ""
            seen_equations.add(formula.label)
            marked.append(f'<span class="book-equation equation-{kind}"{id_attr}>'
                          f'{left}{math}{right}<a class="equation-number" href="#{formula.label}">'
                          f'({eq_numbers[formula.label]})</a></span>')
            return f"\x01{len(marked) - 1}\x01"

        text = "\n\n".join(equations.rewrite(card, key, emit) for key in keys if card.sections.get(key))
        return _blocks(text, link, labels, marked)

    def proof(card, identity, title):
        return f'<details class="proof"{identity}><summary>{title}</summary>{content(card, fields(card))}</details>'

    toc, body, seen, seen_equations = [], [], set(), set()
    for section, group in groupby(entries, key=lambda e: e["section"]):
        view = outline[section]
        if chapter := view.get("chapter"):
            ordinal = chapter["number"]
            if chapter.get("appendix"):
                prefix = f"{names['appendix']} {ordinal}"
            else:
                prefix = f"第{ordinal}章" if language == "ja" else f"Chapter {ordinal}"
            heading = chapter["title"]
            title = html.escape(f"{prefix}　{heading}" if heading else prefix)
            target = f"chapter-{chapter['id']}"
            toc.append(f'<a class="toc-chapter" href="#{target}">{title}</a>')
            body.append(f'<h2 id="{target}">{title}</h2>')
        heading = view["title"]
        if heading is None:
            heading = names["appendix"] if view.get("legacy_appendix") else (
                "補足資料" if language == "ja" else "Supplement")
        target = view["id"]
        title = html.escape(f"{view['number']}　{heading}")
        level = "h3" if data.get("hierarchical") else "h2"
        css = ' class="toc-section"' if data.get("hierarchical") else ""
        toc.append(f'<a{css} href="#{target}">{title}</a>')
        body.append(f'<{level} id="{target}">{title}</{level}>')
        items = [cards[e["id"]] for e in group]
        index = 0
        while index < len(items):
            card = items[index]
            ident = _identity(card, seen)
            index += 1
            if card.kind.startswith("B"):
                body.append(f'<section class="prose"{ident}>{content(card, BODY_FIELDS.get(card.kind, fields(card)) if not card.legacy else fields(card))}</section>')
                continue
            if card.kind == "A3":
                owner = str(card.meta.get("proves", ""))
                title = f'{names["proof"]} {link(owner)}' if owner else names["proof"]
                body.append(proof(card, ident, title))
                continue
            env = card_environment(card) or "convention"
            heading = html.escape(refs.get(card.id, names.get(env, env)))
            card_title = str(card.meta.get("title") or "") if env != "convention" else ""
            label = f'<span class="kname">{heading}</span>'
            if card_title:
                label += f'（{html.escape(card_title)}）'
            article = [f'<article class="card k-{html.escape(env)}"{ident}><header>{label}</header>',
                       f'<div class="stmt">{content(card, BODY_FIELDS.get(card.kind, fields(card)) if not card.legacy else fields(card))}</div>']
            if card.kind == "A5" and card.sections.get("solution"):
                article.append(f'<details class="proof"><summary>{names["solution"]}</summary>'
                               f'{content(card, ("solution",))}</details>')
            while index < len(items) and items[index].kind == "A3" and items[index].meta.get("proves") == card.id:
                following = items[index]
                article.append(proof(following, _identity(following, seen), names["proof"]))
                index += 1
            body.append("".join(article) + "</article>")
    def index_term(term):
        # Index metadata uses the same inline TeX notation as the card body.
        value = html.escape(term)
        return re.sub(r"\$([^$]+)\$", lambda m: r"\(" + m[1] + r"\)", value)

    terms, formulas = [], []
    for cid in dict.fromkeys(e["id"] for e in entries):
        for key, target_list in (("index", terms), ("formula_index", formulas)):
            for item in cards[cid].meta.get(key) or []:
                item = item if isinstance(item, dict) else {"term": item}
                target = item.get("target") or cid
                target_list.append((item.get("reading") or item["term"], item["term"], target))
    ja = language == "ja"
    catalog_title = "定義・定理・演習一覧" if ja else "Definitions, theorems and exercises"
    groups = (
        ("term-index", "用語索引" if ja else "Term index", terms),
        ("formula-index", "記号・主要式索引" if ja else "Formula index", formulas),
        ("statement-index", catalog_title, [(str(i).zfill(8), cards[cid].meta.get("title") or cid, cid)
            for i, cid in enumerate(dict.fromkeys(e["id"] for e in entries))
            if card_environment(cards[cid])]),
        ("equation-index", "数式番号一覧" if ja else "Equation numbers",
         [(str(i).zfill(8), "", label) for i, label in enumerate(eq_numbers)]),
    )
    for target, title, items in groups:
        if items:
            toc.append(f'<a href="#{target}">{title}</a>')
            body.append(f'<h2 id="{target}">{title}</h2><ul class="book-index">')
            for _, term, cid in sorted(items):
                body.append(f'<li>{index_term(str(term))} {link(cid)}</li>')
            body.append("</ul>")
    text = "\n".join(body)
    heading = html.escape(str(data["title"]))
    digest = hashlib.sha256(f"{heading}\n{text}".encode()).hexdigest()[:12]
    style = ("<style>.equation-display{display:block;position:relative;padding-inline-end:3.6em}"
             ".equation-display .equation-number{position:absolute;right:0;top:50%;transform:translateY(-50%)}"
             ".equation-inline .equation-number{font-size:.76em;vertical-align:super;padding-inline-start:.18em}"
             ".book-index li{margin-block:.3em}</style>")
    page = render_reading_page(heading, language, "".join(toc), style + text, mathjax=MATHJAX,
                               mathjax_bundle=mathjax_bundle, width_em=36, version=f"{route} / {digest}")
    script = FRAGMENT_ASSET.read_text(encoding="utf-8")
    return page.removesuffix("</body></html>") + f"<script>\n{script}</script></body></html>"
