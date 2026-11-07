# Motivation review

Purpose: catch decks (and plans) that follow the source's order but skip why each concept
exists, and also decks whose background is so long that the audience forgets the question.
Run it on the displayed pages first, as an audience would meet them.

## Two stages, in this order

1. **Criterion-based review** (this file): fresh reviewers who are given the criteria below
   check the deck against them. Repair the findings.
2. **Blind referee** ([blind referee](blind-referee.md)): fresh referees who are told nothing
   but the audience read the repaired deck. Repair, and rerun until a fresh referee finds no
   missing bridge.

Both stages cover **every page** of the deck, in chunks, with a fresh agent per chunk. A
change to a page puts that chunk back into review. A review that covers only the pages that
were changed or only a sample is reported as partial, never as a review of the deck.

## Reviewer

An independent adversarial reviewer in a fresh context ([subagent invocation](../../research-router/references/subagent-invocation.md)).
Give it only: the deck PDF (or the page range), a neutral audience brief (who they are,
what they know, language), and the criteria below. Do not give it the plan, the
motivation cards or the conversation. Its job is to find places where an audience member
could not say why a concept is there. If no independent agent can be run, record that and
do the check yourself from the pages alone; that is not an independent review.

## Criteria

For every concept the deck defines or names (a term, a construction, an algorithm):

- **M1 Problem first.** Before the term, is there a page or a clear line stating what
  we want, on a concrete case?
- **M2 Why not the obvious.** Is it shown how the previous tool fails on that case, and
  why the obvious alternative is not the answer?
- **M3 Idea before definition.** Is the idea stated in words or a picture before the
  formal definition, and is it clear why this definition?
- **M4 Computation, then result.** After the idea, is the computation shown, and only then
  an example of what it achieved?
- **M5 Computation as published.** Is the computation shown as in the source or the
  authors' code, with credit, rather than made for the talk?
- **M6 Origin and position.** Is the page labelled with where it comes from in the
  source (section, subsection, pages), and is material from outside the source
  labelled as such, with person, publication and title?
- **M8 Roles.** On pages that present a method, can an audience member see which part is
  kept from the previous method, which part fixes the obstacle, which has another intended
  aim (explained), which is bookkeeping (quiet) and which limit leads to the next subsection
  (where such parts exist), with emphasis following that?
- **M7 Section map.** Does each section open with a page showing what came before, the
  question of the section, how its subsections relate (what limit each removes), and what
  it hands to the next section?
- **B1 Balance (too much).** Is any concept's background so long that the audience
  would lose the thread? As a guide: from the problem page to the payoff page, more than
  about four pages without a result, or background pages that outnumber the pages on the
  method, is a finding. A thin version is right for minor concepts.
- **B2 Balance (too little).** (Symbols used before their definition are caught earlier by
  `scripts/plan_symbols.py`; here judge motivation and jumps.) Is any term used before its motivation, or any jump the
  audience cannot bridge?

## Report

Numbered findings with severity, page, what an audience member could not say, and the
smallest repair (add a line, add a page, move a page, or cut). Preserve correct concise
passages and say so; a review can be clean. Report the scope inspected, whether it was
independent, and what was not checked (the mathematics, the source's accuracy).
