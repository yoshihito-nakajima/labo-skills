# Check the explanation, not only its inventory

Use these checks for substantial notes and requested reading audits. A bounded
chat answer needs the relevant checks, not a standing review panel. Apply `R`
IDs to located findings, with severity, source/output evidence and a minimum
repair. Do not invent a defect quota or mark human understanding as achieved.

- **R25 Coverage** — First apply the [structure preservation check](reading-structure.md#check-the-structure-before-checking-the-latest-improvement):
  compare the pre-edit source/role map to actual bodies, hierarchy and source-return
  blocks. Check retained obligations separately from the latest requested change.
  A bounded preview and a newly labelled optional view cannot silently remove
  required main-route roles. Then derive expected in-scope units from the source before
  consulting the writer's outline or coverage claims. Compare expected versus
  acquired/inspected material, then expected versus actually explained units.
  Missing required material stays visible. A filename, citation, figure asset
  or source reprint is not evidence of explanatory coverage.
  For surveys, check each central claim against its required primary evidence,
  the passages actually inspected and the citation/locator visible in the output.
  In substantial paper preparation, check supporting literature used for
  definitions, methods, applications and consequential comparisons for original
  excerpts and corresponding faithful translations at the relevant explanation
  under [supporting-source reading](paper-preparation.md#make-supporting-literature-readable).
  Bibliography membership alone does not require full translation. A code
  citation, paraphrase, source attachment or working link does not supply a
  missing required passage pair. Record inaccessible or restricted scope exactly.
  At each original/translation entrance, identify the named work, version and
  locator from the visible block itself. A bare "original", generic source role
  or bibliography elsewhere does not identify it. A shared source-labelled
  heading may identify both texts; the work need not be repeated on every line.
  Read the passage as a unit:
  does its introductory clause reach its equation/conclusion and retain the
  needed qualifications? Check clear source switches and descriptive link labels;
  a collection of accurate but detached sentence/link fragments can still fail.
  For paper preparation, also check source section numbers/order, original-text
  and faithful-translation coverage, separation of translation and commentary,
  and figure/equation explanations under [Paper preparation](paper-preparation.md).
  For preparatory reading order, check each owning source unit for connected
  explanation before the original and an immediate explanation-to-source bridge.
  It must map the already introduced objects/steps to exact source locations and
  give reading targets, not just repeat an outline. Moving all originals to a
  larger chapter's end fails source locality; unchanged source wording alone
  does not establish that the reader has been prepared.
  Check title meaning and actual section/subsection hierarchy, not just matching
  numbers in a contents list; detached or flattened local content is a finding.
  Check subject identity at each unit entrance and method/implementation labels
  before code, not only content-specific headings or post-block attribution.
  Across the whole main route, each source unit's translation must lead to the
  next source unit. Optional collections must serve distinct tasks under
  [the view contract](paper-preparation.md#keep-section-progression-and-purpose-specific-views-distinct).
  A whole-document duplicate without an explicit request is a structural finding.
  Check the common bibliography at the end, and separately inspect the citations
  throughout each route: can the reader identify the source and inspected location
  for each source-based claim, equation, figure, code operation and comparison at
  the passage using it? A final-list link, end-of-section source note or post-code
  attribution alone does not pass this check. Locate unsupported or ambiguous
  citation scope and unverified locators as findings.
  Treat an interleaved duplicate, an unexplained restart, or a collection whose
  actual content does not meet its declared purpose as a structural finding.
  For structured added explanations, run the [heading audit H1--H5](../../mathematical-exposition/references/roles-and-headings.md#audit-the-headings-against-the-body).
  Derive role order and boundaries from the owning contract/agreed skeleton,
  not from the draft's existing outline. Check both role and concrete point in
  each heading, fulfillment by the actual body, progression and consistency
  across methods/routes. Locate findings with R25/H1--H5 and the actual heading
  and passage. Content buried in another role does not excuse a missing section;
  merely restoring a role label does not repair detached prose under R27.
  For required code, check each in-scope computational method against matching code
  units, implementation provenance and inspected/executed status. A long code
  appendix or one successful toy run cannot compensate for missing methods.
  For each literature-based code unit, including educational/background units,
  check its exact method source, corresponding implementation search and local
  status report. Searches for the main algorithms do not cover auxiliary units.
  Check actual application evidence and code-unit relationships under
  [Applications to code](application-to-code.md), including background and
  educational units. A method citation or toy run does not cover a missing use case.
  Judge optional collections by their declared tasks, not identical field
  coverage. A code collection needs usable code and operational dependencies;
  an explanation view needs the premises and evidence of its retained argument.
  An accurately labelled lookup index does not promise either full account.
  Inventory the existing application photographs, figures, captions and their
  explanation too. Text alone does not preserve this account if its visual
  context has been omitted or deferred beyond the code that depends on it.
- **R26 Two-way fidelity** — Compare the note's claims to exact sources and
  trace central source claims back into the note. Check headings, formulas,
  figures, analogies and compressed summaries as well as prose. Verify both
  original excerpts and translations against the identified versions and their
  surrounding context. Check omissions, equations, assumptions, quantifiers,
  uncertainty and separation of added commentary. Read Japanese independently
  as well as against the source; presence of paired blocks alone is not fidelity.
  Verify both sides of consequential historical or method comparisons. For central methods,
  trace question, required properties, design, fit/limits and method relationships
  to inspected primary passages with point-of-use deep links. Check both shared
  structure and consequential differences, including sources beyond the target
  paper when necessary. Separate cited statements from a cross-source synthesis; an objective or runnable code alone
  cannot establish this account. Check code attribution against the inspected
  source/revision and the actual author-code search status, including adaptations
  and unresolved availability. Compare each code's visible search report and
  adoption reason against places actually visited and code actually inspected.
  Compare claims retained in multiple views with their sources and with
  each other, including exact locators, search order, adoption reasons, status
  labels, consequential differences and unresolved limits.
  An unvisited supplement, uninspected repository or inaccessible file cannot
  support "no author code"; flag the unfinished source work and missing local
  report even if the independent code is correct and its links work.
  For multiple languages, apply [the multilingual code contract](multilanguage-code.md):
  check author-code preference regardless of language, source/port identity,
  complete implementations, purpose and explained decisions, actual operation
  mappings and per-language execution evidence. Same seed is not necessarily
  the same input; numerical comparisons must respect the method's invariances.
  Test the implementation choice, not only the existence of an adoption reason:
  check whether existing options, a thin wrapper or annotations meet the reader's
  purpose, and distinguish the main execution route from an explanatory example.
  If matching code was found later, check that the choice was reopened against
  the request. Compare the reported selection order and reasons with the actual
  record; do not accept retrospective reasons presented as original evidence.
  Flag unexecuted equivalence claims, but do not demand blanket duplicate runs
  or unconditional adoption of author code. Keep unknown reuse terms distinct
  from demonstrated inability to run or link the implementation.
  For independent code, check the analysis purpose,
  operation-to-mathematics mapping, own choices/deviations and validation evidence;
  an origin label alone is insufficient. A faithfully stated source limitation is not
  automatically a defect in the explanation.
  For claimed method/code relationships, inspect both sides and trace shared
  and changed assumptions, equations and functions/lines to their consequences.
  Inspect the delivered visible code on both sides, its fixed source/line identity,
  and the local pairing. Links, prose or a line table without actual excerpts do
  not discharge an implementation comparison. Check the author-code preference
  and any scoped access gap; a substitute must not impersonate an author version.
  Do not accept "variant", shared provenance or similar syntax as the explanation.
- **R27 Reconstruction** — From the source, identify the inputs, reasoning or
  operations, result and limits. Then locate each needed link in the explanation.
  Check [adjacent-passage continuity](../../mathematical-exposition/SKILL.md#carry-the-argument-across-adjacent-passages)
  in the delivered reading order, including sections without code. At each
  transition, use the adjoining prose to identify what result, object or question
  is being taken up, why this next step follows, and what it contributes. Read
  titles together with their openings; a specific title cannot repair a detached
  paragraph, nor can "next" or "below" supply a missing dependency. Locate the
  first broken boundary in the actual text rather than inferring an intended
  connection from an outline, another route or source knowledge. Check whether
  joining unnecessarily split units within a role is the appropriate repair;
  preserve required role boundaries and repair their transitions rather than
  merging those roles. Do not add a formulaic recap at every paragraph. Apply this
  equally across prose, definitions, proofs, figures, equations, code and comparisons.
  For computational methods, read the application/method account in order:
  visible application context → obstacle → overall computation and full selected
  implementation → explained code excerpts → specific
  strengths and fit to that obstacle, with limits → other-method relationships.
  Stop before the first code and use only the preceding material to identify
  the target, data meaning, goal and difficulty. Inspect the actual photographs,
  figures, captions and explanation needed to do so. Before the first detailed
  excerpt, check that the reader has encountered the input-to-output flow and
  complete selected code with its dependencies. Locate that earlier listing;
  a later appendix, overview table or working link alone cannot pass this check.
  Confirm that excerpts belong to that same implementation and show where each
  operation fits. During the detailed walkthrough, trace a concrete
  operation to its property and its effect on that same obstacle; compare it to
  the shown example and source/code evidence. Generic usefulness or objective
  restatement fails this test. Check both why the application needs the method
  and why the example teaches this passage. Multi-step methods must advance a
  coherent account; forced five-part repetition around tiny snippets can break
  that account. Flag missing/deferred visual context, global batching or link-only
  substitutes even when all headings, ingredients and destinations exist.
  Passing marker-order, keyword, length or link checks cannot establish this
  semantic reading dependency. In a bounded preview, inspect at least one complete
  obstacle-to-operation-to-capability account in the selected scope. Record where
  the prose explains why the decisive operation works and where the corresponding
  code and source can actually be reached. A correct listing followed by limits,
  or a correspondence table without that reasoning, leaves this account unfinished.
  Keep this content check separate from compilation and visual-layout checks.
  Shared accounts
  may deepen evidence but must not make the local reading unit incomplete.
  Read the main route without relying on a later collection. Read each optional
  view using its declared prerequisites for its stated task: follow the argument
  in an explanation view, or understand/use the implementation in a code
  collection. Look for missing definitions, equations, captions, helper functions,
  references or transitions after extraction. Record the first blocked step;
  links to fuller detail cannot replace prerequisites needed for the advertised
  task. Do not require all views to repeat the same content. Knowledge recalled
  from the source cannot fill a missing explanation; this check is source-aware.
- **R28 Fresh reading** — When independent accessibility evidence is requested
  or materially useful, give a fresh isolated reader only the frozen output and
  neutral audience brief. Ask for actual understanding, first confusion and
  recoverable concise passages before repairs. Withhold sources, author intent
  and prior reports. A reader primed by notes cannot establish a deck's standalone
  readability. Preserve initial difficulty separately from later source rescue.
- **R28a Provenance wording** — `scripts/provenance_lint.py` reports no self-attribution in
  the deliverable's sources, code comments and generated records (quoted sources excluded
  by path); see [Sources, R5a](source-rules.md).
- **R29 Rendered output** — Check the current built version, not a stale PDF.
  Confirm it with `output verify-current` of [labo-build](../../labo-build/references/build-contract.md#current-build-check)
  before running any check on the PDF; after a failed build, report the failure.
  For PDFs, use the shared
  [navigation-check procedure](../../mathematical-navigation/references/pdf-checks.md):
  run the offline structural check over the full current PDF, then use changes
  and their impact to select rendering and representative viewer checks. Keep
  structural, rendered-page and actual viewer evidence distinct. A structural
  diff does not establish unchanged rendering; reuse prior visual evidence only
  for previously inspected pages with identical renders under the same settings.
  Inspect every page/slide for a complete visual review; otherwise disclose the
  inspected subset. Test equations/glyphs, readable labels, cropping, figure
  placement, listings and navigation at real reading scale. Check that the
  application visuals and their explanations are encountered before the code
  that requires them; later visibility does not repair a missing introduction.
  Inspect mixed-role figures for their background as well as result roles.
  For PDFs, inspect
  the actual nested bookmark tree as well: source section/method
  parentage, named subjects above role entries, useful local entries, readable
  titles and correct destinations. Inspect the main-route section boundary and
  any optional collection entry, not only navigation inside one method.
  Check that excerpt/translation pairs remain visibly associated with the
  relevant explanation and exact source identity after pagination.
  Inspect representative landing content for source and added units. A visible
  heading hierarchy, linked contents page or successful body links cannot
  establish that bookmark navigation exists. For code-bearing
  deliverables, inspect every displayed method-code block, including appendix
  listings: its method/implementation label must be visible before the block,
  and its source/link row must appear immediately after that block and
  visibly identify it. Check that the nearby explanation reconstructs the
  substantive operations and their correspondence to body equations/steps;
  correct destinations alone do not establish this. In the main route, inspect
  the preceding translation/explanation too: the code must correspond to that operation in
  the same source unit, not be reachable only in a later catalogue. Test its actual links:
  implementation source at the claimed fixed file/function/lines or supplement
  location, matching full code/editable unit, and explanatory body, with return
  routes where separate listings exist. A pre-block link, homepage, generic
  index or shared filename without a matching post-block row is a finding,
  even when a document-wide link checker passes. Check point-of-use citations against their reference entries
  and return links. Open external paper/code destinations and inspect whether
  they reach the intended supporting passage or implementation version/function.
  A live homepage, redirect to unrelated content or HTTP 200 is insufficient.
  Record unsupported page anchors and access failures explicitly. The shared
  checker inventories external routes without opening or executing them; access
  and semantic destination checks remain separate work. Inspect actual PDF
  annotations/destinations through the shared checker, then inspect the intended
  landing content and representative viewer behavior. TeX/Markdown markup alone
  cannot establish that generated links exist or reach the right unit. Record
  unresolved or unsupported actions as failed or incomplete coverage, not silent
  success. Do not repeat an unchanged GUI route merely to duplicate existing
  evidence; recheck changed routes, affected targets and viewer-dependent behavior.
  Check that file links/attachments remain usable in the delivered bundle, not
  only at the author's absolute workspace paths. Record untested destinations
  or viewer restrictions as limits, rather than claiming the route works.
  When optional views exist, inspect their bookmark subtrees, landing content,
  main-route next-section links, corresponding-unit links and references.
  Check filtered targets and relocated content; assess each landing against
  its advertised scope rather than requiring a duplicate full account.
  Extraction or build success does not prove visual correctness, source
  fidelity or understanding.
- **R30 Closure and saturation** — Before review, fix the scope and planned
  checks. For a substantial artifact, default to one full evidence-based review,
  one consolidated repair pass, then one targeted recheck of changed claims,
  dependencies and rendered pages. Do not start another full review panel
  automatically. For PDF navigation, retain the inexpensive full structural
  check on each build while targeting repeated visual and viewer work under
  the shared procedure. Passing structural checks does not close outstanding
  visual, semantic or coverage findings. A pass is saturated when it adds no new
  material, actionable finding: a material finding would change a central claim or proof, source
  fidelity or required coverage, the reader's ability to follow a decisive
  argument, or the requested deliverable's usability. Resolve every earlier
  material finding as corrected, disproved with evidence, or explicitly
  unresolved; keep duplicates, optional preferences and low-impact polish out
  of the repair queue unless the user requests them. If the targeted recheck
  reveals a new material issue, repair it if possible, verify that exact issue
  and its dependencies once, then close the round and report any residual gap.
  Reopen a broad review only when the user changes the goal or new source
  evidence undermines a central result. Record source identity, covered scope,
  unresolved gaps and next steps in the existing record. A structurally valid
  record cannot certify scientific truth or reader comprehension.
  Remove unnecessary whole-document repetition while preserving content and
  dependencies needed for each requested view. Do not remove a local explanation
  or supporting passage pair merely because a link to it exists elsewhere.
  In the reader-facing handoff, distinguish source verification, implementation
  inspection/execution and visual checks, with their actual scope. Do not use
  an unqualified "verified" or mark the requested explanation complete while
  required primary evidence or corresponding implementations remain missing;
  disclosure records the gap rather than waiving it.
- **R31 Coverage records and sentence reading** — Run `scripts/check_coverage.py` on the
  note's coverage data and report its output, including open entries; a pass shows the
  records are complete, not that the content is right. Then check the content the records
  point to. (a) Resources: every must-read supplement is actually displayed or explained at
  the main-text call site, with locator; an `unobtained` entry shows the places tried and the
  request, and the failure was reported with free alternatives; an AI-created stand-in exists only
  with a recorded per-resource permission, is labelled and shown beside an open entry
  ([ledger](resource-ledger.md)). (b) Lineage: for sampled entries compare the four
  statements (purpose, place, inherited, changed) with the primary passage, and, where code
  exists, the side-by-side difference with the stated execution ([lineage](lineage-and-comparison.md)).
  (c) Chain: at each unit boundary read only the preceding unit's end and the next unit's
  opening and name the need being taken up; at each parent end find the summary of what the
  subsections established. (d) Sentences: sample `cite`/`property`/`show` sentences from the
  delivered text, take the reader floor, and test whether the object, what is known, the
  exact claim and its benefit can be recovered without leaving the note
  ([claim gloss](unit-chain-and-claim-gloss.md)). A sentence that leans on a prior result
  and leaves the reader to ask "what is that, what is known, why does it matter" fails.
  Locate failures at the sentence, not at the section.
- **R32 Figure readiness** — For a method paper, judge whether the reader could present each
  main-text figure, and whether a [companion page](../../reading-companion/SKILL.md) could be
  built for it. For every main-text figure, and every supplementary figure the main text cites
  where understanding a main figure depends on it, check in the note: (a) what the figure
  claims (the main-text sentence that cites it and the caption, with locators) and how to read
  each panel (axes, colours, sizes, the marks to look at); (b) the computation behind it: step,
  function, lines and parameter values with where they are stated, and, where the figure or
  the claim compares methods, the earlier method's code; (c) the data and the
  [reproduction level](methods.md#reproducing-the-papers-figures) reached, with the run's
  correspondence to the panel; (d) what the figure does not show; (e) where the figure's
  difference comes from (steps and lines, marked as the paper's statement or the note's reading);
  (f) for the whole note, the lineage overview, the code-block notes (what each block does, where
  it comes from, how it differs) and the values table that a companion takes over. Report a table, one row per
  figure: ready, ready at a lower level, or blocked, with the missing part named. Put every
  missing item into the [request list](resource-ledger.md#request-list) and give it to the user
  with the review. Supplementary figures the main text does not need for understanding are not
  required here.

Delegate by the evidence needed, with a short task-specific packet and bounded
paths; no named agent persona or fixed model is required. A source-aware auditor
derives expectations before seeing the author's account. If cold isolation or
rendering is unavailable, finish useful checks and state that limit. Never
describe a self-check as independent or retry unchanged work for a favorable verdict.
