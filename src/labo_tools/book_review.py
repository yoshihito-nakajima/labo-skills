"""Intake review of cards: frozen review packets, recorded reviews bound to fingerprints, and a verbatim check.

A review packet is a list of card ids with fingerprints plus the cards' text; it never contains source text.
A recorded review applies only to a card whose fingerprint still equals the packet's: a changed card is not
reviewed.  The verbatim check compares card text with local source-text files and reports card ids, run lengths
and the card's own words, never the source's.
"""

from __future__ import annotations

import datetime as _dt
import hashlib
import json
import re
import stat
import tempfile
from collections import deque
from pathlib import Path

from .book import BookError, Book, book_lock, dump_card

README = """# Review packet {n} of {total}

Route: {route}.  Kind of review: {kind}.  Cards: {count} ({chars} characters).

Read `cards.md` and judge only the listed cards (marked REVIEW).  Cards marked CONTEXT are shown for their statements
only; they are not under review.  `manifest.json` fixes each card's fingerprint: report against these ids.

Return: a report with, for each finding, the card id, the location in the card, what is wrong, severity (major or
minor) and the smallest repair; and the list of card ids you checked completely.  Do not edit cards, the manifest
or anything outside your result folder.  Do not copy source text into the report.
"""


def _sha(path: Path) -> str:
    with path.open("rb") as file:
        return hashlib.file_digest(file, "sha256").hexdigest()


def select(book: Book, route: str, *, cards: list | None = None, section: int | str | None = None,
           closure: str | None = None, unreviewed: str | None = None) -> list:
    data = book.load_route(route)
    seq = book.sequence(data)
    order = list(dict.fromkeys(e["id"] for e in seq if e["id"] in book.cards))
    pool = [i for i in order if book.cards[i].kind in ("A1", "A2", "A3", "A4", "A5", "A6")]
    if cards:
        unknown = [c for c in cards if c not in book.cards]
        if unknown:
            raise BookError(f"unknown cards: {', '.join(unknown)}")
        want = set(cards) | {p.id for c in cards for p in book.proofs_of(c)}
        return [i for i in pool if i in want] + [c for c in cards if c not in pool]
    if section is not None:
        if isinstance(section, str):
            if section.isdecimal():
                section = int(section)
            else:
                indexes = [i for i, row in enumerate(data["sections"]) if row["id"] == section]
                if len(indexes) != 1:
                    raise BookError(f"route {route}: section id {section!r} must identify one section")
                section = indexes[0]
        return [e["id"] for e in seq if e["section"] == section and e["id"] in pool]
    if closure:
        if closure not in book.cards:
            raise BookError(f"unknown card {closure}")
        keep = set(book.closure([closure]))
        keep |= {book.chosen_proof(x) for x in list(keep) if book.cards[x].kind in ("A1", "A2", "A5")}
        return [i for i in pool if i in keep]
    if unreviewed:
        return [i for i in pool if not book.cards[i].reviewed_current(unreviewed)]
    return pool


def review_input(book: Book, route: str, out: Path, kind: str = "math", max_chars: int = 60000, **selection) -> list:
    """Write frozen packets under `out` (must not exist). Returns the packet directories."""
    ids = select(book, route, **selection)
    if not ids:
        raise BookError("nothing to review: the selection is empty")
    if out.exists():
        raise BookError(f"{out} exists; review inputs are immutable, choose a new folder")
    packets, cur, size = [], [], 0
    for cid in ids:
        n = len(book.cards[cid].path.read_text(encoding="utf-8"))
        if cur and size + n > max_chars:
            packets.append(cur)
            cur, size = [], 0
        cur.append(cid)
        size += n
    packets.append(cur)
    dirs = []
    for k, group in enumerate(packets, 1):
        d = out / f"packet-{k:02d}"
        d.mkdir(parents=True)
        context, seen = [], set(group)
        for cid in group:
            for r in book.node_requires(cid) if book.cards[cid].kind in ("A1", "A2", "A5") else book.cards[cid].requires:
                if r in book.cards and r not in seen:
                    seen.add(r)
                    context.append(r)
        text = []
        for cid in group:
            c = book.cards[cid]
            text.append(f"<!-- REVIEW {cid} fingerprint {c.fingerprint()} -->\n{c.path.read_text(encoding='utf-8')}")
        for cid in context:
            c = book.cards[cid]
            text.append(f"<!-- CONTEXT {cid} [{c.kind}] statement only -->\n"
                        + "\n".join(f"## {k}\n{v}" for k, v in c.sections.items()
                                    if k in ("definition", "hypotheses", "conclusion", "quantifiers", "convention", "body")
                                    and c.kind != "A3"))
        body = "\n\n---\n\n".join(text)
        (d / "cards.md").write_text(body, encoding="utf-8")
        manifest = {"route": route, "kind": kind, "packet": k, "of": len(packets),
                    "created": _dt.date.today().isoformat(),
                    "cards": [{"id": cid, "fp": book.cards[cid].fingerprint(),
                               "file_sha256": _sha(book.cards[cid].path)} for cid in group],
                    "context": context}
        (d / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=1), encoding="utf-8")
        (d / "README.md").write_text(README.format(n=k, total=len(packets), route=route, kind=kind, count=len(group),
                                                  chars=len(body)), encoding="utf-8")
        dirs.append(d)
    return dirs


