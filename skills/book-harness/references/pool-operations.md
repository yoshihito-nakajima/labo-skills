# Keeping a large pool in order

## Naming and areas

Ids are lowercase kebab-case and stay meaningful: `def-`, `lem-`, `prop-`, `thm-`, `cor-`, `ex-`, `exer-`, `sol-`,
`conv-` followed by the notion (`def-quotient-map`). Glue ids start with the book (`parity-glue-3`). `area` is the pool
directory: a mathematical topic (`sets`, `rings`), not a book. Old identifiers go to `aliases`; never reuse an id
for another fact. Fewer than a few hundred cards per area; split an area when it grows past that.

## Reading the pool without loading it

- `book search "<words>" [--kind A2]` finds candidates; use several queries (the matcher is lexical).
- `book show <id>...` gives a card with what it requires, what uses it, its proofs, mappings, findings, reviews and
  routes. `book list --route R --kind A2 --status drafted --stale --legacy` selects cards.
- Work on the card and its neighbourhood; `closure` and `impact` give the exact sets.

## Rewriting operations (dry run by default; `--apply` to do it)

- **merge** `KEEP DROP`: same kind only. Every reference to DROP (requires, relations, mappings, borrows, anchors,
  `[[...]]` mentions, `[by:]` cites, route items) is rewritten to KEEP; DROP becomes an alias; the old file moves to
  `retired/` with `merged_into`. If DROP required something KEEP does not, or both claims have proofs, the plan says
  so: decide by hand (one proof `owner`, the rest `owner: false`). A card listed twice in a route is listed once.
- **rename** `OLD NEW`: the same rewriting; OLD remains an alias.
- **retire** `ID --reason`: refuses while something still refers to the card; moves it to `retired/`.
- **split**: no command, because splitting is a mathematical decision. Create the new cards (searching first),
  move the content, point the references at the right new card with `rename`/`merge` plans as a guide, retire the
  old card, then `check`.
- Nothing is deleted. Rewriting a card re-serializes its front matter (comments in the YAML are lost).

## Legacy cards

Cards cut from existing TeX carry `legacy: true`, `variant: unclassified` and one `本文` section. When such a card
is next touched, `book restructure ID` rewrites it as the template's placeholder sections beside the old text; fill
them, delete `本文`, set `legacy: false` and choose the variant. `check` warns `LEGACY`, `BODY-LEFT` and
`UNCLASSIFIED-VARIANT` until then. A legacy card renders as its original environment.

## Dependency candidates

`book deps [--route R] [--write]` reads `\cref`, `\ref`, `\eqref` (an equation's owner is the card whose text
contains its `\label`) and `[[card]]` mentions in card text. A citation is not a prerequisite (motivation, forward
remarks, comparisons cite too), so the result is stored only as `requires_candidates`, which no check treats as a
hard edge. `book promote ID [--only a,b]` makes real prerequisites hard `requires`; `book reject ID [--only ...]`
(both work only on candidates already stored, so run `deps --write` first) drops mentions and remembers them in `not_requires` so they are not proposed again. `--candidates` on `closure`,
`impact`, `graph` and `html` follows candidates too, for a first look before they are settled. Settle imported
cards before relying on their graph.

## Several writers

The pool is shared. `book new`, the rewriting operations, `anchor` and `record-review` take a lock on the root and
read fresh, so two writers cannot create the same id or both miss each other's similar card; a second creator of
the same id gets an error and must search and reuse. Edit a card only for the unit you own; when a shared card
changes, `book impact` names every card and glue to reread in every route, and the other routes' producers are told.
Writers that rewrite the same card at once need the project's own ownership rule; the tool does not merge edits.

## Scale and storage

Parsed cards are cached in `<root>/.index/` (path, size, mtime), created automatically, ignored by its own
`.gitignore` and safe to delete. A cached run of `check` on about 1,700 cards takes a quarter of a second; a few
tens of thousands of cards remain interactive. The book root's Git (if any) is local only, with no remote and all
pushes refused, as for other course material; originals and source text caches are outside it.
