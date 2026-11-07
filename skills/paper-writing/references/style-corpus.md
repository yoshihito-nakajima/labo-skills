# Workspace style corpus and rules

Use the workspace writing corpus to learn from examples while keeping its
observations distinct from instructions.

For mathematical names, symbols and role labels, also apply the shared
[terminology and notation audit](../../reading-reference/references/terminology-audit.md).
Its definition/semantic verification is distinct from the soft style cues
below: compare actual same-role definitions and formulas, preserving valid
alternative conventions and recording missing source evidence. For an existing
manuscript, keep the initial local reader assessment ahead of corpus access.

## Per-task workflow

1. Identify the manuscript's field, target venue, language, and document type.
2. Read `writing/.rules/README.md` and the applicable rule files. For a
   submission-format task, verify the venue's current official instructions and
   template as well.
3. Read `writing/.corpus/README.md` and its index, then select a small number
   of relevant examples. If the target manuscript has
   a local `writing/.corpus/selections/<document>/corpus.toml`, use its
   selected examples and judgments as the first guide. Existing paper-level
   `decisions/corpus.toml` may be consulted locally but must be reviewed before
   staging: private IDs, paths, source selections and excerpts stay local.
   Prefer the author's own prose
   when learning their voice; use field exemplars for genre conventions and
   venue materials for submission requirements. Do not read every corpus item
   when only a few fit the task.
4. Notice recurring tendencies in vocabulary, phrasing, sentence and paragraph
   length, transitions, register, claim framing, and pacing. Treat these as
   weak style cues, not hard constraints. Preserve the author's intent and the
   current request. Learn the pattern rather than reusing distinctive wording,
   sentence sequences, or claims.
5. Check whether the selected examples actually cover the requested style
   choice. Coverage is weak when no source is close in field, language, genre,
   or register; when source versions or locators cannot be checked; or when
   examples materially disagree and the difference has no clear explanation.
   A small corpus alone is not a problem if its examples are relevant and
   trustworthy. Treat coauthored samples as field evidence when an individual's
   voice cannot be isolated.
6. When weak coverage limits the requested style match, warn the user with the
   concrete gap and its effect on the current draft. Explain that a relevant
   source can be added to `writing/.corpus/index.md`. If the user wants a
   repeated preference to govern future drafts, explain the scoped-rule option
   in `writing/.rules/`. Continue the requested work where possible and mark
   style choices that remain tentative.
7. If a task-specific choice is made from examples, record the selected source,
   locator, and resulting judgment in
   `writing/.corpus/selections/<document>/corpus.toml`. In a tracked paper
   decision or `writing/.rules/`, keep only independently adopted minimal
   nonconfidential rules without local source IDs, paths, excerpts or provenance.

## Promoting observations

The corpus remains descriptive. A single example or an uncertain tendency does
not create a rule. When a recurring preference remains unresolved, explain the
gap and, when useful, offer a concise, scoped rule for the user to add to
`writing/.rules/`. Keep its evidence and exceptions with the rule. The user may
also add or revise workspace rules directly.

Add guidance to this skill only when the user or assistant identifies a durable
writing convention that applies across fields. Keep author voice, discipline
conventions, and venue requirements in the workspace corpus or rules, with
their scope stated explicitly.

## Storage boundary

The shared corpus also serves `reading/` notes and lectures. Its originals,
index, registration metadata, extracts and selection history are local-only;
follow [source and corpus privacy](../../labo-layout/references/reference-privacy.md).
Use an independent local Git only when requested, without remotes or LFS and
with all pushes blocked. Never copy the corpus into tracked paper/policy files,
force-add it, bypass hooks, or upload it to public/private GitHub or other services.
Public availability does not change this boundary.

## Register or update examples

Before writing any new entry, including an open book or paper, verify that
parent `git ls-files -- writing/.corpus` is empty and `git check-ignore -q --
writing/.corpus/index.md` succeeds. Add the parent exclusion if missing; if any
corpus paths are already tracked, stop staging/sharing them and perform the
explicit preservation-and-untracking migration under the privacy protocol.
Create or update the index only inside this local corpus. An existing corpus
Git must have no remotes, an effective executable deny-all pre-push hook, and
no clean filters/LFS; repair missing protections before recording a snapshot.
Store original files here or link to their existing local-only source location.
Do not copy an ignored inbox original into a tracked paper just to register it.
Record private selections only beneath the corpus. Check again before any
parent/policy commit or push; never force-add or bypass a failed guard. Layout
creation supplies exclusions but does not silently migrate tracking, initialize
local Git or install hooks. Use the explicit privacy installer for requested
local history and verify actual bytes afterward.
