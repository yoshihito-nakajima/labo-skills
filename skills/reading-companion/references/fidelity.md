# Fidelity: where the numbers come from

## Default: the authors' code on a parameter grid

For each step choose a few values per parameter (a grid), run the authors' code at every
grid point in an isolated environment, and embed the results. The controls move between grid
points, so every figure on the page is an output of the authors' code. Record for each result
file the script, the authors' commit, the data, the random seed and the date. Keep grids small
(the page must stay small): a few values per parameter, and subsample points for drawing only.

Choose the grid so that the effect can be seen: include the default, the values the paper or
the code uses, and on each side a value extreme enough that the change is obvious in the figure
(for example the value that switches a step off, or one that overdoes it). Mark such values as
added to show the effect, not as recommended settings. When the code draws random numbers, use
the same seed at every grid point so that a change between grid points comes from the parameter
and not from the draw, and say so on the page.

The earlier method is run the same way, on the same input, with its own published code when that
code exists, over its own parameter grid ([comparison](comparison.md)); otherwise say which
implementation was used and label it.

## Compute budget: understanding, not exact restoration

The page serves understanding, so the runs are sized to be quick to make and to redo: aim for
about **1 minute** per run (one result file), and never more than **5 minutes**.

- **Estimate first.** Time one run on the real input, or a small input, and scale it (cost often
  grows with the square of the number of cells or nodes: graph distances, scoring of tree pairs).
  Do not start a run whose estimate exceeds 5 minutes.
- **Cut in this order:** the number of repeated runs (100 → 10 → 5), then the number of cells kept
  (a lower downsampling target), then the grid. Keep what the figure's claim needs (the shape of
  the trees, how much they vary, the direction of a difference to the earlier method).
- **Say it.** Every result file records `runtime_seconds` and `scale_down` (what is smaller than
  in the paper: cells, runs, grid; empty if nothing); the page states it with the data and in the
  limits ("fewer than the paper: n cells, m runs").
- **Run long jobs in the background** and watch them: CPU use and the output files' modification
  time show whether a job is working or stuck.
- **Exception.** When the aim is to match the paper's numbers (level L1 comparison), ask the user
  for the time first.
- A result already made over budget may be kept if it is marked as over budget with its runtime.

## Synthetic runs for the controls

The paper's figure shows what the paper showed; the page's controls are there to let the reader
feel what behaviour the code produces, so they need data small enough to switch at once. Every
control on the page therefore lives on small synthetic data (the authors' own synthetic data when
they provide some, otherwise AI-created data): one run unit per figure. Runs on the paper's or
substitute data are optional remakes without controls, folded as references. AI-created data are
used when the user has agreed (record the wording and date in the plan), under these conditions:

- The code that runs is the authors' (and the earlier method's) own, unedited (compatibility shims
  only). Only the data are made by the page's author.
- The data are small (around 600 points), have a known truth (say what it is), and are labelled
  "AI-created synthetic data" with the generating script. They never stand in for a missing paper
  resource.
- Controls: only the arguments the figure's claim depends on, on a small grid (each grid point
  within about 10 seconds, the whole experiment within the 5-minute budget). The call is the same
  function the paper's figure used; when its values differ from the paper's (because the data are
  small, for example the code's own rule for fewer than 1,000 cells), say which and why.
- Present the earlier method and the authors' method on the same data and controls; report what is
  observed, including when the claim is not confirmed.

## Which data: the reproduction level

Run on the authors' data when it can be obtained; otherwise obtain the same data from its primary
source, or use a substitute dataset of the same kind, under the levels L1–L4 and the labelling
rules of [reproducing figures](../../reading-reference/references/methods.md#reproducing-the-papers-figures).
Every result file records its level, the data's identity (source page, accession, hash,
preprocessing) and the figure and panel it corresponds to, with what does not transfer. What would
raise a level goes into the [request list](../../reading-reference/references/resource-ledger.md#request-list).

## Say what was run

Next to every figure the page computes, a run card states what produced it (and, folded under
it, the whole code of the functions the controls belong to, selling points highlighted):

1. **Calls** — the calls actually executed, as code: which function at which commit, on which data,
   with which arguments, how many times, in which order (for example
   `lib.neighbour_graph(points, k, boost)`, `method.py` L4–10, once per grid point).
2. **Whose code** — each call marked as the authors' code, the earlier method's code, or AI-written
   driver code (the script that loads data, loops over the grid, repeats a call to count
   frequencies, or converts outputs for drawing).
3. **From control to drawing** — for each control: the argument it sets, the line of the function
   where it acts (re-shown, highlighted, with the current value), the output it changes, and what in
   the figure draws that output (for example "noise → `noise` → L53 sets OD → L61 gives P = 0 below
   OD → not in `down_ind` → grey ring").
4. **Where in the method** — which steps of the whole-method map and which panels of the paper the
   run executes, and which it does not ("not run here").

The relevant lines of the authors' code are re-shown inside the run block, next to the figure, not
only elsewhere on the page.

## Re-implementation only with a parity record

A continuous control that the grid cannot give may use a small re-implementation (for example in
JavaScript), labelled `AI re-implementation`. It needs a parity record: the same inputs run
through the authors' code and the re-implementation, the largest difference and the tolerance.
A re-implementation without a passing parity record is not shown. Running the authors' Python in
the browser (Pyodide) is heavy and is used only with the user's permission.

## Provenance labels

`paper` (the paper's text, figure or number), `author code` (verbatim excerpt),
`author-code run` (grid result, with its reproduction level), `earlier-method code` /
`earlier-method run`,
`AI re-implementation`, `speaker's` (the companion's own explanation). AI-written code and its
results are never presented as the authors' or the user's own.

## Licences

Show the licence of every code excerpt next to it. Paper figures are cut out of the source,
unaltered, with locator. The companion is private; showing excerpts in it does not license
redistribution.
