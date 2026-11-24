# Work through a book's scope

Use this loop for an assigned source range, a topic, or a topic with assigned sources. A **unit** is a section or
coherent group of results with a stated endpoint in the route plan. It may use a source passage, existing cards,
or both. Work in plan order and keep the direct prerequisites within the unit's reading context.
For Japanese text, apply the [writing rules](writing-rules.md) when drafting cards and reading the assembled section.

## The loop

1. **Frame.** Find the unit's place, allowed prerequisites and endpoint in the route plan. For each source
   being taken in, find or create its `C1` with edition, hash and page map. Run `book check --route R` to establish
   the starting state.
2. **Read the assigned material and check its mathematics.** Cover the relevant statements, proofs and adopted
   exercises. Note hypotheses, quantifier order, boundary cases, omissions and errors. If the unit uses existing
   cards, read those cards and their direct prerequisites against the requested endpoint.
3. **Decide the cards** ([granularity](#granularity)).
4. **Search the pool before writing** (`book search`, then `book show`). Search across volumes by name, symbols and
   key words, including relevant alternative names or languages. For material being migrated, import the other
   volumes into the mirror before treating the search as exhaustive. Compare hypotheses, quantifiers, normalization
   and the proof route, then choose:
   - **same** statement → reuse; when adding a source, add its locator and a C2 row with relation `same`;
   - differing hypotheses, domain or strength → a new card with a `variant`, `implies`, `special-case` or
     `equivalent` relation that says what differs;
   - same statement, materially different proof → another A3 for the same claim (`owner: false`) only when it adds
     a method or fills a gap; otherwise do not duplicate proofs;
   - nothing fits → new, with `--decision new --reason`.
5. **Write the cards in the book's own words** ([no copying](#no-copying)), in the template's sections: each step of
   a proof justified with `[by: card-id]`, boundary cases stated, hypotheses used. Name other cards in running text
   as `[[card-id]]` so references survive moving cards between books. Record terms, notation and key formulas at
   their introduction when the book carries an index. Check that the reader-facing fields contain everything
   needed to understand and use the fact.
6. **Place the cards in the route** with `book place <route> <ids> [--section "Title"] [--after <card>]`.
   A claim shows its owning proof by default. Use the locked commands for concurrent writes. If taking source
   material in, record each covered source range in C2 with locators, `maps_to`, `adoption` and `scope_audit`.
   Use `OK` when the cards exist and required proofs are closed. Record the reason and outstanding obligation
   for other states, including the owning book for a deferred item. Reused cards retain their source locators.
7. **Self-check** every definition, construction, proof, calculation and solution; set `status: self-checked`
   only for what was actually checked. Run `book anchor` on cards whose neighbours you read, `book check --route R`,
   and settle `book deps` candidates for imported cards.
8. **End of a batch** (a related group of units): [review the new or changed cards](intake-review.md).

## Granularity

- One statement, one proof, one example or one exercise per card; statement and proof are separate cards.
- A lemma a proof needs and others may cite is its own card. Keep sub-items together when they form one
  statement. Split them when a proof or a route needs one independently, and cite the exact card that
  introduces each notation or supplies each inference used. The route can present related cards together.
- One definition card per notion. Notation shared by several definitions is an `A1 notation-only` card; a rule that
  governs a whole book part (product measure convention, "numbers are integers") is an `A6`.
- A remark with no mathematics gets no card. A remark that is mathematics ("this fails without X") is an A4
  counterexample or an A2 claim.
- Lecture-note text that connects cards (motivation, transitions, previews, recaps) is glue: B cards of this book.
  If writing it needs a new fact, the fact becomes an A card first.

## Writing the glue

Glue (B cards) is what makes the route a lecture note. Write it after the fact cards it connects exist, from the
reader's position: the question that makes the next card necessary (B1), what has just been established and what is
still missing (B2), a result announced before its proof (B3, never a prerequisite), a recap (B4), the entrance of a
volume with its exact borrowed results (B5). Name fact cards by `[[id]]`; state no new fact; keep each piece short.
Pacing, emphasis and the reader's pull follow [mathematical-exposition](../../mathematical-exposition/SKILL.md)
(adjacent passages, reader pull). Anchor a transition to both neighbours (`book anchor`) so it is reread when either
changes. Glue belongs to one route: another book that reuses the cards writes its own.

## No copying

- Cards hold the book's own formulation. Follow the source's argument where it is right, but write definitions and
  proofs from the argument, not sentence by sentence; do not keep a run of the source's sentences. Names of results,
  standard notation and formulas may be the same. Restate exercises.
- Record **locators only**: source id, print page or number, section. No quotation, OCR text or page image goes into
  a card, finding, review packet, report or commit message. `book leak-check` enforces this on English text
  (math is ignored); it cannot see a translation, so the rule remains the producer's.
- Originals and their text caches stay outside every Git.

## When the source is imperfect

- A sketch or omitted step: fill it, and say so in the C2 `difference` ("source omits step X; supplied").
- An error: correct it and record the correction in the C2 `difference`; if the statement changes, it is a variant
  of the source's, not the same card.
- A result the source proves with something not yet in the pool: create or borrow that card. Never assume silently.
  If it cannot be proved now, the card stays `stated`, the C2 row is `PARTIAL` and the obligation is written down.
  Do not weaken a conclusion or strengthen a hypothesis to finish; a scope change needs a recorded reason.
- Choosing exercises: adopt those later text uses, those that test a definition, and counterexamples; each adopted
  one is an A5 with a worked solution; each declined one that the plan expects has a C2 reason.

## Adapt a result from a paper

Read the exact cited statement and proof before choosing what to carry into the route. Use the
[result reuse check](../../knowledge-dependencies/SKILL.md#reuse-a-result-across-artifacts) and record the paper
version and locators in C1/C2. Follow the book's agreed prerequisite boundary to decide which cited results or
omitted steps to supply, and note additions or changes in the mapping. If a published or shareable source is
available, use its precise locator in the rendered book. For a local unpublished source, follow its existing
access and citation constraints. Self-check and independently review new or changed mathematics under the
[route review rules](intake-review.md).

## Several sources for one content

Read the second source against the cards of the first. Compare statements; add its locator and a C2 row with the
relation; do not write the content twice. Where two sources differ in hypotheses, the difference is a variant, and
joining books on the pool must settle which one a route uses.

## A unit is done when

The cards placed in the route reach the unit's stated endpoint, the self-check is recorded, and structural
checks have no unresolved errors for the unit. New cards use the appropriate templates and variants. For source
intake, the C2 rows reflect actual adoption and coverage. Track independent review at the batch boundary and
confirm route-wide closure at the book boundary.

## Capacity

Units are small so that one context holds the unit, the nearest candidate cards (`book show`) and their direct
prerequisites. Do not load the pool or whole books. Batches for review follow the project's size rule (a few tens of
pages' worth of cards); `review-input --max-chars` splits them.
