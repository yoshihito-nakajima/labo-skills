"""Invoke latexmk with isolated aux files and output PDF/SyncTeX artifacts."""

from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
from typing import Iterator

from .locking import exclusive_lock
from .paper import PaperError, paper_folder


ENGINE_FLAGS = {
    "pdflatex": "-pdf",
    "lualatex": "-lualatex",
    "xelatex": "-xelatex",
    "uplatex": "-pdfdvi",
}
DEFAULT_OUTPUT_MAX_FILES = 30
_OUTPUT_LOCK_NAME = ".labo-output.lock"


@dataclass(frozen=True)
class OutputPruneResult:
    removed: tuple[str, ...]
    file_count: int
    max_files: int

    @property
    def over_limit(self) -> bool:
        return self.file_count > self.max_files


@contextmanager
def output_transaction(workspace: Path) -> Iterator[Path]:
    """Serialize builds and cleanup that mutate the shared output directory."""
    workspace = workspace.resolve()
    output = workspace / "output"
    if output.is_symlink():
        raise PaperError("output directory must not be a symlink")
    output.mkdir(parents=True, exist_ok=True)
    lock_path = workspace / _OUTPUT_LOCK_NAME
    if lock_path.is_symlink():
        raise PaperError("output lock must not be a symlink")
    # Retain the lock file: unlinking it can split waiters over different inodes.
    with lock_path.open("a+b") as lock_file:
        with exclusive_lock(lock_file):
            yield output


def _output_files(output: Path) -> list[Path]:
    return [
        path for path in output.iterdir()
        if path.is_file() or path.is_symlink()
    ]


def prune_output(
    output: Path, max_files: int = DEFAULT_OUTPUT_MAX_FILES,
    *, protected_stems: set[str] | None = None,
    superseded_prefixes: set[str] | None = None,
) -> OutputPruneResult:
    """Remove oldest known PDF/SyncTeX groups; caller must hold output_transaction."""
    if max_files < 2:
        raise PaperError("--max-files must be at least 2 to retain a PDF and SyncTeX")
    if output.is_symlink() or not output.is_dir():
        raise PaperError("output must be a real directory")

    files = _output_files(output)
    groups: dict[str, list[Path]] = {}
    for path in files:
        if path.is_symlink():
            continue
        name = path.name
        if name.endswith(".synctex.gz"):
            stem = name[:-len(".synctex.gz")]
        elif name.endswith(".synctex"):
            stem = name[:-len(".synctex")]
        elif name.endswith(".pdf"):
            stem = name[:-len(".pdf")]
        else:
            continue
        groups.setdefault(stem, []).append(path)

    protected = protected_stems or set()
    superseded = superseded_prefixes or set()
    removed: list[str] = []
    file_count = len(files)
    for stem, members in groups.items():
        if stem in protected or not any(stem.startswith(prefix) for prefix in superseded):
            continue
        for path in members:
            try:
                path.unlink()
            except FileNotFoundError:
                continue
            removed.append(path.name)
            file_count -= 1

    candidates = sorted(
        (
            max(path.stat().st_mtime for path in members), stem, members
        )
        for stem, members in groups.items()
        if stem not in protected
        and not any(stem.startswith(prefix) for prefix in superseded)
    )
    for _, _, members in candidates:
        if file_count <= max_files:
            break
        for path in members:
            try:
                path.unlink()
            except FileNotFoundError:
                continue
            removed.append(path.name)
            file_count -= 1

    return OutputPruneResult(tuple(removed), file_count, max_files)


def _is_wsl() -> bool:
    if os.environ.get("WSL_INTEROP"):
        return True
    try:
        release = Path("/proc/sys/kernel/osrelease").read_text(encoding="utf-8")
    except OSError:
        return False
    return "microsoft" in release.casefold()


