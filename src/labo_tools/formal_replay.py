"""Explicit, selected-source Lean replay; never approval or a project sandbox.

No Lake or elan process is started. Dependencies must already have compiled
artifacts. See the skill-owned formal-replay reference for the trust boundary.
"""

from __future__ import annotations

from datetime import datetime, timezone
import json
import math
import os
from pathlib import Path
import re
import signal
import subprocess
import tempfile
import time

from .evidence import Catalog, EvidenceError, _digest, _digest_file, _path


NAME = re.compile(r"[A-Za-z_][A-Za-z_0-9']*(?:\.[A-Za-z_][A-Za-z_0-9']*)*\Z")
PIN = re.compile(r"leanprover/lean4:v(4\.[0-9]+\.[0-9]+)\Z")
REVISION = re.compile(r"[0-9a-f]{40}\Z")
HASH_SUFFIXES = {".lean", ".olean", ".ilean", ".ir", ".so", ".dylib", ".dll", ".a"}
ENV_FILES = {"lean-toolchain", "lake-manifest.json", "lakefile.lean", "lakefile.toml"}
WINDOWS = os.name == "nt"
WARNINGS = [
    "Selected-source build only: prepared imported artifacts are hashed, not rebuilt from source.",
    "Lean can execute project/dependency code during elaboration. Execute only trusted code; this is not a network or filesystem sandbox.",
    "No Lake, elan, installer, dependency fetch, or cache-download command is invoked by this runner.",
    "This uses the selected Lean kernel, not an independent proof checker, and does not establish equivalence to the informal claim.",
    "A completed replay never promotes a claim, approves a snapshot, changes alignment, or endorses arbitrary axioms.",
]


def _ordinary(path: Path, *, directory: bool = False) -> Path:
    """Reject links, including ancestors, before reading selected local inputs."""
    absolute = path.absolute()
    for part in [absolute, *absolute.parents]:
        if part.is_symlink():
            raise EvidenceError(f"symlinked replay input is not supported: {path}")
    if not (absolute.is_dir() if directory else absolute.is_file()):
        raise EvidenceError(f"missing replay {'directory' if directory else 'file'}: {path}")
    return absolute


def _inventory(directory: Path) -> dict[str, str]:
    """Source, pins and compiled Lean inputs, including prepared dependencies."""
    result = {}
    def walk_error(error: OSError) -> None:
        raise EvidenceError(f"cannot inventory replay inputs: {directory}: {error}") from error

    for current, directories, filenames in os.walk(directory, followlinks=False, onerror=walk_error):
        directories[:] = sorted(name for name in directories if name not in {
            ".git", ".venv", "__pycache__", "node_modules",
        })
        for name in directories:
            _ordinary(Path(current) / name, directory=True)
        for name in sorted(filenames):
            path = Path(current) / name
            if path.suffix in HASH_SUFFIXES or name in ENV_FILES or name == "package-overrides.json":
                _ordinary(path)
                result[path.relative_to(directory).as_posix()] = _digest_file(path)
    return result


def _git_head(directory: Path) -> str | None:
    """Read only: do not run Git (or hooks) during preflight."""
    metadata = directory / ".git"
    if not metadata.is_dir() or metadata.is_symlink():
        return None
    head = _ordinary(metadata / "HEAD").read_text(encoding="utf-8").strip()
    if REVISION.fullmatch(head):
        return head
    if not head.startswith("ref: refs/"):
        return None
    reference = head[5:]
    if ".." in reference or "\\" in reference or "\0" in reference:
        return None
    ref = metadata / reference
    if ref.is_file():
        value = _ordinary(ref).read_text(encoding="utf-8").strip()
        return value if REVISION.fullmatch(value) else None
    packed = metadata / "packed-refs"
    if packed.is_file():
        for line in _ordinary(packed).read_text(encoding="utf-8").splitlines():
            parts = line.split()
            if len(parts) == 2 and parts[1] == reference and REVISION.fullmatch(parts[0]):
                return parts[0]
    return None


