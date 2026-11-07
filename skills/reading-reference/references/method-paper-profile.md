# Method-paper profile: a detailed reading note for a paper whose contribution is a method with code

Use when the paper's contribution is a computational or experimental method that comes
with code, data or a pipeline (typical in life science and information science), and
the request is a detailed PDF for understanding or introducing it. It does not add
rules: it fixes which parts such a note consists of and sends each to the reference
that owns it. A starting skeleton is in `assets/method-note/`.

It is built for method-and-code papers. For a mathematical paper whose substance is a
proof, do not use the skeleton as a template without adjusting it (see the end).

## Parts of the note, in the order of the source

| Part | What it holds | Owner |
|---|---|---|
| Scope and reader floor | the paper's identity and version, what was read and not read, the assumed mathematics and domain knowledge | [unit chain](unit-chain-and-claim-gloss.md#reader-floor), [Sources](source-rules.md) |
| Spine and section map | the question, the claims in dependency order, each unit's parent, needs and produces | [unit chain](unit-chain-and-claim-gloss.md#argument-spine-and-the-chain-of-units) |
| Literature intake | the paper's supplement, cited works by relation and need, code and data: fetched by open routes, proposed to the user, substitutes confirmed, deepened where a claim needs it | [literature intake](literature-intake.md) |
| Resource ledger | every figure, method section, supplement item, code and dataset the paper consists of, with status | [ledger](resource-ledger.md) |
| Per source section | background card → mathematics and implementation → correspondence table → original → faithful translation, in the paper's order | [paper preparation](paper-preparation.md), [structure](reading-structure.md) |
| Roles in a method | what is kept from the predecessor, what fixes the obstacle, other aims, bookkeeping, the limit that remains | [roots and lenses](roots-and-lenses.md), [application to code](application-to-code.md) |
| Author code | the authors' functions shown verbatim, with licence and commit, beside the step they implement; under every excerpt, a note per block: what it does in plain words, where it comes from, how it differs and what that changes | [application to code](application-to-code.md#give-every-code-unit-a-reason-card) |
| Supplement route | main text → supplement, every code/procedure/claim-bearing item read at its call site | [ledger](resource-ledger.md#supplements-that-must-be-read) |
| Prior work and versions | one treated entry per inherited, compared, criticised or earlier-version work, with the code difference | [lineage](lineage-and-comparison.md) |
| Lineage overview | one table near the introduction: each earlier work's purpose, the paper's criticism, what the method keeps or changes, what checking the source found, and the section that treats it; related lineages the code does not show (a concept, an approach of another family) as reference rows; later developments only as a separate, sourced, auxiliary list | [lineage](lineage-and-comparison.md#overview-table) |
| Sentence-level glosses | object, known, claim and benefit for each cite, property and show sentence | [unit chain](unit-chain-and-claim-gloss.md#claim-gloss-lowering-the-step-between-sentences) |
| Execution and reproduction | the authors' code run in an isolated environment, labelled runs, what was and was not reproduced | [methods](methods.md#execution-environments) |
| Figures to present | for every main-text figure: its claim and reading, the code behind it, where the figure's difference comes from (the steps and lines that make the difference to the earlier method or between conditions, marked as the paper's statement or the note's reading), the reproduction level reached (L1–L4) and the request list for what would raise it | [reproducing figures](methods.md#reproducing-the-papers-figures), [request list](resource-ledger.md#request-list) |
| Values | one table of the parameters: the paper's value, the code's default (and the rule that sets it), the values used in each run of the note or companion | [methods](methods.md#reproducing-the-papers-figures) |
| Status | what was not obtained or not read, why, and what the user can supply | [ledger](resource-ledger.md#when-something-cannot-be-obtained) |
| Index and bibliography | terms with their defining place, the references with their identity records | [Sources](source-rules.md) |

Give each unit (section, subsection, key equation, figure) a stable `\label` as you write, with a
prefix by kind (`sec:`, `eq:`, `fig:`, `def:`). Decks and talks derived from the note cite these
labels and link to its pages ([two decks](../../deck-from-references/references/two-decks.md#link-to-the-detailed-note));
renaming a label breaks those links, so add labels rather than rename them. An appendix generated
from the decks (note label → deck pages) lets the reader go from the note to the deck.

Completion is checked with `scripts/check_coverage.py` on the coverage data (including the
`overview` record: lineage table, values table, code-block notes, figure differences), then by
[review](review.md).

To prepare the presentation by seeing and moving the paper, build a private HTML companion with
[reading-companion](../../reading-companion/SKILL.md). Plan it while writing the note: the
companion adds no claim the note does not carry, so it is built from the parts above: the
lineage overview (its introduction), the code-block notes (its same/changed lists), the
difference sources and the figure part (its figure units) and the values table (its controls).
Write these as you read, not afterwards; they also give the note's reader a map. Review judges
readiness ([R32](review.md)).

## Working order


1. Fix the paper, its version and its supplements; build the ledger and the
   [intake record](literature-intake.md), obtain what can be obtained by open routes, and give the
   user the proposal table (what is asked, what substitute is proposed and why) before reading on.
2. Write the scope, spine and section map; list the lineage entries.
3. Read and write section by section in the paper's order, adding resources and works that
   turn up on the way to the ledger and obtaining them.
4. Obtain the authors' code, read it against each step, run it in an isolated environment,
   and compare versions when a prior version exists. For each main-text figure, record the
   code behind it and run it at the highest [reproduction level](methods.md#reproducing-the-papers-figures)
   available, using substitute data when the authors' data cannot be obtained.
5. Write the status part, run the coverage gate, review (including figure readiness, R32),
   give the user the request list, and repair.

## Do not fill gaps with invented material

A missing figure, dataset, supplement item or code is reported, not replaced. An
AI-created stand-in exists only with the user's permission for that resource
([ledger](resource-ledger.md#when-something-cannot-be-obtained)). Label every run, figure and
code unit by its provenance class (R5a) so the reader can tell the paper from the
added material.

## Mathematical papers

The note parts for scope, spine, original and translation, unit chain, sentence glosses and
lineage carry over. The parts built around code and runs do not: a proof-centred paper has
no pipeline to execute, and its roles, correspondence tables and reproduction part should
be replaced by the dependency and proof-checking material of [methods](methods.md) (the
mathematical branch) and [mathematical exposition](../../mathematical-exposition/SKILL.md).
Use this profile for a mathematical paper only when it is also a method paper (a numerical
scheme with an implementation), and say which parts were replaced.
