# Synthetic authoring trial: named subjects and document reading order

All sources, terminology and code here are fictional. No browsing or execution
is needed. Use reading-reference and mathematical-exposition for the bounded
outline and opening-text task below; do not create a full handout or PDF.

## User request

Prepare the structure for Japanese explanatory notes on the two supplied source
subsections. Make clear at the beginning which named method is being explained.
After reading each original/translation, I want to continue to the next source
subsection. Replace the old complete reprint with a background/explanation-only
view for sequential reading, omitting the target paper's original/translation
blocks and code listings. Keep the concepts and evidence needed to understand
the explanation. Do not add a code collection. Include references. Give the
ordered heading tree, a sentence at each source-unit entrance and at the
optional-view entrance, and the visible labels
before/after the two method-code blocks. Do not invent results, executions or
sources; the following information is the complete trial input.

## Supplied source information

Fictional source *Local estimators*, §3 Estimation:
- §3.1 Positive rows defines "Row normalization (RN)": for nonnegative weights
  with positive sum, divide the weighted sum of values by that sum.
- §3.2 Empty rows defines "Empty-row completion (ERC)": use RN on positive
  sums, and the center's value when the sum is zero. This extends definedness;
  no accuracy improvement is asserted.

The faithful source headings are "3 推定", "3.1 正の行", "3.2 空の行".
The selected scope is exactly these two subsections, retaining their source
numbers and parentage. Their full original text and faithful Japanese translation
are available for inclusion; this outline task need only identify their slots.
The added roles per unit are Background, Obstacle, Method/implementation,
Fit/limits, Comparison, Execution status, Implementation search, Source
correspondence and Original/translation. Several operations share one method
role. A station example and its figure/caption are supplied to establish the
input and empty-neighborhood issue before code; no numerical results exist.

Two inspected author-release files have complete editable copies and fixed
fictional identity in the trial bundle (no live URL is claimed):
- RN: `author-v1/rn.py`, `normalize`, lines 1–3.
- ERC: `author-v2/erc.py`, `complete`, lines 1–5; positive branch is the same RN
  calculation and the zero-sum branch returns the center value.
Both were inspected but not executed. The bibliography comprises *Local
estimators* and the two author-release source records. All claims and code
should retain their point-of-use identity even when the bibliography is shared.

One additional fictional method paper is used in the explanation:
*Completion rule*, v1, §2 p.3: "For an empty row, retain the center value.
This defines an output but gives no accuracy guarantee." This is the exact
inspected passage, with no hidden qualification in the supplied context.
Explain its role and include the original and your faithful Japanese translation
where this supporting claim is used. Add its source record to the references.
Another listed work, *History of sensors*, is background bibliography only and
supplies no explanatory claim in these notes. Its text is not supplied.

The old main text introduced s[i] only in the target-paper original block, and
its explanation referred to "the denominator above". State how the filtered
view makes the denominator intelligible without that omitted block.

## Separate bounded control

A different user requests only a two-sentence Japanese translation. State whether
the above multi-route structure applies to that request; do not draft it.

A further user explicitly requests an exact duplicate for a separate printing
purpose. State how this differs from automatically retaining the old reprint;
do not generate the duplicate.
