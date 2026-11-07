# Reproducible build contract

For `writing/<slug>/main.tex`, use the absolute checkout-local launcher
resolved in `SKILL.md`:

```sh
python3 <labo-script> output build --paper <slug> --dry-run
python3 <labo-script> output build --paper <slug> --engine pdflatex
```

`latexmk` runs from the paper directory with:

- `-pdf` (or `-lualatex`/`-xelatex`), `-synctex=1`;
- `-auxdir=writing/<slug>/.temp` for logs and intermediate state;
- `-jobname=<slug>` and `-outdir=output` for `<slug>.pdf` and
  `<slug>.synctex.gz`, directly beside all other reading PDFs;
- `-interaction=nonstopmode -halt-on-error` for automated operation.

Directories are passed as absolute paths, so they remain correct regardless
of the launch directory. The source remains canonical. Real compilation needs
the matching TeX distribution and the `latexmk` executable.

Report success only when both a nonempty PDF and SyncTeX are present. If
latexmk reuses a PDF but its SyncTeX is missing, the command forces at most one
rebuild; it does not disable the cache on every run or claim success without
the promised outputs.

Each successful build writes `<slug>.pdf` and same-stem SyncTeX directly under
`output/`. Source roots under one project slug overwrite the same pair; the most
recently built root is the one available from that project. The viewer stays
closed by default; pass `--open` to launch the host's default PDF handler.
After a successful build, the command prunes the oldest managed output groups
toward a 30-file limit. A PDF and its `.synctex.gz` or `.synctex` file are
removed together; known standalone PDFs form one-file groups. The current
build is protected during cleanup. `.gitkeep`, symlinks, and unrecognized files
are preserved, so the command warns when those files prevent reaching the
limit. Use `--max-files <count>` to choose another limit, or
`output prune --max-files <count>` to clean `output/` without compiling. The
internal output lock coordinates build and cleanup commands without adding a
lock file to `output/`. A fixed `.labo-output.lock` in the workspace root is
retained rather than unlinked or replaced, so concurrent waiters share the same
file. POSIX uses `flock`; native Windows uses an exclusive one-byte CRT lock at
offset zero, with interruptible retries on contention. Locking past EOF is
supported, so no seed write or truncation is needed. The lock is released on
normal and exceptional exit; this is coordination between cooperating commands,
not protection against an unrelated program replacing files.

Generated PDFs, SyncTeX files, and caches in these build locations are ignored.
The root `inbox/` is an unassigned local staging area and is ignored by default;
preserve assigned originals in `research/<slug>/inbox/`. Do not ignore all PDF
files by extension: research-specific inboxes and references may contain
trackable source material. Publisher PDFs and arXiv TeX *as input references*
belong in the local-only `reference/<key>/` archive, excluded from the parent
Git and GitHub under the [source privacy rules](../../labo-layout/references/reference-privacy.md). Never
unignore `output/` merely to retain the result of a local build.

## Current-build check

Every build attempt writes `<cache>/<slug>.build.json`: the status (`ok` or `failed`),
the error of a failed build, the source root, the published PDF and, when it succeeded,
the PDF's SHA-256. A failed build leaves the previously published pair in `output/`, so
that PDF is then stale. Before any check that reads the PDF (navigation, rendering,
project verifiers) or any report that the document "passes", run

```sh
python3 <labo-script> output verify-current --source <document-root.tex>
python3 <labo-script> output verify-current --paper <slug>
```

It exits 0 only when the latest build of that target succeeded and `output/` still holds
exactly that PDF; otherwise report the build failure, not the checks.

A step that rewrites the published PDF after a successful build (for example a
normalization) is part of the build: pass it as
`output build --source <document-root.tex> --postprocess "<command>"` (repeatable). It
runs only after a successful build, without a shell, from the workspace, and each step is
recorded with the hashes before and after; a failing step marks the build failed. A
pipeline that must post-process outside the build records the step with
`output record-postprocess --source <document-root.tex> --step <command>`, which is
refused after a failed build.

