---
name: labo-git
description: Set up and verify local research Git and a separate publishable skills fork, including push guards and reviewed contribution checks. Use for Git/PR environment setup, not manuscript publication or ordinary source reading.
---

# Research Git and contribution setup

## Publication boundary

Two kinds of destination are kept apart.

- **Public**: the independent policy Git normally mounted at `.agents` (the user's skills fork and
  any upstream PR), and any public repository such as the website's `website/public`. Only reusable
  instructions, tools and fictional tests go to the policy Git, after the content review below.
- **The parent research repository**: commit it and push it to the user's own **private** remote as
  the work proceeds; this is routine and needs no per-push permission. Never push it to a public
  remote or open a PR from it. It excludes, by design, the archives with their own Gits
  (`reference/`, `writing/.corpus/`), which stay local.

Which workspace folders may be committed at all, and which stay local, is decided per folder
in a [placement policy](references/placement.md). It has no public kind: research material goes
only to a remote verified private, and an unverifiable remote counts as not private.

Both push and PR for skills operate within the policy Git and independently of the parent: select its
verified fork URL, commits and branch; a parent commit, gitlink update or parent push is not required to
publish a skill, and pushing the parent publishes no skill. Parent commits and selected gitlink updates are
recorded as ordinary parent work.
A push request alone does not request a PR; an authorized PR includes the
necessary push of its reviewed policy branch, without a second approval.

`.claude -> .agents` is a local alias, not another publishable tree. Recreate
that link locally using the policy's deployment instructions; do not publish
the parent to carry it. A standalone policy checkout, alternate host mount or
isolated contribution worktree uses the same policy-repository boundary, not
the surrounding workspace. Resolve the real Git root rather than trusting a
directory name or following links into research directories.

Only reusable instructions, tools and fictional tests belong in the policy
history. Moving or copying a source, manuscript, research result, progress log
or private profile into `.agents` does not make it publishable. Generic
`skills/<name>/references/` guidance is eligible after content review.
An exception requires an explicit user request identifying the material and
destination; ordinary commit, backup, push or PR wording does not grant it.

## Setup and verification

Inspect actual repository roots, status, remotes, effective hooks and existing
privacy configuration. Preserve dirty work, branches, archives and parent
gitlinks. Resolve the policy checkout from this skill's real location; it can
be mounted at `.agents` or `.claude`.

Read [setup and checks](references/setup.md) when installing or repairing this
boundary. The guard requires a reviewed head plus an exact destination for policy pushes. Its
`local-only` role, which disables every push of a repository while preserving local commits, is optional
and for repositories the user wants kept off all remotes (the source archives; the parent only if the user
asks). Install only in repositories covered by the user's setup request. Existing
remote history is not erased by these guards or ignore rules.

Review content as well as paths, including commit messages. The push guard
supports this boundary; it does not replace the content review.

Use [labo-pr](../labo-pr/SKILL.md) for a contribution. Setup may prepare and test
the environment without publishing it. Existing authorization for a specific
PR continues to apply; do not ask for the same approval again. An unrelated
dirty worktree calls for an isolated contribution checkout.

If GitHub diagnostics fail inside a restricted network, retry the specific
read-only check using the host's authorized network mechanism before concluding
that credentials are invalid. Never print tokens or request them in chat.
Report verified identity, fork/base URLs, guard status and remaining blockers
separately.
