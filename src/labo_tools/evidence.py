"""Optional, source-local evidence records; never mathematical certification."""

from __future__ import annotations

from datetime import date
import hashlib
import json
import os
from pathlib import Path, PurePosixPath, PureWindowsPath
import re

import yaml

from .plans import SLUG, UniqueSafeLoader


CHECKOUT = Path(__file__).resolve().parents[2]
SKILL = CHECKOUT / "skills" / "research-management"
PROTOCOL = "skills/research-management/references/evidence.md"
STANDARDS = "skills/paper-referee/references/standards.md"
STATUSES = frozenset({
    "open", "unverified", "proved/agent", "proved/literature",
    "proved/owner-checked", "verified-formally", "verified-computationally",
    "disputed", "refuted",
})
PROVED = frozenset({
    "proved/agent", "proved/literature", "proved/owner-checked", "verified-formally",
})
KINDS = ("proof", "writing", "formal", "owner")
IGNORED_DIRS = frozenset({
    ".git", ".lake", ".temp", ".venv", ".uv-cache", "__pycache__",
    "build", "dist", "output",
})
SHA256 = re.compile(r"[0-9a-f]{64}\Z")
MAX_RECORD_BYTES = 2 * 1024 * 1024


class EvidenceError(ValueError):
    """An invalid, ambiguous, or unsafe evidence operation."""


def _workspace(workspace: Path) -> Path:
    root = workspace.resolve()
    if not root.is_dir():
        raise EvidenceError("workspace must be an existing directory")
    if root.is_relative_to(CHECKOUT):
        raise EvidenceError("private evidence must be outside the policy checkout")
    return root


def _relative(value: object) -> str:
    if not isinstance(value, str) or not value or "\\" in value or "\0" in value:
        raise EvidenceError("input paths must be nonempty workspace-relative POSIX paths")
    path = PurePosixPath(value)
    if path.is_absolute() or PureWindowsPath(value).drive or path.as_posix() != value or any(
        part in {".", "..", ""} for part in path.parts
    ) or value == ".":
        raise EvidenceError(f"input path must be normalized and relative: {value}")
    return value


def _path(root: Path, value: object, *, directory: bool = False,
          missing: bool = False, policy: bool = False) -> Path:
    relative = _relative(value)
    path = root / relative
    current = root
    for part in PurePosixPath(relative).parts:
        current /= part
        if current.is_symlink():
            raise EvidenceError(f"symlinked input is not supported: {relative}")
    resolved = path.resolve()
    if not resolved.is_relative_to(root.resolve()):
        raise EvidenceError(f"input path must stay inside its selected root: {relative}")
    if not policy and resolved.is_relative_to(CHECKOUT):
        raise EvidenceError("private evidence paths must not enter the policy checkout")
    if missing and not path.exists():
        if not path.parent.is_dir():
            raise EvidenceError(f"parent directory must already exist: {relative}")
        return path
    if not (path.is_dir() if directory else path.is_file()):
        raise EvidenceError(f"missing or non-{'directory' if directory else 'file'} input: {relative}")
    return path


