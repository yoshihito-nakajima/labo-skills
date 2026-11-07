# Three deployments from one policy checkout

Distribute this whole policy directory: `skills/`, the reusable launcher/code,
Claude-native `agents/` and the minimal root `settings.json`. No private parent
workspace, external generated `.codex/` files or validation record is required.

| Use | Real submodule | Additional entry |
| --- | --- | --- |
| Codex or a harness using `.agents` | `.agents` | none |
| Claude Code | `.claude` | none |
| Codex and Claude Code together | `.agents` | whole-directory relative symlink `.claude -> .agents` |

A single-host deployment uses its own native location. Do not create the other
host's directory as a routine setup step. In combined use, both names reach one
checkout, including the same `skills/`, `agents/` and `settings.json`; individual
skill links and a second policy copy are unnecessary.

Register only real submodule mounts in `.gitmodules`: `.agents` for Codex or
combined use, `.claude` for Claude-only use. In combined use, track the relative
`.claude -> .agents` symlink as an ordinary Git entry; it is not another
submodule. A recursive clone initializes the `.agents` submodule, and the
tracked alias exposes that same checkout to Claude. Adding a second submodule
entry for the symlink does not create a second initialized checkout.

1. Resolve the real loaded skill/script directory and consuming workspace.
   Inspect installed host help/version and relevant existing settings. Consult
   available official setup/documentation skills, reusing completed checks.
   Confirm local support before applying native fields or settings.
2. Choose the deployment above. For combined use, create the relative
   `.claude -> .agents` link only after checking `.claude` is absent. Preserve
   an existing directory or link, inspect its contents, and merge any wanted
   native configuration into the real checkout before a deliberate migration.
   Do not overwrite user files or build per-skill forwarding trees.
3. Claude Code reads bundled `agents/*.md` and root `settings.json` directly
   through its `.claude` entry. Each native adapter preloads its matching
   `math-…` skill with `skills: [role]`; the body and description live in that
   skill. It executes the current task without invoking the skill again.
   Direct loading of `/math-… <bounded packet>` supplies instructions in the
   current context; it does not itself request a fork. Bundled adapters omit
   model/effort so the host chooses them. The optional role installer
   with `--host claude` checks/generates that same native location, refuses a
   different `.claude` tree, and preserves differing existing files.
4. For Codex, run `scripts/install_roles.py` from the real policy checkout with
   `--workspace` and `--host codex`. Model/effort overrides are optional. Preview, then
   add `--apply` to create `.codex/agents` role files. Use
   `assets/codex-agents.toml` as a supported-key example for `.codex/config.toml`.
   Create a new absent config from it or merge only needed `[agents]` keys into
   an existing file. Preserve primary model/effort, provider, permissions,
   hooks, MCP and unrelated settings. The installer leaves main settings alone.
   Codex adapters use native defaults or local overrides and read the role SKILL.md
   in the existing delegated thread. Personal `~/.codex/agents` registration is
   unnecessary for this project. Shared skill frontmatter contains no host-specific spawning/model fields; other
   harnesses use their own native interface or the sequential routing fallback.
5. Validate parse and fresh native discovery separately from live execution.
   Use bounded native nesting probes when authorized; keep unavailable model
   access or authentication explicit. Codex depth is a decreasing invocation
   packet budget; Claude's bundled settings additionally select two native
   subagent layers and six concurrent subagents. All branches share the root's
   allocation. Host upgrades and authentication changes keep their own scope.

The launcher and installer resolve their real source path, so invoking them
through `.claude -> .agents`, from an unrelated working directory or after
relocation keeps the same implementation. Tests exercise all three deployments
as actual Git submodules, including a workspace name with spaces, repeated
invocation, relocation, native role/settings reads and conflict preservation.
Single-host fixtures assert that the other host's directories remain absent.

Keep the role skills available to automatic invocation: Claude skips missing or
disabled preloads with a warning, so a native adapter without its loaded skill
does not supply the full role. The native verifier's `Read, Glob, Grep` list
restricts its tools. Direct skill loading retains a behavioral
read-only requirement; do not assert that it has the same technical restriction.
Check each entrypoint separately when claiming execution. Validation/loading
alone establishes neither child creation nor effective account access.

Concrete runtime choices belong to local host configuration or actual invocations,
not portable handoffs or shared role bodies. Do not infer account availability from
bundled adapters. Missing selection controls or roles do not block ordinary authorized
work: use the consultation and assignment fallbacks in research-router. Independent
review still requires a genuinely separate context.
