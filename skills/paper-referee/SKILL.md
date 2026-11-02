---
name: paper-referee
description: Rigorously audit mathematical papers, decisive proofs, section openings and exposition against numbered criteria, actively testing claims and hypotheses. Report evidence-based findings without rewriting; not for slides or lecture notes.
---

# Mathematical paper referee

Before substantive work, follow [eligibility and handoff](../research-router/references/editing-capability.md).

For each user request, follow the [required consultation](../research-router/references/consultation.md).

When author identity, voice, or preferences matter, consult the Labo workspace
[author profile](../../../profile/author-identity.md) when available. Keep
personal facts there rather than in skill text; update only explicit durable
facts or corrections from the user, or facts they ask to save, with source
context. Apply this skill's normal verification rules. For author-blind
reading, defer profile access until the blind review record is complete.

Read [numbered standards](references/standards.md). For English prose or
typesetting review, also read [English conventions](references/english-style.md).
Infer the paper, audience and requested scope from the task. Default to a
mathematician outside the immediate specialty. A section-only request stays
local; a whole-paper request must account for the whole paper, even when read
in parts. Reviewing does not authorize rewriting, building, or publishing.

Resolve `<labo-script>` below to the absolute `../../scripts/labo.py` path
relative to this skill's **real directory** (follow symlinks first). Do not
use a globally installed `labo` command or infer the workspace from the
shell's current directory. The launcher uses its private Git superproject;
pass `--workspace /absolute/path/to/labo` to override it or when using a
standalone policy checkout.

The `paper map` and `paper section` commands below apply to the standard Labo
TeX layout with `main.tex` and `sections/`. For Markdown, a single TeX file or
another layout, inspect the actual source and heading/include order directly
with line locators; for PDF-only input use page/statement locators. Preserve
the existing layout while applying the same local-reading and evidence rules.

## Adversarial mathematical audit

Treat the assigned claims as obligations to withstand attempts at falsification.
Prioritize the central theorem and its weakest load-bearing inference over
editorial polishing. Follow the decisive argument to its actual inputs, even
when several routine calculations around it are correct. Within the requested
scope, actively test:

- Every cited theorem's hypotheses on the actual objects and substitutions;
  the exact prior-art statement and the claimed new delta.
- Quantifier order, dependence of choices/constants/subsequences, uniformity,
  and whether a pointwise assertion was promoted to a simultaneous one.
- Empty, zero, endpoint, degenerate and extremal cases relevant to the claim;
  limit/interchange, compactness, attainment and existence steps.
- Hidden standing assumptions, definitions that import the conclusion,
  circular lemma reuse, and changes of objects or conventions during the proof.

A counterexample must satisfy the stated hypotheses and contradict the exact
conclusion. An apparent proof gap requires the missing inference and its
consequence identified at a precise passage. Keep a demonstrated defect,
a plausible concern needing a named check, and an unavailable check distinct.
Do not promote suspicion to refutation, or the ability to imagine a repair to
a passed proof. When an adopted dependency graph exists, inspect affected
edges against the source; acyclicity alone cannot establish complete extraction.

Keep blockers explicit and first in the report. State the affected claim,
downstream consequence and minimum obligation for resolving each finding.
Do not silently supply a new lemma, missing proof or stronger hypothesis and
then judge the manuscript as if it contained that repair. A requested review
remains report-only. Use direct, exact criticism of the mathematics and text;
avoid insults, theatrical hostility, compulsory praise and criticism quotas.
If attempted stress tests reveal no supported defect, say what was tested
and what remains unchecked rather than manufacturing one.

## Review protocol

1. Fix the source version and scope. If the abstract is in scope, read it
   alone first and record what question, result and significance are recoverable.
   Keep research plans, positioning memos, author explanations and earlier
   reviews out of the initial reader assessment; they can inform subsequent
   evidence checks.
