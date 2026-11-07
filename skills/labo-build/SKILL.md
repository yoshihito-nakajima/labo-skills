---
name: labo-build
description: Compile TeX documents in writing/ or reading/ into slug-named PDF and SyncTeX outputs, overwrite prior results, and prune old outputs against a file-count limit.
---

# TeX build

Before substantive work, follow [eligibility and handoff](../research-router/references/editing-capability.md).

For each user request, follow the [required consultation](../research-router/references/consultation.md).

When author identity, voice, or preferences matter, consult the Labo workspace
[author profile](../../../profile/author-identity.md) when available. Keep
personal facts there rather than in skill text; update only explicit durable
facts or corrections from the user, or facts they ask to save, with source
context. Apply this skill's normal verification rules.

Read [build contract](references/build-contract.md) before running compilation.
Book-derived courses under `local/materials/` (or a user-selected external root) use [reading-book](../reading-book/SKILL.md) and `scripts/book_materials.py`; do not pass their roots to the writing/reading CLI.
Resolve `<labo-script>` to the absolute `../../scripts/labo.py` path relative
to this skill's **real directory** (follow symlinks first). Use
`python3 <labo-script> output build --paper <slug> [--engine pdflatex]`
for the standard `writing/<slug>/main.tex` layout. For any TeX document root
under `writing/<slug>/` or `reading/<slug>/`, use
`output build --source <document-root.tex>`; this detects engine requirements
and writes one current PDF/SyncTeX pair named `<slug>` for that project,
overwriting the pair on each build while keeping source-specific cache names.
Successful builds prune old managed outputs
toward a 30-file limit, warning when protected or unrecognized files keep the
count higher. The viewer stays closed unless `--open` is supplied; use
`--max-files <count>` to change the limit or `output prune --max-files <count>`
to clean the directory without a build. The build contract explains working
directories and artifact names.
The launcher uses the private Git superproject, not the shell's current
directory; pass `--workspace /absolute/path/to/labo` to override it or when
using a standalone policy checkout. No project installation is required.

Keep selectable PDFs directly in `output/`, with same-stem SyncTeX beside them.
Every document root under the same project slug writes the same output pair, so
the most recently built root is the one available from `output/`. Intermediate
files stay beside each source in `.temp/`.

After producing the current artifact, the build runs the shared
[PDF navigation check](../mathematical-navigation/references/pdf-checks.md)
and saves its report in the source's existing cache. Surface failures and
incomplete checks separately from compilation; keep the produced artifacts and
continue unrelated writing. Structural results do not certify rendering,
viewer behavior, index coverage or mathematics. Use the shared procedure for
changed-page inspection and representative viewer checks, rather than repeating
every GUI click after each build.

A failed build keeps the previous PDF in `output/`. Steps that rewrite the PDF after a
successful build go through `--postprocess` so they are recorded. Before checking or
reporting on that PDF, run `output verify-current` as described in the
[build contract](references/build-contract.md#current-build-check); a check of a stale PDF
is not a result.

Do not use a global TeX build directory, commit generated PDFs or caches,
or treat a successful build as a mathematical review. On failure inspect only
the necessary local log/errors; do not delete source material or silently
rewrite the paper.
