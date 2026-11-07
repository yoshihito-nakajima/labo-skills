# Preserve the reading structure across revisions

Read this before outlining or revising substantial source-based reading material,
including a one-method preview. This file owns source hierarchy, role-section
boundaries, source-return order and optional-view structure. It does not impose
this format on bounded answers, translation-only work or an explicitly different
user format. A short preview selects fewer source units; it does not silently
turn the selected unit into an explanation-only collection.

## Fix the scope and the section map before editing

Identify the target work/version and selected original units at the entrance.
Distinguish the target reading source, supporting method literature, application
studies and implementation sources. State what question sends the reader to each
supporting work and what it contributes on returning to the target. Do not replace
this reading route with a chronological tool/search log.

Before editing, record a compact section map in the existing local outline or
handoff. For each selected source unit, record its original number/title/parent,
required role sections in order, source-return and original/translation blocks,
and locations of their existing content. Record also, per unit, its root problem and
background card — used here, root, shared example, lens, applied view, specific example,
limit example ([roots and lenses](roots-and-lenses.md#background-card)) — and, for each code unit, the
implementation search status ([R18](methods.md)), the adopted code and its license
([R6a](source-rules.md)); fill these before the unit's prose is written, so roots, cards
and code order are designed rather than added afterwards. Record also, per unit, its parent, what it `needs` from earlier units and what it
`produces` for later ones, and the resource-ledger and lineage entries it uses
([unit chain](unit-chain-and-claim-gloss.md#argument-spine-and-the-chain-of-units),
[resource ledger](resource-ledger.md), [lineage](lineage-and-comparison.md)); a unit's
opening names its needs. Add required but missing units too:
the current draft cannot define its own completeness. Use the actual source and
agreed scope to establish the expectation. Private source-specific maps belong
with the artifact, not in this reusable skill.

For a computational-method reading unit, retain these explicit roles beneath the
owning source section:

1. Background: application, visible evidence and reason for this example.
2. Obstacle: the requirement the current method must meet.
3. Method/implementation: whole computation and complete selected code, then
   mathematical and code operations with their consequences.
4. Specific fit and limits: what the operations achieve for the same obstacle
   and the conditions under which they do so.
5. Comparison: consequential relationships to other methods/implementations.
6. Execution status: inspected, executed, reproduced and still unverified scope.
7. Implementation search/adoption: checked candidates, results and choice.
8. Target-source correspondence: introduced objects/steps mapped to source text.
9. Named target work's original and faithful translation.

Roles 1–7 use the content criteria in [Applications to code](application-to-code.md)
and [Methods](methods.md); roles 8–9 use the sequence below and the passage criteria
in [Paper preparation](paper-preparation.md). Keep an agreed status/search order.
Supporting originals/translations belong at their explanatory points and do not
replace roles 8–9. File downloads and raw logs may be appended; the local account
still needs the actual comparison, status and adoption reasoning. Facts buried
elsewhere do not supply a role section. For noncomputational units derive the
appropriate explanatory/proof roles from the source and task, without invented
software, empirical application or execution records.

For each requested revision, mark which entries change and where the other
required entries remain. Merging subheadings inside one role is possible; losing
a required role, source parent or return block is not a formatting simplification.
If the user changes the reading purpose, update the declared scope and section
map accordingly; otherwise retain the existing main reading route. Do not ask
for approval of routine layout choices or add an approval gate.

## Source-aligned reading structure

Retain the target paper's section and subsection numbers, titles' meaning, order
and hierarchy as the reading backbone. Keep translation, local explanation,
application context and corresponding implementation within that source unit.
Do not flatten original subsections into paragraphs or move their substance to
a later generic supplement. Clearly label added commentary or subordinate boxes
without changing or impersonating the source hierarchy. Keep source and
added equation/figure numbers distinguishable. For a bounded request, retain the
original numbers of the selected sections rather than renumbering them from one.

At each named-method/concept unit entrance, identify its established name and
abbreviation before the background, following
[subject identity and role headings](../../mathematical-exposition/references/roles-and-headings.md#name-the-subject-before-its-roles).
Retain an existing informative source title; add an identified subject line when
its title alone does not name the object being explained.

Under the source hierarchy, preserve the added role sections of the method
contract or agreed outline. For computational methods, use the fixed skeleton in
[section map above](#fix-the-scope-and-the-section-map-before-editing), once per method rather than per
excerpt. Each role heading shows [role | concrete point](../../mathematical-exposition/references/roles-and-headings.md),
and its opening carries forward the preceding argument under
[adjacent-passage continuity](../../mathematical-exposition/SKILL.md#carry-the-argument-across-adjacent-passages).
Consolidate unnecessary divisions within a role while keeping the role boundaries.
In PDFs expose both parts of these headings in the source-aligned bookmark tree
under [R14](explanation.md). Distinguish bookmarks from the visible contents and
ordinary hyperlinks; inspect actual titles and landing content.

The main route completes each source unit before advancing to the next. Optional
collections follow [document sequence and view scope](#keep-section-progression-and-purpose-specific-views-distinct).
They provide a different use of selected material, not a duplicate of the whole
document. Keep the source section as the local owner of its explanation; a later
collection or link cannot replace content required in that main unit.

Account for the in-scope original text and provide a faithful translation into
the requested language (Japanese for Japanese reading materials). Present the
original passage and its translation in a clearly corresponding form, with exact
source locations; do not silently omit difficult passages or replace translation
with a summary. Preserve qualifications, assumptions, notation and uncertainty.
Label an ambiguity or suspected error rather than silently correcting the author.
Separate original text, translation and added interpretation. A source attachment
or a link alone does not replace the requested original-text/translation coverage.

### Background card and shared roots

The background of every unit is a card whose fields, root list and generator check are
defined in [roots and lenses](roots-and-lenses.md). Decide it in the section map above,
before the unit is written. A reason that no source states is marked as unverified,
never supplied from memory.

In the preparatory explanation, explain what each passage is saying, its role
in the argument and how it connects to adjacent passages. Explain mathematical
objects, hypotheses and decisive steps where used. For each figure/table,
provide its caption translation and explain the quantities, conditions, visible
patterns, supported inference and limits. Show the relevant visual at a readable
scale; merely paraphrasing its caption is insufficient.

## Prepare the reader, then return to the source

For explanatory reading material, unless a different order is requested, complete
this sequence inside each owning source section/subsection:
**background and connected explanation → implementation/comparison and relevant
status records → explanation-to-source correspondence → original and faithful
translation**. Retaining the source hierarchy does not require exposing the
unprepared reader to its original passage first. Keep source sections in their
original order and keep each section's original text and translation internally
intact; do not collect several subsections' originals at the end of a chapter or
move them to a generic appendix. Translation-only or explicitly interleaved
formats retain their requested order.

Build the eventual reading task throughout the explanation: introduce the objects,
question and difficulty before operations, and identify the decisive steps the
reader will recognize in the source. Do not rely on an unread original to make an
opening or transition intelligible. Immediately before the original, give a short
correspondence from the explanation's objects, equations, code or findings to the
source's exact paragraphs, equation/algorithm steps or figures. Include consequential
notation changes, omissions or limitations, and distinguish added examples and
implementations from what the target source itself says. An outline recap or
"now read the paper" does not provide this correspondence. Then let the reader
read the complete in-scope source unit, followed by its faithful translation.
The bridge must not replace either text or silently repair the source. In the
main route, the translation closes this account and the next source unit follows.

Use explicit subordinate role headings for the correspondence and original/translation
stages, consistent with the agreed outline, and test their built destinations.
Apply this return to the main target source within its owning unit. Supporting
literature has its own local excerpt/translation pairs under
[supporting-source reading](paper-preparation.md#make-supporting-literature-readable); do not defer
those pairs to the target paper's source-return block.

## Keep section progression and purpose-specific views distinct

In the main reading route, finish a source section/subsection with its original
and faithful translation, then advance to the next in-scope source unit. Do not
restart the same unit's background, implementation or complete account between
that translation and the next section. Short return/navigation links are useful;
a second full explanation at that boundary interrupts the source progression.

Do not add or retain a complete duplicate merely to supply a second reading
route. Remove an unchanged reprint from the rendered structure when revising
under this contract; preserve its underlying material. Honor an explicit request
for a duplicate as an exception, with its scope labelled. Otherwise, add an
optional collection only when it serves a distinct reader task. For example:

- A background/explanation view omits the target paper's original/translation
  blocks and lets the reader follow the explanatory argument continuously. Select
  code according to that view's scope. Retain definitions, hypotheses, necessary
  equations, visuals/captions, supporting-literature pairs and limitations for
  the claims still made. Repair transitions and references left by extraction.
- A code collection groups implementations for lookup or execution. Keep method
  and implementation identities, input/output contracts, required helpers/data,
  dependencies, entry commands, provenance/reuse terms and actual execution
  status. Include enough operation explanation and mathematics correspondence to
  use the code accurately; link to the fuller application and argument. It need
  not repeat all background, primary passages or translations from the main text.

These are examples, not two required additional parts. A clearly labelled index
may serve lookup; it is not an independently readable explanation or executable
code collection. A genuinely new appendix states its contribution. State each
view's purpose, included scope and prerequisites at its entrance, and supply
navigation to corresponding main units. Put same-PDF collections after the main
sequence, or produce separate files when requested. Keep the main source order
intact; optional collections may use a task-appropriate order with source mappings.

Derive views from shared maintained content where practical; do not maintain
independent prose/code copies that can drift. Test the selected content and its
dependencies, not equality to the whole main text. Retained claims, source
locators, implementations, status and qualifications must agree across views.
Completeness is relative to each declared task, not identical coverage everywhere.

Require substantive citations throughout each reading route. At the passage
that uses a source, identify which claim, equation, figure, code operation or
comparison it supports, with an inspected page/section/equation/figure locator;
for code use the fixed version and file/function/lines as appropriate. Place
citations where their scope is clear while reading, repeating them when a new
passage or route would otherwise lose that connection. Do not invent unverified
locators. A link to a final list, a single source note at a section's end, or a
post-code provenance row does not by itself cite intervening mathematical or
comparative claims. Cite the relevant literature in those passages too. Preserve
the distinction between source claims and the notes' own derivations.

Place the common bibliography at the document's end, after any optional
collections. Each view retains attribution for the content it uses; separately
delivered files need usable references and links in their own delivery context.
References, code files and raw assets may be shared. The final list does not
replace attribution beside claims and code. Preserve source citation identities
while including the additional literature and implementation sources actually used.

For example, an optional explanation view can follow two main units:

```text
Main reading route
  Source unit A: subject name → preparation → source correspondence → original/translation
  Source unit B: subject name → preparation → source correspondence → original/translation
Background/explanation collection (only if useful or requested)
  A then B: connected explanations with their required supporting evidence
  Target-paper original/translation blocks omitted; references repaired
References (one common final list)
```

For computational units, preparation retains the agreed background, obstacle,
method/implementation, fit/limits, comparison and status roles. This document
sequence does not impose code or an empirical application on proof-only units.

## Check the structure before checking the latest improvement

Compare the delivered structure to the pre-edit map and actual source, not to
headings generated from the revised draft. Check missing, moved and reparented
units, role order, target identity and source-return boundaries. A claimed
replacement must fulfill the same role with substantive content. Distinguish
absent content, content hidden in another role, and content intentionally outside
the user's agreed scope. A source link, heading count, successful toy run or
supporting passage pair cannot make an absent target-source reading complete.

Then read each role's body and transitions: what source question is being resolved,
what evidence/operation resolves it, and what the next section takes from it.
Apply [R25–R27](review.md) and the H1–H5 heading audit. Check the specific new
feedback (for example clearer links or whole-before-part code) in addition to,
not instead of, retained obligations. For a PDF compare the actual nested outline,
visible headings and landing content to the same map under R29. Record content,
source fidelity, implementation execution and rendering separately. Do not mark
uninspected units passed or treat a rendered preview as complete source coverage.

Useful adversarial cases are in the self-contained
[structure-preservation fixture](../../../tests/fixtures/reading-reference/structure-preservation.md).
