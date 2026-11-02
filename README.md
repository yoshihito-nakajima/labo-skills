# labo-skills

Shared research skills developed through actual mathematical work.
**Fork this repository, then add your fork as the `.agents` submodule in
your own research repository.** Use and improve its skills, rules, and tools
in that checkout, and send useful changes back here as pull requests.
Your research repository can have any name; `labo` is the example below.

Research plans describe the **story of a research program**, not a queue of
papers. Develop and revise that story alongside prior literature and relevant
Lean formalizations: sources can reshape the narrative, while formalization
can clarify assumptions, definitions, and obstructions. Write the English paper
from this evolving evidence, with its introduction as part of the story.
Papers, slides, reading notes, and web pages are outputs of the
research institute. Japanese translations are supplementary reading/checking
material; English remains the manuscript original.
Use [japanese-translation](skills/japanese-translation/SKILL.md) for a continuous
Japanese reading copy that includes its equations and figures and preserves
the source's argument, so wording and reasoning can be examined in Japanese.

## Separation and ownership

- Public: this repository, its skills, numbered reviewing rules, software,
  fictional examples, and generic changes proposed by pull request.
- Private: your research repository, with research plans, original
  inbox material, Lean files, manuscripts, references, presentations, personal
  skills, and any unpublished writing.
- The distribution model is **fork, use, improve, and selectively contribute
  upstream**. The researcher's fork holds their public research policy; the
  private parent records which commit of that fork it uses. A submodule is
  the normal operating model, not an optional wrapper around an installed CLI.
- Additional skills in `.agents/skills/` belong to the policy fork. Keep
  private-only skills outside that public checkout in a host-supported location
  chosen by the user. Public policy and research have independent Git histories.
- Public pull requests must be prepared from **sanitized, independently
  reproducible commits**. Nothing automatically publishes private text.

`momota1029/labo-skills` is the current shared upstream. Its maintainer can
work directly in it; other researchers normally use their own forks.
Improvements can remain useful in a fork whether or not they are proposed
or accepted upstream. Different mathematical practices need not converge on
one personal configuration.

## Use the fork as a submodule

First fork `momota1029/labo-skills` into your GitHub account or chosen
organization. From your research repository root, replace `YOUR_ACCOUNT`
below with the owner of **your fork**:

```sh
git submodule add https://github.com/YOUR_ACCOUNT/labo-skills.git .agents
```

Start with `git init` if the chosen workspace is not yet a Git repository.
If `.agents` already contains files, preserve them before replacing that
directory with a submodule. `.gitmodules` should point to your fork, so the
research workspace can use your improvements before any upstream PR is merged.

Commit `.gitmodules` and the `.agents` gitlink in the private
repository. The parent stores a commit reference, not copies of the skills.
After cloning an already-configured `labo`, initialize the recorded checkout:

```sh
git submodule update --init --recursive -- .agents
```

An ordinary update checks out the recorded commit, often in detached-HEAD
state; it does not mean "use the newest upstream version." Before editing
policy, inspect the submodule's status and remotes and work on a branch in
the researcher's fork. Preserve uncommitted changes. Do not silently run
`update --remote`, reset a checkout, change remotes, or create a fork.

## Improve in your fork and contribute upstream

The normal flow is:

```text
shared labo-skills → your fork → .agents in your research repository
shared labo-skills ← selected pull requests ← improvements in your fork
```

1. Edit the actual skills or tools in `.agents` while using them for research.
   Commit the improvement on a branch in your fork. Describe the observed
   problem and check the change with a small reproducible example.
2. To use that version in your research repository, record its commit in the
   parent gitlink. Before sharing the parent commit, push the policy commit
   to the fork named in `.gitmodules` so others can fetch it.
3. When an improvement would help others, propose a focused PR from a branch
   in your fork to the shared upstream. Include the reusable change and
   synthetic examples, independently of manuscripts and fork-specific choices.
   `labo-self-improve` develops the improvement; `labo-pr` prepares the contribution.

Using an improvement does not require upstream acceptance. Sending a PR is
optional, and its acceptance does not automatically change anyone's workspace.
To adopt upstream changes, fetch and review them, integrate the chosen changes
into your fork, validate that version, then update the parent's gitlink.
`labo-sync` guides this incoming path; a routine `git pull` of the private
research repository does not need a dedicated skill. Preserve your fork's own
work; do not reset it to upstream as an update strategy.

