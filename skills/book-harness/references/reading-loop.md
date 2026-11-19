# Reading a source into the pool

The producer's loop for taking a book (or part of one) into the card pool. One pass takes one **unit**: the
smallest piece of a source that can be adopted or declined as a whole — a section's definitions and results with
their proofs, one exercise with its solution, one convention. Work a unit or a small group from one section at a
time, in the order the route or plan gives. Intake is not finished at the last card: it ends with the
[intake review](intake-review.md).

## The loop

1. **Frame.** Know the book (route), the source and its record (`C1`; create it with `book new C1 <id>` if
   missing, with edition, hash and the page map), and the unit's place in the route. Run `book check --route R`;
   start from a state without new errors.
2. **Read the unit completely**: statements, proofs, the exercises that belong to it. Note hypotheses, quantifier
   order, boundary cases (empty sets, empty index, degenerate objects), what the source leaves to the reader, and
   anything wrong.
3. **Decide the cards** ([granularity](#granularity)).
4. **Search the pool before writing** (the whole pool: every volume of the course must already be imported, or a result
   owned by another volume is missed) (`book search`, at least three queries: the notion's name, its symbols, key
   words, in each language the pool uses and under older names; `book show` the nearest candidates). Compare
   hypotheses, quantifiers, normalization and the proof route, then choose:
   - **same** statement → reuse: add the new locator to the card's `sources`, write the C2 row with relation `same`;
   - differing hypotheses, domain or strength → a new card with a `variant`, `implies`, `special-case` or
     `equivalent` relation that says what differs;
   - same statement, materially different proof → another A3 for the same claim (`owner: false`) only when it adds
     a method or fills a gap; otherwise do not duplicate proofs;
   - nothing fits → new, with `--decision new --reason`.
5. **Write the cards in the book's own words** ([no copying](#no-copying)), in the template's sections: each step of
   a proof justified with `[by: card-id]`, boundary cases stated, hypotheses used. Name other cards in running text
   as `[[card-id]]` so references survive moving cards between books.
6. **Place the cards in the route** in reading order: `book place <route> <ids> [--section "Title"] [--after <card>]`
   (a claim shows its owning proof by itself; never edit `route.yaml` by hand while others write). Then **write the
   C2 row** for the unit: every source that covers it with locators, `maps_to` with relations,
   `adoption` and `scope_audit`. `OK` only when the cards exist and their proofs are closed; otherwise `PARTIAL`,
   `TODO` or `MISSING` with the remaining obligation. `OUT` names the book that owns it.
7. **Self-check** every definition, construction, proof, calculation and solution; set `status: self-checked`
   only for what was actually checked. Run `book anchor` on cards whose neighbours you read, `book check --route R`,
   and settle `book deps` candidates for imported cards.
8. **End of a batch** (a section group; tens of pages, see capacity below): intake review.

## Granularity

- One statement, one proof, one example or one exercise per card; statement and proof are separate cards.
- A lemma a proof needs and others may cite is its own card. Sub-items (i)(ii)(iii) stay together unless cited or
  proved separately.
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

## Several sources for one content

Read the second source against the cards of the first. Compare statements; add its locator and a C2 row with the
relation; do not write the content twice. Where two sources differ in hypotheses, the difference is a variant, and
joining books on the pool must settle which one a route uses.

## A unit is done when

`check --route` has no error for it; its cards are in the template's sections (not `legacy`), with variants chosen;
its C2 rows are not `TODO`; locators and relations are recorded; the self-check is real. The batch is done when the
intake review is.

## Capacity

Units are small so that one context holds the unit, the nearest candidate cards (`book show`) and their direct
prerequisites. Do not load the pool or whole books. Batches for review follow the project's size rule (a few tens of
pages' worth of cards); `review-input --max-chars` splits them.
