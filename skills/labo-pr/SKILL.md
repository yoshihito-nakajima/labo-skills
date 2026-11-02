---
name: labo-pr
description: Contribute selected research-skill improvements from the user's labo-skills fork to the shared upstream through a focused pull request, independently of manuscripts.
---

# Selective public pull request

Before substantive work, follow [eligibility and handoff](../research-router/references/editing-capability.md).

For each user request, follow the [required consultation](../research-router/references/consultation.md).

When author identity, voice, or preferences matter, consult the Labo workspace
[author profile](../../../profile/author-identity.md) when available. Keep
personal facts there rather than in skill text; update only explicit durable
facts or corrections from the user, or facts they ask to save, with source
context. Apply this skill's normal verification and publication rules.

Read [publication gate](references/publication-gate.md) before drafting a
commit or PR. Use the available Git/GitHub capability in the current host.

The normal contribution is **the user's fork branch → shared upstream**.
Operate inside the loaded policy checkout, normally the `.agents` submodule.
The private workspace does not need to publish its research to contribute.
Resolve that checkout from this skill's real directory rather than the shell's
current directory. Inspect its status and remotes, and the private parent's
status when one exists. A standalone checkout has no parent gitlink to update.
Identify the actual fork URL, upstream repository, head branch and base branch;
do not infer destinations from `origin` or `upstream` names alone. If HEAD is
detached, attach the work to the intended branch without discarding changes.
Prepare a focused branch containing selected skills, rules, tools and synthetic
examples; exclude unrelated fork customizations from the upstream diff.
Show the concrete diff and destination. Ask whether to publish only when the
user has not already requested the PR. If the user prefers to push personally,
prepare the changes and commands without pushing.

Stage only selected public files inside the policy checkout. Never use a
parent-wide `git add .` to prepare a policy contribution. Committing or
pushing a public change does not authorize committing the private parent's
gitlink, adopting a new version, or pushing manuscripts.

An improvement can be used in the fork before the PR is accepted. Detecting
an improvement alone does not authorize publishing it.
