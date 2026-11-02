# Corpus-backed terminology and notation audit

Use this workflow for terminology/notation checks and for the affected
mathematical language in substantive manuscript drafting, revision or review.
`reading-reference` owns source investigation; `paper-writing` owns authorized
edits and `paper-referee` owns report-only findings. Keep the requested scope:
a local audit needs targeted sources, not an automatic field survey or a new
mandatory catalog. Corpus collection/population is a separate action.

## Read the manuscript before the corpus

Preserve the initial blind/local reader assessment before accessing corpus
examples or author explanations. Record what each important symbol or name
actually denotes: its first use and definition/reference, object type, ambient
space, quantifier/binding scope and mathematical role. Prioritize inherited
concepts, newly coined role labels, overloads and conventions affecting formulas.
Include displayed equations, theorem statements and captions in the affected
scope. Later source verification can explain the intended meaning without
erasing a first-use omission or the reader's initial confusion.

## Compare definitions and roles, not token counts

Use the existing `writing/.corpus/` index and any manuscript-selected sources
to locate a small relevant set. Select by **same field and same mathematical
role**, then inspect the actual definition, formula and surrounding use.
A word's frequency, a title, a corpus tag or a search excerpt does not show
that it names this object. Prefer the primary source behind inherited notation;
trace an exposition to that source when attribution or meaning depends on it.
The style corpus supplies soft cues for voice and phrasing; the definition and
semantic checks here retain their force independently of those soft cues.

For consequential terminology and symbols, inspect the actual matching source
pages under [source identity and access rules](source-rules.md). Record the
source title, exact edition/preprint version, local source identity, and
definition/equation/section/page. Distinguish printed and PDF page numbers.
Extracted text is a locator aid: visually check consequential symbols, signs,
indices and normalization on the rendered source page. Match its version to
the extraction; resolve edition drift, OCR loss or a different PDF before
claiming verification. If that page is unavailable, mark the comparison
unverified rather than inferring the symbol from damaged text or memory.

Compare the manuscript and source objects, assumptions, domains, role and
formula together. Respect multiple legitimate conventions. For a sign, scalar
factor, duality or index shift, write the translation and check its effect on
the affected statements/applications. A consistently defined alternative is
allowed; an unconverted formula may be a mathematical defect. Use the existing
[notation-lineage workflow](research-positioning.md#track-notation-and-convention-genealogy)
when consequential conventions or attribution need durable investigation.

## Classify the actual issue

| Classification | Evidence and response |
| --- | --- |
| Semantic misuse | The manuscript's actual object/role conflicts with the inspected definition or a claimed identification; show that mismatch and its consequence. |
| Undefined coined role label | The text assigns a name without a usable definition or precise standard reference; identify the missing role locally and check relevant source usage before calling the name nonstandard. |
| Inconsistent names or collision | Trace the same object under incompatible names, or one symbol with unresolved meanings in overlapping scope. |
| Normalization/sign mismatch | Exhibit the two formulas and missing translation; distinguish inconsistent use from a valid alternative convention. |
| Defined deliberate terminology | Preserve a clear, mathematically coherent local definition; explain any consequential collision or misleading inherited association with evidence. |
| Stylistic preference | Label an optional wording choice separately from definition or correctness findings. |

For example, in `sup_{f in F} J(f)`, the binding only makes `f` an element of
`F`. Calling it a “test” without defining that role or supplying a usable
standard reference can hide what objects are allowed. Identify its actual
type and suggest the smallest clarification, such as “an element f of F” or
an accurate definition of the test family. Preserve properly defined test
functions and established uses supported by the relevant source; this is not
a word blacklist. A supremum variable is a maximizer/extremizer only when
attainment is established. Keep arbitrary elements, approximate optimizers,
maximizing sequences and attained maxima distinct when suggesting wording.

A missing corpus hit establishes a coverage gap, not that a term is wrong or
nonstandard. For unresolved consequential uses, inspect targeted primary
evidence beyond the corpus when needed; report inaccessible or inconclusive
sources explicitly. Keep a locally demonstrated missing definition separate
from an unverified field-convention claim. If no suitable corpus exists,
continue the local semantic checks and identify which comparisons remain open;
do not invent corpus evidence or require corpus population to report findings.

## Deliver findings or scoped repairs

For each finding give the manuscript location, actual type/role, classification,
inspected source version and exact passage/page, evidence status, impact, and
smallest repair. Use an explicit “no matching source inspected” limitation when
appropriate. Distinguish demonstrated inconsistency, concern and preference;
severity follows the mathematical/reader consequence, not how unusual a word
sounds. Mention accepted alternatives when that prevents a mistaken rename.

Report-only work returns this evidence without changing the manuscript or
creating audit files merely to satisfy the workflow. Within authorized edits,
check affected definitions, uses, formulas and citations before renaming;
substantive contribution changes still belong to the author's decision.
Reuse an existing decision or positioning record when persistence is requested
or already part of the task. No new catalog or blanket renaming is required.
