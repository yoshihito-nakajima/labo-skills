# Blind referee

The last check of a deck, run after the criterion-based [motivation review](motivation-review.md)
has been repaired. It answers one question: can someone who knows nothing about this talk
follow it, page by page, and say why each thing is there?

## Setup

- **Fresh and empty.** Every blind referee is a new agent with no history
  ([subagent invocation](../../research-router/references/subagent-invocation.md)). It gets
  only: the pages (render at 120 dpi or more, or give extracted text together with the page
  images; never tiny images), and one sentence naming the audience (for example
  "mathematicians who do not know the data-science literature"). It does not get the plan,
  the rubric, the role names, the sources, this conversation, or any earlier review.
- **Whole deck.** Every page of the deck, in order, is read by some referee. Split into
  chunks of at most about 16 pages; give each chunk the previous chunk's last page for
  continuity. A chunk may not be skipped because it was "unchanged".
- **Both languages** only for layout; the content referee reads one language.

## What the referee does

1. Read the pages in order. After each page write one line: what this page says, and the
   question it leaves open. Mark `STUCK` where it cannot say why something is there.
2. At the end of each subsection (the referee decides the boundaries) answer in its own
   words: what problem is being solved; why the idea looks natural; what is kept from the
   earlier method and what is changed; what remains. Where an answer cannot be given, name
   the first page where the missing bridge should be.
3. List any claim it doubts, any figure it cannot read, any page it finds too dense, and
   what it would ask the speaker.
4. Do not rewrite slides and do not judge mathematics beyond what is visible.

Undefined symbols and forward references are not the referee's job: the plan has
already passed `scripts/plan_symbols.py` (see [plan format](plan-format.md)). If a
referee still finds one, fix the plan entry first, then the page.

## After the referee

Repair each STUCK, then rerun fresh referees on the affected chunks until a fresh referee
reports no STUCK on a bridge. Report what was run, which pages each referee read, how many
rounds, what was repaired, and what the referees could not judge (accuracy against sources
is not theirs to judge).

## Lessons for the next round

- A fresh referee still finds new gaps every round; stop when the findings are only
  density, small figures or code-for-analysts taste, and report those as open, not as clean.
- Referees repeatedly stuck on: symbols used before they are defined on the same page,
  forward references to later sections, and a formula quoted without the one-sentence
  reason it takes that form. Define on the page, with the source page.
- Fixed-height flow boxes overflow silently (no overfull warning): render the pages
  and look at every box after adding text; move long explanations to a line below.
- Added text must not be longer than the page it joins: split into a new page rather
  than shrinking text below the size rule.