## Existing source layouts

An imported manuscript may retain its original entry name, repository-root
paths and TeX configuration. Pass the actual document root (not an included
section) as an absolute or workspace-relative path:

```sh
python3 <labo-script> output build --source writing/<slug>/<entry>.tex
python3 <labo-script> output build --source reading/<slug>/<entry>.tex
```

Named source builds run from the workspace root, use source-specific job names
in `.temp/`, and copy the checked PDF/SyncTeX pair to `output/<slug>.*`.
Existing source-derived output variants under `<slug>_` are retired when a
slug-named build replaces them. Standard `writing/<slug>/main.tex` also uses
the project slug as its output name. Do not generate a wrapper or restructure
mathematics just to fit the CLI.

An explicit `--engine` wins, then a `% !TeX program = ...` directive, then
package detection (`xeCJK` before `fontspec`/`luatexja`). Otherwise a named
source build honors the workspace's `.latexmkrc`, or defaults to pdfLaTeX.
Inspect input paths and choose a matching command for layouts with other cwd
requirements. Build upstream inputs first when an
external-document reference requires their auxiliary files. Record the working
command and any missing inputs; preservation is not a claim that every historic
variant was rebuilt. Section-reading tools still require their documented layout.

Editor integrations may invoke `output build --source` with the document root
supplied by their language server. Store host-specific settings in the user's
workspace, not global configuration installed by this skill.

## References and indexes

For mathematical documents, also perform the build-stage checks in
[mathematical-navigation](../../mathematical-navigation/SKILL.md).
When indexes are required, include their generation in the actual build path and
recompile until references and index pages are current. A successful TeX run with
an absent or stale index does not satisfy the artifact requirement.

After the current PDF/SyncTeX pair has been created, run the shared offline
[PDF navigation check](../../mathematical-navigation/references/pdf-checks.md)
on that PDF. The build saves `navigation-<stem>.json` in the existing `.temp/`
cache, using the source-specific build stem. Supply the current auxiliary file
when available; its supported hyperref label forms provide limited additional
expectations. Preserve the prior report for comparison before replacing it.
Source roots can share an output slug, so compare document identity as well as
filename. Document-specific required destinations and routes can be checked
through `<entry>.navigation.json` beside the selected TeX root (for example,
`main.navigation.json` for `main.tex`). Both source and paper builds load it
automatically; absence is reported as requirements not supplied, not verified.
Malformed or unreadable conditions produce a failed/incomplete navigation report.
Rendering comparisons retain a separate `navigation-<stem>.render.json` baseline
under the shared procedure; routine structural builds never replace it.

Report the structural status and report location separately from compilation.
A missing checker dependency, failed check or incomplete coverage stays visible;
retain the PDF/SyncTeX and allow unrelated work to continue. Do not report clean
navigation unless the relevant structural checks passed. Inspect rendered link
colors, index layout and representative equation/theorem/step/index/bookmark
landings under the shared procedure, and record rendering and viewer evidence
separately. A structural diff alone does not establish unchanged page rendering.

## SyncTeX discovery

Keep PDF and SyncTeX together by default. The `synctex view` and `synctex edit`
commands support `-d <directory>` for separate synchronization data, but the
editor/viewer must pass that location as well. Do not separate these files
without checking the user's integration. After relocation, check that forward
and reverse queries still identify the intended source; file existence alone
does not establish working synchronization.

## Local book courses

A book-derived course kept in workspace `local/materials/` (or a user-selected external root) is built with `scripts/book_materials.py build` as specified by [reading-book storage](../../reading-book/references/storage.md). This `output build --source` command accepts only roots inside `writing/<slug>/` or `reading/<slug>/` of the parent workspace. Keep the course PDF and SyncTeX under the materials root's `output/` (`local/output/` by default), with cache under `cache/`, outside materials Git.
