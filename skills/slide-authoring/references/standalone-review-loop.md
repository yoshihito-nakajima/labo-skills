# Review loop: do the slides carry the talk by themselves?

Use when the deck must convey its argument from the frames alone: a reading deck, a deck that will
be sent around, or a live talk whose slides should survive a lost thread. The producer runs the loop
and keeps editing authority; reviewers are read-only and never see the producer's reasoning. The
triage table, the fresh re-review and the stopping rule are those of
[exposition-review](../../exposition-review/SKILL.md); this reference adds what is specific to
slides: the reviewer sees only rendered frames, and the question is what the frames alone say.

## 1. Freeze the deck and the reader's view

- Record the version (source path and hash or commit) and build the PDF. The **reader's view** is the
  rendered frames in order, as images with a text dump per frame. It excludes speaker notes, the
  script, the source files and the producer's conversation: the point is to test the deck without
  the speaker.
- Write a **brief** of at most ten lines: the audience and what they know, the time, the one message
  the deck must deliver, what the audience should be able to say afterwards, fixed constraints.
  State intentions only; do not explain the argument.
- List the permitted sources for fidelity checks, kept for the critic and withheld from the cold
  reader.

## 2. Cold read (frames only)

Give a fresh reader the reader's view and the brief, nothing else. Ask for, per frame in order:

1. the claim the frame makes, in one sentence of the reader's own;
2. the first thing a viewer would still ask (the missing bridge), and whether the next frame answers it;
3. whether the frame repeats an earlier one, and what the repeat adds.

Then, from the frames alone, the reader writes the message of the whole deck and what they would
tell someone else afterwards. A mismatch with the brief's message is a major finding, whatever the
individual frames look like. The reader also lists terms and symbols used before they are defined
and frames whose point they could not recover.

## 3. Flow review, then critique

- Dispatch [exposition-flow-review](../../exposition-flow-review/SKILL.md) on the same reader's view to
  rebuild the actual flow of the deck, the breaks and the scattered or repeated topics. Decide on its
  proposal first and restructure before any line-level work.
- Then dispatch a slide critic (a fresh context; two critics on different models when the deck is long
  or important, each unaware of the other's report) with the reader's view, the brief, the permitted
  sources and the [slide standards](slide-standards.md). Ask for numbered `S` findings with severity,
  frame number, visible evidence and the smallest repair, plus one concise correct frame as a control.
  Include density (a frame that cannot be read in the time it will be shown), claims that need the
  speaker to be understood, and figures whose reading is not on the frame.

## 4. Triage, repair, re-review

Triage every finding as in exposition-review (accept, adapt, reject with a checkable reason, ask). Repair
the cause across the deck: a term undefined at one frame is checked at every later use; a missing bridge
is checked at the neighbouring junctions. Do not repair a repeated frame by deleting the content the
audience still needs; keep the stronger statement once and make the later frame add something.
Freeze the new version and send it to a **fresh** reader and critic with the changed frames listed; do not
send earlier reports. Stop when a fresh round returns no blocker or major finding, or after three
rounds, and hand over with the open findings listed.

## Report

Return the deck first, then separately: versions and reviewers (and models), rounds, the triage
summary with every rejected or open blocker and major finding, and what was not covered (animations,
live demonstrations, the speaker's delivery). A deck is not "reviewed" if only the producer read it,
and the loop does not judge the mathematics: send decisive claims to
[math-verifier](../../math-verifier/SKILL.md) or [paper-referee](../../paper-referee/SKILL.md).
