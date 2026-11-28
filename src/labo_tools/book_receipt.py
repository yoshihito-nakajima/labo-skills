"""Accept a complete independent math pass on a frozen book case."""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

from .book import BookError, ID_RE, STATUS, book_lock, parse_card
from .book_review import _sha, atomic_text, write_card_review

SCOPE = "scope.json"
FREEZE = "freeze.json"
ASSIGNMENT = "review-assignment.json"
MANIFEST = "manifest.json"
RECEIPT = "review-receipt.json"
CLEAN_PASS = re.compile(r"RESULT: pass CHECKED: ([a-z0-9,-]+) FINDINGS: none")


def _object(path: Path) -> dict:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except ValueError as exc:
        raise BookError(f"invalid JSON in {path}") from exc
    if not isinstance(data, dict):
        raise BookError(f"expected an object in {path}")
    return data


def _inside(root: Path, relative: str) -> Path:
    path = Path(relative)
    if path.is_absolute() or ".." in path.parts:
        raise BookError(f"expected a relative case path: {relative}")
    target = root / path
    if target.resolve() != target:
        raise BookError(f"case paths must resolve without links: {relative}")
    return target


def inspect_case(case: Path, packet: str) -> tuple[dict, dict]:
    """Verify frozen file bytes and return the full scope and frozen pool cards."""
    case = case.resolve()
    if not re.fullmatch(r"packet-[0-9]+", packet):
        raise BookError("expected a packet name such as packet-01")
    manifest_path = f"input/{packet}/{MANIFEST}"
    freeze = _object(_inside(case, FREEZE))
    for required in (SCOPE, manifest_path, f"input/{packet}/cards.md"):
        if required not in freeze:
            raise BookError(f"freeze does not cover {required}")
    snapshots = {}
    for relative, digest in freeze.items():
        path = _inside(case, relative)
        if _sha(path) != digest:
            raise BookError(f"freeze mismatch: {relative}")
        if relative.startswith("canonical/pool/") and path.suffix == ".md":
            if path.name == "README.md":
                continue
            card = parse_card(path)
            if card.id in snapshots:
                raise BookError(f"duplicate frozen card: {card.id}")
            snapshots[card.id] = card

    scope = _object(case / SCOPE)
    manifest = _object(case / manifest_path)
    full = scope.get("full_cards")
    cards = manifest.get("cards")
    if (manifest.get("kind") != "math" or not isinstance(scope.get("route"), str)
            or scope["route"] != manifest.get("route") or not isinstance(full, dict) or not full
            or not isinstance(cards, list)):
        raise BookError("expected a math manifest with an explicit, nonempty full scope")
    manifest_ids = set()
    for entry in cards:
        cid = entry.get("id") if isinstance(entry, dict) else None
        if not isinstance(cid, str) or not ID_RE.fullmatch(cid) or cid in manifest_ids or cid not in full:
            raise BookError(f"invalid or out-of-scope manifest entry: {cid}")
        manifest_ids.add(cid)
        target = full[cid]
        card = snapshots.get(cid)
        if (card is None or card.kind not in ("A1", "A2", "A3", "A4", "A5", "A6") or card.legacy
                or not isinstance(target, dict)):
            raise BookError(f"no frozen full card for {cid}")
        relative = card.path.relative_to(case).as_posix()
        if (relative != f"canonical/{target.get('file')}" or card.fingerprint() != target.get("fp")
                or target["fp"] != entry.get("fp") or freeze[relative] != target.get("sha256")
                or target["sha256"] != entry.get("file_sha256")):
            raise BookError(f"manifest, scope and frozen file disagree for {cid}")
    if manifest_ids != set(full):
        raise BookError("manifest does not cover the whole full scope")
    context = manifest.get("context")
    if (not isinstance(context, list) or any(not isinstance(cid, str) or cid not in snapshots for cid in context)
            or manifest_ids.intersection(context)):
        raise BookError("manifest context must be frozen separately from full cards")
    return full, snapshots


def _json(data: dict) -> str:
    return json.dumps(data, ensure_ascii=False, indent=2) + "\n"


def prepare(case: Path, packet: str, report: str, producer: str | None, reviewer: str,
            next_request: Path | None) -> dict:
    case = case.resolve()
    if not producer or not reviewer or producer == reviewer or any(c.isspace() for c in producer + reviewer):
        raise BookError("use distinct, nonempty producer and reviewer run IDs from the host")
    if Path(report).parts[:1] != ("result",) or Path(report).suffix != ".md":
        raise BookError("report must be a Markdown path under result/")
    report_path = _inside(case, report)
    if report_path.exists():
        raise BookError("prepare the assignment before the review report exists")
    if next_request is not None and not next_request.is_file():
        raise BookError(f"next request not found: {next_request}")
    freeze_hash = _sha(_inside(case, FREEZE))
    inspect_case(case, packet)
    if _sha(case / FREEZE) != freeze_hash:
        raise BookError("freeze changed while preparing the assignment")
    continuation = {"path": str(next_request), "sha256": _sha(next_request)} if next_request else None
    data = {"version": 1, "packet": packet, "freeze": freeze_hash, "report": report,
            "producer": producer, "reviewer": reviewer, "next_request": continuation}
    path = _inside(case, ASSIGNMENT)
    try:
        with path.open("x", encoding="utf-8") as file:
            file.write(_json(data))
    except FileExistsError as exc:
        raise BookError("already assigned; use the existing assignment or a new case") from exc
    return {"action": "DISPATCH", "reviewer": reviewer, "assignment": str(path)}


