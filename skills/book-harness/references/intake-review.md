# Review and close a card route

Use normal review for any route, with a route-wide check at the book boundary. An explicit hard review is a
separate task.

## When to call an independent reviewer

Self-check new or changed work inside the production unit. Send ordinary independent reviews once a coherent
section or group of units has stabilized. Freeze the new or changed material and give the reviewer its direct
prerequisites and relevant source passages. Carry forward valid reviews for unchanged versions and inputs.
Group related repairs and recheck the changed mathematics and affected uses. Handle requested output checks at
coherent build boundaries.

Bring a bounded review forward when the next work relies on a decisive new proof or a serious issue in a
direct prerequisite puts that work in doubt. Hold only the dependent work and continue other units. At the
book boundary, close
remaining required reviews and check the assembled route. For sizing and budget, use the
[course handoff guidance](../../course-authoring/references/production-handoff.md#まとまった範囲で提出する).

## 1. Self-check (producer)

For every new or changed fact card: hypotheses and quantifier order stated; boundary cases handled; every notion
used defined earlier or borrowed (entrance `borrows`); every proof step justified and the cites equal to `requires`;
exercise solutions worked. Where using sources, check the wording, locators and relations, and record C2 source
coverage for material being taken in. Mark `self-checked` for the actual scope checked.

## 2. Mechanical gates

```sh
book check --route R                      # no errors; read the warnings
book list --route R --legacy              # none among the new cards (or recorded as pending)
book list --route R --stale               # none, or reread and anchor
book deps --route R                       # imported cards: promote real prerequisites, reject mentions
book leak-check --route R --source-text <dir of the sources' local text> [--source-text ...]
```

When taking source material in, `leak-check` must scan every source the relevant C2 rows name, and it fails
when nothing was scanned. It reports card ids, run lengths and the card's own words; fix by rewriting the card,
then rerun. A clean result covers English runs of at least 12 words outside math. Check paraphrase and translation
as part of the producer's reading.

## 3. Independent review

```sh
book review-input --route R --unreviewed math --out local/review/<case>/input [--section N | --cards a,b | --closure X]
```

writes frozen packets (`manifest.json` with each card's id and fingerprint, `cards.md`, a reader note); an existing
folder is never overwritten. Hand a packet to [reading-book-math-review](../../reading-book-math-review/SKILL.md)
(a fresh context with the [capability required by the work](rounds.md#roles-and-model-capability)). For a check
needed before a dependent unit, use `--cards` for the exact claims and proofs. If an independent reviewer is
unavailable, record the unchecked range in the project's progress.

## 4. Returned report

Triage every finding: for each real one `book new D1 <id> --route R --target <card> --severity major|minor --summary
"..."` (it records the target's fingerprint); repair the cards; `book anchor` the cards that read them; `book check`.
Group related repairs. Use `review-input --cards <ids>` for changed mathematics and affected uses that need
independent confirmation, and record the result:

```sh
book record-review --manifest <packet>/manifest.json --report <report file> --result pass|findings [--ids ...]
```

A reviewer's last line may list the cards that have findings (`RESULT: findings CHECKED: a,b,c FINDINGS: b`); the other checked cards then pass. Only cards whose fingerprint still equals the packet's are recorded; a card edited since is listed as changed and
stays unreviewed. A `pass` of a math review lifts a card from `drafted` or `self-checked` to `independent`; the
report is stored by hash, not copied. `check` warns when a card marked `independent` no longer matches a review.
List `--ids` as the cards the reviewer checked completely; do not pass the whole packet if the reviewer covered less.

For a PDF comment, keep the reviewed artifact and route version, physical page and label or card ID, and the
issue. Repair reader text in the card. Record a common build defect once with representative locations and
the affected scope. Distinguish the author's repair and regeneration from a checked repair of the new version.

## 5. Route closure

- **Scope and reading order.** Compare the route to the agreed plan. Check each unit, stated prerequisites and
  borrows, definition order, proof obligations and joins between sources or sections. Check the requested
  transitions or lecture structure. Run `book check` and resolve errors and relevant findings.
- **Mathematics.** New and changed fact cards use the appropriate templates and carry current independent
  reviews. Reused reviews apply to the recorded fingerprint and its prerequisites. Use `book impact` after a
  change to reread affected cards and prose and reopen the relevant confirmation. Report remaining unchecked
  work and carried-over legacy cards with their actual coverage.
- **Sources.** Resolve the C2 rows for the assigned source scope and run the verbatim check for material taken in.
- **Requested output.** For a reader-facing PDF, check representative card text, references, colors and
  indexes at the first assembled preview. Later checks follow coherent build boundaries and cover changes
  and their effects, with wider coverage after a shared build change. Record the route, build settings and PDF
  identity for [output review](../../reading-book-output-review/SKILL.md). Carry forward relevant math review
  evidence while the mathematical content and prerequisites are unchanged.

The current `book status` prints `complete` for source mappings and `taken in` for source coverage plus review of
in-scope non-legacy fact cards. It reports carried-over legacy separately. To close an assembled route, record the
reading-order and scope check against the plan, including for routes with no new C2 rows. Report written,
self-checked and independently reviewed ranges with their versions.
