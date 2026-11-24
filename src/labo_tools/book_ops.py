"""Operations that keep a large card pool tidy: show, list, merge, rename, retire, restructure, dependency candidates.

Every operation that rewrites files takes the root lock, works on a fresh read, and is a dry run unless
`apply=True`.  Rewriting a card re-serializes its front matter, so comments in the YAML are not kept.
Nothing is deleted: merged, renamed and retired cards move to `<root>/retired/` with a pointer.
"""

from __future__ import annotations

import re
from pathlib import Path

import yaml

from .book import (BookError, Book, Card, MENTION_RE, TEMPLATES, book_lock, clean_tex, dump_card, UNCLASSIFIED)

LIST_FIELDS = ("requires", "requires_candidates", "references", "between", "forward", "answered_by",
               "conventions", "well_defined")
SCALAR_FIELDS = ("proves", "illustrates", "target")
BY_RE = re.compile(r"(\[by:\s*)([^\]]+)(\])")


# ---------------------------------------------------------------- reading the pool


def used_by(book: Book, cid: str) -> list:
    return sorted(c.id for c in book.cards.values() if cid in c.requires and c.id != cid)


def show(book: Book, cid: str) -> dict:
    """A card with its neighbourhood: what it needs, what uses it, proofs, mappings, findings, reviews."""
    card = book.cards.get(cid)
    if card is None:
        raise BookError(f"unknown card {cid}")
    brief = lambda x: {"id": x, "kind": book.cards[x].kind, "title": book.cards[x].meta.get("title", ""),  # noqa: E731
                       "summary": book.cards[x].summary(100)} if x in book.cards else {"id": x, "missing": True}
    routes = [r for r in book.routes() if any(e["id"] == cid for e in book.sequence(book.load_route(r)))]
    return {
        "id": cid, "kind": card.kind, "variant": card.meta.get("variant"), "title": card.meta.get("title"),
        "status": card.meta.get("status"), "fingerprint": card.fingerprint(), "legacy": card.legacy,
        "aliases": card.meta.get("aliases") or [], "path": str(card.path.relative_to(book.root)),
        "sources": card.meta.get("sources") or [], "relations": card.meta.get("relations") or [],
        "reviews": card.meta.get("reviews") or [], "reviewed_current": card.reviewed_current(),
        "requires": [brief(x) for x in card.requires],
        "requires_candidates": [brief(x) for x in card.meta.get("requires_candidates") or []],
        "used_by": [brief(x) for x in used_by(book, cid)],
        "proofs": [x.id for x in book.proofs_of(cid)],
        "mapped_by": sorted(c.id for c in book.cards.values() if c.kind == "C2"
                            and any(isinstance(m, dict) and m.get("card") == cid for m in c.meta.get("maps_to") or [])),
        "findings": sorted(c.id for c in book.cards.values() if c.kind == "D1" and c.meta.get("target") == cid),
        "routes": routes, "sections": dict(card.sections), "body": card.body if card.legacy else None,
    }


def render_show(info: dict) -> list:
    lines = [f"{info['id']}  [{info['kind']}{'/' + info['variant'] if info.get('variant') else ''}]  "
             f"{info.get('title') or ''}",
             f"status {info.get('status')}  fingerprint {info['fingerprint']}  file {info['path']}"
             + ("  LEGACY" if info["legacy"] else "")]
    for key in ("aliases", "routes", "proofs", "mapped_by", "findings"):
        if info[key]:
            lines.append(f"{key}: " + ", ".join(info[key]))
    for s in info["sources"]:
        lines.append(f"source: {s.get('src', '')} {s.get('loc', '')}")
    for key in ("requires", "requires_candidates", "used_by"):
        if info[key]:
            lines.append(f"{key}:")
            lines += [f"  {x['id']}" + ("" if x.get("missing") else f" [{x['kind']}] {x['summary']}") for x in info[key]]
    for r in info["reviews"]:
        lines.append(f"review: {r.get('kind')} {r.get('result')} fp {r.get('fp')} {r.get('date', '')}")
    lines.append("")
    for k, v in info["sections"].items():
        lines += [f"## {k}", v, ""]
    return lines


