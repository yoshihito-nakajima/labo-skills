---
name: research-management
description: Start or resume story-centered research from inbox material, maintain plans and evidence, and propose changes to research-program boundaries.
---

# Research program maintenance

Before substantive work, follow [eligibility and handoff](../research-router/references/editing-capability.md).

For each user request, follow the [required consultation](../research-router/references/consultation.md).

When author identity, voice, or preferences matter, consult the Labo workspace
[author profile](../../../profile/author-identity.md) when available. Keep
personal facts there rather than in skill text; update only explicit durable
facts or corrections from the user, or facts they ask to save, with source
context. Apply this skill's normal verification rules.

Read [research policy](references/research-policy.md) before changing a plan.
Start with the central question and the developing argument, not publication
milestones. Inspect `plan.md` and only the smallest related evidence needed.

Keep the research story, prior-literature evidence, and relevant Lean work in
conversation. Use sources to locate the question and its relation to earlier
results; use formalization to pressure-test definitions, assumptions, and
candidate claims. Let either kind of evidence reshape the plan, and record
which claims are formalized, proved by other means, or still open.

Before a new or substantively reframed plan, run `reading-reference`'s required
[research-positioning investigation](../reading-reference/references/research-positioning.md).
Maintain one reusable program-level memo of the search coverage, exact prior-work
comparisons, inherited versus added ingredients, and notation/convention lineage.
Link it from the plan; reuse an adequate existing record. When the central
question, result, relevant hypotheses or method changes the comparison, refresh
the affected evidence and story. Ordinary progress updates do not restart the
survey. If inspection changes the contribution, propose the resulting reframing
instead of preserving an unsupported novelty claim.

For substantive plan drafts, full plan revisions, or requests to explain a
whole research program, apply the claim-level evidence and prior-work standard
in [research policy](references/research-policy.md).
Distinguish what prior sources establish, what this program adds, and what
remains conjectural or open. Compare the relevant hypotheses, objects,
conclusions, and proof methods; link each central claim to its exact source and
proof record. The plan should explain the decisive proof mechanism and its
dependencies, while each established central result has a complete, inspected
derivation in the linked record. Open claims need a concrete proof route,
missing lemmas, and known obstacles. Never infer novelty from an absent
citation or an unsuccessful search.

For load-bearing results or reviews that need durable reuse, read the optional
[evidence protocol](references/evidence.md). It defines stable claim IDs,
scoped proof/formal evidence, and review-input snapshots, with templates and
checks owned by this checkout. Reuse an adopted catalog when relevant; create
one only within the requested work. Keep exploration in prose when a catalog
would add no value. Its claim statuses do not change the plan's two statuses.
Never treat a structural check or an unchanged snapshot as proof certification,
and never promote a claim from the owner's praise or permission to edit.

For categories, theorem/question nodes and nested work progress, use
[research-exploration](../research-exploration/SKILL.md). It supplements the
program story without changing this skill's two plan statuses. Its formal
completion gate reuses adopted claim catalogs and directly covering formal
reviews. When accepting plan edits or exploration in an existing program, follow
[labo-layout's safe structural migration](../labo-layout/references/research-migration.md)
to create a missing tree and reuse existing records. Read-only work preserves
the layout. Structural migration leaves past proof statuses and links intact;
new proof-bearing tasks use the formal completion gate.

Use `labo-layout` for workspace and program creation. A request to start
research from supplied material authorizes creating the necessary plan and
source directory; reuse a relevant existing program when appropriate.
Populate the story and next investigation from that material, distinguishing
proposals from established evidence. Do not stop at an empty template.

When useful, proactively **propose** a new program, split, combination,
reframing, or temporary cessation of work. Changes beyond the requested work,
especially existing program boundaries, are editorial recommendations for human
review, not state-machine transitions or automatic deletion.
Apply accepted changes with Git history, preserve all original sources, and
run `python3 <labo-script> research check`.

Resolve `<labo-script>` to the absolute `../../scripts/labo.py` path relative
to this skill's **real directory** (follow symlinks first), not the shell's
current directory. This executes the policy checkout being used, without
installing the project. The launcher detects the private Git superproject;
use `--workspace /absolute/path/to/labo` to override it or when using a
standalone policy checkout. For a frontmatter-only inventory, run
`python3 <labo-script> research list --format json`.
For an adopted evidence catalog or review, run `evidence check` on those
explicit paths; do not make unrelated research pass a new mandatory gate.

For a program-level account of recorded claims and review coverage, read
[evidence status](references/evidence-status.md) and use `evidence status
--research <slug>`. It reads only the selected program or explicit records;
absence of a catalog does not trigger migration. For manuscript input omissions,
read [scope diagnostics](references/evidence-scope.md). For authorized actual
Lean execution, read [selected-source replay](references/formal-replay.md):
`evidence replay` plans only unless `--execute` is explicit, uses prepared trusted
code, and never equates a completed replay with informal alignment or approval.
