# The step ledger

`steps.json` is the single source for the page, the dependency check and the review assignments.
Change it first, then rebuild downstream. Fields of each step:

| field | meaning |
|---|---|
| `id`, `title`, `statement` | short id, a title, one or two lines of what is claimed |
| `hyps` | the standing assumptions the step uses (names only) |
| `deps` | ids of steps it uses; the graph must be acyclic |
| `loc` | where it is in the source (file and label, or theorem number and page) |
| `origin` | `inherited` (from prior work), `standard`, `adapted` (a known method, changed), `new` (as the source claims) |
| `tier` | `key`, `semi`, `standard` |
| `why_tier` | one or two sentences; required for `key` |
| `role` | what the step does for the theorem |
| `seeds` | where a reviewer should push hardest (not shown on the page) |
| `outside` | `true` for a side remark the theorem does not depend on |

`_meta.target` names the step that is the theorem itself (default `T`).

## What is key

A step is **key** when removing it breaks the theorem **and** the source claims it as new, so the
literature does not already supply it. If only the first holds it is **semi-key** (necessary, but a
combination of known methods, or a detail specific to this setting); if neither, **standard**.
Origin is the source's own attribution until the prior-work stage checks it against primary
sources; classes are provisional until then.

For someone else's paper, take the novelty claim from the paper's own text (its introduction and
its remarks on prior work). If the paper makes no claim, say so and treat the decisive steps as
semi-key.

## Granularity

Split by the idea a step carries, not by lemma numbers: a device used in two lemmas is one step,
and a lemma that contains two ideas (for example a case split) can become two. A good ledger has a
handful of key steps; if most steps are key, the criterion is being applied to "needed" alone.

## Source of truth

Before reading, find which version is current: compare modification times of the manuscript, the
plan, earlier reading notes and PDFs. Older notes may describe a superseded proof; use them only
as pointers.

`check_ledger.py` reports schema errors, cycles, steps the theorem does not depend on, the
topological order, and for each key step which steps fail if it fails.