def list_cards(book: Book, *, route: str | None = None, kind: str | None = None, area: str | None = None,
               status: str | None = None, stale: bool = False, legacy: bool = False, limit: int = 0) -> list:
    ids = None
    if route:
        ids = [e["id"] for e in book.sequence(book.load_route(route))]
    pool = [book.cards[i] for i in ids if i in book.cards] if ids is not None else list(book.cards.values())
    stale_ids = set()
    if stale:
        for c in book.cards.values():
            for a, fp in (c.meta.get("anchors") or {}).items():
                if a in book.cards and book.cards[a].fingerprint() != fp:
                    stale_ids.add(c.id)
    out = [c for c in pool if (not kind or c.kind == kind) and (not area or c.meta.get("area") == area)
           and (not status or c.meta.get("status") == status) and (not stale or c.id in stale_ids)
           and (not legacy or c.legacy)]
    return out[:limit] if limit else out


# ---------------------------------------------------------------- rewriting references


def _swap(value, mapping: dict):
    return mapping.get(value, value)


def _dedupe(items: list, drop: str | None = None) -> list:
    seen, out = set(), []
    for x in items:
        key = yaml.safe_dump(x, sort_keys=True) if isinstance(x, dict) else x
        if key not in seen and x != drop:
            seen.add(key)
            out.append(x)
    return out


def rewrite_card(card: Card, mapping: dict) -> tuple:
    """(new meta, new body, changed) after replacing ids by `mapping` in every reference position."""
    meta = {k: v for k, v in card.meta.items()}
    for f in LIST_FIELDS:
        if meta.get(f):
            meta[f] = _dedupe([_swap(x, mapping) for x in meta[f]], card.id)
    for f in SCALAR_FIELDS:
        if meta.get(f):
            meta[f] = _swap(meta[f], mapping)
    if meta.get("anchors"):
        meta["anchors"] = {_swap(k, mapping): v for k, v in meta["anchors"].items()}
    for f, key in (("maps_to", "card"), ("borrows", "card"), ("relations", "to"), ("sources", "src")):
        if meta.get(f):
            meta[f] = _dedupe([{**x, key: _swap(x.get(key), mapping)} if isinstance(x, dict) else x for x in meta[f]])
    body = MENTION_RE.sub(lambda m: f"[[{_swap(m.group(1), mapping)}]]", card.body)
    body = BY_RE.sub(lambda m: m.group(1) + ", ".join(_swap(x.strip(), mapping) for x in m.group(2).split(",")) + m.group(3), body)
    return meta, body, (meta != card.meta or body != card.body)


def _rewrite_routes(book: Book, mapping: dict, apply: bool) -> list:
    changed = []
    for slug in book.routes():
        path = book.root / "route" / slug / "route.yaml"
        try:
            data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        except (yaml.YAMLError, UnicodeDecodeError) as exc:
            raise BookError(f"route {slug}: route.yaml cannot be read: {exc}") from exc
        hit = [False]

        def fix(item):
            if isinstance(item, str):
                new = _swap(item, mapping)
                hit[0] |= new != item
                return new
            if isinstance(item, dict):
                out = dict(item)
                for k in ("card", "proof_of"):
                    if k in out:
                        new = _swap(out[k], mapping)
                        hit[0] |= new != out[k]
                        out[k] = new
                if out.get("proof") in mapping:
                    out["proof"] = mapping[out["proof"]]
                    hit[0] = True
                return out
            return item

        targets = set(mapping.values())
        seen_targets: set = set()
        for sec in data.get("sections") or []:
            items = []
            for item in (fix(i) for i in sec.get("items") or []):
                cid = item if isinstance(item, str) else item.get("card") if isinstance(item, dict) else None
                if cid in targets:  # a merge can list the same card twice: keep the first place only
                    if cid in seen_targets:
                        hit[0] = True
                        continue
                    seen_targets.add(cid)
                items.append(item)
            sec["items"] = items
        data["appendix"] = [fix(i) for i in data.get("appendix") or []] if data.get("appendix") else data.get("appendix")
        if not data.get("appendix"):
            data.pop("appendix", None)
        if hit[0]:
            changed.append(f"route/{slug}/route.yaml")
            if apply:
                path.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8")
    return changed