def _prepared(project: Path) -> tuple[list[Path], list[dict], list[str]]:
    problems: list[str] = []
    dependencies = []
    paths = []
    manifest = _ordinary(project / "lake-manifest.json")
    try:
        data = json.loads(manifest.read_text(encoding="utf-8"))
    except (ValueError, UnicodeError) as exc:
        raise EvidenceError(f"invalid lake-manifest.json: {exc}") from exc
    if not isinstance(data, dict) or not isinstance(data.get("packages"), list):
        raise EvidenceError("lake-manifest.json must contain a packages list")
    if data.get("packagesDir", ".lake/packages") != ".lake/packages" or data.get("lakeDir", ".lake") != ".lake":
        problems.append("only conventional .lake/packages and .lake directories are supported")
    if (project / ".lake/package-overrides.json").exists():
        problems.append("package overrides require manual audit; automatic replay does not support them")
    seen = set()
    for entry in data["packages"]:
        if not isinstance(entry, dict):
            raise EvidenceError("each Lake manifest package must be a mapping")
        name = entry.get("name")
        if not isinstance(name, str) or not re.fullmatch(r"[A-Za-z_][A-Za-z_0-9-]*", name) or name in seen:
            raise EvidenceError("manifest package names must be unique simple names")
        seen.add(name)
        revision = entry.get("rev")
        if entry.get("type") != "git" or not isinstance(revision, str) or not REVISION.fullmatch(revision) or entry.get("subDir") not in (None, ""):
            problems.append(f"{name}: requires a prepared Git package pinned to a full lowercase commit, without subDir")
            continue
        directory = project / ".lake/packages" / name
        if not directory.is_dir():
            problems.append(f"{name}: prepared dependency directory unavailable")
            continue
        _ordinary(directory, directory=True)
        actual = _git_head(directory)
        dependencies.append({"name": name, "revision": revision, "actual_head": actual,
                             "path": str(directory)})
        if actual != revision:
            problems.append(f"{name}: local HEAD does not match the pinned manifest revision")
        library = directory / ".lake/build/lib/lean"
        if not library.is_dir():
            problems.append(f"{name}: prepared .lake/build/lib/lean unavailable")
        else:
            paths.append(_ordinary(library, directory=True))
    local = project / ".lake/build/lib/lean"
    if local.is_dir():
        paths.insert(0, _ordinary(local, directory=True))
    # Old lib layouts are deliberately not guessed: explicit unavailable beats
    # silently searching the wrong artifacts.
    return paths, dependencies, problems


def _command(argv: list[str], cwd: Path, env: dict[str, str], *, stdin: str | None = None) -> dict:
    return {"argv": argv, "cwd": str(cwd), "environment": env, "stdin": stdin,
            "status": "not-run", "exit_code": None, "stdout": "", "stderr": ""}


def _run_command(record: dict, timeout: float) -> bool:
    """No shell. File-backed capture avoids hanging on inherited pipe handles.

    POSIX timeout kills the process group. Windows kills the direct process;
    descendant cleanup there is explicitly not guaranteed.
    """
    start = time.monotonic()
    process = None
    with tempfile.TemporaryFile() as output, tempfile.TemporaryFile() as errors:
        try:
            process = subprocess.Popen(record["argv"], cwd=record["cwd"], env=record["environment"],
                                       stdin=subprocess.PIPE, stdout=output, stderr=errors,
                                       text=True, encoding="utf-8", errors="replace",
                                       start_new_session=not WINDOWS,
                                       creationflags=getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0) if WINDOWS else 0)
            process.communicate(record["stdin"], timeout=timeout)
            record.update(status="completed" if process.returncode == 0 else "failed",
                          exit_code=process.returncode)
        except subprocess.TimeoutExpired:
            if WINDOWS:
                process.kill()
            else:
                # Deliberately detached hostile processes are outside this
                # trusted-code contract, not sandboxed here.
                os.killpg(process.pid, signal.SIGKILL)
            process.communicate()
            record.update(status="timeout", exit_code=process.returncode)
        except OSError as exc:
            record.update(status="unavailable", stderr=str(exc))
        output.seek(0)
        errors.seek(0)
        record["stdout"] = output.read().decode("utf-8", errors="replace")
        record["stderr"] += errors.read().decode("utf-8", errors="replace")
    record["duration_seconds"] = round(time.monotonic() - start, 6)
    return record["status"] == "completed"


def _axioms(output: str, declaration: str) -> list[str] | None:
    escaped = re.escape(declaration)
    empty = re.findall(rf"'{escaped}' does not depend on any axioms", output)
    lists = re.findall(rf"'{escaped}' depends on axioms:\s*\[([^\]]*)\]", output, re.DOTALL)
    if len(empty) + len(lists) != 1:
        return None
    if empty:
        return []
    names = [name.strip() for name in lists[0].split(",")]
    # Do not silently drop an unrecognized/escaped/new Lean output format.
    if not names or any(not NAME.fullmatch(name) for name in names):
        return None
    return names


