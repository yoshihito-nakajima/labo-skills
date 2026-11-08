---
name: labo-build
description: Compile TeX documents in writing/ or reading/ into PDF and SyncTeX outputs named after the project slug and the root, overwrite prior results, and prune old outputs against a file-count limit.
---

# TeX build

Luna and Haiku only collect evidence here and hand substantive work to another agent: [roles](../research-router/references/editing-capability.md).

When author identity, voice, or preferences matter, consult the Labo workspace
[author profile](../../../profile/author-identity.md) when available. Keep
personal facts there rather than in skill text; update only explicit durable
facts or corrections from the user, or facts they ask to save, with source
context. Apply this skill's normal verification rules.

Read [build contract](references/build-contract.md) before running compilation.
Book-derived courses under `local/materials/` (or a user-selected external root) use [reading-book](../reading-book/SKILL.md) and `scripts/book_materials.py`; do not pass their roots to the writing/reading CLI.
`<labo-script>` is the checkout-local launcher `scripts/labo.py` of this policy checkout: from the workspace root it is
`.agents/scripts/labo.py` (or the same file through the `.claude` mount). Use it rather than a globally installed `labo`
command. It finds the workspace from its own location, so neither the working directory nor an absolute path matters;
`--workspace <dir>` (relative or absolute) is only for overriding that or for a standalone policy checkout. Use
`python3 <labo-script> output build --paper <slug> [--engine pdflatex]`
for the standard `writing/<slug>/main.tex` layout. For any TeX document root
under `writing/<slug>/` or `reading/<slug>/`, use
`output build --source <document-root.tex>`; this detects engine requirements
and writes one current PDF/SyncTeX pair named after the root: its own file stem
when that begins with the project slug, otherwise `<slug>-<stem>`; a root called `main.tex` is the
project's main document and takes the slug. A later build
of the same root overwrites its pair; other roots of the project keep theirs.
Successful builds prune old managed outputs
toward a 30-file limit, warning when protected or unrecognized files keep the
count higher. The viewer stays closed unless `--open` is supplied; use
`--max-files <count>` to change the limit or `output prune --max-files <count>`
to clean the directory without a build. The build contract explains working
directories and artifact names.
The launcher uses the private Git superproject, not the shell's current
directory. No project installation is required.

Keep selectable PDFs directly in `output/`, with same-stem SyncTeX beside them.
Each document root writes its own pair (see the naming rule above), so a project can
hold several, for example a translation and an explanation, without one
overwriting the other. Intermediate files stay beside each source in `.temp/`.

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
