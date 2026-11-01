"""Read-only inventory of one explicitly selected program's evidence records."""

from __future__ import annotations

from collections import Counter
import os
from pathlib import Path, PurePosixPath

from .evidence import (
    Catalog, EvidenceError, IGNORED_DIRS, PROVED, _check_record, _issue,
    _load, _path, _record_shape, _relative, _workspace,
)
from .plans import SLUG


MAX_RECORDS = 500
MAX_REVIEW_DEPTH = 32
PROOF_REVIEW_KINDS = frozenset({"proof", "formal", "owner"})


def _within_program(path: str, program: str) -> str:
    path = _relative(path)
    if not PurePosixPath(path).is_relative_to(PurePosixPath(program)):
        raise EvidenceError("catalog and discovery directory must stay inside the selected research program")
    return path


def _discover(root: Path, name: str) -> tuple[list[str], list[dict]]:
    """Only YAML records in the selected reviews directory, never a global scan."""
    directory = _path(root, name, directory=True)
    paths: list[str] = []
    issues: list[dict] = []

    def walk_error(error: OSError) -> None:
        issues.append(_issue("error", "unreadable-reviews", name, str(error)))

    for current, directories, filenames in os.walk(directory, followlinks=False, onerror=walk_error):
        current_path = Path(current)
        depth = len(current_path.relative_to(directory).parts)
        retained = []
        for child in sorted(directories):
            if child in IGNORED_DIRS:
                continue
            relative = (current_path / child).relative_to(root).as_posix()
            try:
                _path(root, relative, directory=True)
                if depth >= MAX_REVIEW_DEPTH:
                    raise EvidenceError("review discovery depth limit reached")
                retained.append(child)
            except (EvidenceError, OSError) as exc:
                issues.append(_issue("error", "unsafe-review-directory", relative, str(exc)))
        directories[:] = retained
        for filename in sorted(filenames):
            if Path(filename).suffix.lower() not in {".yaml", ".yml"}:
                continue
            relative = (current_path / filename).relative_to(root).as_posix()
            if len(paths) >= MAX_RECORDS:
                issues.append(_issue("error", "record-limit", name,
                                     f"more than {MAX_RECORDS} records; select a smaller directory or explicit records"))
                return paths, issues
            paths.append(relative)
    return sorted(paths), issues


