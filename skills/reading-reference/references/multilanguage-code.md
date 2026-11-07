# Source-grounded implementations across languages

## Choose the source and the learning purpose first

Prefer relevant inspected author/supplement code regardless of its language.
Do not silently replace R, Julia, MATLAB, C or another original language with
Python. Preserve its actual language, fixed version and consequential behavior
when presenting it. Language preference does not discharge R18's source search,
and the display order follows [the adopted source code first](application-to-code.md#show-the-adopted-source-code-first).

For teaching materials, choose languages to serve the requested learning goal
and the method: Python, R, Julia or others may show useful differences in array
handling, linear algebra, iteration and library interfaces. When the reader asks
for practice across languages, supply substantive matching implementations, not
just a language list or unrelated syntax examples. Honor explicit language scope;
do not automatically require every method in every language or multiply copies
for a translation-only or bounded mathematical question.

If matching author code is not located or usable within the documented search,
write a complete implementation grounded in the paper's exact equations and
algorithm steps when code is required. Report the scoped search and unresolved
pointers; absence from that search is not proof that no author code exists.
An identified third-party implementation may also supply a useful route.

## Explain what was written and why

At each code unit distinguish author code, third-party code, adaptation/port of
an identified implementation, and an independently written teaching implementation.
A paper is the mathematical source, not the distributor of newly written code.
A port cites both its code parent and method source; an independent implementation
states its source-based design and any implementations used for comparison.
Do not call an independent version an author-code port merely because the method
is the same. Keep code-source rows and complete editable files under R20.

Explain the intended learning/computational purpose and the concrete choices:
what is preserved from the source, what omitted detail is supplied, what is
simplified, what numerical/storage choices change, and why these choices serve
that purpose. Describe their effects on inputs, outputs, efficiency and limits.
Generic labels such as "educational" or "faithful" do not supply this account.

Map the same mathematical operations to real functions/lines in each language.
Explain idiomatic choices, not only syntax substitutions: index origin, row/column
layout, dropping singleton dimensions, broadcasting versus matrix multiplication,
normalization, eigensolver ordering and selected subspace when relevant.
Separate notation changes, mathematically equivalent operations and changes that
can alter results. A language change alone is not a new method.

Keep the application-first role skeleton and adjacent-passage continuity. Each
language block takes a specific calculation/question from the preceding prose
and explains afterward what its operations obtain for that purpose. Group the
versions within the same method stage; do not restart the entire background for
each language. Preserve actual original-code comparisons; newly written variants
cannot stand in for evidence about an unseen author implementation.

## Run and compare only what the evidence supports

Inspect before running; provide complete files, dependencies and entry commands.
Check available runtimes. Install missing runtimes within the user's authorization
and environment constraints, using official sources and a suitable isolated
project environment for dependencies. Record actual runtime/package versions.
Do not turn a missing executable into a mathematical defect, invent a successful
run, or silently change the user's environment beyond the authorized setup.

Use the same saved inputs and settings across languages; a matching seed alone
need not generate identical data. Compare outputs or invariants appropriate to
the method, accounting for sign, scale, basis rotation and degeneracy. Record
metrics, tolerances, observed values and the tested scope. Agreement on a bounded
example is not general equivalence or reproduction of the paper's experiment.
A syntax/static check is not execution; one language's success does not validate
another. If any version remains unexecuted, say so at its code entrance and in
the result account, with the specific missing condition.

Where implementations appear, retain the citations, consequential design choices,
operation correspondence, full-file access and per-language verification status.
Optional code collections follow [the view contract](paper-preparation.md#keep-section-progression-and-purpose-specific-views-distinct)
without duplicating the full main explanation.
Review language selection and author-code preference, actual complete listings,
source/port identities, explained differences and claims against execution evidence.
A trio of code blocks without this explanation fails the learning purpose.
