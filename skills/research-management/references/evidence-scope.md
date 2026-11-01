# Diagnose a selected TeX evidence scope

- [Select the source and optional comparison](#select-the-source-and-optional-comparison)
- [Supported discovery grammar](#supported-discovery-grammar)
- [What remains unresolved](#what-remains-unresolved)

Use `evidence scope` to find likely gaps between a TeX source's literal local
inputs and the actual evidence members selected for a review. This is a
read-only diagnostic, not a dependency-completeness certificate, TeX execution,
freshness approval, or mathematical review. It does not inspect the truth of a
claim or whether a reviewer actually read a file. An `ok` result means only that
the supported diagnostics found no issue.

The loaded policy checkout owns this reference and the implementation in
`src/labo_tools/evidence_scope.py`. Resolve `<labo-script>` to the absolute
`../../scripts/labo.py` path from the real `research-management` skill directory.
Do not copy the resolver into the private research workspace or substitute an
unrelated installed executable. The same code serves writing sources, reading
sources, and other explicitly selected TeX roots inside the host workspace.

## Select the source and optional comparison

```sh
python3 <labo-script> evidence scope --paper example --format json
python3 <labo-script> evidence scope --source reading/example/source/main.tex
python3 <labo-script> evidence scope --source reading/example/source/main.tex \
  --compile-root .
python3 <labo-script> evidence scope --paper example \
  --record research/example/reviews/writing.yaml --strict
python3 <labo-script> evidence scope --paper example \
  --file writing/example/main.tex --tree writing/example/sections
```

Choose exactly one of `--paper SLUG` (meaning `writing/SLUG/main.tex`) and
`--source PATH`. Source and selected evidence paths are normalized,
workspace-relative POSIX paths; the shell's current directory is irrelevant.
UTF-8 filenames, including spaces, are supported. Absolute paths, drive-qualified
paths, workspace escape, symlinked inputs or ancestors, and inputs entering the
policy checkout are rejected. Missing or unreadable selected roots are errors.

By default the diagnostic uses the source's parent as its compilation-root
candidate. When the real build runs elsewhere, pass `--compile-root DIR`: an
existing normalized workspace-relative directory, with the special value `.`
meaning the workspace root. The same path-safety rules apply; symlinks, escapes,
absolute/drive-qualified paths, and policy-checkout directories are rejected.
For workspace-root builds such as named `output build --source` sources,
`--compile-root .` permits literal workspace-root input paths. Choosing a root
does not prove the build actually uses it or certify complete discovery.

Without `--record`, `--file`, or `--tree`, the command only discovers inputs; it
does not invent a selected scope or issue omitted-member warnings. Repeat
`--file` and `--tree` for the intended comparison, or choose one `--record`.
Do not combine record and explicit-file/tree comparisons.

For explicit scopes, `--tree` uses the evidence protocol's ordinary-file
inventory and cache exclusions. A literal input under an excluded directory can
still be discovered, but requires an explicit `--file` to count as covered.
Discovery does not silently add that file to the selected scope.

For record comparison:

- File coverage comes from actual recorded `files` keys.
- Tree coverage comes from actual recorded member keys, **not** from a directory
  prefix. A new input added under a recorded tree is omitted until it belongs to
  a newly authorized review snapshot.
- Claim evidence coverage can be reconstructed from the selected catalog only
  when the current complete transitive claim fingerprint exactly matches the
  recorded fingerprint. This includes claim evidence, owner-confirmation inputs,
  and formal-project inputs. A changed or unavailable claim cannot be assumed to
  have contained today's evidence paths: the historical claim hash does not
  encode a recoverable member list. Such scope remains unresolved.
- Changed/unavailable recorded files are reported; record membership is not
  treated as approval of current bytes. Scope inspection is not a replacement
  for `evidence check`, which also checks record/report/policy freshness and
  verdict metadata.

## Supported discovery grammar

The reader scans UTF-8 sources for these simple braced literal commands:

| Commands | Inputs |
| --- | --- |
| `\input{path}`, `\include{path}` | TeX files; append `.tex` when no extension is present |
| `\includegraphics{path}` | An explicit extension, or a unique local `.pdf`, `.png`, `.jpg`, `.jpeg`, `.eps`, `.ps`, `.svg`, or `.mps` variant |
| `\bibliography{one,two}`, `\addbibresource{path}` | Bibliography files; append `.bib` when no extension is present |
| `\documentclass{class}`, `\LoadClass{class}` | Local `.cls` files |
| `\usepackage{one,two}`, `\RequirePackage{one,two}` | Local `.sty` files |

A single simple optional bracket argument and an optional star are accepted
before the braced filename. Filenames cannot contain nested braces, TeX macro
controls, or the active/special tokens `#`, `$`, `^`, `~`, `%`. Package lists and
the traditional bibliography command split on literal commas. This is not a
general TeX argument parser.

Only TeX, local class, and local style inputs are recursively scanned; graphics
and bibliography files are listed without interpreting their contents. Each
discovered edge includes the referring path, original argument, kind, and
one-based line number. Repeated references retain their provenance. The source
root itself is an input. Cycles are explicit unresolved items, not infinite
recursion.

The explicit `--compile-root`, or otherwise the source root's parent, is the
diagnostic's declared **compilation-root candidate**; this does not prove that a
build actually runs there. Both this base and the referring source's parent are
checked, even with an explicit root. If they
give different existing paths, or multiple graphic variants exist, the reference
is ambiguous: no candidate is arbitrarily selected or traversed. If only a
source-relative candidate exists, it is listed and traversed conservatively but
remains explicitly unresolved, because ordinary TeX compilation-root semantics
have not been confirmed. Such discovery is not evidence that the build uses it.
Relative `..` within a literal dependency is normalized only when it remains
inside the workspace; it cannot escape or bypass symlink checks.

Absent local style/class inputs remain unresolved external TeX dependencies.
The command does not inspect the TeX installation, `TEXINPUTS`, package search
paths, engine-dependent graphic preferences, or build-tool configuration.
Absent ordinary literal inputs are errors, not assumed external successes.

Comments are masked with escaped-percent handling. Standard `\verb`/`\Verb`
forms and `verbatim`, `verbatim*`, `Verbatim`, `lstlisting`, `minted`, and `comment`
environments are masked while preserving line numbers. Unterminated verbatim
constructs remain unresolved. Scanning stops at literal `\endinput` or
`\end{document}`; this does not evaluate definitions or control flow.

## What remains unresolved

The reader never expands TeX. Macro-defined/group-dependent filenames,
unbraced `\input`, definitions such as `\def`/`\newcommand`, conditionals,
`\includeonly`, `\graphicspath`, `\DeclareGraphicsExtensions`, import-family
commands, catcode changes, control-sequence construction, Lua, and low-level
file/write operations produce unresolved diagnostics where recognized. Literal
inputs encountered in conditional text can be conservative candidates, not proof
that a branch executes. A macro redefinition can invalidate the meaning of
otherwise recognizable commands. The generic list of recognized hazards is not
an exhaustive audit of TeX's programming language or every package command.

Traversal stops at 256 distinct parsed source files, depth 64, 2 MiB per parsed
source, or 16 MiB total parsed source bytes. Hitting a bound is unresolved, never
a successful completeness result. A literal dependency path is limited to 4096
UTF-8 bytes and 128 components. Inspection reads current bytes, not an atomic
frozen version of concurrently edited files. The command does not compile, execute a
shell, fetch network resources, follow symlinks, scan unrelated workspace trees,
or chase Markdown links, bibliography contents, arbitrary custom commands, or
external package dependencies. Selected evidence tree inventory follows the
existing evidence protocol rather than recursively interpreting its contents.

The JSON result uses `schema_version: 1` and `status: ok|warning|error`, with
`dependencies`, `covered` (including selection provenance), `omitted`,
`suggested_files`, `unresolved`, and structured `issues`. Discovery-only results
have no omitted comparison. Suggestions are paths for a human to evaluate,
not edits or approval. Warnings fail only under `--strict`; errors fail in
either mode. Text and JSON report the same diagnostics.

Resolve ambiguities by inspecting the actual build convention and concrete
inputs within the authorized task. Select additional files only when the real
review needs them, then capture and perform a new scoped review when appropriate.
Never rewrite an old passing snapshot, broaden a review implicitly, infer
mathematical correctness from dependency discovery, or turn an unresolved input
into a silent completeness claim.
