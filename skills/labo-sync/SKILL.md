---
name: labo-sync
description: Review and selectively adopt shared labo-skills changes into the user's fork and workspace pin; not for routine project pulls.
---

# Adopt upstream labo-skills changes

Before substantive work, follow [eligibility and handoff](../research-router/references/editing-capability.md).

Use this skill when the user wants newer shared Labo skills or tools in their
fork. A routine `git pull` of the private research repository is a separate
Git task and does not need this workflow.

For each request, follow the [required consultation](../research-router/references/consultation.md).
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

Treat the policy fork and parent gitlink as distinct updates. Advance the
parent pin only to the selected policy commit; before sharing that parent
commit, make sure the policy commit is available from the fork recorded in
`.gitmodules`. Pushes and pull requests follow the user's request: do not push
or open a PR merely because upstream was fetched. A selected upstream change
does not imply that every upstream commit belongs in the fork.
