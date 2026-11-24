---
name: course-planning
description: >-
  Design or replan mathematical books and courses: reader, narrative, bounded volumes,
  prerequisites, completion boundaries and final integration. Produces an actionable
  architecture from existing sources and drafts; not mathematical text production or proof review.
---

# Plan mathematical books and courses

Own the architecture: the overall route, the book being finished now, its
reader-facing flow and prerequisite connections, and the later integration plan.
[course-authoring](../course-authoring/SKILL.md) owns canonical mathematical text,
production progress, corrections and official output. For book-led work,
[reading-book](../reading-book/SKILL.md) retains editions and source adoption.
Planning alone does not start production, review, workers or continuous loops.

## Recover the actual project

Read the current entrypoint, plan and compact status; inspect the actual include
order and relevant headings, statements and source records. Distinguish written
content, unclosed proofs, outstanding findings and future aspirations. Do not
reread the entire course or review history to propose a boundary. Treat claims
whose prerequisites have not been checked as provisional.

Keep the author's destination and adopted scope visible. Recover the question
and learning route conveyed by the current text, then identify what prevents a
coherent completion. Separate overall ambitions, the present book, and small
writing/checking assignments. Deferring adopted content to another book does
not delete it or make the overall project complete.

## Design a finishable book

Use the [plan contract](references/plan-contract.md) to produce a concrete plan:
reader and starting facts; central question; endpoint; section roles; adopted
content and exclusions; prerequisites; size estimate; and completion evidence.
Map existing passages to their proposed homes and name missing bridges.
Choose boundaries by mathematical purpose and prerequisites, not equal page
counts. Use a size preference from the project, including preliminaries,
appendices and indexes, with allowance for uncertain proof work. Do not impose
a universal page range or compress necessary explanation to satisfy a target.

For each part, say what question it answers, which inputs the reader uses,
what it establishes, and where that output is used next. Use these roles to
write the transitions or set the question and endpoint of a lecture. The same
reader-order principle applies in [paper-structure](../paper-structure/SKILL.md#produce-a-reviewable-architecture).
When exact dependency management materially helps, use
[knowledge-dependencies](../knowledge-dependencies/SKILL.md) on the bounded
scope; do not require a complete theorem graph before useful planning.

## Decide reading and production routes

When asked for an actionable plan, give a standard reading order and a production
order, with each book's endpoint, primary-source role and boundary. Explain any
difference between the two. A topic list with prerequisites deferred to an
unspecified later stage is not a schedule. Preserve coherent runs of designated
primary sources and integrate overlap rather than continually inventing a new
whole-course architecture. Assign essential early inputs to a named owner before
using them; do not conceal a cycle behind a preliminary restatement.

For existing material, plan initial placement followed by a forward authoring pass.
Name that pass's adopted scope, starting unit, exit and explicitly deferred work;
keep the author-checked position distinct from pending independent review.
Plan review submissions at coherent section-group or chapter boundaries using
[the submission rule](../course-authoring/references/production-handoff.md#まとまった範囲で提出する),
rather than requiring an exercise-by-exercise review schedule. Integration is a
later stage unless the user requests an intermediate collected output.

When the books are built from cards ([book-harness](../book-harness/SKILL.md)), the plan's reading order becomes
each book's route, including the reader-facing chapter and section hierarchy, and the preliminaries below become its entrance card with exact `borrows`. The route plan
supplies the agreed scope and endpoint for [route closure](../book-harness/references/intake-review.md#5-route-closure).
Source mappings supply evidence for the assigned source ranges.

## Connect books without duplicating mathematics

Use [volume entrances and borrowed results](references/preliminaries.md) to plan
and maintain each book's opening. State borrowed definitions, conventions and results precisely in preliminaries,
including assumptions, conclusions, normalization, stable labels, source owner
and version. Distinguish established prerequisites from unfinished drafts and
unproved obligations. A restatement is not proof evidence. Define self-containedness
by the exact permitted inputs and adopted content for each book, not by a label
such as foundational or advanced. Close every substantive dependency inside the
book or at its declared input boundary; state that qualification. For a collected
work, also declare common inputs and close imported results internally unless
they are among those inputs. Moving promised content into assumed prerequisites
is a scope change, not a proof repair.

Keep one editable source for each result and proof. Reuse that source in volume
and collected outputs; generated restatements and immutable review packets are
not additional editable canonical texts. Resolve circular prerequisites rather
than hiding them behind cross-references. Conditional drafting can proceed, but
affected results remain incomplete until their prerequisites are established.

## Make adoption and integration concrete

Budget a separate integration stage: fix versions and reading order, connect
preliminaries, compare hypotheses and conclusions before merging results,
preserve stable-label mappings, harmonize notation and transitions, and check
the actual reading route. Changed claims and affected uses need appropriate
checks through course-authoring; unchanged evidence can be reused. Integration
does not automatically reduce a collected book to the per-volume size target.

Keep existing project roots, mathematical sources and review histories. Follow
the [course layout](../course-authoring/references/layout.md) for optional volume
plans; create only the selected volume, not empty directories for the whole
ambition. Keep a single current entrypoint and a short current status. Preserve
superseded decisions as history rather than stacking conflicting execution
instructions at the entrance. Do not duplicate detailed status in several files.

For a design-only request, return the proposal without restructuring files.
When adoption is authorized, update the operative plan and entrypoints, record
the old-to-new scope mapping, and identify stale execution configurations before
resuming anything. Planning does not grant production ownership. Preserve any
existing stop instruction until the user authorizes the relevant work.

Report the selected book, inspected evidence, concrete plan and structural edits,
remaining prerequisite decisions, and whether any execution/build checks were
actually run. An attractive outline does not certify the mathematics.
