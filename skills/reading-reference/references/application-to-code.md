# Explain methods from actual applications to code

Use for substantive computational-method explanations and every literature-based
method-code unit in the agreed reading scope, including educational, background
and auxiliary implementations. Unrelated installation, plotting-only utilities
and syntax illustrations do not create a method application task. Bounded source
lookup or translation retains its scope; pure proof explanations do not require
invented empirical applications or software.

## Keep the section as the reading unit

In source-aligned reading, preserve the source's sections and subsections: numbers,
faithfully translated titles, order and hierarchy. Complete the local account in
the corresponding unit: source passage and faithful translation, explanation,
application context, essential implementation and interpretation. These are
coverage obligations, not a source-first display order. Follow the
[preparation-to-source sequence](paper-preparation.md#prepare-the-reader-then-return-to-the-source)
within each owning source unit. Keep additions
visibly distinct from the source. Do not flatten source subsections into paragraphs
or detach their explanations into a later collection of supplements.

Identify the method by its established name before its background; put the
role sections below that subject identity under the
[heading contract](../../mathematical-exposition/references/roles-and-headings.md#name-the-subject-before-its-roles).

Use the ordered role-section map in [Reading structure](reading-structure.md#fix-the-scope-and-the-section-map-before-editing)
for each coherent method/application account, once per method rather than per
excerpt. That file owns the skeleton, including comparison, execution status,
implementation search/adoption and the return to the target original/translation.
This file supplies each method role's content requirements. Preserve the source
parent and role boundaries; group operations within a role and connect adjacent
openings to the result or question just established. Optional collections retain
the roles needed for their declared task under the same structure contract.

## Establish the application before its code

Organize the added explanation around a coherent application and method:
**application, including its visual context → obstacle → overall computation
and complete selected code → explained operations
→ the code's specific strengths and fit to that obstacle → relationships to
other methods**. This reading dependency supplies the role skeleton once per
method/application account, not five repeated sections for every excerpt. Preserve
the internal order of source passages/translations; place the added application
account before its first method-code block and return to the original at that
source unit's end under the paper-preparation contract.

Bring the existing application account as a whole: background photographs,
input examples, diagrams, relevant figures/tables, captions and their reading,
data meaning, task and desired output. Retain all of these in-scope materials
when revising; do not replace them with a shorter paragraph, a figure number or
a link to the back matter. Explain what the reader sees and how it exposes the
problem. Before the first code, the reader must be able to identify the actual
target, what is wanted and what makes it difficult. Domain knowledge is not
implied by mathematical expertise. This prerequisite takes precedence over
brevity and proximity of code to a translated sentence.

Place visuals by their explanatory role: background/input, obstacle, mechanism,
result or comparison. A result figure may also be the clearest view of the input
objects or the question. Show and explain it before code when needed for that
purpose, label its status, and return to it for the result or comparison later.
Re-display it where necessary. Do not classify every figure as an after-code
result or remove the photographs from a mixed-role figure. Keep visible marks,
captions and explanatory prose together at a readable scale. File storage once
does not mean display once. Source originals and their translation order stay
intact; an added, clearly attributed preview can supply the earlier context.

## Show the adopted source code first

The search for the source authors' or official code comes before any independent code
is written ([R18](methods.md)). On the reader's main route, every code unit then opens
with the code that search adopted:

1. the source authors' code, if obtained and its license allows display ([R6a](source-rules.md));
2. otherwise a later or related author's code for the same operation, or an official
   library, whose license allows display, with its relation stated (not the source authors'
   code, and what differs); obtained code with an unknown license is linked, not shown;
3. otherwise the source paper's own algorithm (its table or figure) beside AI-created code,
   labelled, with the link to the unshown code and a statement of what was searched (R18).

An AI-created implementation follows, labelled as a supplement (a check, an adaptation
or a missing step), never as the unit's main code, even when it is shorter or was
written first. How much of the adopted code may be displayed depends on its license
([R6a](source-rules.md)). The comparison section then refers back to this display
instead of repeating it.

## Show the whole implementation before its parts

Once this application and obstacle are established, give the implementation's
whole flow before explaining selected operations. Explain what goes in, the
meaningful stages and their data dependencies, and what comes out. Then display
the complete implementation unit that carries out that flow, including required
imports and helpers or their already displayed definitions. For a larger system,
choose a coherent method-level unit and identify the external interfaces and
dependencies; do not substitute a hollow wrapper, pseudocode or an outline for
the actual implementation. Choose the unit from the method's input-to-output
flow, not from whichever fragment is easiest to display. The scope is the
explained method, not every file in its repository. A later full listing or a
link to it does not supply this first whole-code encounter. Explain this initial
listing at the level of inputs, stages, data flow and outputs; reserve detailed
operation-to-mathematics reasoning for the following walkthrough.

After that whole view, develop the relevant mathematics and select the operations
that explain how the method works. Keep each excerpt near its explanation and
identify where it belongs in the already displayed unit, using matching function
names and line identities. Before each excerpt, identify which calculation or
unresolved task from that immediately
preceding explanation it carries out, and what output or check is needed for the
current purpose. "Below we implement X" alone does not explain this connection.
Name the algorithm and implementation visibly before the listing; a description
of the calculation or a bare function name is not always enough to identify it.
Keep the identified source/link row immediately after the code under R20, then
interpret the operation and any output against that same purpose, including its
fit; do not claim an unperformed check. For a multi-step method, carry the same
problem forward through meaningful stages; introduce a new obstacle where it actually
arises. Do not restart the entire application or force the five-part structure
around every small code fragment. Avoid fragmenting one computation merely to
produce more headings or repeated claims of suitability.

After the code, connect its concrete functions, variables or operations to the
property they produce, explain how that property addresses the obstacle already
shown, and state the conditions and remaining limits. Refer back to the same
photograph, feature, diagram or data example when it carries this explanation.
Explain the gain in terms of the task, rather than praising a method as useful,
fast or superior in general. A restatement of syntax or the optimization objective
does not establish this fit. Distinguish supported application findings from a
mathematical explanation and from what a simplified teaching run actually tests.
Introduce the comparison from the property or limitation just established;
explain which question about this same problem the alternative will address.
Then explain the shared and changed operations and their consequences. Several
related excerpts can share the method-level fit section and comparison section;
keep these two role boundaries visible rather than merging them into one title.

For a bounded preview, reduce the number of methods or operations, not the causal
explanation within the selected unit. Carry the stated obstacle through the
design choice, mathematical property, exact implementing operation and resulting
capability. Explain why each decisive operation produces that property; naming
an algorithm, displaying its objective or adding a line-to-formula table is not
enough. Establish what the method achieves for this task before turning to its
limits. Select supporting original passages for those decisive mechanisms, not
only introductory promises or result summaries. Keep the usable source/code
links and return paths required for the selected unit even in a short preview.

Complete background before code does not require putting the full implementation
search, environment log or all later result analysis before code. Keep those
records complete in the same method account, at the point where they serve the
reader, without interrupting the code-to-fit explanation. Longer surrounding
modules, delivery copies and ancillary code may live in explained appendices
with links and return paths. They do not replace the complete selected unit
shown before its detailed walkthrough, or its local application and interpretation.

## Keep local accounts complete and collections purposeful

Complete the local application/method account through the connected stages above,
including evidence, visuals and interpretation, mathematics-to-code mapping,
comparison, scoped implementation search/adoption, execution status and open
limits. A later collection cannot supply missing local explanation.

Follow [document sequence and optional views](paper-preparation.md#keep-section-progression-and-purpose-specific-views-distinct).
A background/explanation view keeps the evidence and dependencies of its retained
argument. A code collection keeps the context and operational information needed
to understand and use its implementations, with links to fuller application
accounts; it need not reproduce the entire application or source-reading sequence.
An index is legitimate for lookup when labelled as such. Do not expand any of
these into a full duplicate to satisfy this contract. Use shared maintained
sources and compare retained facts, locators, statuses and limits across views.

## Explain why the application belongs here

For every in-scope method/application account, develop:

1. **Application.** What actual study analyzes and wants to achieve, with the
   domain explanation and visible materials specified above.
2. **Obstacle.** What must be estimated, preserved, distinguished or predicted,
   and what makes that difficult in the displayed example. Ground the need and
   assumptions in inspected passages; do not invent author motives or failures.
3. **Code.** Introduce the overall computation and show its complete selected
   implementation before picking out its decisive mathematical/code operations.
   Keep their sources identifiable. Map input/output
   meanings and consequential adaptations to the actual functions and variables.
4. **Specific strengths and fit.** Explain the operation → property → effect on
   this obstacle → conditions/limits chain. Read the relevant published figures,
   tables and outcomes against it; keep authors' interpretations and the note's
   synthesis distinct. A pipeline outcome does not isolate one method's effect,
   and a synthetic run does not establish the published application's success.
5. **Relationships.** Explain what other methods share or change and how that
   changes the response to this same task, under the relationship rules below.

Choose the example as the method's *specific example*: the one where its lens is most
visible ([roots and lenses](roots-and-lenses.md)), next to the root's shared example.
Also state **why this example is introduced in this particular section**: which
concept, mechanism, comparison or limitation the reader should understand through
it, and how it connects the preceding passage to the code now shown. This teaching
rationale is the writer's explanation, grounded in the example's properties; do
not attribute it to the application authors without evidence. Saying that a
method is popular or useful in a field supplies neither this rationale nor the
application-side reason for using it. Apply both reasons to educational,
background and auxiliary method code as well as headline algorithms.

## Find and inspect the application evidence

For each method, also record what the sources say about its lens and its failure
([roots and lenses](roots-and-lenses.md#collect-them-while-investigating-the-sources)); this
search is the *specific example* row of [the card-driven search](roots-and-lenses.md#let-the-card-decide-what-to-search).
Inspect its proposal's application sections and follow references,
supplements and application papers as needed, beyond the target bibliography.
Find evidence of the actual need, placement of the method and obtained result,
not just an abstract or a sentence saying it is used in a field. A proposal with
an actual application can supply this evidence; otherwise inspect a paper that
uses the method. Do not assume a matching application exists without searching.

Keep four roles explicit: target reading source, method literature, application
study, and implementation source/version. One document may fill several roles.
At the point of use, link exact sections/pages/equations/panels for the application's
problem and results and the method's design. Record inspected scope and unresolved
access in existing source notes. A bibliography entry or private search log cannot
replace the reader-facing explanation. Map this evidence to the source section,
passage/operation, local code and the learning purpose before drafting.

For substantial paper preparation, show the supporting method/application passages
with faithful translations under [supporting-source reading](paper-preparation.md#make-supporting-literature-readable).
Their exact locators and displayed text establish what the paper says; code-source
rows establish implementation provenance. Neither substitutes for the other.

A synthetic run may expose a mechanism or verify an operation, but cannot stand
in for actual application evidence. If that evidence is unavailable or no actual
use is found within the searched scope, record the checked places and precise
missing link as unfinished work; do not fabricate an application or claim the
method has none. Disclosure does not close the required application coverage.
Application grounding does not itself require rerunning every published study:
match any reproduction claim to the procedure, data, settings and actual run.

For additional language versions, apply [the multilingual code contract](multilanguage-code.md).
Carry one calculation through the languages with actual code and explain the
idiomatic operations, design decisions and per-language verification.

## Give every code unit a reason card

Beside each code excerpt or full listing, record in this order, so that a derived view
(for example a slide) can use it directly:

1. **Step** — which step of the algorithm the code implements (the algorithm's step
   number or equation, and the matching lines).
2. **Reason** — why this code is shown at this subsection: the obstacle it addresses or
   the root it serves, with the source that states that reason (page).
3. **Lines to look at, what they do and role** — the few characteristic blocks; for each, what
   it does in plain words ("sets OD and TD as percentiles of the local density"), where it comes
   from ("inherited from SPADE, `downsample.R` L95–107", "added by the authors"), and its role:
   inherited unchanged, removes the obstacle, serves another aim, only tidies, or leads on; for a
   change, what it changes in the output. A role label alone does not explain the lines.
4. **Provenance and license** — by the provenance classes (R5a) of [Sources](source-rules.md),
   with the license and the display extent it allows (R6a).

## Explain relationships for every code unit

Identify the implemented mathematical procedure and its relationship to relevant
other methods and code in the material. Distinguish:

- another implementation or numerical solver for the same method;
- a special case, variant or extension;
- shared operations within methods with different objectives or assumptions;
- an alternative for the same application requirement;
- a different estimation target or question despite similar-looking operations.

For each relevant relationship, identify both procedures/implementations, their
shared objects and steps, the exact changed assumptions, equations or operations,
and the corresponding functions or lines. Explain why the change is made and
how it affects computed outputs, admissible inputs or interpretation. Code origin
(author, library or independent) is a separate issue from mathematical lineage.
A change of language alone is not a new mathematical variant. Similar-looking
code does not prove equivalence or historical descent.

Inspect primary passages and, for implementation claims, fixed code on both
sides. Distinguish an explicit source claim from a supported synthesis. Explain
what evidence supports a special-case or equivalence claim; numerical agreement
requires the relevant comparison under R20, not static resemblance. Do not force
all-pairs comparisons or an invented predecessor. If a relation cannot be
established, report that gap rather than assigning a convenient label.

For consequential implementation comparisons, show the actual relevant code on
both sides in the delivered explanation, with fixed versions, file/function
identities and original line numbers. Prefer inspected corresponding author or
supplement code when obtainable, then an identified maintained/third-party
implementation; document scoped missing access rather than silently substituting
two teaching rewrites. Follow R18/R20 for selection and source rows. A paper,
GitHub link, function name or line-number table without visible code is not the
comparison. Select short matching excerpts around the operations being compared;
retain faithful code and mark omissions, with complete editable units available.
Keep each pair in view together where practical, and put the identified source
row directly after each block. Do not copy a large unrelated listing just to
satisfy presence.

Lead into each pair with the question from the preceding method account. Identify
which operation in one excerpt corresponds to which operation in the other,
what is mathematically shared or changed, and its effect on inputs, outputs or
interpretation. Account for layout/transposes, neighborhood conventions,
normalization, regularization and solvers when consequential. Source inspection
supports a conditional operation correspondence, not unperformed numerical
agreement or reproduction. A compact table may index these visible excerpts but
cannot replace them. Missing comparison code remains a located limitation.

Use local prose or a compact comparison table when useful. Each code excerpt,
full listing and editable unit must link to its applicable application account
and relationship explanation, with a return route when these are separate.
Related blocks may share a raw evidence asset or complete code file, but each
local method route must become a full account across its stages. Optional
collections retain what their declared task needs and link to the fuller account.

## Completion and review

Check the delivered artifact in source reading order. Confirm preserved section
and subsection hierarchy. Apply the [heading audit H1--H5](../../mathematical-exposition/references/roles-and-headings.md#audit-the-headings-against-the-body)
to complete method accounts: fixed role order and boundaries, role plus concrete
point, corresponding body content and progression. Check optional views against
their own declared scope. Then apply [R27](review.md) to adjacent prose and displays;
coverage or compliant-looking titles alone do not establish continuity. For PDFs,
expose these useful local units and operation stages as nested bookmarks under their
owning source section/method, following [R14](explanation.md). Inspect the actual
built outline and destinations; a contents page or styled headings alone do not
establish bookmark navigation. Read each application/method account in its delivered order. Stop just before
its first code: using only what has appeared, identify the target, data, desired
output and obstacle, and inspect the photographs/figures and their explanation
that make these concrete. After the code, reconstruct how its actual operations
address that same obstacle and under what conditions, then read the comparisons.
Check both application-side necessity and why the example belongs in that unit,
with published evidence and relevant method/code relationships. Code markers,
heading order, keyword/length checks and inventories do not establish this
reader-facing dependency. Flag a visually unsupported introduction, background
first supplied after code, or fragmented template cycles even if all links work. Apply this to all
in-scope method-bearing units, including educational and auxiliary code.
Inspect cited evidence and both sides of claimed relationships, and test actual
built routes. Correct headings, an inventory of ingredients, a runnable toy or
working remote links alone cannot establish a coherent local reading unit.
Missing application evidence, misplaced code, hierarchy flattened into generic
supplements, unexplained variants or missing teaching rationale remain findings.
An accurate account hidden in prose or a distant appendix also remains a finding
when the requested local explanation cannot be found through its headings and
navigation.
Traverse the main local account without relying on a later collection. Traverse
each optional view for its stated task and check assumptions, references and
transitions left by extraction. Compare retained claims, locators, implementation
identity, statuses, limits and links. A complete appendix plus an incomplete local
account fails; a complete local account plus a labelled lookup index need not.
