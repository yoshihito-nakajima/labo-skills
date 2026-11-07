#!/usr/bin/env python3
"""Create, check, and build a workspace-local, local-only book-materials repository."""

from __future__ import annotations

import argparse
import hashlib
import os
from pathlib import Path
import re
import shutil
import stat
import subprocess
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from labo_tools.navigation import check_navigation

from reference_privacy import PrivacyError, require_local_boundary


DENY_PUSH = "#!/bin/sh\n# book-materials-deny-all-v1\necho 'Local book materials: all pushes are prohibited' >&2\nexit 1\n"
NO_FILTERS = "* -filter\n"


def run(*args: str, cwd: Path, check: bool = True) -> subprocess.CompletedProcess[str]:
    env = {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}
    return subprocess.run(args, cwd=cwd, env=env, text=True, capture_output=True, check=check)


def location(root: Path, workspace: Path) -> Path:
    """Allow only the guarded workspace/local default or a separate external root."""
    original = root.absolute()
    lexical_workspace = workspace.absolute()
    common = Path(os.path.commonpath((original, lexical_workspace)))
    workspace = workspace.resolve()
    # Resolve harmless .. aliases; reject symlinks in the selected namespace.
    # The shared host prefix may itself be an OS alias such as /var or /tmp.
    for parent in (original, *original.parents):
        if parent == common:
            break
        if parent.is_symlink():
            raise ValueError("materials path must not use symlinks")
    root = original.resolve()
    if root == workspace / "local":
        require_local_boundary(workspace)
        if (root / ".git").exists():
            raise ValueError("local/ must not own Git; only materials/ owns Git")
    else:
        if root == workspace or workspace in root.parents or root in workspace.parents:
            raise ValueError("internal materials root must be the guarded workspace/local directory")
        if any((parent / ".git").exists() for parent in (root, *root.parents)):
            raise ValueError("external materials root must not be inside another Git repository")
    return root


def validate(root: Path, workspace: Path) -> None:
    root = location(root, workspace)
    if not root.is_dir():
        raise ValueError("materials root does not exist")
    gitroot = root / "materials"
    if (root / ".git").exists() or gitroot.is_symlink() or (gitroot / ".git").is_symlink() or not (gitroot / ".git").is_dir():
        raise ValueError("only materials/ must own a real .git directory")
    top = run("git", "rev-parse", "--show-toplevel", cwd=gitroot).stdout.strip()
    if Path(top).resolve() != gitroot.resolve():
        raise ValueError("materials/ must own its independent Git")
    if run("git", "remote", cwd=gitroot).stdout.strip():
        raise ValueError("local materials Git must have no remotes")
    hook = gitroot / ".git" / "hooks" / "pre-push"
    if not hook.is_file() or hook.is_symlink() or hook.read_text() != DENY_PUSH or (os.name != "nt" and not (hook.stat().st_mode & stat.S_IXUSR)):
        raise ValueError("executable deny-all pre-push hook is missing or modified")
    hooks_path = run("git", "config", "--local", "--get", "core.hooksPath", cwd=gitroot).stdout.strip()
    if not hooks_path or Path(hooks_path).resolve() != hook.parent.resolve():
        raise ValueError("Git hooks path does not point to the guarded directory")
    attributes = gitroot / ".git" / "info" / "attributes"
    if not attributes.is_file() or attributes.is_symlink() or attributes.read_text() != NO_FILTERS:
        raise ValueError("external Git filters are not disabled")
    for name in ("originals", "cache", "output"):
        path = root / name
        if path.is_symlink() or (path.exists() and not path.is_dir()):
            raise ValueError(f"{name}/ must be a real directory outside materials Git")
        if any(entry.is_symlink() for entry in path.rglob("*")):
            raise ValueError(f"{name}/ must not contain symlinks")
    for entry in gitroot.rglob("*"):
        if entry.is_symlink():
            raise ValueError("materials Git must not contain symlinks")


def install(root: Path, workspace: Path) -> None:
    root = location(root, workspace)
    if root.exists() and (root.is_symlink() or any(root.iterdir())):
        raise ValueError("install requires a new empty real directory")
    root.mkdir(parents=True, exist_ok=True)
    gitroot = root / "materials"
    gitroot.mkdir()
    run("git", "init", "-q", cwd=gitroot)
    (gitroot / ".gitignore").write_text("*.synctex\n*.synctex.gz\n**/.temp/\n", encoding="utf-8")
    hook = gitroot / ".git" / "hooks" / "pre-push"
    hook.write_text(DENY_PUSH, encoding="utf-8")
    hook.chmod(0o755)
    run("git", "config", "--local", "core.hooksPath", str(hook.parent), cwd=gitroot)
    attributes = gitroot / ".git" / "info" / "attributes"
    attributes.write_text(NO_FILTERS, encoding="utf-8")
    for name in ("cache", "output"):
        (root / name).mkdir()
    validate(root, workspace)


