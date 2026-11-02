# Mathematical delegation roles

Use these roles for a research task that actually benefits from decomposition.
Role names do not establish model capability: apply [eligibility](editing-capability.md),
select a currently callable model suited to research reasoning through native
fields, and record model/effort provenance. Luna remains evidence/coordination
only in this fork. A preset is a starting choice, to be reconsidered for the
task; high effort alone does not establish mathematical competence.

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
and review requirements. Reuse the completed consultation for this assignment;
missing provenance, consultation or critical packet fields return to the parent
for resolution rather than triggering recursive advisors or a replacement role.

## Host entry boundaries

Codex setup registers project `.codex/agents` adapters with explicit native
model/effort and a short instruction to read the matching role skill. Read that
skill as instructions in the existing delegated thread. Claude-specific skill
frontmatter does not select a Codex model or create a Codex child.

In Claude Code, direct `/math-… <packet>` skill execution uses `context: fork`
and the built-in `general-purpose` agent to start one fresh child with the
skill body as its task. The skill's native `model`/`effort` fields apply there.
Supply the bounded packet after the slash name. These bodies use no argument
placeholder; Claude appends the invocation arguments to the skill prompt as
documented in [argument passing](https://code.claude.com/docs/en/skills#pass-arguments-to-skills).
Native `agents/math-….md` adapters instead preload the same body through
`skills: [math-…]`, with their own explicit model/effort/tools. A preloaded
skill's fork configuration does not request another invocation: execute the
current assignment in the existing child. Do not reinvoke the same skill or
spawn a replacement merely to activate its instructions. Include direct skill
children in the parent's remaining depth and shared slot accounting as well.

Keep automatic skill invocation enabled so native preload can load the role.
If host policy disables or hides it, report the missing preload; an empty
adapter is not the full role. The native verifier has a read-only tool list;
the direct general-purpose skill path has a behavioral read-only requirement
and must not be described as having the same technical restriction.

Other harnesses use their own actual delegation and model controls. Detect
host capabilities rather than treating every non-Codex harness as Claude Code.
