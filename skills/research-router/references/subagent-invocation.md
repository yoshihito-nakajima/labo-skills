# Subagent invocation

Use this contract for advisor consultations, task-specific workers, and
independent reviewers. The selected skill still owns each role's source,
editing, and review limits.

## Start a thread with a bounded packet

Start each new role in a fresh agent thread without the coordinator's
conversation history. Use the host's native boundary: for `spawn_agent`,
explicitly set `fork_turns: "none"`; another host may provide a fresh task or
subagent invocation instead. Check that its context behavior supplies the
needed boundary. Give the agent a short packet containing only what its
assignment needs:

- the request or a neutral restatement of the question;
- the exact task, scope, and expected output;
- allowed source files or paths, with version or frozen-artifact identity;
- relevant constraints and evidence needed to do the work;
- assignment provenance: the user's task or parent's bounded role, permitted work,
  actual tool/permission limits and the context boundary; keep private runtime
  selection metadata out of reusable task instructions;
- consultation status for this assignment, so a worker can reuse a completed
  check without recursively commissioning another advisor;
- context and files the agent must not use, when the selected skill requires
  that boundary.

Use the host's actual callable interface. A native default or inherited model is
valid; explicit selection is optional when supported and appropriate. Concrete
runtime choices belong to host configuration or the invocation, not the reusable
packet. Missing model/effort metadata or a named preset does not block delegation.
If dispatch is unavailable, use the [consultation fallback](consultation.md) and
[sequential assignment rules](editing-capability.md); do not fake another worker.

Do not paste the full conversation, implementation transcript, unrelated
decisions, or another reviewer's report. Do not rely on a saved persona or
prompt template in place of the selected skill's current assignment.

A follow-up operation such as `followup_task` continues an existing agent
thread and its assignment context. Use it to continue that agent's work.
Start a fresh thread when a new role or independent review needs fresh context;
do not reuse a producer's thread as an independent reviewer.

## Nested delegation and one shared budget

A qualified worker may delegate a proper subproblem when the user or selected
skill authorizes delegation and the host exposes native child spawning. Nesting
preserves this contract, including actual native dispatch and fresh context.
Reuse the completed consultation for the same assignment; a child does not
commission another advisor merely because it received delegated work.

The root allocates a finite remaining depth and one session-wide concurrency
budget. Each packet states its remaining depth, the number of descendant slots
reserved to its subtree, and who integrates its result. A child consumes one
slot while active; its descendants share the subtree's remaining allocation.
Sibling allocations must fit the root's remaining slots. Decrement depth at
every edge, and stop spawning at zero. A per-branch cap copied independently to
every child is not a global budget. Keep reservations with the root/integrator;
release them after results are collected and the host releases the thread.
Completed but still open threads can continue to occupy host slots.

For example, with six available spawned-thread slots, an integrator taking one
may reserve two slots to each of two branches (one worker and one descendant),
leaving one spare. The branches cannot each spawn six agents. Use sequential
work or return a bounded redispatch packet when slots or depth run out; do not
retry a native limit error in a loop.

Prefer the host's native nesting. Check the installed host rather than assuming
all versions share a depth control. When native nesting is absent, return the
subproblem to the nearest capable parent for dispatch; identify that as
parent-mediated delegation. Starting subprocess CLIs to evade a native limit
does not preserve its session budget or permission boundary.

For mathematical decomposition, proving and independent verification, use the
[mathematical role contract](mathematical-roles.md). Host role presets are optional adapters; the selected skill and current packet
remain the task authority. Configure actual host support only when requested through
[agent-host-setup](../../agent-host-setup/SKILL.md).

## Preserve independent reviews

For a cold or blind review, send the frozen artifact and only the primary
sources permitted by its skill. Keep the author's rationale, proposed repair,
implementation discussion, and prior reports out of the packet. Keep parallel
reviewers' reports hidden from one another until their assigned reads finish.
After an accepted change, use a new thread for the fresh review required by the
owning skill.

## State the limits of isolation

The host's fresh-context boundary (such as `fork_turns: "none"`) keeps parent
conversation turns out of the new thread. It does not by itself remove system
or workspace instructions, restrict filesystem access, or create a separate
workspace. A reviewer may still see
prior context in files or repository instructions. Keep the assigned read set
explicit, avoid exposing review history in that set, and report any visible
context that could have affected independence. Do not describe a review as
fully isolated when those limits matter or cannot be checked.

If the host does not expose a way to start a separate thread with the needed
history boundary, state that independent context could not be established and
follow the selected skill's fallback. Do not certify independence from a
self-check.

## Example packet

```text
Review only the frozen `artifact.md` and the cited `source.pdf` for whether
Claim 2 follows from its stated hypotheses. Do not read author notes, prior
reviews, or the repair discussion. Return any finding with an exact location,
the supporting source passage, and the reasoning; otherwise report no finding.
```

## Bound each worker

Every model call re-reads the whole context, so cost grows with calls times context size. Give each worker one
bounded unit and stop it there: set a tool-call and context budget in the packet, and have it return partial
results and the remaining obligations when the budget is reached. Start a fresh worker for the next unit rather
than continuing one across many units. Pass a prepared packet (exact excerpts, cited statements, source text) and a
short role card instead of whole files or the full chain of skill references; load page images only when text
cannot be read. While waiting for workers, the coordinator waits once with the longest timeout the host allows
(or for a completion notice) instead of polling with short sleeps or status checks: each wake re-reads the
coordinator's whole context. Long-course specifics live in the reading-book
[token budget](../../reading-book/references/token-budget.md).
