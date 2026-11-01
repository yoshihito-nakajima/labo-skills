# Prepare to read and present a paper

Use for substantial close-reading and presentation-preparation materials about
a paper or a specified part. The objective is that the reader can explain the
paper's questions, reasoning, methods and evidence while consulting the original.
Apply to the agreed unit; do not turn a short answer or source search into a
full-paper project. Keep original sources unchanged.

## Source-aligned reading structure

Retain the target paper's main section numbers, titles' meaning and order as the
backbone. Put prerequisites, implementation commentary and cross-method synthesis
under clearly identified supplemental subsections or boxes. Keep source and
added equation/figure numbers distinguishable. For a bounded request, retain the
original numbers of the selected sections rather than renumbering them from one.

Account for the in-scope original text and provide a faithful translation into
the requested language (Japanese for Japanese reading materials). Present the
original passage and its translation in a clearly corresponding form, with exact
source locations; do not silently omit difficult passages or replace translation
with a summary. Preserve qualifications, assumptions, notation and uncertainty.
Label an ambiguity or suspected error rather than silently correcting the author.
Separate original text, translation and added interpretation. A source attachment
or a link alone does not replace the requested original-text/translation coverage.

After the faithful rendering, explain what each passage is saying, its role in
the argument and how it connects to adjacent passages. Explain mathematical
objects, hypotheses and decisive steps where used. For each figure/table,
provide its caption translation and explain the quantities, conditions, visible
patterns, supported inference and limits. Show the relevant visual at a readable
scale; merely paraphrasing its caption is insufficient.

## Method understanding with literature evidence

For each in-scope method, make the following connected reasoning recoverable:

- **Question:** what objects or observations are analyzed, and what needs to be
  understood about them? Explain why the question matters in this paper.
- **Requirements:** what must be preserved, distinguished, estimated or tested
  to answer it? State the relevant assumptions and what counts as success.
- **Design:** why do the definitions, theoretical framework, objective and
  operations serve those requirements? Explain the mechanism, not just symbols.
- **Fit and limits:** which properties of the target make the method appropriate,
  what conclusions its outputs support, and when assumptions or design fail.
- **Relationships:** what purpose, assumptions or mathematical structure is shared
  with relevant methods, exactly where they diverge, and what that divergence
  changes in computation or interpretation. Distinguish a special case, variant,
  extension, alternative theory for the same question and a different question.

Use inspected primary passages for the motivation, inherited ideas, new
contribution and every historical/comparative assertion. Inspect both sides of
a comparison; do not infer novelty from missing citations or a failed search.
Bring in predecessors and other literature needed to explain these relationships,
including works outside the target bibliography. Their number may substantially
exceed that of the target paper; relevance and resolved dependencies determine
the stopping point, not a citation budget or an exhaustive history.

Place a hyperlink to the supporting passage beside each such claim, with the
paper identity and exact section/page/equation/figure. Prefer direct page/section
anchors; if unavailable, link the document with a visible exact locator and state
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

Connect analysis question → mathematical objects/equations/steps → code operations
→ outputs → interpretation. Explain input/output meanings and match substantive
variables, functions and line ranges to the source mathematics. Show an example
chosen to expose the method's purpose or a consequential difference/limit, and
explain what its result establishes. Distinguish execution from static inspection.
Supply complete selected executable units and necessary helpers in editable form;
a library call, pseudocode or unrelated toy alone is not method implementation.
Use point-of-use links between explanation, matching full code and sources, with
return routes according to [Explanation](explanation.md).

At each method/code unit, distinguish explicitly:

1. the **target paper** currently being read;
2. the **method literature**, including the proposal or later modification and
   the exact procedure implemented;
3. the **implementation source**, its author, revision/version, file/function
   and status (author implementation, later author version, adaptation,
   third-party implementation or independent teaching code).

Do not use “original paper/code” as the sole identification. One work may occupy
more than one role, but the roles must remain clear. Prefer corresponding,
inspected and reusable author code. Record scoped search and access outcomes
honestly; finding a repository does not mean inspecting its code.

For independent code, explain especially carefully why it was written, how each
substantive operation realizes cited mathematics, its own choices and departures,
what the example teaches and the evidence for correctness. Link the exact source
passages alongside this explanation. A disclaimer that code is independently
written does not discharge these obligations. Missing author code does not waive
the requirement for a transparent corresponding implementation.

## Completion conditions

Before declaring the agreed unit complete, check the actual delivered artifact:

- Every in-scope source section has its original numbering and order, corresponding
  original text, faithful translation and distinct substantive explanation.
- Each method has a recoverable question-to-design-to-interpretation account,
  with relevant relationships grounded in inspected literature at linked locations.
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

Missing required translation, explanation, primary evidence, code or navigation
remains incomplete work even when disclosed. Deliver useful checked units and
state remaining scope and blockers accurately; do not shrink the agreed task or
call an interim summary complete. No fixed manifest or additional review panel is
required to apply these conditions.
