---
name: mathematical-exposition
description: Explain mathematical papers, proofs and concepts, or improve the clarity, emphasis and pacing of mathematical prose. Use for substantive explanations in chat, reading notes and manuscripts; not for source lookup or build-only work.
---

# Explain the mathematics clearly

Luna and Haiku only collect evidence here and hand substantive work to another agent: [roles](../research-router/references/editing-capability.md).

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

For mathematical definitions, claims, proofs and calculations, apply
[mathematical substance and proof detail](references/mathematical-substance.md).
Purpose and intuition must accompany checkable mathematical content, not replace
it. For lecture materials, this includes intermediate calculations, the reader
threshold, and correcting source defects through their downstream uses.

From the first draft, organize multi-stage proofs by their actual obligations.
For persistent mathematical documents, use [mathematical-navigation](../mathematical-navigation/SKILL.md)
alongside the proof-detail rules. Read the workspace author profile when available;
carry explicit recurring preferences into drafting and checks, not only final polish.

## Write for the reader who must be pulled through

Every substantive explanation follows [reader pull](references/reader-pull.md):
write for the hurried reader, the reader without the definitions and the reader
who cannot fill gaps between lines. Put the conclusion, a picture, why it
matters and the key idea on the first screen; give each section a plain opening
that states its conclusion and a closing that raises the next question.
Define terms as exactly as the paper, using only words already available, with
example and purpose. Write every step's reason. Show the central idea from
several genuinely different angles, connect each concept to those already on
the page, and place figures where they do work. Keep the page self-contained:
links and file paths support the text and never carry it, and repository
paths or internal note names do not appear in reader-facing prose. The
explanation is longer and gentler than the paper, never vaguer. These are jobs
for the prose, not labels: write natural expository prose in which the content
carries the structure, without template signposts such as 「結論：」 or
「ポイントは」 (see [sound like a person](references/reader-pull.md#sound-like-a-person-not-a-template)).

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

Across sections and subsections, keep the chain explicit: each unit's opening names what
it takes from earlier units and what it adds for its parent, and a parent closes with what
its parts established. For a reading note the chain, the reader floor and the sentence-level
gloss of claims that lean on prior results are in
[unit chain and claim gloss](../reading-reference/references/unit-chain-and-claim-gloss.md).

For structured explanations, role sections and headings, computational-method
explanations, optional views and supporting-source reading, follow
[the detailed rules](references/adjacent-passages.md).

## Check the result

Check the mathematical argument and its teachability separately under
[the substance checks](references/mathematical-substance.md#工程を通じた確認).
A sound plan, fluent prose or complete headings do not establish either.

For substantial written artifacts (web pages, HTML, reading companions,
lecture and reading notes, long explanations), do not hand over a first draft:
after the self-checks below, run the [exposition-review](../exposition-review/SKILL.md)
loop with independent flow and critique reviewers. Short chat answers are exempt.

Run the [readability audit P1--P11](references/reader-pull.md#readability-audit)
on the actual text: hurried-reader first screen, headings alone, section
openings alone, undefined terms, gaps, next question, angles, connections,
figures, the no-links test and natural prose. Repair failures before delivery.

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
