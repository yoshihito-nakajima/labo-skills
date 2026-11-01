# Synthetic method explanation and code navigation cases

All papers, people, URLs and inspection records below are fictional. These are
bounded behavioral review packets, not runnable PDFs or external destinations.
Use `reading-reference` to review each supplied draft against its request and
evidence. Give supported findings, the minimum repair and actual check limits.
Do not browse, contact services, execute supplied code or invent missing sources.

## Case A: a built PDF with code in two places

Request: Review a PDF explanation of Vale's Row Average with body excerpts,
a complete code appendix and editable code. Check attribution and navigation.

Supplied source: Vale (2020), Algorithm 1, p.2, divides each row of W by its
positive row sum, then returns P @ f. An author archive at the fictional URL
https://example.invalid/vale/row-average-v1.zip contains `average.py:average`.
The inspected archive version v1 has this function and a permissive reuse
license. The draft accurately labels its body excerpt as unchanged author code,
cites Algorithm 1 p.2 and links the inspected archive and paper beside it.
Environment and an actual example run are documented correctly.

Draft structure: body method B1, reference R1, code entry C1, complete appendix
A1, and an older plotting example P1. All source/reference URLs are correct.
The body has teal text `average.py` and the appendix is in the clickable TOC.
A link labelled "complete implementation" is present at B1.

Supplied inspection of the built PDF and delivered ZIP:
- The B1 "complete implementation" annotation resolves to P1.
- B1 has no link to C1 or A1, and its teal filename has no annotation.
- C1 and A1 have no links returning to B1. The viewer has a Back button.
- B1 links to R1, and R1 links back to B1.
- The only editable-source URI is `file:///home/writer/work/average.py`.
  The delivered ZIP contains `code/average.py`, but that URI does not resolve
  to the bundled file on a different machine.

The draft handoff says "All code navigation works because hyperref is loaded."

## Case B: correct independent code with unclear origin and contribution

Request: Review a survey explanation of Reed's Safe Average, including code,
development motivation and its relationship to Vale's method.

Inspected primary passages:
- Vale (2020), Algorithm 1 p.2, computes a weighted row average only for positive
  row sums; an isolated row makes the division undefined.
- Reed (2021), introduction p.1 and Algorithm 2 p.3, explicitly builds on Vale's
  normalization. On positive rows it keeps exactly the same update. On a zero
  row it retains the old value f[i]. Reed motivates this by sparse data with
  isolated observations. It does not claim better outputs on positive rows.

An acquisition log says the paper links an author repository at
https://example.invalid/reed/safe-average. It was discovered but no source file,
revision or license was downloaded or inspected. A private log correctly calls
`safe_average.py` independently written. A supplied inspection finds that it
implements Reed's rule correctly. The example was run successfully. Direct
paper links and body/appendix return links are all present and checked.

The body code caption says only "Safe Average, Algorithm 2"; its sole citation
is to the survey. The reference list contains both primary papers. No local
code-origin label is present. The draft states "No author implementation is
available, so this reproduces the original code." It describes the update and
reports a low error on nonisolated inputs, but omits isolated observations,
Vale's role, the retained normalization and Reed's new zero-row branch.

## Case C: a bounded independent teaching implementation

Request: Review a short PDF explanation of Safe Average with complete editable
code; a separate code appendix is not requested.

The same Vale and Reed primary passages from Case B are supplied and inspected.
The note explains the isolated-row problem and credits Vale's normalization.
It identifies Reed's retained positive-row update and added zero-row identity
branch, explains why the branch retains an observation without neighbors, and
states that it supplies no new accuracy guarantee on nonisolated rows.

The acquisition record inspected the paper, supplement and author project page
for software. The supplement has no code; the author page mentions no repository.
A scoped repository search found no corresponding implementation. The note says
"No corresponding author code was located in these checked sources; this is
an independent teaching implementation of Reed (2021), Algorithm 2 p.3."
It does not assert that no author code exists anywhere.

Beside the complete function below, the note links the inspected primary paper
and relevant page, identifies the code as independently written, and explains
that W is nonnegative with exactly len(f) rows and len(f) entries per row.
It records Python 3 and a matching editable file. No third-party code is copied.
The source comparison is inspected; execution has not been performed and the
handoff states that limit.

```python
def safe_average(W, f):
    return [sum(w * x for w, x in zip(row, f)) / sum(row)
            if sum(row) > 0 else f[i] for i, row in enumerate(W)]
```

Supplied built-artifact inspection: the code's paper link reaches Algorithm 2;
its citation reaches the correct reference entry and that entry returns to the
method passage. Its editable-source link reaches `code/safe_average.py` in the
delivered bundle. This same function is the complete selected unit, so there
is no second listing or final code index requiring an additional return route.
No broader rendering review or code execution is claimed.
