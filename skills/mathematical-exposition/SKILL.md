---
name: mathematical-exposition
description: Explain mathematical papers, proofs and concepts, or improve the clarity, emphasis and pacing of mathematical prose. Use for substantive explanations in chat, reading notes and manuscripts; not for source lookup or build-only work.
---

# Explain the mathematics clearly

Before substantive work, follow [eligibility and handoff](../research-router/references/editing-capability.md).

For each request, follow the [research-router consultation](../research-router/references/consultation.md).

Use this skill when the task centers on explaining a mathematical argument,
bridging a needed concept, or improving how mathematical prose guides its
reader. Keep the owning workflow in charge:

- For source-based notes or paper explanations, use [reading-reference](../reading-reference/SKILL.md) for source versions, coverage and deliverables.
- For a research manuscript, use [paper-writing](../paper-writing/SKILL.md) for authorship, scope and production.
- For an undergraduate lecture note, also use [undergraduate-lecture](../undergraduate-lecture/SKILL.md) for its reader floor.

An ordinary chat explanation stays in chat. A request to explain does not by
itself authorize file edits, publication or a full manuscript workflow.

## Set the reader and scope

Use the audience, source/version, question and requested depth already present
in the task. Ask only when a missing choice would change the explanation.
Inspect the actual source and the dependencies needed for the argument; a title
or abstract does not establish an unseen proof. If the source is unavailable,
explain what can be established independently and mark the boundary.

Before drafting, identify what the reader should be able to reconstruct and
which background results may be used as stated tools. Do not create a separate
plan document for an ordinary explanation.

## Build a usable route through the argument

Make the question, claim, main obstacle and decisive move visible. Introduce
objects, notation, hypotheses and technical terms before they carry an
inference. Connect each important step to its inputs, reason and conclusion.
For an external theorem used as a black box, state the usable result, verify
that its hypotheses apply, and give a source location when available. Explain
the decisive argument when that is what the user asked to understand.

Spend more explanation at a change of viewpoint or a non-obvious inference.
Move through routine supported steps compactly, with their reasons still
recoverable. Repeat a definition or condition when the reader needs it again at
the point of use. Put a caution beside the specific tempting mistake it
prevents; do not add warnings, examples, roadmaps or recaps by quota.

Keep source assertions, checked derivations, illustrative examples and new
claims distinguishable. Preserve hypotheses, quantifiers and limits. If a
proof gap remains, identify the unresolved implication instead of smoothing
it into finished prose.

For substantive computational-method explanations, follow
[the application-to-code contract](../reading-reference/references/application-to-code.md).
Keep each source section/subsection as a coherent reading unit, preserving its
number, title meaning, order and hierarchy. Place the operation's code immediately
after its translation and necessary explanation, followed by operation/output
interpretation; use short cycles for multi-step procedures. Explain both why
the application needs the method and why this example is introduced here for
the reader. Application problem, requirements, mechanism, published result and
code remain connected dependencies, not a long mandatory block delaying all code.
Explain relevant method/code relationships locally, including shared/changed
operations and consequences, for educational/background/auxiliary methods too.
Give these local purposes meaningful subordinate headings so the reader can
find the application requirements and code correspondence. For substantial PDFs,
follow the reading skill's [navigation rules](../reading-reference/references/explanation.md)
for source-aligned nested bookmarks and added explanatory units; preserve the
short operation/code cycles rather than collecting long prefatory sections.
Bounded questions and purely theoretical arguments retain their scope; the
reading skill owns source checks.

## Check the result

Read the explanation in order. Check that each object is defined when first
needed, each inference has enough support for the declared reader, and the
emphasis follows the actual mathematical work. Then check source fidelity and
whether the reader can state what the argument now establishes and what remains
open. Preserve clear concise passages; length alone is not evidence of clarity.

Return the explanation or revised passage first. Keep source boundaries,
unresolved points and any change summary separate from reader-facing prose.
