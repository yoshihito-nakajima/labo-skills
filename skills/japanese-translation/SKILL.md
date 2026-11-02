---
name: japanese-translation
description: Create or revise a Japanese translation that can be read on its own, so awkward wording and problems in the argument remain noticeable without alternating with the source. Use for Japanese-only reading copies, including mathematical manuscripts and papers.
---

# Japanese translations for continuous reading

Before substantive work, follow [eligibility and handoff](../research-router/references/editing-capability.md).
For each request, follow the [required consultation](../research-router/references/consultation.md).

Give the reader a natural, faithful Japanese text they can read continuously
without switching to the source language. Reading the Japanese alone should
make awkward wording, unclear references, and difficult-to-follow reasoning
noticeable. Source comparison then establishes whether a problem came from
the translation or was already present in the source.

## Establish the source and scope

Use the source, version, intended readers, requested extent, and output format
already established in the task. Read the actual in-scope text and necessary
surrounding context. A full translation covers the requested text, including
difficult passages; it is not a summary or an expanded explanation.

In a Labo workspace, consult applicable `writing/.rules/` and the relevant
Japanese examples in `writing/.corpus/index.md` when present. Follow supplied
glossaries and established terminology. Use language examples for phrasing and
register while keeping the translated content anchored to its source. Personal
and field-specific preferences stay in workspace rules and corpus records.

Translation alone does not invoke the expanded paper-preparation workflow.
Use [reading-reference](../reading-reference/SKILL.md) for separately requested
explanations or source investigations and
[paper-writing](../paper-writing/SKILL.md) for requested manuscript revisions.
A translation request leaves the source manuscript unchanged.

## Preserve what the reader needs to notice

Write idiomatic Japanese at the source's level of formality and technical
detail. Change word order, supply grammatically necessary subjects with clear
antecedents, and split or join sentences when their meaning stays the same.
Keep section and paragraph order, the progression of the argument, emphasis,
qualifications, and repetitions that matter to how the source reads.

Preserve assumptions, quantifier order, dependence of constants, logical
connectives, claim strength, and uncertainty. In particular, preserve the
difference between a statement about each object and one that holds uniformly,
and between a suggestion and a proved conclusion. Keep notation, numerical
values, citations, and equation content intact.

Natural Japanese must not silently supply missing premises, justify an
unsupported transition, strengthen a claim, resolve an ambiguous reference,
or repair a suspected mathematical error. Translate the statement the author
actually made. Put substantive concerns in accompanying notes with source
locations; keep a proposed repair out of the translated body. Readable language
should let a source-level problem remain visible.

## Read the Japanese alone, then compare

For a new translation, draft from the source and then set it aside. For an
existing translation, start by reading the Japanese before consulting its
source. Read in document order, using only the context present in the Japanese.

Notice forced collocations, particles and word order, excessive nominal
phrasing, sentence rhythm, and changes of register. Also notice referents the
reader cannot identify, unexplained terms, transitions whose grounds are
unclear, and conclusions whose connection to the stated premises is hard to
follow. Do not mentally fill these gaps from remembered source passages.

Compare the affected passages with the source before deciding how to fix them.
Correct translation-induced ambiguity, omissions, and awkwardness. If the
source itself is unclear or makes an unsupported move, preserve its content
and report the specific concern separately. If the cause remains uncertain,
say what is unresolved rather than choosing a convenient interpretation.
After corrections, reread the Japanese in sequence.

If only Japanese is available, perform the Japanese reading pass and state the
limit of any fidelity assessment. Do not attribute a problem to an unseen source.

## Make mathematical documents readable in Japanese alone

Include all in-scope definitions, assumptions, theorem statements, proofs,
displayed equations, figures, tables, and captions at their points of use.
Translate the title, abstract, headings, theorem names, and ordinary prose;
retain conventional notation, proper names, and bibliographic identities.
Keep section, theorem, equation, and citation references traceable to the
source and resolved within the Japanese document.

When deriving a Japanese-only copy from a bilingual document, carry shared
equations and figures into the Japanese flow. Removing English blocks must
not leave a Japanese proof referring to a formula that only appeared there.
Likewise, links back to the source do not replace translated statements or
other in-scope material. Include what the source contains without expanding
it into a new textbook or completing its missing arguments.

## Deliver the reading copy

Present the Japanese text as a continuous document by default, without paired
source passages or bilingual tables. Honor an explicit alternative format.
Keep accompanying notes brief and outside the translated body. Locate each
material concern by source section, equation, page, or file and the corresponding
Japanese phrase; distinguish unresolved translation choices from concerns
confirmed in the source. A diagnosis-only request returns findings and suggested
wording without silently rewriting the document.

Ordinary chat stays in chat. For requested files, reuse the existing destination.
In Labo, an own-manuscript translation normally belongs in
`writing/<paper>/ja/`; other persistent reading translations belong in
`reading/<slug>/`. Record the source version and covered scope compactly in
existing metadata, a source comment, or an accompanying reference record.
On updates, check which source passages changed rather than claiming a stale
translation matches the current manuscript.

Build requested PDFs through [labo-build](../labo-build/SKILL.md), and inspect
the rendering and resolved references. Before delivery, check coverage and
source fidelity as well as the Japanese reading experience. Report the checks
actually performed; a completed translation does not certify the source's
mathematical correctness.
