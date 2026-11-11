---
name: labo-layout
description: Initialize a labo research workspace, start or resume research with the current exploration-tree layout, and create or locate research, manuscript, and reference files while preserving existing material.
---

# Create and use a research workspace

Luna and Haiku only collect evidence here and hand substantive work to another agent: [roles](../research-router/references/editing-capability.md).

When author identity, voice, or preferences matter, consult the Labo workspace
[author profile](../../../profile/author-identity.md) when available. Keep
personal facts there rather than in skill text; update only explicit durable
facts or corrections from the user, or facts they ask to save, with source
context. Apply this skill's normal verification rules.

Use for requests such as 「研究室を初期化して」「inboxのこれで研究したい」
or 「この資料・原稿はどこに置く？」. Read the [directory contract](references/layout.md).
For creation commands and their effects, read [workspace creation](references/creation.md).
For reference placement and Git operations, also follow
[source and corpus privacy](references/reference-privacy.md). Both `reference/`
and `writing/.corpus/`, including corpus registration metadata, stay outside
the parent Git; any local history has no remotes and all pushes are prohibited.
GitHub operations follow [labo-git's publication boundary](../labo-git/SKILL.md#publication-boundary):
only the independent policy Git is eligible for push/PR by default; everything
else remains local. Trackability for local history never grants upload permission.

Resolve the workspace from the loaded policy submodule's Git superproject,
or use the user's explicit destination. Resolve `scripts/labo.py` from this
skill's real directory (`../../scripts/labo.py`), not from the shell's cwd.
Inspect the relevant existing paths before writing; the directory need not
be named `labo`. A placement question alone needs an answer, not scaffolding.
For a layout-display request, show the [complete workspace skeleton](references/layout.md)
including workspace-internal `local/`, its no-Git original/books/topics and review roles, and the preserved legacy materials Git boundary. Inspect existing paths and distinguish the actual
layout from illustrative or absent branches. Display-only work does not create
directories, move files, or change Git settings.

## Initialize

When asked to set up the workspace, run `layout init`. It adds missing core
directories, the workspace-level `writing/.corpus/` and `writing/.rules/`
guides, an empty `AGENTS.md` only if absent, and missing workspace ignore
patterns. Existing corpus entries, rules, files, and personal instructions
stay intact. Root `inbox/` contents are local staging; assigned originals under
research-specific inboxes remain trackable.
The normal setup is **fork `labo-skills`, then mount the user's fork at
`.agents` as a submodule**. Installation steps are in the creation reference.
If already connected, use that checkout; it is where the user develops their
own improvements and optional upstream contributions.

## Start or resume research

The current research layout includes `plan.md`, `inbox/` and an empty
`exploration/tree.json` by default. The tree's `schema_version` identifies its
structure; no extra style field in the plan or claim catalog is required.
An existing program without a tree simply has no exploration tree. Its claims
and research status retain their original meanings.

When accepting plan edits or mathematical exploration in an existing program,
follow [safe research-layout migration](references/research-migration.md) as
part of that work, without asking for separate migration permission. Reuse and
check an existing tree; initialize a missing one, then add or reuse only the
current scoped work node. Read-only inventories, explanations, report-only
reviews and checks preserve the existing layout. A directory placement question
alone still authorizes no writes. `layout init` does not scan or migrate programs.

For an inbox-based research request:

1. Read the selected sources, preserving their original bytes. Inventory
   existing programs with `research list --format json` when `research/`
   exists, then read the relevant plans. Relate new input to the existing
   question before deciding whether a new program is needed.
2. Use `research-management` for the research story and evidence. A request
   to start research authorizes creating the necessary program; do not ask
   for a skill name or repeat permission. Ask only if an unresolved choice
   would substantially change the research direction. Propose splits or
   mergers of existing programs before changing their boundaries.
3. For a new program, use `layout new research` with a meaningful title and
   summary grounded in the material. It creates the empty exploration tree
   through the shared exploration initializer; create `claims.yaml` when
   registering concrete claims. Fill the generated `plan.md` body with
   the question, context, current evidence, open issues, and first concrete
   investigation. A template alone does not complete an intake request.
4. Store assigned originals in `research/<slug>/inbox/`; check for name
   collisions and preserve bytes when moving or copying. Record their origin
   in the plan. If one source serves several programs, keep one original and
   link to it. Keep imported AI proposals distinguishable from verified results.
5. Run `research check`, then continue the requested investigation from the
   recorded next step. For an existing program, update its current story;
   do not create a new program merely because another file arrived.

## Place other work

Use `layout new paper` or `layout new reference` when a new item is needed.
Creating a paper also initializes the shared writing corpus and rules guides
when they are missing and appends `/writing/.corpus/` to the parent ignore
rules even without a prior `layout init`. Reference creation likewise ensures
`/reference/` is ignored. Create reading notes under `reading/<slug>/` with `layout new reading`, one directory per source
([layout](references/layout.md#one-source-one-reading-directory)), formalizations
under `lean/`, and optional website/profile material only when those tasks
arise. The directory contract explains their relationships; output slugs need
not match programs.
For local courses and long notes, use [course-authoring](../course-authoring/SKILL.md) and its workspace-internal local layout; add [reading-book](../reading-book/SKILL.md) for book-led source tracking; ordinary reading notes still use `reading/`. When creating or relocating such a course, follow its [local navigation rule](../reading-book/references/layout.md#workspace-からの案内) so the workspace has an entry to the local materials and output.
Layout creation supplies paths and templates, not mathematical validation or
permission to publish. Read the owning skill when doing the substantive work.

Keep operational rules in the policy checkout. Leave the user's `AGENTS.md`
content and existing research intact. Do not copy policy READMEs into private
data, bulk-migrate old `doc` papers, or change Git privacy settings as setup.
