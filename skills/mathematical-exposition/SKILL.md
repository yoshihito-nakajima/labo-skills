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

### Carry the argument across adjacent passages

The reader must be able to follow each move from the adjoining text, without
searching elsewhere or inventing the connection. Apply this to sections and
paragraphs, definitions and claims, proofs, figures, equations, code, results
and comparisons, including explanations with no code. At a transition, carry
forward the specific object, result or unresolved question just established;
make clear what the next passage does with it and why that advances the current
purpose. At a new unit's opening, establish this link before introducing a new
task. Recover an earlier dependency locally when needed. A reference or a
phrase such as "next", "as above" or "below we implement" does not supply the
missing connection. Explain what the new step yields for that same purpose.

For structured explanations, follow [subject identity, role skeleton and two-part headings](references/roles-and-headings.md).
Identify the named method or concept before its background; identify the method
and implementation before a code block. A content-specific message does not
replace that subject name.
Fix the role sections and their order from the owning workflow or agreed outline.
Each added section heading shows **role | concrete point**, so the reader sees
both the stable skeleton and what this section will say. Keep source titles and
faithful translation intact; apply this structure to the added explanation.

Preserve those role boundaries while carrying the prose across them. Combine
unnecessary subdivisions within a role, not different required roles into one
unlabeled unit. Do not restart the skeleton at every small operation. Use explicit
bridges where the connection would otherwise be missing, not a fixed recap at
every paragraph. Preserve needed evidence and coverage when merging subdivisions.

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
number, title meaning, order and hierarchy. Establish the application using its
complete background photographs, figures, captions, data meaning and explanation,
then the concrete obstacle, before showing code. Code proximity applies after
this context is understood. Explain how the actual operations produce a property
that addresses that obstacle, with conditions and limits, then compare relevant
methods. Return to the same visible example to make the connection intelligible.
Preserve this flow at the method/application level; multiple code stages should
advance one explanation, not repeat a five-heading template. Retain the complete
existing visual account, and place mixed-role figures by what they help the
reader understand rather than treating all figures as later results.
Apply this to educational/background/auxiliary methods too. Use meaningful
subordinate headings where they help readers find the argument. For substantial
PDFs, follow the reading skill's [navigation rules](../reading-reference/references/explanation.md)
for source-aligned nested bookmarks and added explanatory units.
Follow the reading skill's [document sequence and optional views](../reading-reference/references/paper-preparation.md#keep-section-progression-and-purpose-specific-views-distinct).
After each main section's translation, proceed to the next source section.
Do not add a full reprint merely to create another reading route. Optional
background/explanation and code collections serve distinct reader tasks; retain
the definitions, evidence, visuals and operational context their selected content
needs, repair transitions after extraction, and keep shared claims and status
consistent. Neither collection is mandatory, and neither replaces a complete
local method account. Cite retained claims at the point of use and keep usable
references. For substantial paper preparation, also follow
[supporting-source reading](../reading-reference/references/paper-preparation.md#make-supporting-literature-readable)
for original excerpts and faithful translations of other literature used in the
explanation. Code attribution and explanatory paraphrase do not replace these pairs.
Bounded questions and purely theoretical arguments retain their scope; the
reading skill owns source checks.

## Check the result

For structured explanations, run the [heading audit H1--H5](references/roles-and-headings.md#audit-the-headings-against-the-body):
check role boundaries/order, both title parts, fulfillment by the body, progression
and consistency across comparable units/routes. Then read the explanation in order,
including passages without code. At each
transition, identify from the adjacent prose what is carried forward, why the
next move is needed, and what it contributes. Locate the first boundary where
that cannot be recovered; repair the connection, order or unnecessary split.
Titles, contents lists, links and the presence of all required ingredients do
not establish continuity. Check that each object is defined when first needed,
each inference has enough support for the declared reader, and the emphasis
follows the actual mathematical work. Then check source fidelity and
whether the reader can state what the argument now establishes and what remains
open. Preserve clear concise passages; length alone is not evidence of clarity.

Return the explanation or revised passage first. Keep source boundaries,
unresolved points and any change summary separate from reader-facing prose.
