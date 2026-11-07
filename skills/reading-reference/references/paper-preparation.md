# Prepare to read and present a paper

Use for substantial close-reading and presentation-preparation materials about
a paper or a specified part. The objective is that the reader can explain the
paper's questions, reasoning, methods and evidence while consulting the original.
Apply to the agreed unit; do not turn a short answer or source search into a
full-paper project. Keep original sources unchanged.

Translation-only requests use
[japanese-translation](../../japanese-translation/SKILL.md), including when the
requested translation covers a whole paper. This expanded preparation contract
applies when explanatory or presentation-preparation materials are requested.

## Source-aligned reading structure

Before drafting or revising, follow [Reading structure](reading-structure.md):
freeze the selected source-unit and role-section map, keep source hierarchy, and
retain the local return to the named target work. That reference owns structure;
this file owns passage coverage, source/translation fidelity and reading evidence.

## Prepare the reader, then return to the source

Use the [preparation-to-source sequence](reading-structure.md#prepare-the-reader-then-return-to-the-source)
and its explicit correspondence and target-original/translation sections. Supporting
literature pairs below have a different role and cannot replace that return.

## Identify and group original/translation units

At every original/translation unit, name the work in a shared heading: author
and a recognizable title or established short title, with the version/year and
exact locator alongside it. Use "[named work]'s original and translation",
not a bare "original" or "application paper" whose identity must be inferred.
Within that identified unit, simple "original" and "faithful translation"
labels suffice; do not repeat the full attribution at every sentence. Keep
the identity visibly associated with both texts after pagination and explicitly
renew it when the source changes. This applies to both the main source and
supporting literature; a survey, method proposal and application study are
distinct works even when they explain the same method.

Choose a complete reading unit, such as a connected paragraph with its equation
and qualifications, rather than scattering isolated one-sentence extracts.
Short passages remain appropriate when they contain the complete point; length
alone is not the criterion. Do not leave an introductory clause detached from
the equation or conclusion it introduces. Group related source links at a
natural boundary of this unit under [R14](explanation.md), with labels such as
"Open [named work], §3, p.4" and access to the bibliography. Preserve each
citation's scope and every source switch; grouping links does not permit losing
point-of-use evidence or replacing missing displayed content with a link.

## Make supporting literature readable

For a paper whose contribution is a method with code, the [method-paper profile](method-paper-profile.md) lists the parts of the note and their owners.

Which works this covers is decided by the [lineage and comparison inventory](lineage-and-comparison.md):
every inherited, compared, criticised, encompassing, encompassed, earlier-version and
origin relationship is inventoried and treated at the level given there. Supplements are
inventoried and read under the [resource ledger](resource-ledger.md).

In substantial explanatory reading material, include the inspected passages from
other works that supply the definitions, assumptions, method design, application
evidence or consequential comparisons actually developed in the explanation.
This applies to method proposals, application studies and predecessors, including
works outside the target bibliography. A code quotation or citation is a separate
form of evidence and does not replace reading the paper passage.

At the relevant explanatory point, provide the source identity and version,
exact section/page/equation/figure locator, original-language excerpt (English
for an English source), and its corresponding faithful Japanese translation
when preparing Japanese notes. Label these separately from added interpretation.
Introduce why the passage is being read and connect it to the surrounding
argument. Related claims may share one coherent passage pair; do not repeat a
quotation mechanically at each citation or collect all pairs in a remote appendix.

Select enough context to preserve the actual claim and its conditions. Inspect
the surrounding text, mark omissions and keep necessary equations, definitions,
figure/caption references and qualifications traceable. Do not reconstruct an
English quotation from a paraphrase or back-translate Japanese into a supposed
original. Follow [translation fidelity](../../japanese-translation/SKILL.md):
preserve assumptions, quantifiers, uncertainty and claim strength; put corrections
or extra reasoning outside the translation. Check the Japanese on its own and
then against the original. An excerpt's translation is not a full-paper translation.

Choose passages by their role in the explanation, not bibliography membership.
Passing citations, reference-only indexes, bounded lookups and translation-only
tasks do not automatically acquire this expanded scope. Respect applicable
quotation/reuse limits; cite and explain the remainder where full display is not
available. Record an inaccessible passage or restricted display as a specific
coverage limit rather than substituting invented text, calling a summary a
faithful translation, or claiming the requested paired coverage is complete.

## Keep section progression and purpose-specific views distinct

Follow [document sequence and optional views](reading-structure.md#keep-section-progression-and-purpose-specific-views-distinct).
That reference owns view scope, main-route progression and bibliography placement.
A request to improve a code or quotation block does not change the reading product
into an explanation-only view or authorize dropping its target-source return.

## Method understanding with literature evidence

For every in-scope method, make the question, required properties, decisive
design, fit/limits and consequential relationships recoverable. This also
applies to noncomputational methods; their reasoning need not be numerical or
empirical.

While reading the method literature, collect each method's lens (what it attends to and
what it is good and bad at), its root's shared example, its specific example and its
limit example, with their sources, under [roots and lenses](roots-and-lenses.md#collect-them-while-investigating-the-sources);
then list the questions the paper leaves open and search for them as in
[let the card decide what to search](roots-and-lenses.md#let-the-card-decide-what-to-search).

For computational methods, follow [Applications to code](application-to-code.md).
Within each section/subsection, connect the actual application problem, need and
obstacle, pipeline/mechanism, published result and significance to the code.
Explain why the study uses the method and why this example is introduced here.
Bring the existing application background, photographs, figures, captions and
their reading into the method's introduction before code; make the target and
obstacle concrete. Follow [whole before part](application-to-code.md#show-the-whole-implementation-before-its-parts)
inside the method account. Keep each selected operation near its mathematical
explanation, then explain the operations' specific strengths and fit to that
obstacle and their limits, followed by method relationships. Multi-step methods
advance this same account without restarting a template for every snippet.
Classify visuals by their explanatory roles, including mixed roles, rather than
putting all figures after code. Preserve the internal order of source/translation
and identify added material clearly under the source-return sequence above. Apply this to educational/background/auxiliary code.
For noncomputational proof methods, explain the question, hypotheses, decisive
argument and consequences without inventing an empirical application.

Use inspected primary passages for the motivation, inherited ideas, new
contribution and every historical/comparative assertion. Inspect both sides of
a comparison; do not infer novelty from missing citations or a failed search.
Bring in predecessors and other literature needed to explain these relationships,
including works outside the target bibliography. Their number may substantially
exceed that of the target paper; relevance and resolved dependencies determine
the stopping point, not a citation budget or an exhaustive history.

Place a labelled link to the supporting passage beside the claim or coherent
group of claims it supports, with the paper identity and exact
section/page/equation/figure. Make the citation's extent unambiguous and renew it
when the source changes; do not split connected prose merely to repeat a link
after each sentence. Prefer direct page/section anchors; if unavailable, link
the document with a visible exact locator and state
the navigation limit. Distinguish a source's explicit statement from the note
writer's synthesis, providing the latter's premises and reasoning. If evidence
cannot be inspected, mark the claim provisional and the required dependency open.
Do not manufacture a citation to make an unsupported explanation look grounded.

## Mathematics, code and interpretation

Each explained computational method needs corresponding code; this is part of
paper preparation even if code was not separately requested. Use the selection,
reuse and execution rules in [Methods](methods.md). Proof techniques without a
computational procedure use its mathematical branch; do not invent a numerical
substitute for a proof or fabricate an algorithm for a noncomputational method.

Preserve the section-local presentation above. In each explanation/code cycle,
trace inputs → mathematical objects/equations/steps → code operations
→ outputs → interpretation. Explain input/output meanings and match substantive
variables, functions and line ranges to the source mathematics. Show an example
chosen to expose the method's purpose or a consequential difference/limit, and
explain what its result establishes. Distinguish execution from static inspection.
Supply complete selected executable units and necessary helpers in editable form;
a library call, pseudocode or unrelated toy alone is not method implementation.
Apply [R20](methods.md) to every displayed method-code block: explain its
contents and equation/step correspondence locally, and place its specifically
identified implementation-source and full-code links immediately after it.
Use the return routes and PDF placement rules in [Explanation](explanation.md).

At each method/code unit, distinguish explicitly:

1. the **target paper** currently being read;
2. the **method literature**, including the proposal or later modification and
   the exact procedure implemented;
3. the **application study**, its actual need, method placement and reported results;
4. the **implementation source**, its author, revision/version, file/function
   and status (author implementation, later author version, adaptation,
   third-party implementation or independent teaching code).

Do not use “original paper/code” as the sole identification. One work may occupy
more than one role, but the roles must remain clear. Prefer corresponding,
inspected and reusable author code. Record scoped search and access outcomes
honestly; finding a repository does not mean inspecting its code.

Apply [R18](methods.md) per literature-based code unit, including added teaching
examples and background methods. Identify the exact method source, follow its
implementation pointers, inspect matching code when found, and report checked
places, access/inspection status and the adoption or independent-code rationale
at the code's reader-facing location. Unfollowed pointers remain unfinished
source work; neither a private search log nor the educational label waives it.

For independent code, explain especially carefully why it was written, how each
substantive operation realizes cited mathematics, its own choices and departures,
what the example teaches and the evidence for correctness. Link the exact source
passages alongside this explanation. A disclaimer that code is independently
written does not discharge these obligations. Missing author code does not waive
the requirement for a transparent corresponding implementation.

## Completion conditions

Before declaring the agreed unit complete, check the actual delivered artifact:

- Every in-scope source section/subsection retains its number, title meaning,
  order and hierarchy, with corresponding original text, faithful translation
  and distinct substantive explanation in that unit.
- Before the first code in each method account, the reader can identify the
  actual target, desired output and obstacle from the presented application,
  including its background photographs/figures, captions and explanation.
  Before the first detailed excerpt, the input-to-output flow and complete
  selected implementation have already been displayed with necessary dependencies.
  A later listing or a link alone does not fulfill that order. Corresponding
  operations stay near their mathematical explanation; their specific fit
  to that same obstacle and its limits are explained before method comparisons.
  The stages form a connected account instead of repeated generic templates.
  Preserve the practical need and the reason for choosing the example here.
  An optional collection keeps the material needed for its declared task without
  replacing any required local explanation. Shared implementations and evidence
  remain identifiable and reachable from each place that uses them.
- Adjacent passages carry the argument forward under [R27](review.md), including
  sections without code. The heading audit H1--H5 checks fixed role boundaries
  and order, role plus concrete point, fulfillment by the body, progression and
  consistent use across comparable units within each view's scope. Openings take
  up the preceding content; a correct-looking two-part title does not supply that
  connection. For PDFs,
  inspect the actual bookmark tree for source sections and required added units, checking nesting, titles and targets;
  inspect source and added-unit landing content. A populated contents page or
  accurate prose alone does not establish this navigation.
- In preparatory reading order, each source unit's background and explanation
  precede its original/translation; the immediately preceding correspondence
  tells the reader what to look for and where. Check this inside each owning
  subsection, not only at the end of a larger method or chapter. Source-internal
  order, wording and the boundary between interpretation and translation remain
  intact. A moved source block without preparation/correspondence is insufficient.
- The subject is named before its background, and each code block names the
  method and implementation before the listing. Content-specific messages or
  post-code provenance alone do not fulfill that entrance identification.
- Supporting literature used substantively has located original excerpts and
  corresponding faithful translations at the relevant explanatory points.
  Inspect context, omissions and mathematical conditions; distinguish these pairs
  from paraphrase, added explanation and code provenance. Both main-source and
  supporting pairs have an unambiguous named-work heading, coherent passage
  boundaries and source links whose destination and coverage can be recognized.
- Read across source-section boundaries: each main unit's translation leads to
  the next source unit. Optional collections have distinct purposes and preserve
  needed dependencies after extraction. The common bibliography is last; each
  view cites retained claims, equations, figures, code operations and comparisons
  locally. Neither the final list nor a post-code source row substitutes for this.
- Each computational method has matching complete code, local attribution,
  mathematics-to-operation correspondence and meaningful example interpretation.
  Independent implementations include design/deviation and validation explanations.
- Body, formal references, code excerpts, full code and editable files have the
  required matching routes. Test built-artifact destinations, not source markup.
- Open the external links and inspect the intended documents/passages and code
  files/functions at the claimed versions. Record actual checks in existing notes;
  HTTP success, an unchecked URL or a homepage alone is insufficient. Test page
  anchors where supported, and disclose unsupported anchors or access barriers.
- Source fidelity, code inspection/execution and rendered usability are checked
  separately under [Review](review.md), without claiming reader comprehension.
- Read each view against its declared task, then compare shared claims, exact
  locators, status labels, limits and return links. Check for orphaned references
  and assumptions after filtering; do not demand full-main-text duplication.

- Coverage records (resource ledger, lineage inventory, unit chain, claim gloss) are kept as
  data and `scripts/check_coverage.py` passes, with every open entry either resolved or
  accepted in writing by the user. A stand-in exists only with the user's per-resource permission, is labelled AI-created, and does not close an entry.

Missing required translation, explanation, primary evidence, code or navigation
remains incomplete work even when disclosed. Deliver useful checked units and
state remaining scope and blockers accurately; do not shrink the agreed task or
call an interim summary complete. No fixed manifest or additional review panel is
required to apply these conditions.
