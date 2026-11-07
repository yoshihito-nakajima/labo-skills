# Resource ledger and the main-text → supplement route

Use for substantial paper preparation. It owns three things: the inventory of what a
paper consists of and what was actually obtained, the order in which main text and
supplements are read, and what happens to material that cannot be obtained. Identity,
versions and privacy stay in [Sources](source-rules.md); this file adds the ledger and
its completion gate. Bounded questions and translation-only work keep their scope.

## Build the ledger before drafting

List every resource the paper consists of, from the paper itself rather than from what
happens to be on disk: main sections, figures/panels and tables, methods sections,
internal appendices, supplementary figures/tables/text/notes, supplied code and data,
software and dataset pointers, and the versions of any code the paper depends on. Each
entry records: kind, what it is, where the paper refers to it, status
(`listed` → `obtained` → `read`, or `unobtained`), locator in the obtained copy, and the
unit of the deliverable that uses it. Keep it as data (see the coverage gate below),
next to the section map, and update it as work proceeds.

## Acquisition is the writer's job

A supplied PDF that lacks its supplement is incomplete input, not a reason to leave the
supplement out. Obtain it: publisher page, DOI landing page, the journal's
supplementary-information link, author or lab pages, the repository named in the
paper, preprint servers. Record each place tried and the outcome. "Not in the input
file" is never the recorded reason. For data and code, use only
[sources that can be relied on](methods.md#reproducing-the-papers-figures); a dead or unsafe
portal and an unofficial copy are recorded as places tried, not as sources. Obtained files go to the sources area under
[R6](source-rules.md), as separate documents with their own identity record.

Acquisition continues while the note is written. A cited work, supplement item, dataset,
code version or figure source that turns up in the middle of a passage (a cited
statement that has to be checked, a method whose original is named, a dependency of
the code) is added to the ledger at once and obtained the same way, not left as a
reference to a title. Pick up the work itself, not a summary of it or a recollection.

## Read in the order the paper does

The route is main text first, supplement as the main text calls for it. When the main
text cites a supplementary item (figure, table, method, code), read that item at that
point and treat it where the main text uses it. Do not leave all supplements to a
closing block, and do not read them before the main argument is clear. Supplements
need not be merged into the main account; they are read, recorded, and brought in where
the main account depends on them.

## Supplements that must be read

Whatever the paper's own labelling, read, record and explain at the usual level
(excerpt, faithful translation when the note is in another language, explanation,
locator) every supplementary item that is:

1. code or a software package;
2. a detailed procedure or pseudocode for a method the main text only sketches;
3. a figure or table on which the main text rests a claim by pointing to it;
4. a derivation of a formula or bound the main text states;
5. data or statistics that support a stated result or control;
6. materials and methods needed to interpret an experiment or dataset;
7. an additional experiment or validation the main text relies on.

Other supplementary items are listed with a one-line reason they were not read. A
supplement item the main text never cites and that falls under none of the seven kinds
may stay listed.

## When something cannot be obtained

Keep the entry `unobtained` and report it to the user at once, in the same turn the
failure is found, not only in the final summary. The report has three parts:

1. **Places tried** and the outcome of each (not found, access denied, paywall,
   broken link, wrong version), so the user can judge what else to try.
2. **What is wanted**: which statement, figure, method, dataset or number the main
   text takes from it, where the note needs it, and what the note cannot say without it.
3. **Free alternatives** the user could fetch instead: an open-access version, a
   preprint, an author or repository copy, a closely related open source that contains
   the same statement or figure, each with its link and what it would and would not
   replace. Give the link to the page that carries the item (and, where a site demands
   a visit to a landing page first, say which one), because direct file links are often
   refused.

"The download failed" is a recorded outcome, not a reason to stop reporting and not a
reason to fill the gap.

**No AI-created stand-in without permission.** Do not synthesise a replacement for an
unobtained resource (a missing figure, table, dataset, supplement item, code, a
sketch of "what the item would show") unless the user has given permission for that
resource. Permission is per resource: it names the entry, is recorded with its date and
wording, and does not extend to other entries or to later work. A general permission
("fill gaps as needed") is not a permission. When asked, say what would be made and how
it would be labelled. A stand-in made with permission is labelled AI-created under
[R5a](source-rules.md), shown beside the open entry, and never closes the entry; the
gate below reports the entry as open. Computations and experiments the note itself
requires (running the authors' code, checking a claim) are not stand-ins and follow
[execution](methods.md#execution-environments). Running the authors' code on the same data
obtained again, or on a substitute dataset of the same kind, to show a figure is such an
execution, under the levels and labels of [reproducing figures](methods.md#reproducing-the-papers-figures).

## Intake and proposal

Cited works, supplements, code and data are collected, fetched by open routes only, proposed to
the user (with substitutes asked, never assumed) and accepted when supplied, as set out in
[literature intake](literature-intake.md); its record `intake.json` is the ledger's source for
what is obtained, asked, avoided or substituted.

## Request list

When the user will fetch material, keep one request list beside the ledger and give it to the
user whenever it changes (at the latest after review, [R32](review.md)). One line per item:
what to fetch (named precisely: dataset and file, supplement item, figure source, code
repository and version), the page to get it from (the landing page, not only a file link),
which figure, panel or unit it serves, and what it enables (the reproduction level it would
reach, or the statement the note could then make). Mark items the writer could not fetch and
why. When the user supplies an item, record it as `obtained` with its identity and remove it
from the list.

## Coverage gate

`scripts/check_coverage.py` reads one data file holding this ledger and the other
coverage records ([lineage](lineage-and-comparison.md),
[unit chain and claim gloss](unit-chain-and-claim-gloss.md)). For the ledger it reports:
an entry without status; a must-read entry not `read`, or `read` without the unit that
uses it; an `unobtained` entry without places tried or without the stated request; a
stand-in that is not labelled AI-created or has no recorded per-resource permission
(`permission`: who, when, wording); and open entries, which block completion
unless the user has accepted them in writing. A passing gate means the records are
complete and consistent. It does not show that the text is faithful or understandable;
review checks those under [Review](review.md).
