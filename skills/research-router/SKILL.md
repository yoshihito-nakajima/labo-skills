---
name: research-router
description: Route mathematical research tasks to the appropriate labo skill and check request understanding and the next action using available consultation.
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

Before delegation, inspect the actual callable interface and relevant local roles.
Use an available matching adapter or a bounded general-purpose assignment; another
host's preset is not a requirement. Default/inherited selection is valid. Keep
concrete model choices out of portable instructions and task handoffs. Missing
presets or runtime metadata alone are not reasons to stop. Follow
[task assignment](references/editing-capability.md) and the
[invocation contract](references/subagent-invocation.md). Actual host setup is a
separate task, not a routine prerequisite for writing.

For each user request, follow the [consultation and its availability fallback](references/consultation.md).
Slides are built in stages, with the user's reaction at each gate: see [staged build of slides](../deck-from-references/references/staged-build.md).

1. Identify the **artifact and reader**: research story, Lean, manuscript,
   slide, reading note, reference, website, or repo policy.
2. Consult the matching skill, read it completely, and follow **its own**
   references. Do not accumulate all skills' rules by default.
3. Workspace setup, paths, and inbox intake → `labo-layout`;
   research lifecycle and story → `research-management`; mathematical paper
   drafting or revision → `paper-writing`; mathematical paper review →
   `paper-referee`; paper compilation → `labo-build`; slides →
   `slide-authoring` (talk plan for a paper → `paper-talk-planning`; slides in the
   manner of example decks → `deck-from-references`); a private interactive HTML companion to a method
   paper's reading note → `reading-companion`; research positioning, source collection, paper/book
   explanation and reading notes → `reading-reference`; website →
   `website-publishing`; adversarial review of a finished explanation, page or
   note (flow and passage-level critique) → `exposition-review`; continuous Japanese reading translations →
   [japanese-translation](../japanese-translation/SKILL.md);
   actual Codex/Claude host settings and subagent roles →
   [agent-host-setup](../agent-host-setup/SKILL.md); skill improvements in the user's fork →
   `labo-self-improve`; Git boundaries and push setup →
   [labo-git](../labo-git/SKILL.md); selected upstream
   contributions → `labo-pr`; selective upstream adoption into the fork →
   `labo-sync`.
4. After the scope check, if task-specific delegation is useful,
   formulate a short task-specific assignment *from the selected skill* and
   follow the [subagent invocation contract](references/subagent-invocation.md).
   Host role presets are optional; the selected skill and current packet control
   responsibility and scope. Use the
   [mathematical role contract](references/mathematical-roles.md) for decomposition,
   proving and verification. Nested workers share the root's finite depth and
   descendant concurrency budget.
   Choose by the work required:

   - **Evidence and coordination**: literal source collection and dispatch.
   - **Content and production**: explanations of supplied arguments, literature
     synthesis, drafting and ordinary artifact edits.
   - **Proof**: new arguments, missing steps, hypotheses and counterexamples.
   - **Verification**: a separate fresh check of an exact statement and proof
     before adopting a newly established decisive mathematical conclusion as a
     research result or decisive proof dependency. Routine explanations and
     clearly marked tentative work follow their own assigned scope.

   Reconstructing missing arguments uses the proof responsibility, even in a summary;
   the authorized producer may do it sequentially when delegation is unavailable.
   Follow [concrete escalation triggers](references/editing-capability.md) when
   assumptions, proof steps, examples or source support reveal an obstacle.
5. Keep the user's `AGENTS.md` independent. Do not edit it as part of routing.

For paper-introduction drafting, restructuring or narrative assessment, also
use [paper-introduction](../paper-introduction/SKILL.md). It owns discovery and
telling order, while `paper-writing` owns manuscript edits and `reading-reference`
owns the positioning investigation. A report-only request remains report-only.

To stress-test a proof with several independent adversarial viewpoints, use
[proof-adversarial-review](../proof-adversarial-review/SKILL.md); to see which steps are key, what the
review found, how the result differs from prior work and whether it looks like a paper, on one
private page, use [reading-proof-review](../reading-proof-review/SKILL.md). Both apply to the user's
own manuscript or to a published paper, and both are report-only.

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

GitHub operations follow [labo-git's publication boundary](../labo-git/SKILL.md#publication-boundary):
by default only the independent policy Git is eligible for push or PR;
everything outside it remains local.

The research plan supplies human context; a skill supplies the operational
rules. Neither is an excuse to expose private material in public changes.

GitHub operations follow [labo-git's publication boundary](../labo-git/SKILL.md#publication-boundary):
by default only the independent policy Git is eligible for push or PR;
everything outside it remains local.
