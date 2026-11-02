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
   Alternatively `/math-… <bounded packet>` runs that same body in one fresh
   built-in general-purpose child via Claude's `context: fork`. Reconsider their
   model/effort for the actual task and account. The optional role installer
   with `--host claude` checks/generates that same native location, refuses a
   different `.claude` tree, and preserves differing existing files.
4. For Codex, run `scripts/install_roles.py` from the real policy checkout with
   `--workspace`, `--host codex`, and explicit `--model`/`--effort`. Preview, then
   add `--apply` to create `.codex/agents` role files. Use
   `assets/codex-agents.toml` as a supported-key example for `.codex/config.toml`.
   Create a new absent config from it or merge only needed `[agents]` keys into
   an existing file. Preserve primary model/effort, provider, permissions,
   hooks, MCP and unrelated settings. The installer leaves main settings alone.
   Codex adapters select model/effort and read the corresponding role SKILL.md
   in the existing delegated thread. Personal `~/.codex/agents` registration is
   unnecessary for this project. Claude skill frontmatter has no equivalent
   spawning/model meaning in Codex; other harnesses need their own native setup.
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
restricts its tools. Direct general-purpose skill execution retains a behavioral
read-only requirement; do not assert that it has the same technical restriction.
Check each entrypoint separately when claiming execution. Validation/loading
alone establishes neither child creation nor effective account access.

Model presets are revisable deployment choices, not a fixed capability ranking.
On 2026-11-02, official [Opus 5.5](https://platform.claude.com/docs/en/models/opus-5-5/overview)
used ID `claude-opus-5-5`, while local Claude Code 2.1.222's `opus` alias resolved
to `claude-opus-5`. The bundled Claude roles select the explicit 5.5 ID at high
effort. Recheck current official guidance, local selection and account access;
syntax/loading evidence alone does not prove live API compatibility.
