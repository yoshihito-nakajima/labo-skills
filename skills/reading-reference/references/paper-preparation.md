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

Retain the target paper's section and subsection numbers, titles' meaning, order
and hierarchy as the reading backbone. Keep translation, local explanation,
application context and corresponding implementation within that source unit.
Do not flatten original subsections into paragraphs or move their substance to
a later generic supplement. Clearly label added commentary or subordinate boxes
without changing or impersonating the source hierarchy. Keep source and
added equation/figure numbers distinguishable. For a bounded request, retain the
original numbers of the selected sections rather than renumbering them from one.

Use meaningful subordinate headings for added explanation so that application
requirements, the reason for using the method/example, code correspondence,
results/scope and method relationships can be found locally. In a PDF, make the
source hierarchy and these useful added units directly reachable through nested
bookmarks under [R14](explanation.md). Distinguish actual PDF bookmarks from
visible headings, the table of contents and ordinary hyperlinks. Keep the short
explanation/code cycles below while adding this structure.

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

For every in-scope method, make the question, required properties, decisive
design, fit/limits and consequential relationships recoverable. This also
applies to noncomputational methods; their reasoning need not be numerical or
empirical.

For computational methods, follow [Applications to code](application-to-code.md).
Within each section/subsection, connect the actual application problem, need and
obstacle, pipeline/mechanism, published result and significance to the code.
Explain why the study uses the method and why this example is introduced here
for the reader. These dependencies do not require an extended standalone account
before any code: place the corresponding implementation immediately after each
passage's translation and necessary explanation, then interpret its operations
and outputs. Use short cycles for multi-step methods. Apply this to educational,
background and auxiliary code, including relevant method/implementation relationships.
For noncomputational proof methods, explain the question, hypotheses, decisive
argument and consequences without inventing an empirical application.

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
- Each computational passage leads directly from translation/necessary
  explanation into its corresponding code and operation/output reading. Local
  application context states both the practical need and the reason for choosing
  that example here, with inspected results and method/code relationships.
  Shared accounts and full listings supplement, rather than replace, this content.
- Added application/requirements and code-correspondence explanations have
  identifiable local headings. For PDFs, inspect the actual bookmark tree for
  source sections and required added units, checking nesting, titles and targets;
  inspect source and added-unit landing content. A populated contents page or
  accurate prose alone does not establish this navigation.
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
