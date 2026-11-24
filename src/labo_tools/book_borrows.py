"""Version declared dependencies for cards borrowed by another book."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
import hashlib
import json
import re


OWNER_ID = re.compile(r"[a-z0-9][a-z0-9-]*\Z")
VERSION = re.compile(r"sha256:[0-9a-f]{64}\Z")


def declarations(cards):
    for card in cards:
        if card.kind == "B5":
            for entry in card.meta.get("borrows") or []:
                yield card.id, entry


@dataclass
class RouteEvidence:
    positions: dict
    proofs: dict
    borrows: dict


class BorrowSnapshots:
    def __init__(self, book):
        self.book = book
        self.routes = {}
        self.versions = {}

    def _evidence(self, owner):
        if owner not in self.routes:
            sequence = self.book.sequence(self.book.load_route(owner))
            positions, proofs, borrows = {}, defaultdict(set), defaultdict(list)
            for i, entry in enumerate(sequence):
                card = self.book.cards.get(entry["id"])
                if card is None:
                    continue
                positions.setdefault(card.id, i)
                if card.kind == "A3":
                    proofs[card.meta.get("proves")].add(card.id)
            for _, entry in declarations(self.book.cards[cid] for cid in positions):
                if isinstance(entry, dict) and isinstance(entry.get("card"), str):
                    borrows[entry["card"]].append(entry)
            self.routes[owner] = RouteEvidence(positions, proofs, borrows)
        return self.routes[owner]

    def version(self, owner, cid):
        if not isinstance(owner, str) or not OWNER_ID.fullmatch(owner):
            raise ValueError(f"invalid owning route {owner!r}")
        if cid not in self._evidence(owner).positions:
            raise ValueError(f"{cid} is absent from owning route {owner}")
        return self._version(owner, cid, ())

    def _version(self, owner, cid, trail):
        key = (owner, cid)
        if key in trail:
            cycle = " -> ".join(f"{r}/{c}" for r, c in (*trail, key))
            raise ValueError(f"borrowed dependency cycle: {cycle}")
        if key in self.versions:
            return self.versions[key]
        route = self._evidence(owner)
        card = self.book.cards[cid]
        if not card.template or not card.template.dep:
            raise ValueError(f"{owner}/{cid} is not a mathematical prerequisite card")
        proofs = route.proofs.get(cid, set())
        if len(proofs) > 1 or (card.kind == "A2" and not proofs):
            raise ValueError(f"{owner}/{cid} needs one selected proof, found {len(proofs)}")
        parts = [card, *(self.book.cards[pid] for pid in proofs)]
        payload = []
        for part in parts:
            deps = sorted(set(part.requires) | set(part.meta.get("conventions") or []))
            pins = []
            for dep in deps:
                if dep in route.positions:
                    if route.positions[dep] >= route.positions[part.id]:
                        raise ValueError(f"{owner}/{part.id} uses {dep} before it is established")
                    pin = self._version(owner, dep, (*trail, key))
                else:
                    pin = self._upstream(owner, dep, route.borrows.get(dep, ()), (*trail, key))
                pins.append((dep, pin))
            payload.append((part.id, part.fingerprint(full=True), pins))
        encoded = json.dumps([owner, payload], ensure_ascii=False, separators=(",", ":")).encode()
        self.versions[key] = "sha256:" + hashlib.sha256(encoded).hexdigest()
        return self.versions[key]

    def _upstream(self, owner, cid, entries, trail):
        pins = set()
        for entry in entries:
            upstream, recorded = entry.get("owner"), entry.get("version")
            if not (isinstance(upstream, str) and OWNER_ID.fullmatch(upstream)
                    and isinstance(recorded, str) and VERSION.fullmatch(recorded)):
                raise ValueError(f"{owner}/{cid} has an invalid upstream borrow")
            pins.add((upstream, recorded))
        if len(pins) != 1:
            raise ValueError(f"{owner}/{cid} needs one exact upstream borrow")
        upstream, recorded = next(iter(pins))
        if cid not in self._evidence(upstream).positions:
            raise ValueError(f"{cid} is absent from upstream owning route {upstream}")
        version = self._version(upstream, cid, trail)
        if recorded != version:
            raise ValueError(f"{owner}'s upstream borrow {upstream}/{cid} is stale")
        return version


def pin_issues(book, slug, cards):
    """Validate the current route's declared borrowed versions; do not rewrite pins."""
    snapshots = BorrowSnapshots(book)
    seen = {}
    for entrance, entry in declarations(cards.values()):
        if not isinstance(entry, dict):
            yield "BORROW-INVALID", entrance, "borrows entries must be mappings"
            continue
        cid, owner, recorded, why = (entry.get(key) for key in ("card", "owner", "version", "why"))
        if not all(isinstance(x, str) and x.strip() for x in (cid, owner, recorded, why)):
            yield "BORROW-INVALID", entrance, "each borrow needs card, owner, version and why"
            continue
        if not OWNER_ID.fullmatch(owner) or not VERSION.fullmatch(recorded) or owner == slug:
            yield "BORROW-INVALID", entrance, f"{cid}: expected a sha256 version and another owning route ID"
            continue
        pin = (owner, recorded)
        prior = seen.setdefault(cid, pin)
        if prior != pin:
            yield "BORROW-INVALID", entrance, f"{cid}: conflicting owner or version"
            continue
        if cid in cards:
            # A joint route may already place the earlier book's card.
            continue
        try:
            current = snapshots.version(owner, cid)
        except ValueError as exc:
            yield "BORROW-INVALID", entrance, str(exc)
        else:
            if recorded != current:
                yield "BORROW-STALE", entrance, f"{owner}/{cid} changed; reread its proof, premises and uses"
