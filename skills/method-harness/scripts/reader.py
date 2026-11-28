"""Render the source map's reading aids and links back from the other views."""

from html import escape
from html.parser import HTMLParser
from pathlib import Path
import re
from shutil import copy2
from textwrap import dedent

import method
from book_links import BookReferences, book_card_html
from hashlib import sha256
import yaml
from claim_readings import ClaimReadings, KINDS, ORIGIN_RELATIONS, POINT_KINDS, REALIZATION_KINDS
from lineage import CODE_KINDS, STATUS as LINEAGE_STATUS
from passages import (
    CODE_REASON_SECTIONS, check_reader_fact, code_reason_section, load_writing_fact,
    reader_options, reading_blocks, writing_namespaces,
)


RETURN_JS = """<script>
function openReadingAid() {
  let target = document.getElementById(location.hash.slice(1));
  if (target?.classList.contains('passage-figure') && !target.getClientRects().length) {
    target = document.getElementById(target.id + '--reading') || target;
  }
  if (!target) return;
  if (target.matches('[data-reading-ref]')) {
    const evidence = target.querySelector(':scope > details, :scope > article details');
    if (evidence) evidence.open = true;
  }
  const own = target.querySelector(':scope > details.section-fold');
  if (own) own.open = true;
  const foldSelector = 'details.reading-aid, details.evidence, details.math-aid, details.original-section, details.section-fold';
  let fold = target.closest(foldSelector);
  if (!fold) { if (own) target.scrollIntoView(); return; }
  while (fold) {
    fold.open = true;
    fold = fold.parentElement.closest(foldSelector);
  }
  target.scrollIntoView();
}
addEventListener('hashchange', openReadingAid);
addEventListener('DOMContentLoaded', () => {
  openReadingAid();
  const selector = 'details.ordered-reading, details.evidence, details.section-fold';
  const sections = [...document.querySelectorAll('[data-reader-section]')];
  for (const link of document.querySelectorAll('.view-nav a, .toc-views a')) {
    const destination = link.getAttribute('href');
    if (!['faithful.html', 'index.html'].includes(destination) || link.getAttribute('aria-current')) continue;
    link.addEventListener('click', () => {
      let current;
      for (const node of sections) {
        if (node.getBoundingClientRect().top > 165) break;
        current = node;
      }
      link.setAttribute('href', current ? destination + '#' + current.id : destination);
    });
  }
  for (const toggle of document.querySelectorAll('[data-reading-toggle]')) {
    const section = toggle.closest('[data-reader-section]')?.dataset.readerSection;
    const scopes = section ?
      sections.filter(node => node.dataset.readerSection === section ||
        node.dataset.readerSection.startsWith(section + '.')) : [document];
    const blocks = scopes.flatMap(node => [...node.querySelectorAll(selector)]);
    if (!blocks.length) continue;
    const update = () => {
      const expanded = blocks.every(block => block.open);
      toggle.textContent = (section ? 'この節を' : 'すべての節を') + (expanded ? '閉じる' : '開く');
      toggle.setAttribute('aria-expanded', String(expanded));
    };
    toggle.hidden = false;
    toggle.addEventListener('click', () => {
      const open = !blocks.every(block => block.open);
      blocks.forEach(block => { block.open = open; });
      update();
    });
    blocks.forEach(block => block.addEventListener('toggle', update));
    update();
  }
});
</script>"""


class PassageLocations(HTMLParser):
    """Locate the end of top-level paragraphs and the direct items of each algorithm."""

    VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param",
            "source", "track", "wbr"}

    def __init__(self, html):
        super().__init__()
        self.offsets = [0, *(m.end() for m in re.finditer("\n", html))]
        self.stack = []
        self.paragraphs = []
        self.equations = {}
        self.algorithms = {}
        self.algorithm_ends = {}
        self.pending = None
        self.algorithm = None
        self.equation_numbers = []
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        if tag in self.VOID:
            return
        if tag == "ol" and not self.stack:
            self.algorithm, self.pending = self.pending, None
        self.stack.append(tag)

    def handle_startendtag(self, tag, attrs):
        pass

    def handle_data(self, data):
        if self.stack == ["p", "strong"]:
            title = re.match(r"Algorithm (\d+)：", data)
            if title:
                self.pending = int(title[1])
        if self.stack[-1:] == ["mtext"]:
            equation = re.fullmatch(r"\(原(\d+)\)", data)
            if equation:
                self.equation_numbers.append(int(equation[1]))

    def handle_endtag(self, tag):
        if not self.stack or self.stack[-1] != tag:
            return
        self.stack.pop()
        row, column = self.getpos()
        start = self.offsets[row - 1] + column
        end = start + len(tag) + 3
        if tag == "li" and self.stack == ["ol"] and self.algorithm:
            self.algorithms.setdefault(self.algorithm, []).append(start)
        if tag == "ol" and not self.stack:
            if self.algorithm:
                self.algorithm_ends[self.algorithm] = end
            self.algorithm = None
        if tag == "p" and not self.stack:
            self.paragraphs.append(end)
            self.equations.update((number, end) for number in self.equation_numbers)
            self.equation_numbers.clear()

    def position(self, at):
        if at.get("heading"):
            return 0
        if "paragraph" in at:
            return self.paragraphs[at["paragraph"] - 1]
        if "equation" in at:
            return self.equations[at["equation"]]
        return self.algorithms[at["algorithm"]][at["step"] - 1]


def locator_label(at):
    if at.get("heading"):
        return f'§{at["section"]} 見出し'
    if "paragraph" in at:
        return f'§{at["section"]} 第{at["paragraph"]}段落'
    if "equation" in at:
        return f'§{at["section"]} 式(原{at["equation"]})'
    return f'§{at["section"]}・手順{at["step"]}'


PROOFS_PAGE = "proofs.html"
METHODS_PAGE = "methods.html"


def section_key(passage):
    return tuple(map(int, str(passage["at"]["section"]).split(".")))