def _digest_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _digest(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def _mapping(value: object, name: str, required: set[str],
             optional: set[str] | None = None) -> dict:
    if not isinstance(value, dict) or any(not isinstance(key, str) for key in value):
        raise EvidenceError(f"{name} must be a mapping with string keys")
    keys = set(value)
    if not required <= keys:
        raise EvidenceError(f"{name} missing fields: {', '.join(sorted(required - keys))}")
    unknown = keys - required - (optional or set())
    if unknown:
        raise EvidenceError(f"{name} unknown fields: {', '.join(sorted(unknown))}")
    return value


def _text(value: object, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise EvidenceError(f"{name} must be a nonempty string")
    return value


def _strings(value: object, name: str) -> list[str]:
    if not isinstance(value, list) or any(not isinstance(item, str) or not item for item in value):
        raise EvidenceError(f"{name} must be a list of nonempty strings")
    if len(value) != len(set(value)):
        raise EvidenceError(f"{name} must not contain duplicates")
    return value


def _load(path: Path) -> dict:
    if path.stat().st_size > MAX_RECORD_BYTES:
        raise EvidenceError("evidence YAML exceeds 2 MiB")
    try:
        data = yaml.load(path.read_text(encoding="utf-8"), Loader=UniqueSafeLoader)
    except (yaml.YAMLError, ValueError, RecursionError) as exc:
        # SafeLoader can raise ValueError for an invalid implicit timestamp,
        # independently of YAML syntax or the duplicate-key constructor.
        raise EvidenceError(f"invalid evidence YAML: {exc}") from exc
    if not isinstance(data, dict):
        raise EvidenceError("evidence YAML must be a mapping")
    if type(data.get("schema_version")) is not int or data["schema_version"] != 1:
        raise EvidenceError("schema_version must be 1")
    return data


def _files(root: Path, names: list[str], *, policy: bool = False) -> dict[str, str]:
    return {name: _digest_file(_path(root, name, policy=policy)) for name in sorted(set(names))}


def _tree(root: Path, name: str, *, lean_only: bool = False) -> dict[str, str]:
    directory = _path(root, name, directory=True)
    result = {}

    def walk_error(error: OSError) -> None:
        raise EvidenceError(f"cannot read selected tree: {name}") from error

    for current, directories, filenames in os.walk(directory, followlinks=False, onerror=walk_error):
        directories[:] = sorted(item for item in directories if item not in IGNORED_DIRS)
        for child in directories:
            _path(root, (Path(current) / child).relative_to(root).as_posix(), directory=True)
        for child in sorted(filenames):
            if child == ".git":
                continue
            relative = (Path(current) / child).relative_to(root).as_posix()
            path = _path(root, relative)
            if not lean_only or path.suffix == ".lean":
                result[relative] = _digest_file(path)
    return result


def init_catalog(workspace: Path, catalog: str, *, dry_run: bool = False) -> list[str]:
    root = _workspace(workspace)
    path = _path(root, catalog, missing=True)
    if path.exists():
        raise EvidenceError(f"{catalog} already exists; inspect and use it instead")
    template = (SKILL / "assets" / "claims.yaml").read_bytes()
    if not dry_run:
        with path.open("xb") as stream:
            stream.write(template)
    return [f"create {catalog}"]


class Catalog:
    """One explicitly selected catalog; never a mandatory workspace-wide graph."""

    def __init__(self, workspace: Path, catalog: str):
        self.root = _workspace(workspace)
        self.path = _relative(catalog)
        data = _load(_path(self.root, catalog))
        _mapping(data, "catalog", {"schema_version", "claims"})
        if not isinstance(data["claims"], dict):
            raise EvidenceError("claims must be a mapping of stable IDs")
        self.claims = data["claims"]
        self.inputs: dict[str, dict] = {}
        for key, value in self.claims.items():
            if not isinstance(key, str) or not SLUG.fullmatch(key):
                raise EvidenceError("claim IDs must use lowercase kebab-case")
            claim = _mapping(value, f"claim {key}", {"statement", "status"}, {
                "evidence", "dependencies", "formal", "owner_check", "obstruction", "next_check",
            })
            _text(claim["statement"], f"{key}.statement")
            if not isinstance(claim["status"], str) or claim["status"] not in STATUSES:
                raise EvidenceError(f"{key}: unknown evidence status")
            for name in ("evidence", "dependencies"):
                _strings(claim.get(name, []), f"{key}.{name}")
            for name in ("obstruction", "next_check"):
                if name in claim:
                    _text(claim[name], f"{key}.{name}")

    def closure(self, key: str) -> list[str]:
        active: list[str] = []
        visited: set[str] = set()
        stack = [(key, False)]
        while stack:
            current, leaving = stack.pop()
            if leaving:
                active.pop()
                visited.add(current)
                continue
            if current in active:
                raise EvidenceError(f"claim dependency cycle: {' -> '.join([*active, current])}")
            if current in visited:
                continue
            if current not in self.claims:
                raise EvidenceError(f"unknown claim dependency or target: {current}")
            active.append(current)
            stack.append((current, True))
            stack.extend((dep, False) for dep in reversed(self.claims[current].get("dependencies", [])))
        return sorted(visited)

    def _formal(self, key: str, formal: object, status: str) -> dict:
        data = _mapping(formal, f"{key}.formal", {
            "project", "source", "declaration", "kernel", "alignment",
        })
        project = _path(self.root, data["project"], directory=True)
        source = _path(self.root, data["source"])
        if not source.is_relative_to(project) or source.suffix != ".lean":
            raise EvidenceError(f"{key}: formal source must be a .lean file inside its project")
        _text(data["declaration"], f"{key}.formal.declaration")
        if any(char.isspace() for char in data["declaration"]):
            raise EvidenceError(f"{key}: formal declaration must be one fully qualified name")
        reports = {}
        for kind in ("kernel", "alignment"):
            record = _mapping(data[kind], f"{key}.formal.{kind}", {"verdict", "report"})
            if record["verdict"] not in ("pending", "pass", "fail"):
                raise EvidenceError(f"{key}: {kind} verdict must be pending, pass, or fail")
            report = record["report"]
            if report is not None:
                reports[_relative(report)] = _digest_file(_path(self.root, report))
            if record["verdict"] in ("pass", "fail") and report is None:
                raise EvidenceError(f"{key}: a completed {kind} assessment requires its actual report")
            if status == "verified-formally" and record["verdict"] != "pass":
                raise EvidenceError(f"{key}: verified-formally requires passing kernel and alignment records")
        environment = [project / "lean-toolchain", project / "lake-manifest.json"]
        lakefiles = [project / name for name in ("lakefile.toml", "lakefile.lean")
                     if (project / name).exists()]
        if not lakefiles:
            raise EvidenceError(f"{key}: formal project requires a Lake file")
        environment.extend(lakefiles)
        file_inputs = _tree(self.root, data["project"], lean_only=True)
        # An explicitly selected production source must never disappear behind
        # the general project's cache/directory exclusions.
        file_inputs.update(_files(self.root, [path.relative_to(self.root).as_posix()
                                             for path in [source, *environment]]))
        file_inputs.update(reports)
        return {"mapping": data, "files": file_inputs}

    def claim_inputs(self, key: str) -> dict:
        if key in self.inputs:
            return self.inputs[key]
        claim = self.claims[key]
        status = claim["status"]
        evidence = claim.get("evidence", [])
        if status in PROVED | {"verified-computationally", "refuted"} and not evidence:
            raise EvidenceError(f"{key}: checked or refuted claims require actual evidence files")
        dependencies = claim.get("dependencies", [])
        if status in PROVED:
            for dep in dependencies:
                if self.claims[dep]["status"] not in PROVED:
                    raise EvidenceError(f"{key}: proved claim depends on an unresolved or non-proved claim: {dep}")
        result = {
            "statement": claim["statement"], "status": status,
            "dependencies": sorted(dependencies), "evidence": _files(self.root, evidence),
        }
        if "owner_check" in claim:
            result["owner_check"] = _files(self.root, [_relative(claim["owner_check"])])
        elif status == "proved/owner-checked":
            raise EvidenceError(f"{key}: owner-checked status requires the actual owner_check record")
        if "formal" in claim:
            result["formal"] = self._formal(key, claim["formal"], status)
        elif status == "verified-formally":
            raise EvidenceError(f"{key}: verified-formally requires an exact formal mapping")
        self.inputs[key] = result
        return result

    def fingerprints(self, keys: list[str]) -> dict[str, str]:
        result = {}
        for key in sorted(set(keys)):
            closure = self.closure(key)
            result[key] = _digest({dep: self.claim_inputs(dep) for dep in closure})
        return result


def _policy_paths(kind: str) -> set[str]:
    return {PROTOCOL, STANDARDS} if kind in {"proof", "writing"} else {PROTOCOL}


def snapshot(workspace: Path, *, kind: str, catalog: str | None = None,
             claim_ids: list[str] | None = None, files: list[str] | None = None,
             trees: list[str] | None = None, policy_files: list[str] | None = None) -> dict:
    root = _workspace(workspace)
    if kind not in KINDS:
        raise EvidenceError("unknown review kind")
    keys = claim_ids or []
    if catalog is not None and not keys:
        raise EvidenceError("select actual reviewed claims with --claim; no implicit whole-catalog review")
    if keys and catalog is None:
        raise EvidenceError("--claim requires --catalog")
    if kind != "writing" and not keys:
        raise EvidenceError(f"{kind} review requires --catalog and at least one --claim")
    if not keys and not files and not trees:
        raise EvidenceError("a snapshot needs explicitly selected claims, files, or trees")
    fingerprints = {}
    if catalog is not None:
        selected = Catalog(root, catalog)
        fingerprints = selected.fingerprints(keys)
        if kind == "formal" and any("formal" not in selected.claims[key] for key in keys):
            raise EvidenceError("a formal review requires an exact formal mapping for every selected claim")
    return {
        "schema_version": 1,
        "kind": kind,
        "verdict": "pending",
        "reviewer": None,
        "mode": "owner" if kind == "owner" else "single-context",
        "reviewed_at": None,
        "report": None,
        "report_sha256": None,
        "catalog": catalog,
        "claims": fingerprints,
        "files": _files(root, files or []),
        "trees": {name: _tree(root, name) for name in sorted(set(trees or []))},
        "policy_inputs": _files(CHECKOUT, sorted(_policy_paths(kind) | set(policy_files or [])),
                               policy=True),
    }


def _fingerprints(value: object, name: str, *, paths: bool = True) -> dict:
    if not isinstance(value, dict):
        raise EvidenceError(f"{name} must be a fingerprint mapping")
    for key, digest in value.items():
        if paths:
            _relative(key)
        elif not isinstance(key, str) or not SLUG.fullmatch(key):
            raise EvidenceError("snapshot claim IDs must use lowercase kebab-case")
        if not isinstance(digest, str) or not SHA256.fullmatch(digest):
            raise EvidenceError(f"{name}: fingerprint must be lowercase SHA-256")
    return value


def _record_shape(record: dict) -> None:
    _mapping(record, "review record", {
        "schema_version", "kind", "verdict", "reviewer", "mode", "reviewed_at",
        "report", "report_sha256", "catalog", "claims", "files", "trees", "policy_inputs",
    })
    if record["kind"] not in KINDS:
        raise EvidenceError("unknown review kind")
    if record["verdict"] not in ("pending", "pass", "fail"):
        raise EvidenceError("review verdict must be pending, pass, or fail")
    modes = ("owner",) if record["kind"] == "owner" else ("single-context", "independent")
    if record["mode"] not in modes:
        raise EvidenceError("review mode does not match the review kind")
    if record["catalog"] is not None:
        _relative(record["catalog"])
    _fingerprints(record["claims"], "claims", paths=False)
    _fingerprints(record["files"], "files")
    _fingerprints(record["policy_inputs"], "policy_inputs")
    if not _policy_paths(record["kind"]) <= set(record["policy_inputs"]):
        raise EvidenceError("review record is missing its required policy inputs")
    if not isinstance(record["trees"], dict):
        raise EvidenceError("trees must be a mapping")
    for name, values in record["trees"].items():
        _relative(name)
        _fingerprints(values, f"tree {name}")
        if any(not PurePosixPath(key).is_relative_to(PurePosixPath(name)) for key in values):
            raise EvidenceError("tree fingerprint contains a file outside its selected tree")
    if record["catalog"] is None and record["claims"]:
        raise EvidenceError("claim fingerprints require a catalog")
    if record["catalog"] is not None and not record["claims"]:
        raise EvidenceError("catalog reviews require explicit claim fingerprints")
    if record["kind"] != "writing" and not record["claims"]:
        raise EvidenceError("this review kind requires explicit claim fingerprints")
    if not (record["claims"] or record["files"] or record["trees"]):
        raise EvidenceError("review record has no selected inputs")
    if record["report"] is not None:
        _relative(record["report"])
    if record["verdict"] != "pending":
        _text(record["reviewer"], "reviewer")
        value = str(record["reviewed_at"])
        try:
            if date.fromisoformat(value).isoformat() != value:
                raise ValueError
        except ValueError as exc:
            raise EvidenceError("reviewed_at must be an actual ISO date YYYY-MM-DD") from exc
        _relative(record["report"])
        if not isinstance(record["report_sha256"], str) or not SHA256.fullmatch(record["report_sha256"]):
            raise EvidenceError("a completed review requires the actual report_sha256")


def _issue(severity: str, code: str, path: str, message: str) -> dict:
    return {"severity": severity, "code": code, "path": path, "message": message}


def _check_record(root: Path, name: str) -> tuple[str, list[dict]]:
    try:
        record_path = _path(root, name)
        record = _load(record_path)
        _record_shape(record)
        if record["report"] == name:
            raise EvidenceError("a review snapshot cannot serve as its own substantive report")
    except (EvidenceError, OSError, UnicodeError) as exc:
        return "invalid", [_issue("error", "invalid-record", name, str(exc))]

    issues = []
    stale = False
    try:
        current = snapshot(
            root, kind=record["kind"], catalog=record["catalog"],
            claim_ids=list(record["claims"]), files=list(record["files"]),
            trees=list(record["trees"]), policy_files=list(record["policy_inputs"]),
        )
        for field in ("claims", "files", "trees", "policy_inputs"):
            if current[field] != record[field]:
                stale = True
                issues.append(_issue("warning", "stale-inputs", name, f"changed review inputs: {field}"))
    except (EvidenceError, OSError, UnicodeError) as exc:
        stale = True
        issues.append(_issue("warning", "stale-inputs", name,
                             f"recorded inputs cannot be reproduced: {exc}"))
    if record["verdict"] != "pending":
        try:
            if _digest_file(_path(root, record["report"])) != record["report_sha256"]:
                stale = True
                issues.append(_issue("warning", "stale-report", name,
                                     "the substantive review report has changed"))
        except (EvidenceError, OSError, UnicodeError) as exc:
            stale = True
            issues.append(_issue("warning", "stale-report", name, str(exc)))
    if record["verdict"] == "fail":
        issues.append(_issue("error", "failed-review", name, "the recorded review did not pass"))
        return "failed", issues
    if record["verdict"] == "pending":
        issues.append(_issue("warning", "pending-review", name, "the review has not been completed"))
    state = "stale" if stale else ("pending" if record["verdict"] == "pending" else "current")
    return state, issues


def check_evidence(workspace: Path, *, catalog: str | None = None,
                   records: list[str] | None = None) -> dict:
    root = _workspace(workspace)
    if catalog is None and not records:
        raise EvidenceError("select a catalog or at least one review record")
    issues = []
    checked = []
    count = 0
    if catalog is not None:
        try:
            selected = Catalog(root, catalog)
            count = len(selected.claims)
            selected.fingerprints(list(selected.claims))
        except (EvidenceError, OSError, UnicodeError) as exc:
            issues.append(_issue("error", "invalid-catalog", catalog, str(exc)))
    for name in records or []:
        state, problems = _check_record(root, name)
        checked.append({"path": name, "state": state})
        issues.extend(problems)
    status = ("error" if any(item["severity"] == "error" for item in issues)
              else "warning" if issues else "ok")
    return {"schema_version": 1, "status": status, "claim_count": count,
            "records": checked, "issues": issues}
