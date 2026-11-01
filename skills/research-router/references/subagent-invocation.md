# Subagent invocation

Use this contract for advisor consultations, task-specific workers, and
independent reviewers. The selected skill still owns each role's source,
editing, and review limits.

## Start a thread with a bounded packet

For every `spawn_agent` call, explicitly set `fork_turns: "none"`. Do not
inherit the coordinator's conversation history. Give the agent a short packet
containing only what its assignment needs:

- the request or a neutral restatement of the question;
- the exact task, scope, and expected output;
- allowed source files or paths, with version or frozen-artifact identity;
- relevant constraints and evidence needed to do the work;
- context and files the agent must not use, when the selected skill requires
  that boundary.

Do not paste the full conversation, implementation transcript, unrelated
decisions, or another reviewer's report. Do not rely on a saved persona or
prompt template in place of the selected skill's current assignment.

`followup_task` continues an existing agent thread and its assignment context.
Use it to continue that agent's work. Start a new `spawn_agent` thread when a
new role or independent review needs fresh context; do not reuse a producer's
thread as an independent reviewer.

## Preserve independent reviews

For a cold or blind review, send the frozen artifact and only the primary
sources permitted by its skill. Keep the author's rationale, proposed repair,
implementation discussion, and prior reports out of the packet. Keep parallel
reviewers' reports hidden from one another until their assigned reads finish.
After an accepted change, use a new thread for the fresh review required by the
owning skill.

## State the limits of isolation

`fork_turns: "none"` prevents parent conversation turns from being copied into
the new thread. It does not remove system or workspace instructions, restrict
filesystem access, or create a separate workspace. A reviewer may still see
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
