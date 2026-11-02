---
name: research-exploration
description: Organize mathematical exploration into nested categories and stable theorem/question nodes, read compact progress trees, and coordinate bounded parallel work within a research program using the current labo layout.
---

# Mathematical exploration trees

Before substantive work, follow [eligibility and handoff](../research-router/references/editing-capability.md).
For each user request, follow the [required consultation](../research-router/references/consultation.md).
Reuse consultation and model provenance already established for this request.

Use for persistent categories, candidate theorems, questions, experiments,
obstacles and next actions beneath `research/<slug>/`. `research-management`
owns the story and `plan.md`; `labo-layout` owns creation and safe structural migration.

## Structure and reading

New programs receive an empty exploration tree from `layout new research`.
When accepting plan edits or exploration in an existing program, follow
[labo-layout's safe migration](../labo-layout/references/research-migration.md):
reuse a supported tree or initialize the missing structure, then add/reuse only
the current scoped task. Inventory, explanations, report-only reviews and
checks remain read-only. A missing tree describes structure, not noncompliance
or missing mathematical proof. Its `schema_version` identifies the format;
plans and claim catalogs need no competing style/profile marker.

Preserve the plan, evidence, links, claim IDs and existing proof statuses.
Keep the plan's `in_progress` / `completed` meanings and use
`research-management` when findings change the story. Layout migration itself
neither certifies nor invalidates old claims. Sequential/parallel settings
describe execution; stored parallel mode alone neither starts agents nor
broadens the user's authorized task. Use bounded delegation when the current
request or applicable skill instructions authorize it.

Resolve `<labo-script>` as the absolute `../../scripts/labo.py` path from this
skill's **real directory**, following symlinks. The mounted checkout detects
the private Git superproject; use `--workspace /absolute/path` for overrides or
a standalone checkout. The following follow
`python3 <labo-script> research exploration`:

```sh
init --research example --if-missing
tree --research example --depth 2
tree --research example --node compactness --depth 1 --format json
show --research example --node uniform-bound
show --research example --node uniform-bound --details
check --research example
```

Read the compact tree first, then selected metadata and records. The tree is a
deterministic metadata projection with full-subtree counts and visible depth
limits. It does not read proof bodies or generate mathematical summaries.
Update summaries from actual evidence after investigation.

## Explore and record

Use stable descriptive IDs. Titles and categories may change while IDs stay
stable. Split nodes when independent questions, obligations or experiments
justify separate progress; let the mathematics determine the depth.

State objects, hypotheses, desired conclusion, known evidence and the next
discriminating step. Seek a proof, counterexample, small computation or precise
obstruction. Record what was checked, where it lives and what remains open.
Reuse an existing record or the [detail template](assets/record.md). Preserve
failed routes and useful obstructions; `parked` marks work set aside.

Work states are `queued`, `active`, `blocked`, `done`, `parked`. `done` finishes
a scoped task, including a negative result. Proof-bearing tasks additionally
require current formal-evidence records before `done`; see the
[Lean completion policy](references/lean.md). A finished task still has a
concrete next action for integration.
Parent completion does not complete children. Counts describe work inventory,
with no implied percentage of mathematical completion.

Classification parents locate topics, never logical prerequisites. Reuse claim
catalogs through `claim_refs` and dependency graphs through `dependency_refs`,
as `workspace/path#stable-id` links. Avoid a second proof-status catalog.
Use [knowledge-dependencies](../knowledge-dependencies/SKILL.md) for prerequisites
and the [evidence protocol](../research-management/references/evidence.md) for
claim evidence. Apply the owning mathematical skills to proofs and exposition,
and `reading-reference` when sources or contribution positioning need work.
Tree bookkeeping alone needs no new positioning survey.

## Parallel coordination

Read [parallel coordination](references/parallel.md) before assigning work.
One integrator owns settings, allocation and `plan.md`; workers own named nodes
and scoped records. Use native agents and current model-selection rules.
The CLI records work rather than managing agent lifecycles. Sequential mode
supports the same tree without delegation.

Read [format and commands](references/format.md) for mutations, revisions,
schema and limits. Reusable code stays in this checkout; private trees and
proof records stay in the parent workspace.
