# Reconstruct the relevant method

Apply the branches the source actually uses. Missing data, code or figures
in a purely theoretical source do not create empirical tasks.

## Mathematical arguments

- **R15 Dependencies** — Trace definitions, statements and proof steps to
  exact source locations. Each dependency ends in an explanation, declared
  reader knowledge, a permitted usable black box, or a named open gap. Detect
  circular use, including exercises that assume the result they are used to prove.
- **R16 Applications** — Give the actual input objects, theorem hypotheses,
  substitutions and conclusion. Reconstruct essential omitted estimates,
  constructions, limit interchanges and diagram identities. Track quantifier
  order, choices, constant dependence, uniformity and exceptional cases.
- **R17 Scope** — Explain why important assumptions are needed and check any
  illustrative example or counterexample. Preserve the distinction between an
  author proof and an added reconstruction. A numerical check is not a general
  proof; a claimed Lean verification needs the actual matching declaration.
  For books, include in-scope exercises and solve those requested or needed for
  the argument; listing an exercise does not mean it was solved.

## Algorithms and computation

- **R18 Target** — Choose the paper's procedure, an inspected fixed code
  revision, or both with a declared main route. Preserve discrepancies in
  defaults, inequalities, ties and library behavior. Keep source-reported,
  statically inspected, pedagogical and actually rerun results distinct.
  For paper preparation or requested code, identify all in-scope computational
  methods and their
  primary papers before selecting implementations. For each, identify the
  corresponding author implementation, inspected library version or explicitly
  independent implementation, and map its operations to the source procedure.
  An API call without inspecting the relevant implementation cannot establish
  this match. Do not describe a convenient substitute as the paper's code.
  For every literature-based implementation unit, including educational,
  background and auxiliary code, trace the actual method paper/version and
  exact equation, algorithm or procedure before choosing an implementation.
  Actually inspect its software pointers, supplement, author project pages and
  linked repositories for corresponding author or official code. This applies
  when choosing independent teaching code from the outset, not only when
  replacing an existing implementation. A search for a different central method
  or a survey-level software list does not cover this unit. Unrelated setup
  commands and syntax-only illustrations do not require author-code searches.
  When matching code is found, inspect the relevant file/function and compare
  it with the cited procedure and proposed teaching code. Prefer relevant,
  inspected and reusable author code; explain adaptations or the concrete reason
  for retaining an independent implementation, with consequential differences.
  A discovered repository alone is not an inspected implementation.
  Before writing independent code, state the reader's explanatory or computational
  purpose and compare the matching implementation's existing options, a thin
  wrapper and an annotated excerpt with the proposed independent route. Identify
  the concrete requirement and how each relevant option meets or misses it.
  "Educational", shorter code, a later author, or an already working draft alone
  does not justify choosing independent code as the main execution or reproduction
  route. A source-grounded execution route may have a separate independent
  explanatory example. Author provenance alone does not establish suitability.
  When matching code is discovered after an independent draft exists, reopen
  the choice against the request; do not merely append a reason to retain it.
  Consider switching routes, keeping the draft as a bounded explanatory example,
  or retaining it with a concrete reason. Past effort or a successful toy run
  cannot settle this choice. Reconsider whether the evidence would support the
  same route if the independent draft did not already exist.
  At each unit's reader-facing location, name/link the places actually checked,
  report their outcomes and the resulting implementation choice. Distinguish
  not searched, found but uninspected, found but inaccessible, inspected but
  unsuitable/reuse-restricted, and not located within the searched scope. If a
  paper's software pointer or supplement was not followed, say so explicitly
  and retain it as unfinished source work; do not claim the search is complete.
  Do not infer that code exists merely from a citation, or that it does not exist
  from an incomplete search, an access failure or the existence of independent
  code. A private log, successful toy run or generic "educational code" label
  cannot replace this local report or close an unresolved required search.
- **R19 State path** — Specify input shapes/units, stable IDs versus local
  indices, preprocessing, updates, parameter values, randomness, ties, edge
  cases, loops, stopping and saved outputs. Explain consequential constants
  and their rationale when known; do not invent historical settings. A small
  hand-worked trace should actually follow the selected method.