def build(root: Path, workspace: Path, course: str, dry_run: bool) -> None:
    validate(root, workspace)
    root = root.resolve()
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", course):
        raise ValueError("course must be a simple slug")
    folder = root / "materials" / "courses" / course
    main = folder / "main.tex"
    if folder.is_symlink() or main.is_symlink() or not main.is_file():
        raise ValueError("course main.tex is missing or symlinked")
    if not re.search(r"\\documentclass\b", main.read_text(encoding="utf-8").split(r"\begin{document}", 1)[0]):
        raise ValueError("main.tex is not a document root")
    cache = root / "cache" / course
    output = root / "output"
    if cache.is_symlink() or output.is_symlink():
        raise ValueError("build directories must not be symlinks")
    for suffix in (".pdf", ".synctex.gz"):
        target = output / f"{course}{suffix}"
        if target.is_symlink() or target.with_name(target.name + ".new").is_symlink():
            raise ValueError("build artifacts must not be symlinks")
    command = ["latexmk", "-xelatex", "-synctex=1", "-interaction=nonstopmode", "-halt-on-error", "-file-line-error", f"-outdir={cache}", "main.tex"]
    print(" ".join(command))
    if dry_run:
        return
    cache.mkdir(parents=True, exist_ok=True)
    output.mkdir(parents=True, exist_ok=True)
    subprocess.run(command, cwd=folder, check=True)
    pdf = cache / "main.pdf"
    sync = cache / "main.synctex.gz"
    if not (pdf.is_file() and pdf.stat().st_size and sync.is_file() and sync.stat().st_size):
        raise ValueError("build needs a nonempty PDF and SyncTeX pair")
    for source, target in ((pdf, output / f"{course}.pdf"), (sync, output / f"{course}.synctex.gz")):
        temporary = target.with_name(target.name + ".new")
        if source.is_symlink() or target.is_symlink() or temporary.is_symlink():
            raise ValueError("build artifacts must not be symlinks")
        shutil.copy2(source, temporary)
        temporary.replace(target)
    check_navigation(output / f"{course}.pdf", cache, "main", cache / "main.aux", source=main)
    print(output / f"{course}.pdf")


def fingerprint(root: Path) -> dict[str, tuple[int, str]]:
    result = {}
    for path in sorted(root.rglob("*")):
        if path.is_symlink():
            raise ValueError("migration refuses symlinks")
        digest = hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else "directory"
        result[str(path.relative_to(root))] = (stat.S_IMODE(path.stat().st_mode), digest)
    return result


def migrate(source: Path, destination: Path, workspace: Path, writers_stopped: bool) -> None:
    """Move one stopped repository as a unit; keep history and dirty files intact."""
    if not writers_stopped:
        raise ValueError("migration requires confirmed stopped writers and --writers-stopped")
    source = location(source, workspace)
    destination = location(destination, workspace)
    validate(source, workspace)
    if source == destination or destination.exists():
        raise ValueError("migration destination must not exist")
    if not destination.parent.is_dir() or source.stat().st_dev != destination.parent.stat().st_dev:
        raise ValueError("migration needs an existing parent on the same filesystem; no duplicate live copy is made")
    before = fingerprint(source)
    configuration = (source / "materials/.git/config").read_bytes()
    # rename is atomic on this filesystem; only Git's absolute hooks path changes.
    source.rename(destination)
    try:
        if fingerprint(destination) != before:
            raise ValueError("migration content/mode verification failed")
        hooks = destination / "materials/.git/hooks"
        run("git", "config", "--local", "core.hooksPath", str(hooks), cwd=destination / "materials")
        validate(destination, workspace)
    except Exception:
        (destination / "materials/.git/config").write_bytes(configuration)
        destination.rename(source)
        raise
    print(f"Moved verified local materials to {destination}")
    print("Update private navigation and absolute source/build paths, then rebuild PDF/SyncTeX and check synchronization before resuming writers.")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=["install", "check", "build", "migrate"])
    parser.add_argument("--root", type=Path, help="default: <workspace>/local")
    parser.add_argument("--from-root", type=Path, help="existing stopped materials root, for migrate only")
    parser.add_argument("--writers-stopped", action="store_true", help="assert writers were explicitly confirmed stopped")
    parser.add_argument("--workspace", type=Path, required=True)
    parser.add_argument("--course")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    args.root = args.root or args.workspace.resolve() / "local"
    try:
        if args.mode == "migrate":
            if not args.from_root:
                raise ValueError("migrate requires --from-root")
            migrate(args.from_root, args.root, args.workspace, args.writers_stopped)
        elif args.mode == "install":
            install(args.root, args.workspace)
        elif args.mode == "check":
            validate(args.root, args.workspace)
        else:
            if not args.course:
                raise ValueError("build requires --course")
            build(args.root, args.workspace, args.course, args.dry_run)
    except (OSError, ValueError, PrivacyError, subprocess.CalledProcessError) as exc:
        print(f"Book materials: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
