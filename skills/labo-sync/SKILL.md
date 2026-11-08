---
name: labo-sync
description: Review and selectively adopt shared labo-skills changes into the user's fork and workspace pin; not for routine project pulls.
---

# Adopt upstream labo-skills changes

Luna and Haiku only collect evidence here and hand substantive work to another agent: [roles](../research-router/references/editing-capability.md).

Use this skill when the user wants newer shared Labo skills or tools in their
fork. A routine `git pull` of the private research repository is a separate
Git task and does not need this workflow.
Read the repository's [fork and submodule policy](../../README.md) first.

Inspect the parent repository and `.agents` separately: confirm the parent
gitlink, `.gitmodules` URL, fork remotes, branch, and worktree status. Preserve
local work; do not overwrite or stash user changes as an automatic recovery
step. If an unexpected branch, remote, or dirty state changes what would be
integrated, explain the choice before proceeding.

Fetch the verified shared upstream, review the candidate commits and their
diffs, and identify which changes fit the user's fork. Integrate selected work
while preserving fork-specific changes. Never use a reset to upstream or a
blind submodule `update --remote` as the adoption strategy. Validate the
affected skills or tools and inspect the resulting diff for private research
material before sharing anything.

Follow the [publication boundary](../labo-git/SKILL.md#publication-boundary).
Treat policy adoption, policy push/PR and local parent gitlink recording as
independent operations. Advance the parent pin only to the selected policy
commit when adoption is requested and record it in the parent's own history
(pushed to its private remote as usual). The parent has no PR. Fork pushes and upstream PRs operate only in the
policy Git and follow the user's request, not merely an upstream fetch. A
selected upstream change does not imply that every upstream commit belongs
in the fork.
