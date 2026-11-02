# Format and commands

`research/<slug>/exploration/tree.json` is the sole metadata authority.
`exploration/.lock` is a retained native process-lock file; retain its inode
while a process may write. `layout new research` uses the same initializer as
`research exploration init`; existing programs follow
[labo-layout migration](../../labo-layout/references/research-migration.md)
during accepted plan edits or exploration. Reading a program without a tree
with `tree` / `check` returns `adoption: not_enabled` without writes. This is a
structural absence, not a failure or proof judgment. Ordinary `research list` /
`research check` retain their existing scope.

`init --if-missing` validates and returns an existing tree under the native lock,
preserving its bytes, revision, nodes and settings. Its settings arguments apply
only to a new tree; use `configure` to change an existing tree. An invalid tree
is reported and retained. Plain `init` still refuses an existing target.

Schema version 1 has exactly these top-level fields:

```json
{
  "schema_version": 1,
  "revision": 0,
  "settings": {"mode": "sequential", "integrator": "primary", "max_workers": 2},
  "nodes": []
}
```

Every node stores exactly these fields, including nulls and empty arrays:

```json
{
  "id": "uniform-bound", "parent": "compactness", "kind": "theorem",
  "title": "Uniform bound candidate",
  "summary": "Pointwise control is known; uniformity remains open.",
  "next": "Test the family without compactness.",
  "state": "queued", "owner": null, "proof_required": true,
  "record": "research/example/notes/uniform-bound.md",
  "claim_refs": ["research/example/claims.yaml#uniform-bound"],
  "dependency_refs": ["research/example/dependencies.yaml#uniform-bound"],
  "revision": 1
}
```

IDs use lowercase kebab-case. Null parent means root. Kinds: `category`,
`question`, `definition`, `conjecture`, `theorem`, `lemma`, `example`, `task`.
Theorem is an object kind, independent of its evidence. Title, summary and next
are nonempty single-line text; owner is a name or null. References use normalized
workspace-relative forward-slash paths, optionally `#ID` for catalog/graph links.
Records are optional text files; long reasoning belongs outside this JSON.

`proof_required` is a boolean, automatically true and mandatory for theorem /
lemma kinds. Use `--proof-required` for any other node establishing a mathematical
conclusion, including examples, counterexamples and independent helper results.
`--no-proof-required` is for purely organizational work, never a way to bypass
the all-proof policy. See [Lean completion](lean.md).

`tree` sorts siblings by ID and reads only metadata. `--node ID` selects a
subtree; `--depth N` limits visible edge depth from zero. Counts cover every
depth in the selected subtree; `visible` / `total` expose hidden nodes. JSON
nodes form a flat preorder list with relative `depth` and full metadata.

`proof_targets` and `guarantee_counts` also cover the whole selected subtree,
including hidden nodes. Evidence-enabled trees check that same entire subtree;
depth limits reduce output, not freshness inspection. `current_records` counts
exclude stale targets even if their work state remains done.

By default `tree` labels proof targets `not_checked`: it makes no freshness
claim. `tree --with-evidence` and `show --with-evidence` inspect referenced
catalogs, review records and their input hashes. `check` always performs that
inspection and reports a done proof task whose evidence became stale as an
error. An empty tree has no proof targets, not universal proof coverage.
`guarantee.state=current_records` means required recorded formal assessments
match their current inputs, not that Python certified the mathematics.

`show --node ID` reads metadata; `--details` reads that node's UTF-8 record up
to 1 MiB. Read larger/binary sources separately. `check` validates schema, IDs,
parents, acyclicity, modes, ownership, active-owner bounds and referenced file
existence. Its formal completion gate reuses the owning evidence checker for
exact claim IDs, claim closure and direct formal-review freshness. Mathematical
correctness remains a substantive assessment. Symlink traversal is unsupported. Hostile concurrent
filesystem replacement is outside this trusted-workspace workflow's guarantees.

The following follow `python3 <labo-script> research exploration`. All accept
`--workspace PATH` and `--format text|json` after the leaf command:

```sh
add --research example --node compactness --kind category \
  --title 'Compactness route' --summary 'Explore what compactness controls.' \
  --next 'Separate pointwise and uniform estimates.'
add --research example --node uniform-bound --parent compactness --kind theorem \
  --title 'Uniform bound candidate' --summary 'Uniformity remains open.' \
  --next 'Try a noncompact family.' --record research/example/notes/uniform-bound.md
update --research example --node uniform-bound --expect-revision 1 \
  --state blocked --summary 'The noncompact example diverges.' \
  --next 'Check which compactness hypothesis blocks the example.'
```

`update` requires a fresh **node** revision and replaces only supplied fields.
Stale revisions fail before writing. Read and reconcile changes before retrying;
unrelated nodes have separate revisions. `--claim-ref` / `--dependency-ref`
replace entire arrays; repeat flags for several links, use `-` alone to clear.
`--parent -`, `--record -` and (sequential mode) `--owner -` clear nullable fields.
IDs are immutable; preserve history and park retired work. No delete command.

`configure --research example --actor primary --expect-revision T ...` uses
the **tree** revision to change settings. `--mode parallel` requires owners on
all nodes; assign them first. Sequential mode retains nodes and owners and
suspends parallel ownership checks. Only the current integrator changes settings.

Mutations lock, validate, fsync a temporary file and atomically replace the JSON.
Readers see a complete old or new document; failed mutations preserve the old
tree. Hand edits and shared record edits bypass these safeguards. Actor names
are coordination labels, not authenticated permissions. Network/distributed
locking and power-loss durability of the directory rename are outside the
guarantees; use local storage and Git for durable history.
