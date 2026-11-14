# Optional fork housekeeping

Apply this procedure only when the fork owner has explicitly enabled a standing
housekeeping preference. Record that choice in the consuming workspace, not in
shared skills. Installing or contributing this file does not enable it.

## The rule

For finished public policy work, integrate the reviewed changes into the fork's
actual default branch within the owner's authorization. Remove redundant branches
only under an explicit cleanup preference, preserving unmerged work and local
backups. A branch containing material excluded by the
[publication gate](../../labo-pr/references/publication-gate.md), such as private
research, sources, manuscripts, PDFs, data or private logs, must not be pushed. Preserve it locally
and extract reusable changes into a clean public branch instead. Deleting a
branch does not remove material already published in its history.

Classify by content, not by branch name:

- Changes already in the default branch (the branch is an ancestor, every commit is patch-equivalent under
  `git cherry`, or the diff on the branch's own files is empty) count as merged: delete the branch.
- A branch with an open upstream PR stays until that PR is merged or closed.
- Merging a PR into the shared upstream belongs to the upstream owner; never report it as done.

## Bringing `main` level

- Verify actual fork/upstream URLs and default branches, then fetch their current
  tips. Integrate upstream without replacing newer changes with an old snapshot.
- If local history mixes policy and private material, leave it intact and prepare
  selected reusable changes in a separate worktree from a verified public base.
  Inspect the complete diff and every included commit's contents. A filename scan
  alone is insufficient.
- Run `publication_guard.py check` and `review` for the exact base, head and
  destination before pushing. Never force-push, rewrite the default branch or
  bypass the guard. If a deletion is blocked, do not switch transports to evade it.
- Preserve the active checkout and its uncommitted work. Parent gitlink recording
  remains separately authorized local work, not a prerequisite or an automatic
  consequence of housekeeping. The parent is never part of a skills push.

## Small traps

- In zsh write `"${SHA}:refs/heads/main"`; `$SHA:refs` is read as a modifier and the push silently
  sends nothing.
- A full local test run can fail on tests that also fail on the untouched upstream base; compare against
  that base before blaming a change.