def _retire_file(book: Book, card: Card, extra: dict) -> Path:
    target = book.root / "retired" / f"{card.id}.md"
    if target.exists():
        raise BookError(f"already retired: {target}")
    target.parent.mkdir(parents=True, exist_ok=True)
    meta = {**card.meta, **extra}
    target.write_text(dump_card(meta, card.body), encoding="utf-8")
    card.path.unlink()
    return target


def _apply_mapping(book: Book, mapping: dict, skip: set, apply: bool) -> list:
    lines = []
    for c in book.cards.values():
        if c.id in skip:
            continue
        meta, body, changed = rewrite_card(c, mapping)
        if changed:
            lines.append(f"rewrite references in {c.id}")
            if apply:
                c.path.write_text(dump_card(meta, body), encoding="utf-8")
    lines += [f"rewrite {x}" for x in _rewrite_routes(book, mapping, apply)]
    return lines


# ---------------------------------------------------------------- merge, rename, retire


def merge(root: Path, keep: str, drop: str, apply: bool = False) -> list:
    """Make `drop` an alias of `keep`: rewrite every reference, move `drop` to retired/ with a pointer."""
    with book_lock(root):
        book = Book(root, use_cache=False)
        a, b = book.cards.get(keep), book.cards.get(drop)
        if a is None or b is None:
            raise BookError("both cards must exist")
        if keep == drop:
            raise BookError("keep and drop are the same card")
        if a.kind != b.kind:
            raise BookError(f"kinds differ ({a.kind} vs {b.kind}); merge only the same kind of card")
        lines = [f"merge {drop} into {keep}: {drop} becomes an alias of {keep}"]
        if set(b.requires) - set(a.requires) - {keep}:
            lines.append(f"note: {drop} required {sorted(set(b.requires) - set(a.requires))}, which {keep} does not; "
                         f"decide by hand whether {keep} needs them")
        if a.kind == "A2" and book.proofs_of(drop) and book.proofs_of(keep):
            lines.append("note: both claims have proofs; after the merge mark one proof owner and the others owner: false")
        lines += _apply_mapping(book, {drop: keep}, {drop}, apply)
        if apply:
            meta = dict(a.meta)
            meta["aliases"] = _dedupe(list(meta.get("aliases") or []) + [drop] + list(b.meta.get("aliases") or []))
            meta["sources"] = _dedupe(list(meta.get("sources") or []) + list(b.meta.get("sources") or []))
            a.path.write_text(dump_card(meta, a.body), encoding="utf-8")
            _retire_file(book, b, {"merged_into": keep})
            lines.append(f"moved {drop} to retired/")
        return lines


def rename(root: Path, old: str, new: str, apply: bool = False) -> list:
    from .book import ID_RE

    with book_lock(root):
        book = Book(root, use_cache=False)
        card = book.cards.get(old)
        if card is None:
            raise BookError(f"unknown card {old}")
        if not ID_RE.match(new) or new in book.cards:
            raise BookError(f"{new} is not a free kebab-case id")
        lines = [f"rename {old} -> {new}; {old} stays as an alias"]
        lines += _apply_mapping(book, {old: new}, {old}, apply)
        if apply:
            meta = {**card.meta, "id": new}
            meta["aliases"] = _dedupe(list(meta.get("aliases") or []) + [old])
            target = card.path.with_name(f"{new}.md")
            target.write_text(dump_card(meta, card.body), encoding="utf-8")
            card.path.unlink()
        return lines


