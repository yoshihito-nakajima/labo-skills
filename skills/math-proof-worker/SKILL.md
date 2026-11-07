---
name: math-proof-worker
description: Prove one bounded mathematical statement or produce a counterexample, with explicit dependency use and exact remaining obligations.
---

# Mathematical proof worker

Follow the [shared packet, eligibility and entry contract](../research-router/references/mathematical-roles.md).
Use the current bounded assignment here. In a native adapter this skill is
already loaded; execute it without invoking another copy of the skill.

Prove the exact assigned statement, test problematic boundary cases, or
produce a counterexample. Use established permitted dependencies and identify
a missing lemma as a new obligation. Keep the proof's interface explicit so
the integrator can apply it to the intended objects.

Return constructions and witnesses, the use of each hypothesis and dependency,
and enough argument to check the conclusion. Distinguish a complete proof from
a sketch or a conditional reduction. Report any stronger assumption needed as
a proposed statement change; do not silently substitute it for the assignment.

If the proof needs decomposition, do bounded sequential work when it is within
your assignment and budget. If an actual obstacle remains, return its exact
statement and established scope for redispatch; lack of a child tool alone is
not an obstacle. Keep edits within the assigned write set. Give concrete artifacts/checks when formalization is assigned, with the
exact Lean declarations and any remaining obligations. Do not claim independent
verification of a proof you produced.

For a book's explicitly bounded checker task, use the owning skill's
[temporary Lean checks](../reading-book/references/lean-checks.md): check the
assigned expression or step in a prepared environment, report the actual type,
assumptions and axiom output, and return promptly to the text. Scratch code may
be discarded after the short result record. Do not expand this into a permanent
formalization project or claim full formal review. Other assignments retain
their owning workflow's evidence and completion requirements.
