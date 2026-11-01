# Explain a research program from its evidence

Use this mode when the request asks for an account of a research program or a
connected body of local work: plans, proof notes, papers, source literature,
formalization, or several projects. It supplements the paper- and
book-centered workflow in `SKILL.md`; it does not turn every ordinary paper
reading into a field-wide survey.

## Scope and evidence map

Start from the user's requested program and reader outcome. Inspect its plan,
central proof records, relevant reading/reference notes, paper drafts, and Lean
coverage. Identify the main claims and their dependencies before drafting. For
each central claim, record in prose or a compact table:

- its exact statement, assumptions, and current status;
- the primary source/version and precise theorem, section, page, file, or
  declaration that supports it;
- any direct predecessor and what that predecessor actually establishes;
- the proof record or formalized declaration for the current claim, including
  what remains outside that evidence;
- the decisive proof mechanism, its dependencies, and any unresolved step.

Do not infer a result's status from a plan, title, build success, or nearby
formalization alone. A formalized result is only the statement and assumptions
in the checked declaration. Keep proved informal arguments, manuscript claims,
conjectures, proposals, and open questions visibly distinct.

## Compare prior work at the mathematical boundary

For every central contribution, verify the direct predecessor and the primary
sources needed to understand the comparison. State what is inherited, what is
a direct consequence or reformulation, and what this program adds. Compare the
objects, hypotheses, conclusions, and proof methods at the level where they
differ. Explain which difference creates the new question and which new proof
step addresses it. Do not call a result novel because a search found no match,
because a paper omits a citation, or because a local plan describes it as new.
Separate a checked comparison from the authors' own positioning, and leave
inaccessible or unresolved comparisons open.

As a schematic check, if a predecessor proves a statement under hypothesis
$H_0$ and the current result uses $H_1$, say whether the hypotheses are
comparable or incomparable, compare the conclusions, and identify which new
argument supplies any claimed extension. Call it a generalization only after
checking that relation against both statements.

Define a useful literature boundary rather than starting an unbounded citation
crawl: include the direct predecessors and the background results necessary
to state, prove, or compare the program's central claims. Follow further
references when they are named as dependencies or materially affect a novelty
claim. Record source versions and exact locators. State the boundary and any
missing primary evidence in the delivered account.

## Reconstruct the proofs and the story

For every central result in the requested scope, lead the reader through the
definitions and hypotheses, the obstacle, the full dependency chain, each
nontrivial inferential step, the decisive argument, and the conclusion. The
reader should be able to follow the proof from the account itself without
opening an unmentioned proof note. Routine standard lemmas may remain black
boxes when their precise statement, applicability, and primary source are
given. Inspect the proof record rather than trusting its title or summary. If
it omits a needed step, reconstruct it only when the sources justify the
reconstruction and label the addition; otherwise keep the gap explicit. A
link or a proof roadmap does not replace requested proof exposition.

Tell the program as an evidence-led sequence: what earlier work made possible,
where its scope ends, why the current question follows, what idea changes the
available tools, which theorem the new argument proves, and what that result
opens or leaves unresolved. This is a mathematical explanation, not a
chronological activity log. Keep the author's stated motivation distinct from
the explanatory narrative added for the reader, and do not force a claim of
novelty or superiority.

## Completeness and handoff

For a request for the whole program, a high-level overview is an opening, not a
finished deliverable. Cover all central results in the requested scope, their
proofs, the necessary background literature, relevant prior-work comparisons,
and exact evidence boundaries. If the requested scope is too large for one
artifact, divide it into coherent installments while continuing the remaining
work; state which units are covered and which remain. Keep detailed derivations
in their research records when appropriate, but link them at the relevant
explanation and explain the complete central argument in the reader-facing
artifact itself.

Before handoff, check the account in both directions: every central claim in
the guide must lead to inspected evidence, and every in-scope central result
and comparison in the evidence map must appear in the guide. Distinguish source
verification, proof reconstruction, Lean inspection/build evidence, and
rendered-output checks. Report actual gaps rather than treating their
disclosure as a substitute for requested coverage.
