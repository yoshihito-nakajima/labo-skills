# Reviewable skill design

Apply these principles when creating or changing skills in this collection,
including local experiments that may later become a PR. Design for a reviewer
who has not seen the conversation or the private artifact. A local improvement
can remain local; preparing a clear change does not authorize publication.

## Give each reusable responsibility a home

- Identify the behavior being added, when it should be invoked, and which skill
  owns it. Put detailed instructions and necessary supporting resources together
  under that owner; callers should link to them rather than copy the rules.
- Extend an existing skill for a refinement of its existing responsibility.
  Create a separate skill when the work has a distinct trigger, coherent outcome,
  and reusable procedure that can be used independently or by several workflows.
  Neither a file-count target nor every small preference justifies a new skill.
- Keep the entrypoint short enough to reveal the role and workflow. Use
  `references/`, `scripts/`, and `assets/` only for concrete needs of that role.
  Do not make a general workflow skill absorb unrelated detailed procedures.

## Keep the change focused

- Before editing, identify the necessary new files, existing callers and
  compatibility paths. Inspect the current diff so unrelated work is preserved.
  A future PR should have one coherent purpose, with the new responsibility
  grouped together and existing skills changed only where integration requires it.
- Do not combine the feature with incidental renaming, reformatting, cleanup,
  deletion of existing skills, or changes to host settings. Preserve existing
  capabilities and discovery behavior. When generalizing a host tool into a
  skill, list everything it currently produces and carry each output over,
  opt-in if necessary; never drop one silently. If rules move, update current callers and
  keep a short forwarding reference when old paths still need to resolve; keep
  one authoritative rule body rather than two editable copies.
- Keep project-specific content and user-identifying evidence in the project.
  Reusable skill files must make sense without a private workspace. Follow the
  [publication boundary](../../labo-pr/references/publication-gate.md) for any
  eventual contribution; use self-contained fictional examples when examples
  are needed to explain or validate the reusable behavior.

## Make the result reviewable

Validate skill metadata and local references, and inspect the resulting diff for
scope and lost responsibilities. For meaningful behavioral changes, exercise
representative requests at the appropriate cost; distinguish structural checks
from actual execution. Do not add tests that merely check copied wording.
New executable helpers need execution checks. Report the owner, necessary caller
changes, validation and remaining limits so the contribution can be assessed on
its own. Use the existing repository overview to make new roles discoverable.

Commit, push, PR creation and adoption into a workspace follow the user's
authorized scope through [labo-pr](../../labo-pr/SKILL.md) or the applicable Git
workflow. Do not publish merely because the skill was designed with a PR in mind.
