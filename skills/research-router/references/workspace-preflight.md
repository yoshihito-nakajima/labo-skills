# Lightweight workspace preflight

The preflight of [research-router](../SKILL.md): run it once for each new
task that reads or changes a Labo workspace, before routing or substantive
work.

For each new task that reads or changes a Labo workspace, run this once before
routing or substantive work. Do not repeat it when the same request passes
through consultation or another skill.

1. Resolve the workspace root and inspect its branch, configured tracking
   branch, `git status --short --branch`, submodule pins, and task-relevant
   paths. Use the branch's actual tracking remote; do not assume it is named
   `origin`.
2. If a tracking branch is configured, fetch its remote once with
   `git fetch --no-recurse-submodules <remote>`. If it contains no commits to
   add, do nothing. If it is strictly ahead of the local branch, advance with
   `git merge --ff-only @{upstream}` only when the worktree and submodules are
   clean and the incoming commits do not change submodule gitlinks. If there is
   an incoming update that cannot meet these conditions, preserve the current
   state and skip the pull; continue from the local workspace when possible and
   report the pending update briefly. If no tracking branch exists or fetching
   fails, continue locally and mention the skipped sync when relevant. After a
   fast-forward, recheck the task paths and submodule pins before proceeding.
3. For file-producing tasks, locate the existing target and follow its local
   layout. Create only paths the task needs. Do not initialize or reorganize
   the whole workspace as a routine preflight; a placement question alone
   does not authorize creating files.

Never stash, reset, rebase, or update a submodule to its remote tip as part of
this preflight. Selective skill updates use `labo-sync`; the workspace's
recorded submodule pins remain authoritative.
