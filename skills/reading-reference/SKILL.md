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

- [Sources](references/source-rules.md): acquisition, versions and coverage.
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

## Purpose and completion contract

Prepare the reader to reconstruct the paper's reasoning and explain it in a
presentation, especially why its methods answer its questions. Method
understanding connects the analysis target and question, required properties,
theoretical design, suitability and limits, relationships to other methods,
and mathematical operations to implementation and interpreted outputs. For
computational methods, follow the section-local reading contract and per-code
relationships in [Applications to code](references/application-to-code.md), including
background and educational methods. Explain both why the application needs the
method and why that example belongs in this section. Place corresponding code
immediately after the translation and necessary explanation of its operation.
Use identifiable subordinate headings for local application requirements and
code correspondence; in PDFs expose the source hierarchy and useful added units
as nested bookmarks, checking the built outline under [R14](references/explanation.md).

For substantial close-reading or presentation-preparation materials about a
paper or specified part, read
[Paper preparation](references/paper-preparation.md) before drafting. It owns
the source-aligned structure, original text and faithful translation, and the
purpose-to-evidence-to-code completion contract. Apply its code requirement to
each explained computational method even without a separate request for code.
A proof-only paper does not require fabricated software; explain its proof
methods through the mathematical branch. Bounded questions, source lookup and
reviews retain their requested scope rather than triggering a full translation.

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
   coverage; label a deliberately bounded overview as such. When the request
   spans a local research program or several connected research records, also
   use [research-program synthesis](references/research-program-synthesis.md):
   map the central claims and proofs, compare them with the relevant primary
   literature, and make the boundary between inherited results, this work's
   contribution, and open questions explicit. A program-level reading guide
   is not complete when it gives only a roadmap to the proof records.
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
   For any paper, trace method motivations, lineage and comparisons to inspected
   primary sources and exact locations, including predecessors beyond its
   bibliography when needed. For a survey, do not stop at the survey citation.
   When code is requested or required by the paper-preparation contract,
   map each literature-based code unit, including educational and auxiliary
   implementations, to its exact method source and an actual search for matching
   author/supplement/official code under [R18](references/methods.md). Report
   the search, implementation choice and execution status at that code unit;
   a toy experiment does not establish source coverage. Also map each method-code
   unit to inspected application evidence for the problem, requirements, pipeline
   role and obtained result under [Applications to code](references/application-to-code.md).
   Map source sections/subsections and local passages to that evidence, the
   reader's learning purpose and adjacent code before drafting.
5. Explain the question, useful result, decisive argument and its limits.
   For central methods, explain the motivating limitation, inherited ideas and
   new contribution with primary evidence. For required code, make provenance
   and the route between explanation, full implementation and sources usable
   in the delivered artifact; apply the explanation and methods references.
   Preserve source section/subsection hierarchy and complete each local unit
   with translation, necessary explanation, immediately corresponding code and
   operation/output interpretation. Use short explanation/code cycles for
   multi-step methods, with application and relationship context in that unit.
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
   For paper preparation, explicitly check every completion condition in the
   paper-preparation reference before calling the requested material complete.

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
viewer stays closed unless `--open` is supplied. Inspect the rendering. Use
`slide-authoring` for requested decks, retaining this skill's source checks.
Preparing notes does not authorize publication or author contact.
