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
"Checked Reed (2021)'s software pointers, supplement v1 and author project page
at https://example.invalid/reed/project, plus a scoped repository search. No
corresponding author code was located in those checked sources. We use an
independent teaching implementation of Algorithm 2 p.3 to expose the zero-row
branch; it is not a reproduction of author software."
It does not assert that no author code exists anywhere.

Immediately after the complete function below, a labelled source/link row
identifies it as independently written, links its complete editable file, and
separately links the inspected primary paper and relevant page. The note explains
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
The nearby explanation maps `sum(row)` to Algorithm 2's row sum,
`sum(w * x ...) / sum(row)` to the positive-row normalized update, and `f[i]`
to its isolated-row identity branch; the returned list is the signal at all rows.
No broader rendering review or code execution is claimed.


## Case D: correct links placed before two different code blocks

Request: Review a PDF explanation with two implementations, an unchanged author
function `average` and an independent `safe_average`. Both code blocks have
correct, readable captions. A paragraph before the first block links Vale's
inspected fixed GitHub revision, `average.py` lines 10–18, Reed's paper at
Algorithm 2, and the delivered complete independent file. All these destinations
are confirmed correct in supplied built-PDF observations. Each block also has
correct nearby input/output and operation-to-equation explanations, and correct
body/appendix return links.

Built PDF observation: neither block has a source/link row after it. The first
ends at the bottom of p.4. The next page begins the second block; a shared
"code sources" link appears only after the next section's heading and points to
an index containing both files. The handoff reports that a global link check
passes. Does the actual placement let the reader identify each block's source?

## Case E: code supplied only as a supplement archive

Request: Review a short PDF with one unchanged author implementation. The
inspected paper links `https://example.invalid/vale/supplement-v1.zip`, containing
`src/average.py`, function `average`. The archive cannot open at a member through
a URL fragment. Its version and reuse terms are documented. An actual supplied
PDF-link observation confirms the immediately post-code row opens this archive,
visibly names the exact member/function and labels the code as unchanged author
code. The same row links the complete delivered editable unit and body equation
(E2). Nearby prose explains every substantive operation and E2 correspondence;
input/output meanings, settings and inspection/execution status are stated.
The unit is the complete selected function, so no separate listing is needed.

Review under these supplied facts; do not require a GitHub repository to exist,
invent a function-level archive anchor, or claim a live external check occurred.

## Case F: correct source row with an unexplained author implementation

Use Case E's inspected source, working post-code links and attribution. Replace
its code explanation with "This is the author's function, so it implements E2."
No variables, input/output meanings, substantive steps, settings or E2 mapping
are explained. The complete function is attached and its source correspondence
was inspected privately. Assess whether links and author provenance alone meet
the requested method explanation.


## Case G: central-method searches leave a teaching method unsearched

Request: Review a paper-reading PDF with a main Safe Average implementation
and an added educational implementation of Vale's Row Average. Both units have
correct immediate post-code links, provenance, input/output explanations and
operation-to-equation correspondence. Both independent functions are correct.

Supplied observations: Reed's matching code was searched and inspected. The
added Vale unit cites Vale (2020), Algorithm 1 p.2, but the writer did not open
Vale's software pointer, supplement or author project page. The available paper
passage explicitly links a supplement archive with an `average.py` member; its
contents and license have not been acquired or inspected. At Vale's code, the
PDF says only "Independent educational code; author code is unavailable." The
handoff says all code sources were checked because the central method was checked.

Assess coverage per code unit, the absence claim and the reader-facing report;
do not invent the supplement's contents or require replacing code before it is
inspected.

## Case H: a private log cannot supply a local search-status report

Request: Review two independently written educational code units grounded in
Reed's Algorithm 2 and a separate method, North's Algorithm 3. Correct code,
working post-code links and substantive equation explanations are supplied.

Actual acquisition log: Reed's paper-linked repository was found, but no file,
revision or license was inspected. North's supplement URL was visited and access
failed; no matching source code was acquired. The PDF captions say only
"Educational implementation; no original software exists." Neither code's
reader-facing passage identifies the checked or unvisited places. The handoff
argues that the private acquisition log and successful toy runs close provenance.

