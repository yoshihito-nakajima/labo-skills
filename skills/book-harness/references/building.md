# From cards to a book

`book render --route R --level L0..L4` produces the TeX of a route (see [pool and route](pool-and-route.md)):
`\section` per route section, with `\chapter` added for chaptered routes. A chaptered standalone build uses
a book class. Theorem-like environments share a counter per section, and proofs follow their claims by default.
Labels and `\index` entries derive from supported card fields. Write the generated files to the project's cache or output
folder. Make text corrections in the cards and regenerate.

## Card content in the reader edition

For the selected show level, read the generated text with the cards at hand. Check that the full statement and
the conventions, boundary cases and notes needed to use it reach the reader. Keep internal records in their
[own fields and ledgers](templates.md#reader-text-and-working-notes).

The current renderer takes A1 definition and notation, A2 hypotheses and conclusion, A3 steps, A4 setting and
verification, A5 question and solution, and A6 convention. A2 quantifiers and boundary cases and A6 scope are
not emitted as separate blocks. State reader-facing quantifiers and exceptions in the rendered statement or
convention, and place necessary proof explanations in the steps. Use a single natural passage in the reader
edition. When changing templates or supported reader fields, update the renderer and check representative
output in the same change.

## Reader-facing build

Before the first assembled preview, record the actual build entry point, shared TeX settings, index
registration and build command. Reuse the project's established settings where available. Apply
[mathematical-navigation](../../mathematical-navigation/SKILL.md) to that build. The built-in standalone
preamble is a quick preview baseline. Check the preamble and index build actually used before handing an
output to readers.

- **References.** `[[card-id]]` in card text becomes `\cref{label}` with the card's `label`, else `card:<id>`; every
  label belongs to its actual target. Shared numbering retains separate reference types and names for
  definitions, theorems, lemmas, propositions, axioms, examples and exercises. For A2, set `env` to the intended
  kind when it differs from the theorem default. Use a named target for a cited unnumbered convention. Follow
  the [typed reference rules](../../mathematical-navigation/references/typed-references.md).
  Keep legacy labels that still point to the same content. `REF-OUTSIDE-ROUTE` warns about mentions outside the
  route and its borrows.
  Follow the [cross-volume prerequisite rules](pool-and-route.md#prerequisites-from-another-book) to
  cite borrowed material and validate the owning route and version before building.
- **Colors and links.** Apply the project palette to headings, numbers and reference links as specified by
  [mathematical-navigation](../../mathematical-navigation/SKILL.md). Compare the displayed reference type and
  number with the destination and confirm that its name and number form the link.
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
- **Reading.** Give readers the [shared reading page](views.md#reader-facing-html) from `book read`.
  `book html` gives the card and dependency tools.
- **Equations and indexes.** Set `typed_navigation: true` when creating a numbered card book. Use a display for each
  equation or group the reader needs to cite. Put a stable `\label{eq:topic-name}` inside that formula and cite it
  with `\cref{eq:topic-name}` or `\eqref{eq:topic-name}`. Use separate displays for independently cited lines.
  The renderer gives otherwise unlabelled displays a generated label. Add the authored label before citing one in
  new prose. For an important inline formula, an explicit label or index registration creates a numbered target
  at that occurrence. Incidental inline symbols stay inline without numbers.
  Write term entries in `index` and formula entries in `formula_index` as
  `{term: ..., reading: ..., target: 'eq:topic-name'}`. The formula target is required in a typed route. Put
  multiple independently citeable formulas on their own entries. Give terms a useful reading or alias at their
  introduction. Custom build macros receive the label, reading and display term. With a custom TeX preamble, include
  the shared `INLINE_TEX` macro once and configure the term index to link to its source and the formula index to link
  to the actual equation number. Generate linked lists of numbered statements, exercises and equations.
- **Cross-format check.** Run `book check --route ROUTE` before freezing. In the real build, verify `@cref` types and
  destinations in TeX's aux output and reuse its numbers in the HTML. Check both index files, catalog links and
  HTML fragments. Test at least one equation in a folded proof, a definition or theorem, and an exercise from the
  printed and HTML navigation. For the F01/F02 builder the output review script is
  [check_reader_references.py](../../reading-book-output-review/scripts/check_reader_references.py).
- **Reader-facing headings.** Use the mathematical subject as the route and section title. Keep production
  unit IDs and revision codes in the plan or route metadata. Check the generated cover, section headings,
  printed PDF contents, PDF bookmarks and HTML headings. Apply the
  [hierarchical numbering rules](../../mathematical-navigation/references/document-navigation.md#長大教材の階層番号).
  In a chaptered book, use the [outline checker](../../reading-book-output-review/scripts/check_reader_outline.py)
  with `--toc-pages FIRST LAST` to compare printed TOC numbers against the route, using physical PDF page numbers.
  Compare the printed titles with the route and check the bookmarks and HTML headings in the same build.
  Confirm cross-references and indexes
  at representative old and new section boundaries. A layout-only migration preserves the flattened card/proof
  order and mathematical fingerprints.
- **Numbering and index.** Numbers come from the route's section order and LaTeX counters, so reordering a route
  renumbers; use labels, ids and `[[...]]`, never typed numbers. Register index entries in a card's `index` where the
  notion is introduced.
- **Joined books.** A route that `includes` others renders them in order; check the joined route
  (`check --route joint`) and review its glue and entrance, which are new text.

Keep the route version, generated TeX and matching PDF together for output review. Use card IDs and stable
labels to trace PDF positions back to the cards. For an unnumbered proof or transition, record the containing
claim or section label alongside its card ID. A successful compile records build health. Check text coverage,
reference types, colors, destinations and indexes in the [output review](../../reading-book-output-review/SKILL.md).
