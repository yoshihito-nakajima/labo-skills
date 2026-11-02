# Synthetic application-to-code review packet

All studies, names, sources and inspection records here are fictional. Review
only against the supplied evidence; do not browse, execute code or infer source
access. Report located findings and minimum repairs, plus any check limits.
The supplied link observations are not an actual rendered-artifact inspection.

## Request and scope

Review method explanations with code for a Japanese reading handout. The in-scope
units are `row_average`, its safe variant `safe_average`, and the background
helper `select_neighbors`. Installation commands are also displayed. Original
passages and faithful translations are in scope. The target's hierarchy is
§3 Estimator, §3.1 Neighborhood selection, §3.2 Safe averaging; Japanese titles
may translate these meanings but must preserve the numbers and levels.

## Supplied inspected primary evidence

- Vale, *Row Averaging* (2020), Algorithm 1 p.2: for positive row sum s[i],
  compute p[i,j]=W[i,j]/s[i] and output sum_j p[i,j]*f[j].
- Reed, *Safe Averaging* (2021), §2 p.3 Algorithm 2: retain exactly that update
  on positive rows; on a zero row return f[i]. This ensures a defined output;
  it does not guarantee accuracy for isolated observations.
- Pine, *Sparse Monitoring* (2022), §1 p.1: 30 stations have intermittent labels;
  the task is to estimate signal at stations. §3 pp.4–5: neighbors within radius
  r define W, then Reed's average supplies the estimates used for anomaly flags.
  Fig.2 p.6: 3 isolated stations have defined outputs using the fallback; no
  comparison measures accuracy improvement on those 3 stations. Table 1 p.7
  reports aggregate error over all 30, without an ablation of the fallback.
- Moss, *Radius Neighborhoods* (2019), Algorithm 1 p.2: include j when distance
  is less than or equal to r. Pine §3 explicitly uses this rule.

Supplied fixed-code inspection records:
- `vale-v1.py:row_average`, lines 10–14: normalize positive rows and apply to f.
- `reed-v2.py:safe_average`, lines 20–27: same positive-row expression;
  line 24 returns f[i] on zero sum. No other changed operation.
- `notes.py:select_neighbors`, lines 3–8: tests distance strictly less than r.
  This differs from Moss only at the radius boundary.
- `notes.py:row_average` and `notes.py:safe_average` independently implement
  the two cited averaging rules. No equivalence run was performed.

## Draft A

The handout begins with the three code blocks, followed by the equations. A final
application section accurately supplies Pine's problem, requirements, pipeline,
Fig.2/Table 1 results and limitations. All code blocks link there and to fixed
editable sources, and the code rows immediately follow their blocks.
`select_neighbors` is labelled "educational setup helper, so no application or
relationship explanation is needed". Its boundary rule is not discussed.
`safe_average` is labelled "another implementation of Vale, numerically
interchangeable; the improved aggregate error proves the fallback solves the
isolated-station accuracy problem". A successful synthetic constant-row run is
its only implementation validation.

## Draft B

The handout retains §3 Estimator and its two subsections §3.1 Neighborhood
selection and §3.2 Safe averaging, with faithful source passages/translations.

In §3.1, local commentary explains Pine's sparse-station task, why distances
must define which observations can contribute, and why this study is chosen
here: it makes the radius-boundary convention and its effect on connectivity
visible before the reader sees the selection code. It shows the corresponding
essential `select_neighbors` code immediately after this explanation, followed
by its identified source/link row and an operation-to-equation reading. Moss's
≤ r is contrasted with the note's < r at exactly the boundary, with consequences
for weights and possible isolation. Necessary published evidence is explained
locally with exact source locations; shared full sources only add detail.

