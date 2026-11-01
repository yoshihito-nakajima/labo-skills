"""Explicit, prefix-only reader sessions; not reader isolation or certification.

The coordinator may inspect the full source to bind its bytes. Only ``next``
returns source text, and only the cumulatively authorized prefix. Keep both
source and session paths out of an isolated reader's tools and initial brief.
"""

from __future__ import annotations

from contextlib import contextmanager
import hashlib
import json
import os
from pathlib import Path
import tempfile
import uuid

import yaml

from .evidence import EvidenceError, SHA256, _path, _relative, _workspace
from .plans import UniqueSafeLoader


MAX_SOURCE_BYTES = 16 * 1024 * 1024
MAX_SESSION_BYTES = 4 * 1024 * 1024
MODES = {"single-context", "independent"}


class ReadingError(ValueError):
    """Invalid, stale, or unsafe staged-reader operation."""


def _digest(value: object) -> str:
    return hashlib.sha256(json.dumps(
        value, sort_keys=True, ensure_ascii=False, separators=(",", ":"),
    ).encode("utf-8")).hexdigest()


def _mapping(value: object, keys: set[str]) -> dict:
    if not isinstance(value, dict) or set(value) != keys:
        raise ReadingError("invalid reading-session fields")
    return value


def _text(value: object) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ReadingError("reader and observation fields must be nonempty text")
    try:
        value.encode("utf-8")
    except UnicodeError as exc:
        raise ReadingError("reader and observation fields must be valid UTF-8 text") from exc
    return value


def _integer(value: object, *, minimum: int = 0) -> int:
    if type(value) is not int or value < minimum:
        raise ReadingError("invalid reading-session integer or line boundary")
    return value


def _sha(value: object) -> str:
    if not isinstance(value, str) or not SHA256.fullmatch(value):
        raise ReadingError("invalid reading-session digest")
    return value


def _paths(workspace: Path, session: str, *, missing: bool = False) -> tuple[Path, Path]:
    root = _workspace(workspace)
    return root, _path(root, session, missing=missing)


def _source(root: Path, source: str) -> tuple[bytes, dict]:
    path = _path(root, source)
    with path.open("rb") as stream:
        before = os.fstat(stream.fileno())
        raw = stream.read(MAX_SOURCE_BYTES + 1)
        after = os.fstat(stream.fileno())
    if len(raw) > MAX_SOURCE_BYTES:
        raise ReadingError("reading source exceeds 16 MiB")
    if (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns) != (
        after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns,
    ):
        raise ReadingError("reading source changed while being captured")
    try:
        raw.decode("utf-8")
    except UnicodeError as exc:
        raise ReadingError("reading source must be UTF-8 text") from exc
    if not raw:
        raise ReadingError("reading source must not be empty")
    return raw, {
        "path": _relative(source), "sha256": hashlib.sha256(raw).hexdigest(),
        "bytes": len(raw), "lines": len(raw.splitlines(keepends=True)),
        "device": before.st_dev, "inode": before.st_ino,
    }