def retire(root: Path, cid: str, reason: str, apply: bool = False, force: bool = False) -> list:
    with book_lock(root):
        book = Book(root, use_cache=False)
        card = book.cards.get(cid)
        if card is None:
            raise BookError(f"unknown card {cid}")
        referrers = sorted(c.id for c in book.cards.values() if c.id != cid and cid in c.ref_ids())
        lines = [f"retire {cid}: {reason}"]
        if referrers and not force:
            raise BookError(f"{cid} is still referenced by {', '.join(referrers[:8])}"
                            f"{' ...' if len(referrers) > 8 else ''}; merge or rewrite them first (or --force)")
        if apply:
            lines.append(f"moved to {_retire_file(book, card, {'retired': reason}).relative_to(book.root)}")
        return lines


# ---------------------------------------------------------------- legacy cards


def restructure(root: Path, cid: str) -> str:
    """Rewrite a legacy card as the template's sections (placeholders) beside the old text, for splitting by hand.

    The old text stays under '本文'.  The producer fills the sections, deletes '本文', sets `legacy: false`
    and chooses the variant; `check` warns while either is left.
    """
    with book_lock(root):
        book = Book(root, use_cache=False)
        card = book.cards.get(cid)
        if card is None or card.template is None:
            raise BookError(f"unknown card {cid}")
        if not card.legacy:
            raise BookError(f"{cid} is not a legacy card")
        sections = "".join(f"## {ja}\n\nTODO\n\n" for _, ja, _en in card.template.required)
        meta = dict(card.meta)
        meta["restructure"] = "started"
        card.path.write_text(dump_card(meta, sections + f"## 本文\n\n{card.sections.get('body', '').strip()}\n"),
                             encoding="utf-8")
        return str(card.path.relative_to(book.root))


# ---------------------------------------------------------------- dependency candidates

REF_RE = re.compile(r"\\(?:c|C|eq|auto)?ref\*?\{([^}]*)\}|\\(?:cref|Cref)\{([^}]*)\}")
LABEL_RE = re.compile(r"\\label\{([^}]+)\}")


def label_owners(book: Book) -> dict:
    """label -> card id: a card's own label, its aliases, and every \\label written inside its text."""
    owners = {}
    for c in book.cards.values():
        if c.kind in ("A1", "A2", "A3", "A4", "A5", "A6"):
            for lab in [c.meta.get("label")] + list(c.meta.get("aliases") or []) + LABEL_RE.findall(c.body):
                if lab and lab not in owners:
                    owners[lab] = c.id
    return owners


def deps_candidates(root: Path, route: str | None = None, write: bool = False) -> dict:
    """Candidate `requires` from \\ref-style citations in card text (and `[[card]]` mentions).

    Candidates are only mentions: a result cited in motivation is not a prerequisite.  With write=True they go
    to `requires_candidates` (never to `requires`); a producer promotes the real ones with `promote`.
    """
    with book_lock(root) if write else _null():
        book = Book(root, use_cache=False)
        owners = label_owners(book)
        ids = {e["id"] for e in book.sequence(book.load_route(route))} if route else None
        result, written = {}, 0
        for c in list(book.cards.values()):
            if c.kind not in ("A1", "A2", "A3", "A4", "A5") or (ids is not None and c.id not in ids):
                continue
            cited = []
            for m in REF_RE.finditer(c.body):
                for lab in (m.group(1) or m.group(2) or "").split(","):
                    target = owners.get(lab.strip())
                    if target:
                        cited.append(target)
            cited += [x for x in c.mentions() if x in book.cards]
            own = {c.id, c.meta.get("proves")}
            declined = set(c.meta.get("not_requires") or [])
            new = [x for x in dict.fromkeys(cited) if x not in own and x not in c.requires and x not in declined
                   and book.cards[x].kind != "A3"]
            if new:
                result[c.id] = new
                if write:
                    meta = dict(c.meta)
                    meta["requires_candidates"] = new
                    c.path.write_text(dump_card(meta, c.body), encoding="utf-8")
                    written += 1
        return {"cards_with_candidates": len(result), "edges": sum(len(v) for v in result.values()),
                "written": written, "candidates": result}


