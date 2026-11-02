# Substantive-work eligibility and handoff

Before substantive work, establish your current model, the host's reasoning
setting when exposed, and suitability for the assignment from evidence.
Apply this rule to coordinators, advisors, workers and reviewers, including
direct skill invocations.

Substantive work includes interpretation, synthesis, mathematical reasoning,
chat explanations, drafting replacement prose, and editing or deciding changes
to any artifact: research, manuscripts, code, configuration, skills and other
prose. Checking correctness and interpreting validation results also belong to
the substantive worker.

## Establish eligibility

Use matching current-session host metadata, or the parent's actual explicit
model selection and exposed reasoning setting conveyed in the bounded
assignment packet. The latter is valid invocation provenance for a delegated
worker; it need not rediscover its identity or delegate again merely because
local self-metadata is absent. Select suitable models from the host's currently
callable choices using the task and available capability evidence. A provider
catalogue or global default alone establishes neither the current model nor
its suitability. Keep missing or conflicting provenance unknown.
When the host has no reasoning-effort control, record it as unsupported;
that absence alone does not disqualify an otherwise suitable model.

Confirmed lightweight models may coordinate and collect literal evidence only.
In this user's fork, Luna is restricted to that role at every reasoning effort,
including high. Increasing effort does not remove that restriction. Keep other
model choices dynamic rather than maintaining a fixed family/tier table.

If your current model or task suitability is unknown, delegate substantive
work. Confidence, apparent task simplicity, self-description and an advisor's
approval do not establish eligibility. Recognizing that the task exceeds your
understanding or judgment remains an additional reason to escalate, even with
otherwise adequate provenance.

## Hand off the whole substantive task

Discover the host's callable models and select a suitable worker. Follow the
[subagent invocation contract](subagent-invocation.md): set the actual model
selection and any exposed reasoning control through the host's native
invocation fields, and carry those selections and their source in the packet.
A model name written only in the prompt does not select the worker. If the
host exposes no model-selection field, matching worker-session metadata must
establish the actual model before it does substantive work. A host without
either form of model provenance has not established a qualified worker.

The qualified worker owns the analysis, replacement text, actual artifact
edits, and relevant checks. Advice or a patch proposal from that worker does
not authorize a restricted coordinator to write its own version or apply the
patch. A restricted coordinator may inspect paths, read sources, collect exact
passages or command output, and relay the worker's progress and final result
faithfully, without adding its own substantive conclusions.

Reuse an established assignment's provenance and completed consultation;
qualified workers do not recursively hand off solely because they received a
delegated task. Escalate when provenance conflicts, suitability remains
unestablished, or the assignment exceeds that worker's capability. If no
qualified worker is available, preserve artifacts and return a brief handoff
with the request, literal evidence, remaining work and missing capability.
There is no self-edit fallback.

## Behavioral limits

This is a behavioral instruction, not a sandbox or a runtime write barrier.
Skill links and project instructions make it discoverable; they do not prove
compliance. A hook whose host support and behavior have not been validated
does not enforce it. Report observed handoffs and checks separately from any
claim of technical enforcement.
