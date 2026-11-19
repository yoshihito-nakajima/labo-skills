# From cards to a book

`book render --route R --level L0..L4` produces the TeX of a route (see [pool and route](pool-and-route.md)):
`\section` per route section, theorem-like environments with one counter per section, proofs after their claims,
labels and `\index` entries from the cards. Output is generated: it goes to the project's cache or output folder
and is not tracked, and nobody edits it.

- **References.** `[[card-id]]` in card text becomes `\cref{label}` with the card's `label`, else `card:<id>`; every
  rendered fact card carries that label. Referring by id keeps references valid when a card moves between books.
  A mention of a card that is not in the route (and not borrowed) is warned about (`REF-OUTSIDE-ROUTE`).
  Legacy bodies keep their own labels.
- **Text in cards.** Card text is Markdown-light: `**bold**`, numbered and bulleted lists, `$...$` math. Proof cites
  `[by: a, b]` print as a cross reference (`\cref{...}`); an axiom card (`ax-...` or `env: axiom`) renders as an
  `axiom` environment. Unicode symbols a text font lacks (⇒ ⇐ ⇔ ω ℵ ...) are written as `\ensuremath{...}`; a title with
  `_`, `&`, `%`, `#` outside `$...$` is escaped.
- **Whole document.** `--standalone --language ja|en [--title T]` adds a preamble (`ja`: upLaTeX + dvipdfmx,
  `jsarticle`; `en`: pdfLaTeX/XeLaTeX `article`; both with amsthm environments and cleveref) and the document
  wrapper; `--preamble FILE` replaces the built-in preamble with the project's own (it must define the environments
  `definition theorem lemma proposition corollary axiom example exercise solution` and load cleveref).
  Without `--standalone` only the body is written, for `\input` from the project's `main.tex`.
- **Building.** Compile with the project's build path ([course-authoring](../../course-authoring/SKILL.md) for
  courses, [labo-build](../../labo-build/SKILL.md) for papers); the tool does not compile. Structural and visual PDF
  checks, index coverage and the output review are separate evidence from `book check`.
- **Reading.** `book html` (see [views](views.md)) is the reading and slicing aid; it is not the book.
- **Index macros.** In a card, `index` (terms) and `formula_index` (formulas) entries are plain strings, or mappings
  `{term: ..., reading: ...}`. With `--term-macro termat --formula-macro formulaat` (the project's own macros) a
  mapping is written as `\termat{<card label>}{reading}{term}`; without the options it is a plain `\index{term}`.
  Imported (legacy) cards already carry the project's macros in their text.
- **Numbering and index.** Numbers come from the route's section order and LaTeX counters, so reordering a route
  renumbers; use labels, ids and `[[...]]`, never typed numbers. Register index entries in a card's `index` where the
  notion is introduced.
- **Joined books.** A route that `includes` others renders them in order; check the joined route
  (`check --route joint`) and review its glue and entrance, which are new text.
