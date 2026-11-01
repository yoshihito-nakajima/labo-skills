---
name: research-router
description: Route mathematical research tasks to the appropriate labo skill and require a brief consultation on request understanding and the next action.
---

# Research routing

Before drafting or changing source artifacts, follow
[editing capability and handoff](references/editing-capability.md). Apply this
check to your own role as well as delegated workers.

## Lightweight workspace preflight

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

## Surface relevant capabilities

When the task reveals a concrete gap or a workspace capability that could
materially help with the current or a likely next step, follow
[capability tips](references/capability-tips.md). Mention the trigger, the
available action, and its practical benefit briefly. Keep the tip tied to the
user's work; do not recite a general skill or tool catalog.

When author identity, voice, or preferences matter, consult the Labo workspace
[author profile](../../../profile/author-identity.md) when available. Keep
personal facts there rather than in skill text; update only explicit durable
facts or corrections from the user, or facts they ask to save, with source
context. Apply the selected skill's normal verification rules.

Before the first delegation, including consultation, retrieve the models and
reasoning settings actually callable through the host's delegation interface,
using its discovery tools/API or runtime catalogue. A provider-wide catalogue
alone does not establish availability. If readily exposed, obtain your own
model and effort from matching current-session metadata; otherwise mark them
unknown, rather than inferring them from defaults or self-description.

Choose each needed role's model and effort from that set using task requirements
and available model-selection skills or current official guidance. Do not fix
advisor, prover, or reviewer roles to model families by convention. Honor explicit
user model constraints; otherwise prefer current suitable models and justify older
choices. Reuse discovery within the task and pass selections through actual tool
arguments.
Apply the same criteria to roles you keep; delegate content-understanding or
research-reasoning work if your own model's suitability cannot be established.

For each user request, follow the [required consultation](references/consultation.md).

1. Identify the **artifact and reader**: research story, Lean, manuscript,
   slide, reading note, reference, website, or repo policy.
2. Consult the matching skill, read it completely, and follow **its own**
   references. Do not accumulate all skills' rules by default.
3. Workspace setup, paths, and inbox intake → `labo-layout`;
   research lifecycle and story → `research-management`; mathematical paper
   drafting or revision → `paper-writing`; mathematical paper review →
   `paper-referee`; paper compilation → `labo-build`; slides →
   `slide-authoring`; source collection, paper/book explanation and reading
   notes → `reading-reference`; website → `website-publishing`; skill
   improvements in the user's fork → `labo-self-improve`; selected upstream
   contributions → `labo-pr`; selective upstream adoption into the fork →
   `labo-sync`.
4. Beyond the required consultation, if task-specific delegation is useful,
   formulate a short task-specific assignment *from the selected skill*.
   Do not depend on a proprietary stored subagent persona or prompt template.
   Independent result reviews start in a fresh context with the original request,
   constraints, artifact, and necessary primary sources. Do not inherit the
   implementation conversation or the author's or coordinator's verdict.
   Choose by the mathematical judgment needed to establish correctness:

   - **Routine processing** (organization, extraction, prescribed conversion):
     lightweight model, low reasoning effort.
   - **Content understanding** (literature synthesis, explaining known arguments):
     general-purpose model, standard or higher reasoning effort.
   - **Research reasoning** (proofs, assumptions, counterexamples, mathematical
     review): current upper-tier model suited to mathematical reasoning, high effort.

   Reconstructing missing arguments counts as research reasoning, even in a
   summary.
5. Keep the user's `AGENTS.md` independent. Do not edit it as part of routing.

The research plan supplies human context; a skill supplies the operational
rules. Neither is an excuse to expose private material in public changes.
