# Codex host configuration

Official sources (recheck for the installed release):

- [Subagents and standalone role schema](https://learn.chatgpt.com/docs/agent-configuration/subagents#custom-agents)
- [Configuration reference](https://learn.chatgpt.com/docs/config-file/config-reference)
- [Local skill locations and directory symlinks](https://learn.chatgpt.com/docs/build-skills#where-codex-loads-local-skills)

Consult an available official `openai-docs` skill when useful, preserving the
session's local-inspection-first source order and reusing completed source
checks. The [project example](../assets/codex-agents.toml) and
[deployment procedure](deployment.md) are included in this distributable
checkout; external generated config is not needed to reconstruct the setup.
Codex/general use mounts the policy at `.agents`; Claude-only use mounts it at
`.claude` and does not create a Codex entry. For combined use, keep `.agents`
as the real submodule and add a whole-directory `.claude -> .agents` alias.
Do not create per-skill registration trees or another policy checkout.

Inspect `codex --version`, `codex --help`, and `codex debug models` when those
commands exist. Filter the model catalogue to IDs and supported effort;
raw catalogue entries may contain long system instructions. Current CLI
`--strict-config app-server --print-startup-config` validates recognized main
configuration without starting a model turn; filter its output rather than
publishing the user's requirements. This does not prove role execution.

For the standalone schema supported by Codex 0.164.0, project roles live in
`.codex/agents/*.toml`, each with `name`, `description`, and
`developer_instructions`. Set `model` and `model_reasoning_effort` together.
Role fields take precedence over resolved spawn/default settings; verify the
effective selection. Preserve the root's model and permissions. Older releases
may use a different role/config schema; use their supported schema rather than
mixing legacy `[agents.<role>] config_file` and standalone files.

Supported shared `[agents]` settings in this release include `enabled`,
`max_concurrent_threads_per_session`, `default_subagent_model`,
`default_subagent_reasoning_effort` and `interrupt_message`. The concurrent cap
excludes the primary and counts open spawned threads. Keep a separate bounded
task budget for descendants. Do not invent `agents.max_depth` or a config key
for `fork_turns` when the installed schema does not expose one. Fresh context
is selected at invocation (`fork_turns: "none"` on hosts exposing that field),
not by naming the role. Reuse a matching completed consultation.

Inspect role discovery in a fresh host/session, then run a bounded native call
if needed. Existing chats may retain their startup role roster; new files do
not prove an already-running tool schema has reloaded. A successful invocation
from a delegated worker proves nesting for that session, not an arbitrary
depth or the effective behavior of every other Codex client.