class PassageViews:
    def __init__(self, root, web, *, code_route):
        self.root = method.Root(root)
        self.web = web
        self.books = BookReferences(self.root.root)
        self.claims = ClaimReadings(self.root.root)
        self.namespaces = writing_namespaces(root)
        self.options = reader_options(root)
        diagnostics = method.check(self.root)
        if any(level == "ERR" for level, *_ in diagnostics):
            raise ValueError("\n".join(f"{issue} {card}: {message}" for _, issue, card, message in diagnostics))
        self.stale = {}
        for _, code, card, message in diagnostics:
            if code in {"STALE", "STALE-PASSAGE"}:
                self.stale.setdefault(card, []).append(message)
        self.passages = [
            (card.id, passage)
            for card in self.root.cards.values() if card.kind == "map"
            for passage in card.get("passages", [])
        ]
        self.appendices = bool(self.options.get("appendices", False))
        self.fact_pages = self.options.get("fact_page", "paper.html")
        if self.appendices:
            self.fact_pages = PROOFS_PAGE
        self.code_ids = set(method.route_ids(self.root, code_route))
        self.figure_assets = {}
        self.facts = {}
        if self.appendices:
            self.assign_numbers()

    @staticmethod
    def figure_anchor(passage, link):
        return link["anchor"] if "anchor" in link else f'{passage["id"]}-{link["card"]}'

    def show_figure_inline(self, link):
        if "display" in link:
            return link["display"] == "inline"
        return self.options.get("inline_figures", False) or link.get("inline_image", False)

    def writing_fact(self, ref):
        if ref not in self.facts:
            self.facts[ref] = load_writing_fact(self.root.root, method.WRITING_CARDS, ref, self.namespaces)
        return self.facts[ref]

    def figures_in(self, section):
        anchors = {}
        for _, passage in self.passages:
            if str(passage["at"]["section"]) != section:
                continue
            for link in passage["links"]:
                if link["role"] == "figure" and self.show_figure_inline(link):
                    anchors.setdefault(link["card"], self.figure_anchor(passage, link))
        return anchors

    def return_links(self, role, identifier):
        items = []
        for _, passage in self.passages:
            for link in passage["links"]:
                if link["role"] != role or link["card"] != identifier:
                    continue
                anchor = passage["id"]
                if role == "figure" and self.show_figure_inline(link):
                    anchor = self.figure_anchor(passage, link)
                href = f'index.html#{anchor}'
                items.append(f'<a href="{href}">通読 {locator_label(passage["at"])}に戻る</a>')
                break
        return '<p class="passage-back">' + " · ".join(items) + "</p>" if items else ""

    def figure_html(self, passage, link, captions, *, in_reading=False, faithful=False):
        identifier = link["card"]
        card = self.root.cards[identifier]
        if identifier not in self.figure_assets:
            source = self.root.root / card.get("image")
            asset = Path("assets/translation") / (identifier + source.suffix.lower())
            target = self.web / asset
            target.parent.mkdir(parents=True, exist_ok=True)
            copy2(source, target)
            from PIL import Image  # only figure cards need Pillow
            with Image.open(source) as image:
                self.figure_assets[identifier] = asset, *image.size
        href = f'figures.html#c-{identifier}'
        title = escape(link.get("label", card.get("title")))
        panel = escape(link["panel"])
        anchor = self.figure_anchor(passage, link)
        alt = escape(card.get("alt"), quote=True)
        caption = captions.get(anchor, "")
        if in_reading:
            anchor += "--reading"
        asset, width, height = self.figure_assets[identifier]
        image_size = f'width="{width}" height="{height}"'
        if "crop" in link:
            left, top, right, bottom = link["crop"]
            if right > width or bottom > height:
                raise ValueError(f"{anchor}: 図の範囲が画像を超えている")
            frame_width, frame_height = right - left, bottom - top
            image_html = (
                f'<div class="figure-frame" style="max-width:{frame_width}px;aspect-ratio:{frame_width}/{frame_height}">'
                f'<img src="{asset}" alt="{alt}［{panel}］" loading="lazy" {image_size} '
                f'style="width:{width / frame_width:.6%};margin-left:{-left / frame_width:.6%};'
                f'transform:translateY({-top / height:.6%})"></div>'
            )
        else:
            image_html = f'<img src="{asset}" alt="{alt}" loading="lazy" {image_size}>'
        if faithful:
            return (
                f'<details class="evidence source-figure" id="{anchor}"><summary>{title}を表示</summary>'
                f'{image_html}</details>{caption}'
            )
        cue_label = "" if in_reading else '<strong>図の見方</strong> '
        content = (
            f'{image_html}<figcaption><p><strong>{title}</strong> <span class="figure-panel">{panel}</span></p>'
            f'<p class="figure-cue">{cue_label}{escape(link["text"])}</p>{caption}'
            f'<p class="figure-source"><a href="{href}">図の出典と参照箇所</a></p></figcaption>'
        )
        if self.options.get("fold_evidence", False) and not self.appendices:
            return (
                f'<details class="passage-figure evidence" id="{anchor}" data-figure-card="{identifier}">'
                f'<summary>{title} {panel}</summary><figure>{content}</figure></details>'
            )
        return (
            f'<figure class="passage-figure" id="{anchor}" data-figure-card="{identifier}">'
            f'{content}</figure>'
        )

    def fact_context(self, fact, latex, *, include_code=True):
        ordered = self.options.get("ordered_reading", False)
        if self.options.get("structured_facts", False):
            check_reader_fact(self.root, fact, require_goal=not ordered)

        def part(key, heading, extra=""):
            text = fact.sec(key)
            if not text:
                return ""
            return (f'<section class="fact-context" data-fact-part="{key}">'
                    f'<p class="fact-part-heading">{heading}</p>{latex(text)}{extra}</section>')

        before = part("Setup", "設定")
        if not ordered:
            before += part("Goal", "示したいこと" if fact.kind != "definition" else "定義する目的")
        if not include_code:
            return before, ""
        snippets = "".join(self.code_excerpt(ref["card"], ref["line"], ref.get("through"))
                           for ref in fact.meta.get("reader_code", []))
        return before, part("In code", "コードではどうなるか", snippets)

    def code_excerpt(self, identifier, line, through=None, *, preserve_indent=False):
        card = self.root.cards[identifier]
        code, error = self.root.code_lines(card)
        if error:
            raise ValueError(error)
        first = card.get("code")["lines"][0]
        last = through if through is not None else line
        source = "\n".join(code[line - first:last - first + 1])
        line_text = escape(source if preserve_indent else dedent(source).strip())
        line_label = f"{line}–{last}" if last != line else str(line)
        href = f'code.html#c-{identifier}-L{line}'
        title = escape(card.get("title"))
        return (f'<div class="code-excerpt"><p><a href="{href}">{title}（{line_label}行）</a></p>'
                f'<pre><code>{line_text}</code></pre></div>')

    def link_html(self, link, latex, passage_id, fact_uses, *, integrated=False):
        role, identifier, text = link["role"], link["card"], escape(link["text"])
        if role == "book":
            key = link.get("key") or identifier.replace(":", "--")
            return self.book_fold(identifier, text, f"{passage_id}--book--{key}")
        if role == "source":
            source = self.root.cards[identifier]
            href, title, loc, terms = (
                escape(value, quote=True)
                for value in (source.get("url"), source.get("title"), link["loc"], source.get("license"))
            )
            return f'<p class="fact-source">{text} <a href="{href}">{title} {loc}</a>（{terms}）</p>'
        if role == "math":
            fact = self.writing_fact(identifier)
            html_id = passage_id + "-" + identifier.replace(":", "--")
            href = self.fact_href(fact)
            note = latex(link["note"]) if link.get("note") else ""
            if identifier in fact_uses:
                return (
                    f'<div class="aid-item"><p>{text}</p>{note}'
                    f'<p><a href="#{fact_uses[identifier]}">{escape(fact.meta["title"])}を読む</a> · '
                    f'<a href="{href}">数学と証明</a></p></div>'
                )
            fact_uses[identifier] = html_id
            statement = latex(fact.sec("Statement"))
            proof = latex(fact.sec("Proof")) if fact.sec("Proof") else ""
            before, after = self.fact_context(fact, latex, include_code=not integrated)
            name = "定義" if fact.kind == "definition" else "命題"
            proof_html = (f'<section data-fact-part="Proof"><p class="fact-part-heading">証明</p>'
                          f'{proof}</section>') if proof else ""
            if integrated and self.options.get("fold_evidence", False):
                title = escape(fact.meta["title"])
                proof_fold = self.evidence_fold(f"証明｜{title}", proof_html) if proof_html else ""
                statement_html = (f'{note}{before}<section data-fact-part="Statement">'
                                  f'{statement}</section>')
                return (
                    f'<article class="reading-fact" data-fact="{fact.id}" id="{html_id}">'
                    f'{self.evidence_fold(f"{name}｜{title}", statement_html)}{proof_fold}'
                    f'<p class="fact-source"><a href="{href}">数学カードの出典</a></p></article>'
                )
            if integrated:
                return (
                    f'<article class="reading-fact" data-fact="{fact.id}" id="{html_id}">'
                    f'<p class="fact-title"><strong>{escape(fact.meta["title"])}</strong></p>'
                    f'{note}{before}<section data-fact-part="Statement">'
                    f'<p class="fact-part-heading">{name}</p>{statement}</section>{proof_html}'
                    f'<p class="fact-source"><a href="{href}">数学カードの出典</a></p></article>'
                )
            evidence = (
                f'<details class="proof math-aid" data-fact="{fact.id}" id="{html_id}">'
                '<summary>設定からコードまで読む</summary>'
                f'{before}<section data-fact-part="Statement"><p class="fact-part-heading">{name}</p>'
                f'{statement}</section>{proof_html}{after}</details>'
            )
            return (
                f'<div class="aid-item"><p><strong>数学の補完 ／ {escape(fact.meta["title"])}</strong></p>'
                f'<p>{text}</p>{note}{evidence}'
                f'<p><a href="{href}">数学と証明で前後の議論を見る</a></p></div>'
            )

        card = self.root.cards[identifier]
        if role == "figure":
            href = f'figures.html#c-{identifier}'
            title = escape(link.get("label", card.get("title")))
            panel = escape(link["panel"])
            main_figure = next(
                (ref["anchor"] for _, passage in self.passages for ref in passage["links"]
                 if ref["role"] == "figure" and ref["card"] == identifier and ref.get("anchor")),
                None,
            )
            in_text = f'<a href="#{main_figure}">通読の掲載図を見る</a> · ' if main_figure else ""
            return (
                f'<div class="aid-item"><p><strong>図 ／ {title} {panel}</strong></p>'
                f'<p>{text} {in_text}<a href="{href}">図と出典を開く</a></p></div>'
            )

        if role == "code":
            heading = "" if integrated else "<p><strong>実装の理由</strong></p>"
            return (
                f'<div class="aid-item">{heading}<p>{text}</p>'
                f'{self.code_excerpt(identifier, link["line"], link.get("through"))}</div>'
            )

        if role == "claim":
            if integrated:
                return f'<p>{text} <a class="fact-source" href="cards.html#c-{identifier}">出典</a></p>'
            return (f'<div class="aid-item"><p>{text} '
                    f'<a href="cards.html#c-{identifier}">対応する主張と出典を開く</a></p></div>')

        view = "code.html" if identifier in self.code_ids else "cards.html"
        href = f'{view}#c-{identifier}'
        return (
            f'<div class="aid-item"><p><strong>補足実験</strong> {text} '
            f'<a href="{href}">実行記録を開く</a></p></div>'
        )

    def ordered_html(self, passage, latex, captions, fact_uses, shown_alternatives):
        identifier = passage["id"]
        items = []
        reasons = {}
        for kind, value in reading_blocks(passage):
            if kind == "text":
                items.append(latex(value))
                continue
            if kind == "fact-code":
                fact = self.writing_fact(value["card"])
                _, implementation = self.fact_context(fact, latex)
                block = implementation.replace(' data-fact-part="In code"', "", 1)
            elif value["role"] == "figure" and (self.show_figure_inline(value) or value.get("display") == "reading"):
                block = self.figure_html(passage, value, captions, in_reading=True)
            elif "walkthrough" in value:
                card = self.root.cards[value["card"]]
                alternative_key = card.id, value.get("design")
                alternative = ""
                if alternative_key not in shown_alternatives:
                    alternative = card.secs.get(code_reason_section("別の導出", value.get("design")), "")
                    shown_alternatives.add(alternative_key)
                block = self.code_walkthrough(passage, value, latex, alternative)
            elif value["role"] == "code" and self.options.get("code_proofs", False):
                card = self.root.cards[value["card"]]
                key = f'{identifier}--{value["key"]}--design'
                variant = value.get("design")
                reason_key = (card.id, variant)
                if reason_key in reasons:
                    design = f'<p class="fact-source"><a href="#{reasons[reason_key]}">同じ処理の設計と導出</a></p>'
                else:
                    design = self.code_design(card, key, latex, variant, value.get("label"))
                    reasons[reason_key] = key
                title = escape(value.get("code_title", value.get("label", card.get("title"))))
                code = (f'<p>{escape(value["text"])}</p>'
                        f'{self.code_excerpt(card.id, value["line"], value.get("through"))}')
                block = design + self.evidence_fold(f"コード｜{title}", code)
            else:
                block = self.link_html(value, latex, identifier, fact_uses, integrated=True)
            part = ' data-reading-part="code"' if kind == "fact-code" else ""
            anchor = f' id="{identifier}--evidence--{value["key"]}"' if kind != "fact-code" and self.claims.enabled else ""
            items.append(f'<div{anchor} data-reading-ref="{value["key"]}"{part}>{block}</div>')
        if self.claims.enabled:
            items.insert(1, self.claim_reading_html(passage, latex))
        return "".join(items)

    def code_walkthrough(self, passage, link, latex, alternative=""):
        identifier = passage["id"]
        walk = link["walkthrough"]
        entries = {entry["id"]: entry for entry in self.claims.entries[identifier]}
        code_claim = entries[walk["claim"]]
        claim_anchor = f'{identifier}--claim--{code_claim["id"]}'
        stage_anchor = f'{identifier}--{link["key"]}'
        math = [entries[ref] for ref in walk["math"]]

        def math_item(entry, body):
            heading = escape(entry["title"])
            if self.appendices:
                heading = (f'<a href="{PROOFS_PAGE}#{identifier}--claim--{entry["id"]}">{heading}</a>')
            return f'<p class="fact-part-heading">{heading}</p>{body}'

        code_statement = self.claim_statement(code_claim, claim_anchor, latex)
        reason_label = "未確認" if code_claim.get("status") == "open" else "根拠"
        code_statement += latex(rf"\textbf{{{reason_label}}}　{code_claim['reason']}")
        statement = "".join(math_item(entry, latex(entry["statement"])) for entry in math)
        proofs = "".join(math_item(entry, latex(entry["reason"]) if entry.get("status") != "open"
                                   else latex(rf"\textbf{{未確認}}　{entry['reason']}")) for entry in math)
        if alternative:
            proofs += self.evidence_fold("別の導出と計算", latex(alternative))
        title = escape(link.get("code_title") or link.get("label") or self.root.cards[link["card"]].get("title"))
        snippet = self.code_excerpt(link["card"], link["line"], link.get("through"), preserve_indent=True)
        folds = (
            self.evidence_fold("コードの主張", code_statement, claim_anchor),
            self.evidence_fold("つながりの証明", latex(walk["bridge"]), f"{stage_anchor}--bridge"),
            self.evidence_fold("数学の主張", statement, f"{stage_anchor}--math"),
            self.evidence_fold("証明", proofs, f"{stage_anchor}--proof"),
            self.evidence_fold("実コード", snippet, f"{stage_anchor}--code"),
        )
        return self.evidence_fold(f"実装｜{title}", "".join(folds), f"{stage_anchor}--walkthrough")

    def fact_href(self, fact):
        if self.appendices:
            return f'{PROOFS_PAGE}#fact--{escape(fact.id, quote=True)}'
        return f'{self.fact_pages}#{escape(fact.meta["label"], quote=True)}'

    def code_title(self, link):
        return link.get("code_title") or link.get("label") or self.root.cards[link["card"]].get("title")

    @staticmethod
    def line_label(link):
        last = link.get("through", link["line"])
        return f'{link["line"]}–{last}' if last != link["line"] else str(link["line"])

    @staticmethod
    def claim_statement(entry, anchor, latex):
        return (f'<div class="claim-statement" data-claim-statement="{anchor}">'
                + latex(entry["statement"]) + "</div>")

    def claim_reading_html(self, passage, latex):
        identifier = passage["id"]
        claims = self.claims.entries.get(identifier, [])
        if not claims:
            return ""
        titles = {entry["id"]: entry["title"] for entry in claims}
        evidence = {link["key"]: link for link in passage["links"]}
        placed = {link["walkthrough"]["claim"] for link in passage["links"] if "walkthrough" in link}
        folds = []
        for entry in claims:
            if entry["id"] in placed:
                continue
            kind = KINDS[entry["kind"]]
            pending = entry.get("status") == "open"
            anchor = f'{identifier}--claim--{entry["id"]}'
            context = self.claim_statement(entry, anchor, latex)
            reason = "未確認" if pending else "根拠"
            context += latex(rf"\textbf{{{reason}}}　{entry['reason']}")
            references = []
            for dependency in entry.get("requires", []):
                references.append(f'<a href="{self.claim_href(identifier, dependency, "index.html")}">'
                                  f'{escape(titles[dependency])}</a>')
            for key in entry.get("basis", []):
                link = evidence[key]
                if link["role"] == "math":
                    label = self.writing_fact(link["card"]).meta["title"]
                elif link["role"] == "book":
                    label = self.books.resolve(link["card"]).card.meta["title"]
                else:
                    label = link.get("code_title") or link.get("label") or self.root.cards[link["card"]].get("title")
                references.append(f'<a href="#{identifier}--evidence--{key}">{escape(label)}</a>')
            if references:
                context += '<p class="fact-source">' + " ・ ".join(references) + "</p>"
            title = f'{kind}｜{escape(entry["title"])}' + ("（未確認）" if pending else "")
            folds.append(self.evidence_fold(title, context, anchor))
        return self.evidence_fold(f"数学的な言明（{len(folds)}件）", "".join(folds)) if folds else ""

    @staticmethod
    def evidence_fold(title, content, identifier=None):
        anchor = f' id="{identifier}"' if identifier else ""
        return f'<details class="evidence"{anchor}><summary>{title}</summary>{content}</details>'

    def book_fold(self, reference, introduction, anchor):
        selection = self.books.resolve(reference)
        card, proof = selection.card, selection.proof
        anchor = escape(anchor, quote=True)
        title = escape(str(card.meta.get("title") or card.id))
        body = book_card_html(selection, card)
        proof_html = ""
        if proof is not None:
            proof_html = (
                f'<details class="evidence book-proof" id="{anchor}--proof" data-book-proof="{proof.id}">'
                f'<summary>証明</summary>{book_card_html(selection, proof)}</details>'
            )
        return (
            f'<p>{introduction}</p><details class="evidence book-card" id="{anchor}" '
            f'data-book-card="{escape(reference, quote=True)}" data-book-version="{selection.version}">'
            f'<summary>本のカード｜{title}</summary>'
            f'<div class="book-card-body">{body}</div>{proof_html}</details>'
        )

    def code_design(self, card, identifier, latex, variant=None, label=None):
        chunks = []
        for heading in CODE_REASON_SECTIONS:
            content = card.secs[code_reason_section(heading, variant)]
            chunks.append(f'<p class="fact-part-heading">{heading}</p>{latex(content)}')
        if alternative := card.secs.get(code_reason_section("別の導出", variant)):
            chunks.append(self.evidence_fold("別の導出と計算", latex(alternative)))
        title = escape(label or card.get("title"))
        fold = self.evidence_fold(f"設計の主張と導出｜{title}", "".join(chunks), identifier)
        return f'<div data-code-design="{card.id}">{fold}</div>'

    def insert(self, section, rendered, latex, captions=None):
        if self.appendices:
            return self.insert_main(section, rendered, latex, captions or {})
        records = [(map_id, item) for map_id, item in self.passages if str(item["at"]["section"]) == section]
        if not records:
            return rendered
        locations = PassageLocations(rendered)
        positioned = []
        for map_id, passage in records:
            at = passage["at"]
            identifier = passage["id"]
            try:
                position = locations.position(at)
            except (IndexError, KeyError) as error:
                raise ValueError(f"{identifier}: 訳文中の位置が見つからない {at}") from error
            positioned.append((position, map_id, passage))
        insertions, fact_uses, shown_alternatives = {}, {}, set()
        for position, map_id, passage in sorted(positioned, key=lambda item: item[0]):
            identifier, at = passage["id"], passage["at"]
            refs = {link["card"] for link in passage["links"]}
            issues = "".join(
                f'<p class="passage-stale">{escape(message)}</p>'
                for message in self.stale.get(map_id, [])
                if message.startswith(identifier + ":") or message.split(" ", 1)[0] in refs
            )
            note = latex(passage["note"]) if passage.get("note") else ""
            source_note = ""
            if passage.get("source_note"):
                source_note = '<div class="passage-source-note">' + latex(
                    r"\textbf{原文注}　" + passage["source_note"]
                ) + "</div>"
            figures, items = [], []
            for link in sorted(passage["links"], key=lambda link: link["role"] != "math"):
                if link["role"] == "figure" and self.show_figure_inline(link):
                    figures.append(self.figure_html(passage, link, captions or {}))
                elif "reading" not in passage:
                    items.append(self.link_html(link, latex, identifier, fact_uses))
            probe = ""
            if passage.get("probe") and "reading" not in passage:
                probe = '<div class="reading-probe">' + latex(r"\textbf{手で確かめる}　" + passage["probe"]) + "</div>"
            ordered = "reading" in passage
            if ordered:
                items = [self.ordered_html(passage, latex, captions or {}, fact_uses, shown_alternatives)]
            aid = (
                f'<details class="reading-aid{" ordered-reading" if ordered else ""}" id="{identifier}" '
                f'data-comment-label="日本語訳 {locator_label(at)}">'
                f'<summary>{escape(passage["summary"])}</summary>{issues}{note}{"".join(items)}{probe}</details>'
            )
            if not (issues or note or items or probe):
                aid = f'<span id="{identifier}"></span>'
            if ordered and figures:
                block = '<div class="passage-group">' + "".join(figures) + source_note + aid + "</div>"
            else:
                block = "".join(figures) + source_note + aid
            insertions.setdefault(position, []).append(block)
        for position, inserts in sorted(insertions.items(), reverse=True):
            rendered = rendered[:position] + "".join(inserts) + rendered[position:]
        return rendered

    def code_reasons(self, identifier):
        refs = {
            (link["line"], link.get("through", link["line"]), link["text"])
            for _, passage in self.passages for link in passage["links"]
            if link["role"] == "code" and link["card"] == identifier
        }
        if not refs:
            return ""
        items = "".join(f'<li><a href="#c-{identifier}-L{line}">{line}{"–" + str(end) if end != line else ""}行</a> '
                        f'{escape(reason)}</li>' for line, end, reason in sorted(refs))
        return '<ul class="passage-code-reasons">' + items + "</ul>"

    def code_math(self, identifier):
        items = {}
        for _, passage in self.passages:
            for link in passage["links"]:
                if link["role"] != "math":
                    continue
                fact = self.writing_fact(link["card"])
                if any(ref["card"] == identifier for ref in fact.meta.get("reader_code", [])):
                    label = escape(fact.meta["label"], quote=True)
                    items[label] = f'<a href="{self.fact_href(fact)}">{escape(fact.meta["title"])}</a>'
        return '<p class="passage-back">数学と証明 ' + " · ".join(items.values()) + "</p>" if items else ""

    def attach_card_returns(self, html, show_code_reasons=False):
        def insert(match):
            card = self.root.cards[match[2]]
            role = {"figure": "figure", "step": "code", "run": "run", "claim": "claim"}.get(card.kind)
            reasons = self.code_reasons(card.id) + self.code_math(card.id) if role == "code" and show_code_reasons else ""
            return match[0] + (self.return_links(role, card.id) if role else "") + reasons

        return re.sub(
            r'(<article\b[^>]*data-card-id="([a-z0-9-]+)"[^>]*>\s*<div class="hd">.*?</div>)',
            insert, html, flags=re.S,
        )

    def reading_notes(self, latex, *, fold=True):
        notes = []
        ordered = sorted(self.passages, key=lambda entry: tuple(map(int, str(entry[1]["at"]["section"]).split("."))))
        for _, passage in ordered:
            if "reading" in passage and passage.get("probe"):
                href = f'index.html#{passage["id"]}'
                notes.append(f'<li>{latex(passage["probe"])}'
                             f'<a href="{href}">{escape(locator_label(passage["at"]))}の詳読</a></li>')
        if not notes:
            return ""
        if not fold:
            return '<ul class="passage-notes">' + "".join(notes) + "</ul>"
        return ('<details class="passage-notes"><summary>読解メモ・手計算</summary>'
                '<ul>' + "".join(notes) + "</ul></details>")

    # Main text and appendices: key statements in the reading, proofs (A), implementation (B).

    MAIN_NAMES = {"definition": "定義", "math": "命題"}

    def text_positions(self, section, rendered):
        """Where each passage of a section sits in the rendered translation."""
        locations = PassageLocations(rendered)
        return {passage["id"]: locations.position(passage["at"])
                for _, passage in self.passages if str(passage["at"]["section"]) == section}

    def set_text_order(self, positions):
        """Order passages as they appear in the translation and number the statements in that order."""
        self.text_order = dict(positions)
        if self.appendices:
            self.assign_numbers()

    def ordered_passages(self):
        order = getattr(self, "text_order", {})
        indexed = [(section_key(passage), order.get(passage["id"], position), position, map_id, passage)
                   for position, (map_id, passage) in enumerate(self.passages)]
        return [(map_id, passage) for *_, map_id, passage in sorted(indexed, key=lambda item: item[:3])]

    def section_passages(self):
        grouped = {}
        for map_id, passage in self.ordered_passages():
            grouped.setdefault(str(passage["at"]["section"]), []).append((map_id, passage))
        return grouped

    def code_groups(self):
        """Code blocks (section, code card) in paper order, each with its walkthroughs in text order."""
        groups = {}
        for _, passage in self.ordered_passages():
            for link in passage["links"]:
                if "walkthrough" in link:
                    groups.setdefault((str(passage["at"]["section"]), link["card"]), []).append((passage, link))
        return groups

    def assign_numbers(self):
        """Number main statements by chapter, the rest of Appendix A by A.n and code steps by B.k.j."""
        self.numbers, self.fact_numbers, self.step_numbers, self.card_numbers = {}, {}, {}, {}
        chapters = {}
        for _, passage in self.ordered_passages():
            chapter = str(passage["at"]["section"]).split(".")[0]
            for entry in self.claims.main_entries(passage["id"]):
                chapters[chapter] = chapters.get(chapter, 0) + 1
                self.numbers[f'{passage["id"]}--claim--{entry["id"]}'] = (
                    self.MAIN_NAMES[entry["kind"]], f"{chapter}.{chapters[chapter]}")
        count = 0
        for _, passage in self.ordered_passages():
            for kind, value in reading_blocks(passage) if "reading" in passage else []:
                if kind == "link" and value["role"] == "math":
                    fact = self.writing_fact(value["card"])
                    if fact.id not in self.fact_numbers:
                        count += 1
                        self.fact_numbers[fact.id] = ("定義" if fact.kind == "definition" else "命題", f"A.{count}")
            for entry in self.claims.entries.get(passage["id"], []):
                anchor = f'{passage["id"]}--claim--{entry["id"]}'
                if entry["kind"] in POINT_KINDS and anchor not in self.numbers:
                    count += 1
                    name = {"definition": "定義", "cost": "計算量"}.get(entry["kind"], "補題")
                    self.numbers[anchor] = (name, f"A.{count}")
        for index, (block, uses) in enumerate(self.code_groups().items(), 1):
            self.card_numbers[block] = f"B.{index}"
            for step, (passage, link) in enumerate(uses, 1):
                self.step_numbers[f'{passage["id"]}--{link["key"]}'] = f"B.{index}.{step}"

    def claim_label(self, passage_id, claim_id):
        """Numbered label of a statement, e.g. 命題 4.9 or 補題 A.12; other kinds keep their kind name."""
        anchor = f"{passage_id}--claim--{claim_id}"
        if anchor in self.numbers:
            name, number = self.numbers[anchor]
            return f"{name} {number}"
        entry = next(entry for entry in self.claims.entries[passage_id] if entry["id"] == claim_id)
        return KINDS[entry["kind"]]

    def claim_page(self, passage_id, claim_id):
        """Appendix A holds every statement except the code claims of the walkthroughs (Appendix B)."""
        if not self.appendices:
            return "index.html"
        passage = next(passage for _, passage in self.passages if passage["id"] == passage_id)
        if any(link["walkthrough"]["claim"] == claim_id for link in passage["links"] if "walkthrough" in link):
            return METHODS_PAGE
        return PROOFS_PAGE

    def claim_href(self, passage_id, claim_id, current):
        page = self.claim_page(passage_id, claim_id)
        prefix = "" if page == current else page
        return f"{prefix}#{passage_id}--claim--{claim_id}"

    def claim_title(self, passage_id, claim_id):
        entry = next(entry for entry in self.claims.entries[passage_id] if entry["id"] == claim_id)
        return self.claim_label(passage_id, claim_id) + "｜" + entry["title"]

    def code_flow(self, passage):
        """The steps of a passage's code in order, as one line that leads to Appendix B."""
        steps = []
        for link in passage["links"]:
            if "walkthrough" in link:
                stage = f'{passage["id"]}--{link["key"]}'
                steps.append(f'<a href="{METHODS_PAGE}#{stage}--walkthrough">{escape(self.code_title(link))}'
                             f'（{self.step_numbers[stage]}）</a>')
        if not steps:
            return ""
        return (f'<p class="code-flow" data-code-flow="{passage["id"]}"><span class="sketch-label">コードの流れ</span>'
                + " → ".join(steps) + "</p>")

    def proof_sketch(self, passage_id, entry, latex, *, link=True):
        """The point of a statement as the outline of its proof (or the role of a definition)."""
        anchor = f"{passage_id}--claim--{entry['id']}"
        label = "証明の筋" if entry["kind"] == "math" else "定義の役割"
        target = (f'<p class="proof-link"><a href="{PROOFS_PAGE}#{anchor}">'
                  f'{"証明" if entry["kind"] == "math" else "背景"}は付録 A の{self.claim_label(passage_id, entry["id"])}</a></p>'
                  if link else "")
        return (f'<div class="claim-sketch" data-sketch="{anchor}"><p class="sketch-label">{label}</p>'
                f'{latex(entry["point"])}{target}</div>')

    def step_links(self, passage, *, titled=True):
        links = []
        for link in passage["links"]:
            if "walkthrough" not in link:
                continue
            stage = f'{passage["id"]}--{link["key"]}'
            title = f' {escape(self.code_title(link))}' if titled else ""
            links.append(f'<a href="{METHODS_PAGE}#{stage}--walkthrough">{self.step_numbers[stage]}{title}</a>')
        return links

    # The main text: the translation with the key statements displayed in place.

    def main_claim_html(self, passage, entry, latex):
        anchor = f'{passage["id"]}--claim--{entry["id"]}'
        name, number = self.numbers[anchor]
        return (
            f'<div class="main-claim" id="{anchor}" data-main-claim="{anchor}">'
            f'<p class="claim-head"><strong>{name} {number}</strong>（{escape(entry["title"])}）</p>'
            f'{self.claim_statement(entry, anchor, latex)}{self.proof_sketch(passage["id"], entry, latex)}</div>'
        )

    def insert_main(self, section, rendered, latex, captions):
        records = [(map_id, item) for map_id, item in self.passages if str(item["at"]["section"]) == section]
        if not records:
            return rendered
        locations = PassageLocations(rendered)
        insertions = {}
        for map_id, passage in records:
            at, identifier = passage["at"], passage["id"]
            try:
                position = locations.position(at)
                closing = locations.algorithm_ends[at["algorithm"]] if "algorithm" in at else position
            except (IndexError, KeyError) as error:
                raise ValueError(f"{identifier}: 訳文中の位置が見つからない {at}") from error
            refs = {link["card"] for link in passage["links"]}
            issues = "".join(
                f'<p class="passage-stale">{escape(message)}</p>'
                for message in self.stale.get(map_id, [])
                if message.startswith(identifier + ":") or message.split(" ", 1)[0] in refs
            )
            figures = "".join(self.figure_html(passage, link, captions) for link in passage["links"]
                              if link["role"] == "figure" and self.show_figure_inline(link))
            source_note = ""
            if passage.get("source_note"):
                source_note = '<div class="passage-source-note">' + latex(
                    r"\textbf{原文注}　" + passage["source_note"]) + "</div>"
            claims = "".join(self.main_claim_html(passage, entry, latex)
                             for entry in self.claims.main_entries(identifier))
            steps = self.step_links(passage)
            label = f'data-comment-label="日本語訳 {locator_label(at)}"'
            more_line = ""
            if claims or steps:
                more_line = (self.code_flow(passage)
                             + f'<p class="passage-links"><a href="{PROOFS_PAGE}#A-{identifier}">この箇所の詳読（付録 A）</a></p>')
            if "algorithm" in at:
                numbers = []
                for entry in self.claims.main_entries(identifier):
                    anchor = f'{identifier}--claim--{entry["id"]}'
                    numbers.append(f'<a href="#{anchor}">{" ".join(self.numbers[anchor])}</a>')
                marker = " · ".join(numbers + self.step_links(passage, titled=False))
                insertions.setdefault(position, []).append(
                    f'<span class="algo-ref" id="{identifier}" {label}>▷ {marker or "付録 A"}</span>')
                block = issues + figures + source_note + claims + more_line
                if block:
                    insertions.setdefault(closing, []).append(
                        f'<div class="main-claims" id="{identifier}--main">{block}</div>')
                continue
            if claims or steps or issues:
                block = (f'<div class="main-claims" id="{identifier}" {label}>'
                         f'{issues}{claims}{more_line}</div>')
            else:
                block = f'<span class="passage-anchor" id="{identifier}"></span>'
            insertions.setdefault(position, []).append(figures + source_note + block)
        for position, inserts in sorted(insertions.items(), reverse=True):
            rendered = rendered[:position] + "".join(inserts) + rendered[position:]
        return rendered

    # Appendix A: the detailed reading of each passage, with every statement and its proof.

    def claim_uses(self, passage):
        """Where each statement of a passage is used: later statements, the main text and code steps."""
        identifier = passage["id"]
        entries = self.claims.entries.get(identifier, [])
        uses = {entry["id"]: [] for entry in entries}
        for entry in entries:
            for dependency in entry.get("requires", []):
                uses[dependency].append((self.claim_href(identifier, entry["id"], PROOFS_PAGE),
                                         self.claim_title(identifier, entry["id"])))
        for link in passage["links"]:
            if "walkthrough" not in link:
                continue
            stage = f'{identifier}--{link["key"]}'
            target = f'{METHODS_PAGE}#{stage}--walkthrough'
            for ref in link["walkthrough"]["math"]:
                uses[ref].append((target, f"{self.step_numbers[stage]} {self.code_title(link)}"))
        return uses

    def proofs_sections(self, sections, latex):
        """Appendix A in paper order: the reading of each passage, then its numbered statements."""
        grouped = self.section_passages()
        placed_facts = set()
        out = []
        for number, label in sections:
            blocks = [self.appendix_passage(passage, latex, placed_facts) for _, passage in grouped.get(number, [])]
            if blocks:
                out.append((number, label, "".join(blocks)))
        return out

    def appendix_passage(self, passage, latex, placed_facts):
        identifier = passage["id"]
        parts = []
        for kind, value in reading_blocks(passage) if "reading" in passage else []:
            if kind == "text":
                parts.append(latex(value))
                continue
            if kind == "fact-code":
                continue
            role = value["role"]
            if role == "math":
                fact = self.writing_fact(value["card"])
                if fact.id in placed_facts:
                    name, number = self.fact_numbers[fact.id]
                    block = (f'<p>{escape(value["text"])} <a href="#fact--{fact.id}">'
                             f'{name} {number}（{escape(fact.meta["title"])}）</a></p>')
                else:
                    placed_facts.add(fact.id)
                    block = f'<p>{escape(value["text"])}</p>' + self.fact_article(fact, latex)
            elif role == "figure" and value.get("display") != "link":
                block = self.figure_html(passage, value, {}, in_reading=True)
            elif role == "book":
                key = value.get("key") or value["card"].replace(":", "--")
                block = self.book_block(value["card"], escape(value["text"]), f"{identifier}--book--{key}")
            elif "walkthrough" in value:
                stage = f'{identifier}--{value["key"]}'
                block = (f'<p class="step-ref"><a href="{METHODS_PAGE}#{stage}--walkthrough">'
                         f'{self.step_numbers[stage]} {escape(self.code_title(value))}（{self.line_label(value)}行）</a>'
                         f'　{escape(value["text"])}</p>')
            else:
                block = self.link_html(value, latex, identifier, {}, integrated=True)
            parts.append(f'<div id="{identifier}--evidence--{value["key"]}" data-reading-ref="{value["key"]}">'
                         f'{block}</div>')
        articles = self.claim_articles(passage, latex)
        back = f'<p class="passage-back"><a href="index.html#{identifier}">通読 {locator_label(passage["at"])}</a></p>'
        return (
            f'<section class="appendix-passage" id="A-{identifier}" data-appendix-passage="{identifier}">'
            f'<h3>{escape(passage["summary"])}</h3>{back}{self.code_flow(passage)}'
            f'<div class="appendix-reading">{"".join(parts)}</div>{"".join(articles)}</section>'
        )

    def claim_articles(self, passage, latex):
        identifier = passage["id"]
        walk_claims = {link["walkthrough"]["claim"] for link in passage["links"] if "walkthrough" in link}
        uses = self.claim_uses(passage)
        articles = []
        for entry in self.claims.entries.get(identifier, []):
            if entry["id"] in walk_claims:
                continue
            anchor = f'{identifier}--claim--{entry["id"]}'
            pending = entry.get("status") == "open"
            title = f'{self.claim_label(identifier, entry["id"])}｜{escape(entry["title"])}'
            requires = "".join(f'<li><a href="{self.claim_href(identifier, ref, PROOFS_PAGE)}">'
                               f'{escape(self.claim_title(identifier, ref))}</a></li>'
                               for ref in entry.get("requires", []))
            requires = (f'<p class="claim-requires">使う前提</p><ul class="claim-requires">{requires}</ul>'
                        if requires else "")
            origin = self.origin_html(entry, latex)
            if entry["kind"] not in POINT_KINDS:
                basis = " · ".join(f'<a href="#{identifier}--evidence--{key}">{escape(self.basis_label(passage, key))}</a>'
                                   for key in entry.get("basis", []))
                articles.append(
                    f'<article class="appendix-statement" id="{anchor}" data-appendix-statement="{anchor}">'
                    f'<h4>{title}{"（未確認）" if pending else ""}</h4>{self.claim_statement(entry, anchor, latex)}'
                    f'<section data-appendix-part="proof"><p class="fact-part-heading">{"未確認" if pending else "根拠"}</p>'
                    f'{requires}{latex(entry["reason"])}'
                    + (f'<p class="fact-source">見る箇所：{basis}</p>' if basis else "") + f'</section>{origin}</article>')
                continue
            links = uses[entry["id"]]
            main = anchor in self.numbers and not self.numbers[anchor][1].startswith("A.")
            if main:
                lead = (f'<p class="claim-lead" data-appendix-part="lead">証明の筋は'
                        f'<a href="index.html#{anchor}">本文の{self.claim_label(identifier, entry["id"])}</a></p>')
            else:
                lead = (f'<div class="claim-lead" data-appendix-part="lead">{latex(entry["point"])}</div>'
                        if entry.get("point") else "")
            used = (f'<p class="claim-uses" data-appendix-part="uses">使う：'
                    + " · ".join(f'<a href="{href}">{escape(label)}</a>' for href, label in links) + "</p>"
                    if links else "")
            proof_heading = ("証明" if entry["kind"] == "math" else "根拠") + ("（未確認）" if pending else "")
            articles.append(
                f'<article class="appendix-claim{" is-main" if main else ""}" id="{anchor}" data-appendix-claim="{anchor}">'
                f'<h4>{title}</h4>{lead}'
                f'<section data-appendix-part="statement">{self.model_html(entry, latex)}'
                f'{self.claim_statement(entry, anchor, latex)}</section>'
                f'<section data-appendix-part="proof"><p class="fact-part-heading">{proof_heading}</p>'
                f'{requires}{latex(entry["reason"])}</section>{origin}{used}</article>'
            )
        return articles

    def basis_label(self, passage, key):
        link = next(link for link in passage["links"] if link["key"] == key)
        if link["role"] == "math":
            return self.writing_fact(link["card"]).meta["title"]
        if link["role"] == "book":
            return self.books.resolve(link["card"]).card.meta["title"]
        if "walkthrough" in link:
            return f'{self.step_numbers[passage["id"] + "--" + key]} {self.code_title(link)}'
        return link.get("code_title") or link.get("label") or self.root.cards[link["card"]].get("title")

    def book_block(self, reference, introduction, anchor):
        selection = self.books.resolve(reference)
        card, proof = selection.card, selection.proof
        anchor = escape(anchor, quote=True)
        title = escape(str(card.meta.get("title") or card.id))
        proof_html = ""
        if proof is not None:
            proof_html = (f'<div class="book-proof" id="{anchor}--proof" data-book-proof="{proof.id}">'
                          f'<p class="fact-part-heading">証明</p>{book_card_html(selection, proof)}</div>')
        return (
            f'<p>{introduction}</p><div class="book-card" id="{anchor}" '
            f'data-book-card="{escape(reference, quote=True)}" data-book-version="{selection.version}">'
            f'<p class="fact-part-heading">本のカード｜{title}</p>'
            f'<div class="book-card-body">{book_card_html(selection, card)}</div>{proof_html}</div>'
        )

    def fact_article(self, fact, latex):
        name, number = self.fact_numbers[fact.id]
        uses = []
        for _, passage in self.ordered_passages():
            if any(link["role"] == "math" and link["card"].split(":", 1)[-1] == fact.id for link in passage["links"]):
                uses.append(f'<a href="#A-{passage["id"]}">{locator_label(passage["at"])}</a>')
        goal = latex(fact.sec("Goal")) if fact.sec("Goal") else ""
        setup = (f'<section data-fact-part="Setup"><p class="fact-part-heading">設定</p>{latex(fact.sec("Setup"))}</section>'
                 if fact.sec("Setup") else "")
        proof = (f'<section data-fact-part="Proof"><p class="fact-part-heading">証明</p>{latex(fact.sec("Proof"))}</section>'
                 if fact.sec("Proof") else "")
        code = ""
        if fact.sec("In code"):
            snippets = "".join(self.code_excerpt(ref["card"], ref["line"], ref.get("through"))
                               for ref in fact.meta.get("reader_code", []))
            code = (f'<section data-fact-part="In code"><p class="fact-part-heading">コードではどうなるか</p>'
                    f'{latex(fact.sec("In code"))}{snippets}</section>')
        stale = "".join(f'<p class="passage-stale" data-writing-stale="{fact.id}">STALE：{escape(message)}</p>'
                        for message in getattr(self, "writing_stale", {}).get(fact.id, []))
        return (
            f'<article class="appendix-fact" id="fact--{fact.id}" data-fact="{fact.id}">'
            f'<h4>{name} {number}｜{escape(fact.meta["title"])}</h4>{stale}'
            f'<div class="claim-lead" data-fact-part="Goal">{goal}</div>'
            f'{setup}<section data-fact-part="Statement">{latex(fact.sec("Statement"))}</section>{proof}{code}'
            f'<p class="claim-uses">使う：{" · ".join(uses)}</p></article>'
        )

    # Appendix B: from the statements to the computation, one code card at a time.

    def methods_sections(self, sections, latex, extras=None):
        """Appendix B in paper order: per section, each code card it uses with its numbered steps."""
        extras = extras or {}
        shown_alternatives, placed_cards = set(), set()
        blocks = {}
        for (section, card_id), uses in self.code_groups().items():
            card = self.root.cards[card_id]
            code = card.get("code")
            first = card_id not in placed_cards
            placed_cards.add(card_id)
            anchor = f"B-{card_id}" if first else f'B-{card_id}--{section.replace(".", "-")}'
            meta = (f'<p class="fact-source">{escape(code["file"])} {code["lines"][0]}–{code["lines"][1]}行 · '
                    f'<a href="code.html#c-{card_id}">コードカード</a></p>')
            gist = latex(card.get("gist")) if card.get("gist") and first else ""
            if first:
                gist += self.lineage_html(card, latex)
            steps = []
            for passage, link in uses:
                alternative_key = card.id, link.get("design")
                alternative = ""
                if alternative_key not in shown_alternatives:
                    alternative = card.secs.get(code_reason_section("別の導出", link.get("design")), "")
                    shown_alternatives.add(alternative_key)
                steps.append(self.method_step(passage, link, latex, alternative))
            title = f'{self.card_numbers[(section, card_id)]}　{escape(card.get("title"))}'
            blocks.setdefault(section, []).append(
                f'<section class="method-card" id="{anchor}" data-method-card="{card_id}"><h4>{title}</h4>'
                f'{meta}{gist}{"".join(steps)}{extras.get(card_id, "") if first else ""}</section>')
        missing = set(extras) - placed_cards
        if missing:
            raise ValueError(f"Ports without a code section: {sorted(missing)}")
        return [(number, label, "".join(blocks[number])) for number, label in sections if number in blocks]

    def method_step(self, passage, link, latex, alternative=""):
        identifier = passage["id"]
        stage = f'{identifier}--{link["key"]}'
        walk = link["walkthrough"]
        entries = {entry["id"]: entry for entry in self.claims.entries[identifier]}
        code_claim = entries[walk["claim"]]
        claim_anchor = f'{identifier}--claim--{code_claim["id"]}'
        reason = "未確認" if code_claim.get("status") == "open" else "根拠"

        def part(key, heading, body, anchor=None):
            ident = f' id="{anchor}"' if anchor else ""
            return (f'<section{ident} data-step-part="{key}"><p class="fact-part-heading">{heading}</p>'
                    f'{body}</section>')

        claim = (self.claim_statement(code_claim, claim_anchor, latex)
                 + latex(rf"\textbf{{{reason}}}　{code_claim['reason']}"))
        sketches = "".join(
            f'<li><a href="{PROOFS_PAGE}#{identifier}--claim--{ref}">{escape(self.claim_title(identifier, ref))}</a>'
            f'{latex(entries[ref]["point"])}</li>' for ref in walk["math"])
        snippet = self.code_excerpt(link["card"], link["line"], link.get("through"), preserve_indent=True)
        back = (f'<p class="passage-back"><a href="index.html#{identifier}">通読 {locator_label(passage["at"])}</a>'
                f'　<a href="{PROOFS_PAGE}#A-{identifier}">付録 A の詳読</a></p>')
        return (
            f'<article class="method-step" id="{stage}--walkthrough" data-method-step="{stage}">'
            f'<h5>{self.step_numbers[stage]}　{escape(self.code_title(link))}（{self.line_label(link)}行）</h5>{back}'
            + part("sketch", "証明の筋（証明は付録 A）", f'<ul class="step-sketch">{sketches}</ul>', f"{stage}--math")
            + f'<div id="{claim_anchor}" data-step-claim="{claim_anchor}">{part("claim", "コードの主張", claim)}</div>'
            + part("realization", "定理と計算の対応", self.realization_table(passage, link, latex))
            + part("bridge", "つながりの証明", latex(walk["bridge"]), f"{stage}--bridge")
            + (part("alternative", "別の導出と計算", latex(alternative)) if alternative else "")
            + part("code", "実コード", snippet, f"{stage}--code")
            + "</article>"
        )

    def realization_table(self, passage, link, latex):
        stage = f'{passage["id"]}--{link["key"]}'
        rows = []
        for number, row in enumerate(link["walkthrough"]["realization"], 1):
            anchor = f"{stage}--realization" if number == 1 else f"{stage}--realization-{number}"
            outside = " ".join(latex(row[key]) for key in ("error", "outside") if row.get(key)) or "—"
            cells = (
                ("対応", f"({chr(96 + number)})"),
                ("数学の側", latex(row["math"])),
                ("計算の側", latex(row["code"])),
                ("種類", REALIZATION_KINDS[row["kind"]]),
                ("実装で満たす仮定", latex(row["holds"])),
                ("範囲外・誤差", outside),
            )
            rows.append(f'<tr id="{anchor}" data-realization="{stage}" data-realization-kind="{row["kind"]}">'
                        + "".join(f'<td data-label="{label}"><div>{value}</div></td>' for label, value in cells)
                        + "</tr>")
        return ('<table class="realization"><thead><tr><th>対応</th><th>数学の側</th><th>計算の側</th><th>種類</th>'
                '<th>実装で満たす仮定</th><th>範囲外・誤差</th></tr></thead><tbody>' + "".join(rows) + "</tbody></table>")

    def outside_theory(self, latex):
        """Every correspondence that is not an equality, grouped by kind, for the end of Appendix B."""
        groups = {kind: [] for kind in REALIZATION_KINDS if kind != "equality"}
        for _, uses in self.code_groups().items():
            for passage, link in uses:
                stage = f'{passage["id"]}--{link["key"]}'
                for number, row in enumerate(link["walkthrough"]["realization"], 1):
                    if row["kind"] == "equality":
                        continue
                    anchor = f"{stage}--realization" if number == 1 else f"{stage}--realization-{number}"
                    detail = " ".join(latex(row[key]) for key in ("error", "outside") if row.get(key))
                    groups[row["kind"]].append(
                        f'<li data-outside="{stage}"><p><a href="#{anchor}">{self.step_numbers[stage]}({chr(96 + number)})</a> '
                        f'{escape(self.code_title(link))}</p>{latex(row["math"])}{detail}</li>')
        return "".join(
            f'<p class="fact-part-heading">{REALIZATION_KINDS[kind]}（{len(items)}件）</p><ul class="outside-list">{"".join(items)}</ul>'
            for kind, items in groups.items() if items)

    def relink(self, html, current):
        """Send in-text links to passages, statements and steps to the page that now holds them."""
        passages = {passage["id"] for _, passage in self.passages}

        def target(match):
            fragment = match[1]
            if fragment in passages:
                href = f"#{fragment}" if current == "index.html" else f"{PROOFS_PAGE}#A-{fragment}"
            elif "--claim--" in fragment:
                passage_id, claim_id = fragment.split("--claim--", 1)
                page = self.claim_page(passage_id, claim_id)
                if current == "index.html" and fragment in self.numbers and not self.numbers[fragment][1].startswith("A."):
                    page = "index.html"
                href = fragment if page == current else f"{page}#{fragment}"
                href = href if "#" in href else f"#{href}"
            elif fragment.endswith("--walkthrough"):
                href = f"#{fragment}" if current == METHODS_PAGE else f"{METHODS_PAGE}#{fragment}"
            else:
                return match[0]
            if href.startswith(current + "#"):
                href = href[len(current):]
            return f'href="{href}"'

        return re.sub(r'href="#([a-z0-9][a-z0-9-]*)"', target, html)

    # Lineage: the prior work behind each code card and what kind of code it is.

    def source_label(self, proposal):
        source = self.root.cards[proposal["src"]]
        page = f'（PDF p.{proposal["pdf_page"]}）' if proposal.get("pdf_page") else ""
        return f'{escape(str(source.get("title")))}　{escape(proposal["loc"])}{page}'

    def lineage_html(self, card, latex):
        lineage = card.get("lineage")
        if not lineage:
            return ""
        status = "" if lineage["status"] == "checked" else '<span class="lineage-open">（未確認）</span>'
        rows = [("提案", self.source_label(lineage["proposal"])),
                ("提案者の意図", latex(lineage["intent"]) + status),
                ("このコード", CODE_KINDS[lineage["code"]]
                 + (f'。{escape(lineage["follows"])}' if lineage.get("follows") else "")),
                ("元の提案との違い", latex(lineage["differences"]))]
        if lineage.get("substitute"):
            rows.insert(1, ("代替資料で照合", escape(lineage["substitute"])))
        body = "".join(f'<div class="lineage-row"><p class="sketch-label">{label}</p><div>{value}</div></div>'
                       for label, value in rows)
        return (f'<div class="lineage" data-lineage="{card.id}" data-lineage-status="{lineage["status"]}">'
                f'<p class="fact-part-heading">由来</p>{body}</div>')

    def lineage_table(self, latex):
        """Appendix D: proposal → this code → differences, grouped by the proposing source."""
        groups = {}
        for (section, card_id), _ in self.code_groups().items():
            card = self.root.cards[card_id]
            lineage = card.get("lineage")
            if not lineage or card_id in {c for items in groups.values() for c, _ in items}:
                continue
            groups.setdefault(lineage["proposal"]["src"], []).append((card_id, section))
        out = []
        for src, items in groups.items():
            title = escape(str(self.root.cards[src].get("title")))
            rows = []
            for card_id, section in items:
                card = self.root.cards[card_id]
                lineage = card.get("lineage")
                number = self.card_numbers[(section, card_id)]
                open_mark = "（未確認）" if lineage["status"] == "open" else ""
                rows.append(
                    f'<tr data-lineage-row="{card_id}"><td data-label="コード"><div><a href="methods.html#B-{card_id}">'
                    f'{number} {escape(str(card.get("title")))}</a></div></td>'
                    f'<td data-label="箇所"><div>{escape(lineage["proposal"]["loc"])}</div></td>'
                    f'<td data-label="素性"><div>{CODE_KINDS[lineage["code"]]}{open_mark}</div></td>'
                    f'<td data-label="違い"><div>{latex(lineage["differences"])}</div></td></tr>')
            out.append(f'<p class="fact-part-heading">{title}</p><table class="realization lineage-table"><tbody>'
                       + "".join(rows) + "</tbody></table>")
        return "".join(out)

    # Cost statements and the comparison with the original work.

    @staticmethod
    def model_html(entry, latex):
        if not entry.get("model"):
            return ""
        return (f'<div class="claim-model" data-claim-model="1"><p class="sketch-label">計算の模型</p>'
                f'{latex(entry["model"])}</div>')

    def origin_html(self, entry, latex):
        origin = entry.get("origin")
        if not origin:
            return ""
        if origin.get("src"):
            source = self.root.cards[origin["src"]]
            where = escape(str(source.get("title")))
        else:
            where = escape(origin["cite"])
        if origin.get("loc"):
            where += "　" + escape(origin["loc"])
        if origin.get("pdf_page"):
            where += f'（PDF p.{origin["pdf_page"]}）'
        note = latex(origin["note"]) if origin.get("note") else ""
        label = "代替資料" if origin.get("substitute") else "原典"
        substitute = (f'<p class="origin-substitute" data-origin-substitute="1"><strong>代替資料で照合</strong>　'
                      f'{escape(origin["substitute"])}</p>' if origin.get("substitute") else "")
        return (f'<div class="claim-origin" data-origin-relation="{origin["relation"]}">'
                f'<p><span class="sketch-label">{label}</span>{where}　<strong>{ORIGIN_RELATIONS[origin["relation"]]}</strong></p>'
                f'{substitute}{note}</div>')

    # Paragraph coverage: every paragraph of the translation is read, or recorded as holding no claim.

    @staticmethod
    def paragraph_texts(rendered):
        """Plain text of each top-level paragraph, numbered as `at.paragraph` counts them."""
        locations = PassageLocations(rendered)
        texts, start = [], 0
        for end in locations.paragraphs:
            chunk = rendered[start:end]
            start = end
            chunk = chunk[chunk.rfind("<p"):] if "<p" in chunk else chunk
            chunk = re.sub(r"<annotation[^>]*>.*?</annotation>", "", chunk, flags=re.S)
            if "<!--caption-" in chunk:
                texts.append(None)  # place of a figure caption, read with the figure
                continue
            text = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", chunk)).strip()
            texts.append(text or None)
        return texts, locations

    @staticmethod
    def paragraph_fp(text):
        return sha256(text.encode("utf-8")).hexdigest()[:8]

    def paragraph_coverage(self, section, rendered):
        """(number, fingerprint, text, how it is covered) for every paragraph of a section."""
        texts, locations = self.paragraph_texts(rendered)
        equation_paragraph = {number: locations.paragraphs.index(position) + 1
                              for number, position in locations.equations.items()}
        covered = {}
        for _, passage in self.passages:
            at = passage["at"]
            if str(at["section"]) != section:
                continue
            if "paragraph" in at:
                covered.setdefault(at["paragraph"], []).append(passage["id"])
            elif "equation" in at and at["equation"] in equation_paragraph:
                covered.setdefault(equation_paragraph[at["equation"]], []).append(passage["id"])
        ledger = self.ledger().get(section, {})
        rows = []
        for number, text in enumerate(texts, 1):
            if text is None:
                rows.append((number, None, "", ("figure", None)))
                continue
            fp = self.paragraph_fp(text)
            if number in covered:
                rows.append((number, fp, text, ("passage", covered[number])))
            elif number in ledger:
                rows.append((number, fp, text, ("ledger", ledger[number])))
            else:
                rows.append((number, fp, text, ("missing", None)))
        return rows

    def ledger(self):
        if not hasattr(self, "_ledger"):
            name = self.options.get("paragraph_ledger")
            data = yaml.safe_load((self.root.root / name).read_text(encoding="utf-8")) if name else {}
            self._ledger = {str(section): {int(k): v for k, v in (entries or {}).items()}
                            for section, entries in (data or {}).items()}
        return self._ledger

    def check_paragraphs(self, sections):
        """Errors for paragraphs that are neither read nor recorded, stale ledger entries and redundant ones."""
        errors = []
        passages = {passage["id"] for _, passage in self.passages}
        seen = set()
        for section, rendered in sections:
            for number, fp, text, (how, value) in self.paragraph_coverage(section, rendered):
                where = f"§{section} 第{number}段落"
                if how == "missing":
                    errors.append(f"{where}: 詳読も記録もない（{fp}）{text[:60]}")
                if section in self.ledger() and number in self.ledger()[section]:
                    seen.add((section, number))
                    entry = self.ledger()[section][number]
                    if how == "passage":
                        errors.append(f"{where}: 詳読があるので段落表の記録は不要")
                    elif how == "figure":
                        errors.append(f"{where}: 図の位置なので段落表の記録は不要")
                    elif not isinstance(entry, dict) or entry.get("fp") != fp:
                        errors.append(f"{where}: 段落表の指紋が本文と違う（現在 {fp}）。段落を読み直して更新する")
                    elif not ((isinstance(entry.get("none"), str) and entry["none"].strip())
                              or entry.get("passage") in passages):
                        errors.append(f"{where}: 段落表には none（主張を含まない理由）か passage（扱う詳読）が必要")
        for section, entries in self.ledger().items():
            for number in entries:
                if (section, number) not in seen:
                    errors.append(f"§{section} 第{number}段落: 段落表の記録に対応する段落がない")
        return errors


    def coverage_html(self, labels):
        """Appendix D: how each paragraph of the translation is handled."""
        out = []
        for number, label in labels:
            rows = getattr(self, "coverage", {}).get(number)
            if not rows:
                continue
            items = []
            for paragraph, fp, _, (how, value) in rows:
                if how == "figure":
                    continue
                if how == "passage":
                    body = "詳読 " + " · ".join(f'<a href="{PROOFS_PAGE}#A-{pid}">{escape(self.passage_summary(pid))}</a>'
                                              for pid in value)
                elif value.get("passage"):
                    pid = value["passage"]
                    body = f'主張は詳読 <a href="{PROOFS_PAGE}#A-{pid}">{escape(self.passage_summary(pid))}</a> で扱う'
                else:
                    body = "主張なし：" + escape(value["none"])
                items.append(f'<li data-paragraph="{number}:{paragraph}" data-paragraph-how="{how}">'
                             f'第{paragraph}段落　{body}</li>')
            out.append(f'<p class="fact-part-heading">{label}</p><ul class="coverage-list">{"".join(items)}</ul>')
        return "".join(out)

    def passage_summary(self, pid):
        return next(passage["summary"] for _, passage in self.passages if passage["id"] == pid)

    def origins_html(self):
        """Appendix D: every statement compared with its original work, grouped by the relation found."""
        groups = {relation: [] for relation in ORIGIN_RELATIONS}
        for _, passage in self.ordered_passages():
            for entry in self.claims.entries.get(passage["id"], []):
                origin = entry.get("origin")
                if not origin:
                    continue
                anchor = f'{passage["id"]}--claim--{entry["id"]}'
                source = (str(self.root.cards[origin["src"]].get("title")) if origin.get("src") else origin["cite"])
                mark = "（代替資料）" if origin.get("substitute") else ""
                groups[origin["relation"]].append(
                    f'<li data-origin="{anchor}"><a href="{PROOFS_PAGE}#{anchor}">'
                    f'{escape(self.claim_title(passage["id"], entry["id"]))}</a>　{escape(source)}{mark}</li>')
        return "".join(f'<p class="fact-part-heading">{ORIGIN_RELATIONS[relation]}（{len(items)}件）</p>'
                       f'<ul class="origin-list">{"".join(items)}</ul>' for relation, items in groups.items() if items)