def evidence_status(workspace: Path, *, research: str, catalog: str | None = None,
                    reviews: str | None = None, records: list[str] | None = None) -> dict:
    """Inventory recorded claims and reviews, without approving or rewriting them."""
    root = _workspace(workspace)
    if not isinstance(research, str) or not SLUG.fullmatch(research):
        raise EvidenceError("research must be a lowercase kebab-case program name")
    program = f"research/{research}"
    _path(root, program, directory=True)
    if reviews is not None and records:
        raise EvidenceError("choose a discovery directory or explicit records, not both")

    catalog_name = _within_program(catalog or f"{program}/claims.yaml", program)
    catalog_path = root / catalog_name
    catalog_present = catalog_path.exists() or catalog_path.is_symlink()
    issues: list[dict] = []
    claims: list[dict] = []
    selected = None
    if catalog_present or catalog is not None:
        try:
            selected = Catalog(root, catalog_name)
        except (EvidenceError, OSError, UnicodeError) as exc:
            issues.append(_issue("error", "invalid-catalog", catalog_name, str(exc)))
    if selected is not None:
        for key, claim in sorted(selected.claims.items()):
            row = {
                "id": key, "statement": claim["statement"], "evidence_status": claim["status"],
                "structure": "valid", "evidence_files": list(claim.get("evidence", [])),
                "dependencies": list(claim.get("dependencies", [])),
                "formal": None, "reviews": [], "current_reviews_by_kind": {}, "attention": [],
            }
            try:
                selected.fingerprints([key])
            except (EvidenceError, OSError, UnicodeError) as exc:
                row["structure"] = "invalid"
                row["attention"].append("invalid-evidence")
                issues.append(_issue("error", "invalid-claim", f"{catalog_name}#{key}", str(exc)))
            formal = claim.get("formal")
            if isinstance(formal, dict):
                # Malformed mappings are retained as invalid rows, not a crash or an inferred pass.
                row["formal"] = {
                    "declaration": formal.get("declaration"),
                    "kernel": formal.get("kernel", {}).get("verdict")
                    if isinstance(formal.get("kernel"), dict) else None,
                    "alignment": formal.get("alignment", {}).get("verdict")
                    if isinstance(formal.get("alignment"), dict) else None,
                }
                for kind in ("kernel", "alignment"):
                    if row["formal"][kind] != "pass":
                        row["attention"].append(f"formal-{kind}-not-passing")
            if claim["status"] in {"open", "unverified", "disputed", "refuted"}:
                row["attention"].append(f"claim-{claim['status']}")
            claims.append(row)

    discovery_dir = None
    if records:
        names = sorted(set(_relative(name) for name in records))
        if len(names) > MAX_RECORDS:
            raise EvidenceError(f"select at most {MAX_RECORDS} records")
    else:
        discovery_dir = _within_program(reviews or f"{program}/reviews", program)
        directory = root / discovery_dir
        if directory.exists() or directory.is_symlink() or reviews is not None:
            try:
                names, problems = _discover(root, discovery_dir)
                issues.extend(problems)
            except (EvidenceError, OSError, UnicodeError) as exc:
                names = []
                issues.append(_issue("error", "invalid-review-directory", discovery_dir, str(exc)))
        else:
            names = []

    rows_by_id = {row["id"]: row for row in claims}
    checked = []
    for name in names:
        row = {"path": name, "state": "invalid", "kind": None, "claims": [],
               "reviewed_at": None, "verdict": None}
        try:
            record = _load(_path(root, name))
            _record_shape(record)
            row.update({"kind": record["kind"], "claims": sorted(record["claims"]),
                        "reviewed_at": str(record["reviewed_at"]) if record["reviewed_at"] else None,
                        "verdict": record["verdict"]})
            if record["catalog"] is not None and record["catalog"] != catalog_name:
                row["state"] = "out-of-scope"
                issues.append(_issue("warning", "foreign-catalog", name,
                                     "record targets another catalog; its research inputs were not inspected"))
            else:
                row["state"], problems = _check_record(root, name)
                issues.extend(problems)
                for key in record["claims"]:
                    if key in rows_by_id:
                        rows_by_id[key]["reviews"].append({
                            "path": name, "kind": row["kind"], "state": row["state"],
                        })
                    else:
                        issues.append(_issue("warning", "unknown-reviewed-claim", name,
                                             f"record names an unavailable claim: {key}"))
        except (EvidenceError, OSError, UnicodeError) as exc:
            issues.append(_issue("error", "invalid-record", name, str(exc)))
        checked.append(row)

    for row in claims:
        current = Counter(review["kind"] for review in row["reviews"] if review["state"] == "current")
        row["current_reviews_by_kind"] = dict(sorted(current.items()))
        row["has_current_proof_review"] = any(current[kind] for kind in PROOF_REVIEW_KINDS)
        if not row["has_current_proof_review"]:
            row["attention"].append("no-current-proof-review")
            if row["evidence_status"] in PROVED:
                issues.append(_issue("warning", "unreviewed-established-claim",
                                     f"{catalog_name}#{row['id']}",
                                     "recorded as proved, but no directly selected current proof/formal/owner review was found"))

    adoption = ("catalog" if catalog_present else "records-only" if names else "not-adopted")
    status = ("error" if any(issue["severity"] == "error" for issue in issues)
              else "warning" if issues else "ok")
    return {
        "schema_version": 1, "status": status, "research": research, "adoption": adoption,
        "catalog": catalog_name if catalog_present or catalog is not None else None,
        "reviews_directory": discovery_dir,
        "selection": "explicit-records" if records else "program-reviews-directory",
        "claims": claims, "records": checked,
        "summary": {
            "claim_count": len(claims), "record_count": len(checked),
            "evidence_statuses": dict(sorted(Counter(row["evidence_status"] for row in claims).items())),
            "review_states": dict(sorted(Counter(row["state"] for row in checked).items())),
            "claims_with_current_proof_review": sum(row["has_current_proof_review"] for row in claims),
            "claims_without_current_proof_review": sum(not row["has_current_proof_review"] for row in claims),
            "formal_mappings_needing_attention": sum(
                row["formal"] is not None and any(
                    row["formal"][kind] != "pass" for kind in ("kernel", "alignment")
                ) for row in claims
            ),
        },
        "issues": issues,
        "limits": [
            "Recorded evidence statuses are assertions, not certifications by this inventory.",
            "Only explicitly named claims receive review coverage; transitive dependencies do not inherit approval.",
            "Historical and conflicting records are retained; dates do not automatically supersede a review.",
            "No workspace-wide discovery or mathematical, visual, Lean, or independence check is performed.",
        ],
    }