def open_default_viewer(pdf: Path) -> str | None:
    """Ask the host system's default handler to open the built PDF."""
    try:
        if os.name == "nt":
            os.startfile(str(pdf))  # type: ignore[attr-defined]
        elif sys.platform == "darwin":
            subprocess.Popen(
                ["open", str(pdf)], stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                start_new_session=True,
            )
        elif _is_wsl():
            wslview = shutil.which("wslview")
            if wslview:
                command = [wslview, str(pdf)]
            else:
                wslpath = shutil.which("wslpath")
                cmd = shutil.which("cmd.exe")
                if not wslpath or not cmd:
                    return "WSL needs wslview or both wslpath and cmd.exe to open the Windows default viewer"
                converted = subprocess.run(
                    [wslpath, "-w", str(pdf)], check=True,
                    capture_output=True, text=True,
                )
                windows_path = converted.stdout.strip()
                if not windows_path:
                    return "wslpath returned an empty Windows path for the PDF"
                command = [cmd, "/c", f'start "" "{windows_path}"']
            subprocess.Popen(
                command, stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                start_new_session=True,
            )
        else:
            subprocess.Popen(
                ["xdg-open", str(pdf)], stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                start_new_session=True,
            )
    except (AttributeError, OSError, subprocess.CalledProcessError) as exc:
        return f"could not open the default PDF viewer: {exc}"
    return None


def _engine_options(engine: str | None) -> list[str]:
    if engine is None:
        return []  # Honor the workspace's latexmk configuration.
    if engine not in ENGINE_FLAGS:
        raise PaperError(f"unsupported engine: {engine}")
    options = [ENGINE_FLAGS[engine]]
    if engine == "uplatex":
        options += ["-e", "$latex = 'uplatex %O %S'; $bibtex = 'upbibtex %O %B'; $dvipdf = 'dvipdfmx %O -o %D %S';"]
    return options


def _nonempty_file(path: Path) -> bool:
    return path.is_file() and path.stat().st_size > 0


def _has_synctex(output: Path, stem: str) -> bool:
    return any(
        _nonempty_file(output / f"{stem}{suffix}")
        for suffix in (".synctex.gz", ".synctex")
    )


def build_command(workspace: Path, paper: str, engine: str) -> tuple[list[str], Path, Path, Path]:
    if engine not in ENGINE_FLAGS:
        raise PaperError(f"unsupported engine: {engine}")
    workspace = workspace.resolve()
    folder = paper_folder(workspace, paper)
    main = folder / "main.tex"
    if main.is_symlink() or not main.is_file():
        raise PaperError(f"missing or symlinked main.tex: writing/{paper}")
    cache = folder / ".temp"
    output = workspace / "output"
    artifacts = [output / f"{paper}{suffix}" for suffix in (".pdf", ".synctex.gz", ".synctex")]
    if any(path.is_symlink() for path in (cache, output, *artifacts)):
        raise PaperError("build paths must not be symlinks")
    command = [
        "latexmk",
        *_engine_options(engine),
        "-synctex=1",
        "-interaction=nonstopmode",
        "-halt-on-error",
        f"-jobname={paper}",
        f"-auxdir={cache}",
        f"-outdir={output}",
        "main.tex",
    ]
    return command, folder, cache, output


def _compile(command: list[str], cwd: Path, generated: Path, stem: str) -> None:
    try:
        subprocess.run(command, cwd=cwd, check=True)
        if _nonempty_file(generated / f"{stem}.pdf") and not _has_synctex(generated, stem):
            # Recover missing SyncTeX even when latexmk reuses a cached PDF.
            subprocess.run([command[0], "-g", *command[1:]], cwd=cwd, check=True)
    except FileNotFoundError as exc:
        raise PaperError("latexmk executable not found") from exc
    except subprocess.CalledProcessError as exc:
        raise PaperError(f"latexmk failed (exit {exc.returncode})") from exc
    if not _nonempty_file(generated / f"{stem}.pdf"):
        raise PaperError("latexmk finished without producing a nonempty output PDF")
    if not _has_synctex(generated, stem):
        raise PaperError("latexmk finished without producing SyncTeX, including after one forced rebuild")