def _matches(frozen, live) -> bool:
    def content_meta(card):
        return {key: value for key, value in card.meta.items() if key not in ("status", "reviews")}

    return frozen.body == live.body and content_meta(frozen) == content_meta(live)


def _live_cards(root: Path, case: Path, snapshots: dict) -> dict:
    live = {}
    for cid, frozen in snapshots.items():
        relative = frozen.path.relative_to(case / "canonical")
        path = _inside(root, relative.as_posix())
        if not path.is_file():
            raise BookError(f"live card missing: {cid}")
        card = parse_card(path)
        if not _matches(frozen, card):
            raise BookError(f"card or context changed since freeze: {cid}")
        live[cid] = card
    return live


def _checked_report(path: Path, reviewer: str, full: dict) -> str:
    report = path.read_bytes()
    lines = [line.strip() for line in report.decode("utf-8").splitlines() if line.strip()]
    if len(lines) < 3 or lines[-2] != f"REVIEWER: {reviewer}":
        raise BookError("review report is missing the assigned reviewer ID in its footer")
    match = CLEAN_PASS.fullmatch(lines[-1])
    if not match:
        raise BookError("send findings, partial checks and ambiguous reports to manual intake")
    checked = match[1].split(",")
    if len(checked) != len(full) or set(checked) != set(full):
        raise BookError("checked IDs must match the nonempty full scope exactly")
    return hashlib.sha256(report).hexdigest()


def _receive(root: Path, case: Path, reviewer: str, apply: bool) -> dict:
    assignment = _object(_inside(case, ASSIGNMENT))
    report_path = assignment.get("report")
    packet = assignment.get("packet")
    if (assignment.get("version") != 1 or not isinstance(packet, str)
            or not re.fullmatch(r"packet-[0-9]+", packet) or not isinstance(report_path, str)
            or Path(report_path).parts[:1] != ("result",)):
        raise BookError("invalid review assignment")
    if reviewer != assignment.get("reviewer") or reviewer == assignment.get("producer"):
        raise BookError("completed worker does not match the independent assignment")
    if _sha(_inside(case, FREEZE)) != assignment.get("freeze"):
        raise BookError("freeze differs from the dispatched version")
    full, snapshots = inspect_case(case, packet)
    if _sha(case / FREEZE) != assignment["freeze"]:
        raise BookError("freeze changed during review intake")
    report = _checked_report(_inside(case, report_path), reviewer, full)
    receipt_path = _inside(case, f"result/{RECEIPT}")
    continuation = assignment.get("next_request")
    next_request = None
    if continuation is not None:
        if (not isinstance(continuation, dict) or not isinstance(continuation.get("path"), str)
                or not isinstance(continuation.get("sha256"), str)):
            raise BookError("invalid next request in the assignment")
        path = Path(continuation["path"])
        if not path.is_file() or _sha(path) != continuation["sha256"]:
            raise BookError(f"next request changed since dispatch: {path}")
        next_request = str(path)
    receipt = {"version": 1, "assignment": _sha(case / ASSIGNMENT), "report": report,
               "checked": {cid: entry["fp"] for cid, entry in full.items()}, "next_request": next_request}
    if receipt_path.exists() and _object(receipt_path) != receipt:
        raise BookError("review differs from the recorded receipt")
    live = _live_cards(root, case, snapshots)
    for cid in full:
        if live[cid].meta.get("status") not in STATUS[1:]:
            raise BookError(f"full card is not ready for math review: {cid}")
    if apply:
        for cid, entry in full.items():
            write_card_review(live[cid], "math", "pass", report, entry["fp"], promote=True, retry_safe=True)
        if not receipt_path.exists():
            atomic_text(receipt_path, _json(receipt))
    return {"action": "NEXT" if apply and next_request else "RECORDED" if apply else "ELIGIBLE",
            "checked": len(full), "receipt": str(receipt_path) if apply else None, "next_request": next_request}


def receive(root: Path, case: Path, reviewer: str, *, apply: bool = False) -> dict:
    if apply:
        with book_lock(root):
            return _receive(root.resolve(), case.resolve(), reviewer, True)
    return _receive(root.resolve(), case.resolve(), reviewer, False)
