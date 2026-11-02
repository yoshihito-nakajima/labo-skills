# Check the explanation, not only its inventory

Use these checks for substantial notes and requested reading audits. A bounded
chat answer needs the relevant checks, not a standing review panel. Apply `R`
IDs to located findings, with severity, source/output evidence and a minimum
repair. Do not invent a defect quota or mark human understanding as achieved.

- **R25 Coverage** — Derive expected in-scope units from the source before
  consulting the writer's outline or coverage claims. Compare expected versus
  acquired/inspected material, then expected versus actually explained units.
  Missing required material stays visible. A filename, citation, figure asset
  or source reprint is not evidence of explanatory coverage.
  For surveys, check each central claim against its required primary evidence,
  the passages actually inspected and the citation/locator visible in the output.
  For paper preparation, also check source section numbers/order, original-text
  and faithful-translation coverage, separation of translation and commentary,
  and figure/equation explanations under [Paper preparation](paper-preparation.md).
  Check title meaning and actual section/subsection hierarchy, not just matching
  numbers in a contents list; detached or flattened local content is a finding.
  Check that added application requirements, local example rationale, code
  correspondence, results/scope and relationships have identifiable headings
  at the relevant passage; accurate sentences buried in prose are insufficient
  when the reader needs to find these units directly.
  For required code, check each in-scope computational method against matching code
  units, implementation provenance and inspected/executed status. A long code
  appendix or one successful toy run cannot compensate for missing methods.
  For each literature-based code unit, including educational/background units,
  check its exact method source, corresponding implementation search and local
  status report. Searches for the main algorithms do not cover auxiliary units.
  Check actual application evidence and code-unit relationships under
  [Applications to code](application-to-code.md), including background and
  educational units. A method citation or toy run does not cover a missing use case.
- **R26 Two-way fidelity** — Compare the note's claims to exact sources and
  trace central source claims back into the note. Check headings, formulas,
  figures, analogies and compressed summaries as well as prose. Verify both
  sides of consequential historical or method comparisons. For central methods,
  trace question, required properties, design, fit/limits and method relationships
  to inspected primary passages with point-of-use deep links. Check both shared
  structure and consequential differences, including sources beyond the target
  paper when necessary. Separate cited statements from a cross-source synthesis; an objective or runnable code alone
  cannot establish this account. Check code attribution against the inspected
  source/revision and the actual author-code search status, including adaptations
  and unresolved availability. Compare each code's visible search report and
  adoption reason against places actually visited and code actually inspected.
  An unvisited supplement, uninspected repository or inaccessible file cannot
  support "no author code"; flag the unfinished source work and missing local
  report even if the independent code is correct and its links work.
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
  Do not accept "variant", shared provenance or similar syntax as the explanation.
- **R27 Reconstruction** — From the source, identify the inputs, reasoning or
  operations, result and limits. Then locate each needed link in the explanation.
  For computational methods, read each source unit in order: translation and
  necessary explanation → immediately corresponding code → operation/output
  interpretation. Check short cycles for multi-step methods and both reasons:
  why the application needs the method, and why this example teaches the current
  passage. Flag global batching, intervening unrelated material or a link-only
  substitute even when all ingredients and destinations exist. Shared accounts
  may deepen evidence but must not make the local reading unit incomplete.
  Record the first step a reader could not carry out using it. Knowledge recalled
  from the source cannot fill a missing explanation; this check is source-aware.
- **R28 Fresh reading** — When independent accessibility evidence is requested
  or materially useful, give a fresh isolated reader only the frozen output and
  neutral audience brief. Ask for actual understanding, first confusion and
  recoverable concise passages before repairs. Withhold sources, author intent
  and prior reports. A reader primed by notes cannot establish a deck's standalone
  readability. Preserve initial difficulty separately from later source rescue.
- **R29 Rendered output** — Check the current built version, not a stale PDF.
  Inspect every page/slide for a complete visual review; otherwise disclose the
  inspected subset. Test equations/glyphs, readable labels, cropping, figure
  placement, listings and navigation at real reading scale. For PDFs, inspect
  the actual nested bookmark tree as well: source section/method
  parentage, useful added local entries, readable titles and correct destinations.
  Inspect representative landing content for source and added units. A visible
  heading hierarchy, linked contents page or successful body links cannot
  establish that bookmark navigation exists. For code-bearing
  deliverables, inspect every displayed method-code block, including appendix
  listings: its source/link row must appear immediately after that block and
  visibly identify it. Check that the nearby explanation reconstructs the
  substantive operations and their correspondence to body equations/steps;
  correct destinations alone do not establish this. Inspect the preceding
  translation/explanation too: the code must correspond to that operation in
  the same source unit, not be reachable only in a later catalogue. Test its actual links:
  implementation source at the claimed fixed file/function/lines or supplement
  location, matching full code/editable unit, and explanatory body, with return
  routes where separate listings exist. A pre-block link, homepage, generic
  index or shared filename without a matching post-block row is a finding,
  even when a document-wide link checker passes. Check point-of-use citations against their reference entries
  and return links. Open external paper/code destinations and inspect whether
  they reach the intended supporting passage or implementation version/function.
  A live homepage, redirect to unrelated content or HTTP 200 is insufficient.
  Record unsupported page anchors and access failures explicitly. Inspect actual PDF
  annotations/destinations or follow the rendered links; TeX/Markdown markup
  alone cannot establish that the generated links exist or reach the right unit.
  Check that file links/attachments remain usable in the delivered bundle, not
  only at the author's absolute workspace paths. Record untested destinations
  or viewer restrictions as limits, rather than claiming the route works.
  Extraction or build success does not prove visual correctness, source
  fidelity or understanding.
- **R30 Closure and saturation** — Before review, fix the scope and planned
  checks. For a substantial artifact, default to one full evidence-based review,
  one consolidated repair pass, then one targeted recheck of changed claims,
  dependencies and rendered pages. Do not start another full review panel
  automatically. A pass is saturated when it adds no new material, actionable
  finding: a material finding would change a central claim or proof, source
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
  In the reader-facing handoff, distinguish source verification, implementation
  inspection/execution and visual checks, with their actual scope. Do not use
  an unqualified "verified" or mark the requested explanation complete while
  required primary evidence or corresponding implementations remain missing;
  disclosure records the gap rather than waiving it.

Delegate by the evidence needed, with a short task-specific packet and bounded
paths; no named agent persona or fixed model is required. A source-aware auditor
derives expectations before seeing the author's account. If cold isolation or
rendering is unavailable, finish useful checks and state that limit. Never
describe a self-check as independent or retry unchanged work for a favorable verdict.
