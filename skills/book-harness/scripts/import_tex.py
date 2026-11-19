#!/usr/bin/env python3
"""Cut labelled statement blocks of a TeX file into legacy cards (a read-only mirror).

Usage:
  import_tex.py --tex FILE --root BOOKROOT --route SLUG --area AREA [--map map.json]
                [--lines A-B ...] [--owner BOOK] [--status self-checked] [--dry-run]

Each labelled definition / theorem / lemma / proposition / corollary / axiom block becomes an
A1 / A2 / A6 card (`legacy: true`, one `## 本文` section); the proof that follows becomes an A3 card
that `proves` it.  The route lists the cards in text order under the section headings of the TeX.
Labelled `example` / `exercise` environments become A4 / A5 cards, and a proof environment labelled
`sol:NAME` becomes the A3 solution of `exer:NAME`.  `--lines` keeps only blocks starting in the given
line ranges (repeatable); `--owner` records the book that owns them.
Unlabelled blocks and prose are counted and reported, not imported.
Existing cards are never overwritten.  `map.json` maps a TeX label to
{"id", "aliases", "requires", "title", "sources"}; ids missing from the map are derived from the label.
Nothing is read from original sources: only the TeX given.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve()
sys.path.insert(0, str(HERE.parents[2] / "reading-book" / "scripts"))
sys.path.insert(0, str(HERE.parents[3] / "src"))

import tex_blocks  # noqa: E402
from labo_tools.book import dump_card  # noqa: E402

KIND = {"definition": "A1", "theorem": "A2", "lemma": "A2", "proposition": "A2", "corollary": "A2", "axiom": "A6"}
HEADING = re.compile(r"\\(chapter|section|subsection)\*?(?:\[[^\]]*\])?\{([^}]*)\}")
BEGIN_PROOF = re.compile(r"\\begin\{proof\}")


def derive_id(label: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", label.lower()).strip("-")


def inner(lines: list, env: str) -> tuple:
    """(optional title, content) of an environment given its lines."""
    text = "\n".join(lines)
    m = re.search(r"\\begin\{%s\*?\}(\[[^\]]*\])?" % env, text)
    body = text[m.end():] if m else text
    body = re.sub(r"\\end\{%s\*?\}\s*$" % env, "", body.rstrip())
    return (m.group(1)[1:-1] if m and m.group(1) else ""), body.strip("\n")


def simple_envs(lines: list, envs: tuple) -> list:
    """Labelled environments (not followed by proofs): [{env, label, start, end}] with 1-based lines."""
    out, i = [], 0
    while i < len(lines):
        m = re.search(r"\\begin\{(%s)\}" % "|".join(envs), lines[i])
        if not m or lines[i].lstrip().startswith("%"):
            i += 1
            continue
        env, depth, j = m.group(1), 0, i
        while j < len(lines):
            depth += len(re.findall(r"\\begin\{%s\}" % env, lines[j])) - len(re.findall(r"\\end\{%s\}" % env, lines[j]))
            if depth <= 0:
                break
            j += 1
        label = next((x.group(1) for k in range(i, min(j, i + 4) + 1) for x in [re.search(r"\\label\{([^}]+)\}", lines[k])] if x), None)
        out.append({"env": env, "label": label, "start": i + 1, "end": min(j, len(lines) - 1) + 1})
        i = j + 1
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--tex", required=True, type=Path)
    ap.add_argument("--root", required=True, type=Path)
    ap.add_argument("--route", required=True)
    ap.add_argument("--area", required=True)
    ap.add_argument("--map", type=Path)
    ap.add_argument("--lines", action="append", default=[], help="START-END, repeatable")
    ap.add_argument("--owner")
    ap.add_argument("--status", default="self-checked")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args(argv)
    text = a.tex.read_text(encoding="utf-8")
    lines = text.splitlines()
    mapping = json.loads(a.map.read_text(encoding="utf-8")) if a.map else {}
    headings = [(i + 1, m.group(2)) for i, ln in enumerate(lines) for m in [HEADING.search(ln)] if m]
    ranges = [tuple(int(x) for x in r.split("-")) for r in a.lines]
    inside = lambda n: not ranges or any(lo <= n <= hi for lo, hi in ranges)  # noqa: E731
    blocks = [b for b in tex_blocks.blocks(text) if inside(b["start"])]
    planned, skipped, ids = [], {"unlabelled": 0, "incomplete": 0, "unsupported_env": 0}, {}
    for b in blocks:
        if not b["label"]:
            skipped["unlabelled"] += 1
            continue
        if not b["complete"]:
            skipped["incomplete"] += 1
        entry = mapping.get(b["label"], {})
        cid = entry.get("id") or derive_id(b["label"])
        if cid in ids:
            cid = f"{cid}-{len(ids)}"
        ids[cid] = b
        planned.append((cid, b, entry))
    known = set(ids)
    dangling, cards, order = [], [], []
    for cid, b, entry in planned:
        sec = next((t for n, t in reversed(headings) if n <= b["start"]), "")
        stmt = lines[b["start"] - 1:b["stmt_end"]]
        title, body = inner(stmt, b["env"])
        reqs = []
        for r in entry.get("requires", []):
            (reqs if r in known and r != cid else dangling).append(r if r in known and r != cid else (cid, r))
        meta = {"id": cid, "kind": KIND[b["env"]], "title": entry.get("title") or title or b["label"],
                "aliases": entry.get("aliases", []) + [b["label"]], "area": a.area, "legacy": True,
                "label": b["label"], "requires": [], "references": [], "symbols": [], "index": [],
                "sources": entry.get("sources", []), "status": a.status}
        if a.owner:
            meta["owner_route"] = a.owner
        if b["env"] in ("theorem", "lemma", "proposition", "corollary"):
            meta["env"] = b["env"]
        if meta["kind"] in ("A1", "A2"):
            meta["variant"] = "unclassified"
        proof = None
        if b["has_proof"]:
            first = next((k for k in range(b["stmt_end"], b["end"]) if BEGIN_PROOF.search(lines[k])), None)
            if first is not None:
                _, pbody = inner(lines[first:b["end"]], "proof")
                proof = pbody
        if proof is not None:
            meta_p = {"id": f"proof-{cid}", "kind": "A3", "title": f"Proof of {meta['title']}", "variant": "unclassified",
                      "proves": cid, "owner": True, "legacy": True, "area": a.area, "requires": reqs, "references": [],
                      "status": a.status}
            cards.append((f"pool/{a.area}/proof-{cid}.md", dump_card(meta_p, f"## 本文\n\n{proof}\n")))
        else:
            meta["requires"] = reqs
        cards.append((f"pool/{a.area}/{cid}.md", dump_card(meta, f"## 本文\n\n{body}\n")))
        order.append((sec, cid))
    extra = [e for e in simple_envs(lines, ("example", "exercise", "proof")) if inside(e["start"])]
    absorbed = {b["start"] for b in blocks}
    exer_ids = {}
    for e in extra:
        if e["env"] == "exercise" and e["label"]:
            exer_ids[e["label"].split(":", 1)[-1]] = derive_id(e["label"])
    for e in extra:
        label = e["label"]
        if not label or e["env"] == "proof" and not label.startswith("sol:"):
            continue
        if any(b["start"] <= e["start"] <= b["end"] for b in blocks):
            continue  # a proof that belongs to a statement block
        entry = mapping.get(label, {})
        cid = entry.get("id") or derive_id(label)
        sec = next((t_ for n, t_ in reversed(headings) if n <= e["start"]), "")
        title, body = inner(lines[e["start"] - 1:e["end"]], e["env"])
        base = {"area": a.area, "legacy": True, "label": label, "status": a.status}
        if a.owner:
            base["owner_route"] = a.owner
        if e["env"] == "proof":
            target = exer_ids.get(label.split(":", 1)[-1])
            if not target:
                skipped["unsupported_env"] += 1
                continue
            meta = {"id": cid, "kind": "A3", "title": f"Solution of {target}", "variant": "unclassified",
                    "proves": target, "owner": True, **base, "requires": [], "references": []}
        else:
            kind = "A4" if e["env"] == "example" else "A5"
            meta = {"id": cid, "kind": kind, "title": entry.get("title") or title or label, **base,
                    "aliases": entry.get("aliases", []) + [label], "requires": [], "references": [], "symbols": [],
                    "index": [], "sources": entry.get("sources", [])}
            if kind == "A4":
                meta["variant"] = "unclassified"
            order.append((sec, cid))
        cards.append((f"pool/{a.area}/{cid}.md", dump_card(meta, f"## 本文\n\n{body}\n")))
    sections: list = []
    for sec, cid in order:
        if not sections or sections[-1]["title"] != sec:
            sections.append({"title": sec, "items": []})
        sections[-1]["items"].append(cid)
    import yaml

    route_text = yaml.safe_dump({"title": a.route, "sections": sections}, allow_unicode=True, sort_keys=False)
    written = skipped_existing = 0
    for rel, content in cards + [(f"route/{a.route}/route.yaml", route_text)]:
        path = a.root / rel
        if path.exists():
            skipped_existing += 1
            continue
        if not a.dry_run:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
        written += 1
    print(json.dumps({"blocks": len(blocks), "cards_planned": len(cards), "written": written,
                      "existing_left_alone": skipped_existing, "skipped": skipped, "sections": len(sections),
                      "dangling_requires": [list(x) for x in dangling],
                      "not_imported": "prose, remarks and unlabelled blocks"},
                     ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
