# Manuscript conventions

Field-general conventions for mathematical manuscripts and for agent-assisted
drafting. Workspace or author preferences belong in `writing/.rules/`; a single
paper's notation decisions belong with that paper.

## Vocabulary

- Keep the agent's working vocabulary out of the manuscript. Labels coined
  while planning or proving (for example "test objects", "witness layer",
  "shortcut card") appear in the text only if the author adopts them or the
  literature uses them. Name objects as the field does ("finite objects",
  "the function $u_X$").
- Use a technical term in the form the target-language literature uses. Do not
  coin a translation when books in that language keep the original word (for
  example, Japanese texts usually write "coupling", not a translated noun).

## Markup

- Inside TeX, use TeX markup only: `\emph{...}` for emphasis or run-in
  headings, never Markdown such as `**...**` or backticks, even when the text
  is stored in Markdown-based files.
- In Japanese TeX, type no space between Japanese and Latin letters, digits or
  inline math; (u)pLaTeX inserts better spacing itself.
- Avoid parenthetical asides in statements and proofs. A convention a formula
  needs follows as its own sentence ("where ...", 「ただし…とする」); other
  remarks become a clause or are dropped.
- Proof paragraphs may carry working labels (1), (2), ... in drafts. Drop them
  in the output; if a step is cited, show "Step $k$" and cite it as such.

## Definitions and statements

- A definition names objects and fixes notation; it does not assert facts.
  State a needed fact separately ("the metric $d$ is symmetric and ...").
- Keep each definition to the objects it introduces. Introduce an auxiliary
  object (a function space, a map, a closure) in the statement that first
  uses it, not in an earlier definition that merely prepares it.
- Put normalising constants into the definition, so later conditions read
  "$\operatorname{dis} S\le\eta$" rather than "$2\operatorname{dis} S\le\eta$".
- Distinguish a defining equality from an asserted one: write
  `\coloneqq` (mathtools) when a symbol is being defined and `=` only for
  equalities that are claimed or computed.
- Typeset multi-part statements (a), (b), ... as a list.
- When a definition extends a quantity to new arguments, write its formula
  again unless it is literally the same (an infimum over a family is not the
  formula for a single object).
- A fact needed to justify a new name (that a "principal pyramid" is a pyramid)
  is a proposition stated right after the definition, not a claim inside it.
  Never introduce a notion with a promise that it will be justified later.
- State each property once, in the strongest form needed: "$d_{\mathrm P}$
  metrizes weak convergence on $\operatorname{Prob}(Z)$", not "is symmetric,
  is a metric, and metrizes weak convergence".
- Name a result only when it has an established or genuinely descriptive name
  (Prokhorov's theorem, rigidity); a title that restates the statement adds
  nothing.
- Cite a definition or theorem to its first appearance, with a section or
  number checked in that source; cite a later text in addition only for the
  formulation actually used.
- Put the citation of a quoted result in the theorem name, for example
  `\begin{proposition}[Prokhorov's theorem {\cite[Thm.~5.1]{B}}]`, not in the
  statement text.

## Proof economy

- Expand a lemma used only once into the proof that uses it, even at some cost
  in length; keep a separate lemma when it is reused or isolates a genuinely
  separate idea. A short fact listed as a corollary item but used in one place
  is proved there.
- Prove the target statement directly. Do not isolate an intermediate lemma
  whose only use is the next step (for example "some witness gives zero")
  unless it is reused or clarifies a genuinely separate idea.
- When a quantity is an infimum, prefer "take $a$ larger than the value,
  choose a near-optimal witness, then let $a$ decrease" over first proving
  that the infimum is attained, unless attainment is needed later.
