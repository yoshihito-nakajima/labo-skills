# Intake review: normal review when a book is taken in

Taking a source into the pool ends with a **normal review**, not with the last card. It combines the producer's
self-check, mechanical gates and a bounded independent review of the new or changed cards. It is not the hard
(adversarial) review, which is a separate explicit task.

## 1. Self-check (producer)

For every new or changed fact card: hypotheses and quantifier order stated; boundary cases handled; every notion
used defined earlier or borrowed (entrance `borrows`); every proof step justified and the cites equal to `requires`;
no run of source sentences; locators and relations recorded; C2 rows written; exercise solutions worked. Mark
`self-checked` only for what was checked, and say what was not.

## 2. Mechanical gates

```sh
book check --route R                      # no errors; read the warnings
book list --route R --legacy              # none among the new cards (or recorded as pending)
book list --route R --stale               # none, or reread and anchor
book deps --route R                       # imported cards: promote real prerequisites, reject mentions
book leak-check --route R --source-text <dir of the sources' local text> [--source-text ...]
```

`leak-check` must scan every source the C2 rows name, and it fails when nothing was scanned. It reports card ids,
run lengths and the card's own words; fix by rewriting the card, then rerun. A clean result covers English runs of
at least 12 words outside math; it does not cover paraphrase or translation.

## 3. Independent review

```sh
book review-input --route R --unreviewed math --out local/review/<case>/input [--section N | --cards a,b | --closure X]
```

writes frozen packets (`manifest.json` with each card's id and fingerprint, `cards.md`, a reader note); an existing
folder is never overwritten. Hand a packet to [reading-book-math-review](../../reading-book-math-review/SKILL.md)
(a fresh context, a capable model; a lightweight coordinator does not read and judge itself). If the book was
rendered and built, [reading-book-output-review](../../reading-book-output-review/SKILL.md) takes the PDF and the
matching `render` source. Continue independent production while waiting. When no independent reviewer is available,
record the unperformed range in the project's progress and do not record a pass.

## 4. Returned report

Triage every finding: for each real one `book new D1 <id> --route R --target <card> --severity major|minor --summary
"..."` (it records the target's fingerprint); repair the cards; `book anchor` the cards that read them; `book check`.
Then review only what changed: `review-input --cards <changed ids>`, and record the result:

```sh
book record-review --manifest <packet>/manifest.json --report <report file> --result pass|findings [--ids ...]
```

Only cards whose fingerprint still equals the packet's are recorded; a card edited since is listed as changed and
stays unreviewed. A `pass` of a math review lifts a card from `drafted` or `self-checked` to `independent`; the
report is stored by hash, not copied. `check` warns when a card marked `independent` no longer matches a review.
List `--ids` as the cards the reviewer checked completely; do not pass the whole packet if the reviewer covered less.

## 5. The batch is taken in when

- `check --route R` has no error and `leak-check` is clean;
- no new card is `legacy` or lacks a chosen variant;
- every new or changed fact card has a current math review (`book status` shows `never` and `stale` zero for the
  batch), or the unperformed range is written down with its reason;
- no open major finding (D1) for the batch;
- the C2 rows of the batch are not `TODO`.

`book status` prints `complete` (source mappings) and `taken in` (complete and every fact card has a current math
review). The second is the criterion above; do not report a batch as taken in on `complete` alone.

Report separately what was written, what was self-checked, what was independently reviewed and what was not.
Changed mathematics later restarts only the affected cards: `impact`, reread the anchored prose, review again what
changed.
