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

## Close definitions as well as proofs

Check two obligations separately: the reader can interpret the definitions and
statements, and the promised constructions and arguments are justified. A correct
proof or a reference to its owner does not supply missing meanings.

At each definition and imported statement, trace the mathematical vocabulary in
its defining clause, hypotheses and notation to earlier explanations in this text,
exact restatements in its preliminaries, or the explicitly agreed reader inputs.
Apply the same check to those prerequisite definitions until reaching that input
boundary. Include the preliminaries themselves in this reading-order check: a
term defined later does not make an earlier statement readable on first use.
Do not retrospectively declare missing vocabulary familiar to the reader.

Check that a definition specifies its objects and data, the domains and codomains
of operations, defining conditions and relevant conventions. Spell out axioms
whose compressed names would otherwise require undeclared knowledge. For example,
a module definition uses a ring and an additive abelian group; those notions and
the needed operation laws must already be interpretable. Resolve conventions such
as units, commutativity, left/right actions and preservation by homomorphisms when
they affect the text. Distinguish axioms specifying a structure from obligations
to construct an example or prove induced operations well-defined; a definition
itself does not need a proof.

For a book promised readable from its own preliminaries, “defined in the previous
volume” is not a substitute for the necessary local definition. Restate its exact
content and conventions, while preserving one canonical owner and the existing
proof path. A specialized text may accept more vocabulary only through its agreed
input boundary. Stop at that boundary; do not reconstruct all earlier mathematics
or explain every ordinary word. Use examples or nonexamples where they resolve a
real ambiguity, without imposing one for every definition.

During normal author self-check and bounded review, report the first unresolved
term, its use location, the missing dependency and the minimal local repair.
Check definitions and statements in the assigned scope with their direct inputs;
do not require a course-wide glossary, a new dependency database, or a separate
review request for every definition. After a definition or convention changes,
check affected statements and uses even when their proof text did not change.

## Make mathematical structures explicit

Every mathematical structure used by the text must have an interpretable local
definition, including structures recalled as prerequisites. Apply this to
algebraic, topological, measure-theoretic and analytic structures alike. Stop the
recursive definition check at explicitly declared basic language and axioms, not
at a subject name or an unexplained structure assumed familiar. In a book promised
readable from its own preliminaries, restate the required definitions there or
before first use in the body.

For a structure, specify:

- its carrier object or objects;
- its designated data: operations, maps, relations, families of subsets,
  distinguished elements, or other components;
- the type of each component, including domains, codomains and allowed values;
- the axioms with their quantifiers and side conditions, so the reader can test
  whether given data constitute the structure;
- the adopted conventions and any additional properties assumed for this use.

A tuple of unexplained letters or a list of law names is insufficient when the
reader cannot recover their exact conditions from earlier local definitions or
the declared basic inputs. Precise prose is acceptable; do not require every law
to be written symbolically. After an adequate introduction, use normal abbreviations
rather than repeating the full definition at every occurrence. Identify which
data are suppressed when writing a carrier's name for the whole structure.

For example, recalling a measure space `(X, F, mu)` requires a set `X`, a family
`F` of subsets of `X`, and a map `mu: F -> [0, infinity]` into the extended
nonnegative reals. State that `F` contains
`X` and is closed under complements in `X` and countable unions, that `mu(empty)=0`,
and that `mu(union A_n)=sum mu(A_n)` for every pairwise disjoint sequence in `F`.
Explain measurable space before using it in that definition, or define it there.
Completeness, sigma-finiteness and probability normalization are additional
conditions; do not silently build them into all measure spaces. Likewise,
resolve whether rings have units, whether they are commutative, and whether
homomorphisms preserve units.

Check component notions by the definition-closure rule above. For substructures,
quotients, products, completions and morphisms, give the induced data or preservation
conditions actually used. Separate defining a class of structures from constructing
an instance: the latter needs closure, well-definedness (including independence
of representatives), and the required axioms, proved here or supplied by the exact
permitted result. Declaring the axioms does not establish that an instance exists.
A local restatement of a field's laws does not require repeating the construction
of the real numbers; preserve its proof owner and import boundary.

Register each concept actually defined, including additional properties, and
meaningful introduced notation in the relevant indexes, with a route to its exact
introduction. A single definition environment may define several concepts, each
requiring its own usable lookup. Component variables need not each become a new
index entry. When extracting a volume, retain the definition and its index and
reference registrations in that volume's actual inputs. Link validity and semantic
coverage are separate checks; follow mathematical-navigation for their implementation.

Apply this contract during ordinary unit self-check and the existing bounded
mathematical/output reviews. Locate missing data, axioms or conventions and the
smallest repair; do not create a separate job or full rebuild for each definition,
or require a new global structure registry before writing can continue.

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
