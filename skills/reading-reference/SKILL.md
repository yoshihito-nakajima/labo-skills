---
name: reading-reference
description: Read and explain papers, mathematical books, proofs and research methods; create or review source-grounded reading notes; preserve bibliographic versions. Not manuscript editing or website publication.
---

# Read, reconstruct and explain

For each user request, follow the [required consultation](../research-router/references/consultation.md).

When author identity, voice, or preferences matter, consult the Labo workspace
[author profile](../../../profile/author-identity.md) when available. Keep
personal facts there rather than in skill text; update only explicit durable
facts or corrections from the user, or facts they ask to save, with source
context. Apply this skill's normal source-verification rules.

Use for 「この論文を前提から解説して」「この証明を読みたい」,
book/chapter reading, literature collection, and checking a reading note.
Infer the source/version, audience, question and requested output from context.
Ordinary chat stays in chat; create `reading/<slug>/` for requested persistent
work. Notes may explain the user's own research as well as external sources.
Review-only requests produce findings, not silent edits.

For a substantial explanation where mathematical clarity, emphasis or pacing
is the main challenge, also use
[mathematical-exposition](../mathematical-exposition/SKILL.md). This skill
continues to own source identity, reading coverage and deliverable checks.

Read only the references needed for the task:

- [Sources](references/source-rules.md): acquisition, versions and coverage.
- [Explanation](references/explanation.md): teaching a concept, proof or paper.
- [Methods](references/methods.md): reconstructing mathematical, computational
  or empirical reasoning; use only the applicable branches.
- [Review](references/review.md): checking coverage, fidelity, understanding
  and rendered deliverables.

## Workflow

1. Fix the source and the useful unit: a concept, theorem, chapter or paper.
   Inspect the actual text and necessary dependencies. Preserve inaccessible
   or unread scope explicitly; a title or abstract cannot supply an unseen proof.
2. Set the reader outcome before drafting. For a full-paper explanation,
   write a self-contained account detailed enough for the reader to recover
   every main-paper result and its argument without relying on a reading route
   or the source paper to fill gaps. State the needed definitions and
   hypotheses where used, reconstruct decisive proofs and dependencies, and
   explain consequences and limits. A roadmap or summary is not full-paper
   coverage; label a deliberately bounded overview as such.
3. Decide the reader-facing format before drafting. Follow an explicit format
   request. A destination such as `reading/` does not imply Markdown: use a
   PDF for sustained reading or a handout, slides for a presentation, and
   Markdown for editable or reference notes when that fits the request. If the
   medium materially affects usability and context does not resolve it, ask
   one concise question instead of silently choosing. Link the finished
   reader-facing artifact directly and retain its editable source as useful.
4. For substantial reading, map in-scope results and prerequisites to source
   locations before drafting. For a full paper, account for its main text,
   methods, figures/tables and internal appendices; inventory supplements and
   explain those needed for the claims, controls and limitations. A whole-book
   request keeps its full scope while work proceeds through coherent units.
   For a survey, trace central claims and methods to inspected primary sources
   and exact locations, not just back to the survey. When code is requested,
   map each central algorithm to its corresponding implementation and execution
   status before treating a toy experiment as sufficient coverage; apply the
   source and methods references.
5. Explain the question, useful result, decisive argument and its limits.
   Put prerequisite bridges where needed and make each source-to-explanation
   connection findable. A summary, source dump or list of links cannot fulfill
   a request to reconstruct the reasoning or reproduce a method.
6. Deliver useful checked units as they become available, with actual content
   and remaining gaps. Continue the rest of the requested scope; an interim
   explanation is not completion of the whole book or paper.
7. Check the explanation against the sources and the reader's ability to use
   it. For substantial deliverables, apply the review reference. Report actual
   checks, source versions, covered units and unresolved dependencies.
   Separate primary-source checks, implementation inspection/execution and
   rendering checks in the handoff; none certifies the others. Required missing
   sources or implementations remain incomplete work, even when disclosed.

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
Reuse existing records; no fixed manifest, helper CLI, reviewer roster or model
is required. Use `labo-layout` only when creating or locating workspace items.

Produce the requested formats and language. For PDFs, build from the notes'
own TeX root with `labo-build`'s `output build --source reading/<slug>/<root>.tex`
workflow; it places the PDF and SyncTeX in `output/<slug>.*`, overwrites that
pair on later builds from the same project, and prunes old output files. The
viewer stays closed unless `--open` is supplied. Inspect the rendering. Use
`slide-authoring` for requested decks, retaining this skill's source checks.
Preparing notes does not authorize publication or author contact.
