# Card formats and the 14 templates

A card is a Markdown file: YAML front matter, then fixed `## ` sections. Headings may be
written in Japanese or English (both are listed). TeX is written as in the book. A section that
only says `TODO` is a placeholder and `check` warns about it. Section order is free; unknown
sections are warned about.

## Common front matter

```
id: set-de-morgan          # kebab-case, equal to the file name, never reused for another fact
kind: A2                   # template code
variant: equation-inclusion  # where the template has variants; it fixes required structure
title: De Morgan for families
aliases: [SET.DE-MORGAN]   # older identifiers, so existing references keep working
area: sets                 # pool directory (fact cards)
requires: []               # hard prerequisites (card ids)
references: []             # mentions that impose no order; never also in requires
symbols: []                # notation introduced here
index: []                  # index entries registered where the notion is introduced
sources: [{src: <C1 id>, loc: "Prop 2.7(iii), print pp.12-13"}]   # locators only
relations: [{to: <card>, type: variant, diff: "empty index set allowed"}]
status: drafted            # stated | drafted | self-checked | independent | lean
anchors: {<card>: <fingerprint>}   # fingerprints of what this card was read against
reviews: [{kind: math, result: pass, fp: 3f2a9c1e, date: 2026-11-19, report: <sha256>}]   # by `record-review`
requires_candidates: []    # unconfirmed citations (see pool operations); never a hard edge
not_requires: []           # candidates rejected for good
```

Text may name another card as `[[card-id]]`; it renders as a cross reference, `check` resolves it, and with
`--route` a card outside the route that is not borrowed is warned about. `legacy`, `owner_route` (the book that
owned the span when the card was imported) and `restructure` are bookkeeping fields written by the import and
restructure tools. `independent` is meaningful only while a recorded review matches the current fingerprint.

- **Fingerprint**: first 8 hex digits of SHA-256 of the kind, variant and normalized sections
  (`Remarks`, `Caution` and `Why natural` are excluded). A card is **STALE** when an anchor differs
  from the card's current fingerprint. `book anchor ID` records the current ones after rereading.
- **Status** records work, not truth. `independent` names a report and range in `reviews/`;
  a changed statement or proof moves the card back. Self-check is not independent review.
- Size: a claim is a few lines; a proof about a page or a dozen steps. Longer proofs split out
  lemma cards. Sub-items (i)(ii)(iii) stay in one card unless cited or proved separately.

**Imported cards.** A card cut from existing TeX carries `legacy: true`, `variant: unclassified`
and a single `## 本文` (Body) section instead of the template's sections. `check` accepts it with a
`LEGACY` warning and skips the proof-shape and cite checks; split it into the template's sections
when the card is next edited. Legacy cards render as the original environment.

## A: facts (pool)

| | Template | Required sections | Fields | Variants (fix required structure) |
|---|---|---|---|---|
| A1 | definition / notation | 定義 Definition | `well_defined: [claim]` for recursive and quotient-choice | structure, predicate, recursive, quotient-choice, notation-only |
| A2 | claim (theorem, lemma, proposition, corollary) | 仮定 Hypotheses; 結論 Conclusion; 量化子 Quantifiers | `env` (default theorem) | equation-inclusion, equivalence, existence, unique-existence, estimate, construction-correct |
| A3 | proof (of a claim, or of what a definition needs: well-definedness) | 方針 Plan; 段階 Steps | `proves`, `owner` | direct, contrapositive-contradiction, induction, double-inclusion, equivalence-both, construction-uniqueness, cases, computation |
| A4 | example / counterexample | 設定 Setting; 確認 Verification | `illustrates` | concrete, counterexample, computation, motivating |
| A5 | exercise and solution | 問 Question; 解答 Solution | `from` | — |
| A6 | convention | 規約 Convention; 適用範囲 Scope | other cards cite it in `conventions:` | — |

Optional sections: A1 前提 Premises, 記法 Notation, 注意 Caution; A2 境界の場合 Boundary cases,
備考 Remarks; A3 境界の場合の確認 Boundary check, 使った仮定 Hypotheses used; A4 何が分かるか What
it shows; A5 使う主張 Claims used; A6 例外の宣言のしかた Declaring exceptions.