def run_build(workspace: Path, paper: str, engine: str, dry_run: bool) -> list[str]:
    command, cwd, cache, output = build_command(workspace, paper, engine)
    if not dry_run:
        cache.mkdir(parents=True, exist_ok=True)
        output.mkdir(parents=True, exist_ok=True)
        _compile(command, cwd, output, paper)
    return command


def source_build_command(
    workspace: Path, source: Path, engine: str | None = None,
) -> tuple[list[str], Path, Path, Path, str]:
    """Build an explicit document root, including imported source layouts."""
    workspace = workspace.resolve()
    source = source if source.is_absolute() else workspace / source
    if source.is_symlink() or not source.is_file() or source.suffix != ".tex":
        raise PaperError("source must be an existing, non-symlinked .tex file")
    try:
        relative = source.resolve().relative_to(workspace)
    except ValueError as exc:
        raise PaperError("source must be inside the workspace") from exc
    if len(relative.parts) < 3 or relative.parts[0] not in {"writing", "reading"}:
        raise PaperError("source must be under writing/<slug>/ or reading/<slug>/")
    if any(p.is_symlink() for p in source.parents if p != workspace and workspace in p.parents):
        raise PaperError("source directories must not be symlinks")
    source = source.resolve()
    preamble = source.read_text(encoding="utf-8").split(r"\begin{document}", 1)[0]
    if not re.search(r"\\documentclass\b", preamble):
        raise PaperError("source must be the document root, not an included section")
    if engine is None:
        directive = re.search(r"(?im)^\s*%\s*!TEX\s+(?:TS-)?program\s*=\s*([\w-]+)", preamble)
        if directive:
            engine = directive.group(1).lower()
        elif "xeCJK" in preamble:
            engine = "xelatex"
        elif any(word in preamble for word in ("luatexja", "fontspec", "{ltj")):
            engine = "lualatex"
        elif not (workspace / ".latexmkrc").is_file():
            engine = "pdflatex"
    slug = relative.parts[1]
    if source.name == "main.tex" and len(relative.parts) == 3 and relative.parts[0] == "writing":
        command, cwd, cache, output = build_command(workspace, slug, engine or "pdflatex")
        return command, cwd, cache, output, slug
    stem = source.stem if source.stem.startswith(slug) else f"{slug}-{source.stem}"
    cache, output = source.parent / ".temp", workspace / "output"
    artifacts = [output / f"{slug}{suffix}" for suffix in (".pdf", ".synctex.gz", ".synctex")]
    if any(p.is_symlink() for p in (cache, output, *artifacts)):
        raise PaperError("build paths must not be symlinks")
    command = ["latexmk", *_engine_options(engine), "-synctex=1",
               "-interaction=nonstopmode", "-halt-on-error", "-file-line-error",
               f"-jobname={stem}", f"-outdir={cache}", str(source)]
    return command, workspace, cache, output, stem


def run_source_build(
    workspace: Path, source: Path, engine: str | None, dry_run: bool,
) -> tuple[list[str], str]:
    command, cwd, cache, output, stem = source_build_command(workspace, source, engine)
    workspace = workspace.resolve()
    source_path = source if source.is_absolute() else workspace / source
    relative = source_path.resolve().relative_to(workspace)
    output_stem = relative.parts[1]
    if not dry_run:
        cache.mkdir(parents=True, exist_ok=True)
        output.mkdir(parents=True, exist_ok=True)
        generated = output if any(arg == f"-outdir={output}" for arg in command) else cache
        _compile(command, cwd, generated, stem)
        if generated != output:
            # Publish the pair only after compilation and both artifact checks.
            for suffix in (".pdf", ".synctex.gz", ".synctex"):
                artifact = generated / f"{stem}{suffix}"
                if _nonempty_file(artifact):
                    shutil.copy2(artifact, output / f"{output_stem}{suffix}")
            if not _nonempty_file(output / f"{output_stem}.pdf") or not _has_synctex(output, output_stem):
                raise PaperError("published output is missing its PDF or SyncTeX")
    return command, output_stem