def _validate(data: object, root: Path, session: str) -> tuple[dict, bytes]:
    data = _mapping(data, {"header", "header_sha256", "history_sha256", "events"})
    header = _mapping(data["header"], {
        "schema_version", "session_id", "workspace", "session", "source", "reader", "mode",
    })
    if type(header["schema_version"]) is not int or header["schema_version"] != 1:
        raise ReadingError("reading schema_version must be 1")
    if not isinstance(header["session_id"], str) or len(header["session_id"]) != 32:
        raise ReadingError("invalid reading-session identity")
    try:
        if uuid.UUID(hex=header["session_id"]).hex != header["session_id"]:
            raise ValueError
    except ValueError as exc:
        raise ReadingError("invalid reading-session identity") from exc
    if header["workspace"] != str(root) or header["session"] != _relative(session):
        raise ReadingError("reading session is bound to another workspace or session path")
    _text(header["reader"])
    if not isinstance(header["mode"], str) or header["mode"] not in MODES:
        raise ReadingError("reading mode must be single-context or independent")
    source = _mapping(header["source"], {"path", "sha256", "bytes", "lines", "device", "inode"})
    _relative(source["path"])
    _sha(source["sha256"])
    for key in ("bytes", "lines", "device", "inode"):
        _integer(source[key], minimum=1 if key in {"bytes", "lines"} else 0)
    if source["path"] == header["session"]:
        raise ReadingError("reading source and session must be different files")
    chain = _sha(data["header_sha256"])
    if chain != _digest(header):
        raise ReadingError("reading-session header digest mismatch")
    _sha(data["history_sha256"])
    if not isinstance(data["events"], list):
        raise ReadingError("reading-session events must be a list")
    raw, current = _source(root, source["path"])
    if current != source:
        raise ReadingError("reading source changed; start a new explicitly requested session")
    lines = raw.splitlines(keepends=True)
    through, pending = 0, False
    for event in data["events"]:
        if not isinstance(event, dict):
            raise ReadingError("invalid reading-session event")
        kind = event.get("kind")
        if kind == "exposure":
            _mapping(event, {"kind", "through_line", "prefix_sha256", "previous", "sha256"})
        elif kind in {"initial", "rescue"}:
            _mapping(event, {"kind", "through_line", "understanding", "confusion", "previous", "sha256"})
            _text(event["understanding"])
            _text(event["confusion"])
        else:
            raise ReadingError("invalid reading-session event kind")
        boundary = _integer(event["through_line"], minimum=1)
        _sha(event["previous"])
        _sha(event["sha256"])
        payload = {key: value for key, value in event.items() if key != "sha256"}
        if event["previous"] != chain or event["sha256"] != _digest(payload):
            raise ReadingError("reading-session history digest mismatch")
        chain = event["sha256"]
        if kind == "exposure":
            if pending or not through < boundary <= len(lines):
                raise ReadingError("invalid reading-session exposure order")
            prefix = b"".join(lines[:boundary])
            if _sha(event["prefix_sha256"]) != hashlib.sha256(prefix).hexdigest():
                raise ReadingError("reading-session prefix digest mismatch")
            through, pending = boundary, True
        elif kind == "initial":
            if not pending or boundary != through:
                raise ReadingError("invalid or replaced initial reading observation")
            pending = False
        elif not through or pending or boundary != through:
            raise ReadingError("rescue requires the current exposure's initial observation")
    if chain != data["history_sha256"]:
        raise ReadingError("reading-session history was truncated or altered")
    return data, raw


def _load(root: Path, session: str) -> tuple[dict, bytes, bytes]:
    path = _path(root, session)
    with path.open("rb") as stream:
        original = stream.read(MAX_SESSION_BYTES + 1)
    if len(original) > MAX_SESSION_BYTES:
        raise ReadingError("reading session exceeds 4 MiB")
    try:
        data = yaml.load(original.decode("utf-8"), Loader=UniqueSafeLoader)
    except (yaml.YAMLError, ValueError, UnicodeError, RecursionError) as exc:
        # Parser diagnostics may contain private text; never echo them.
        raise ReadingError("invalid reading-session JSON/YAML") from exc
    try:
        data, raw = _validate(data, root, session)
    except (TypeError, RecursionError) as exc:
        raise ReadingError("invalid reading-session metadata") from exc
    return data, raw, original


def _summary(data: dict) -> dict:
    header = data["header"]
    exposures = []
    for event in data["events"]:
        if event["kind"] == "exposure":
            exposures.append({"through_line": event["through_line"],
                              "initial_recorded": False, "rescue_count": 0})
        elif event["kind"] == "initial":
            exposures[-1]["initial_recorded"] = True
        else:
            exposures[-1]["rescue_count"] += 1
    return {
        "schema_version": 1, "session_id": header["session_id"],
        "reader": header["reader"], "mode": header["mode"],
        "through_line": exposures[-1]["through_line"] if exposures else 0,
        "awaiting_observation": bool(exposures and not exposures[-1]["initial_recorded"]),
        "exposures": exposures,
    }


def _append(data: dict, event: dict) -> None:
    event["previous"] = (data["events"][-1]["sha256"] if data["events"]
                         else data["header_sha256"])
    event["sha256"] = _digest(event)
    data["events"].append(event)
    data["history_sha256"] = event["sha256"]