Enforced by `check`:

- A1: recursive and quotient-choice definitions carry `well_defined: [claim]`. Required
  sections exist, ids and kinds are valid, every reference resolves, hard prerequisites have
  no cycle, and (with `--route`) each prerequisite comes earlier or is borrowed.
- A3: each step may end in its justification `[by: card-id]`; every cite is in `requires`
  (error) and every `requires` is cited (warning); the variant's shape is present (both directions
  for `equivalence-both`, base and step for `induction`, existence and uniqueness separately,
  two inclusions); at most one `owner` proof per claim; a claim with several proofs and no owner
  is warned about, and so is an `equivalence` or `unique-existence` claim whose chosen proof has
  another shape.
- A2 with status beyond `stated` and no proof card is warned about.

Rules for the author and the reviewer (not machine-checked; say so when reporting a check):

- A1: a structure states carrier, data and their types, quantified axioms and conventions; every
  word used is defined earlier (definition closure, as far as `requires` records it).
- A2: states hypotheses, quantifier order and boundary cases (empty sets, empty index,
  degenerate). Hypotheses that differ make a different card. The proof is not part of the claim.
- A4: a counterexample says which hypothesis it removes. A5: the question is restated in the
  book's own words, never quoted. A6: stated once; a card that needs it lists it in `conventions`.

## B: lecture-note glue (per book, `route/<slug>/card/`)

Glue states no new fact: it names fact cards by id and says what has been done, what is missing
and why the next thing follows. A fact found while writing glue is moved into an A card.

| | Template | Required sections | Fields |
|---|---|---|---|
| B1 | motivation / question | 問い Question | `answered_by: [cards]`; unanswered questions are warned about |
| B2 | transition | 済んだこと Done; 足りないこと Missing; 次にすること Next | `between: [prev, next]` and anchors on both; variants forward, supplement, turn, bridge-to-example, need-for-definition |
| B3 | preview | 後で示すこと To be shown later | `forward: [cards]`; a previewed result is never a prerequisite |
| B4 | recap | 確立したこと Established | — |
| B5 | entrance | 問いと終点; 前提とする既知事実; 規約 | `borrows: [{card, owner, why}]` |

The entrance lists the exact results the book borrows. `check --route` reports every card
a route needs that is neither in the route nor listed under `borrows` (UNLISTED-BORROW),
so a missing convention or lemma is found before a reader finds it. An unproved borrowed
result is not turned into an assumption without a recorded change of scope.

## C and D: ledgers

| | Template | Where | Required |
|---|---|---|---|
| C1 | source record | `src/` (shared by books) | 書誌, 版・ハッシュ, 頁対応; `edition:` or `sha256:` in the front matter (a warning otherwise); no text from the source |
| C2 | source mapping | `route/<slug>/map/` | `sources: [{src, loc}]`, `maps_to: [{card, relation, diff}]`, `adoption`, `scope_audit`; 原著との差 |
| D1 | finding | `route/<slug>/finding/` | `target`, `target_fp`, `severity`, `status`; 所見 |

- One C2 per audited unit: a unit of content the book adopts, with every source that covers it (one row may name several books). `adoption`: adopted, partial, not-adopted,
  outlook; anything but adopted needs `reason` (and the remaining obligation). `scope_audit`:
  TODO, OK, PARTIAL, MISSING, OUT (owned elsewhere; `reason` names the book). A volume is complete when every row is OK or OUT. An OK whose target changed or is only `stated` is warned about.
- Relations: same, implies, special-case, variant, alt-proof, equivalent, supplied (a card the book adds that the source lacks). A variant says what differs.
- D1 status: fixed, resolved-with-reason (the reason is required), open. A finding whose target
  changed since is flagged for recheck. Open major findings block completion.

## New templates and variants

Add one only when it needs different required fields or a different check. Change a template in
`labo_tools/book.py` and update this file in the same change.
