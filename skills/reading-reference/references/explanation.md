# A reader's route through the argument

- **R7 Reader floor** — State what the reader can already use and what they
  should be able to reconstruct. For an undergraduate mathematical explanation,
  default to calculus, linear algebra and basic proof experience, with specialist
  concepts taught as needed. Mathematical expertise does not imply biological,
  statistical or software expertise. Honor a more specific audience.
- **R8 Progressive depth** — Identify the named concept/method at its unit
  entrance, then start with the question, the plain-words conclusion and an
  accurate concrete picture (see [reader pull](../../mathematical-exposition/references/reader-pull.md)), then deepen into the statement, proof/method and consequences. Bring
  in a prerequisite when its role becomes visible. A natural stopping point
  leaves the reader with a useful result, mechanism or newly usable tool.
  Avoid a front-loaded glossary or an unrelated textbook survey. For substantive
  computational-method explanations, use the connected local accounts in
  [Applications to code](application-to-code.md). Explain the application need
  and why the example belongs here using the complete visible context before
  code, then introduce the overall computation and complete selected implementation
  before examining its parts. Keep meaningful mathematical/code stages and their fit to that
  problem together. Do not reset the application at each small excerpt. Do not scatter
  ingredients across global translation, application and code collections.
  Keep main source units consecutive through their translations. Optional
  collections serve distinct tasks and preserve the dependencies of their
  selected content under [Paper preparation](paper-preparation.md#keep-section-progression-and-purpose-specific-views-distinct).
  Do not add a whole-document duplicate or use a collection to repair a missing
  local explanation.
- **R9 Local bridges** — Before using an object, supply its type/domain,
  notation and needed structure. Connect each important inference to its inputs
  and justification. Apply
  [adjacent-passage continuity](../../mathematical-exposition/SKILL.md#carry-the-argument-across-adjacent-passages)
  across all prose and displays, not only code: each new unit takes up the
  preceding result or question and makes its next purpose intelligible. Check
  the opening before the new content, and the meaning gained after it. A
  permitted background black box needs a usable statement,
  applicability and source. Do not black-box the decisive argument requested
  for explanation or repair its missing proof without labeling the addition.
- **R10 Emphasis** — Spend explanation on the obstacle and the step that
  resolves it; routine supported steps may be brief. Repeat a definition,
  condition or figure key when it makes a resumed passage understandable.
  Judge repetition by its teaching role, not by word count. Place cautions at
  the inference they protect; do not add a warning, exercise or recap by ritual.
- **R11 Fidelity** — Preserve the source's hypotheses, generality, quantifiers,
  normalizations, uncertainty and exceptions through prose, formulas and figures.
  Label source statements, checked derivations, analogies, pedagogical examples
  and open gaps. For source-aligned paper preparation, retain the source section order and
  numbering and section/subsection hierarchy under [Paper preparation](paper-preparation.md). In other formats,
  reorder when useful with a route back to source locations;
  an easier special case cannot replace an in-scope general result.
- **R12 Evidence in view** — Put the actual relevant figure/panel beside its
  substantive explanation at a readable scale. Identify what to compare, the
  named/color-coded marks, quantities, conditions and supported inference.
  Explain controls and limits as well as headline results. A caption paraphrase,
  an inaccessible link or a distant collection of plates is not the explanation.
  Preserve existing background photographs, input examples, captions and their
  reading as part of the application account. Place them before code when they
  establish its target or obstacle. Mixed-role result figures may be previewed
  there and revisited later; do not send every figure to an after-code results
  block. Retain these visuals in views whose arguments depend on them, even when
  their files are stored once. Label faithful redraws and illustrations; never
  fabricate measured evidence.
- **R13 Operational understanding** — If the reader wants to repeat a method,
  teach one continuous path from inputs through operations to outputs. Keep
  formulas, code behavior and interpreted results locally connected. Introduce
  the overall computation and display the complete selected implementation before
  its detailed walkthrough under [the whole-before-part rule](application-to-code.md#show-the-whole-implementation-before-its-parts).
  Longer surrounding modules and ancillary code can live in explained appendices
  with editable sources; they do not replace this initial complete unit.
  When code is requested or required for paper preparation, let the reader
  follow each in-scope computational method from its
  cited primary-source steps to the essential executable unit and the result
  interpreted at that point. Establish the application with its visual context
  and obstacle first; this takes precedence over putting code immediately after
  a translated sentence. During the walkthrough, keep code near its mathematical explanation and
  explain operation → property → effect on that obstacle → conditions/limits,
  followed by relevant method comparisons. Develop a multi-step method as one
  connected account, rather than repeating a template at every excerpt. Follow
  [Applications to code](application-to-code.md); links to shared evidence or
  full listings do not replace this content.
  A code collection must remain usable for its declared task, with necessary
  operation explanations, dependencies, source identity and execution status.
  Link to the full local argument without requiring its wholesale repetition.
- **R14 Usable navigation** — Keep source and local figure numbers distinct,
  and apply [mathematical-navigation](../../mathematical-navigation/SKILL.md)
  from the first draft of persistent mathematical notes. Preserve source locators
  separately from local counters; register required indexes at the definitions
  and formulas, and check actual PDF destinations as well as link colors. Then
  use descriptive equation/code labels and working links where supported, and
  test a route from explanation to evidence and back. Make the clickable extent
  and destination recognizable: name the work and location for a paper link,
  or the implementation and action for a code link. Group related links at a
  coherent passage/code boundary; avoid chains of tiny links and repeated
  one-sentence navigation that interrupt the argument. Preserve local attribution
  and the compact post-code source row below. For substantial PDFs,
  provide a nested bookmark outline matching the source section/subsection
  hierarchy, with useful added explanatory units subordinate to the relevant
  source section or method. Retain the fixed role sections of the owning contract
  or agreed outline, with [role | concrete point](../../mathematical-exposition/references/roles-and-headings.md)
  in each visible heading and its bookmark. Check role boundaries/order and both
  parts of the title against the body under H1--H5; do not infer a hidden role from
  content under another section. Group related operations within their role rather
  than restarting the whole skeleton for every excerpt. Add subordinate operation
  headings only when they aid reading and navigation. Preserve the
  source's numbering, titles' meaning and parentage and distinguish added labels.
  Do not turn every paragraph or citation into a bookmark. Inspect the built PDF's actual outline:
  check required entries, readable titles, nesting and destinations, then inspect
  representative landing content for both source and added units. Correct
  headings or a linked contents page cannot prove that these bookmarks exist
  or reach the intended passage. Link point-of-use
  citations to their formal entries when a reference list is present, with
  return links to the relevant method/code passages. Link each body excerpt to
  the matching complete unit already introduced, and provide return links from
  that unit to the detailed explanation. Optional code indexes or delivery
  appendices may add routes without changing the first reading order. Immediately
  after every displayed method-code block, including appendix listings, place
  an explicit source/link row identifying that particular block. Before the block,
  visibly name the method and implementation under the subject-identity contract;
  its post-block source row serves a different purpose. Follow
  [R20](methods.md) for implementation identity, exact code destinations and
  the accompanying explanation. A link only before the block, at the start of
  a section, or in a distant index does not meet this placement requirement.
  In PDFs, keep the row with the end of its code block in reading order and
  avoid separating it onto an otherwise unrelated page. Give a working link
  to the complete editable implementation as delivered.
  Plain filenames, colored text, a table of contents or viewer history do not
  supply these routes. Do not require an appendix merely to create navigation.
  Give optional collections their own purpose-labelled bookmark subtrees after
  the main sequence, with links to matching main units. Inspect their landing
  content against their declared scope, not against full-main-text coverage.
  Main-route next-section links lead to the next source unit. Cite retained
  claims, equations, figures, code operations and comparisons locally, with
  inspected locators and access to the common final bibliography. A final list
  or post-code source row alone does not supply these citations. Test navigation
  after filtering content; a working link cannot replace a prerequisite needed
  to read the selected explanation or use its code.
  Source attachments retain their evidential role; reproducing a paper or
  listing does not itself teach it.
  For other formats that change teaching order, give a short correspondence
  to the original.

For each central contribution, connect the question and prior capability to
what is retained or changed, the new evidence and its limits. Use the method
understanding contract in [Paper preparation](paper-preparation.md) for detailed
method explanations. Ground motivation, inherited structure, novelty and
comparisons in inspected literature; distinguish authors' statements from an
added synthesis. Reuse, confirmation and negative results can be substantive
contributions; do not force superiority or an exhaustive history onto background
references.
