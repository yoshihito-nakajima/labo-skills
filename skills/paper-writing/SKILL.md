---
name: paper-writing
description: Draft or revise mathematical research manuscripts from research plans, source-grounded literature, and proof evidence; not report-only review.
---

# Mathematical paper writing

For each request, follow the [required consultation](../research-router/references/consultation.md).

For substantive mathematical explanation or revisions to exposition, also use
[mathematical-exposition](../mathematical-exposition/SKILL.md) as a clarity
overlay; this skill remains responsible for manuscript scope and authorship.
For a `*_lec.tex` target, also use
[undergraduate-lecture](../undergraduate-lecture/SKILL.md) for its reader floor.

When author identity, voice, or preferences matter, consult the Labo workspace
[author profile](../../../profile/author-identity.md) when available. Keep
personal facts in that profile, not in this public skill.

For writing tasks, consult the workspace's `writing/.rules/` and
`writing/.corpus/` when present. Load the rules scoped to the manuscript and
venue, then use a small relevant selection from the corpus as a soft guide to
wording, sentence rhythm, transitions, register, and rhetorical pacing. The
corpus informs style without turning every observed feature into a requirement;
never copy distinctive wording or claims from an example. Keep the detailed
selection and promotion process in [the style-corpus workflow](references/style-corpus.md).

Keep workspace and field-specific rules in `writing/.rules/`. If no close
corpus examples match the requested field, language, genre, or register—or the
examples materially conflict—warn the user when that gap affects the requested
style work. Name the weakly grounded choice and explain that a relevant source
can be added to `writing/.corpus/index.md`. If the user wants a recurring
preference to become a requirement, explain that it can be added as a scoped
rule in `writing/.rules/`. Continue with the best available evidence where
possible, and do not turn sparse examples into rules automatically. Add a rule
to this shared skill when the user or assistant identifies it as durable and
useful across fields; keep personal, venue-specific, and field-specific
preferences out of the shared skill.

## Build from the evolving research record

Read the relevant `writing/<paper>/` files and the smallest related evidence
needed from `research/<slug>/plan.md`, `reading/`, `reference/`, and `lean/`.
Let the paper grow from the research story and its evidence. Literature may
change how the question is framed; formalization may clarify assumptions or
expose gaps; a draft may reveal missing links that should return to the plan.
Do not require these activities to happen in a fixed sequence.

Use `reading-reference` to inspect or verify prior literature when needed, and
`research-management` when the program's story or evidence record needs to
change. Keep citations tied to the version actually read, with precise theorem,
section, or page details where available. Never invent references or attribute
a result from memory when the source can be checked.

Treat Lean as evidence for exactly the definitions and statements it checks.
Do not imply that an informal argument is machine-checked, that a placeholder
proves a result, or that formalization of a nearby statement establishes the
paper's full claim. State proof boundaries plainly and preserve open gaps for
the author to resolve.

If this work already has a claim catalog or scoped review records, use the
[evidence protocol](../research-management/references/evidence.md) to inspect
the affected claims and check their recorded inputs after substantive changes.
Preserve the previous report and expose a stale review; do not silently renew
its hash, promote its verdict, or imply that a changed claim remains reviewed.
Recommend the smallest necessary new review. Do not create catalogs or review
records for unrelated work, or make them a prerequisite for ordinary writing.
For an adopted TeX writing review, use the optional
[scope diagnostic](../research-management/references/evidence-scope.md) to compare
literal inputs with the selected files/tree or existing record, especially after
adding includes, figures or bibliography files. Resolve omissions explicitly;
neither the diagnostic nor a fresh snapshot silently renews an earlier pass.

## Preserve the author's argument and voice

Keep the introduction connected to the paper's actual question, prior work,
contribution, and proof route. Follow the mathematical dependencies of this
argument instead of forcing a standard outline onto it. Preserve the author's
intentional voice, examples, and humor already present when they help the
reader; do not silently remove personal asides or distinctive phrasing merely
to make the prose more formal. Make new stylistic additions only when the user
asks or the draft clearly calls for them. Raise substantive changes to claims,
emphasis, or tone for the author to decide.

For an independent report-only assessment, use `paper-referee`; compile or
refresh the PDF and SyncTeX through `labo-build` when the user wants a rendered
manuscript.
