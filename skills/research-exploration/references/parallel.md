# Bounded parallel coordination

Parallel exploration is an execution choice within the current request's
authorization and applicable skill instructions. It is separate from the
standard research directory structure. Stored mode records coordination and
does not start agents or authorize unrelated work. When agents are unavailable,
continue sequentially and record the limit.

Set one integrator, a small `max_workers` matched to host capacity and owners.
The cap counts distinct active worker owners, excluding the integrator;
other assignments stay recorded. This checks metadata, not running processes:
the integrator also observes live host limits and manages agent lifecycles.

The following follow `python3 <labo-script> research exploration`:

```sh
configure --research example --actor primary --expect-revision 0 \
  --mode parallel --integrator primary --max-workers 2
add --research example --actor primary --node compactness --owner worker-a \
  --kind category --title 'Compactness route' --summary 'Test a possible route.' \
  --next 'Investigate the uniform estimate.'
update --research example --actor worker-a --node compactness \
  --expect-revision 1 --state active
```

All parallel nodes have owners. Workers update owned nodes and add self-owned
children beneath owned nodes. The integrator alone creates roots, reassigns
owners, reparents nodes and configures settings; it may reconcile any node after
inspecting worker state and handoff. Avoid overlapping assignments. A parent's
owner does not automatically own descendants. Metadata ownership does not lock
arbitrary records; use disjoint detail files.

Within a shared Lean project, assign disjoint small modules and declaration
names to workers. The integrator coordinates shared definitions, Lake settings,
umbrella imports and the final combined build. Agree on interfaces before two
workers rely on a changing definition. Source ownership is a workflow contract;
the metadata CLI does not intercept Lean-file edits.

Before spawning follow router model provenance, consultation and the
[subagent invocation contract](../../research-router/references/subagent-invocation.md).
Give the question, node IDs/revisions, allowed paths, evidence inputs, expected
proof/counterexample/computation output and stopping condition. Require unresolved
issues in the handoff. Isolate independent reasoning; do not feed an independent
checker the producer's intended conclusion.

The integrator maintains classification and the single narrative `plan.md`.
Workers return evidence and proposed story changes without editing that plan.
Inspect actual records, separate established implications from candidates,
resolve conflicting results, then update summaries, next actions and states.
`done` only completes a scoped task. Reuse claim/dependency evidence instead of
promoting its status through the tree.

At pause/completion record the next concrete check and blocking conditions.
Resume from the tree and scoped records rather than every proof. Reconcile
stale updates; never substitute newer revisions without reading the changes.
