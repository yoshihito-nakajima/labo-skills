---
name: research-router
description: Route mathematical research tasks to the appropriate labo skill and require a brief consultation on request understanding and the next action.
---

# Research routing

Before substantive work, follow
[substantive-work eligibility and handoff](references/editing-capability.md).
Apply this check to your own role as well as delegated workers.

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
alone does not establish availability. Establish your own model and effort
from the invocation provenance accepted by the eligibility rule; keep
unverified values unknown rather than inferring them from defaults or
self-description.

Before making any subagent call, including the required consultation, follow
the [subagent invocation contract](references/subagent-invocation.md) for
thread isolation, assignment packets, and independent-review boundaries.

Choose each needed role's model and effort from that set using task requirements
and available model-selection skills or current official guidance. Do not fix
advisor, prover, or reviewer roles to model families by convention. Honor explicit
user model constraints; otherwise prefer current suitable models and justify older
choices. Reuse discovery within the task and pass selections through actual tool
arguments.
Apply the eligibility rule to roles you keep; delegate all substantive work
when your own eligibility cannot be established.

For each user request, follow the [required consultation](references/consultation.md).

1. Identify the **artifact and reader**: research story, Lean, manuscript,
   slide, reading note, reference, website, or repo policy.
2. Consult the matching skill, read it completely, and follow **its own**
   references. Do not accumulate all skills' rules by default.
3. Workspace setup, paths, and inbox intake → `labo-layout`;
   research lifecycle and story → `research-management`; mathematical paper
   drafting or revision → `paper-writing`; mathematical paper review →
   `paper-referee`; paper compilation → `labo-build`; slides →
   `slide-authoring`; research positioning, source collection, paper/book
   explanation and reading notes → `reading-reference`; website →
   `website-publishing`; continuous Japanese reading translations →
   [japanese-translation](../japanese-translation/SKILL.md);
   actual Codex/Claude host settings and subagent roles →
   [agent-host-setup](../agent-host-setup/SKILL.md); skill improvements in the user's fork →
   `labo-self-improve`; selected upstream
   contributions → `labo-pr`; selective upstream adoption into the fork →
   `labo-sync`.
4. Beyond the required consultation, if task-specific delegation is useful,
   formulate a short task-specific assignment *from the selected skill* and
   follow the [subagent invocation contract](references/subagent-invocation.md).
   Host role presets may select a suitable model and narrow job; the selected
   skill and current packet remain authoritative. Use the
   [mathematical role contract](references/mathematical-roles.md) for decomposition,
   proving and verification. Nested workers share the root's finite depth and
   descendant concurrency budget.
   Choose by the mathematical judgment needed to establish correctness:

   - **Literal evidence collection and coordination**:
     lightweight model, low reasoning effort.
   - **Content understanding** (literature synthesis, explaining known arguments):
     general-purpose model, standard or higher reasoning effort.
   - **Research reasoning** (proofs, assumptions, counterexamples, mathematical
     review): current upper-tier model suited to mathematical reasoning, high effort.

   Reconstructing missing arguments counts as research reasoning, even in a
   summary.
5. Keep the user's `AGENTS.md` independent. Do not edit it as part of routing.

For paper-introduction drafting, restructuring or narrative assessment, also
use [paper-introduction](../paper-introduction/SKILL.md). It owns discovery and
telling order, while `paper-writing` owns manuscript edits and `reading-reference`
owns the positioning investigation. A report-only request remains report-only.

For whole-paper architecture or structural reassessment, use
[paper-structure](../paper-structure/SKILL.md). It maps section roles and
proposed moves from the actual question and proof route. For explicit
definition/assumption/result dependencies, topological order, cycle diagnosis,
prerequisite closure or change impact, use
[knowledge-dependencies](../knowledge-dependencies/SKILL.md). Its declared hard
dependencies constrain logical order; reader order can include clear previews.

For nested mathematical exploration, compact progress trees or bounded
parallel node ownership, use [research-exploration](../research-exploration/SKILL.md).
For accepted plan edits or exploration in an existing program, use
[labo-layout's safe migration](../labo-layout/references/research-migration.md)
to add missing current structure. Read-only work leaves it intact; missing
structure is not a compliance or proof failure. Existing plans retain their format and two statuses; tree
classification is separate from logical dependencies and formal-proof evidence.

Research planning, substantive manuscript writing, changed contribution claims,
submission preparation, and own-research talks with novelty/comparative claims
must pass the [research-positioning checkpoints](../reading-reference/references/research-positioning.md).
The artifact's skill still owns writing or review; `reading-reference` owns the
investigation and reusable memo. Initial blind readings precede memo access;
routine edits and report-only tasks keep the protocol's scope boundaries.

The research plan supplies human context; a skill supplies the operational
rules. Neither is an excuse to expose private material in public changes.
