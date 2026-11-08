# Mathematical responsibilities across hosts

Use the host's configured decomposition, proof and verification roles for the
corresponding work. Apply [assignment and provenance](editing-capability.md)
without asking each worker to assess its general mathematical competence.
Record the role configuration or explicit assignment source and native
model/effort selection. Luna and Haiku remain evidence/coordination only.
The assignment permits the work; its correctness still needs proof and checks.
Use separate fresh verification before adopting newly established decisive
mathematical claims as research results or decisive proof dependencies,
following the owning skill's review rules and the adoption scope in the linked
routing rule. When native delegation is unavailable, a non-restricted producer may
work sequentially under the linked assignment fallback, keeping independent result
adoption pending if no fresh verifier is callable. Restricted workers return the
established scope and remaining obligations to the parent.

## Packet shared by all roles

State the exact proposition (quantifiers included), ambient objects and types,
definitions, hypotheses, notation and permitted lemmas with source/version or
stable dependency IDs. Distinguish proved input from conjecture and delegated
obligations. Include the intended conclusion, known obstruction, allowed files,
output destination, integrator, remaining depth and reserved descendant slots.
Name any Lean declarations and their types, toolchain/library versions and
allowed axioms when formalization is in scope. If no Lean work is assigned,
mark it out of scope rather than inventing formal evidence.

Return the exact scope established, a proof or counterexample with dependency
use, unresolved obligations and the reason each remains, any extra hypothesis
needed, and concrete artifacts/check results. A plausible sketch is a sketch;
a stronger hypothesis changes the proposition and needs integrator acceptance.
An unchecked Lean fragment is not a compiled declaration. Follow the owning
skill's formal-evidence checks before recording completion.

## Single-source role instructions

The role bodies and descriptions live in these skills:

- [math-decomposer](../../math-decomposer/SKILL.md)
- [math-proof-worker](../../math-proof-worker/SKILL.md)
- [math-verifier](../../math-verifier/SKILL.md)

The owning artifact skill still controls sources, write scope, formal evidence
and review requirements. Resolve missing substantive packet fields (statement,
hypotheses, sources or permissions) with the parent; unknown runtime metadata alone
is not a missing mathematical premise. Do not recursively commission advisors.

## Host entry boundaries

The three SKILL.md files are portable instruction bodies, with no native fork,
model or effort frontmatter. Loading one does not create a child or establish
independence. Use it in the current assignment, or pass it to a fresh worker when
a separate role is needed and available. Do not invoke another copy merely to
activate instructions already loaded.

Host adapters may register the skills, tool limits and context controls supported
by that host. Treat bundled adapters for another host as optional examples, not
requirements. Shared adapters omit fixed model choices and use native selection
behavior; installation-specific overrides stay in the consuming configuration.
Use [agent-host-setup](../../agent-host-setup/SKILL.md) only for an actual setup task.
Check loading, fresh context, permissions and live execution separately. A read-only
instruction is not a technical tool restriction; neither is proof certification.
