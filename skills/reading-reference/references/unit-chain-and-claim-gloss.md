# Unit chain and claim gloss

Use for substantial reading notes. It adds two things that role headings and local
openings do not guarantee: a checked chain between sections and subsections, and a
sentence-level gloss for sentences that lean on prior results, assert properties, or say
that something holds. Local continuity stays under
[adjacent-passage continuity](../../mathematical-exposition/SKILL.md#carry-the-argument-across-adjacent-passages)
and [R27](review.md); heading form stays in
[roles and headings](../../mathematical-exposition/references/roles-and-headings.md).

## Reader floor

State the reader floor once at the front of the note: what mathematics and what domain
knowledge may be assumed. The default for a paper from another field is strong
mathematics and no domain knowledge. Domain vocabulary, experimental setups and data
types are then explained at the same level as mathematical terms: when first used, with
what it is, what is known about it and why the paper needs it.

## Argument spine and the chain of units

Put near the front a short account of the paper's spine: the question, the claims in the
order they depend on each other, and the unit that carries each. For a paper with many
dependent results, build it with [knowledge-dependencies](../../knowledge-dependencies/SKILL.md).

In the section map, give each unit a parent (the larger claim it serves), `needs` (what
earlier units established that this one uses: an object, result, notation, dataset or
open question) and `produces` (what later units may use). Then:

- A unit's opening says, in its own words, which need it takes up, what the previous unit
  left open, and what this unit will add for the parent's purpose. A generic background
  paragraph, a summary of the paper, or a title does not do this.
- Every need is either produced by an earlier unit or marked as coming from outside the
  paper (a cited result, background knowledge) and explained where first used.
- A unit with no consumer either serves its parent directly or is an appendix and says so.
- At the end of a parent section, say what the subsections together established.

The coverage gate checks the data (every need has a producer or an outside marker, the
opening names each need, parents exist and come first). Whether the opening actually
connects is a reading check in [R27](review.md).

## Claim gloss: lowering the step between sentences

Number the sentences of the source passages in scope. Classify each by what it does:

- `cite`: invokes a prior result or method ("X is known to be unstable (A, 2016)");
- `property`: asserts a property or behaviour (stable, robust, well defined, converges,
  scales, is sensitive to);
- `show`: says that something holds or has been shown ("X is satisfied", "we obtain Y");
- `plain`: everything else (setup, procedure, report of a measurement).

A `cite`, `property` or `show` sentence needs a gloss with four parts, each in the note
or pointing to the place that supplies it:

1. **Object** — what the named thing is: the term, quantity, method or condition,
   defined well enough to check the claim against it.
2. **Known** — what is known about it, from which source and locator: the statement
   being cited, its conditions, what is and is not asserted.
3. **Claim** — exactly what the sentence asserts here, with quantifiers and the
   conditions under which it is meant.
4. **Benefit** — what holds if it holds and why that is wanted for the argument; what
   would break otherwise.

A `cite` sentence also records a fifth part, **Added**: what this paper adds beyond the
cited work. Gloss content comes from inspected sources (R3, R5a); the writer's own
reading is labelled as such, and an unchecked part is marked open rather than smoothed.
Routine steps the reader can supply from the stated floor need no gloss; mark them
`plain` and do not hide a needed step behind "standard", "similarly" or "clearly".

For a sentence that names a term used as a black box ("by the method of …", "using
measure …"), the object part says what the term is for and what it assumes, not merely
its definition.

## Gate and review

The `sentences` section of the coverage data file lists, per unit, each numbered sentence
with its kind and gloss; the gate reports `cite`/`property`/`show` sentences with a
missing part, and `plain` sentences above a stated share, which signals a skipped
classification. Review samples sentences from the delivered text, checks that the gloss
answers the four questions from the cited source, and checks the chain at unit
boundaries; see [Review](review.md).
