# Request and next-action consultation

For every user request handled by a labo skill, the coordinating agent must
send the request and rough next action to a separate advisor and wait for its
reply before performing or delegating that work, or delivering the substantive
answer. Reading sources to understand the request can come first. An unanswered
consultation or advice about another task does not complete this step.

Launch the advisor under the [subagent invocation contract](subagent-invocation.md).

Give the advisor the original request, relevant constraints and source evidence,
your interpretation, and the proposed next action. Ask whether the interpretation,
scope, and action match the request. Apply the [model check and selection
criteria](../SKILL.md): request interpretation is at least **content
understanding**, even when the ensuing work is routine; use **research
reasoning** when the check requires mathematical judgment.

The advisor checks against the request and evidence, rather than merely echoing
your interpretation. A sound plan needs only brief agreement; otherwise return
the concrete mismatch and correction. Do not invent objections or extra work.
Read the reply and resolve identified mismatches before proceeding. This is
agent-to-agent consultation, not another user-permission step or a full result review.

Reuse the consultation when the same checked plan passes between skills or
workers. Consult again when the request, interpretation, or plan materially changes.
Advisors and delegated workers do not recursively commission advisors for the
same assignment. If the host cannot provide a separate advisor, state that the
consultation could not be performed; self-checking is not independent consultation.
