# Research lifecycle and narrative contract

1. A program is a question plus its research context, conjectures, methods,
   obstructions, and the story by which these change. `plan.md` is the source
   for that narrative; YAML is only an inventory index.
2. YAML `status` accepts **only** `in_progress` (進行中) or `completed` (完了).
   "paused", "parked", "draft", "submitted", and "archived" are not research
   statuses. Lack of attention does not imply mathematical completion.
3. A completed program may be reopened as in progress. The plan must explain
   what was resolved and what new question reopened it.
4. Proactively *propose* splits, integration, suspension of effort, or changes
   of approach when the research story and evidence warrant them. Give the
   rationale and alternatives; ask the human before changing boundaries.
5. Never erase a program because it looks uninteresting. Preserve its plan
   and source originals; document relationships in prose and Git history,
   not in a fragile, mandatory cross-program reference graph.
6. `research/<slug>/inbox/` stores originals untouched; notes and proposed
   interpretations are separate. Root `/inbox/` is local staging for unassigned
   input and its contents are ignored by default.
7. Develop the research story, prior-literature context, and relevant Lean
   formalization iteratively. Literature can revise the question or place a
   result in context; Lean can expose hidden assumptions, sharpen definitions,
   or reveal counterexamples and formalization gaps. Record what each source
   supports and let those findings update the story. A build containing proof
   placeholders does not establish the claimed core, and a Lean result supports
   only the statement actually formalized. Write the paper from this evolving
   evidence; its introduction is part of the story, not a detached summary.
   English is the original manuscript; Japanese is supplementary translation
   checking. Record evidence and remaining gaps in prose, without inventing
   additional research statuses or equating paper completion with research
   completion.
8. Submission order helps a reader unfold the output narrative.
   Papers may cite one another, but citation dependency does not dictate the
   order of mathematical exploration or force program-level references.
9. The human chooses the significance and tone of the story. The agent should
   challenge gaps, identify alternative questions, and record uncertainty.

10. **Claim-level evidence and prior-work comparison.** Run the mandatory
    [research-positioning protocol](../../reading-reference/references/research-positioning.md)
    for a new or substantively reframed program and refresh affected comparisons
    when the question, claims, hypotheses or method changes their relation to
    prior work. Reuse one research-level memo rather than duplicate surveys per
    paper; preserve actual search provenance, open leads, the contribution's
    lineage, and notation decisions. This investigation is required independently
    of the optional evidence catalog below. For a substantive plan,
    full research-story revision, or explicit request for the state of a
    program, give a source-grounded account of each central theorem, method,
    conjecture, and open question. For every central claim, identify the exact
    source and version, theorem or section locator, and proof record or Lean
    declaration that supports it. Distinguish an earlier theorem, its direct
    application or reformulation, the present project's new conclusion or
    proof ingredient, and what remains conjectural or unproved. Compare the
    relevant objects, hypotheses, conclusions, and proof methods; explain which
    change matters and which proof step establishes it. Verify consequential
    comparisons against primary sources. Citation silence or a failed search
    does not establish novelty; state the literature boundary and unresolved
    source gaps. For every completed central result, ensure a complete proof
    exists in the linked record: state the assumptions, expose every
    nontrivial dependency and inferential step, and identify the exact lemma or
    source used. A plan may summarize this proof architecture rather than
    duplicate a long derivation, but an uninspected pointer or the phrase
    "proved elsewhere" does not complete the evidence. Standard results may
    be used as black boxes when their statement, applicability, and primary
    locator are explicit. For unfinished claims, record a concrete proof
    route, needed lemmas, assumptions to establish, and known obstructions
    instead of presenting a proposed argument as proved. `plan.md` should tell
    the story from prior capability and its boundary through the question,
    new idea, result, proof mechanism, and next consequence; keep long
    derivations in proof records and point back to them. Routine progress
    updates need only revise the evidence and story they actually change; this
    full comparison is for substantive plans and program-level accounts, not
    every small edit. Use prose or a table as useful; no fixed claim ledger or
    file schema is required.

11. Use the optional [evidence protocol](evidence.md) for load-bearing claims
    or durable review handoffs when useful. Claim-level evidence statuses and
    dependencies supplement the narrative; they do not add program statuses,
    require a global dependency graph, or automatically certify mathematics.
    The policy checkout owns their format and checker; private records follow it.
