# Lineage and comparison inventory

Use for substantial paper preparation, and wherever a note explains a method that has
predecessors, encompassing frameworks or earlier versions. It owns the inventory of
every relationship the paper (or the explanation) relies on, and the level at which each
related work is treated. Search procedure, memo format and notation genealogy remain in
[research positioning](research-positioning.md); passage pairs follow
[paper-preparation](paper-preparation.md#make-supporting-literature-readable); code
search follows [R18](methods.md). This file decides **which** works need that treatment
and what must be said about each.

## Inventory before drafting

Go through the paper (introduction, methods, comparisons, discussion) and list each
place where it inherits from, compares with, criticises, generalises or is generalised
by another work. Give every entry a relation:

| relation | meaning |
|---|---|
| `inherited` | a component, definition or procedure taken over, possibly changed |
| `baseline` | a method the paper measures itself against |
| `criticised` | a method whose stated weakness motivates the paper |
| `encompassing` | a framework or more general method that contains this one |
| `encompassed` | a special case or simpler method contained in this one |
| `origin` | the problem or purpose a method or concept was created for |
| `prior-version` | an earlier version of the same method, code or definition |

Each entry records: where the paper says it, the primary work, version and locator,
status (`read` / `unread` / `unobtained`), and the four statements below. A relation the
paper states without naming a work is still an entry; find the work.

## What must be established for each related work

1. **Purpose** — what problem the method or concept was created for, in the primary
   source's own terms, and what it was meant to guarantee.
2. **Place** — which larger framework it sits in, and which neighbours share its root.
3. **Inherited** — what this paper keeps, stated precisely (definition, step, constant).
4. **Changed** — what this paper alters or adds, and what the alteration is for.

Take these from inspected primary passages. A statement known only from the target paper
is the authors' positioning, marked as such, not a verified comparison. Never fill a slot
from memory; an unfilled slot is shown as open.

## Treatment level

Entries with relation `inherited`, `baseline`, `criticised`, `encompassing`,
`encompassed` or `prior-version` are treated like the target's own method: displayed
original excerpts with locators and, for notes in another language, faithful
translations at the point of use; the explanation of the four statements; and, when the
work has code, the code at the same level as the target's under
[Applications to code](application-to-code.md). `origin` entries need the primary
passage and the purpose statement. A citation that only supplies background, on which
neither the paper's method nor its claims depend, stays in the bibliography; record it as
such rather than silently skipping it.

## Same and different, down to the code

For an entry whose method and the target both have implementations, put the
corresponding functions side by side and give an inherited/changed/added table at the
operation level (constants, branches, normalisations, stopping rules). Show the actual
difference, and run both on the same small input when both can be run; see
[execution](methods.md#execution-environments). If a prior version exists, fix its
version and compare it with the version used, because a later repository snapshot is not
the code of the paper. State what the comparison did not cover.

## Overview table

Collect the entries in one table near the note's introduction, so a reader (and a
[companion page](../../reading-proof-review/references/companion/overview.md), which takes it over) sees the history
before the code: the work and year, what it was made for, the weakness the paper names, what
the method keeps or changes, what checking the primary source found (including where the
paper's characterisation does not match the source), and the section that treats it. Lineages
the code does not show but that explain the paper (the concept a name comes from, an approach of
another family that shares the idea) are reference rows, marked as such. Developments after the
paper are optional and auxiliary: a separate list, each with its primary source and what it says
about this method, never mixed into the paper's own positioning.

### Later developments: procedure

Work after the paper is searched only when the user wants it, and only as the auxiliary list
above. Read primary texts (the papers, preprints, the code repositories' own files); quote
briefly with a locator; state the date read and the version. A page that redirects to a login
step is not followed: report it as not read, with the address, and look for an open copy
(preprint server, an archive's full-text service). Say plainly when the method is absent from a
source (and why, if the source states its cut-off). What a later work says about this paper's
method is the source's statement; the note's own inference is marked as such.

## Gate

The `comparisons` section of the coverage data file lists these entries and is checked
by `scripts/check_coverage.py`: every entry has a relation, a primary work with status
`read`, the four statements, and, for the treated relations, recorded excerpt,
translation (when required) and code comparison or a stated reason it does not apply.
`unread` or `unobtained` entries of the treated relations are open work. A passing gate
shows the inventory is complete; whether each comparison is right is checked in review
against the primary passages.
