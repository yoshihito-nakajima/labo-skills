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
The user wants a complete main explanation and a code collection for lookup/use,
not a second copy of the entire handout. A source index may accompany them.

For this review fixture, required supporting-paper passage pairs are supplied
and correctly placed in Draft B; other drafts inherit them unless stated otherwise.
Use the separate [supporting-source fixture](supporting-source-reading.md) to test
actual excerpt/translation fidelity. The evidence summaries below are not
themselves verbatim quotations.

## Supplied inspected primary evidence

- Vale, *Row Averaging* (2020), Algorithm 1 p.2: for positive row sum s[i],
  compute p[i,j]=W[i,j]/s[i] and output sum_j p[i,j]*f[j].
- Reed, *Safe Averaging* (2021), §2 p.3 Algorithm 2: retain exactly that update
  on positive rows; on a zero row return f[i]. This ensures a defined output;
  it does not guarantee accuracy for isolated observations.
- Pine, *Sparse Monitoring* (2022), §1 p.1: 30 stations have intermittent labels;
  the task is to estimate signal at stations. §3 pp.4–5: neighbors within radius
  r define W, then Reed's average supplies the estimates used for anomaly flags.
  Plate 1 p.2 (supplied schematic stand-in for a fictional field photograph):
  two station groups lie across a gap, with a lone station beyond the radius r.
  Its caption identifies circles as measurement stations, a radius disk as the
  neighborhood and a dashed edge as a distance exactly r. Fig.2 p.6 repeats this
  layout and colors the output values, so it shows both input context and results.
  Fig.2: 3 isolated stations have defined outputs using the fallback; no
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

Supplied scoped implementation-search record:
- The Vale paper's software note and named project page were checked; `vale-v1.py`
  was located and `row_average` inspected. Its page states no redistribution
  terms. The file was not executed in the handout environment.
- Reed's supplement index and archive were checked; `reed-v2.py` was found in
  member `src/reed-v2.py`, and `safe_average` was inspected. The archive permits
  linking but gives no stated redistribution terms. It was not executed.
- Moss gives no software pointer. The named author page, supplement index and
  repository search were checked; no corresponding implementation was located
  within that scope. This is not evidence that none exists.
- `notes.py` was written before this scoped search. After inspection, the handout
  retains its functions only as adjacent teaching code because they expose the
  three operations separately; Vale/Reed remain the fixed implementation
  comparison sources, not the claimed executed route. The only run was the
  stated constant-row toy. No Pine data, author-code equivalence or reproduction
  run was performed. The missing reuse terms and Moss implementation remain open.

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
selection and §3.2 Safe averaging, with faithful source passages/translations at the end of each owning subsection.
Each preceding correspondence maps the introduced objects and computations to
that subsection's exact source definitions and steps before the original is read.

Before any method code in §3.1, the commentary displays Plate 1 and Fig.2,
their captions and the supplied key. It explains what a station measures, the
gap, the radius disk and the boundary edge before introducing W. Fig.2 is first
read for its station layout; its output colors are revisited after code. The
reader can see why some stations have no contributors. These existing visuals
are retained as visible context rather than reduced to a sentence or a link.

In §3.1, local commentary explains Pine's sparse-station task, why distances
must define which observations can contribute, and why this study is chosen
here: it makes the radius-boundary convention and its effect on connectivity
visible before the reader sees the selection code. It explains the input points,
distance comparisons, construction of neighbor IDs and output, then displays the
complete selected `select_neighbors` function with its necessary imports/helpers.
Its identified source/link row follows. Only then does the walkthrough pick out
the relevant operations, retaining the full function's line identities. Moss's
≤ r is contrasted with the note's < r at exactly the boundary, with consequences
for weights and possible isolation. Necessary published evidence is explained
locally with exact source locations; shared full sources only add detail.

