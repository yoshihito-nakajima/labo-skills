---
name: reading-reference
description: Investigate research positioning, prior work and notation lineage; read and explain papers, mathematical books, proofs and methods; maintain source-grounded notes and bibliographic versions. Not manuscript editing or website publication.
---

# Read, reconstruct and explain

Before substantive work, follow [eligibility and handoff](../research-router/references/editing-capability.md).

For each user request, follow the [required consultation](../research-router/references/consultation.md).

When author identity, voice, or preferences matter, consult the Labo workspace
[author profile](../../../profile/author-identity.md) when available. Keep
personal facts there rather than in skill text; update only explicit durable
facts or corrections from the user, or facts they ask to save, with source
context. Apply this skill's normal source-verification rules.

Use for 「この論文を前提から解説して」「この証明を読みたい」,
「自分の研究はどこに位置するか」「先行研究をどう発展させたか」,
book/chapter reading, literature investigation, and checking a reading note.
Infer the source/version, audience, question and requested output from context.
Ordinary chat stays in chat; create `reading/<slug>/` for requested persistent
work. Notes may explain the user's own research as well as external sources.
Review-only requests produce findings, not silent edits.

For a standalone Japanese translation, including a Japanese-only reading copy
of a whole paper, use [japanese-translation](../japanese-translation/SKILL.md).
Translation alone does not trigger the paper-preparation requirements for
paired original text, added explanation, literature investigation, or method
implementation. Requests for those additional materials retain their scope here.

For a substantial explanation where mathematical clarity, emphasis or pacing
is the main challenge, also use
[mathematical-exposition](../mathematical-exposition/SKILL.md). This skill
continues to own source identity, reading coverage and deliverable checks.

Read only the references needed for the task:

- [Reading structure](references/reading-structure.md): mandatory before outlining
  or revising substantial reading material and bounded previews; source hierarchy,
  retained role sections, source return, optional views and before/after checks.
- [Roots and lenses](references/roots-and-lenses.md): methods sharing a root but seen
  through different lenses; what to collect while investigating the sources, the
  background card, its data format checked by `scripts/check_cards.py`, and how derived
  talks use it.
- [Sources](references/source-rules.md): acquisition, versions and coverage.
- [Literature intake](references/literature-intake.md): the supplement, cited works, code and data of a
  paper: depth, open routes only, the proposal to the user, substitutes only after confirmation.
