# Moving an existing book into cards

A book that exists as TeX chapters and a catalog table is converted in stages. The cards stay a
**read-only mirror** while other threads still write the TeX; ownership changes only at an agreed
restart boundary with every writer stopped.

1. **Mirror.** Cut the TeX at labelled statement blocks (a definition, claim or example
   environment plus the proof that follows) with the existing block rules of
   [reading-book's tex_blocks](../../reading-book/scripts/tex_blocks.py). Each block becomes an
   A card; the proof becomes an A3 `proves` the claim; catalog rows give ids, aliases,
   `requires` and `sources`. Existing labels stay as `label`, so references keep resolving.
   Prose between blocks becomes B cards in the route's order; the chapter's headings become the
   route's sections. Unlabelled blocks are counted and reported, not guessed at.
2. **Check the split is lossless.** Render the route at L4 and compare with the original chapter
   (same blocks in the same order after normalization, then the same compiled pages where the
   book is built). Report every difference; do not proceed on a mismatch.
3. **Use the mirror.** Search, graph, impact and views run on the mirror; findings that need a
   text change go to the TeX owner until cut-over.
4. **Cut over.** Writers stopped; one last mirror from the final TeX; the cards become the
   canonical text; the old chapters move to `retired/` (kept, not deleted); build and navigation
   checks run on the rendered book; restart prompts for every role point at the cards and the
   recorded cursor.
5. **Source ledgers.** Existing scope-audit tables become C2 rows, one per source unit.

The importer (`scripts/import_tex.py`) also cuts labelled examples and exercises (A4, A5) and solutions (a proof
environment labelled `sol:NAME` becomes the A3 of `exer:NAME`), keeps only blocks inside given line ranges
(`--lines`, e.g. the spans an allocation table gives a book) and records `owner_route`. Source mappings from an
existing scope-audit table become C2 rows with a `sources` list and the audit state; rows whose location is prose,
a remark or a line range need cards for that text before they can be `OK`. After the import run
`book deps --write` to get dependency candidates, and treat the cards as `legacy` until restructured.

Existing identifiers are kept as `aliases`; a numbering table is not rewritten. Source texts,
OCR and page images are never copied into cards or into this skill. Private books and their
incidents stay in the workspace; examples in skills are fictional.
