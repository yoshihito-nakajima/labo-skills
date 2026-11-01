# Scoped evidence and review records

- [Authority and scope](#authority-and-scope)
- [Claim catalog](#claim-catalog)
- [Lean alignment](#lean-alignment)
- [Snapshot a review's actual inputs](#snapshot-a-reviews-actual-inputs)
- [Check the selected records](#check-the-selected-records)
- [Supporting opt-in workflows](#supporting-opt-in-workflows)
- [Design provenance](#design-provenance)

## Authority and scope

Use this optional protocol when a durable result will be reused, a proof's
support is easy to confuse, or a review must survive a handoff. Ordinary
exploration and `research check` do not require a catalog. Keep the research
story in `plan.md`; its statuses remain `in_progress` and `completed`.

The loaded policy checkout owns this protocol, its templates, and the executable
checks. Resolve `../../scripts/labo.py` from the real `research-management`
skill directory. The checkout may be mounted at `.agents`, `.claude`, or another
user-selected location. Do not copy the protocol, parser, or schema into the
research workspace or rely on an installed `labo` executable.

Private claims, proof notes, confirmations, and review reports remain research
artifacts in the host workspace. They follow the format defined here; they do
not define a second implementation of the harness. Do not import private
research into the public policy checkout.

## Claim catalog

For a program that needs it, create a catalog with:

```sh
python3 <labo-script> evidence init --catalog research/example/claims.yaml
```

`--dry-run` previews creation. The command copies the empty template maintained
by this skill, requires an existing parent directory, refuses replacement, and
never creates a research program. The
catalog path is explicit: existing projects need no renaming or migration.

The YAML shape is:

```yaml
schema_version: 1
claims:
  finite-cover:
    statement: >-
      State the exact objects, hypotheses, quantifier dependencies, conventions,
      and conclusion here. This example is not a mathematical assertion.
    status: unverified
    evidence: [research/example/finite-cover.md]
    dependencies: []
```

Use stable, descriptive lowercase kebab-case IDs. Never renumber IDs after
reordering a catalog or reuse an ID for a different claim. Keep only independently
useful or load-bearing statements; internal proof steps belong in the evidence
note. Dependencies name IDs in this catalog. This is an optional claim-level
graph, not a mandatory graph of research programs. External ingredients need
an exact statement, source version, and locator in the linked evidence note;
list the actual source files as evidence when their bytes must be tracked.

Every path is a normalized, workspace-relative POSIX path, independent of the
shell's working directory. Inputs must be ordinary files inside the workspace;
symlinked paths and paths into the policy checkout are rejected. A catalog's
evidence list contains local files, not unchecked URLs. A local source record
can identify an external URL and the exact inspected version. The checker does
not fetch external sources or traverse links inside Markdown or TeX.

Evidence statuses are separate from program lifecycle:

| Status | Required interpretation |
| --- | --- |
| `open` | A proposed mathematical question remains unresolved |
| `unverified` | An argument or inherited assertion has not been checked |
| `proved/agent` | An agent checked an argument at the exact stated scope |
| `proved/literature` | An inspected source supports the exact claim and assumptions |
| `proved/owner-checked` | The owner explicitly checked this statement and proof |
| `verified-formally` | Both the kernel/trust and informal-alignment checks passed |
| `verified-computationally` | Only the stated finite computation was checked |
| `disputed` | A concrete unresolved objection remains |
| `refuted` | A checked counterexample refutes the exact statement |

Checked or refuted claims require evidence files. A proved claim cannot rely
on an open, disputed, refuted, or merely computed dependency as an established
lemma. Exact finite verification can support a theorem only after its complete
mathematical justification is recorded. Optional `obstruction` and `next_check`
fields hold short prose; they never upgrade evidence. For owner-checked claims,
`owner_check` must name a local record of the actual scoped confirmation. Praise,
permission to edit, and another agent's verdict are not owner confirmation.

## Lean alignment

Reuse existing `COVERAGE.md`, axiom audits, and verification logs. A claim may
carry a `formal` mapping:

```yaml
formal:
  project: lean/example
  source: lean/example/Example.lean
  declaration: Example.finite_cover
  kernel:
    verdict: pass
    report: lean/example/verification.txt
  alignment:
    verdict: pending
    report: research/example/formal-alignment.md
```

Each verdict is `pending`, `pass`, or `fail`. A pending report may be null.
`verified-formally` requires both verdicts to be `pass` with existing reports,
an exact `lean-toolchain`, a Lake file, and `lake-manifest.json`. Record an empty
pinned Lake manifest for a project with no dependencies. The source must be
inside the named project. All project `.lean` files and pinned environment files
enter its fingerprint, except generated/cache directories. The explicitly
selected source and reports are always hashed, even beneath an otherwise
excluded directory. Add any other relevant excluded inputs explicitly; this
inventory does not replace a Lean dependency or trust audit.

The kernel report records the production declaration, build and replay
commands, placeholder audit, `#print axioms`, dependency revisions, and trust
boundary. The alignment report compares the actual objects, hypotheses,
quantifier order, conventions, and conclusion against this exact claim. Identify
abstract results still lacking their concrete application and any unformalized
direction. Use the [alignment outline](../assets/formal-alignment.md) only when
a new report is needed; do not duplicate an adequate existing coverage record.

`evidence check` verifies record shape, file existence, and freshness. It does not
run Lean, parse theorem semantics, validate log truthfulness, or grant formal
verification. For explicitly authorized execution, use the separately documented
[selected-source replay](formal-replay.md); it plans by default and still does
not establish informal alignment. Never infer a completed proof from a structural
check or promote a claim merely because a replay completed.

## Snapshot a review's actual inputs

Before the authorized review, capture exactly what will be read:

```sh
python3 <labo-script> evidence snapshot --kind proof \
  --catalog research/example/claims.yaml --claim finite-cover
python3 <labo-script> evidence snapshot --kind writing \
  --tree writing/example --file reference/example/reference.md
```

The command prints YAML and writes nothing. Preserve that snapshot with the
actual review report after the review. It always starts at `verdict: pending`,
with no reviewer, date, or report. There is no command that approves a record,
promotes a claim, or refreshes an old passing record.

Repeat `--claim`, `--file`, or `--tree` for the authorized scope. `proof`,
`formal`, and `owner` reviews require named claims; `writing` can cover files
without a catalog. `formal` requires a formal mapping for each selected claim.
A claim snapshot includes its exact statement, status, direct inputs, and all
transitive dependencies within the selected catalog. It records current bytes,
including uncommitted edits, not just the repository's last commit.

`--tree` inventories all ordinary files below the selected directory except
`.git`, `.lake`, `.temp`, `.venv`, `.uv-cache`, `__pycache__`, `build`, `dist`,
and `output` directories. File additions and removals invalidate the snapshot.
Keep review reports outside a snapshotted tree to avoid self-invalidation.
For a local review, prefer explicit files or a smaller tree. External includes,
figures, and sources not in the selected tree require explicit inputs. Cache
exclusions are not a TeX/Lean dependency resolver.
The read-only [scope diagnostic](evidence-scope.md) can suggest literal TeX
inputs missing from this selection. It reports ambiguity and unresolved dynamic
inputs, never promises complete TeX interpretation or widens a saved snapshot.

The active evidence protocol is automatically fingerprinted as a policy input;
proof and writing reviews also include the numbered paper-referee standards.
Use repeatable `--policy-file` for other relevant guidelines in this checkout.
Policy paths are relative to the checkout, so moving `.agents` to `.claude`
does not change their identity. Host writing rules and corpus selections are
private files and should be included with `--file` when relevant.

After the actual review, fill only the metadata:

- `verdict`: `pass` or `fail`, preserving the actual conclusion;
- `reviewer`: the actual person or agent, not an invented identity;
- `mode`: `single-context`, `independent`, or `owner` (only for an owner review);
- `reviewed_at`: the actual ISO date `YYYY-MM-DD`;
- `report`: a workspace-relative path to the substantive review or confirmation;
- `report_sha256`: SHA-256 of that report's bytes at the time of confirmation.

Do not alter captured inputs while filling the metadata. If the source changed
during review, complete the check against a frozen version or start a new scoped
review. Preserve the earlier record through normal version control.

A claim status change also changes the captured inputs, even if the proof
text did not change. Claim promotion and approval recording are separate acts:
if a completed check justifies promotion, review the final recorded statement,
status, and evidence together before saving a new passing snapshot. Do not
silently carry an earlier approval over to the promoted catalog entry.

Proof and writing reviews answer different questions. A wording change outside
the recorded proof inputs need not invalidate a proof review. A changed proof
input requires review; neither a text diff nor this tool can automatically
establish mathematical equivalence. Never close a stale warning by rehashing an
old `pass`. Owner review requires the owner's new confirmation when needed.

## Check the selected records

```sh
python3 <labo-script> evidence check --catalog research/example/claims.yaml
python3 <labo-script> evidence check --record research/example/reviews/proof.yaml \
  --strict --format json
```

Catalog checks reject malformed records, missing inputs, unresolved or circular
dependencies, and inconsistent formal/owner metadata. Review checks distinguish
`current`, `stale`, `pending`, and `failed` records. Pending/stale records warn
normally and fail with `--strict`; malformed or failed records fail in either
mode. A current passing record means its recorded inputs still match, not that
the mathematics is true, the reviewer really performed the check, or an entire
paper is ready. Coverage remains limited to the explicitly selected inputs.

Run only on the chosen catalog and records. Do not create records or require
unrelated programs to migrate merely to silence diagnostics. A report-only
request does not authorize recording approval or editing the manuscript.

## Supporting opt-in workflows

These commands use the same source-local runtime and skill-owned rules. They
create no new workspace-wide policy and do not replace substantive review:

| Need | Entry point | Interpretation |
| --- | --- | --- |
| Detect omitted manuscript inputs | [`evidence scope`](evidence-scope.md) | Conservative dependency diagnostics; no automatic scope expansion |
| Inspect one program's coverage | [`evidence status`](evidence-status.md) | Recorded claim status and direct review freshness, separately |
| Re-execute one mapped Lean source | [`evidence replay`](formal-replay.md) | Plan by default; explicit trusted execution, declaration and axiom observations |
| Preserve an actual first-reader sequence | [`paper reading`](../../paper-referee/references/staged-reading.md) | Cumulative prefixes and append-only observations; no independence certificate |

Changing this protocol's bytes makes existing snapshots stale by design. A
policy update is not a reason to rehash an old passing verdict automatically;
determine and perform the smallest relevant recheck.

## Design provenance

This adaptation is informed by Yoshito Ishiki's public
[review records](https://github.com/yoshito-ishiki-math/math-research-harness-public/blob/main/docs/REVIEW-RECORDS.md)
and [formalization protocol](https://github.com/yoshito-ishiki-math/math-research-harness-public/blob/main/docs/FORMALIZATION.md),
in the public derivative of Haruhisa Enomoto's
[math-research-harness](https://github.com/haruhisa-enomoto/math-research-harness).
The implementation here is source-local to labo-skills; it does not vendor the
other harness or impose its directory layout.