def record_review(root: Path, manifest: Path, report: Path, result: str, kind: str | None = None,
                  ids: list | None = None, promote: bool = True, flagged: list | None = None) -> dict:
    """Record a returned review on the cards of a packet whose fingerprints still match.

    `result` is pass (no defect found in the checked cards) or findings.  Only a `pass` of a math review lifts a
    card to status `independent`.  Reports are referenced by hash, not copied.
    """
    if result not in ("pass", "findings"):
        raise BookError("result must be pass or findings")
    data = json.loads(manifest.read_text(encoding="utf-8"))
    kind = kind or data.get("kind", "math")
    report_hash = _sha(report)
    done, stale, skipped = [], [], []
    with book_lock(root):
        book = Book(root, use_cache=False)
        for entry in data["cards"]:
            cid = entry["id"]
            if ids is not None and cid not in ids:
                skipped.append(cid)
                continue
            card = book.cards.get(cid)
            if card is None or card.fingerprint() != entry["fp"]:
                stale.append(cid)  # changed (or gone) since the packet was frozen: not reviewed
                continue
            # a report that lists the cards with findings passes the other checked cards
            own = "findings" if result == "findings" and (flagged is None or cid in flagged) else "pass"
            write_card_review(card, kind, own, report_hash, entry["fp"], promote=promote)
            done.append(cid)
    return {"recorded": done, "changed_since_packet": stale, "not_listed": skipped}


def atomic_text(path: Path, content: str) -> None:
    """Replace one file intact, including if the process is interrupted before the rename."""
    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent,
                                     suffix=".tmp", delete=False) as handle:
        temporary = Path(handle.name)
        try:
            handle.write(content)
            handle.close()
            if path.exists():
                temporary.chmod(stat.S_IMODE(path.stat().st_mode))
            temporary.replace(path)
        finally:
            temporary.unlink(missing_ok=True)


def write_card_review(card, kind: str, result: str, report: str, fp: str, *,
                      promote: bool, retry_safe: bool = False) -> None:
    """Write one card while the caller holds the book lock."""
    meta = dict(card.meta)
    reviews = list(meta.get("reviews") or [])
    stamp = {"kind": kind, "result": result, "report": report, "fp": fp}
    if retry_safe and any(isinstance(review, dict) and
                          all(review.get(key) == value for key, value in stamp.items()) for review in reviews):
        return
    meta["reviews"] = reviews + [{**stamp, "date": _dt.date.today().isoformat()}]
    if promote and result == "pass" and kind == "math" and meta.get("status") in ("drafted", "self-checked"):
        meta["status"] = "independent"
    text = dump_card(meta, card.body)
    if retry_safe:
        atomic_text(card.path, text)
    else:
        card.path.write_text(text, encoding="utf-8")


# ---------------------------------------------------------------- verbatim check

MATH = re.compile(r"\$\$.*?\$\$|\$.*?\$|\\\[.*?\\\]|\\\(.*?\\\)|\\begin\{(equation|align|gather|multline)\*?\}.*?\\end\{\1\*?\}", re.S)
TEXCMD = re.compile(r"\\[A-Za-z]+\*?|\\.")
WORD = re.compile(r"[a-z]+")


def words(text: str, drop_math: bool = True) -> list:
    if drop_math:
        text = MATH.sub(" ", text)
    return WORD.findall(TEXCMD.sub(" ", text).lower())


def leak_check(book: Book, source_dirs: list, *, route: str | None = None, ngram: int = 8, min_run: int = 12,
               stats: dict | None = None) -> list:
    """Cards sharing a run of >= `min_run` consecutive English words with a source text (math ignored).

    Source files are read in name order, one directory at a time, so a run across a page break is found.
    Results contain card ids, run lengths and the card's own words; source text is never reported.
    """
    ids = {e["id"] for e in book.sequence(book.load_route(route))} if route else None
    table: dict = {}
    cardwords: dict = {}
    for c in book.cards.values():
        if (ids is not None and c.id not in ids) or c.kind not in ("A1", "A2", "A3", "A4", "A5", "A6", "B1", "B2", "B3", "B4", "B5", "C2"):
            continue
        w = words("\n".join(c.sections.values()))
        if len(w) < ngram:
            continue
        cardwords[c.id] = w
        for i in range(len(w) - ngram + 1):
            window = w[i:i + ngram]
            # strings of letters such as "a b a b a b" say nothing about copying
            if len(set(window)) < max(4, ngram // 2) or sum(len(x) for x in window) < 2.5 * ngram:
                continue
            table.setdefault(hash(" ".join(window)), []).append((c.id, i))
    hits: dict = {}
    for d in source_dirs:
        d = Path(d)
        files = sorted(d.rglob("*.txt")) if d.is_dir() else [d]
        window: deque = deque(maxlen=ngram)
        for f in files:
            if stats is not None:
                stats["files"] = stats.get("files", 0) + 1
            for word in words(f.read_text(encoding="utf-8", errors="ignore"), drop_math=False):
                if stats is not None:
                    stats["words"] = stats.get("words", 0) + 1
                window.append(word)
                if len(window) == ngram:
                    for cid, pos in table.get(hash(" ".join(window)), ()):
                        hits.setdefault(cid, set()).add(pos)
    report = []
    for cid, positions in hits.items():
        run = best = best_start = 0
        prev = None
        start = 0
        for p in sorted(positions):
            if prev is not None and p == prev + 1:
                run += 1
            else:
                run, start = 1, p
            prev = p
            if run > best:
                best, best_start = run, start
        words_in_run = best + ngram - 1
        if words_in_run >= min_run:
            report.append({"id": cid, "run_words": words_in_run, "matching_ngrams": len(positions),
                           "card_words": " ".join(cardwords[cid][best_start:best_start + min(words_in_run, 16)])})
    return sorted(report, key=lambda r: (-r["run_words"], r["id"]))
