---
name: proof-adversarial-review
description: Run an independent, adversarial multi-viewpoint review of a frozen mathematical proof, your own manuscript or someone else's paper. Seven roles (line-by-line audit, independent verification, counterexample hunting, hypothesis and dependency audit, prior-art attack, hostile referee, numerical check) get a fixed statement and no one else's verdict; findings are merged by a parent who rules on confirmed versus suspected. Report-only; it never edits the source.
---

# Adversarial proof review

Before substantive work, follow [eligibility and handoff](../research-router/references/editing-capability.md).

For each user request, follow the [required consultation](../research-router/references/consultation.md).

When author identity, voice, or preferences matter, consult the Labo workspace
[author profile](../../../profile/author-identity.md) when available. Keep
personal facts there rather than in skill text; update only explicit durable
facts or corrections from the user, or facts they ask to save, with source
context. Apply this skill's normal verification rules.

Use when a proof (a theorem and the argument for it) should be stress-tested beyond one reader,
before relying on it, submitting it, or building a reading page from it. It complements
[paper-referee](../paper-referee/SKILL.md), which owns the numbered standards for a single
referee-style audit; this skill owns running several independent attacks and merging them. It
reports; it does not rewrite, repair or certify, and the user decides what to change.

Resolve `<scripts>` to this skill's real `scripts/` directory (follow symlinks first).

## Procedure

1. **Freeze the target.** Fix the exact statement, the source files and version, and the scope
   (whole proof, or one decisive lemma). Write a short common brief as in
   [brief and report](references/brief-and-report.md).
2. **Dispatch the viewpoints** listed in [viewpoints](references/viewpoints.md), each in a fresh
   thread under the [subagent invocation contract](../research-router/references/subagent-invocation.md).
   Give each only the common brief, its role and the source paths; never another viewpoint's
   verdict, and never the producer's own checks. Start independent roles in parallel and use the
   waiting time for work that does not depend on their reports.
3. **Collect reports** in the report format. Save each to a local file as it arrives.
4. **Rule** as in [adjudication](references/adjudication.md): merge duplicates, separate confirmed
   from suspected, keep conflicting suspicions as suspicions, and record who raised what. Use
   `python3 <scripts>/findings.py validate|merge|summary` to keep the findings consistent.
5. **Repeat** only on what the findings changed, at most three rounds, and stop earlier when a
   round raises no new confirmed finding.
6. **Report** the panel, the scope each viewpoint actually covered, the findings by severity, and what
   remains unchecked. Do not edit the source; list suggested corrections for the author to accept.

## Limits to state every time

- Failing to find a gap is not a proof that there is none; say what was tried.
- Reviewers that are language models are not an expert's check or a formal proof.
- A reviewer without a shell cannot run numerical checks; record that instead of implying it did.
- The producer cannot be its own independent verifier; its pass counts as author work.
