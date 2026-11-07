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

## Purpose and completion contract

For substantial reading, first fix the source-unit and required role-section map
under [Reading structure](references/reading-structure.md). Keep it through revisions
and inspect it before checking the latest local feedback. The structure reference
owns the outline; paper preparation owns passage fidelity; application-to-code and
methods own method content; review checks the delivered result. A bounded preview
still completes its selected source unit through the target original/translation.


Prepare the reader to reconstruct the paper's reasoning and explain it in a
presentation, especially why its methods answer its questions. Method
understanding connects the analysis target and question, required properties,
theoretical design, suitability and limits, relationships to other methods,
and mathematical operations to implementation and interpreted outputs. For
computational methods, follow the section-local reading contract and per-code
relationships in [Applications to code](references/application-to-code.md), including
background and educational methods. Explain both why the application needs the
method and why that example belongs in this section. Establish the full
application context, including its photographs/figures, captions and reading,
and the obstacle before the first code. Introduce the overall computation and
display its complete selected implementation before walking through excerpts.
Connect those operations to their specific strengths and fit to that obstacle,
followed by method relationships.
Keep code near its mathematical explanation after this context is established;
use a coherent method/application account rather than a template per excerpt.
Throughout the explanation, apply
[adjacent-passage continuity](../mathematical-exposition/SKILL.md#carry-the-argument-across-adjacent-passages),
including passages without code. For structured added explanations, name the method or concept at its entrance,
before background, then retain the role sections prescribed by the method
contract or agreed outline and use
[role | concrete point headings](../mathematical-exposition/references/roles-and-headings.md).
Keep those role boundaries and connect their openings to the preceding content;
consolidate unnecessary subdivisions only within a role. Audit headings and body
under H1--H5 in that reference. In PDFs retain both title parts in nested bookmarks
under the source hierarchy, checking the built outline under [R14](references/explanation.md).
Complete each local method account through meaningful stages. Follow
[document sequence and optional views](references/paper-preparation.md#keep-section-progression-and-purpose-specific-views-distinct):
after a main section's translation, advance to the next source section. Do not
add or retain a whole-document duplicate merely to provide another reading route.
An optional background/explanation or code collection must serve a distinct task,
retain the dependencies needed for that task, and share maintained source content
with the main account. Neither collection is mandatory. Cite sources at the
claims, equations, figures, code operations and comparisons they support, with
inspected locators, and put the common bibliography last. A final-list link or
code-end attribution does not replace those in-text citations.

For substantial close-reading or presentation-preparation materials about a
paper or specified part, read
[Paper preparation](references/paper-preparation.md) before drafting. It owns
the source-aligned structure, preparatory explanation followed by an explicit
return to original text and faithful translation, and the purpose-to-evidence-
to-code completion contract. Supporting literature actually used in the explanation
also needs selected original passages and faithful translations beside the relevant
explanation under [supporting-source reading](references/paper-preparation.md#make-supporting-literature-readable).
This covers the passages used, not full translations of every bibliographic entry.
Apply its code requirement to each explained computational method even without
a separate request for code.
A proof-only paper does not require fabricated software; explain its proof
methods through the mathematical branch. Bounded questions, source lookup and
reviews retain their requested scope rather than triggering a full translation.

For implementation selection and language-learning examples, follow
[source-grounded implementations across languages](references/multilanguage-code.md):
prefer inspected author code in its actual language, supply source-based code
when unavailable, and explain each added language's design and verification.

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
   For paper preparation, map each supporting passage to its displayed original,
   faithful translation and the explanation it supports. For optional views,
   select content by their declared reader task and preserve its dependencies.
   Place background and mixed-role visuals where the problem first needs them;
   do not defer every figure to results. Link optional views to corresponding
   main units; label an index as an index rather than a complete explanation.
5. Explain the question, useful result, decisive argument and its limits.
   For central methods, explain the motivating limitation, inherited ideas and
   new contribution with primary evidence. For required code, make provenance
   and the route between explanation, full implementation and sources usable
   in the delivered artifact; apply the explanation and methods references.
   Preserve source section/subsection hierarchy and complete each local unit
   with faithful translation and a coherent application-first explanation.
   Bring the existing background photographs, figures, captions and explanation
   together before code. Once the obstacle is understood, explain the overall
   computation and show its complete selected implementation. Then develop its
   mathematics and code through meaningful stages, explain their specific fit to that
   problem, then compare methods through visible matching excerpts of actual implementations.
   Do not restart five headings at every excerpt. Finish each source unit with
   the explanation-to-source correspondence and original/translation under the
   paper-preparation contract; preserve their internal order and then advance to
   the next source unit. Name each method/code unit before explaining it.
   By the end of each local method unit, those distributed cycles must form a
   complete application/evidence/search/reproduction account. Optional views
   select and reorganize this content for a different use; they do not replace
   the local explanation or require duplicating its entire account.
   Put prerequisite bridges where needed and make each source-to-explanation
   connection findable. A summary, source dump or list of links cannot fulfill
   a request to reconstruct the reasoning or reproduce a method.
6. Deliver useful checked units as they become available, with actual content
   and remaining gaps. Continue the rest of the requested scope; an interim
   explanation is not completion of the whole book or paper.
7. Before calling substantial material complete, keep the coverage records
   (resource ledger, lineage inventory, unit chain, claim gloss) as one data file and run
   `scripts/check_coverage.py` on it; open entries and record gaps block completion.
   Check the explanation against the sources and the reader's ability to use
   it. For substantial deliverables, apply the review reference. Report actual
   checks, source versions, covered units and unresolved dependencies.
   Separate primary-source checks, implementation inspection/execution and
   rendering checks in the handoff; none certifies the others. Required missing
   sources or implementations remain incomplete work, even when disclosed.
   Review each optional view against its declared task, including dependencies,
   retained claims, locators, statuses, limits and return links. Check supporting
   originals/translations against their actual sources separately from code
   attribution; working code links do not establish passage coverage or fidelity.
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
viewer stays closed unless `--open` is supplied. The build runs the shared
[PDF navigation check](../mathematical-navigation/references/pdf-checks.md).
Record its status separately from rendering and actual viewer checks under R29;
use the shared change-aware procedure instead of repeating every GUI click.
Inspect the rendering and preserve source/content checks even when the structural
report passes. Use `slide-authoring` for requested decks, retaining this skill's
source checks.
Preparing notes does not authorize publication or author contact.
