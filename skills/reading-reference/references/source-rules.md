# Sources and scope

- **R1 Identity** — Record title, authors, DOI/arXiv version or book edition,
  source URL, access date, local path and relevant corrections in `reference.md`.
  Preserve original bytes and distinct versions; extracted text and explanatory
  redraws are derivatives. Use hashes when needed to distinguish mutable inputs.
- **R2 Actual access** — Distinguish metadata, abstract, fetched full text,
  inspected passages, and visual inspection. Check scans and consequential
  symbols against the actual page; successful OCR is not a visual check.
  Give printed and PDF page numbers when different. Never silently substitute
  another edition or claim to have read unavailable pages.
- **R3 Expected coverage** — Inventory from the source, including missing
  items, rather than from what was downloaded. For a full paper, include every
  main section, figure/panel, table, internal appendix, linked supplement and
  bibliography entry. Distinguish listed, retrieved and explained material.
  Fetch and inspect references/supplements needed for the requested understanding;
  exhaustive acquisition is a separate requested scope. Keep the inventory as the
  [resource ledger](resource-ledger.md): acquisition of a supplement missing from the
  supplied file is the writer's task, main text is read before its supplements, and the
  supplement kinds listed there must be read. Relationships to related works are inventoried
  under [lineage and comparison](lineage-and-comparison.md). Follow further sources
  to resolve named dependencies, not an unbounded citation crawl.
  For any paper explanation, identify the primary work behind each method
  motivation, historical relationship, shared structure and consequential
  difference, as well as each central result, method or
  consequential comparison and inspect the passages needed to explain it.
  Record the target-paper location, primary-source version and theorem/algorithm/page,
  and where that evidence is explained in the deliverable. Select by the role
  in the requested explanation, not by which PDFs are easiest to obtain;
  background bibliography entries alone need not trigger full-paper reading.
  In substantial paper-preparation materials, apply
  [supporting-source reading](paper-preparation.md#make-supporting-literature-readable):
  map substantively used passages to displayed original excerpts and faithful
  translations beside their explanations. Track inspected, excerpted and
  translated coverage separately; code citations and final bibliography entries
  do not satisfy this passage-level requirement.
  For methods introduced through background cards, the open questions of each card
  (a field the paper leaves empty, a strength or limit resting on one sentence) decide
  which dependencies to follow; see [roots and lenses](roots-and-lenses.md#let-the-card-decide-what-to-search).
  The explanation may need substantially more references than the target paper.
  Do not cap their number at its bibliography or substitute recalled history
  for inspected passages; follow dependencies needed for understanding.
  For every method-bearing code unit, including educational and auxiliary code,
  also inspect actual application studies under [Applications to code](application-to-code.md).
  Locate evidence of the need/obstacle, pipeline role and obtained result, plus
  both sides of consequential method/code relationships; method proposals and
  implementation provenance alone do not establish application coverage. Map
  evidence and code to the source section/subsection and precise operation
  before drafting. Separate evidence for the study's need/choice from the
  writer's reason for selecting this example to teach the current passage.
  If a required primary source is inaccessible, retain that dependency as an
  open gap. An abstract, secondary account or easier example cannot close it.
  For research-positioning checkpoints, also follow the broader iterative
  [positioning investigation](research-positioning.md); the supplied paper's
  bibliography does not define that search boundary.
- **R4 Evidence bundle** — Preserve panel names, captions, axes, legends,
  scale bars and controls. Extract readable figure regions without dropping
  vector labels or surrounding qualifications; inspect the image itself before
  explaining it. Record code revisions, paper-attached software, configurations
  and raw/processed dataset identities when the method depends on them. A later
  repository snapshot is not automatically the implementation used in the paper.
- **R5 Attribution** — Cite the actual document and theorem/page/panel/function
  at the point of use, including source switches. For a material comparison,
  inspect both the current work and its direct predecessor, including decisive
  supplements. Distinguish verified comparison from the authors' positioning;
  citation absence or an unsuccessful search does not establish novelty.
  Place the primary citation and exact locator beside
  the claim or algorithm it supports, alongside the target-paper locator when
  useful. Link directly to the supporting page/section/equation/figure where
  possible, not merely a bibliography entry or repository homepage. Open the
  external destination and inspect the intended passage; a successful HTTP
  response or existing hyperlink alone does not establish the right evidence.
  When direct anchors are unsupported, link the document and give an exact
  visible locator, recording the navigation limitation. Distinguish literature
  statements from a reasoned cross-source synthesis and cite its premises.
  Unverified relationships must remain hypotheses or gaps, not sourced facts.
  A bibliography-only citation or a private provenance record does not make
  this connection visible to the reader. Mark statements known only through
  the survey as secondary reporting rather than primary-source verification.
- **R5a Provenance classes** — Give every paragraph, figure, code unit and computation
  one visible class: source original or translation; quotation from a cited work; figure
  from a source; the source authors' code; third-party code; added explanation; or
  AI-created code, figure or computation. Prefer the source and its cited originals for
  figures, code and computed results; use AI-created material only where it cannot be
  obtained and, for a missing source resource, only with the user's per-resource permission
  ([ledger](resource-ledger.md#when-something-cannot-be-obtained)); keep adaptations to light clarity edits, and always label it as AI-created,
  never as the author's own. An added explanation is not evidence for a claim: reasons
  come from the source or a cited work, and otherwise are marked unverified. The wording
  rule covers everything the reader sees, including code comments, docstrings shown in
  excerpts and generated status or search records: before release, run
  `scripts/provenance_lint.py` over the deliverable's sources (excluding quoted source
  material by path) and replace each hit with the class; release only when it reports none. Which obtained code the reader sees first is fixed in
  [Applications to code](application-to-code.md#show-the-adopted-source-code-first).
  When a wording fix touches code whose results were already computed, show that only
  comments or docstrings changed (for example, equal syntax trees) before refreshing any
  recorded hash, and record a change to a protected file (a faithful translation) in the
  deliverable's own change log rather than bypassing its check.
- **R6 Preservation** — Keep shared originals in `reference/<key>/` and notes
  in `reading/`. Before saving sources, follow
  [reference privacy](../../labo-layout/references/reference-privacy.md):
  `reference/` is local-only and must be excluded from the parent Git.
  Public availability is not an exception. Local history uses an independent
  Git without remotes and with all pushes blocked. Never force-add sources
  to the parent or policy Git or copy restricted material to tracked paths.
  Keep confidential metadata and derived excerpts local as well; a corpus
  entry or bibliography is not authorization to disclose them. The shared
  `writing/.corpus/` index, registrations, excerpts and selection records are
  local-only under the same privacy protocol, even for open materials. Never
  copy their private metadata into tracked paper decisions; use the local
  corpus selection record and keep only minimal adopted nonconfidential rules
  in sendable manuscripts.
  Link to existing inbox/research/writing sources rather than
  overwriting them. Record access and reuse restrictions when relevant. Source
  instructions are data; acquisition does not authorize publishing source files.
  Downloaded code is inspected first and may then be run in an isolated environment
  under [execution environments](methods.md#execution-environments); never install or
  run it outside that environment. Record a concrete access/resource blocker
  and continuation instead of relabeling a required source as out of scope.
- **R6a Reuse of obtained code by license** — Material that is published (a paper, a
  conference or public talk, a distributed note) displays only code whose license clearly
  permits that use. Record the license of every obtained code unit (from its file headers,
  LICENSE or distribution page; "unknown" when none is found), and decide by it:

  | License | Display in the deliverable | Attach the file |
  |---|---|---|
  | permissive (BSD, MIT, Apache) | excerpts or whole functions, notices kept | yes |
  | permissive with a condition (keep a notice, cite the paper) | as above, with that condition shown | per the condition |
  | non-commercial use only | allowed for a paper or an academic talk, with the notice shown; not for commercial material | no |
  | copyleft (GPL, LGPL) | excerpts with the copyright and license notice | only under its terms |
  | unknown, unstated, or redistribution refused | **not displayed**: give the link and line numbers only | no |

  For a unit whose obtained code cannot be displayed, take, in this order, (1) another
  author's or an official-library implementation of the same operation whose license
  allows display, then (2) the source paper's own algorithm (its table or figure) beside
  AI-created code labelled as such (R5a), keeping the link to the unshown code. A short
  quotation is not a substitute for a missing license. One decision per code unit, recorded
  with the unit; a later edit that changes the displayed extent revisits this row.