def promote(root: Path, cid: str, only: list | None = None) -> list:
    """Move candidates (all, or the listed ones) of a card into its hard `requires`."""
    with book_lock(root):
        book = Book(root, use_cache=False)
        card = book.cards.get(cid)
        if card is None:
            raise BookError(f"unknown card {cid}")
        cand = list(card.meta.get("requires_candidates") or [])
        take = [x for x in cand if only is None or x in only]
        unknown = [x for x in (only or []) if x not in cand]
        if unknown:
            raise BookError(f"not candidates of {cid}: {', '.join(unknown)}")
        meta = dict(card.meta)
        meta["requires"] = _dedupe(list(meta.get("requires") or []) + take)
        rest = [x for x in cand if x not in take]
        if rest:
            meta["requires_candidates"] = rest
        else:
            meta.pop("requires_candidates", None)
        card.path.write_text(dump_card(meta, card.body), encoding="utf-8")
        return take


def reject(root: Path, cid: str, only: list | None = None) -> list:
    """Drop candidates (all, or the listed ones) that are mentions, not prerequisites."""
    with book_lock(root):
        book = Book(root, use_cache=False)
        card = book.cards.get(cid)
        if card is None:
            raise BookError(f"unknown card {cid}")
        cand = list(card.meta.get("requires_candidates") or [])
        gone = [x for x in cand if only is None or x in only]
        rest = [x for x in cand if x not in gone]
        meta = dict(card.meta)
        meta["not_requires"] = _dedupe(list(meta.get("not_requires") or []) + gone)  # not proposed again
        if rest:
            meta["requires_candidates"] = rest
        else:
            meta.pop("requires_candidates", None)
        card.path.write_text(dump_card(meta, card.body), encoding="utf-8")
        return gone


class _null:
    def __enter__(self):
        return None

    def __exit__(self, *exc):
        return False


# ---------------------------------------------------------------- placing cards in a route


def place(root: Path, route: str, ids: list, section: str | None = None, after: str | None = None) -> list:
    """Add cards to a route's reading order (under the root lock, so concurrent writers do not clobber each other).

    `section` is a stable id, title or index; declare the section before placing cards in a chaptered route.
    The default is the last section. `after` puts the
    cards right behind a card already listed.  A card that is already in the route, or is the proof of one that is
    (a claim shows its owning proof by itself), is skipped.
    """
    with book_lock(root):
        book = Book(root, use_cache=False)
        path = book.root / "route" / route / "route.yaml"
        if not path.is_file():
            raise BookError(f"route not found: {route}")
        for cid in ids:
            if cid not in book.cards:
                raise BookError(f"unknown card {cid}")
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        sections = data.setdefault("sections", [])

        def card_of(item):
            return item if isinstance(item, str) else item.get("card") or item.get("proof_of") if isinstance(item, dict) else None

        listed = {card_of(i) for s in sections for i in s.get("items") or []}
        shown = {book.chosen_proof(x) for x in listed if x in book.cards and book.cards[x].kind in ("A1", "A2", "A5")}
        todo = [c for c in ids if c not in listed and c not in shown]
        if not todo:
            return []
        target = None
        if after:
            for s in sections:
                items = s.setdefault("items", [])
                for k, it in enumerate(items):
                    if card_of(it) == after:
                        items[k + 1:k + 1] = todo
                        target = True
                        break
                if target:
                    break
            if not target:
                raise BookError(f"{after} is not listed in route {route}")
        else:
            if section is None:
                if not sections:
                    if data.get("chapters"):
                        raise BookError(f"route {route}: declare a section with an id and chapter before placing cards")
                    sections.append({"title": route, "items": []})
                sec = sections[-1]
            elif str(section).isdigit() and int(section) < len(sections):
                sec = sections[int(section)]
            else:
                sec = next((s for s in sections if section in (s.get("id"), s.get("title"))), None)
                if sec is None:
                    if data.get("chapters"):
                        raise BookError(f"route {route}: unknown section {section!r}; declare its chapter first")
                    sec = {"title": section, "items": []}
                    sections.append(sec)
            sec.setdefault("items", []).extend(todo)
        path.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8")
        return todo
