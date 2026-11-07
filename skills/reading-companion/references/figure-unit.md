# Figure unit (main line)

One unit per main-text figure, in the paper's order. It joins the figure's selling point to the
code selling point that produces it. Its parts, in reading order (a part that does not apply
says so with a reason):

1. **Claim** — the main-text sentence that cites the figure and the caption's statement, with
   locators, kept apart from the companion's explanation. Then, in plain words, what the figure is
   meant to show and why it matters for the paper's question.
2. **Reading** — the paper's figure cut out of the source with numbered marks, and for each mark
   *see* and *learn*, then the figure's *trouble* and *hand-off*, following the
   [reading ladder](../../deck-from-references/references/figure-reading.md). Name panels exactly
   as the paper does ("(ii)", "2C") everywhere on the page. State what each panel plots, the axes,
   colours and sizes. Read marks only from the figure itself, viewed at a size where its parts can
   be told apart.
3. **Figure selling point ↔ code selling point** — for each panel (or group of panels) that
   carries a selling point: the point in one line; the code selling point that produces it (step,
   function, lines); the focused code with the earlier method's code beside it or directly
   before it, coloured as in [comparison](comparison.md); a link to the full step unit in the
   supplement. A panel that compares with an earlier method shows that method's code the same way.
   Then **where the difference comes from**: the steps and lines (blocks of the code map) that make
   the difference the figure shows — to the earlier method, or between the conditions it compares —
   in a sentence each, with whose statement it is (the paper's, or the note's reading) and links
   to the code-map blocks. "What was run" is not enough; say which part of the code the figure's
   point depends on.
4. **Run it** — one run unit per figure, on small synthetic data (see
   [synthetic runs](fidelity.md#synthetic-runs-for-the-controls)): the authors' call shown once,
   the controls as the arguments of that call (or as properties of the data, marked so), the
   earlier method beside it on the same data with its own controls, presets that set the values
   the claim depends on, and the run card. Its role line says what behaviour to look for. The
   paper's figure carries the claim; the run shows what the code does. Its role line carries
   `values_note`: how this call's values differ from the call behind the paper's figure, and why.
   There is exactly one run with controls per figure unit. Under the run, folded, stands the
   **whole code of the functions whose arguments are the controls** (`called`: the authors' and the
   earlier method's, each function in full), with the figure's selling points highlighted and
   labelled (`sell`: ranges of that code, taken from the figure's *difference*) and the control
   lines marked with their current values. A run on the paper's data shows the same functions and
   selling points. Each *learn* of part 2
   carries a `check`: which preset to press, what to look at, and what was observed (confirmed /
   not confirmed, in the page's own words), or "rests on the paper only" with the reason. A claim
   the run does not confirm is reported as not confirmed.

   A run on the paper's data or a substitute (a remake) is optional. When present it has no
   controls (a remake that is a step unit keeps the step unit's controls, but folded), sits folded below the run as a reference for comparing with the paper's panel, and
   says how its call differs from the synthetic run's (values and why). The rest of this part
   describes both kinds. Every run says first, in one line, what it is, as one of these roles:
   - **behaviour on synthetic data** (the run with controls): "AI-created synthetic data with a
     known truth; look for <behaviour> when <argument> moves", with the truth stated;
   - **remake of a panel**: "a remake of Fig. 1 (ii) with <data>; compare <what: shape, counts,
     which points are kept>". The crop of exactly that panel stands next to the run's figure, both
     labelled with the panel name;
   - **for reading the code**: "not a figure of the paper; it shows what <parameter> does in
     <function>". No paper panel is put beside it.

   A remake is computed at the highest
   [reproduction level](../../reading-reference/references/methods.md#reproducing-the-papers-figures)
   reached, said in words ("substitute data: …", not a code such as L3), with
   the earlier method on the same input beside it. Every run has the [run card](fidelity.md#say-what-was-run)
   (calls, whose code, from control to drawing with the code re-shown, where in the method) and the
   data identity, repository and commit next to the figure. A run behind a results figure that is not one
   step of the method is kept as a run of its own (not a step unit of the supplement); a figure whose
   panels come from different data shows one run per dataset. State what does not transfer. When
   nothing can be run, say why, link the
   computation the figure tests or depends on, and point to the request list.
5. **Talk fields** (optional, for slides built from the page): `talk` = `takeaway` (one sentence), `picture`
   (the picture to show), `property` (the one-word property of the method this figure shows, such as
   reproducibility), `panels` (`show`: the panels to show; `rest`: the others, said in a sentence or left to the
   appendix; a figure is shown by panels but never skipped) and `appendix` (what stays out of the main part).
   Slides take their pages from these and from the presenter's notes; they add no claim.
6. **Presenter's notes** — the claim in two or three sentences, what to point at (the marks), the
   questions a listener is likely to ask with answers from the note, and what the figure does not
   show (the distance between the figure and the claim, as the note assesses it).
7. **Supplementary figures** — only those the main text cites where understanding this figure
   depends on them, read in the same way at that point.
8. **Links** — the note's sections and pages, the deck pages, the step units used.
