"""One route-wide identity for a formula in the TeX and HTML editions."""

from __future__ import annotations

from collections import Counter
from copy import copy
from dataclasses import dataclass
import hashlib
import re

# Top-level displayed groups receive one number. An aligned or gathered payload
# remains one formula; authors can use distinct displays for separately cited lines.
MATH = re.compile(
    r"\\\[(.*?)\\\]|\$\$(.*?)\$\$|\\begin\{(equation|align|gather|multline)(\*?)\}"
    r"(.*?)\\end\{\3\4\}|\\\((.*?)\\\)|(?<!\\)\$([^$\n]+?)(?<!\\)\$", re.S)
LABEL = re.compile(r"\\label\{([^{}]+)\}")
EQ_LABEL = re.compile(r"eq:[a-zA-Z0-9][a-zA-Z0-9:._-]*\Z")
TEX_REF = re.compile(r"\\(cref|Cref|eqref|ref|pageref)\*?\{([^{}]+)\}")

FIELDS = {
    "A1": ("definition", "notation"), "A2": ("hypotheses", "conclusion"),
    "A3": ("steps",), "A4": ("setting", "verification"), "A5": ("question", "solution"),
    "A6": ("convention",), "B5": ("endpoint", "known", "conventions", "reader"),
}


def fields(card):
    if card.legacy and card.sections.get("body"):
        return ("body",)
    return FIELDS.get(card.kind, tuple(card.sections))


def normalize(text):
    return re.sub(r"\s+|\\(?:,|;|!|quad\b|qquad\b|left\b|right\b)", "", LABEL.sub("", text))


@dataclass(frozen=True)
class Formula:
    card: str
    field: str
    start: int
    end: int
    math: str
    display: bool
    label: str
    explicit: bool
    native: str | None


def scan(card):
    seen = Counter()
    for field in fields(card):
        text = card.sections.get(field, "")
        for match in MATH.finditer(text):
            a, b, env, _, native_body, inline, dollars = match.groups()
            raw = next(item for item in (a, b, native_body, inline, dollars) if item is not None)
            content = LABEL.sub("", raw).strip()
            labels = LABEL.findall(raw)
            if len(labels) > 1:
                # Multiple explicitly cited lines must be distinct numbered displays.
                raise ValueError(f"{card.id}: one formula group contains multiple labels: {', '.join(labels)}")
            if labels and not EQ_LABEL.fullmatch(labels[0]):
                raise ValueError(f"{card.id}: equation label must begin with eq: ({labels[0]})")
            digest = hashlib.sha256(normalize(raw).encode()).hexdigest()[:10]
            key = f"eq:{card.id}:{field}:{digest}"
            seen[key] += 1
            label = labels[0] if labels else key if seen[key] == 1 else f"{key}-{seen[key]}"
            yield Formula(card.id, field, match.start(), match.end(), content,
                          a is not None or b is not None or env is not None,
                          label, bool(labels), env)


class Equations:
    def __init__(self, cards, *, strict=False, enabled=True):
        # Some rendered routes display the same card more than once.
        cards = {card.id: card for card in cards}
        self.by_card = {cid: list(scan(card)) if enabled else [] for cid, card in cards.items()}
        self.selected = {}
        if not enabled:
            return
        index_targets = set()
        for card in cards.values():
            for entry in card.meta.get("formula_index") or []:
                target = entry.get("target") if isinstance(entry, dict) else None
                if target:
                    if not isinstance(target, str) or not EQ_LABEL.fullmatch(target):
                        raise ValueError(f"{card.id}: bad formula index target {target!r}")
                    index_targets.add(target)
                elif strict:
                    raise ValueError(f"{card.id}: formula index entry needs an exact target")
        for card in cards.values():
            for field in fields(card):
                for match in TEX_REF.finditer(card.sections.get(field, "")):
                    labels = [label.strip() for label in match[2].split(",")]
                    if strict and match[1] == "eqref" and (len(labels) != 1 or not EQ_LABEL.fullmatch(labels[0])):
                        raise ValueError(f"{card.id}: eqref must name one equation: {match[0]}")
                    index_targets.update(label for label in labels if label.startswith("eq:"))
        for formulas in self.by_card.values():
            for formula in formulas:
                if not (formula.display or formula.explicit or formula.label in index_targets):
                    continue
                if formula.label in self.selected:
                    raise ValueError(f"{formula.card}: duplicate equation label {formula.label}")
                self.selected[formula.label] = formula
        missing = index_targets - self.selected.keys()
        if missing:
            raise ValueError("missing equation targets: " + ", ".join(sorted(missing)))

    def rewrite(self, card, field, emitter):
        s = card.sections.get(field, "")
        parts, at = [], 0
        for f in self.by_card.get(card.id, ()):
            if f.field == field and f.label in self.selected:
                parts.extend((s[at:f.start], emitter(f)))
                at = f.end
        parts.append(s[at:])
        return "".join(parts)


def display_math(f):
    if f.native == "align":
        return r"\begin{aligned}" + f.math + r"\end{aligned}"
    if f.native in ("gather", "multline"):
        return r"\begin{gathered}" + f.math + r"\end{gathered}"
    return f.math


def emit_tex(f):
    if f.display:
        return f"\\begin{{equation}}\\label{{{f.label}}}\n{display_math(f)}\n\\end{{equation}}"
    return rf"\bookinlineequation{{{f.label}}}{{${f.math}$}}"


# The anchor is at the indexed occurrence. Preserve the enclosing theorem's
# current label so that inline notation does not disturb its cross-references.
INLINE_TEX = (r"\newcommand{\bookinlineequation}[2]{"
              r"{\refstepcounter{equation}\label{#1}#2"
              r"\,\textsuperscript{\hyperref[#1]{(\theequation)}}}}" + "\n")


def tex_cards(book, cards, equations):
    result = copy(book)
    result.cards = dict(book.cards)
    visible = {c.id for c in cards}
    for cid in visible:
        card = copy(book.cards[cid])
        card.sections = {key: equations.rewrite(card, key, emit_tex) for key in card.sections}
        entries = card.meta.get("formula_index") or []
        if entries:
            card.meta = card.meta.copy()
            card.meta["formula_index"] = [
                entry for entry in entries
                if not isinstance(entry, dict) or not entry.get("target")
                or (entry["target"] in equations.selected and equations.selected[entry["target"]].card in visible)
            ]
        result.cards[cid] = card
    return result


def reference_directory_tex(statements, equations, *, language="ja", hierarchical=True):
    ja = language == "ja"
    heading = "chapter" if hierarchical else "section"
    groups = (
        ("定義・定理・演習一覧" if ja else "Definitions, theorems and exercises", statements),
        ("数式番号一覧" if ja else "Equation numbers", equations),
    )
    result = []
    for title, entries in groups:
        if entries:
            result.extend((rf"\{heading}*{{{title}}}", rf"\addcontentsline{{toc}}{{{heading}}}{{{title}}}",
                           r"\begin{multicols}{3}"))
            result.extend(rf"\noindent\cref{{{label}}}\par" for label in entries)
            result.append(r"\end{multicols}")
    return "\n".join(result) + "\n"
