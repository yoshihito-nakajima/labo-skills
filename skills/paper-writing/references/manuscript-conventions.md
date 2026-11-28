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
- Refer to results, sections and equations by label, never by typed numbers.
- Proof paragraphs may carry working labels (1), (2), ... in drafts. Drop them
  in the output; if a step is cited, show "Step $k$" and cite it as such.

## Notation and quantifiers

- Introduce notation at the scope where it is used. Fix a symbol for the whole
  paper only when the argument has that scope, and when a result lets a
  parameter vary, state its range there and say which estimates are uniform in
  it (a group $G$ fixed throughout, a prime $p$ fixed only within one section).
- State a definition for the object that plays the role in the problem; use a
  generic symbol only when the definition will be applied to several objects
  (the Hodge star of the given metric $g$, not of "a metric", when only $g$
  occurs).
- State a standing convention (an identification, a choice of representatives,
  a sign or orientation convention) before the first object that needs it,
  not afterwards with "here we take ...".
- Keep few symbols alive: introduce a symbol right before its first use and do
  not carry it beyond its last use.
- Do not fix with "Let" a letter that is already bound by a quantifier or by a
  definition in the same argument; use another letter.
- Present members of an indexed family in increasing index order, in formulas
  and in prose, unless the mathematics requires another order
  ($H^0\to H^1\to H^2$).
- Do not refer to a mathematical object by a pronoun or a demonstrative phrase
  ("the usual one", "the former") when a standard symbol exists.

## Definitions and statements

- At a definition, state only the domain and hypotheses that make the
  expression meaningful; put stronger assumptions with the result that uses
  them (define the Euler characteristic for finite CW complexes and assume
  orientability in the theorem).

- Introduce the data of a statement with "Let" and keep "for every" for the
  objects the conclusion ranges over, so that the proof does not begin by fixing
  them again. Do not fix a parameter with "Let" and then let it vary in the
  conclusion ("let $\varepsilon>0$ ... as $\varepsilon\to0$"); introduce the
  family instead ("for $\varepsilon>0$, let $u_\varepsilon$ be ...").
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
- Lead a defining sentence with the new term, or define the symbol in a
  display with `\coloneqq` and state the ranges of the variables after it.
  Avoid "We call [a long noun phrase with formulas] the T": the term the
  reader is waiting for comes last, and two formulas end up separated only by
  "of" or "over". Display variants of one quantity side by side instead of
  repeating the sentence for each, and pair the names with the display by
  "respectively".
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

- Do not use Landau notation ($O$, $o$, $\Theta$, $\Omega$, or $\lesssim$
  hiding constants) unless the author asks for it. State explicit bounds with
  named constants and what they depend on, or write the limit.


- If a proof announces its steps by order ("we next prove the second
  assertion"), number all of them in order from the first, matching the items
  (i), (ii), ... of the statement; otherwise use no ordinal words.
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
