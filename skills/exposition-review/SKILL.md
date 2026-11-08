---
name: exposition-review
description: Run an adversarial review loop on a finished explanatory artifact (web exposition, HTML page, reading companion, lecture or reading note, long written explanation) before handing it over. Freeze the draft, have independent reviewers first rebuild its whole flow and then attack it passage by passage, triage every finding, revise and re-review until no major finding remains. Use whenever such an artifact is drafted or substantially revised; not for short chat answers or for proof certification.
---

# Review an exposition before anyone else reads it

Luna and Haiku only collect evidence here and hand substantive work to another agent: [roles](../research-router/references/editing-capability.md).

A draft written in one pass always has defects its author cannot see: passages
that make sense only to someone who already knows the argument, near topics
told far apart, a section that answers a question nobody asked yet, a term used
before it is explained. The author's context hides them. This skill puts the
draft in front of readers who do not share that context and are asked to find
fault, and makes the author answer every finding.

The producer (the agent that wrote the artifact) runs this loop and keeps
editing authority. Reviewers are read-only and never see the producer's
reasoning.

## When it applies

Run the loop before delivery for every substantial explanatory artifact:
web pages and HTML expositions, reading companions, lecture notes, reading
notes and written explanations longer than a few screens. It is part of
producing them, not an optional extra; do not hand over a first draft as
finished. A short chat answer is exempt. Mathematical correctness of a decisive
proof still goes to [math-verifier](../math-verifier/SKILL.md) or
[paper-referee](../paper-referee/SKILL.md); this loop judges whether a reader
can follow and is pulled through, and flags suspicious mathematics for that check.

## 1. Freeze the draft and write the reader brief

- Record the artifact version: file paths and a content hash or commit. For a
  web/HTML page, also produce the reader's view: the built page, or a text
  dump of the rendered text with figure captions and image files in reading
  order. Reviewers judge what a reader sees, not the generator source.
- Write a **reader brief** of at most ten lines: who the reader is and what they
  already know, what they should be able to say or do after reading, the one
  message the page must deliver, and any fixed constraints (source edition,
  required sections, length). The brief states intentions; it does not explain
  the argument or defend choices.
- Collect the **permitted sources** for fidelity (the paper edition, the note
  the page is drawn from), and list what reviewers must not see (private drafts
  for a public page, other reviewers' reports, the producer's conversation).

## 2. Flow review first

Dispatch [exposition-flow-review](../exposition-flow-review/SKILL.md) in a fresh
context with only the frozen reader's view, the reader brief and the permitted
sources. It reads the whole artifact, reconstructs the flow it actually has,
finds the breaks, and proposes a reconnected outline with the bridges between
sections.

Structure comes before sentences: a line critique of a draft whose order will
change is wasted. Decide on the flow proposal first (accept, adapt, or reject
with a reason per item), restructure, write the proposed bridges in your own
words, then freeze the new version.

Ask the user before a restructuring that changes agreed sections, the source
order of a source-aligned note, or the page's scope. Otherwise adopt changes
that the brief supports.

## 3. Line critique on the restructured draft

Dispatch [exposition-critique](../exposition-critique/SKILL.md) in a fresh
context on the new frozen version, with the same brief and sources. Use two
critics when the artifact is long or important, ideally on different models or
hosts (for example one Claude subagent and one Codex worker, through the
host's Codex delegation route when available), and do not show either the other's report. Disagreement between
critics is information; agreement is not proof.

## 4. Triage every finding

Keep a triage table for the round, one row per finding:
finding id, reviewer, located quote, decision, and what was done.

- **accept** — repair it. Repair the cause, not only the quoted sentence: if a
  term was undefined, check every later use; if a bridge was missing, check the
  neighbouring junctions too.
- **adapt** — the problem is real but the suggested repair is wrong; record
  the repair actually made.
- **reject** — only with a concrete reason the reviewer could check: the source
  says so, the brief fixes it, the reviewer misread (quote the passage that
  answers it). "I think it is fine" is not a reason. If a reviewer misread, the
  passage may still be unclear; ask whether a reader would misread it too.
- **ask** — a choice that belongs to the user (scope, emphasis, tone).

A repair never deletes citations or reference entries to make a passage
shorter or more self-contained; write the cited content into the page (the
used statement at its point of use, an annotation in the entry) and keep the
citation. Before each re-review, compare citations and reference entries
with the previous version (for web pages, `check_citations.py` in
[website-publishing](../website-publishing/SKILL.md)); a dropped entry or a
dangling citation is a blocker.

Blocker and major findings may not be left without a decision. Do not let the
number of findings decide the effort: one blocker outweighs twenty minor ones.

## 5. Re-review and stop

After repairs, freeze the next version and send it to a **fresh** critic (not
the previous thread), with the brief, the sources, and the list of changed
locations, asking it to check those locations, the junctions around them, and
the whole page for regressions. Do not send the previous reports or triage.

Stop when a fresh review returns no blocker or major finding, or after three
rounds. Run the flow review again if restructuring happened after round one.
If the cap is reached, hand over with the remaining findings listed, not as
finished.

## Report

Return the artifact first. Then, separately: versions reviewed, reviewers and
their models, rounds, the triage table (or its summary with every rejected and
open blocker/major finding listed), and what was not reviewed (unrendered
layouts, interactive behaviour not exercised, mathematics sent elsewhere).
Do not call a page "reviewed" if only the producer read it.