- [Resource ledger](references/resource-ledger.md): inventory of everything the paper
  consists of, the main-text → supplement reading route, must-read supplements, and what
  to do with material that cannot be obtained (report it; no AI-created stand-in without the
  user's per-resource permission).
- [Method-paper profile](references/method-paper-profile.md): the parts of a detailed note for a
  paper whose contribution is a method with code (life science, information science), with a
  skeleton in `assets/method-note/`; not a template for proof-centred mathematical papers.
- [Survey-paper profile](references/survey-profile.md): a survey read section by section — one record per section as
  the single source of the PDF and the HTML, edges stated once, claims checked against pages and figures.
- [Lineage and comparison](references/lineage-and-comparison.md): inventory of inherited,
  compared, criticised, encompassing/encompassed, origin and earlier-version works, and the
  level at which each is treated, down to code differences.
- [Unit chain and claim gloss](references/unit-chain-and-claim-gloss.md): needs/produces
  between sections, the argument spine, the reader floor, and the sentence-level gloss for
  sentences that rely on prior results or assert properties.
- [Terminology and notation audit](references/terminology-audit.md): compare
  manuscript object types, names and conventions against actual same-role
  corpus definitions and primary-source pages; distinguish semantic defects,
  undefined labels, legitimate alternatives and stylistic preference.
- [Research positioning](references/research-positioning.md): mandatory
  literature investigation at research/writing checkpoints, precise contribution
  comparisons, a reusable memo, and notation/convention lineage.
- [Explanation](references/explanation.md): teaching a concept, proof or paper.
- [Applications to code](references/application-to-code.md): section-local reading,
  adjacent explanation/code, actual-use evidence, reasons for choosing the example
  and per-code method relationships; read for
  substantive computational-method explanations or method-bearing code.
- [Methods](references/methods.md): reconstructing mathematical, computational
  or empirical reasoning; use only the applicable branches.
- [Review](references/review.md): checking coverage, fidelity, understanding
  and rendered deliverables.
- [PDF navigation checks](../mathematical-navigation/references/pdf-checks.md):
  shared structural checks, changed-page rendering and representative viewer
  checks for PDFs; distinct from source fidelity and explanatory coverage.
- [Research-program synthesis](references/research-program-synthesis.md):
  explaining a local research program across plans, proof records, literature
  and Lean evidence.

## Required research-positioning checkpoints

Before framing or substantively reframing research, starting substantive
manuscript work or revising its contribution narrative, or preparing own-research
talks with novelty or comparative claims, run the
[positioning protocol](references/research-positioning.md).
Refresh it when the question, claim, hypotheses or method changes the comparison,
and before submission. Investigate beyond the supplied bibliography; do not
replace actual searches and primary-source inspection with recalled literature.
Reuse the program's positioning memo and update affected comparisons rather than
restarting every time. Typo-only edits and routine progress that do not affect
positioning are exempt. Review-only and bounded lookup tasks retain their scope;
a positioning investigation does not itself request full-paper translation,
implementation reproduction or manuscript edits.

## Workflow summary

Read the [workflow and completion contract](references/workflow.md) before
substantial reading, full-paper explanation or paper preparation. In outline:

1. Fix the source and the useful unit; inspect the actual text and preserve unread scope explicitly.
2. Set the reader outcome before drafting, and decide the reader-facing format.
3. Map in-scope results, prerequisites, lineage, code and supporting passages to inspected sources.
4. Explain the question, result, decisive argument and limits; deliver checked units as they become available.
5. Before calling substantial material complete, run `scripts/check_coverage.py` on the coverage records and apply the review reference; report actual checks and unresolved dependencies.

Describe the deliverable by its actual contents and scope, such as a full-paper
explanation, proof reconstruction or reading deck. Do not present notes as a
substitute for reading the source, or imply that they certify the reader's
comprehension or let them claim to have read it. State which sections and
arguments the artifact covers, and name material omissions or source-level
gaps directly.

Before delivery, check the requested language across the complete reader-facing
artifact, including headings, captions, labels and navigation as well as body
prose. Preserve original titles and standard technical terms where they serve
the reader; do not let those exceptions leave ordinary explanatory text in a
different language.

Keep source originals in `reference/<key>/` or their existing inbox; record
identity in `reference.md`. Persist notes and derived assets in `reading/`,
with source links and a compact coverage/next-step record when needed to resume.
Keep the cross-paper positioning memo with its research program, reusing an
equivalent existing record; the positioning protocol owns its reusable template.
Reuse existing records; no fixed manifest, helper CLI, reviewer roster or model
is required. Use `labo-layout` only when creating or locating workspace items.

Produce the requested formats and language. For PDFs, build from the notes'
own TeX root with `labo-build`'s `output build --source reading/<slug>/<root>.tex`
workflow; it places the PDF and SyncTeX in `output/<slug>.*`, overwrites that
pair on later builds from the same project, and prunes old output files. The
viewer stays closed unless `--open` is supplied. The build runs the shared
[PDF navigation check](../mathematical-navigation/references/pdf-checks.md).
Record its status separately from rendering and actual viewer checks under R29;
use the shared change-aware procedure instead of repeating every GUI click.
Inspect the rendering and preserve source/content checks even when the structural
report passes. Use `slide-authoring` for requested decks, retaining this skill's
source checks.
Preparing notes does not authorize publication or author contact.
