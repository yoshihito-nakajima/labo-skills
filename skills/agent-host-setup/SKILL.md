---
name: agent-host-setup
description: Configure and validate Codex or Claude Code host settings and mathematical subagent roles beyond skill instructions, including native nesting, model selection and bounded delegation.
---

# Agent host setup

Luna and Haiku only collect evidence here and hand substantive work to another agent: [roles](../research-router/references/editing-capability.md).

Use this skill for actual host configuration. For an ordinary research task,
use the selected research skill and [invocation contract](../research-router/references/subagent-invocation.md).

The whole directory containing `skills/`, Claude-native `agents/` and root
`settings.json` is the distributable source. Follow
[deployment](references/deployment.md): `.agents` for Codex/general harnesses,
`.claude` for Claude Code, or `.agents` plus the whole-directory alias
`.claude -> .agents` for both. External Codex files and private validation
records are optional deployment results.

1. Inspect the installed CLI version/help, project and relevant user settings,
   existing role definitions and available native delegation fields. Read only
   relevant keys; avoid printing authentication, environment secrets or private
   session history. Discover available setup/agent-development skills and use
   their applicable guidance. A recommendation-only skill does not itself
   authorize implementation; the user's request can authorize it separately.
2. Resolve unstable or missing behavior against official host documentation.
   Read [Codex](references/codex.md) or [Claude Code](references/claude.md) as
   relevant. Check installed support before adding keys: current web docs may
   describe a later release. Record source URLs and the version actually tested.
3. Choose the smallest project-scoped settings/roles that implement the request.
   Preserve primary model/effort, permissions, hooks, provider, MCP and unrelated
   user configuration. Global changes need an understood scope and authority;
   a project request normally belongs in project files. Keep reusable behavior
   in this policy checkout and private host choices in the consuming workspace.
4. Keep role instructions portable: no concrete model IDs, provider aliases or
   fixed reasoning levels in shared skills, templates or task handoffs. Bundled
   native adapters omit model/effort and use the host's selection behavior.
   The [role installer](scripts/install_roles.py) previews or creates adapters;
   optional `--model`/`--effort` overrides are deployment choices only. Use such
   overrides only when requested or justified by the actual setup task and
   confirmed supported by the host. A missing preset is not a reason to change
   configuration during ordinary research or writing; use the routing fallback.
   Role bodies live in `math-decomposer`, `math-proof-worker`, `math-verifier`.
   Native adapters load these instructions into their current child. Direct skill
   loading does not by itself spawn a separate worker or establish independence.
   Preserve differing existing files, unrelated settings and the user's primary
   runtime choices. Single-host setup leaves the other host's entry absent.
5. Validate syntax and host loading, then use a tiny native delegation probe
   when authorized. Bound its depth, concurrency, tools, time and cost. Test
   actual parent→child→grandchild when claiming nesting. Check effective model
   selection from host events/metadata where available. A read-only synthetic
   lemma can exercise statement/dependency/gap return without opening research.
   Never use subprocess CLIs to bypass disabled native delegation or limits.
6. Report separately: files parse, host loads roles/settings, actual nested call,
   actual selected model/effort, mathematical output checked, and untested parts.
   A smoke test proves neither general proof ability nor technical enforcement
   of behavioral rules. State reload/restart requirements and remaining limits.
   Commit/push only within the user's publication authorization, policy before
   the parent pin when both repositories are involved.

Examples (preview first; defaults use host selection):

```sh
python3 .agents/skills/agent-host-setup/scripts/install_roles.py --workspace . --host codex
python3 .claude/skills/agent-host-setup/scripts/install_roles.py --workspace . --host claude
```

The installer is optional setup tooling, not a prerequisite for ordinary task work.
