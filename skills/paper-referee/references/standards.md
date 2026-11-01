# Numbered standards for **papers only**

Use `P` IDs consistently in review findings. These are auditable tests, not
an imposed paper outline. Apply them to the assigned scope and reader, using
visible passages as evidence. Test a section **locally** first; then disclose
which references resolved dependencies. Missing evidence is not a proven defect.

## P1. Narrative and question

- **P1.1 Central problem** — A reader can identify the actual mathematical
  question early, or is told exactly where its formal statement appears.
- **P1.2 Stakes** — The text makes clear why the question matters *within its
  research context*: the obstacle, limitation or unexplained phenomenon and
  what the result changes. Do not invent a failed approach to manufacture drama.
- **P1.3 Movement** — Each section opening says what changes in the story:
  an obstruction, method, result, counterexample, or synthesis.
- **P1.4 Contribution** — Original contribution is distinguishable from a
  known result, motivation, computational observation, or conjecture.
- **P1.5 Submission ordering** — If other papers are relevant, their
  relationship can be unfolded by submission order; non-linear references
  must still be navigable without reading every cited work.
- **P1.6 Abstract** — Read it independently. Recover the objects, question,
  result and scope without paper-specific unexplained terms. Later definitions
  can repair a body passage but do not make an opaque abstract self-contained.

## P2. Section openings and global map

- **P2.1 Purpose** — From the opening alone, a reader knows why this
  section exists.
- **P2.2 Inputs** — The opening identifies material it assumes; if the
  prerequisites are elsewhere, it gives a useful route to them.
- **P2.3 Outputs** — The promised local result or understanding is specific.
- **P2.4 Route** — The opening allows the reader to predict which result or
  section will matter next. A list of theorem numbers without their roles
  does not explain the argument.
- **P2.5 Honest locality** — An opening does not promise self-containment
  when nontrivial external definitions are silently needed.

## P3. Local readability

- **P3.1 Defined vocabulary** — Symbols and mathematical objects are defined
  at first use in the section or their source is unambiguously located. Check
  object types, ambient spaces, indices and binding scope in statements,
  displays, tables and captions as well as prose; familiarity is not a binding.
- **P3.2 Dependencies** — A lemma from elsewhere is identified precisely
  enough to find; a reader is not forced to search the entire paper.
- **P3.3 Scope of assumptions** — Quantifiers, standing hypotheses, and
  exceptions are visible where they matter. Say which variables a choice,
  constant, subsequence or estimate depends on, and what is uniform. A result
  for one selected object does not establish a result for every such object.
- **P3.4 Local progress** — One can say what was proved or learned from a
  section without already reading its successor.
- **P3.5 No false autonomy** — Cross-reference is welcome when signposted;
  a local review must not demand gratuitous restatement of all earlier proofs.
- **P3.6 Recoverable relation** — Identify what the passage asserts and why
  it follows. If a noun phrase hides the operative map, inequality or relation,
  locate that omission even when an expert can guess it. Preserve both the
  initial confusion and any reference-assisted recovery.

## P4. Mathematical rigor

- **P4.1 Exact claims** — Hypotheses and conclusions support the claimed
  theorem, including edge cases and degenerate examples.
- **P4.2 Proof transitions** — Nontrivial inferences have arguments or exact
  cited lemmas. For an application, match the current objects, substitutions
  and hypotheses to the cited result unless that match is already immediate.
  "Standard" and "the same proof" do not cover a new limiting or compactness step.
- **P4.3 Formal mapping** — Where Lean verification is asserted, map the
  prose claim to its declaration and dependencies; note mismatches, axioms,
  and proof placeholders. Do not call a claim verified when its proof depends
  on `sorry`/`admit` or `sorryAx`.
- **P4.4 Status honesty** — Conditional results, unchecked arguments, and
  research conjectures are visibly different from established theorems.
- **P4.5 Counterexamples** — Stress-test strong hypotheses and boundary
  cases; give a checkable witness for a claimed refutation. A finite experiment
  can refute a universal claim but cannot prove it in general.
- **P4.6 Decisive step** — The actual obstacle and the estimate, construction
  or reduction resolving it receive enough explanation to verify. Routine
  calculations can be concise; filling those out does not close a missing core.
