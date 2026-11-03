# Keep the role skeleton visible in two-part headings

Use for authored section/subsection headings in structured explanations. The
owning workflow or agreed artifact outline supplies the role skeleton. This
contract does not impose headings on a short answer or paragraph, rename theorem
labels or captions, or rewrite a source's titles and faithful translation.

## Name the subject before its roles

At the entrance to a named method, concept or algorithm unit, identify what is
being explained by its established name, with its abbreviation when relevant,
before the background starts. Keep **subject identity**, **structural role** and
**concrete point** distinct: a heading naming the method owns the subordinate
`Background | ...`, `Method/implementation | ...` and other roles. A descriptive
promise about what the method does cannot replace its name. When the existing
source heading already identifies it, use that heading; otherwise add a clearly
labelled subject line or subordinate heading without rewriting the source title
or inventing a new name. Do not repeat the subject name in every paragraph.

Before each method-code block, visibly name its algorithm and implementation,
for example `Named method — author implementation` or `Named method — teaching
implementation`, adding the operation for an excerpt when helpful. A function
identifier or an explanation of the calculation alone may not identify the
method. This pre-block identity complements the immediate post-block source row
required by the reading workflow; it does not move or replace that attribution.
Use these identities consistently in visible headings, contents and bookmarks.

At a new unit's entrance, also make its relationship to the preceding unit
intelligible: continuing the argument, comparing an alternative, checking the
original, or entering a collection for a different task. Label that task and scope
under the owning workflow's view contract; duplicating the complete account does
not by itself supply a new reading purpose.

## Fix the skeleton, then write the titles

Before drafting or restructuring, identify the required roles, their order and
section boundaries. Preserve the agreed skeleton across comparable methods and
within views serving the same purpose. Optional views select roles appropriate
to their declared task; a code collection need not repeat every background role.
Where a source hierarchy must be
preserved, put these role sections beneath the owning source section/method;
retain its numbers, titles' meaning and order. The computational-method skeleton
is specified by [Applications to code](../../reading-reference/references/application-to-code.md).
For other structured explanations, use the roles suited to the requested artifact;
do not import computational roles into a proof or invent an implementation.

Each role section needs a heading with two visible parts:
**structural role | concrete point of this section**. In Japanese, for example,
`障害｜近傍が空の観測点では平均を定義できない` names both the stage and the
specific difficulty. A colon or another clear separator is equivalent; the
criterion is meaning, not a required glyph. A label such as "Supplement" records
provenance, not the role. "Background" alone omits the point; a concrete title
alone omits the role. A role followed by "explanation of this role" adds no point.

Keep role names and granularity stable within the artifact. The concrete half
states what this particular section establishes, asks or does; it must not claim
more than its evidence or execution status supports. Use the same two parts in
visible headings, contents entries and bookmarks where present. A good title
helps the reader predict both where they are in the argument and what they will
learn there.

Role boundaries remain identifiable even when adjacent roles address one problem.
Do not collapse background, obstacle, implementation and fit into one unlabeled
unit merely to improve flow. Combine unnecessary divisions *within* a role, and
carry the prose across the retained boundary. Several operations can share one
method/implementation section; do not restart the full skeleton for every code
excerpt. If a requested scope genuinely changes the needed roles, state the scope
and adjust its skeleton explicitly rather than silently hiding or dropping a role.
Preserve required evidence/search/execution sections as well as the main argument.

At each opening, take up the actual preceding result or unresolved question and
show what this section will do with it. The concrete half of the title must be
fulfilled in the body, whose conclusion advances the next role. Apply
[adjacent-passage continuity](../SKILL.md#carry-the-argument-across-adjacent-passages)
inside and between roles; headings cannot replace the prose connection.

## Audit the headings against the body

Check the outline against the agreed skeleton first, then read each heading,
its opening and body, and the adjacent ending/opening in reading order. Apply:

- **H1 Skeleton:** Are the required role sections present, ordered and bounded
  as agreed, at the right level under the source hierarchy? Content buried in
  another role does not repair a missing boundary. Is the named subject visible
  at the unit entrance, before its roles, and is each code block identified by
  method and implementation before it starts? Check each reading route.
- **H2 Two parts:** Does the heading explicitly name both the structural role
  and a concrete point/task? Neither half alone, or a vacuous second half, passes.
  A subject name supplies identity at the owning level, not a substitute for
  these two parts; a concrete message cannot supply a missing subject name.
- **H3 Fulfillment:** Does the actual body perform the named role and support
  the concrete point? A formally correct heading above unrelated text or an
  unsupported claim fails. Inspect the passage; do not infer it from the title.
- **H4 Progression:** Does the opening take up the preceding content, and does
  the section's result explain why the next role follows? Specific titles and
  words such as "next" do not establish this connection. At a source-reading or
  optional-view boundary, can the reader distinguish original confirmation from
  selected explanatory material, and understand the purpose of that transition?
- **H5 Consistency:** Are role names, hierarchy and granularity consistent across
  comparable units within each declared scope, with content-specific second halves? Check
  rendered headings/bookmarks where making a PDF-navigation claim. Repeating
  the five roles at each small operation also fails the intended granularity.

Locate failures by criterion and actual heading/passage, with the smallest
repair: restore a role boundary, supply the missing half, correct an unsupported
message, or reconnect the prose. During authoring, repair these before delivery;
a review-only task reports them without rewriting. A list of headings or a regex
for separators cannot certify H1, H3 or H4. Record uninspected bodies/rendering
as limits; do not invent findings or force headings into an unsectioned answer.