In §3.2, the faithful translation and short explanation identify isolated stations
and the requirement to return a defined value. The commentary says why this
application belongs here: it separates definedness from prediction accuracy and
shows precisely when the zero-row branch is needed. It explains the positive-row
normalization and immediately shows that code with its source row and meaning.
It then explains the zero-row case, immediately shows the fallback code with its
source row and interpretation, and compares the changed branch against Vale.
Pine's Fig.2/Table 1 are shown and interpreted at their relevant points; fallback
accuracy is not inferred from aggregate error. Fixed-code locations on both sides
are supplied, and static inspection remains distinct from the bounded toy run.
Each subsection completes this local account before the next begins. Long full
implementations and shared evidence are linked with return routes. Supplied
artifact observations confirm those links and adjacent source rows.

The local account uses meaningful added headings: "Application task and
requirements", "Why this example here", "Positive-row normalization and code
correspondence", "Zero-row fallback and code correspondence", and "Published
results, scope and relation to Vale". The relevant headings occur at their
short explanation/code cycles, not in a long preamble. Supplied PDF-outline
inspection records this tree, with readable Japanese title equivalents and
destinations landing at each named unit:

```text
3 Estimator
  3.1 Neighborhood selection
    Application task and requirements
    Boundary convention and corresponding code
  3.2 Safe averaging
    Application task and requirements / why this example here
    Positive-row normalization and code correspondence
    Zero-row fallback and code correspondence
    Published results, scope and relation to Vale
```

Source numbers and parentage remain unchanged; added headings are clearly
identified as commentary. Not every paragraph/citation is a bookmark.

## Draft C

All application evidence, mathematical explanations, code, citations and links are
accurate. Original subsection numbers appear in the contents, but the body demotes
§3.1 and §3.2 to unnumbered paragraphs under a generic "Translation" section.
After all translations, a separate "Applications" section presents the full
problem → needs → mechanism → published results account for every method.
A final "Code" section contains the essential executable units and explanations;
all routes work and each code block has its source row. The writer claims that
correct source order and application-to-code order establish a complete reading
structure, and that hyperlinks make immediate placement unnecessary.

## Draft D

The body preserves source section/subsection hierarchy. Each passage's translation
and mathematical explanation is followed immediately by its corresponding code,
identified source row and interpretation. An adjacent application paragraph says
only "Pine uses this method, which is popular in monitoring." Bibliographic data,
reported results and variant relationships are accurate. It does not explain
Pine's need or why that example was chosen to teach this particular passage.

## Draft E

All source text, application needs, local example rationale, mathematical/code
correspondence, results/scope and relationships are accurately explained at the
correct passages. Each translation/necessary explanation leads immediately into
the corresponding essential code, source row and interpretation. However, every
added explanation is headed only "Supplement"; its individual purposes are
buried in running prose. The PDF has correctly nested bookmarks for §3, §3.1 and
§3.2, but no entries for the local application requirements, code correspondence
or operation stages. The writer claims that source bookmarks plus accurate
prose make these specific explanations directly discoverable.

## Draft F

The body and linked table of contents use the same meaningful source and added
headings as Draft B; code cycles and all substantive explanations are correct.
Supplied inspection of the actual PDF outline instead finds §3, §3.1, §3.2 and
all added entries as siblings. "Zero-row fallback and code correspondence"
points to §3.1's neighbor-selection code. The writer checked the TeX heading
commands and the contents-page links, and reports that nested bookmark
navigation passed without inspecting the outline tree or its landing content.

## Bounded production input

For a small production trial, use only this fictional passage from Reed §2:
"For a row with positive sum, divide its weights by that sum and average the
observed values. If the row sum is zero, return the value at that row."
The two-station teaching input is W = [[1, 1], [0, 0]], f = [2, 4]. It is an
independent illustration, not Pine's data or an empirical accuracy test. This
passage and the supplied evidence permit a bounded §3.2 example, not a claim to
translate an unseen full paper or reproduce a real study.

## Bounded controls

A separate response only translates two supplied sentences on a user's request,
without explaining a method or supplying method code. Another explains a proof
of a finite-set identity without a computational procedure. Evaluate these under
their own scopes; do not expand them into application searches or coding tasks.
