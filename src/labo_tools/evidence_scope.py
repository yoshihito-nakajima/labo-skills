"""Read-only, bounded TeX input diagnostics, not a TeX interpreter or approval."""

from __future__ import annotations

from bisect import bisect_right
from pathlib import Path, PurePosixPath, PureWindowsPath
import re

from .evidence import (
    Catalog, EvidenceError, _digest_file, _load, _path, _record_shape, _relative,
    _tree, _workspace,
)
from .plans import SLUG


MAX_FILES = 256
MAX_DEPTH = 64
MAX_FILE_BYTES = 2 * 1024 * 1024
MAX_TOTAL_BYTES = 16 * 1024 * 1024
CONTROL = re.compile(r"\\([A-Za-z@]+|.)", re.DOTALL)
ARGUMENT = re.compile(r"\s*\{([^{}]*)\}")
OPTION = re.compile(r"\s*\[[^\[\]]*\]")
COMMANDS = {
    "input": ("tex", ".tex"), "include": ("tex", ".tex"),
    "includegraphics": ("graphic", ""), "bibliography": ("bibliography", ".bib"),
    "addbibresource": ("bibliography", ".bib"),
    "documentclass": ("class", ".cls"), "LoadClass": ("class", ".cls"),
    "usepackage": ("style", ".sty"), "RequirePackage": ("style", ".sty"),
}
DYNAMIC = {
    "graphicspath", "DeclareGraphicsExtensions", "includeonly", "import", "subimport",
    "inputfrom", "subinputfrom", "includefrom", "subincludefrom", "catcode",
    "csname", "newcommand", "renewcommand", "providecommand", "def", "edef",
    "gdef", "xdef", "let", "newif", "DeclareRobustCommand", "newenvironment",
    "renewenvironment", "ExplSyntaxOn",
    "InputIfFileExists", "IfFileExists", "scantokens", "directlua", "write", "openin",
}
VERBATIM = {"verbatim", "verbatim*", "Verbatim", "lstlisting", "minted", "comment"}
GRAPHICS = (".pdf", ".png", ".jpg", ".jpeg", ".eps", ".ps", ".svg", ".mps")


def _masked(source: str) -> tuple[str, bool]:
    """Mask comments/verbatim while preserving offsets and line numbers."""
    chars = list(source)
    offset = 0
    malformed = False

    def mask(start: int, end: int) -> None:
        for index in range(start, end):
            if chars[index] != "\n":
                chars[index] = " "

    while offset < len(source):
        if source[offset] == "%":
            end = source.find("\n", offset)
            end = len(source) if end < 0 else end
            mask(offset, end)
            offset = end
            continue
        match = CONTROL.match(source, offset)
        if not match:
            offset += 1
            continue
        name = match.group(1)
        if name in {"verb", "Verb"}:
            start = match.end()
            if start < len(source) and source[start] == "*":
                start += 1
            if start >= len(source) or source[start].isspace():
                malformed = True
                offset = match.end()
                continue
            end = source.find(source[start], start + 1)
            newline = source.find("\n", start)
            if end < 0 or (newline >= 0 and end > newline):
                malformed = True
                end = len(source) if newline < 0 else newline
            else:
                end += 1
            mask(offset, end)
            offset = end
            continue
        if name == "begin":
            arg = ARGUMENT.match(source, match.end())
            if arg and arg.group(1) in VERBATIM:
                marker = "\\end{" + arg.group(1) + "}"
                end = source.find(marker, arg.end())
                if end < 0:
                    malformed = True
                    end = len(source)
                else:
                    end += len(marker)
                mask(offset, end)
                offset = end
                continue
        offset = match.end()
    return "".join(chars), malformed


