# Links between sections, subsections and slides

A talk is a chain of questions. Each unit says what it inherits, what is still
open and what it supplies, so that someone reading only titles, subtitles and
closing bars can recover the chain.

## Concept chains: why before what

A concept is never introduced by its definition alone. A major concept gets pages in the
order fixed in [plan format](../../paper-talk-planning/references/plan-format.md) (opening
page, why the previous tool is not enough, idea and definition, computation with its code,
what it achieved, limit and next); that file is the one authority for the order and for the
rule that computation and code share one page when they fit. Each closing bar asks what the
next page answers, and the computation covers the roles of
[inherit-new-forward](inherit-new-forward.md).

A minor concept keeps the chain thin: the problem as the subtitle, one failure on the
page, definition and result on the same page. A term never appears before the page that
shows why it is needed. Keep the balance: the chain from problem to payoff stays short
enough that the audience does not forget the question (see
[motivation review](../../paper-talk-planning/references/motivation-review.md)).

## Reopening at every subsection

The first page of each subsection opens with what it uses (the figures, formulas, inherited
result and published application, each with its source), then names its root problem by ID
and the other subsections that share it. It shows the root's shared example with the same
figure as on the previous subsections, then this method on that example (applied view),
then the example where this method's lens is most visible (specific example); the limit
example closes the subsection and opens the next one
([roots and lenses](../../reading-reference/references/roots-and-lenses.md)). It restates the problem on the running example,
even when it is the same problem as before: what this method asks, how the
previous method falls short in that respect (a picture where one exists), and the reason for
the idea, quoted from the source or its cited original with person, publication and page.
Only then the idea and the computation. The reason is never supplied from memory; where no
source states one, say so. Introduce each method only after showing the problem and
the failure of the previous approach on the running example.

## Position cue

The source section, subsection and page range appear as a tag above the title of every
page. They label the page; they do not order it. Material that is not in the source
(background from a cited original or standard theory) carries a chip `background (not in
the survey)` and a credit of person, publication and title.

## Slide to slide

- **Closing bar**: the last element of a page is one sentence: the claim just
  established, the scope of that claim (what it does not say), or the question the
  next page answers.
- **Grey subtitle** under the next title restates, in one line, the premise
  carried over, so the pair closing bar + subtitle is the hinge.
- **Titles** are claims or questions in ordinary mathematical language, not labels.
- **Turn page**: where an obstacle appears (a quantity cannot be computed, a method
  fails), use a sparse page with the question and one or two lines, then the page
  that resolves it. This is also the pacing device.
- **Step reveal**: a construction or game is shown as the same page with one more
  step each time.

## Subsection to subsection

The last page of a method states its limit as an obstacle (not as criticism); the
first page of the next method states, in the subtitle, which obstacle it removes
and what it keeps. Use the pattern: *A achieves X but needs Y; the next idea
replaces Y by Z.* Change the subsection tag so the position is visible.

## Section opener: the map of the section

Every section opens with a map page. It shows, in this order:

1. **Before**: what the previous sections settled and which of their limits this section
   takes up.
2. **Problem of the section**: the one question the section answers.
3. **Map of the subsections**: how they relate, drawn as a chain or a small graph. Each
   subsection is labelled with the limit of the previous one that it removes, so the
   audience sees why the order is what it is. Mark which subsections are major (full
   motivation chain) and which are thin.
4. **After**: what this section hands to the next one and what stays open.
5. The source's section, subsection and page range, and the navigation position.

The first page of each subsection restates in its subtitle the subsection's place in this
map (what it adds to the previous one). The last page of the section repeats the "after".

## Section to section

The opener of a section shows: what the previous section settled, the open problem,
what this section supplies, and the position in the navigation. The closing bar of
the previous section's last page carries the same open problem. When the source has
no section summary and the section ends a long stretch, add one table of questions,
answers and what remains.

## Checks

- Every closing question is answered by the title or subtitle of the next page.
- No link without an open problem; no open problem left unanswered later.
- Mark each link in the plan as stated by the source (with page) or as the speaker's.
