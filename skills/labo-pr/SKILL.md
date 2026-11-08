---
name: labo-pr
description: Contribute selected research-skill improvements from the user's labo-skills fork to the shared upstream through a focused pull request, independently of manuscripts.
---

# Selective public pull request

Luna and Haiku only collect evidence here and hand substantive work to another agent: [roles](../research-router/references/editing-capability.md).

When author identity, voice, or preferences matter, consult the Labo workspace
[author profile](../../../profile/author-identity.md) when available. Keep
personal facts there rather than in skill text; update only explicit durable
facts or corrections from the user, or facts they ask to save, with source
context. Apply this skill's normal verification and publication rules.

Read [publication gate](references/publication-gate.md) before drafting a
commit or PR, including updates to an existing PR. Publish reusable rules and
procedures extracted from the work, not the underlying research materials.
Classify by content: a skill's generic `references/` guidance may belong in the
PR, while a paper, reading note or private example placed there does not. Use
the available Git/GitHub capability in the current host.

The normal contribution is **the user's fork branch → shared upstream**.
An unqualified PR request in this workflow refers to reusable skills/tools;
do not turn it into manuscript publication. For repository setup or push
protection use [labo-git](../labo-git/SKILL.md). Its
[publication boundary](../labo-git/SKILL.md#publication-boundary) applies to
both push and PR: the independent policy Git is the only skills destination; the parent
research repository goes to the user's private remote, never to a public one.
Operate inside the loaded policy checkout, normally the `.agents` submodule.
Do not create a parent PR to contribute; a parent push is not part of it. The local `.claude`
alias and parent gitlink are not publication targets or prerequisites.
Resolve that checkout from this skill's real directory rather than the shell's
current directory. Inspect its status and remotes, and the private parent's
status when one exists. A standalone checkout has no parent gitlink to update.
Identify the actual fork URL, upstream repository, head branch and base branch;
do not infer destinations from `origin` or `upstream` names alone. If HEAD is
detached, attach the work to the intended branch without discarding changes.
Prepare a focused branch containing selected skills, rules, tools and synthetic
examples; exclude unrelated fork customizations from the upstream diff.
When the checkout is dirty or its history is mixed, use a separate worktree
from the verified upstream base and apply only selected changes. Continue
preparation without disturbing the active checkout. Check every included
commit and record the reviewed head/destination using the
[publication guard](../labo-git/references/setup.md) when installed. Already
upstream changes need no reverse/reapply PR. Distinguish network failure from
authentication failure before asking the user to reauthenticate.
Show the concrete diff and destination. Ask whether to publish only when the
user has not already requested the PR. If the user prefers to push personally,
prepare the changes and commands without pushing.

Stage only selected public files inside the policy checkout. Never use a
parent-wide `git add .` to prepare a policy contribution. Committing or
pushing a public change does not authorize committing the private parent's
gitlink or adopting a new version. Those are separate local operations.

An improvement can be used in the fork before the PR is accepted. Detecting
an improvement alone does not authorize publishing it.
