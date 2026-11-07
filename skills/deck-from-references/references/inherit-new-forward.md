# Roles of the parts of a method: kept, fixes the obstacle, other aim, tidy, limit

Following the source's order is not enough. On every page that presents a method, algorithm
or construction, the audience must see, for each part, why it is there. The names say the
intent, because "new" cannot tell an obstacle-fixing change from another important change.

## The roles

A subsection starts from an **obstacle**: the failure of the previous method on a concrete case
(the "why the previous tool is not enough" page). Each part of the new method is then one of:

| Role (label) | Meaning | Emphasis |
|---|---|---|
| **kept** (`inherited`, "従来のまま") | taken over unchanged from an earlier method; name that method | quiet: ring marker, grey; say what it means ("only the input changed") |
| **fixes the obstacle** (`fix`, "障害を克服") | the change that overcomes the obstacle of this subsection; name the obstacle it removes | most prominent: filled marker, listed first |
| **other aim** (`aim`, "別の狙い") | a change that does not overcome the obstacle but has an intended purpose (speed, scalability, a guarantee, robustness) | emphasized and explained: say the purpose and why it matters |
| **tidy** (`tidy`) | bookkeeping with no intended purpose beyond making it run (checks, symmetrization, indexing, stopping rule) | not emphasized: dimmed or elided, never numbered |
| **limit** (`forward`, "残る限界") | a limit or cost that remains and becomes the next subsection's obstacle | emphasized and tied to the next page |

Not every page has every role. Do not invent a role to fill the set; a first method has
nothing to keep; a page may have only `fix` and `inherited`.

## Rules

1. **Name the obstacle.** The page before the computation states the obstacle; each `fix` item
   says which obstacle it removes, each `aim` item says its purpose.
2. **One sentence on what the idea changes** (what is replaced in what) before the computation.
3. **Computation after the idea, result after the computation.** The order of the chain is in
   [plan format](../../paper-talk-planning/references/plan-format.md). The computation covers every role.
4. **Tie the computation to the idea.** The first line of an algorithm or code page recalls the
   idea; each item of the "look at" list names its role and where the idea appears in its lines.
5. **Emphasis follows role.** `fix` and `aim` and `limit` are emphasized; `inherited` is named and
   then quiet; `tidy` is not drawn attention to. Equal emphasis on every line is a defect.
6. **Name what is kept from.** The predecessor may be a method of the talk or outside it (mean
   shift, classical MDS). Say which; if outside the talk, introduce it on that page as background.
7. **A part that looks unused is explained** (for example: only the input of the unchanged step
   has changed).
8. **Roles are claims.** Check each against the source or the code: a `fix` removes an obstacle
   the talk has shown; an `aim` has a purpose the source or code supports; an `inherited` part is
   the same procedure as before; a `limit` is stated by the source or follows from the computation.
   If unsure between `aim` and `tidy`, ask whether the audience would miss it: if so it is `aim`.
