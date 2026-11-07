# Setup and checks

Apply the [publication boundary](../SKILL.md#publication-boundary): only the
independent policy Git is sendable by default. Parent history and everything
else in the workspace remain local. `.claude` is an alias of that policy, not
a second upload or a reason to publish the parent.

## Local research repository

Run `python3 <policy>/scripts/publication_guard.py install --repo <workspace>
--role local-only`. It rejects every ordinary push, including URL pushes,
tags and deletions, while preserving local commits. Existing source privacy
hooks are refreshed through their installer; other executable hooks are
preserved and chained. Custom hook paths need inspection. Repeat installation
is supported.

Ignore new research artifacts in the parent as appropriate for its layout.
Already tracked research may continue to have local commits. Do not untrack,
move, delete, rewrite history, remove remotes or destroy local backups just to
install this boundary. Previous uploads remain on GitHub until a separately
authorized cleanup. Fetch remains available. Archives with independent Git
need their own local-only guard; a parent's hook cannot protect another Git.

## Publishable policy fork

Verify the fork and upstream using authenticated repository metadata. Fetch
upstream and resolve the chosen public base to a commit. Do not mark a mixed
local HEAD as a trusted public base. Then run:

```sh
python3 <policy>/scripts/publication_guard.py install --repo <policy> --role policy
```

Prepare a branch in a separate worktree from the verified upstream base.
Apply only selected reusable changes; inspect shared-file hunks rather than
copying unrelated dirty files wholesale. Worktree hooks are shared but review
records are per worktree. Preserve the active checkout and parent gitlink.

After committing selected changes, run the read-only structural check:

```sh
python3 <policy>/scripts/publication_guard.py check --repo <contribution> --base <public-base-sha> --head HEAD
```

It examines every new commit against each parent, including merged branches,
add-then-delete content and old blobs being replaced. Only policy locations and
small UTF-8 text blobs are accepted; archives, PDFs, binary assets, Git LFS
pointers, research paths and non-regular files are rejected. An intentional
non-text contribution needs a separately reviewed extension of the guard, not
a bypass. Generic skill `references/` text is accepted.

This check does not understand private mathematics or certify content is
public. Inspect every included commit's diff and message under the publication
gate, plus PR title/body/attachments. After that review, record its scope:

```sh
python3 <policy>/scripts/publication_guard.py review --repo <contribution> --base <public-base-sha> --head HEAD --destination https://github.com/OWNER/labo-skills.git --content-reviewed
```

The record lives in local Git metadata. It binds the resolved base, head and
exact push URL. It neither pushes nor approves unrelated work. The hook checks
structure again and accepts only branch updates matching that head and URL;
new commits or another destination require a new review. Tags/deletions need
their own explicit workflow and are blocked here. Dirty worktree files do not
change reviewed committed bytes.

For an authorized push use
`git -C <contribution> push <verified-fork-url> HEAD:refs/heads/<topic>`.
For an authorized PR, push its reviewed policy branch as needed, then use
`gh pr create --repo <upstream> --head <fork-owner>:<topic> --base <base-branch>
--title ... --body-file <local-body-file>` with explicitly verified policy
repositories. Do not push the parent or create a parent PR. Its local commit
and gitlink state are not prerequisites for either operation. A push alone
does not trigger a PR. Already upstream changes need no reverse/reapply PR.

## Verification and limits

Run `status --repo <root>` to inspect the role, hook configuration and review
record. Exercise real pushes to disposable local bare repositories; blocked
pushes must leave remote refs unchanged. Check old-hook argument/stdin
preservation and source-privacy `check-local` compatibility.

Hooks protect ordinary Git use, not deliberate `--no-verify`, changed hook
configuration, another clone or direct API/LFS uploads. Never use those routes
to bypass a failed check. Reinstall local hooks/config after cloning/restoring.
Keep authentication checks separate from networking failures: a restricted
network can make `gh auth status` misleading. Do not recreate credentials until
an authentication failure has been established with working connectivity.
