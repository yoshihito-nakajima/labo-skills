#!/usr/bin/env python3
"""Mechanical evidence that a taken-in source followed the book-harness loop (see assets/trial/README.md).

  trial_check.py --root BOOKROOT --route SLUG --source-id C1ID --source-text DIR [--review-input DIR]
Exit 0 when every automated item passes; the manual items are always listed.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "src"))

from labo_tools import book as bk  # noqa: E402
from labo_tools import book_review as rev  # noqa: E402

MANUAL = ["the planted error (a product of two odd numbers is odd) is corrected and recorded in a C2 `difference`",
          "the exercise is restated in the book's own words, with a worked solution",
          "the boundary case n = 0 (and negative integers) is handled where it matters",
          "the sketch proof was replaced by a complete one, with every step justified",
          "the report says which cards were independently reviewed and which were not"]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", required=True, type=Path)
    ap.add_argument("--route", required=True)
    ap.add_argument("--source-id", required=True)
    ap.add_argument("--source-text", required=True, action="append")
    ap.add_argument("--review-input", type=Path)
    a = ap.parse_args(argv)
    book = bk.Book(a.root, use_cache=False)
    res = bk.check(book, a.route)
    results = []

    def item(name, ok, detail=""):
        results.append((ok, name, detail))

    item("book check has no errors", not res["errors"], "; ".join(res["errors"][:3]))
    c1 = book.cards.get(a.source_id)
    item("the source record exists (C1)", c1 is not None and c1.kind == "C1")
    rows = [c for c in book.cards.values() if c.kind == "C2" and c.route == a.route]
    item("source mapping rows exist (C2)", bool(rows))
    item("every C2 row has locators into the source", all(
        any(isinstance(s, dict) and s.get("src") == a.source_id and s.get("loc") for s in r.meta.get("sources") or [])
        for r in rows) and bool(rows))
    item("no mapping row is left TODO", all(r.meta.get("scope_audit") != "TODO" for r in rows) and bool(rows))
    facts = [c for c in book.cards.values() if c.kind in ("A1", "A2", "A3", "A4", "A5", "A6") and a.source_id in
             " ".join(str(s.get("src")) for s in c.meta.get("sources") or [] if isinstance(s, dict))]
    item("fact cards cite the source", bool(facts))
    item("new fact cards were made through the pool search (a `searched` record)",
         all(c.meta.get("searched") for c in facts if c.kind != "A3"))
    item("no legacy cards among the new ones", not any(c.legacy for c in book.cards.values()))
    proofs = [c for c in book.cards.values() if c.kind == "A3"]
    item("proofs exist, and those with prerequisites cite them with [by: ...]", bool(proofs) and all(
        bk.BY_RE.search(c.sections.get("steps", "")) for c in proofs if c.requires))
    stats: dict = {}
    hits = rev.leak_check(book, [Path(p) for p in a.source_text], route=a.route, stats=stats)
    item("no verbatim run of the source in any card", stats.get("words", 0) > 0 and not hits,
         ", ".join(h["id"] for h in hits))
    packets = sorted(a.review_input.glob("packet-*/manifest.json")) if a.review_input else []
    if a.review_input:
        ok = bool(packets)
        for m in packets:
            for entry in json.loads(m.read_text())["cards"]:
                ok &= entry["id"] in book.cards and book.cards[entry["id"]].fingerprint() == entry["fp"]
        item("a review packet exists and matches the current cards", ok)
    for ok, name, detail in results:
        print(("PASS " if ok else "FAIL ") + name + (f" ({detail})" if detail and not ok else ""))
    print("\nTo judge by reading:")
    for m in MANUAL:
        print("  - " + m)
    return int(not all(ok for ok, _, _ in results))


if __name__ == "__main__":
    raise SystemExit(main())
