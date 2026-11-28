# Accepting a complete independent math review

Use this opt-in receipt for a handoff case whose full mathematical scope is listed in a single frozen packet.
The independent reviewer still checks the mathematics and the scoped use of prerequisites. The harness checks
the handoff and records a clean result. Findings, partial checks, older case layouts, or changed versions go to
the usual producer/intake path. The automatic C2 queue keeps its own packet contract.

## Fixed case

Use `freeze.json` to map every frozen case file to its SHA-256. Include `scope.json`, the packet's
`manifest.json` and `cards.md`, and the relevant source and edition evidence. In `scope.json`, set `route`
and list `full_cards` as a map from card ID to `{file, fp, sha256}`. The `file` is relative to the book root.
Copy the full cards, the prerequisite/application cards required by the scope and the comparison cards under
`canonical/pool/`, retaining their paths. Include them in the freeze. The manifest's math entries must match
the full scope exactly. Its `context` entries must have frozen copies and remain outside the full scope.
Use the existing case scope to describe different checks for full cards and context. The reviewer reads the
full cards and checks prerequisite applications and comparisons to the extent called for by that scope.

## One return, one receipt

The coordinator prepares the assignment for a **fresh independent run**. Use host run IDs or preassigned fresh
worker paths that can be matched against the host's completion notification. The producer and reviewer must
be different runs, and the reviewer must have an independent context. Use the same parent model guard as
other live writes when the project requires one. The optional next request is a prewritten, permitted handoff
after a clean pass (such as output review or the next production unit). Its bytes are pinned during assignment.

```sh
labo book review-receipt prepare --case CASE --root BOOK \
    --producer PRODUCER --reviewer REVIEWER --next-request REQUEST
```

The defaults are `input/packet-01` and `result/math-review.md`. Give the reviewer the case, assignment and
report path. The reviewer writes the normal report and ends a complete pass with two lines, after the
evidence and checks. Include every fully reviewed ID once, separated by commas. Omit context-only IDs.

```text
REVIEWER: host-reviewer-id
RESULT: pass CHECKED: def-example,thm-example,proof-thm-example FINDINGS: none
```

At completion, use the reviewer's ID from the **host** and the normal project guard for this write. This
identity check relies on the coordinator pairing the host's assignment and completion. Keep the assignment
and frozen files under the usual project ownership rules.

```sh
labo book review-receipt apply --case CASE --root BOOK --reviewer REVIEWER
```

The command checks the freeze, scope, manifest, report, matching live versions, and continuation. It records all
verified full-card stamps under the book lock and emits a single `NEXT` line or `RECORDED`. A repeated invocation
keeps one stamp per card for this report. Treat the next-request path as a handoff candidate subject to the
existing dispatch claim. Preserve the report and the case receipt. If the command refuses, pass its reason
and the case to ordinary intake. For an integration test with a prepared case, use `check` in place of `apply`;
it leaves cards and receipt files alone. For historical cases, compare the frozen scope and the actual
manual receipt read-only. Historical reports with no assignment or explicit footer stay on their old path.
