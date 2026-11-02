"""A conservative completion gate over existing claim/formal-review records.

This module checks recorded inputs, not Lean or mathematical alignment itself.
"""

import json

from .evidence import Catalog, EvidenceError, _load, _path
from .evidence_status import evidence_status


def guarantee(workspace, research, nodes):
    cache = {}

    def has_report(name):
        text = _path(workspace, name).read_text(encoding="utf-8").strip()
        return bool(text) and text.casefold() not in {"pass", "passed", "ok", "success", "true", "verified"}

    def local_scopes(project):
        """Path packages need explicit snapshot trees; the old catalog omits them."""
        scopes, seen, pending = set(), set(), [project]
        while pending:
            current = pending.pop()
            if current in seen:
                continue
            seen.add(current)
            manifest = json.loads((current / "lake-manifest.json").read_text(encoding="utf-8"))
            if not isinstance(manifest, dict) or not isinstance(manifest.get("packages"), list):
                raise EvidenceError("Lake manifest must declare a packages list")
            for package in manifest["packages"]:
                if not isinstance(package, dict):
                    raise EvidenceError("invalid Lake manifest package")
                if not isinstance(package.get("type"), str) or package["type"] not in {"path", "git"}:
                    raise EvidenceError("unsupported Lake dependency type requires an explicit scope audit")
                if package.get("type") == "path":
                    directory = package.get("dir")
                    if not isinstance(directory, str) or not directory:
                        raise EvidenceError("path package needs an explicit dir")
                    raw = current / directory
                    if any(part.is_symlink() for part in (raw, *raw.parents)):
                        raise EvidenceError("symlinked local dependencies require an explicit scope audit")
                    target = raw.resolve()
                    if not target.is_relative_to(workspace.resolve()):
                        raise EvidenceError("path dependency outside workspace needs a separately supported audit")
                    relative = target.relative_to(workspace.resolve()).as_posix()
                    _path(workspace, relative, directory=True)
                    scopes.add(relative)
                    pending.append(target)
        return scopes

    def claim_result(reference):
        path, marker, key = reference.partition("#")
        if not marker or not key:
            return "unregistered", [f"claim reference needs an exact #ID: {reference}"]
        if not path.startswith(f"research/{research}/"):
            return "invalid", ["claim catalog must belong to the selected program"]
        if path not in cache:
            try:
                selected = Catalog(workspace, path)
                status = evidence_status(workspace, research=research, catalog=path)
                cache[path] = (selected, {row["id"]: row for row in status["claims"]})
            except (EvidenceError, OSError, UnicodeError) as exc:
                cache[path] = str(exc)
        cached = cache[path]
        if isinstance(cached, str):
            return "invalid", [cached]
        selected, rows = cached
        if key not in selected.claims:
            return "unregistered", [f"unknown claim: {reference}"]
        try:
            closure = selected.closure(key)
        except EvidenceError as exc:
            return "invalid", [str(exc)]
        for target in closure:
            claim = selected.claims[target]
            row = rows[target]
            label = f"{path}#{target}"
            formal = claim.get("formal")
            if not isinstance(formal, dict):
                return "unformalized", [f"{label}: exact formal mapping absent"]
            for kind, pending in (("kernel", "execution_pending"), ("alignment", "alignment_pending")):
                report = formal.get(kind)
                if not isinstance(report, dict) or report.get("verdict") != "pass":
                    return ("failed" if isinstance(report, dict) and report.get("verdict") == "fail" else pending), [f"{label}: {kind} report not passing"]
                try:
                    if not has_report(report["report"]):
                        return "invalid", [f"{label}: empty or verdict-only {kind} report"]
                except (KeyError, TypeError, EvidenceError, OSError, UnicodeError) as exc:
                    return "invalid", [f"{label}: invalid {kind} report: {exc}"]
            if claim["status"] != "verified-formally":
                return "unformalized", [f"{label}: claim is {claim['status']}, not verified-formally"]
            if row["structure"] != "valid":
                return "invalid", [f"{label}: formal inputs cannot be reproduced"]
            reviews = [review for review in row["reviews"] if review["kind"] == "formal"]
            if any(review["state"] == "failed" for review in reviews):
                return "failed", [f"{label}: failed formal review requires reconciliation"]
            current = [review for review in reviews if review["state"] == "current"]
            if not current:
                return ("stale" if any(review["state"] == "stale" for review in reviews) else "review_pending"), [f"{label}: no directly covering current formal review"]
            try:
                required_trees = local_scopes(_path(workspace, formal["project"], directory=True))
            except (KeyError, ValueError, EvidenceError, OSError, UnicodeError) as exc:
                return "scope_pending", [f"{label}: dependency input scope unavailable: {exc}"]
            substantive, covered = False, False
            for review in current:
                record = _load(_path(workspace, review["path"]))
                if not required_trees.issubset(record["trees"]):
                    continue
                covered = True
                if has_report(record["report"]):
                    substantive = True
            if not covered:
                return "scope_pending", [f"{label}: formal review must snapshot local dependency trees: {sorted(required_trees)}"]
            if not substantive:
                return "invalid", [f"{label}: empty or verdict-only formal review report"]
        return "current_records", []

    result = {}
    for node in nodes:
        state, reasons = "not_required", []
        if node["proof_required"]:
            state = "current_records"
            if not node["claim_refs"]:
                state, reasons = "unregistered", ["at least one exact existing claim reference is required"]
            for reference in node["claim_refs"]:
                state, reasons = claim_result(reference)
                if state != "current_records":
                    break
        result[node["id"]] = {"state": state, "reasons": reasons}
    return result