Assess the two distinct statuses and the missing local report. A repository
being found does not establish suitability or permission to copy it, and an
access failure does not establish worldwide absence.

## Case I: inspected author code and an explanatory companion

Request: Review a bounded PDF explanation of Reed's Safe Average. The supplied
record says the writer followed the paper's software pointer and supplement to
the author repository, then inspected fixed v1 `safe.py:safe_average` and its
reuse terms before choosing a route. The function accepts a single matrix and
also has optional batching helpers. Its settings already meet the requested
single-matrix computation. An inspected permissive license permits reuse.

The note selects the author function as its main execution route. An independent
single-matrix companion exposes the positive-row sum and zero-row identity
branch as named intermediate values for hand calculation. The note considered
annotating the author function and states that the companion supplies this
separate intermediate-value trace; it does not claim independent code was
necessary to compute the result. Static comparison establishes corresponding
branches. Neither route was executed; no numerical equivalence is claimed.

Both displayed functions have immediate labelled links to their fixed source or
complete editable unit, Algorithm 2 p.3 and the body explanation. The independent
passage reports the checked route, selection order, companion role, omitted
batching and validation limit. Inputs, operations, normalization, limitations
and equation correspondence are explained. No author experiment rerun is claimed.

Review the supplied choice and disclosure; do not infer that an explanatory
companion must be deleted because matching author code is available.

## Case J: an existing option is presented as a reason to rewrite

Request: Review a PDF explaining North's ridge iteration and its implementation
choice. The paper-linked author v2 function has inspected parameters `bandwidth`
and `stop="displacement"`, accepts a single point cloud and exposes its update
function. The required fixed bandwidth and displacement stopping are supported
without modifying that code. The author version and reuse terms were inspected.

The dated task record shows the writer first created independent code, then
found and read author v2. At the code, all links, attribution and equations are
correct. The note says "After comparing alternatives, we originally chose our
own main implementation because fixed bandwidth and simple stopping required
it. The successful toy run shows it is numerically interchangeable with v2."
The original reason was not recorded. The draft supplies no comparison run of
v2 and no evidence that a wrapper or annotated author update fails the purpose.

Review the choice, chronology and numerical claim using only these supplied
facts. Do not infer that the independent algorithm is incorrect or that
independent code is forbidden.

## Case K: a later discovery changes the selected route

Request: Review a revised explanation of Vale's Row Average. The dated record
shows independent code was created while the paper's software link was
inaccessible. An author archive was later recovered and its fixed v1 function,
settings and permissive reuse terms were inspected. It meets the requested
computation directly; no extra package is needed.

The revised note states at its code: "The independent draft came first; its
original adoption rationale was not recorded. After recovering and inspecting
v1, we reconsidered the choice and use it for the main computation. The old
function remains only as a hand-calculation companion. We statically checked
its operations against v1, but did not compare numerical runs."
Correct post-code source links, complete units and equation explanations are
supplied. The handoff does not call this an author experiment rerun.

Review whether this reassessment and its limits are supported. Do not require
an invented contemporaneous reason or blanket duplicate execution.

## Case L: the requested convention differs from the inspected code

Request: Explain the paper's finite orthogonal projection with no rescaling.
The inspected author package explicitly returns a distance-rescaled projection;
its implementation has no unscaled option. A thin wrapper could undo the
nonzero scale, and the note acknowledges that possibility. For this bounded
hand calculation it chooses an independent four-line illustration that exposes
the orthogonal basis and product directly, with a link to the author function
and explicit scale conversion. This is labelled an explanatory companion;
the author package remains the documented route for its rescaled algorithm.

The selected unit has correct provenance, operation-to-equation explanation,
editable source and post-code links. The code and conversion were inspected
statically; no execution, superiority or numerical equivalence is claimed.
The selection record predates the independent illustration and matches the
reported purpose. Review the concrete convention and role without treating
author provenance as sufficient reason to erase the illustration.