- **R20 Reuse** — For code understanding/reuse, including the paper-preparation requirement,
  include complete
  selected implementation units, necessary helpers/configuration, environment,
  entry commands and matching editable files, with provenance and reuse terms.
  Pseudocode or a repository link cannot replace this. Inspect before any
  execution; report what was really run and its outcome.
  Cover the central algorithms in the requested unit, not only the one easiest
  to demonstrate. Supply their essential executable units beside the relevant
  explanation, with explicit links to complete editable sources and any longer
  appendix listing. At each code unit that implements or explains a paper
  algorithm, identify the paper/version and exact algorithm, equation or step,
  with a working source link and a page/section anchor where supported. State
  locally whether the code is original-author code, an adaptation, an inspected
  third-party/library implementation or independently written for the note.
  Link reused code to its fixed revision/version and relevant file/function or
  lines where available; retain applicable reuse terms and explain consequential
  changes. Immediately after each displayed method-code block, identify its
  origin and provide a labelled link to the actual corresponding implementation:
  for GitHub or another repository, the inspected fixed revision and file,
  function or line range; for supplementary code, the actual supplement file
  or archive member and function, with a direct link where supported. If a
  supplement cannot deep-link to a member, give the archive link and the exact
  member/function visibly; do not pretend the archive opens at that function.
  A repository homepage, paper citation or generic appendix/index link alone
  is not a code-source link. For an independent implementation, link the
  complete delivered editable unit and separately identify its mathematical
  source; do not label that source as the origin of code written for the note.
  Beside that block's source/link row, give the R18 search outcome and adoption
  reason even for independent educational code. If corresponding code was found,
  link it as well and state whether it was inspected, used, adapted or not used
  and why. Report unresolved or unvisited sources explicitly; do not substitute
  a link to the note's own code for the reference's implementation-search report.
  Briefly report the actual discovery/selection order when it bears on the choice,
  evidence available at selection, the code's present role and reason, and
  outstanding comparisons. If independent code preceded the source search, say
  so; do not present a later rationale as a documented original reason. Mark
  unrecorded historical reasons as unknown rather than inventing them. This is
  a short decision record, not a request for inferred inner motives or a detailed
  thought log. Distinguish public access, permission to redistribute and ability
  to execute; an unknown redistribution license alone does not establish that
  execution or linking is prohibited or technically impossible.
  Use labels that distinguish implementation source, complete editable code,
  and the paper's equation/algorithm rather than an ambiguous "source" link.
  Every displayed method-code block also needs a nearby explanation of its
  inputs/outputs, substantive variables and operations, why they implement
  the method, and consequential settings, normalizations or deviations. Map
  those variables and operations to specific equations, algorithm steps and
  interpreted results in the explanatory body, with links to those passages
  when separate. "This implements the equations", a function name, an API
  description or an appendix dump does not supply this explanation. These
  requirements apply to author, adapted, library and independent code alike;
  they do not depend on the reader separately requesting a code walkthrough.
  Do not fabricate missing revision or license information: state the
  uncertainty and any resulting reuse barrier. A general disclaimer or separate
  provenance log cannot replace attribution beside the code. Independently
  written teaching code requires more than an origin label: explain its analysis
  question, why this example reveals the method's properties, input/output
  meaning, the source definition/equation/step behind each substantive operation,
  independent design choices, simplifications and departures from the source,
  and the basis and scope of validation. Link the supporting passages next to
  those explanations. Explain what its observed results do and do not establish;
  separate a checked static correspondence from actual execution. Do not call a
  teaching example a reproduction of the paper's experiment without the matching
  procedure, data, settings and run evidence. These requirements concern paper-method
  code, not unrelated syntax illustrations. An unrelated toy or known-answer check
  does not supply a missing algorithm or reproduce a paper's experiment.
  Match validation to the claimed correspondence. Static inspection does not
  establish numerical equivalence or a rerun. For claims of interchangeability,
  numerical agreement or reproduction, compare the required common inputs,
  settings and meaningful outputs or invariants, accounting for conventions
  such as eigenvector sign, scale or basis. If comparison was not executed,
  restrict the claim accordingly. Do not require duplicate execution of every
  explanatory function or agreement between different mathematical targets.
  Restrictions on code reuse may require a transparent independent implementation;
  unresolved source, license, data or execution barriers remain visible gaps.
  Purely theoretical reading does not require inventing a coding task.
- **R21 Comparisons** — Explain how each baseline computes its score. Check
  data splits/leakage, tuning, aggregation, uncertainty, resources and comparable
  conditions. Implementation claims need fixed code evidence on both sides.
  A pipeline-level gain does not isolate the effect of one changed operation.

## Empirical evidence

- **R22 Design** — Trace question, experimental/observational unit, intervention
  or comparison, measurement, processing, analysis and interpretation. Distinguish
  independent samples from technical replicates; explain denominators, controls,
  exclusions, normalization and missingness. Unreported is not the same as absent.
- **R23 Inference** — Preserve effect sizes, sample sizes, test assumptions,
  uncertainty definitions and multiplicity. Distinguish association from causation,
  measurement/proxy from mechanism, and nonsignificance from equivalence. Match
  conclusions to the studied population and conditions. Compare earlier studies
  only along dimensions their actual designs support.
- **R24 Visual evidence** — Read axes, units, scales, legends, group labels,
  annotations and error bars from the image, not only its caption. Explain the
  specific comparison supporting the conclusion; incompatible scales cannot
  support a direct intensity comparison. Source limitations must survive the
  explanation rather than becoming stronger claims.
