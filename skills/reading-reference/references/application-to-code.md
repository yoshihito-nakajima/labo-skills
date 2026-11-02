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
application context, essential implementation and interpretation. Keep additions
visibly distinct from the source. Do not flatten source subsections into paragraphs
or detach their explanations into a later collection of supplements.

Make the added account discoverable through meaningful subordinate headings,
not only sentences embedded in running prose. Let the reader identify the
application's problem and requirements, why this method and example belong here,
the requirement/equation-to-code correspondence, published results and the
implemented scope, and relevant method/code relationships. Place these headings
at their point of use; closely related purposes may share a concise heading.
For several operations, nest the corresponding explanation/code cycles under
the method. Added headings must remain distinguishable from source headings
and must not renumber or reparent the source's sections.

Immediately after a passage's translation and necessary explanation, show the
code for the operation just explained. For a multi-step method, use short cycles:
explain a step → show its corresponding code → identify its source/link row →
read the operations and outputs against the mathematics. Do not make the reader
finish all translations, an extended application tour, or unrelated method
explanations before seeing that step's code. Consecutive source passages within
the unit retain their order; code commentary does not alter the original text.

The application-to-code logic below remains required, but is not a demand for
five long standalone blocks before any code. Establish enough purpose and
context to understand the current step, then develop its mathematics and code
together. Introduce published results where they clarify that step, with their
scope and interpretation. If a necessary result occurs later in the source,
briefly explain and locate it locally without moving its original/translation.
Explicit headings organize these local cycles; they do not require completing
an extended application tour before the first code block.

Long complete implementations, shared evidence and cross-method syntheses may
also appear elsewhere. They supplement a locally understandable passage and
essential executable code; a link to an appendix or shared account cannot replace
those. Repeat only the context needed to resume reading. The identified source/link
row immediately after every displayed method-code block remains required by R20.

## Explain why the application belongs here

For every in-scope method-code unit, connect:

1. **Application problem.** What actual published study analyzes, what the
   investigators wanted to know or achieve, and the domain context needed to
   understand that question.
2. **Requirements and obstacle.** What had to be estimated, preserved,
   distinguished or predicted, and what made it difficult. Use inspected
   passages for the application's need, assumptions and choice of method;
   do not invent author motives, historical failure or superiority.
3. **Where and why this method works.** Its position in the application's
   pipeline, inputs, mathematical objects and decisive operations, the property
   that meets the requirement, and the limitations of that reasoning.
4. **What was actually obtained.** The relevant published figure, table or
   result, its quantities, conditions, evaluation and scientific or practical
   significance. Distinguish supported findings, authors' interpretations and
   limits; a pipeline outcome alone does not isolate one method's causal effect.
5. **Correspondence to this code.** Map those inputs, equations, operations and
   outputs to the adjacent functions, variables and lines. Explain faithful,
   adapted or simplified parts, their reasons and effects. Keep published
   results, static correspondence, local reruns and synthetic examples distinct.

Also state **why this example is introduced in this particular section**: which
concept, mechanism, comparison or limitation the reader should understand through
it, and how it connects the preceding passage to the code now shown. This teaching
rationale is the writer's explanation, grounded in the example's properties; do
not attribute it to the application authors without evidence. Saying that a
method is popular or useful in a field supplies neither this rationale nor the
application-side reason for using it. Apply both reasons to educational,
background and auxiliary method code as well as headline algorithms.

## Find and inspect the application evidence

For each method, inspect its proposal's application sections and follow references,
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

A synthetic run may expose a mechanism or verify an operation, but cannot stand
in for actual application evidence. If that evidence is unavailable or no actual
use is found within the searched scope, record the checked places and precise
missing link as unfinished work; do not fabricate an application or claim the
method has none. Disclosure does not close the required application coverage.
Application grounding does not itself require rerunning every published study:
match any reproduction claim to the procedure, data, settings and actual run.

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

Use local prose or a compact comparison table when useful. Each code excerpt,
full listing and editable unit must link to its applicable application account
and relationship explanation, with a return route when these are separate.
Related blocks may share evidence without duplicating a full account, but retain
the local context, essential code and reading of its operations required above.

## Completion and review

Check the delivered artifact in source reading order. Confirm preserved section
and subsection hierarchy and identifiable local application/requirements,
code-correspondence, results/scope and relationship headings. For PDFs, expose
these useful local units and operation stages as nested bookmarks under their
owning source section/method, following [R14](explanation.md). Inspect the actual
built outline and destinations; a contents page or styled headings alone do not
establish bookmark navigation. Then read each passage's translation/explanation into
its immediately corresponding code and operation/output interpretation. Check
both application-side necessity and why the example belongs in that unit, with
published evidence and relevant method/code relationships. Apply this to all
in-scope method-bearing units, including educational and auxiliary code.
Inspect cited evidence and both sides of claimed relationships, and test actual
built routes. Correct headings, an inventory of ingredients, a runnable toy or
working remote links alone cannot establish a coherent local reading unit.
Missing application evidence, misplaced code, hierarchy flattened into generic
supplements, unexplained variants or missing teaching rationale remain findings.
An accurate account hidden in prose or a distant appendix also remains a finding
when the requested local explanation cannot be found through its headings and
navigation.
