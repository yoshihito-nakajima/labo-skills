# Pool, routes and joining books

## Layout

```
book/
  pool/<area>/<id>.md          fact cards A1-A6, shared by every book
  src/<id>.md                  source records C1, shared
  route/<slug>/route.yaml      sections, order, what is shown, includes
  route/<slug>/card/           glue B1-B5 of this book
  route/<slug>/map/            source mappings C2
  route/<slug>/finding/        findings D1
```

Ids are unique across the whole root. Prefix glue ids with the book (`intro-glue-1`).
Generated output (TeX, HTML, PDF) goes to the project's cache/output, never into the root.

## Pool first

Before a fact card is created, search for it: `book search "<words, symbols, old names>"`, with
several queries (the matcher is lexical). `book new` for an A card runs the same search and stops
when a similar card exists; the caller must state one of

- `--decision reuse` — the same statement; nothing is written, the route simply lists the card;
- `--decision variant:<id>` — hypotheses, quantifiers, domain or normalization differ; the new
  card gets a `variant` relation to `<id>` and must say what differs;
- `--decision new --reason "<why none fits>"` — recorded in `searched:`.

A proof is created with `book new A3 <id> --proves <claim>`: the first proof becomes the owner; a second needs
`--decision alt --reason "<what it adds>"` and is not the owner. The search compares cards of the same kind.

The search is a prompt to compare hypotheses and quantifiers, not an equivalence test. Same name
with different hypotheses is a different card; the same claim with a different proof is the same
claim card with another A3 (`owner: false` for the alternative).

## Mapping sources to cards (at creation time)

Reading a source unit, in the order of the book: find or create the cards, then write its C2
at once: relation (same, implies, special-case, variant, alt-proof, equivalent), adoption and
scope audit. Several sources for one claim are several C2 rows pointing at one card. The
scope audit of a volume is the set of its C2 rows; completion is `book status`.

## Routes

```yaml
title: Parity A
includes: [prelim]            # earlier routes, in order; the cards are shared, not copied
sections:
  - title: Even
    items:
      - entrance-a             # a card id
      - {card: claim-parity, proof: later}   # owner | later | omit | appendix | <A3 id>
      - {proof_of: claim-parity}             # its proof, after the lemmas it uses
appendix: [lem-technical]
```

- The sequence is what the reader sees. Every card's `requires` (and cited conventions) must come
  earlier in the sequence or be listed under `borrows` in an entrance card of the route.
- A claim shows its chosen proof right after it unless `proof` says otherwise; `later` places
  it at `proof_of` (list `proof_of` only for a claim marked `proof: later`, or the proof appears twice and `check`
  warns `DUPLICATE-IN-ROUTE`). A different proof for this book is chosen with `proof: <A3 id>`.
- **Joining books**: a route that `includes` others plus its own sections and glue is the joint
  book; reading order, glue and entrance are its own, cards are shared. A card has one owning
  proof in the pool; other books cite or choose an alternative explicitly.
- **Glue between joined parts** is a B2 between the last card of one part and the first of the next.
- Symbols that two cards use differently are a conflict when joined: settle it in an A6
  convention or a variant, not in the glue.

## Show levels

`book render --level`: L0 definitions, claims and conventions only (the statements of the book);
L1 adds examples; L2 adds proofs; L3 adds glue (lecture-note form); L4 adds exercises with
solutions. The cards are the same at every level. Labels come from the card's `label`, index
entries from `index`.
