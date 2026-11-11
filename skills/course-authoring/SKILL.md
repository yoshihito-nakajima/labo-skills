---
name: course-authoring
description: Create and maintain local mathematical courses and long notes, either following books or organized by topic, with one canonical text, resumable progress, optional local Git and separate normal or adversarial review. Not research-paper authorship or ordinary chat explanations.
---

# Local courses and mathematical notes

Own the plan, canonical text, correction integration, progress and official output.
For book-led work, also use [reading-book](../reading-book/SKILL.md) for editions,
source coverage and adoption decisions. Topic-led work starts from a question,
reader and prerequisite route; it does not require a whole-book coverage ledger.
Both modes cite the sources actually used and record changes to their claims.

## Start or resume

Read the existing plan, current progress summary, relevant text and outstanding
returns before choosing work. Preserve existing locations and owners; using this
skill does not take over another producer, migrate a live course or start reviews.
Use [storage and build](references/storage.md) for new placement, privacy and tools;
use [layout](references/layout.md) and [role folders](references/role-folders.md) when creating or resuming a handoff.
Keep one canonical text, not a second reviewed edition that must be edited in parallel.

For new work, establish the reader, adopted scope, allowed starting facts and the
next meaningful section. Use `local/books/<slug>/` for book-led courses and
`local/topics/<slug>/` for topic-led courses or notes. New projects default to no Git.
Original books belong in `local/original/`, which must be ignored and never added
to any Git, including local-only Git. Existing originals may stay in their protected
input location. Do not move or copy them merely to match a layout.

## Produce useful mathematical units

Apply [mathematical-exposition](../mathematical-exposition/SKILL.md) for explanation
and proof detail, and [undergraduate-lecture](../undergraduate-lecture/SKILL.md)
when appropriate to the reader. Self-check every adopted definition, construction,
proof, calculation and necessary exercise solution. Restrict independent review
effort, not mathematical correctness or the agreed self-contained scope.
Separate intuition from the actual proof; do not turn missing proofs into sketches
or silently strengthen assumptions, weaken conclusions or drop adopted material.

Write one coherent unit using its direct prerequisites. Record the actual text and
proof locations, source correspondence when relevant, unresolved obligations and
next work in the existing `progress.md`; keep historical detail out of the current
summary. Preserve valid earlier evidence and recheck changed claims and affected uses.
Independent checks unavailable in the host remain explicitly unperformed.

Use [mathematical-navigation](../mathematical-navigation/SKILL.md) from the first
draft. Long courses use section-scoped shared theorem numbering `1.18.5` and
separate equation numbering `(1.18.7)`. Preserve semantic labels. Keep definition,
notation and formula indexes connected to the actual introductions.

## Normal production and optional hard review

Normal production includes full author self-check and selective, bounded independent
math/output checks, prioritizing important dependencies, source repairs and generalizations.
It does not routinely launch the adversarial panel or make every theorem wait for approval.
For this ongoing production workflow, exposition clarity is self-checked and
selectively reviewed too; do not automatically run exposition-review on each
increment or handoff. Run its loop on a frozen completed scope when requested.
Use [math review](../reading-book-math-review/SKILL.md) and
[output review](../reading-book-output-review/SKILL.md) in `local/review/<case>/`.
For explicit hard review of a fixed proof or chapter, use
[proof-adversarial-review](../proof-adversarial-review/SKILL.md) in
`local/hard_review/<case>/`; a folder name alone is not an instruction to launch it.
Reviewers return findings; the producer owns repair and integration.

Follow the [production handoff contract](references/production-handoff.md) for
immutable inputs, ownership and returns. Continue independent production while
waiting. Resolve serious findings before relying on the affected claim. Distinguish
written, self-checked, independently reviewed, returned, author-received, repaired,
rechecked and reflected in PDF. Review status always names a version and scope.

Build coherent changes together; structural PDF checks, visual inspection, index
coverage and mathematical review are separate evidence. At a chapter boundary,
compare adopted scope with actual proofs and necessary solutions, outstanding
findings, references/indexes and matching output. Report concrete remaining work;
neither page count nor an empty review queue establishes completion.