- **P4.7 Proof interfaces** — Track dependencies and assumptions through
  reuse. Apply an established result directly when it suffices; a different
  variant needs its additional argument. Check for circular dependencies.

## P5. Exposition and references

- **P5.1 Definitions** — Definition placement helps the reader, not merely
  the author or proof assistant. Introduce the needed mechanism before claims
  that rely on it; move lengthy constructions outside theorem statements.
- **P5.2 Examples** — Strategic examples reveal what assumptions do; absence
  is an issue only when it materially impedes comprehension.
- **P5.3 Citations** — Claims attributed to prior work are tied to findable,
  precise references and inspected source versions. Check the actual statement
  and hypotheses, not an abstract or a nearby citation. Distinguish original
  results, verified known results, and suspected-known claims still unverified;
  an unsuccessful search does not establish novelty.
- **P5.4 Contrasts** — Differences from earlier work are accurate, not
  rhetorical or based on an obsolete preprint. Compare both statements' objects,
  hypotheses, quantifiers, conclusions and decisive mechanisms; distinguish
  inheritance, special case/reformulation, extension, alternative proof and
  incomparable scope. A new notation is not a new result. Use the
  [positioning protocol](../../reading-reference/references/research-positioning.md)
  after the initial reader assessment when such claims are in scope.
- **P5.5 Terminology** — Terms remain stable unless the change is explained.
- **P5.6 Attribution** — Make clear who introduced a concept, proved a result,
  or later reformulated it. Cite borrowed concepts at first substantive use;
  crediting an exposition is not evidence that its author originated the idea.
- **P5.7 Vocabulary cost** — A new term, abbreviation or parameter system must
  earn its reading cost through explanation or reuse. Identify the concrete
  relation it hides and test a simpler formulation; unfamiliarity alone is
  not grounds to call established terminology nonstandard.
- **P5.8 Notation lineage** — Established definitions, symbols, signs and
  normalizations are respected where they fit. Consequential departures or
  translations between conventions are explicit and consistent with the cited
  source; check that statements and proofs survive the translation. Do not
  demand wholesale renaming merely because another source uses other symbols.

## P6. Editorial integrity

- **P6.1 Source hierarchy** — English TeX is original; optional Japanese
  translation is a reading/checking aid, not a second independent authority.
- **P6.2 Readability vs. rigor** — A rigorous formal proof does not excuse an
  impossible-to-navigate paper; an elegant paper does not establish Lean truth.
- **P6.3 Genre boundary** — Do not judge slides, lectures, or a website by
  paper-only density or completeness standards.
- **P6.4 Concision** — Recommend shortening only when it improves the
  reader's argument reconstruction. Identify the passage's job and whether
  deletion, a formula, reordering or a precise reference preserves it. Relocate
  a secondary claim with its necessary setup, not just its proof. Preserve
  hypotheses, attribution, teaching examples and useful local reminders.
- **P6.5 Emphasis** — Give the decisive idea more space than routine support.
  Diagnose actual repetition, delayed purpose or needless decoding rather than
  imposing identical paragraph rhythms, a word quota or a universal outline.
- **P6.6 Revision integrity** — A proposed cut or moved definition must leave
  retained claims well-formed and their applications valid. Recheck affected
  dependencies; unchanged sections need no repeated review merely for bookkeeping.

## P7. Referee process and report

- **P7.1 Scope disclosure** — Record which openings and sections were read;
  never imply the whole work was inspected when it was not.
- **P7.2 Reproducible location** — Every criticism identifies a section,
  statement, or local passage.
- **P7.3 Severity** — Label as blocker (invalid or inaccessible claim), major
  (material comprehension gap), or minor (local editorial friction).
  Reserve blocker for a central failure preventing the requested use. Label
  style preferences separately; an unavailable check is an explicit limitation.
- **P7.4 Minimal repair** — Give a concrete, focused remedy, including a
  cross-reference instead of repeated text when appropriate.
- **P7.5 Epistemic limit** — Separate proven defect, plausible concern, and
  unresolved question. A local reading cannot certify global completeness.
- **P7.6 Reader evidence** — Record what the text let the reader reconstruct
  before checking the intended answer. Prior author context, full-text preload
  or a previous review prevents claiming a fresh first encounter; neither
  reviewer agreement nor a tool's success proves human comprehension.
