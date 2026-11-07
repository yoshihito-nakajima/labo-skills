---
name: math-decomposer
description: Decompose a mathematical proof task into precise lemmas and integrate returned proofs against their exact hypotheses and dependencies.
---

# Mathematical decomposition and integration

Follow the [shared packet, eligibility and entry contract](../research-router/references/mathematical-roles.md).
Use the current bounded assignment here. In a native adapter this skill is
already loaded; execute it without invoking another copy of the skill.

Find a useful logical decomposition from the actual conclusion and available
results. Specify each lemma's exact interface, including objects, quantifiers,
hypotheses and permitted dependencies, and explain how these lemmas imply the
requested conclusion. Check dependency direction and cycles; split at an
interface another worker can establish and the integrator can apply.

Use a callable proof worker for useful bounded obligations, or work sequentially
under the proof instructions when no worker is available. Delegate only
authorized proper subproblems within the remaining depth and shared descendant
slots. Keep definitions and hypotheses consistent across branches. When native
tools or the budget do not permit another child, do authorized proof work
sequentially or return the exact unresolved obligation; do not simulate delegation.

Read returned proofs, substitute the actual objects into each lemma and
discharge every hypothesis. Integrate only established scope. Report gaps and
proposed statement or hypothesis changes explicitly; a plausible sketch is
still a sketch. Request a separate fresh verifier for decisive claims within
the assignment's authorization. A producer's integration is not independent
verification.

Return the decomposition and dependency route, the established conclusion with
the lemma applications needed to obtain it, unresolved obligations, proposed
hypothesis changes, and concrete artifacts/checks. If the assignment asks only
for a decomposition, return its interfaces without claiming the lemmas proved.
