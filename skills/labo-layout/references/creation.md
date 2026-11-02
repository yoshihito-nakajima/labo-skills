# Workspace creation

## Connect the policy once

First use or create the user's fork of `momota1029/labo-skills` as part of
the requested setup. Resolve the owning account or organization from the
request and available context; ask only if the destination is unclear.
Then connect **that fork** to the user's research repository:

```sh
git init                            # only for a new, not-yet-versioned workspace
mkdir -p inbox
git submodule add https://github.com/YOUR_ACCOUNT/labo-skills.git .agents
```

Replace `YOUR_ACCOUNT` with the chosen fork's owner, or use its actual Git
URL. The maintainer of the shared upstream may use it directly. Ordinary
users pin their own fork in `.gitmodules`, enabling local adoption and PRs
without waiting for upstream acceptance. Reuse an existing setup rather than
creating another fork or changing its remotes. If `.agents` contains files,
inspect them and preserve personal work before connecting a submodule.
Do not overwrite an existing checkout or run `update --remote` to initialize it.
After cloning an existing workspace, use:

```sh
git submodule update --init --recursive -- .agents
```

The checkout's `skills/` is now `.agents/skills/`. Its source files and tools
are used in place. No forwarding skills or project installation are needed.
Runtime requirements are Python 3.11+, Git and PyYAML 6.x.

Skills and tools are edited in this fork checkout. `labo-self-improve` owns
improvements and `labo-pr` owns selected contributions to the shared upstream.
An ordinary `layout init` only creates workspace structure; it does not
create forks, initialize submodules, or update their pinned versions.

## Create only the requested structure

In these examples `<labo-script>` means the absolute path to
`../../scripts/labo.py` from the real `labo-layout` skill directory.
The launcher defaults to its Git superproject from any working directory.
For a standalone policy checkout or a different destination, add
`--workspace /absolute/path/to/workspace` to each command. The selected
workspace must be outside the public policy checkout.

```sh
python3 <labo-script> layout init
python3 <labo-script> layout new research finite-observations \
  --title 'Finite observations and reconstruction' \
  --summary 'Determine which data can be recovered from finite observations.' \
  --next 'Compare two elementary examples with the same observations.'
python3 <labo-script> layout new paper reconstruction
python3 <labo-script> layout new reference example-source
```

- `layout init` adds `inbox/`, `research/`, `lean/`, `writing/`,
  `writing/.corpus/`, `writing/.rules/`, `reading/`, `reference/`, and
  `output/`. It creates generic corpus/rules guides and an empty corpus index
  only when absent, creates an empty `AGENTS.md` if absent, and appends missing
  workspace ignore patterns to `.gitignore`. Root `inbox/` contents are local
  unassigned intake; assigned originals under `research/<slug>/inbox/` and
  source PDFs under `reference/` remain trackable. It does not populate
  research programs, import source files, install dependencies, or run Git.
  Repeating it preserves existing files; empty directories can be recreated
  after cloning. Inspect pre-existing broad ignore rules such as `*.pdf` so
  they do not hide assigned source materials.
- `layout new research` creates `research/<slug>/plan.md`, `inbox/` and the same
  empty sequential `exploration/tree.json` as `research exploration init`.
  The YAML contains the supplied title, summary, optional next step, an empty
  tag list and `in_progress`. Complete the narrative body from actual sources.
  Create `claims.yaml` when registering concrete claims; an empty tree does not
  certify any mathematics. Existing programs follow the
  [safe resume/migration procedure](research-migration.md) during plan editing
  or exploration, while read-only requests preserve their layout.
- `layout new paper` creates `writing/<slug>/main.tex` and
  `sections/01-introduction.tex`, compatible with `paper map` and `build`. It
  also creates missing workspace-level corpus/rules guides, preserving any
  existing local index or rules. It creates no research program or translation
  automatically.
- `layout new reference` creates `reference/<key>/reference.md` for identity
  and version provenance. Fill it from the source; do not invent metadata.

Names use lowercase kebab-case. New-item commands refuse an existing target,
including an empty directory; inspect and complete it directly when appropriate.
All creation commands support `--dry-run`, which reports planned changes
without creating directories or files. Symlinked destination components are
rejected. The tools do not move inbox material; the agent preserves sources
and records provenance in the context of the actual research request.

Templates are maintained in this skill's `assets/`; generated research
documents belong to the workspace. The only writing guides initialized from
templates are the workspace-owned corpus and rules files under `writing/`;
the policy skill documentation itself is not copied into the workspace.
`website/`, `profile/`, Japanese translations, Lean project configuration,
and reading outputs are created only when needed by their own tasks.

## Check the resulting work

After creating a research plan, run `research check` and inspect its story
and source links. For a new paper, `paper map --paper <slug>` checks that its
section openings are readable; `build --paper <slug> --dry-run` shows the
build command without compiling. These checks validate structure, not content.
No layout command commits, pushes, opens a PR, or publishes research.