def inspect_scope(workspace: Path, *, source: str | None = None,
                  paper: str | None = None, record: str | None = None,
                  files: list[str] | None = None, trees: list[str] | None = None,
                  compile_root: str | None = None) -> dict:
    """Discover literal TeX dependencies and compare an explicitly chosen scope.

    ``status == 'ok'`` means only that these diagnostics found no issue. It is
    never a completeness, review, freshness, or mathematical validity verdict.
    No source, snapshot, selected scope, or review metadata is changed.
    """
    root = _workspace(workspace)
    if (source is None) == (paper is None):
        raise EvidenceError("select exactly one of --source or --paper")
    if paper is not None:
        if not SLUG.fullmatch(paper):
            raise EvidenceError("paper must be a lowercase kebab-case directory name")
        source = f"writing/{paper}/main.tex"
    assert source is not None
    _path(root, source)
    if Path(source).suffix.lower() != ".tex":
        raise EvidenceError("scope source must be a .tex file")
    if record is not None and (files or trees):
        raise EvidenceError("--record cannot be combined with --file or --tree")
    if compile_root is not None:
        if compile_root != ".":
            _path(root, compile_root, directory=True)
        compilation_root = compile_root
    else:
        compilation_root = PurePosixPath(source).parent.as_posix()
    issues: list[dict] = []
    unresolved: list[dict] = []
    dependencies: list[dict] = []
    coverage: dict[str, list[str]] = {}
    selection = {"mode": "discovery", "record": record, "files": [], "trees": [], "claims": []}

    def issue(code: str, path: str, message: str, *, line: int | None = None,
              severity: str = "warning", **extra: object) -> None:
        item = {"severity": severity, "code": code, "path": path, "message": message}
        if line is not None:
            item["line"] = line
        item.update(extra)
        issues.append(item)

    def unresolved_item(code: str, path: str, line: int, message: str, **extra: object) -> None:
        item = {"code": code, "path": path, "line": line, "message": message, **extra}
        unresolved.append(item)
        issue(code, path, message, line=line, **extra)

    def cover(path: str, via: str) -> None:
        coverage.setdefault(path, []).append(via)

    if record is not None:
        selection["mode"] = "record"
        data = _load(_path(root, record))
        _record_shape(data)
        selection.update(files=sorted(data["files"]), trees=sorted(data["trees"]),
                         claims=sorted(data["claims"]))
        # A selected tree covers only its recorded members, not later additions.
        for name, digest in data["files"].items():
            cover(name, f"record-file:{record}")
            check_recorded(root, name, digest, issue)
        for tree, members in data["trees"].items():
            for name, digest in members.items():
                cover(name, f"record-tree:{tree}")
                check_recorded(root, name, digest, issue)
        if data["claims"]:
            # Claim hashes contain no historical membership list. Recover current
            # files only when the complete transitive fingerprint still matches.
            try:
                catalog = Catalog(root, data["catalog"])
                for key, digest in data["claims"].items():
                    if catalog.fingerprints([key])[key] != digest:
                        issue("unresolved-claim-scope", record,
                              f"claim {key} changed; historical evidence membership cannot be recovered")
                        unresolved.append({"code": "unresolved-claim-scope", "path": record,
                                           "line": 0, "message": f"unrecoverable claim scope: {key}"})
                        continue
                    for dep in catalog.closure(key):
                        inputs = catalog.claim_inputs(dep)
                        for field in ("evidence", "owner_check"):
                            for name in inputs.get(field, {}):
                                cover(name, f"record-claim:{key}/{dep}")
                        for name in inputs.get("formal", {}).get("files", {}):
                            cover(name, f"record-claim:{key}/{dep}")
            except (EvidenceError, OSError, UnicodeError) as exc:
                unresolved_item("unresolved-claim-scope", record, 0, str(exc))
    elif files or trees:
        selection.update(mode="explicit", files=sorted(set(files or [])), trees=sorted(set(trees or [])))
        for name in selection["files"]:
            _path(root, name)
            cover(name, f"file:{name}")
        for name in selection["trees"]:
            for member in _tree(root, name):
                cover(member, f"tree:{name}")

    visited: set[str] = set()
    active: list[str] = []
    total_bytes = 0

    def candidate(base: str, target: str) -> str:
        if (not target or "\\" in target or "\0" in target or
                PurePosixPath(target).is_absolute() or PureWindowsPath(target).drive):
            raise EvidenceError("dependency must be a local relative POSIX filename")
        if len(target.encode("utf-8")) > 4096 or len(PurePosixPath(target).parts) > 128:
            raise EvidenceError("literal dependency path exceeds the supported 4096-byte/128-component bound")
        parts = [] if base == "." else list(PurePosixPath(base).parts)
        for part in PurePosixPath(target).parts:
            if part == "..":
                if not parts:
                    raise EvidenceError("dependency must not escape the workspace")
                parts.pop()
                continue
            parts.append(part)
            prefix = PurePosixPath(*parts).as_posix()
            current = root / prefix
            # Inspect before normalizing away a later '..': a symlinked
            # component must not disappear behind lexical normalization.
            if current.is_symlink():
                raise EvidenceError(f"symlinked input is not supported: {prefix}")
            if current.exists():
                _path(root, prefix, directory=current.is_dir())
        normalized = PurePosixPath(*parts).as_posix()
        _relative(normalized)
        # _path checks every component, including symlinks and policy checkout.
        try:
            _path(root, normalized)
        except EvidenceError:
            if (root / normalized).exists() or (root / normalized).is_symlink():
                raise
            # Check nearest existing ancestor as well, without traversing it.
            ancestor = PurePosixPath(normalized).parent
            while ancestor.as_posix() != "." and not (root / ancestor).exists():
                ancestor = ancestor.parent
            if ancestor.as_posix() != ".":
                _path(root, ancestor.as_posix(), directory=True)
        return normalized

    def resolve(target: str, kind: str, suffix: str, owner: str, line: int) -> str | None:
        variants = [target]
        if not PurePosixPath(target).suffix:
            variants = [target + ext for ext in GRAPHICS] if kind == "graphic" else [target + suffix]
        bases = list(dict.fromkeys([compilation_root, PurePosixPath(owner).parent.as_posix()]))
        names = []
        root_names = []
        try:
            for base in bases:
                for variant in variants:
                    name = candidate(base, variant)
                    if base == compilation_root:
                        root_names.append(name)
                    if (root / name).is_file() and name not in names:
                        names.append(name)
        except (EvidenceError, OSError, UnicodeError) as exc:
            unresolved_item("unsafe-dependency", owner, line, str(exc), argument=target)
            issues[-1]["severity"] = "error"
            return None
        if len(names) > 1:
            unresolved_item("ambiguous-dependency", owner, line,
                            "multiple local paths or graphic variants; no resolution was chosen",
                            argument=target, candidates=names)
            return None
        if not names:
            if kind in {"style", "class"}:
                unresolved_item("external-tex-dependency", owner, line,
                                "no local style/class found; TeX installation and search paths were not inspected",
                                argument=target)
            else:
                unresolved_item("missing-dependency", owner, line,
                                "literal dependency was not found under either documented base",
                                argument=target)
                issues[-1]["severity"] = "error"
            return None
        name = names[0]
        if name not in root_names:
            unresolved_item("source-relative-dependency", owner, line,
                            "only a source-relative candidate exists; compilation-root semantics are unconfirmed",
                            argument=target, candidates=[name])
        return name

    def visit(name: str, depth: int) -> None:
        nonlocal total_bytes
        if name in active:
            unresolved_item("dependency-cycle", name, 0, "circular literal inputs", cycle=[*active, name])
            return
        if name in visited:
            return
        if depth > MAX_DEPTH or len(visited) >= MAX_FILES:
            unresolved_item("traversal-limit", name, 0, "bounded traversal limit reached")
            return
        visited.add(name)
        try:
            path = _path(root, name)
            size = path.stat().st_size
            if size > MAX_FILE_BYTES or total_bytes + size > MAX_TOTAL_BYTES:
                unresolved_item("read-limit", name, 0, "bounded source byte limit reached")
                return
            # Bound the actual read as well as the stat, including concurrent
            # growth between the two operations. This is not a frozen snapshot.
            remaining = min(MAX_FILE_BYTES, MAX_TOTAL_BYTES - total_bytes)
            with path.open("rb") as stream:
                contents = stream.read(remaining + 1)
            if len(contents) > remaining:
                unresolved_item("read-limit", name, 0, "bounded source byte limit reached")
                return
            total_bytes += len(contents)
            text, malformed = _masked(contents.decode("utf-8"))
        except (EvidenceError, OSError, UnicodeError) as exc:
            issue("unreadable-source", name, str(exc), severity="error")
            return
        if malformed:
            unresolved_item("malformed-verbatim", name, 0, "unterminated or unsupported verbatim construct")
        active.append(name)
        offset = 0
        depth_brace = 0
        newlines = [index for index, char in enumerate(text) if char == "\n"]
        while offset < len(text):
            match = CONTROL.match(text, offset)
            if not match:
                if text[offset] == "{":
                    depth_brace += 1
                elif text[offset] == "}":
                    depth_brace -= 1
                offset += 1
                continue
            command = match.group(1)
            line = bisect_right(newlines, offset) + 1
            offset = match.end()
            if command in {"endinput"}:
                break
            if command == "end":
                arg = ARGUMENT.match(text, offset)
                if arg and arg.group(1).strip() == "document":
                    break
            if command.lower().startswith("if") or command in DYNAMIC or command in {"else", "fi", "or", "unless"}:
                unresolved_item("dynamic-tex", name, line,
                                f"\\{command} may alter input discovery; TeX was not evaluated", command=command)
            if command not in COMMANDS:
                continue
            if offset < len(text) and text[offset] == "*":
                offset += 1
            option = OPTION.match(text, offset)
            if option:
                offset = option.end()
            arg = ARGUMENT.match(text, offset)
            if not arg:
                unresolved_item("nonliteral-dependency", name, line,
                                f"\\{command} requires a simple braced literal argument", command=command)
                continue
            offset = arg.end()
            raw = arg.group(1).strip()
            if depth_brace or any(char in raw for char in "\\#$^~%"):
                unresolved_item("nonliteral-dependency", name, line,
                                "macro/group-dependent filename was not expanded", command=command, argument=raw)
                continue
            kind, suffix = COMMANDS[command]
            targets = raw.split(",") if command in {"bibliography", "usepackage", "RequirePackage"} else [raw]
            for target in targets:
                target = target.strip()
                resolved = resolve(target, kind, suffix, name, line)
                if resolved is None:
                    continue
                dependencies.append({"path": resolved, "kind": kind, "from": name,
                                     "line": line, "argument": target})
                if kind in {"tex", "style", "class"}:
                    visit(resolved, depth + 1)
        active.pop()

    dependencies.append({"path": source, "kind": "source", "from": None, "line": 1, "argument": source})
    visit(source, 0)
    discovered = sorted({item["path"] for item in dependencies})
    omitted = [] if selection["mode"] == "discovery" else sorted(set(discovered) - set(coverage))
    for name in omitted:
        issue("omitted-dependency", name, "discovered input is outside the selected actual evidence members")
    status = "error" if any(item["severity"] == "error" for item in issues) else "warning" if issues else "ok"
    return {
        "schema_version": 1, "status": status, "source": source,
        "compilation_root": compilation_root, "selection": selection,
        "dependencies": dependencies,
        "covered": [{"path": name, "via": sorted(set(coverage[name]))}
                    for name in discovered if name in coverage],
        "omitted": omitted, "suggested_files": omitted, "unresolved": unresolved, "issues": issues,
        "limitations": "Literal, bounded diagnostics only; not TeX completeness, approval, freshness certification, or mathematical verification.",
    }


def check_recorded(root: Path, name: str, digest: str, issue) -> None:
    """Report changed recorded members without refreshing their fingerprints."""
    try:
        if _digest_file(_path(root, name)) != digest:
            issue("changed-recorded-input", name, "recorded member bytes changed; membership is not approval")
    except (EvidenceError, OSError, UnicodeError) as exc:
        issue("unavailable-recorded-input", name, str(exc))