@contextmanager
def _lock(root: Path, session: str):
    lock = _path(root, session + ".lock", missing=True)
    try:
        descriptor = os.open(lock, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError as exc:
        raise ReadingError("reading session is locked; inspect the lock rather than auto-removing it") from exc
    try:
        os.close(descriptor)
        yield
    finally:
        lock.unlink()


def _write(root: Path, session: str, data: dict, *, original: bytes | None = None) -> None:
    encoded = (json.dumps(data, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    if len(encoded) > MAX_SESSION_BYTES:
        raise ReadingError("reading session exceeds 4 MiB")
    path = _path(root, session, missing=original is None)
    descriptor, temporary = tempfile.mkstemp(prefix=".reading-", dir=path.parent)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(encoded)
            stream.flush()
            os.fsync(stream.fileno())
        # Recheck the source immediately before publishing a new state.
        _, current = _source(root, data["header"]["source"]["path"])
        if current != data["header"]["source"]:
            raise ReadingError("reading source changed; session was not updated")
        path = _path(root, session, missing=original is None)
        if original is None:
            # Atomic publication without ever overwriting an existing target.
            os.link(temporary, path)
        else:
            if path.read_bytes() != original:
                raise ReadingError("reading session changed concurrently; session was not updated")
            os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


@contextmanager
def _errors():
    try:
        yield
    except EvidenceError as exc:
        # A malformed private source path can itself contain withheld text.
        raise ReadingError(
            "unsafe or missing reading path: use normalized workspace-relative POSIX paths, "
            "existing parents, and no symlinks or policy-checkout targets"
        ) from exc
    except OSError as exc:
        # Do not emit absolute private paths or file contents in OS diagnostics.
        raise ReadingError("reading-session filesystem operation failed; check paths, permissions, and locks") from exc


def start_reading(workspace: Path, source: str, session: str, reader: str, *,
                  mode: str = "single-context") -> dict:
    """Explicitly create one private session, exposing no source text yet."""
    with _errors():
        root, path = _paths(workspace, session, missing=True)
        _text(reader)
        if not isinstance(mode, str) or mode not in MODES:
            raise ReadingError("reading mode must be single-context or independent")
        if path.exists():
            raise ReadingError("reading session already exists; refusing to overwrite")
        if _relative(source) == _relative(session):
            raise ReadingError("reading source and session must be different files")
        with _lock(root, session):
            _, identity = _source(root, source)
            header = {
                "schema_version": 1, "session_id": uuid.uuid4().hex,
                "workspace": str(root), "session": _relative(session),
                "source": identity, "reader": reader, "mode": mode,
            }
            digest = _digest(header)
            data = {"header": header, "header_sha256": digest,
                    "history_sha256": digest, "events": []}
            _write(root, session, data)
        return _summary(data)


def next_reading(workspace: Path, session: str, through_line: int) -> dict:
    """Record and return a strictly growing cumulative prefix, never a suffix."""
    with _errors():
        root, _ = _paths(workspace, session)
        with _lock(root, session):
            data, raw, original = _load(root, session)
            summary = _summary(data)
            if summary["awaiting_observation"]:
                raise ReadingError("record initial understanding and first confusion before another exposure")
            boundary = _integer(through_line, minimum=1)
            if not summary["through_line"] < boundary <= data["header"]["source"]["lines"]:
                raise ReadingError("through-line must strictly increase within the captured source")
            prefix = b"".join(raw.splitlines(keepends=True)[:boundary])
            digest = hashlib.sha256(prefix).hexdigest()
            _append(data, {"kind": "exposure", "through_line": boundary, "prefix_sha256": digest})
            _write(root, session, data, original=original)
        result = _summary(data)
        result.update({"text": prefix.decode("utf-8"), "prefix_sha256": digest})
        return result


def observe_reading(workspace: Path, session: str, understanding: str, confusion: str, *,
                    rescue: bool = False) -> dict:
    """Append an immutable initial observation, or a separately labeled rescue."""
    with _errors():
        root, _ = _paths(workspace, session)
        _text(understanding)
        _text(confusion)
        if type(rescue) is not bool:
            raise ReadingError("rescue must be a boolean")
        with _lock(root, session):
            data, _, original = _load(root, session)
            summary = _summary(data)
            if not summary["through_line"]:
                raise ReadingError("expose a prefix before recording an observation")
            if rescue and summary["awaiting_observation"]:
                raise ReadingError("record the initial observation before any rescue")
            if not rescue and not summary["awaiting_observation"]:
                raise ReadingError("initial observation already recorded; append a rescue instead")
            _append(data, {"kind": "rescue" if rescue else "initial",
                           "through_line": summary["through_line"],
                           "understanding": understanding, "confusion": confusion})
            _write(root, session, data, original=original)
        return _summary(data)


def reading_status(workspace: Path, session: str) -> dict:
    """Read-only validation and metadata; no source or observation prose."""
    with _errors():
        root, _ = _paths(workspace, session)
        data, _, _ = _load(root, session)
        return _summary(data)
