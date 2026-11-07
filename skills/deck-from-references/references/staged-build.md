# Staged build of slides: thin whole first, then deepen in chunks the user sets

Use for slides (and the page plan they come from). Slides depend on the user's own way of putting
the paper into words, so a small difference in thinking changes the whole deck, and the user's
understanding often moves while slides are made: slides are often how a half-understood paper
becomes understood. A deck built in one pass on a plan the user approved is wrong in many places
at once. The detailed note and the companion page follow their source closely and are built in one
pass; this rule is for slides only.

## Default

Stage the build. A one-pass build is for the case where the user says so ("build all of it") or
says they already understand the content well enough that a wrong turn is cheap; ask at the start
when in doubt ("how well do you hold this now?"). Do not start deep pages before the first
reaction.

## Gates

1. **Skeleton** (thin whole): the list of every page, section or unit in order, with one sentence each
   (what it says, what it shows). The whole is visible and nothing is deep. The user confirms or reshapes it.
2. **Chunks**: the user names the size of a chunk (usually 1 to 4 pages, or one or two sections or figure
   units). Build only that chunk, deep, and show it (for slides, a contact sheet and the pages at reading
   size). Ask two or three pointed questions (what is off from how you would say it; density; order).
3. **Reaction**: wait for it. Do not build the next chunk, and do not "fix ahead" other chunks, without it.
4. **Measure** the chunk against the example deck and the earlier chunks (`deck_audit.py --example --previous --wraps --overlaps`), and look at the rendered pages before showing it, and say in the report what was off.
5. **Record** the reactions in `REACTIONS.md` in the project (one line each: the preference, the page that
   showed it). Read it before each next chunk and apply it; revise earlier chunks and the skeleton when
   the user's understanding has moved, saying what changed.
6. **Whole check** after the last chunk: consistency across chunks, the checks of the slide skills, then the
   review its workflow asks for.

## What a chunk shows

A chunk is shown as the reader will meet it (the rendered page, the unit in the browser), with the sources
it comes from, so that the reaction can be about the thinking, not about a layout defect. Report what was
and was not looked at.

## Exceptions and limits

- An explicit instruction to build everything, or to build a named set, overrides the chunk size; say that
  the gates were skipped and that drift is likely.
- Checks (links, figure order, source tags) run after every chunk, not only at the end.
- Staging does not lower the accuracy rules of the slide skills: each chunk is as sourced and checked as the whole.