In §3.2, Plate 1 and its explained key are shown again as the method's application
context, so this unit is readable without reconstructing §3.1. The preparatory
explanation identifies isolated stations
and the requirement to return a defined value. The commentary says why this
application belongs here: it separates definedness from prediction accuracy and
shows precisely when the zero-row branch is needed. It derives the positive-row
normalization, identifies the zero denominator at the isolated station, and
extends the rule by returning that station's measured value. Before detailed
excerpts, the reader is shown the complete selected averaging functions for the
versions discussed below, with necessary dependencies and an explanation of
inputs, row-sum calculation, branching and output. The two branches are shown as
one complete function with its source row; the subsequent interpretation picks
out operations from this already introduced unit. That reading
traces `s == 0` to the empty neighborhood of the lone station already shown, and `return f[i]` to a defined
output without division by zero. This fits the need to supply an estimate at
every station, but does not improve that station's accuracy by itself. It then
compares the changed branch against Vale. Positive normalization and the fallback
remain stages of one argument; each does not restart five generic headings.
Pine's Fig.2/Table 1 are shown and interpreted at their relevant points; fallback
accuracy is not inferred from aggregate error. Actual matching excerpts from the inspected author releases are displayed on
both sides with fixed-code identities, original line numbers and immediate source
rows. The prose maps the shared branch and changed boundary operations to those
visible lines. Static inspection remains distinct from the bounded toy run.
Each subsection completes this local account before the next begins. Longer
surrounding modules and shared evidence are linked with return routes; the
selected functions' complete first display remains in the local account. Supplied
artifact observations confirm those links and adjacent source rows.

Across these short local cycles, §3.1 and §3.2 also state the complete scoped
search record: each checked pointer/page/archive and fixed version, whether it
was found and inspected, the fact that `notes.py` preceded the search, why it
was retained after reopening the choice, the unperformed source-code and Pine
reproduction runs, the bounded toy-run status, unknown redistribution terms and
the unresolved Moss search. The relevant Pine question, requirements, pipeline,
Fig.2/Table 1 reading, code correspondence and Vale/Reed/Moss differences occur
at the step where each matters, so this local account is complete without using
the later code collection.

After the complete main sequence, a code collection groups the three implemented
operations for lookup/use. It includes editable units and required helpers,
input/output meanings, equations and branch conventions, environment and entry
commands, the bounded toy input/result status, provenance, reuse limits and
links to the fuller local application/comparison/search accounts. It does not
repeat the main original/translation or all Pine figures and application prose.
Its entrance states that scope. Shared content supplies matching versions and
status without maintaining a second independent account. Every main subsection
advances from its translation to the next source unit without a duplicate.
Supplied observations confirm separate main/code bookmark subtrees and matching
return links. The common bibliography is last, with citations beside retained
claims. Source headings name the subjects before Background; each code block
has a method/implementation label and an immediate identified source row.

The added account uses the fixed roles Background, Obstacle,
Method/implementation, Fit/limits, Comparison, Execution status, and
Implementation search, in that order, once for each complete main method unit.
The code collection uses its declared operational scope. Within Method/implementation in §3.2, positive
normalization and the zero-row branch remain one connected computation.

"Obstacle | An isolated station leaves the average undefined" takes up the
station layout shown in Background. "Method/implementation | Extend the weighted
average to an empty neighborhood" opens: "The isolated station has no contributing
weight, so dividing by the row sum cannot give its output. We keep the normalized
average where that sum is positive and retain the station's measured value where
it is zero." Its derivation and one code unit follow, with the source row.
"Fit/limits | Every station gets a value, but accuracy is still untested" returns
to that obstacle and the limited evidence. "Comparison | Reed changes only
Vale's zero-row behavior" takes up this result to compare the unchanged positive
branch and changed domain. The source passages retain their order and wording;
these titles and bridges are added commentary.

Supplied outline observations give the following subtree for the two source subsections, with Japanese
equivalents of both title parts and destinations landing at the named content:

```text
3 Estimator
  3.1 Neighborhood selection
    Background | Sparse stations require a neighborhood rule
    Obstacle | A radius boundary can exclude a contributing station
    Method/implementation | Select distances strictly below the radius
    Fit/limits | The rule selects contributors but may leave empty rows
    Comparison | Moss includes the boundary that the teaching code excludes
    Execution status | Toy checks do not reproduce Pine's station study
    Implementation search | Moss code remains unlocated within the scoped search
    Source correspondence | Match the radius convention to the source definition
    Original/translation | Read the target work’s identified neighborhood-selection passage
  3.2 Safe averaging
    Background | Sparse stations need an estimate even across the gap
    Obstacle | An isolated station leaves the average undefined
    Method/implementation | Extend the weighted average to an empty neighborhood
    Fit/limits | Every station gets a value, but accuracy is still untested
    Comparison | Reed changes only Vale's zero-row behavior
    Execution status | The teaching run does not reproduce Pine's station study
    Implementation search | Retrieved Vale and Reed code leaves reuse terms unresolved
    Source correspondence | Match positive and empty rows to the source branches
    Original/translation | Read the target work’s identified safe-averaging passage
```

