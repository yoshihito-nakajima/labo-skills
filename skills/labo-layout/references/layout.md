# Directory contract (layout only)

The tree is an example of the **whole workspace layout**. When showing an existing workspace, inspect which branches actually exist and label absent or optional branches.

```text
<parent>/
  labo/
    AGENTS.md                 # initially empty, user-owned
    .agents/                 # Git submodule: researcher's public policy fork
      skills/                # directly discoverable skills, rules and templates
      scripts/labo.py         # run the tools from this checkout
      src/                   # shared tool implementation
    research/<slug>/
      plan.md                 # narrative plan + YAML index
      inbox/                  # originals submitted for this research
      claims.yaml             # optional scoped evidence catalog; not initialized
      reviews/                # optional private review records and reports
      exploration/tree.json   # standard for new/resumed work; schema_version identifies structure
      exploration/notes/       # optional scoped investigation records
    inbox/                    # local staging; contents are gitignored until assigned
    lean/                     # mathematical formalizations
    writing/<paper>/
      main.tex                # canonical English TeX root
      sections/NN-name.tex    # separately reviewable sections
      ja/                     # optional translation checking, non-authoritative
      .temp/                  # ignored build cache
    writing/.corpus/          # local-only shared corpus and index; excluded from parent Git
      README.md
      index.md
    writing/.rules/           # workspace-level, user-maintained writing rules
      README.md
    reading/                  # lecture notes, literature notes, derived exposition
    reference/<key>/          # local-only source Git; excluded from parent Git
    output/                  # ignored PDFs + same-stem SyncTeX, directly selectable
    website/                  # optional source pages/config
    profile/                  # author identity plus optional CV/presentation/event records
    local/                   # workspace-internal, entire /local/ ignored by parent; no own Git
      originals/              # optional new raw books, outside materials Git
      cache/                  # page images, OCR and TeX cache, outside materials Git
      output/                 # course PDF and SyncTeX, outside materials Git
      materials/              # the only independent Git under this root; no remote, push denied
        .git/
        sources/              # source identities, editions and locations
        catalog/              # mathematical claims, dependencies and review scope
        shared/               # mathematics actually reused across courses
        courses/<course>/
          START_HERE.md       # handoff when this course has one
          plan.md             # learning order and source roles
          progress.md         # current scope, checks and next work
          main.tex            # canonical lecture root
          chapters/           # one canonical mathematical body
          notes/              # local working notes
        retired/              # old drafts kept distinct from current bodies
```

Each user normally forks the shared `labo-skills` repository and mounts
their fork at `.agents`. The fork submodule is the policy/runtime boundary. Its `skills/`,
`scripts/`, and `src/` remain inside its own Git history; research-program data stays
in `labo/`, while book-derived course materials use `labo/local/materials/`,
whose independent local Git never goes to GitHub. Originals, cache and output
remain under `local/` but outside materials Git. The parent excludes all `/local/`.
The parent tracks the user's fork URL in `.gitmodules` and
the selected policy commit, which may include changes not yet accepted upstream.
Anything committed inside `.agents` belongs to the policy repository, including
additional personal skills. Keep private-only skills outside that public Git
history, using a host-supported location selected by the user. Do not generate
extra links or host configuration as part of workspace initialization.

Run tools from this checkout's `scripts/labo.py`, not a separately installed
`labo` executable. Git identifies the private superproject; an explicit
`--workspace` overrides it. An unrelated standalone checkout needs that
explicit workspace. The default mount places the real skills directly under
`.agents/skills/`; no discovery links are needed. Existing mounts elsewhere
can still run the launcher, but require their own host discovery arrangement.
Do not create `vendor/`,
generated forwarding skills, or private README policy copies.

The same policy checkout can be mounted at `.claude` or another chosen path;
only the host's discovery setup and the launcher path differ. Its reusable
formats, templates, checks, and tests remain authoritative at that location.
Private catalogs and reports follow the owning
[evidence protocol](../../research-management/references/evidence.md). They
are optional research artifacts, not host-side implementations of the harness;
layout initialization does not create them.

`layout new research` creates an empty exploration tree by default. Existing
programs gain that structure when accepted plan-editing or exploration work
needs it, following [safe migration](research-migration.md). A program without
a tree retains its plan, claims and proof statuses; inventories and report-only
work do not write one. Structure and Lean-evidence status are independent.

`research/`, `lean/`, `writing/`, `reading/`, and `reference/` may reference
one another using relative links or identifiers but do not have to share the
same slug. A research program may produce several papers, talks, and notes;
one output may draw from several programs. In particular **do not make an
output document the owner of a research program**.

`writing/.corpus/` and `writing/.rules/` belong to the workspace rather than
to an individual paper. The corpus points to author samples, field exemplars,
and venue sources; its observations inform style softly. Rules state user-
adopted requirements with an explicit scope. Detailed selections stay in local `writing/.corpus/selections/<document>/corpus.toml`.
A paper may keep only minimal adopted nonconfidential rules in its tracked
`decisions/corpus.toml`; exclude corpus IDs, paths, excerpts and provenance.
The corpus serves reading and writing and does not impose stylistic requirements.
Follow [source and corpus privacy](reference-privacy.md) for its independent,
remote-free local Git and parent exclusion.

Keep the research plan's YAML frontmatter short: required `title`, `summary`,
`status`; optional `tags`, `next`. The full argument, transitions, hypotheses,
and open questions belong in Markdown prose. Status is only `in_progress` or
`completed`.

Put unclassified material in the root `inbox/`, a local staging area whose
contents are ignored by default. Once assigned, preserve its original bytes in
`research/<slug>/inbox/` and make interpreted notes elsewhere. Do not replace
originals with an AI-generated summary. Research-specific inboxes retain their
source originals. Reference stores containing arXiv sources, publication
PDFs, metadata and versions are local-only: exclude `/reference/` from the
parent Git. When local history is requested, use an independent Git without
remotes and with a deny-all pre-push hook, never a submodule. See
[reference privacy](reference-privacy.md) before source placement or Git operations. Ignore generated files by their
`output/` and `.temp/` locations rather than by a blanket `*.pdf` rule.

The `output/` directory is build output, not the canonical manuscript or an
archive of historic papers. In the current CLI convention,
`writing/<paper>/main.tex` is the assembly file: use literal top-level
`\input{sections/NN-name}` or `\include{sections/NN-name}` entries in intended
exposition order. Each section marks the end of its opening with
`% LABO:INTRO-END`. The local reader does not evaluate dynamic TeX includes.

Book-derived courses use the [reading-book local materials layout](../../reading-book/references/layout.md), with `materials/` as its own local-only Git under workspace `local/`. This exception does not change placement for ordinary `reading/` notes or research-specific source inboxes.

When a book-derived course is created or moved, the owning [reading-book navigation rule](../../reading-book/references/layout.md#workspace-からの案内) keeps a local `reading/` entry linked to its local canonical text, output and progress. Check ignore and tracking before writing actual course details; ordinary reading notes and display-only layout requests do not create these private indexes.
