# Comparison with the earlier method

Used inside figure units and step units whenever the paper inherits from, or compares with, an
earlier method that has code. The reader should see at once what was kept and what was changed.

## Placement

The earlier method's code is shown in full (not folded), verbatim, with repository, commit,
licence, file and lines and the cited source of the method. Put it beside the authors' code when
the page is wide enough; otherwise directly before it, so the two are read one after the other.
Restate in one line, above both, what the two pieces of code do on the same input. The page's
lineage section has already said what the earlier method was made for and where it is weak; the
comparison is read as the authors' answer to that weakness.

## Correspondence list

Pair line ranges of the two excerpts. Each pair says, in words, three things:

1. **What the code does** — the operation in plain words, for a reader who does not read the code
   ("sets OD and TD as percentiles of the local density LD"; "connects the end states by shortest
   paths on the density-weighted graph"). For a changed pair, say what each side does.
2. **Where it comes from** — "inherited from the plain kNN method (Roe 1999; `older.py` L4–8)", "changed
   from the plain kNN method", "added by the authors", "not used by the authors".
3. **What differs and what that changes** — the difference in the operation and its effect on the
   output (which points are kept, how many branches, how much runs vary); "no visible effect on
   the example data" when so.

Take them from the note's code-block notes. The relation below and its colour only summarise
item 2; a pair that gives a relation without items 1 and 3 is incomplete. The three statements
stand directly above the paired lines in both code panels, as well as in the list, so the reader
learns what a block does where it is shown.

| Relation | Meaning | Colour |
|---|---|---|
| same | the authors keep the earlier method's operation (possibly with other names or units) | green |
| changed | the authors change it; say how, and its role: fixes the obstacle, another aim, or bookkeeping ([roles](../../deck-from-references/references/inherit-new-forward.md)) | orange |
| only in the authors' code | added by the authors; give its role | grey |
| only in the earlier code | dropped or not used by the authors | grey |

The colour is the same in both code panels, in the list and in the figures: where the drawing
allows, the data points or parts a `changed` pair affects are drawn in its colour in both
methods' figures. Every marked block of the authors' code has a pair or an `only` entry; a
`changed` pair whose effect cannot be seen on the example data says so.

## Parameters and runs

The earlier method gets its own parameters with defaults stated in its code or paper, its own
grid (including values that make its behaviour obvious) and its own presets, labelled the same way
as the authors' ones: the code's argument, what it sets in the paper's terms, and the resulting
value; when its argument corresponds to an authors' one, say which. When its parameters
correspond to the authors' ones, offer a switch that links the two sets of controls. Run both on
the same input and show both figures side by side, never only as a toggle. When their random
draws cannot be aligned (different languages or generators), compare what does not depend on
the draw (frequencies, curves, invariants) and say so.
