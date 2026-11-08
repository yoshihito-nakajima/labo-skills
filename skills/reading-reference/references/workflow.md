# Reading workflow and completion contract

The detailed workflow of [reading-reference](../SKILL.md): the purpose and
completion contract for substantial reading, then the seven workflow steps.
Read it before substantial reading, a full-paper explanation or paper
preparation; bounded lookups and reviews keep their requested scope.

## Purpose and completion contract

For substantial reading, first fix the source-unit and required role-section map
under [Reading structure](reading-structure.md). Keep it through revisions
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
relationships in [Applications to code](application-to-code.md), including
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
[adjacent-passage continuity](../../mathematical-exposition/SKILL.md#carry-the-argument-across-adjacent-passages),
including passages without code. For structured added explanations, name the method or concept at its entrance,
before background, then retain the role sections prescribed by the method
contract or agreed outline and use
[role | concrete point headings](../../mathematical-exposition/references/roles-and-headings.md).
Keep those role boundaries and connect their openings to the preceding content;
consolidate unnecessary subdivisions only within a role. Audit headings and body
under H1--H5 in that reference. In PDFs retain both title parts in nested bookmarks
under the source hierarchy, checking the built outline under [R14](explanation.md).
Complete each local method account through meaningful stages. Follow
[document sequence and optional views](paper-preparation.md#keep-section-progression-and-purpose-specific-views-distinct):
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
[Paper preparation](paper-preparation.md) before drafting. It owns
the source-aligned structure, preparatory explanation followed by an explicit
return to original text and faithful translation, and the purpose-to-evidence-
to-code completion contract. Supporting literature actually used in the explanation
also needs selected original passages and faithful translations beside the relevant
explanation under [supporting-source reading](paper-preparation.md#make-supporting-literature-readable).
This covers the passages used, not full translations of every bibliographic entry.
Apply its code requirement to each explained computational method even without
a separate request for code.
A proof-only paper does not require fabricated software; explain its proof
methods through the mathematical branch. Bounded questions, source lookup and
reviews retain their requested scope rather than triggering a full translation.

For implementation selection and language-learning examples, follow
[source-grounded implementations across languages](multilanguage-code.md):
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
   use [research-program synthesis](research-program-synthesis.md):
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
   author/supplement/official code under [R18](methods.md). Report
   the search, implementation choice and execution status at that code unit;
   a toy experiment does not establish source coverage. Also map each method-code
   unit to inspected application evidence for the problem, requirements, pipeline
   role and obtained result under [Applications to code](application-to-code.md).
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
