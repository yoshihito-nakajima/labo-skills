# Step unit (supplement: the code from step 1)

One unit per step of the method, in the method's order, in the supplement after the figure
units. It lets the reader read the code from the beginning, at a pace set by words, pictures and
examples. Figure units link into it; it links back to the figures that rely on it. The order is
the reading order. A part that does not apply says so with a reason; supplements (longer
derivations, provenance details) fold.

1. **Where we are** — the step on the whole-method map, what it receives and hands on, and the
   figures and panels that rely on it.
2. **Background** — why the step is needed: the problem as a concrete picture, what was known,
   with the note's section and page.
3. **Question** — what the reader should be able to answer after the unit (reuse the plan's
   understanding check when there is one).
4. **Idea in words** — what the step does, in plain words and without symbols.
5. **Terms and symbols** — every term and symbol used later in the unit (formula, code, controls,
   figure), each in words and, where possible, as something visible in the figure. Every
   parameter bound to a control, the earlier method's included, is defined here. When the paper's
   symbol and the code's argument differ (the paper's OD is set by the code's `noise`), add a table
   *paper's symbol ↔ code's argument ↔ control on the page*, and use those same names in the text,
   the code notes and the controls.
6. **Formula** — the paper's formula with its locator, and any difference between the paper's
   text, its formula and the implementation. `n/a: reason` when the step has none.
7. **Worked example** — a few numbers the reader can check by hand, from the example data or run
   where possible, labelled by provenance.
8. **What existed before** — what the earlier method was made for and where it is weak (from the
   page's lineage section, one or two lines and a link), where it differs, and its source; its
   code is shown with the authors' code in part 11 ([comparison](comparison.md)). When none
   applies, `n/a: reason`.
9. **Selling point** — the paper's statement with locator.
10. **Before the code** — the purpose and idea restated in two or three lines, with which case of
    the formula or which sentence of the idea each marked block of code carries out.
11. **The code** — the earlier method's code and the authors' code, side by side or one directly
    before the other, coloured by the correspondence list. Above each paired block stand its three
    statements (what it does in words, where it comes from, what differs and what that changes);
    blocks of the authors' code are marked with their role; boilerplate folds. The step's block of
    the whole-code map is the 'where we are' of part 1 (same colour, link). Each parameter is marked in its line and bound to a
    control; the current value is shown beside the code, never written into it.
12. **Figure, controls and presets** — first the run's role in one line (behaviour on synthetic
    data, remake of a named panel, or for reading the code; see [figure unit](figure-unit.md)) and its
    [run card](fidelity.md#say-what-was-run). Then both methods' figures for the
    current values on the same input, side by side, drawn with the paper's encoding, and, for a
    remake, the crop of that panel. Each control is labelled with the code's argument and what it
    sets in the paper's terms, and shows the resulting value ("noise = 5 → OD = 5"). Each preset
    shows its parameter values on the button, sets the controls visibly, and says which figure to
    look at (which method, which plot, which marks) and what should change; include the default and
    values extreme enough to make the effect obvious. Where the drawing allows, highlight what
    changed from the previous setting.
13. **Reading** — see (which marks), learn (what that tells), trouble (what remains hard or what
    the next step answers).
14. **Links and limits** — note section and page, deck pages, the reproduction level and what the
    unit does not show.
