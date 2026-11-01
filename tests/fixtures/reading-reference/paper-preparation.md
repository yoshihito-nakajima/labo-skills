# Synthetic paper-preparation review packet

All authors, papers, URLs and inspection records below are fictional. Use
reading-reference to review the supplied draft against the request and supplied
primary passages. Report supported findings, minimum repairs and check limits.
Do not browse, execute code or invent access to unavailable artifacts. This packet
supplies observations about links, not real external-link tests.

## Request

Prepare Japanese close-reading and presentation notes for the whole of Brook
(2024), *Neighborhood Rules*. Include the source text, translation, explanations
and code so I can explain the methods and their relationship to earlier work.

## Supplied inspected source passages

Target Brook (2024), bibliography contains Vale (2020) only:
- §1 “Question”, p.1: estimate a local signal from nonnegative neighborhood
  weights. Sparse observations can leave an isolated row with no neighbors.
- §2 “Positive rows”, p.2: reproduce Vale's weighted average, defined only when
  row sum is positive; there is no new accuracy theorem on such rows.
- §3 “Isolated observations”, p.3: use Reed's rule that returns f[i] when the
  row sum is zero. Caption of Fig.1: left, positive row; right, isolated row.
  The text says isolation handling ensures a defined output, not improved accuracy.

Additional inspected primary passages:
- Vale (2020), Algorithm 1 p.2: positive-row normalized weighted average.
- Reed (2021), introduction p.1 and Algorithm 2 p.3: retains Vale's positive-row
  operation and adds f[i] for zero rows, motivated by isolated observations.
  Reed is not in the target bibliography.

Supplied author-code search: target paper's software page and Vale/Reed author
pages checked; no corresponding code located in that scope. This does not
establish worldwide absence. A static check of the independent function below
matches Reed's rule for nonnegative square W and matching f. No execution occurs.

## Draft being reviewed

Headings: §1 “Fast implementation”, §2 “Background”. It omits Brook's §3 and
source section mapping. It presents a two-sentence summary in Japanese, no source
passages or faithful translations. It includes Fig.1's caption translated as
“Two cases” but omits the figure and discussion of isolation versus accuracy.

“The original paper proposes a better average. It improves Vale because its
formula is different.” The text cites only Brook §3 through its bibliography.
Vale and Reed appear in a private provenance log. The writer says additional
references are unnecessary because Brook's bibliography defines coverage.

Under “original code” the draft includes:

```python
def average(W, f):
    return [sum(w*x for w, x in zip(row, f))/sum(row)
            if sum(row) > 0 else f[i] for i, row in enumerate(W)]
```

A footnote says “Written for these notes; not executed.” The only explanation
is “Python implements the equations.” No input meaning, analysis question,
operation-to-source mapping, design choices or validation evidence is given.
Vale's method is explained mathematically elsewhere with no matching code unit
or explicit route identifying the positive-row expression as its implementation.

The code links “original” to Brook's homepage and “code” to a repository default
branch. A supplied built-artifact observation finds correct bidirectional routes
between this excerpt, the full matching function, an editable bundled file and
the formal bibliography entry.

Supplied external-link observations:
- Brook's homepage returns HTTP 200 and no paper text.
- The link labelled Reed Algorithm 2 redirects to an unrelated course page.
- The code link reaches a later changed function; no fixed version is identified.
- The Vale PDF link opens the right document, but its viewer ignores #page=2.
  The draft supplies no visible page or algorithm locator.

The handoff says “All sources, links and implementations verified; complete.”

## Bounded control

A different user asks only “Translate the two supplied sentences in Brook §1.”
The response gives those sentences and a faithful Japanese translation, labelled
with §1 p.1, and makes no method, code, source-access or whole-paper claims.
Review this response under its actual request, without inheriting the larger
packet's full-paper scope.
