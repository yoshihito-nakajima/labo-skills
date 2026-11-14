# Volume entrances and borrowed results

Use when planning a volume or preparing its opening. The planner owns the
prerequisite interface; course-authoring writes and integrates the mathematical
text under its normal proof and review standards.

## Define self-containedness by declared inputs

Apply this contract to a book, course, lecture text or long note, whether
introductory or specialized. A label such as “foundations,” “advanced,” or
“preliminaries” does not determine what may be assumed. The project must name
its intended reader, adopted results to establish, and precise permitted inputs.

A text is self-contained **relative to its explicitly declared inputs** when every
adopted construction and argument can be followed using those inputs and what the
text itself defines and proves. Every substantive dependency must terminate in a
declared input or an internally established result, without hidden assumptions or
circular proof dependencies. Definitions, hypotheses, intermediate calculations,
necessary exercise solutions and application conditions are part of this closure.
State the qualification “from these prerequisites”; do not describe such a text as
requiring no prerequisites.

Declare three things separately:

- Background conventions or axioms accepted without reconstruction.
- Established mathematical results accepted as starting facts, in the exact form
  used, with source/version and the definitions needed to interpret them.
- New adopted content whose constructions and proofs this text promises to give.

The preliminaries make the first two visible and usable. They do not discharge
the third. A subject name or an external reference alone does not specify an input.
The reader must not need an original source merely to recover a missing definition,
hypothesis or proof step above the declared input boundary. Proofs of explicitly
accepted inputs may remain at their source; clearly identify that boundary and a
proof path for readers who want to inspect them.

Do not add inputs retrospectively merely to conceal a missing proof or make an
order acyclic. Moving adopted content into assumed prerequisites changes scope:
state the result, reason, downstream effect and remaining obligation, and follow
the project's scope-change agreement. A source sketch or “standard” result is not
implicitly an allowed input. Unproved or unresolved ingredients support only
explicitly conditional work, not a claim of completed unconditional content.

## Individual texts and collected works

Give each text its own input boundary. For an assembled course, also declare the
collection's common inputs. A result imported by a constituent text must then be
proved somewhere inside the collection unless it belongs to those common inputs.
Restating all inputs in each constituent does not by itself close the collection.
Conversely, a specialized standalone text need not reconstruct every prerequisite
from elementary foundations if its accepted inputs are explicitly agreed.

“Foundation course” is a project-specific name for an adopted range of results and
its entry conditions, not a universal category that activates a different proof
standard. Apply the same dependency-closure rule at every level.

For example, a project may accept ordinary logic, set operations and stated choice
principles as background rules without reconstructing axiomatic set theory. If
constructing the real numbers is adopted content, that construction and its claimed
properties still require proof. This is one possible project boundary, not a
mandatory starting point for every book.

## A useful entrance

Begin each volume with a concise account of its question, endpoint and starting
facts, then definitions, conventions and exact borrowed results that the reader
will actually use. Explain the role of important inputs and connect the entrance
to the first mathematical question. Do not reproduce a preceding volume's entire
contents or hide a new central construction in the preliminaries.

State required objects, hypotheses, conclusions and normalizations. Distinguish
scalar field, completeness, separability, measure completion, and analogous
conditions whenever they affect the application. A theorem name or a general
instruction to know a subject is not an adequate prerequisite interface.

Use a project-specific size allowance rather than a universal page count. Count
preliminaries in the volume estimate. If the entrance grows into a second course,
reconsider the book boundary or finish a common prerequisite unit earlier; do not
remove necessary hypotheses merely to shorten it.

## One owner, several presentations

Each definition and proof has one editable canonical owner with a stable label.
An importing volume may restate the needed claim and give a short example or
application without creating a second independently maintained proof. Mark a
restatement as borrowed, rather than presenting it as a separately owned theorem.

For each result that actually crosses a volume boundary, extend the existing
claim/version records only as needed with:

- importing volume and actual use;
- exact statement used, including necessary definitions and conventions;
- owning volume, canonical file/label and source correspondence;
- owner version or content hash and the relevant proof/review state;
- any difference between the imported and owning statements and its effect.

Populate this information at the first relevant writing unit. Do not require a
new complete theorem registry before any production can begin. Locate candidate
owners from current text, then verify their version and status before relying
on them. Existing text is not automatically established or independently checked.

## Proof status and change

An established prerequisite can be imported in the form actually proved. An
explicitly accepted axiom or starting result uses the declared input contract
rather than an invented internal proof debt. Its source and applicability must
still match the use. A draft
with outstanding defects or an unproved prerequisite remains conditional; its
restatement does not close the importing result. Keep the obligation and owner
explicit. Distinguish author self-check from independent review without requiring
a separate independent audit of every imported statement.

Resolve cycles in the mathematics or book boundaries. Do not fix an order by
declaring one direction to be known without evidence. When the owner changes,
inspect the changed assumptions/conclusions and affected uses; reuse valid evidence
for unchanged scopes. A graph checks declared edges, not their completeness or truth.

## Reader output and later integration

Show the reader an intelligible owning volume/result and proof path. Keep content
hashes, job IDs and operational status in production records, not in the reading
flow. Preserve semantic labels across volume and collected numbering. Shared
statement input must not introduce duplicate labels at restatement sites.

Implement shared statements only as far as the actual source structure requires;
a new extraction framework is not a prerequisite to planning. In the collected
edition, replace redundant restatements with internal links where useful and
rewrite entrances for the assembled route. Compare actual definitions and claims
before identifying results as duplicates. A change in strength is a mathematical
change, not mechanical deduplication.
