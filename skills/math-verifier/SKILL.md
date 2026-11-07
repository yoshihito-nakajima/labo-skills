---
name: math-verifier
description: Independently check a frozen mathematical proof against its exact statement and permitted primary sources, reporting located gaps or checked scope.
---

# Independent mathematical verifier

Follow the [shared packet, eligibility and entry contract](../research-router/references/mathematical-roles.md).
Use the current bounded assignment here. In a native adapter this skill is
already loaded; execute it without invoking another copy of the skill.

Use a fresh thread containing only the frozen statement, proof and permitted
primary sources. Keep producer discussion and other review reports out of the
read set. If visible context compromises that boundary, report its extent
instead of certifying independent review.

Check quantifiers, hidden hypotheses, lemma applicability, edge cases and the
passage from local conclusions to the final result. Actively test delicate
steps and look for counterexamples where useful. Report located findings with
supporting reasoning, or the exact checked scope and no finding. Follow the
owning review skill's required report format when one is selected.

Keep this role read-only: do not edit, repair, spawn another worker or become
the proof producer. A repair needs a separate producer and a fresh review
thread. A native adapter may restrict tools; loading this skill alone does not.
If no fresh independent context is available, report that independent review is
unavailable. Do not switch this read-only assignment into editing; the producer
can continue under its own assignment. No context boundary certifies a proof
or filesystem isolation. Report available check evidence and its limits.
