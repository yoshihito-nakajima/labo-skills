# Sourced dependency graph and CLI contract

## Schema version 1

The YAML root has exactly `schema_version`, `scope`, `coverage`, and `nodes`.
Unknown fields and duplicate mapping keys are errors. Empty graphs are allowed
for an explicitly empty or not-yet-extracted scope; they prove no coverage.

```yaml
schema_version: 1
scope: The selected proof route for Theorem 3, including its definitions.
coverage:
  status: partial
  note: Main proof inspected; external compactness input still needs source review.
nodes:
  - id: ambient
    kind: definition
    statement: State the exact ambient objects and conventions.
    source:
      path: research/example/proof.md
      locator: 'Definition 1, paragraphs 1–2'
    requires: []
  - id: conclusion
    kind: theorem
    statement: State the exact hypotheses, quantifiers and conclusion.
    source:
      path: research/example/proof.md
      locator: 'Theorem 3 and its proof'
    requires: [ambient]
    references: []
```

`scope`, `coverage.note`, every `statement`, and each source `locator` are
nonempty strings. `coverage.status` is `partial` or `source-reviewed`, a
**supplied assessment**, not a computed verdict. Describe the reviewed source
versions, scope and remaining omissions in the note; source-reviewed coverage
can be limited to a selected proof rather than an entire manuscript.

Each node requires `id`, `kind`, `statement`, `source`, and `requires`;
`references` is optional and defaults to `[]`. IDs use lowercase kebab-case,
start with a letter, are unique and survive reordering. Kinds are `definition`,
`assumption`, `construction`, `lemma`, `theorem`, or `external`. These are
descriptive kinds; none assigns a proof status. State conditional or unresolved
ingredients accurately in the source and statement.

`A.requires: [B]` means **A requires B**, so a valid topological order places
B before A. `references` names nonbinding narrative links. Both lists must
contain unique existing IDs; self edges and edges present in both lists are
errors. Narrative references can form cycles and impose no order. A hard cycle
is diagnosed with a nonzero exit, rather than accepted as a proof schedule.
One graph represents one explicitly scoped choice of proof route and hypotheses;
the schema does not encode disjunctions between alternative proofs.

`source` has exactly `path` and `locator`. Paths, including `--graph`, are
normalized workspace-relative POSIX paths to existing ordinary files. Parent
traversal, absolute/Windows drive paths, symlinks and paths into the loaded
policy checkout are rejected. Store a local note identifying a remote paper's
exact version and locator, rather than putting a URL in `path`. The harness
does not fetch sources, interpret locators, parse proofs or follow note links.
The existing shared loader limits graph YAML to 2 MiB.

## Commands and results

All commands use `python3 <labo-script> dependencies <action> --graph <path>`
and accept `--format text|json` and a leaf-level `--workspace`. JSON results
include the graph SHA-256, current source SHA-256 values, recorded coverage,
counts, and the common analysis below. Hashes identify current files without
claiming prior review, source consistency over concurrent edits, or freshness
against an earlier graph version.

| Action | Extra arguments | Result |
| --- | --- | --- |
| `check` | none | Validate schema, source paths and declared graph; diagnose cycles. |
| `sort` | none | The same complete analysis, presenting its deterministic order. |
| `order` | repeat `--node ID` in proposed order | Validate a full permutation and every hard prerequisite's position. |
| `closure` | repeat `--node ID` for targets | Targets plus transitive hard prerequisites, with selected topological order. |
| `impact` | repeat `--node ID` for changed nodes | Changed nodes plus transitive hard dependents to reinspect. |

Every invocation audits the whole declared graph. Global cycles produce an
error status even if a closure or impact query selects an unaffected region.
Reachability results remain available for diagnosis; the two completeness
flags distinguish a partial global order from a complete selected order.
No operation writes files or marks mathematical claims/reviews as checked.

- `topological_order`: prerequisite-first order, choosing the lexicographically
  smallest available ID at each step; independent of node/edge YAML order.
- `order_complete`: whether that order includes every node.
- `cyclic_components`: sorted strongly connected hard-dependency components.
- `cycle_witnesses`: one actual closed edge path per component, in **requires**
  direction. A component may contain more cyclic nodes than its witness path.
- `cyclic_nodes`: all nodes in cyclic components, including ones outside the
  chosen witnesses.
- `blocked_nodes`: unresolved downstream nodes outside those components.
  They depend on a cycle without belonging to any cycle themselves.
- `order_check`: for `order`, a `valid` flag plus `missing`, `unknown`,
  `duplicates`, and prerequisite-position `violations`.
- `selected`, `included`, `selection_order`, `selection_order_complete`: for
  closure/impact; `included` contains the seeds themselves, sorted by ID.
  `selection_order` filters the global order and can be partial.

Exit **0** means the declared graph/order passed the requested structural
checks, **1** means a detected hard cycle or invalid proposed order, and **2**
means malformed input, missing source, invalid selection, or workspace/path
error. Malformed-input diagnostics go to stderr, including with JSON selected.
No exit code establishes source-extraction completeness or mathematical truth.

For the bundled synthetic fixture, copy `assets/example.yaml` and
`assets/example-source.md` together into an existing private directory and
replace its source paths with that directory's workspace-relative source path.
Expected sort: `ambient, uniform, estimate, conclusion`; the narrative link
from `ambient` to `conclusion` has no effect. `closure --node estimate` excludes
`conclusion`; `impact --node uniform` includes `uniform, estimate, conclusion`.