def replay(workspace: Path, *, catalog: str, claim: str, execute: bool = False,
           timeout: float = 60.0, toolchain_dir: Path | None = None) -> dict:
    """Plan by default; explicitly execute a selected source and axiom audit.

    Return a JSON-serializable observation, never an approval record. Invalid
    selection raises EvidenceError; unavailable execution prerequisites are
    reported without starting Lean. Timeout is per command, not a global budget.
    """
    if isinstance(timeout, bool) or not isinstance(timeout, (int, float)) or not math.isfinite(timeout) or timeout <= 0:
        raise EvidenceError("replay timeout must be a finite positive number of seconds")
    selected = Catalog(workspace, catalog)
    if claim not in selected.claims:
        raise EvidenceError(f"unknown replay claim: {claim}")
    selected.closure(claim)
    formal = selected.claim_inputs(claim).get("formal")
    if formal is None:
        raise EvidenceError("replay requires an exact formal mapping for the selected claim")
    mapping = formal["mapping"]
    project = _path(selected.root, mapping["project"], directory=True)
    source = _path(selected.root, mapping["source"])
    declaration = mapping["declaration"]
    if not NAME.fullmatch(declaration):
        raise EvidenceError("replay declaration must use simple ASCII dotted Lean identifiers")
    module = ".".join(source.relative_to(project).with_suffix("").parts)
    if not NAME.fullmatch(module) or module in {"Init", "Lean", "Std", "Main"}:
        raise EvidenceError("replay needs an unambiguous simple project-root module (not Init, Lean, Std, or Main)")
    pin = _ordinary(project / "lean-toolchain").read_text(encoding="utf-8").strip()
    match = PIN.fullmatch(pin)
    problems = []
    if not match:
        problems.append("only exact stable leanprover/lean4:v4.X.Y toolchain pins are supported")
    if toolchain_dir is None:
        elan = Path(os.environ.get("ELAN_HOME", str(Path.home() / ".elan")))
        toolchain = elan / "toolchains" / pin.replace("/", "--").replace(":", "---")
    else:
        toolchain = Path(toolchain_dir)
    toolchain = toolchain.absolute()
    lean = toolchain / "bin" / ("lean.exe" if WINDOWS else "lean")
    if not lean.is_file() or not (toolchain / "lib/lean/Init.olean").is_file():
        problems.append("prepared direct Lean installation unavailable; no elan shim or installer will be run")
    else:
        _ordinary(toolchain, directory=True)
        _ordinary(lean)
        if not os.access(lean, os.X_OK):
            problems.append("selected Lean binary is not executable")
        # A script in bin/lean is not accepted as a direct installed toolchain.
        with lean.open("rb") as stream:
            magic = stream.read(4)
        native = magic[:2] == b"MZ" if WINDOWS else magic in {
            b"\x7fELF", b"\xcf\xfa\xed\xfe", b"\xfe\xed\xfa\xcf", b"\xca\xfe\xba\xbe",
        }
        if not native:
            problems.append("selected Lean must be a native toolchain binary, not a shim script")
    search, dependencies, prepared_problems = _prepared(project)
    problems.extend(prepared_problems)
    # Selected-source output always wins over prepared artifacts. Other module
    # collisions would make the prepared environment ambiguous.
    modules = {}
    for directory in search:
        for name in _inventory(directory):
            if name.endswith(".olean"):
                imported = name[:-6].replace("/", ".")
                if imported != module and imported in modules:
                    problems.append(f"ambiguous prepared module: {imported}")
                modules[imported] = str(directory)
    # Lean 4.19's Delaborator/Options.lean defines pp.maxSteps; pp.all also
    # enables deep-term printing. There is no pp.maxDepth option in that release.
    audit = (f"import {module}\nset_option pp.all true\n"
             "set_option pp.maxSteps 1000000\n"
             f"#check @{declaration}\n#print {declaration}\n"
             f"set_option pp.all false\n#print axioms {declaration}\n")
    placeholder = Path("<temporary-replay>")
    env = {"PATH": os.pathsep.join([str(toolchain / "bin"), os.defpath]), "LEAN_SYSROOT": str(toolchain),
           "LEAN_PATH": os.pathsep.join([str(placeholder), *map(str, search)]),
           "LANG": "C.UTF-8", "LC_ALL": "C.UTF-8"}
    if WINDOWS and "SYSTEMROOT" in os.environ:
        env["SYSTEMROOT"] = os.environ["SYSTEMROOT"]
    commands = [
        _command([str(lean), "--version"], project, env),
        _command([str(lean), "--help"], project, env),
        _command([str(lean), "--trust=0", f"--root={project}", "-o",
                  str(placeholder / source.relative_to(project).with_suffix(".olean")), str(source)], project, env),
        _command([str(lean), "--trust=0", "--stdin"], project, env, stdin=audit),
    ]

    def inputs() -> dict:
        result = {"catalog_sha256": _digest_file(selected.root / catalog),
                  "project_files": _inventory(project), "environment_sha256": _digest(env),
                  "dependency_heads": {item["name"]: _git_head(Path(item["path"]))
                                       for item in dependencies}}
        if lean.is_file():
            result["lean_executable_sha256"] = _digest_file(_ordinary(lean))
        if (toolchain / "lib/lean").is_dir():
            result["toolchain_library_files"] = _inventory(_ordinary(toolchain / "lib/lean", directory=True))
        result["sha256"] = _digest(result)
        return result

    before = inputs()
    report = {"schema_version": 1, "kind": "lean-selected-source-replay",
              "status": "plan", "executed": False, "catalog": catalog, "claim": claim,
              "statement": selected.claims[claim]["statement"], "project": mapping["project"],
              "source": mapping["source"], "module": module, "declaration": declaration,
              "toolchain": {"pin": pin, "directory": str(toolchain), "version": None},
              "dependencies": dependencies, "timeout_seconds_per_command": timeout,
              "preflight": {"ready": not problems, "problems": sorted(set(problems))},
              "commands": commands, "inputs_before": before, "inputs_after": None,
              "inputs_changed": None, "axiom_audit": {"status": "not-run", "axioms": None,
              "sorry_ax": None, "review_required": None, "raw_output": None},
              "warnings": list(WARNINGS), "alignment": "not-assessed",
              "approval": "not-granted"}
    if WINDOWS:
        report["warnings"].append("Windows timeout terminates only the direct Lean process; descendant termination is not guaranteed. Use trusted code in an external sandbox when needed.")
    if not execute:
        return report
    if problems:
        report["status"] = "unavailable"
        return report
    report.update(executed=True, status="failed",
                  started_at=datetime.now(timezone.utc).isoformat())
    try:
        with tempfile.TemporaryDirectory(prefix="labo-lean-replay-") as temporary:
            fresh = Path(temporary)
            env["LEAN_PATH"] = os.pathsep.join([str(fresh), *map(str, search)])
            # The controlled environment is shared by each command record.
            # Snapshot the actual values before invoking anything.
            before["environment_sha256"] = _digest(env)
            before["sha256"] = _digest({k: v for k, v in before.items() if k != "sha256"})
            output = fresh / source.relative_to(project).with_suffix(".olean")
            output.parent.mkdir(parents=True, exist_ok=True)
            commands[2]["argv"][4] = str(output)
            for index, command in enumerate(commands):
                if not _run_command(command, timeout):
                    report["failure"] = f"command {index + 1}: {command['status']}"
                    if index == 3:
                        report["axiom_audit"].update(status=command["status"], raw_output=command["stdout"])
                    break
                if index == 0:
                    report["toolchain"]["version"] = command["stdout"].strip()
                    if not re.search(rf"\bversion {re.escape(match[1])}(?:\s|,|\))", command["stdout"]):
                        report["failure"] = "selected Lean version does not match the exact toolchain pin"
                        break
                elif index == 1:
                    if any(flag not in command["stdout"] for flag in ("--trust", "--stdin", "--root")):
                        report["failure"] = "selected Lean does not advertise the required trust/stdin/root options"
                        break
                elif index == 2 and not output.is_file():
                    report["failure"] = "Lean returned success without producing the selected source artifact"
                    break
            else:
                raw = commands[3]["stdout"]
                axioms = _axioms(raw, declaration)
                if axioms is None:
                    report["axiom_audit"].update(status="unavailable", raw_output=raw)
                    report["failure"] = "axiom output is missing, ambiguous, or unsupported; no success inferred"
                else:
                    sorry = "sorryAx" in axioms
                    report["axiom_audit"].update(status="failed" if sorry else "completed",
                        axioms=axioms, sorry_ax=sorry, review_required=bool(axioms), raw_output=raw)
                    if sorry:
                        report["failure"] = "selected declaration transitively depends on sorryAx"
                    else:
                        report["status"] = "completed"
                        if axioms:
                            report["warnings"].append("Every reported axiom requires explicit trust-policy review; none is automatically endorsed.")
                report["built_artifact_sha256"] = _digest_file(output)
    finally:
        try:
            report["inputs_after"] = inputs()
            report["inputs_changed"] = report["inputs_before"] != report["inputs_after"]
        except (EvidenceError, OSError) as exc:
            report["inputs_after"] = {"error": str(exc)}
            report["inputs_changed"] = True
        if report["inputs_changed"]:
            report["status"] = "failed"
            report["failure"] = "tracked replay inputs changed or became unreadable during execution"
        report["finished_at"] = datetime.now(timezone.utc).isoformat()
    return report