Conventionally `origin` points to your fork and `upstream` to the shared
repository. Inspect actual URLs before pushing or selecting a PR destination;
remote names alone do not establish ownership. Git actions follow the user's
requested scope, including when they prefer to push personally.

No installer copies skills into the private repository. There is no `vendor/`,
generated forwarding `SKILL.md`, private README requirement, or automatic
update of another repository.

The checked-out harness is the authority: reusable instructions, formats,
templates, implementation, and synthetic tests all live here. Consuming
workspaces conform to that checkout, not the reverse. Improve the actual
checkout while using it; do not first build a private `labo` implementation
and leave the shared skills describing a different system. Private research
and user-specific records remain in the parent workspace.

## Agent integration

Use [agent-host-setup](skills/agent-host-setup/SKILL.md) for actual Codex or
Claude Code settings and native mathematical roles. Its create-only installer
requires an explicit model and effort, preserves existing differing roles, and
references this checkout's current contracts. Host discovery, role loading,
actual model execution and parent→child→grandchild execution are separate
validation steps. The [invocation contract](skills/research-router/references/subagent-invocation.md)
allocates a shared finite descendant budget; the
[mathematical roles](skills/research-router/references/mathematical-roles.md)
specify exact lemma interfaces, hypothesis discharge, integration and independent
verification. Native caps and behavioral allocation are reported separately.

The mathematical role bodies and descriptions live in
[math-decomposer](skills/math-decomposer/SKILL.md),
[math-proof-worker](skills/math-proof-worker/SKILL.md), and
[math-verifier](skills/math-verifier/SKILL.md). Project Codex adapters read these
skills in their existing child. Claude supports both direct forked-skill
execution and native adapters that preload the same skill; the adapter does
not reinvoke it. Claude-specific frontmatter does not configure other harnesses.

Distribute this policy directory as `.agents` for Codex/general harnesses, or
as `.claude` for Claude Code. For both, use an `.agents` submodule and the
whole-directory relative alias `.claude -> .agents`. Native Claude `agents/`
and minimal `settings.json` ship at the policy root; external Codex configuration
is expanded from the included installer/example. The
[deployment procedure](skills/agent-host-setup/references/deployment.md) covers
these three forms without individual skill links or a second policy copy.
Actual submodule tests cover fresh deployment, external working directories,
relocation, repeat runs and conflict preservation.