Source numbers and parentage remain unchanged; added headings are identifiable as
commentary. The role names are the same in §3.1 and §3.2; their concrete points
reflect the different operations. Not every paragraph or citation gets a bookmark.

The code subtree identifies operations, input/output contracts, use instructions
and status, with links to corresponding main units. It does not repeat all seven
main roles. This supplied observation is not an actual rendered-PDF inspection
by the reviewer; evaluate its scope separately from the complete main account.

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
all added entries as siblings. "Method/implementation | Extend the weighted average to an empty neighborhood"
points to §3.1's neighbor-selection code. The writer checked the TeX heading
commands and the contents-page links, and reports that nested bookmark
navigation passed without inspecting the outline tree or its landing content.

## Draft G

The complete local route is identical to Draft B, including its distributed
application evidence, full factual search/adoption record and execution limits.
The later “Source index” contains only source identities and links back to
§3.1/§3.2. It promises lookup only. The usable code collection is unchanged.
Its writer says this index need not repeat the detailed explanation/search log.

## Draft H

The code collection is identical to Draft B's collection. In §3.1
and §3.2, the local route includes the faithful translation, corresponding code
and one-sentence summaries, then links away for Pine's exact results,
the detailed implementation-search/adoption record, execution status,
consequential method differences and unresolved limits. Its writer says the
bookmark and return link make the local route complete enough.

## Draft I

Draft B's text is retained, and markers say application → obstacle → code →
fit → comparison. The generator classifies every figure as a result and moves
Plate 1 and Fig.2, with their captions and explanations, after all method-code
blocks in the main route. Before code there is only a prose summary of the station
task. All figures, source rows, bookmarks and links are present and marker-order
checks pass. The writer calls this equivalent to Draft B because nothing was
deleted from the file.

## Draft J

The main route shows Plate 1 before code, but replaces Fig.2's station-layout panel
with a link to later results. They state that a result figure cannot belong in
the application introduction, even though its radius disk and boundary edge
are used without explanation in the first selection-code walkthrough. The
remaining context and all implementation-search details match Draft B.

## Draft K

The material contains every item of Draft B, including all visuals. The writer
splits normalization and the fallback into six tiny fragments, each with five
identical headings. Each new application paragraph restarts Pine's overall task;
each fit paragraph says only that its variable "is useful and meets the task".
The reader is never shown how a zero row corresponds to the displayed isolated
station or why the branch returns a defined value. Token/length and order checks
pass. The writer treats the many cycles as stronger evidence of completeness.

## Draft L

The local route is Draft B. A new “Background only” view removes target-paper
original/translation and code but also removes Plate 1 and Fig.2. It retains
explanations of the radius disk and boundary edge referring to "the figure above",
with links to the main route in place of visible figures. It claims independent
continuous reading. The requested code collection remains usable.

## Draft M

The main route is Draft B. The generator retains an additional copy of all
source units, explanation, code and original/translation with no explicit request
for that duplicate, claiming that two complete reading routes are mandatory.

## Draft N

The main route is Draft B. Its “Runnable code collection” contains excerpts only;
the helpers and imports are absent, and an entry command names an omitted file.
It removes input shapes and unexecuted-status notes, claiming the links to the
main explanation make this usable without further assembly.

## Whole-before-part controls

Two previews establish the station task and zero-row obstacle correctly, explain
the branch's specific benefit and retain working source/code links. Preview P
starts with an isolated fallback branch; only after its walkthrough does an
appendix show the complete function. Preview Q first explains input rows, row
sums, the positive/empty branches and output, displays the complete selected
function and required imports/helpers, then picks out the fallback using matching
line numbers. Neither preview prints unrelated repository modules. Compare their
reading order, identify the first missing prerequisite and give a minimum repair.
Do not treat P's later completeness or a new roadmap alone as the repair.

## Preview control: presence without an explanation of fit

A one-method preview correctly identifies a zero denominator as the obstacle,
displays the two-branch safe-average code and its equation, then moves directly
to a limitations section. A table maps the branch to the equation but never
explains why returning the observed center value gives a defined output at that
same isolated station. The displayed code path is plain text; the only live link
opens the paper homepage. The author reports that compilation and all-page
render inspection succeeded. Evaluate whether this is ready for a content trial
and identify the smallest repair within the one-method scope; do not require a
larger handout or new empirical accuracy study.

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
