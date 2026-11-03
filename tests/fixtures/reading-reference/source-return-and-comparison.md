# Synthetic trial: prepare the source reading and expose comparison code

All names, passages and code below are fictional. No private research is needed.
The requested handout prepares a reader for §2.1 Weighted average and §2.2 Empty
neighborhood, in that order. Each unit needs a complete local account and its
original with faithful translation. Source §2.1 defines a normalized weighted
sum for positive total weight. §2.2 extends its domain by returning the center
measurement when the total weight is zero; it makes no accuracy claim.

Two inspected frozen implementations have these relevant lines:

```python
# Author release v1, average.py, lines 18–20
s = sum(weights)
value = sum(w * x for w, x in zip(weights, values))
return value / s
```

```python
# Author release v2, average.py, lines 22–26
s = sum(weights)
if s == 0:
    return center
value = sum(w * x for w, x in zip(weights, values))
return value / s
```

Both complete files and their source identity are available. No numerical run
was made. The weights are nonnegative and the inputs are finite.

Evaluate each candidate using the applicable reading rules, locating the first
missing obligation; repair only the affected decision.

- A retains the two numbered source headings but begins each with the original,
  then its translation, then the complete background and method explanation.
- B has connected preparation, but all originals/translations are collected
  after §2.2, followed by one general summary saying "now read the paper".
- C completes each subsection's preparation, identifies the zero denominator
  before the extension, then maps that issue to the precise source definition
  immediately before the intact original/translation. At the comparison it
  displays the two excerpts above with their fixed file/line identity, source
  rows and full-file links. It explains that v1 lines 18–20 equal v2 lines 22,
  25–26 for positive s, whereas v2 lines 23–24 extend definedness at s=0.
  It does not infer accuracy or measured numerical agreement. The source
  wording, order and translated qualifications are preserved. Subject names
  identify the source units before Background; each excerpt identifies the
  method and author release before the code. The main route proceeds from the
  §2.1 translation to §2.2, and ends with the common bibliography. No second
  route was requested or added.
- D follows C's source order but replaces the two code excerpts with GitHub
  links and a table saying "v1 18–20; v2 22–26".
- E displays two independent note rewrites, while the inspected author releases
  are only named in a footnote. No reason for substituting them is given.
- F explicitly requests translation only, retaining original-first parallel
  alignment, with no added method teaching or implementation comparison.

Expected distinctions: A needs the preparatory order within each source unit;
B needs local returns and a concrete correspondence, not global relocation;
C meets the supplied-content requirements but does not establish rendered or
executed behavior; D needs actual corresponding code in view; E should use the
available inspected author excerpts for its comparison or substantiate a genuine
barrier; F keeps its requested format and acquires no code requirement.