The actual skills are `skills/<name>/SKILL.md` inside this checkout.
`plugin.json` also describes the collection for
[Agent Plugin](https://agent-plugins.org/specification) hosts; plugin installation
is not a prerequisite for submodule use. Register the checked-out collection
with the host, preserving its location rather than maintaining another copy.

[Codex discovers repository skills](https://developers.openai.com/codex/skills)
under `.agents/skills`. Mounting this repository at `.agents` places the real
skills there directly, without copies or forwarding links. Other hosts can
register the same checked-out collection using their discovery mechanism.
Existing submodule placements can still execute the launcher; moving them
is a separate migration. `AGENTS.md` remains entirely user-owned.

The source-local runtime also works when this checkout is mounted at `.claude`
or another user-selected path. Substitute that path in shell examples, or
resolve the launcher from the real loaded skill directory. Host discovery is
separate: a working launcher does not imply that every host automatically
discovers every placement. Do not maintain parallel copies of the harness.

Each skill owns its rules under its own `references/`. In particular,
`paper-referee` standards do not govern slides. Routing and task-specific
delegation belong to skills and the current agent host, not a mandatory set
of named agents or saved subagent prompts. Private repositories do not need
README copies of these policies.

## Run the checked-out tools

The runtime needs Python 3.11+, Git, and PyYAML 6.x. Install PyYAML into the
chosen Python environment if it is missing:

```sh
python3 -m pip install 'PyYAML>=6,<7'
```

On native Windows, use the selected `python` executable in place of `python3`.
The runtime does not require WSL; host-relative input names in evidence and
reader records still use normalized forward-slash paths. CLI text/JSON output is
UTF-8, including when piped on Windows; staged prefix text preserves original
line-ending bytes.

Do **not** install this project to use it. From the private `labo` root,
invoke the launcher in the submodule. Replace `example-paper` with an actual
paper directory:

```sh
python3 .agents/scripts/labo.py layout init
python3 .agents/scripts/labo.py research check
python3 .agents/scripts/labo.py research list --format json
python3 .agents/scripts/labo.py paper map --paper example-paper
python3 .agents/scripts/labo.py paper section --paper example-paper --name 01-introduction
python3 .agents/scripts/labo.py build --paper example-paper --dry-run
```

The launcher imports the code beside it, so the policy checkout and executed
tools cannot accidentally come from different installations. Unless
`--workspace` is explicit, Git identifies the launcher's **superproject** as
the research workspace; the shell's current directory is irrelevant. A
standalone checkout requires `--workspace /path/to/private/labo`. An agent
resolves the launcher relative to the real loaded skill directory, including
when that directory was reached through a symlink. An explicitly supplied
relative workspace path is relative to the invocation directory.
Place `--workspace` after the selected leaf command, for example
`python3 /path/to/labo-skills/scripts/labo.py evidence status --research example
--workspace /path/to/private/labo`; it is not a top-level option before `evidence`.

## Create and use the research workspace

Once the submodule and runtime dependencies are available, ask the agent
「研究室を初期化して」 or 「inbox のこれで研究したい」. The `labo-layout`
skill creates the necessary structure and uses `research-management` to
develop the actual research plan. Initialization is also directly available
as `layout init`: it adds missing core directories, preserves existing files
and `AGENTS.md` content, and adds workspace ignore patterns. Unassigned root
`inbox/` contents are local staging; assigned research originals and reference
PDFs stay visible to Git. It creates no research programs or policy README
copies.

New items can be created from templates maintained in the layout skill:

```sh
python3 .agents/scripts/labo.py layout new research finite-observations \
  --title 'Finite observations and reconstruction' \
  --summary 'Determine which data can be recovered from finite observations.'
python3 .agents/scripts/labo.py layout new paper reconstruction
python3 .agents/scripts/labo.py layout new reference example-source
```

Creation commands accept `--dry-run` and refuse to overwrite existing items.
A research template needs its narrative filled from the actual input before
intake is complete. The tools leave inbox originals in place; the skill
handles their assignment and provenance. See the
[creation workflow](skills/labo-layout/references/creation.md) and
[directory contract](skills/labo-layout/references/layout.md) for details.

## Mathematical exploration and safe layout migration

[research-exploration](skills/research-exploration/SKILL.md) adds nested
categories, theorem/question nodes and compact progress trees to the standard
research layout. `layout new research` creates `plan.md`, `inbox/` and an empty
`exploration/tree.json`. When the agent accepts plan edits or exploration in an
existing program, [labo-layout](skills/labo-layout/references/research-migration.md)
adds missing structure as part of that work, preserves original material and
reuses existing nodes. Inventories, explanations, report-only reviews and checks
remain read-only. A missing tree is simply a structural absence; old plans and
claim statuses retain their meanings. The versioned tree identifies its format
without a second style field in `plan.md` or `claims.yaml`. Classification, work progress and mathematical
dependencies are separate. Read summaries first and selected detail files next:

```sh
python3 .agents/scripts/labo.py research exploration init --research finite-observations --if-missing
python3 .agents/scripts/labo.py research exploration add --research finite-observations \
  --node reconstruction --kind question --title 'Reconstruction question' \
  --summary 'Identify the hypotheses needed for reconstruction.' \
  --next 'Test a finite counterexample.' --proof-required
python3 .agents/scripts/labo.py research exploration tree --research finite-observations --depth 2
python3 .agents/scripts/labo.py research exploration show --research finite-observations --node reconstruction
python3 .agents/scripts/labo.py research exploration tree --research finite-observations --with-evidence
python3 .agents/scripts/labo.py research exploration check --research finite-observations
```

The lightweight tree reads metadata only and labels formal records unchecked.
`--with-evidence` and `check` additionally inspect linked evidence and input
freshness; counts describe scoped work, never a percentage of mathematics proved.
Mutations use native process locks, atomic JSON replacement and per-node
optimistic revisions; failed stale updates must be reread and reconciled.
Parallel workers have named nodes and separate records/modules; one integrator
owns the program story, shared Lean definitions and final integration.

The initializer safely reuses an existing tree, including concurrent work;
it neither duplicates nodes nor overwrites settings. Start with the current
scoped work rather than generating nodes from every historical claim. Create
`claims.yaml` when registering concrete claims. Sequential/parallel mode is an
execution choice, separate from layout adoption and task authorization.

For work recorded in the tree, every proof-bearing result needs Lean evidence before
its task can be `done`. Theorem/lemma nodes require it automatically; mark all
other mathematical conclusions, examples and counterexamples `--proof-required`.
Reuse `claims.yaml` as the theorem index, with exact source/declaration,
substantive kernel and mathematical-alignment reports, and directly covering
current formal reviews for the claim and its prerequisites. Existing evidence
formats and legacy research statuses retain their meanings. See
[Lean completion and placement](skills/research-exploration/references/lean.md).

Prefer small modules in projects grouped by their Lean environment. Current
fingerprints cover the whole mapped project's `.lean` sources: adding a module
can stale another result's review. Finish related edits before renewing reviews;
different change/reuse boundaries can justify separate projects. Stale done
tasks require rechecking. `current_records` describes input-matching assessment
records, not automatic mathematical certification. Existing selected-source
replay does not rebuild all prepared imports or support every local dependency;
unsupported execution stays pending. Explicit local-dependency tree snapshots
are required for completion records using path packages. No background scheduler
or automatic legacy formalization is introduced.

## Required research positioning

Before framing or substantially reframing a program, starting substantive
manuscript work or revising its contribution narrative, and presenting
novelty/comparative claims in an own-research talk, the skills require a
[research-positioning investigation](skills/reading-reference/references/research-positioning.md).
Refresh affected comparisons when the question, result, assumptions or method
changes, and search again before submission. Routine bookkeeping and typo-only
edits do not restart the survey; report-only reviews do not authorize file edits.

The investigation searches alternative terminology and adjacent work, follows
citations in both directions, and compares inspected primary passages with the
actual research claim. Reuse one program-level memo of searches, source versions,
inherited and new ingredients, open leads, and notation/convention decisions.
The [memo template](skills/reading-reference/assets/research-positioning.md) lives
in this checkout; populated private records stay with the research program,
normally at `research/<slug>/literature-positioning.md`, or in an adequate
existing record. Carry the findings and precise citations into the paper itself.
No search certifies all prior work or proves novelty from an absence of hits.
This is a skill workflow, not a new CLI gate, mandatory claim catalog or copied
host policy.

Writing and in-scope reviews also use a
[corpus-backed terminology audit](skills/reading-reference/references/terminology-audit.md):
compare actual object types, roles and conventions with inspected definitions
and formulas, preserving legitimate alternatives and recording source gaps.
Corpus style cues remain soft; semantic verification checks the mathematics.

For an introduction's central question, concrete significance and narrative
order, use [paper-introduction](skills/paper-introduction/SKILL.md) alongside
`paper-writing`. It shapes the story from the actual results and positioning
evidence, without forcing a novelty claim or fixed paragraph formula.

For whole-paper design or structural reassessment, use
[paper-structure](skills/paper-structure/SKILL.md). It maps current material to
proposed sections with purpose, inputs, outputs and proof/reader routes.
[knowledge-dependencies](skills/knowledge-dependencies/SKILL.md) manages an
optional sourced graph of definitions, assumptions and results, distinguishing
hard prerequisites from narrative references. Its checked-out Python harness
sorts declared dependencies, diagnoses actual cycles separately from downstream
blocked nodes, checks full proposed orders, and computes prerequisite closure
or change impact:

```sh
python3 .agents/scripts/labo.py dependencies sort --graph research/example/dependencies.yaml
python3 .agents/scripts/labo.py dependencies closure --graph research/example/dependencies.yaml --node conclusion
python3 .agents/scripts/labo.py dependencies impact --graph research/example/dependencies.yaml --node uniform
```

The [graph contract](skills/knowledge-dependencies/references/graph.md) defines
the schema and all five commands. Checks cover every **declared** hard edge;
complete extraction and mathematical validity require source review. A proof
schedule and a paper's reader order can differ through clear early statements
and later proofs. Ordinary manuscripts need no dependency-graph migration.

## Optional evidence and review records

For results that need durable handoff or reuse, `research-management` owns an
optional [evidence protocol](skills/research-management/references/evidence.md).
Stable claim IDs connect exact statements to proof notes, inspected literature,
claim dependencies, and optional Lean scope mappings. This supplements the
research story; it does not add program statuses or require a workspace migration.

```sh
python3 .agents/scripts/labo.py evidence init \
  --catalog research/finite-observations/claims.yaml
python3 .agents/scripts/labo.py evidence check \
  --catalog research/finite-observations/claims.yaml
python3 .agents/scripts/labo.py evidence snapshot --kind writing \
  --tree writing/reconstruction
```

Initialization requires an existing parent directory and refuses replacement.
`snapshot` prints a pending YAML record without writing files or approving a
claim. A saved review binds the actual input bytes (including uncommitted
changes), selected dependencies, and the relevant policy files in this checkout.
After a real review, record its author, date, verdict, and hashed report as
described in the protocol. Keep that record outside any tree it snapshots.

```sh
python3 .agents/scripts/labo.py evidence check \
  --record research/finite-observations/reviews/writing.yaml --strict
```

Checks distinguish current, pending, stale, failed, and malformed records.
Pending or stale records are warnings unless `--strict` is used. These are
structural and freshness checks, not mathematical certification, automatic
Lean execution, or permission to renew a passing review. Ordinary research,
writing, and `research check` do not require these files.

### Scope diagnostics and program inventory

Before deciding that a writing review covers a manuscript, inspect literal TeX
dependencies and compare them with the intended selection:

```sh
python3 .agents/scripts/labo.py evidence scope --paper reconstruction \
  --record research/finite-observations/reviews/writing.yaml --format json
python3 .agents/scripts/labo.py evidence status --research finite-observations
```

[`evidence scope`](skills/research-management/references/evidence-scope.md) follows
supported literal includes, graphics, bibliography files, and local classes or
packages. It reports missing, omitted, ambiguous, and unresolved inputs instead
of silently adding them to a review. Dynamic TeX and external package resolution
remain explicit limitations. Without `--record`, `--file`, or `--tree`, it only
discovers dependencies and makes no coverage claim.
The default diagnostic compilation-root candidate is the source's parent. Use
`--compile-root .` for workspace-root builds such as `output build --source`,
or name another actual workspace-relative working directory explicitly.

[`evidence status`](skills/research-management/references/evidence-status.md)
reads one selected program's optional catalog and reviews, showing recorded
claim statuses separately from current/stale/pending/failed review coverage.
Writing reviews do not grant proof coverage; dependencies do not inherit a
review merely because their fingerprints were included. Historical/conflicting
records remain visible. Use repeatable `--record` instead of default discovery
for a narrow active-record check. Both commands are read-only, support JSON and
`--strict`, and never migrate a program without an adopted catalog.

### Explicit Lean replay

Inspect a read-only execution plan for one exact formal mapping:

```sh
python3 .agents/scripts/labo.py evidence replay \
  --catalog research/finite-observations/claims.yaml --claim finite-cover
```

Only an explicit `--execute` invokes a prepared, pinned native Lean toolchain.
[`evidence replay`](skills/research-management/references/formal-replay.md)
builds the selected source into a fresh temporary artifact, then observes the
mapped declaration's type, printed definition, and transitive axioms. It records
actual commands, output and before/after input hashes, and fails on `sorryAx`.
Other axioms remain visible for trust review. Use `--format json` for the full
auditable report; text output omits the potentially large file-hash maps.

This is not a full Lake rebuild or independent proof checker. Prepared imports
are fingerprinted, not rebuilt; the supported conventional layout and exact
version requirements are deliberately narrow. Missing prerequisites remain
unavailable: no Lake, elan, installer, cache download or dependency fetch is
launched. **Lean code can execute arbitrary code during compilation**, so execute
only trusted projects/dependencies or use an external sandbox. The runner itself
is not network/filesystem isolation. A completed replay never updates a claim,
approves a review, or establishes informal-to-formal alignment.

### Staged first-reader records

When staged reading is explicitly requested, the coordinator can use
[`paper reading`](skills/paper-referee/references/staged-reading.md):

```sh
python3 .agents/scripts/labo.py paper reading start \
  --source writing/reconstruction/sections/01-introduction.tex \
  --session research/finite-observations/reviews/reader-one.json --reader reader-one
python3 .agents/scripts/labo.py paper reading next \
  --session research/finite-observations/reviews/reader-one.json --through-line 8
python3 .agents/scripts/labo.py paper reading observe \
  --session research/finite-observations/reviews/reader-one.json \
  --understanding 'The visible text asks ...' --confusion 'The first missing relation is ...'
```

The private session's parent must already exist. Each exposure returns only the
cumulative prefix; initial understanding and first confusion must be recorded
before another exposure. `observe --rescue` appends later recovery without
rewriting that initial record. Changed source bytes/identity invalidate the
session. `status` shows progress without future text or the observation prose.
For independent reading, a coordinator must actually supply a fresh reader only
the neutral brief and exposed prefix; `--mode independent` alone proves nothing.
This is staged output, not a filesystem sandbox, signed log, or review approval.

## Inspect and build

`research list` reads *only the YAML frontmatter* of `research/*/plan.md`.
It never reads the body, inbox, Lean sources, or manuscripts. The only statuses
are `in_progress` and `completed`. A temporarily untouched project is still
`in_progress`; restructuring is expressed in Git history and the prose plan.

`paper map` reads the assembly file `main.tex` to select the literal
`\input{sections/NN-name}` / `\include{sections/NN-name}` entries in manuscript
order, then reads only their openings, delimited by `% LABO:INTRO-END`.
It does not expand TeX macros or support dynamic/conditional inclusion.
`paper section` reads one selected section, never the entire paper.
No mathematical assertion is certified by this tooling.

`output build` delegates to `latexmk`, writing intermediate files to
`writing/<paper>/.temp` and PDF/SyncTeX outputs directly to `output/`, named
`<paper>.pdf` and `<paper>.synctex.gz` so all projects can be selected together.
The project slug names the output pair; roots in the same project overwrite
the same pair. Named sources keep separate intermediate cache names.
`--dry-run` prints the invocation.
Real compilation requires a TeX distribution with `latexmk`. Success requires
both PDF and SyncTeX; a missing SyncTeX
after an otherwise cached build triggers at most one forced rebuild.
Successful builds prune the oldest known PDF/SyncTeX groups toward a default
limit of 30 output files. The viewer stays closed unless `--open` is supplied.
The command warns if protected or unrecognized files keep the count above the
limit. Use `--max-files` to change it or `output prune --max-files 30` to clean
without compiling. A retained workspace-level lock serializes concurrent builds
and cleanup through native POSIX or Windows locking.

For existing document names, use `output build --source` with a TeX root under
`writing/<slug>/` or `reading/<slug>/`. Its output pair is named by the project
slug, so multiple roots under that slug overwrite one another. The source stays
in place and its cache stays in `.temp/`. Engine directives and packages such
as `xeCJK` are detected; `--engine` can override them. The
[build contract](skills/labo-build/references/build-contract.md) describes
working-directory behavior.

## Quality checks

From this policy checkout, with the runtime dependency available:

```sh
python3 -m unittest discover -s tests -v
```

Tests include actual temporary Git submodules mounted at `.agents`, `.claude`,
and a neutral path, with source-local execution from unrelated working
directories and without installing this project. Evidence tests also check
that changed policy bytes invalidate a review without host-side policy copies.
The [CI workflow](.github/workflows/ci.yml) runs the full suite natively on Linux
and Windows with Python 3.11 and 3.13, including cross-process output locking and
all three submodule mounts. A separate Linux job explicitly prepares official
Lean 4.19.0 from a fixed URL with a pinned SHA-256, then requires the real smoke
test: ordinary theorem, transitive `sorryAx`, and custom axiom. This dependency
preparation is a CI step, not an implicit feature of the replay runner.

Positioning route checks ensure that the owning skills share one local protocol
and that its memo template can be copied without broken checkout-relative links.
The [forward-use packets](tests/fixtures/reading-reference/research-positioning.md)
provide small drafting, local-edit, comparison and refresh tasks for fresh agents;
they are not run by the unit suite. Neither link checks nor a successful agent
run certify exhaustive literature coverage or mathematical novelty.

To require the same real smoke with an already prepared local toolchain, set
`LABO_REPLAY_TOOLCHAIN_DIR` to its directory and `LABO_REQUIRE_REAL_LEAN=1` when
running `test_formal_replay.py`. Without a selected toolchain that test truthfully
skips; requiring it turns missing preparation into failure. Mocked tests and the
Linux real-Lean job do not establish real Windows Lean execution or TeX visual
correctness.

Tests and fixtures contain no private research. Workspace mutations are scoped
to the selected private workspace; explicit Lean execution also uses a temporary
build directory and can have the trusted code's own side effects. The CLI
performs no GitHub mutations by itself. `pyproject.toml` remains available for
development or optional packaging, not as the submodule deployment mechanism.

## Scope

The tools implement workspace initialization, item creation, research inventory,
optional sourced mathematical dependency checks/order/closure/impact,
optional evidence snapshots/scope/status/replay, scoped and staged TeX reading,
TeX builds, and output cleanup. Skills define review,
research lifecycle, directory layout, self-improvement, PR, slides, and web
publishing workflows. A public PR is a
deliberate choice, using the available Git/GitHub tools or a direct human push;
no particular connector or branch naming scheme is required.
