# Claude Code host configuration

Official sources (recheck for the installed release):

- [Subagent scope and frontmatter](https://code.claude.com/docs/en/sub-agents#frontmatter-reference)
- [Native nesting](https://code.claude.com/docs/en/sub-agents#let-subagents-spawn-their-own-subagents)
- [Concurrency](https://code.claude.com/docs/en/sub-agents#concurrent-subagent-limit)
- [Settings](https://code.claude.com/docs/en/settings)
- [Skill locations and directory symlinks](https://code.claude.com/docs/en/skills#choose-where-skills-load)
- [Preloading skills](https://code.claude.com/docs/en/sub-agents#preload-skills-into-subagents)
- [Direct skill subagents](https://code.claude.com/docs/en/skills#run-skills-in-a-subagent)
- [Invocation arguments](https://code.claude.com/docs/en/skills#pass-arguments-to-skills)

The native [settings](../../../settings.json), [role files](../../../agents/)
and [deployment procedure](deployment.md) are included in this distributable
checkout. Mount the checkout at `.claude`, or use the whole-directory relative
alias `.claude -> .agents` for combined use. An earlier workspace's external
settings are not required.

Inspect `claude --version`, `claude --help`, existing project roles/settings and
only relevant user setting keys. Installed official `claude-code-setup` and
`plugin-dev/agent-development` skills can help discover existing automation and
role formats; reconcile their examples with the installed CLI and current
official docs. Older fixed model lists are not current availability evidence.

Project roles live in `.claude/agents/*.md` with YAML frontmatter. `model` and
`effort` select native behavior where supported. Current aliases such as `opus`
resolve dynamically: check real host events or API model usage rather than
claiming an exact resolved ID from the alias. A supported option or model alias
does not by itself prove account access. Preserve primary `model`/`effortLevel`.

Role discovery and skill discovery are separate. Claude reads both native
locations from its `.claude` entry. A whole-directory alias exposes the real
policy's skills, roles and settings together; no individual skill links are
needed. Check a fresh host roster before claiming successful discovery.
Codex-only use at `.agents` leaves `.claude` absent.

The mathematical role bodies/descriptions live once in `skills/math-…/SKILL.md`.
Direct `/math-… <packet>` execution uses Claude's `context: fork`, built-in
`general-purpose`, and native skill model/effort fields. Claude appends arguments
when the body has no argument placeholder. Native adapters instead set
`skills: [math-…]` to inject the body at startup; they supply model/effort/tools
and a short instruction to execute the current task, without invoking the skill
again. `disable-model-invocation: true` prevents preload and is not suitable
for these shared role skills. Missing or disabled preloads produce a warning
and are skipped, so check the role body actually loaded.

If using `claude plugin validate`, check that its report actually covers the
components. The tested CLI rejected an enclosing symlink, and returned success
with an empty component report for real directories even with malformed control
files; those runs did not establish component validation. Use explicit YAML/
frontmatter tests and native entry checks for the role files. The standard
skill-creator validator does not accept Claude extension keys; validation of a
standard-frontmatter projection is supplemental, not proof that those extension
fields work. Do not change the global validator to hide this distinction.
Native host loading and live entrypoint checks remain separate.

Claude Code 2.1.222 locally exposes native nesting and recognizes these
environment controls, which may be scoped to project `.claude/settings.json`:

```json
{
  "env": {
    "CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH": "2",
    "CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS": "6"
  }
}
```

Depth counts layers below the main conversation; `2` permits child and
grandchild. Keep the root's shared descendant allocation as well as the host
cap. Newer docs describe exceptions (for example some resume/fork/team paths),
so treat this as a native Agent spawning cap, not a universal process limiter.
Check installed support before copying these keys to another version. On a
host without native nesting, use parent-mediated redispatch and report it.

The decomposer needs `Agent` in its native tools. A proof worker can return
further packets for parent dispatch. The verifier's `Read, Glob, Grep` tool set
keeps it from editing or spawning; Lean execution needs a separately authorized
role with the required tool, preserving independent review boundaries.

Use default fresh subagents rather than fork mode for independent context.
Role files may reload, but creation of the first project `agents` directory and
environment settings can require a fresh session; report this and test a fresh
CLI. Do not add `bypassPermissions`, broad tool allows or subprocess spawning
to make a smoke test succeed. If authentication or account access prevents a
live probe, retain syntax/loading evidence and report live execution unverified.
