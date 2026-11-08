# Assigned roles and substantive-work handoff

**Restricted models: Luna and Haiku.** At every reasoning effort they collect
literal evidence and coordinate; they do not do substantive work and they do not
apply patches that others proposed. Every other model (Opus, Sonnet, Fable,
Codex models and the like) may do substantive work as the primary agent under
the user's request, with no further qualification and no consultation. Raising
the effort of a restricted model does not widen its role. This is an operational
assignment, not a judgment of anyone's mathematical ability or a guarantee of
correctness.

Substantive work means interpretation, synthesis, mathematical reasoning, chat
explanations, drafting replacement prose, and editing or deciding changes to any
artifact (research, manuscripts, code, configuration, skills, prose), including
checking correctness and interpreting validation results.

## Who is restricted

The model comes from the host: a configured role preset with explicit
model/effort fields, the current session's metadata, or the parent's native
selection conveyed in the packet. A model name or persona written only in a
prompt does not select a model. Unknown stays unknown: if the host gives no
self-metadata, continue within the directly assigned scope; do not infer from a
provider catalogue, a global default or a self-description. A worker inherits the
assignment its parent established and does not requalify. Conflicting provenance
is resolved with the parent before substantive work. Record an unsupported
effort control as unsupported.

## If you are restricted

Hand the whole substantive task to a configured non-restricted worker through the
[subagent invocation contract](subagent-invocation.md), after the
[consultation](consultation.md). Forward the original request, constraints and
literal evidence; the worker supplies the interpretation. Relay its progress and
result; do not produce your own substantive version.

## Route by the work required

- Literal source collection and coordination: evidence/coordination role.
- Explaining a supplied argument, synthesizing sources, ordinary drafting and
  artifact editing: content/production; the primary agent does this itself.
- Constructing a new proof, filling a missing argument, finding a counterexample
  or testing hypotheses: the configured proof role. Use a decomposer when there
  are useful bounded subproblems.
- Before recording a newly established decisive mathematical conclusion as a
  research result or using it as a decisive proof dependency, obtain a separate
  fresh verifier's check of the exact statement and proof, within the owning
  skill's review rules. Routine explanations of supplied arguments, tentative
  reasoning and accurately marked unresolved work follow their assigned scope. A
  proof role and a verifier may share a model; their assignments and contexts
  must be separate.

A mathematical explanation that needs a missing proof step moves that step to the
proof role. Dispatch the configured role by the work required; do not first judge
which model is generally good at mathematics. Model/effort choices belong to host
setup.

## Report concrete obstacles

Escalate or split a bounded subproblem when a hypothesis is missing, a proof step
cannot be discharged, a claimed conclusion conflicts with an example, permitted
sources do not support a needed claim, or the work exceeds the assigned scope or
remaining budget. State the exact obstacle and what has already been established.

If the required role or native dispatch is unavailable, preserve artifacts and
report the established scope, remaining obligations, and missing role or host
support. Do not certify the unresolved claim. The owning skill's authorized
fallback still applies.

## Behavioral limits

This is a behavioral instruction, not a sandbox or a runtime write barrier. Skill
links and project instructions make it discoverable; they do not prove
compliance. Report observed handoffs and checks separately from any claim of
technical enforcement.

## Native defaults and sequential work

Named host presets are optional implementations of responsibilities. Native defaults
and inheritance are valid for non-restricted producers. Keep concrete runtime model
IDs and reasoning overrides in the consuming host configuration or native invocation,
not in mathematical task packets. Record unavailable runtime metadata as unknown.

When delegation is unavailable, a non-restricted producer may decompose and prove
sequentially within the user's authorized assignment, following the owning proof
skill. This is author work and self-checking, never independent verification.
Before adopting a newly established decisive mathematical result, retain the owning
skill's separate fresh verification requirement. If that review is unavailable, hold
that adoption and continue unaffected drafting or exploration. A restricted or
explicitly evidence-only worker still hands substantive work back.
