---
name: knowledge-dependencies
description: Build and audit sourced dependencies among mathematical definitions, assumptions and results with a Python harness for deterministic topological order, cycles, proposed orders, prerequisites and change impact; use for explicit dependency management, not proof certification.
---

# Mathematical knowledge dependencies

Before substantive work, follow [eligibility and handoff](../research-router/references/editing-capability.md).
For each request, follow the [required consultation](../research-router/references/consultation.md).

Use an explicit graph when the user wants dependency management or when it
materially clarifies the requested proof or paper structure. Keep adopted
private graphs with the research or manuscript, usually as
`research/<slug>/dependencies.yaml`; an existing adequate path is fine. Ordinary
research and writing need no graph migration. The shared schema, executable
checks and synthetic fixture live in this checkout.

Read [the schema and CLI contract](references/graph.md) before creating or
editing a graph. Use the [synthetic graph](assets/example.yaml) with its
[source note](assets/example-source.md) to see edge direction and coverage;
these are examples, not evidence for a user's research.

## Extract and inspect the declared dependencies

Start from the selected theorem, proof, notes or manuscript. Read exact
statements and decisive applications. Give independently useful definitions,
assumptions, constructions and results stable IDs, exact scoped statements,
and source paths with precise locators. An external ingredient points to a
local source record identifying the inspected primary version and passage.

For each use, check the current objects against the required hypotheses and
quantifiers. Record `A.requires: [B]` when establishing or defining A uses B.
Use `references` for narrative previews, motivation or comparisons that impose
no proof prerequisite. Hypotheses needed by a lemma belong in its inputs;
do not hide them under the final theorem. Distinguish alternative proofs or
conditional branches in the selected graph's scope instead of merging them
into a false cycle or an unconditional claim. An unproved auxiliary result
can be recorded with its unresolved status in the statement/source; graph
ordering does not upgrade its mathematical status.

Record the inspected scope and extraction gaps in `coverage.note`. Use
`source-reviewed` only after reviewing extraction against that stated scope;
it remains a supplied assessment. Revisit the affected statements and edges
after changes. Do not claim complete mathematical dependency extraction from
an acyclic graph or from a tool's successful exit.

## Run the checked-out harness

Resolve `<labo-script>` to the absolute `../../scripts/labo.py` path from this
skill's **real directory**, following symlinks. This uses the implementation
beside the loaded skills under `.agents`, `.claude`, or another mount. It does
not rely on a globally installed command or the invocation directory.
For a standalone checkout or explicit selection, append
`--workspace /absolute/path/to/labo` to the leaf command.

```sh
python3 <labo-script> dependencies check --graph research/example/dependencies.yaml
python3 <labo-script> dependencies sort --graph research/example/dependencies.yaml --format json
python3 <labo-script> dependencies order --graph research/example/dependencies.yaml \
  --node ambient --node uniform --node estimate --node conclusion
python3 <labo-script> dependencies closure --graph research/example/dependencies.yaml --node conclusion
python3 <labo-script> dependencies impact --graph research/example/dependencies.yaml --node uniform
```

`order` checks a proposed **full graph order**, including each ID once. `closure`
includes selected targets and all hard prerequisites; `impact` includes changed
nodes and all hard dependents to reinspect. Repeat `--node` for multiple targets.
These operations never edit the graph, manuscript or review records.

The harness validates the schema and every declared edge, checks source-file
existence, and records current source hashes. It produces a deterministic
topological order, or a partial order with actual cycle witnesses and separate
downstream blocked nodes. Diagnose a cycle at the source: it can expose a
circular proof, incorrect edge classification or mixed proof alternatives.
Do not delete genuine prerequisites merely to obtain a successful sort.

Report the scope, recorded coverage, ordering or violations, and unresolved
source checks. A topological order is a dependency-safe schedule for the
**declared hard edges**. Completeness of extraction, accurate locators,
mathematical truth and valid theorem applications require human/agent source
review. Current source hashes identify inputs; they do not renew prior reviews.
For whole-paper reader order, use [paper-structure](../paper-structure/SKILL.md):
an early announcement with a clear later proof route can be appropriate.
