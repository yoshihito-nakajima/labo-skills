# Evidence status for one research program

This optional inventory brings recorded claim status and review-input freshness
into one view. It does not replace the developing research story, execute Lean,
inspect proof validity, or change a claim. Read the [evidence protocol](evidence.md)
for the catalog and record formats; this reference owns only their bounded
inventory workflow.

Resolve `<labo-script>` from the real owning skill directory. For one program:

```sh
python3 <labo-script> evidence status --research example
python3 <labo-script> evidence status --research example --format json
```

The default inputs are `research/example/claims.yaml` and YAML review records
below `research/example/reviews/`. An existing program without either remains
`not-adopted`: nothing is created, migrated, or made mandatory. An empty inventory
is not a claim that the research is complete, reviewed, or free of open questions.
The existing `research list` and `research check` remain frontmatter-only tools.

## Select the intended records

For an existing nonstandard layout, name a catalog or review directory **inside
the selected research program**:

```sh
python3 <labo-script> evidence status --research example \
  --catalog research/example/evidence/claims.yaml \
  --reviews research/example/evidence/reviews
```

Alternatively, repeat `--record` to select exactly the records needed for the
current decision. This replaces directory discovery; it is not an additive filter:

```sh
python3 <labo-script> evidence status --research example \
  --record research/example/reviews/current-proof.yaml --strict --format json
```

Explicit records may live elsewhere in the private workspace, but cannot be
combined with `--reviews`. A record naming another catalog is shown as
`out-of-scope`; that other catalog and its research inputs are not inspected.
Use a separate request for another program. There is no workspace-wide scan.

Directory discovery reads only `.yaml`/`.yml` files, skips the protocol's cache
directories, rejects symlink traversal, and is bounded to 500 records and 32
nested directory levels. It does not interpret arbitrary Markdown reports as
records. A selected record's proof/formal inputs are read only as required by
the existing freshness checker. Missing explicitly requested paths are errors,
not evidence that the program has not adopted the protocol.

## Read the result without promoting it

The text summary and versioned JSON distinguish:

- The claim's **recorded** evidence status, statement, direct dependencies, and
  structural validity. These labels are assertions in the catalog, not new
  verification performed by the inventory.
- Each selected record's `current`, `stale`, `pending`, `failed`, `invalid`, or
  `out-of-scope` state. The underlying checker still owns freshness semantics.
- Direct current reviews by kind. A current `writing` review is not proof
  coverage. A current `proof`, `formal`, or `owner` record counts as direct
  substantive-review coverage only for claims it explicitly names; dependencies
  included in its fingerprint do not inherit approval or direct coverage.
- Open/unverified/disputed/refuted claims, missing current substantive reviews,
  and kernel/alignment verdicts needing attention. A kernel `pass` alone does
  not establish informal alignment or `verified-formally` status.

All selected historical and conflicting records remain visible. A newer date
does not erase a failed review or automatically supersede an older snapshot.
Consequently, an all-history inventory can remain warning/error after a later
review passes. Select the active records explicitly for a narrow decision;
retain earlier evidence rather than deleting it to obtain a green summary.

`ok` means only that this selected structural inventory produced no diagnostic
issues. Ordinary unresolved exploration remains visible without becoming an
automatic failure. A claim recorded as proved without a directly selected
current substantive review generates a warning. Stale/pending records also
warn; malformed/failed records are errors. Errors exit 1, warnings exit 0 unless
`--strict` requests exit 1, and invalid command selections exit 2. No outcome
grants mathematical, owner, independence, or publication approval.

This command writes no files, changes no statuses, refreshes no hashes, saves
no reports, and executes no proof tools. Use it to choose the smallest actual
next review, not to substitute bookkeeping for that review.
