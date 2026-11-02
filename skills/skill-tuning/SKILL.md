---
name: skill-tuning
description: >-
  Tune a skill through work on a concrete artifact, produce a local preview,
  and iterate from the user's feedback before finalization or source sync.
  Use when the user wants to shape both the skill and its result together;
  use skill-creator for standalone skill authoring.
---

# Tune a skill through a real artifact

Before substantive work, follow [eligibility and handoff](../research-router/references/editing-capability.md).

When author identity, voice, or preferences matter, consult the Labo workspace
[author profile](../../../profile/author-identity.md) when available. Keep
personal facts there rather than in skill text; update only explicit durable
facts or corrections from the user, or facts they ask to save, with source
context. Apply the owning skill's normal verification rules.

Use when the user wants to improve a skill while editing a concrete artifact,
inspect a preview, and steer the next pass. The user's feedback is the central
evaluation step. Read the relevant repository instructions and the skill that
currently owns the artifact before editing.

## Keep the work copy clear

Identify the authoritative source, its exact revision or content hash, the
editable work copy, and the preview destination. Follow the user's chosen
locations and the repository's layout. For a Labo-local trial, keep editable
sources under the appropriate `writing/` item and generated previews under
`output/`.

Preserve the authoritative source. If the user wants to work from a file in
another repository, copy the selected version into the requested workspace and
record its origin there or in the handoff. Make edits to that work copy. A
request for a local trial does not authorize writing the result back to the
source repository; sync only when the user explicitly asks. If the user names
the original as the direct edit target, honor that instead of forcing a copy.

## Make one useful trial

Find the smallest recurring decision the current skill leaves unclear. Update
the existing skill that owns that decision when possible; create a separate
skill only for a reusable workflow gap with a distinct trigger. Generalize the
lesson without turning one artifact's style preference into a universal rule.

Apply the adjusted skill to one bounded, visible part of the artifact. Preserve
the source's mathematical and factual claims unless the user asked to change
them. Keep the edit small enough that the user can say what worked, what went
too far, and what should change next.

Build the requested preview into the named output location and inspect the
render for build failure, clipping, missing content and obvious layout defects.
This check prepares a useful preview; it does not replace the user's judgment
about style, emphasis or the right degree of editing. Do not launch a standing
review panel for a feedback trial. Use a project-mandated source or safety check
when it applies, and state its scope separately.

## Stop at the user's feedback checkpoint

After the first preview, report:

- the editable work-copy path and preview path;
- the exact source version copied;
- the skill decision tested and the bounded artifact change;
- build/render checks and any remaining limits.

Then ask for the user's concrete reaction to the preview. Leave the next
content edit pending that response. Treat this as an active iteration, not a
finished artifact. A clean build or an internal reviewer cannot stand in for
the requested user feedback.

## Continue from feedback

Treat the user's comments as steering for the next pass. Separate a preference
for this artifact from a reusable skill rule. Apply artifact-specific advice to
the work copy. Update the skill when the feedback exposes a general decision
rule that will help future tasks; keep project-only preferences local. Rebuild
the preview and show what changed since the last version.

Repeat until the user says the result is ready or gives a different next step.
Approval of a preview alone does not authorize source sync, publication or
other external delivery. Follow the repository's Git rules; label any required
checkpoint as a draft, and do not treat a commit as user sign-off.