2. For a paper-wide or openings-only review, run
   `python3 <labo-script> paper map --paper <slug> --format json`.
   It follows literal `main.tex` inclusions and reads only section openings
   up to `% LABO:INTRO-END`. Record the argument and dependency route those
   openings actually convey, including what remains unclear. Unsupported
   TeX inclusion needs explicit resolution, not a guessed manuscript order.
3. Read each assigned section with
   `python3 <labo-script> paper section --paper <slug> --name <NN-slug>`.
   Reconstruct its claim from the visible text before following signposted
   dependencies. Record the first missing object, relation or inference and
   any later recovery separately. A precise usable reference can suffice;
   an expert's ability to invent a missing bridge cannot.
4. Check disputed mathematics and attribution against the relevant proof,
   Lean declaration or exact source passage. Distinguish a demonstrated
   defect, a concern, and unavailable evidence. For verbosity, identify what
   a deletion, replacement or relocation preserves; do not recommend cuts
   from word count alone. Retain clear, economical passages.
   When mathematical terminology, symbols or conventions are in scope, run
   the [corpus-backed terminology audit](../reading-reference/references/terminology-audit.md)
   after the initial reader assessment. Match actual types and roles to
   definitions/formulas on inspected source pages; distinguish undefined role
   labels and semantic mismatches from coherent alternatives or preferences.
   For a whole-paper/submission review or in-scope novelty, lineage or notation
   comparison, apply the required
   [positioning investigation](../reading-reference/references/research-positioning.md)
   after the initial reading. Inspect the memo and actual primary evidence,
   search unresolved relevant leads, and check freshness when submission is in
   scope. Judge the paper's claims, not whether a particular memo filename exists.
   Report material source gaps without inventing novelty or treating an unchecked
   concern as a refutation. Local editorial reviews do not start a field survey.
5. Return findings with **rule ID, severity, passage/line, evidence status,
   evidence, consequence, and smallest sufficient repair obligation**. Order
   them by consequence for the assigned use. State the version, sections and
   dependencies actually read, stress tests attempted, and remaining scope.
   Mention effective passages when that helps preserve a working choice;
   a positive example is not a required counterweight to a blocker. A clean
   local reading is not a correctness or whole-paper certificate.

## Optional durable review record

When the user asks to save a review or the workspace already uses scoped
records for this task, follow the owning
[evidence protocol](../research-management/references/evidence.md). Capture
the actual inputs with `evidence snapshot` before reviewing; proof and writing
records have different scopes. For a TeX manuscript, the optional
[scope diagnostic](../research-management/references/evidence-scope.md) helps
identify literal inputs omitted from that selection; unresolved dependencies
still require inspection, and the diagnostic never expands a snapshot. The
snapshot command emits only a pending record. Keep
catalog verdicts and earlier records out of an independent reader's initial
brief; a coordinator can capture their hashes without supplying their contents.

After the real review, record the actual verdict, reviewer, date, and report
hash without changing the captured inputs. If the inputs changed during the
review, recheck the affected scope instead of refreshing an old pass. State
single-context versus genuinely independent reading accurately. Never invent
owner confirmation. A report-only task does not authorize manuscript edits,
approval promotion, or new persistent files merely to satisfy this protocol.

## Optional independent reading

If a fresh reader is requested or needed to test an accessibility concern,
use an available isolated agent with only the frozen artifact and neutral
reader brief. It reports understanding and first confusion before proposing
repairs; do not supply the intended story, prior findings, or author answers.
Compose the assignment for the task; no saved role or model is required.
Without fresh isolation, label the result a local reading, not a blind review.
`paper map` and `paper section` load complete openings/sections: they do not
establish paragraph-by-paragraph prefix isolation. If staged reading is explicitly
requested, follow [staged sessions](references/staged-reading.md): a coordinator
uses `paper reading start/next/observe/status`, exposing only each cumulative
prefix to the fresh reader. Record initial understanding and first confusion
before the next exposure; append later rescue separately. The session tool does
not supply process isolation or certify independence, and creates persistent
private records only within the authorized task. Check a rendered artifact
when making visual claims. Subsequent repairs and rechecks follow the user's
scope; a report-only review does not start an automatic revision loop.
