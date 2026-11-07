# Fork housekeeping: merge or delete, without asking

This is a **fork-specific standing preference**, not an upstream rule. It applies to a fork whose owner
has chosen it (this fork does). Another fork, or an upstream contribution, does not inherit it.

## The rule

When a branch's work in the policy fork is finished, **merge it into the fork's `main` unless it
contains material that must not be handed over; if it does, delete the branch instead.** Do this
without asking each time. "Must not be handed over" is whatever the
[publication gate](../../labo-pr/references/publication-gate.md) excludes: private research, sources,
manuscripts, PDFs, data, private logs.

Classify by content, not by branch name:

- Changes already in `main` (the branch is an ancestor, every commit is patch-equivalent under
  `git cherry`, or the diff on the branch's own files is empty) count as merged: delete the branch.
- A branch with an open upstream PR stays until that PR is merged or closed.
- Merging a PR into the shared upstream belongs to the upstream owner; never report it as done.

## Bringing `main` level

- Local history can contain paths outside the policy tree, and the publication guard rejects them. Do
  not push that history. Review the working tree against upstream (names of changed files, and a scan of
  the added lines for private markers), then build **one** merge commit with `git commit-tree` over that
  tree, with parents the fork's `main` and `upstream/main`. Run `publication_guard.py check` and
  `review`, and push it as a fast-forward. Never force-push or rewrite `main`.
- Fetch upstream again immediately before building that commit: the upstream owner can merge in
  between, and a stale tree would undo their change. Merge upstream into the working branch first and
  resolve conflicts keeping both sides' intent.
- Afterwards put the working branch on the new `main` (the trees are identical, so uncommitted work
  stays as it is) and keep one local backup branch of the old working history until the owner says
  otherwise.
- Deleting fork branches goes through the hosting API (`gh api -X DELETE repos/<fork>/git/refs/heads/<b>`);
  the push guard blocks deletions made through `git push`.
- Recording the new `main` as the parent workspace's `.agents` pin is allowed: commit only that path.
  The parent is never pushed.

## Small traps

- In zsh write `"${SHA}:refs/heads/main"`; `$SHA:refs` is read as a modifier and the push silently
  sends nothing.
- A full local test run can fail on tests that also fail on the untouched upstream base; compare against
  that base before blaming a change.
