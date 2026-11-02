---
name: paper-structure
description: Design or reassess the whole-paper architecture of a mathematical manuscript from its question, results and proofs, with section roles and dependency-safe reading routes; not introduction-only work or prose rewriting.
---

# Mathematical paper structure

Before substantive work, follow [eligibility and handoff](../research-router/references/editing-capability.md).
For each request, follow the [required consultation](../research-router/references/consultation.md).

Use this skill for a new paper's architecture, an existing paper's structural
diagnosis, or a proposed merge, split or relocation of sections. Infer the
reader and requested artifact from the task. A review produces a report; a
design produces a concrete outline. When manuscript edits are requested,
[paper-writing](../paper-writing/SKILL.md) owns those edits. For the introduction's
question, stakes and telling order, use [paper-introduction](../paper-introduction/SKILL.md).
For a correctness audit, use [paper-referee](../paper-referee/SKILL.md); structural
plausibility alone cannot establish a proof.

## Recover the paper's argument

Read the abstract and current section openings before author explanations or
plans when assessing an existing draft. Record the question and argument they
actually convey. Then inspect the main statements, decisive proof steps and
relevant source evidence. Compare this recovered route with the intended one;
record missing mathematical bridges as gaps rather than inventing results to
make an outline work. If only notes exist, anchor the outline to established
results and explicitly conditional or open ingredients.

For a standard Labo TeX manuscript with `main.tex` and `sections/`, resolve
`../../scripts/labo.py` from this skill's real directory and use
`paper map --paper <slug> --format json` to inspect the literal assembly and
openings, then `paper section --paper <slug> --name <section>` for relevant
bodies. For Markdown, a single TeX file or another layout, read the actual
source and heading/include order directly with line locators; for a PDF-only
input use page/statement locators. Keep the existing layout and do not create
TeX scaffolding just to use the reader commands. Do not infer manuscript order
from filenames alone. Pass `--workspace` at the leaf command for a standalone
checkout or explicit workspace selection.

Identify the central question, the exact result answering it, the mechanism
that makes the answer possible, inherited ingredients, and the decisive
obstruction or proof obligation. Check the scope of each result and its role
in the final argument. Substantive new outlines or changed contribution stories
follow the [positioning checkpoints](../reading-reference/references/research-positioning.md);
report-only structural diagnosis keeps that protocol's review boundaries.

## Separate logical order from reader order

Trace definitions, hypotheses and load-bearing results through their actual
applications. Distinguish a hard prerequisite from a motivating example,
preview, or forward reference. A main theorem may be announced before its
proof or technical setup when its statement is interpretable and the later
route is explicit. The proof must still have all of its prerequisites available
or precisely signposted; a dependency cycle needs a mathematical repair.

Use [knowledge-dependencies](../knowledge-dependencies/SKILL.md) when explicit
graph checking would resolve ordering, closure or change-impact questions, or
when the user asks for a managed dependency graph. Adopt a graph only for the
requested scope. Its topological order constrains proof exposition and setup;
it does not prescribe the paper's narrative or certify complete extraction.

Choose section boundaries by a change in mathematical job: setting up an
interface, exposing an obstruction, proving the decisive estimate, deriving
the main theorem, or testing its scope. Keep a short argument with its use
when separation would add needless navigation; isolate reusable technical
machinery when that clarifies the main route. An appendix can hold secondary
detail with an explicit access path. Keep essential hypotheses, meaning and
the main mechanism visible on the main reading route.

## Produce a reviewable architecture

Give a brief argument spine, followed by the proposed section sequence. For
each section, state its **purpose, inputs, outputs, and next use**. Explain
consequential placements from the actual proof or reader need, rather than a
generic introduction/preliminaries/results template. Name the intended entry
point for the target reader and any optional technical route.

For an existing manuscript, map **current sections or passages → proposed
homes**, including retained material, merges, splits, relocations and suggested
cuts. Identify the concrete failure each material move fixes and the setup or
cross-references it must carry. A report-only request stops at this proposal.
Within authorized manuscript editing, apply the map through `paper-writing`
and recheck affected statements, definitions, citations and dependency routes.

Separate essential structural repairs from optional alternatives. If two
orders serve different audiences, explain that tradeoff without forcing a
single universal order. Finish with unresolved proof/positioning dependencies
and the inspected scope. Never present an attractive outline as evidence that
the paper's central claim has been proved.
