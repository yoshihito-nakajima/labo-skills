#!/usr/bin/env python3
"""Check that imported legacy cards still say what the TeX says (a lossless-mirror check for the import).

  verify_import.py --tex FILE --root BOOKROOT [--lines A-B ...] [--json]

For every labelled statement block, example, exercise and `sol:` proof in the TeX (inside the given line ranges) it
finds the card carrying that label and compares the normalized text (comments and white space ignored).  It reports
missing cards, changed text and the share of TeX lines that no card covers (prose, remarks, unlabelled material).
Exit 0 only when nothing is missing or changed.  Prose coverage is information, not a failure: it says what a
cut-over would still have to turn into glue or fact cards.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve()
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE.parents[2] / "reading-book" / "scripts"))
sys.path.insert(0, str(HERE.parents[3] / "src"))

import tex_blocks  # noqa: E402
from import_tex import inner, simple_envs, BEGIN_PROOF  # noqa: E402
from labo_tools.book import Book  # noqa: E402


def norm(text: str) -> str:
    return " ".join(re.sub(r"(?<!\\)%[^\n]*", "", text).split())


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--tex", required=True, type=Path)
    ap.add_argument("--root", required=True, type=Path)
    ap.add_argument("--lines", action="append", default=[])
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    text = a.tex.read_text(encoding="utf-8")
    lines = text.splitlines()
    ranges = [tuple(int(x) for x in r.split("-")) for r in a.lines]
    inside = lambda n: not ranges or any(lo <= n <= hi for lo, hi in ranges)  # noqa: E731
    book = Book(a.root, use_cache=False)
    by_label = {c.meta.get("label"): c for c in book.cards.values() if c.meta.get("label")}
    missing, changed, checked = [], [], 0
    covered = set()

    def compare(label, expected, card):
        nonlocal checked
        checked += 1
        if card is None:
            missing.append(label)
        elif norm(card.sections.get("body", "")) != norm(expected):
            changed.append({"label": label, "card": card.id})

    blocks = [b for b in tex_blocks.blocks(text) if inside(b["start"])]
    for b in blocks:
        if not b["label"]:
            continue
        covered.update(range(b["start"], b["end"] + 1))
        card = by_label.get(b["label"])
        compare(b["label"], inner(lines[b["start"] - 1:b["stmt_end"]], b["env"])[1], card)
        if b["has_proof"]:
            first = next((k for k in range(b["stmt_end"], b["end"]) if BEGIN_PROOF.search(lines[k])), None)
            if first is not None:
                proof = next((c for c in book.proofs_of(card.id)), None) if card else None
                compare(f"{b['label']} (proof)", inner(lines[first:b["end"]], "proof")[1], proof)
    for e in simple_envs(lines, ("example", "exercise", "proof")):
        if not inside(e["start"]) or not e["label"]:
            continue
        if e["env"] == "proof" and not e["label"].startswith("sol:"):
            continue
        if any(b["start"] <= e["start"] <= b["end"] for b in blocks):
            continue
        covered.update(range(e["start"], e["end"] + 1))
        compare(e["label"], inner(lines[e["start"] - 1:e["end"]], e["env"])[1], by_label.get(e["label"]))
    scope = [n for n in range(1, len(lines) + 1) if inside(n) and lines[n - 1].strip()
             and not lines[n - 1].lstrip().startswith("%")]
    uncovered = [n for n in scope if n not in covered]
    result = {"checked": checked, "missing_cards": missing, "changed_text": changed,
              "tex_lines": len(scope), "lines_not_in_any_card": len(uncovered),
              "share_not_covered": round(len(uncovered) / len(scope), 3) if scope else 0.0}
    if a.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"checked {checked} labelled items: {len(missing)} without a card, {len(changed)} changed")
        for m in missing[:20]:
            print(f"  MISSING {m}")
        for c in changed[:20]:
            print(f"  CHANGED {c['label']} ({c['card']})")
        print(f"{len(uncovered)} of {len(scope)} non-blank TeX lines ({result['share_not_covered']:.0%}) are in no card "
              f"(prose, remarks, unlabelled material)")
    return int(bool(missing or changed))


if __name__ == "__main__":
    raise SystemExit(main())
