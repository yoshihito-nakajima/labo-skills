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
  Before choosing a replacement, look for the corresponding original-author
  implementation through the paper/supplement software links and author project
  pages or repositories. Prefer relevant inspected author code when available
  and reusable; explain material adaptations or the reason for another route.
  Record where you looked and distinguish not searched, found but uninspected,
  found but unsuitable/inaccessible, and not located within the searched scope.
  Show the applicable status near the method/code; an independent implementation
  does not establish that author code is unavailable. Do not invent a search
  outcome or treat a discovered repository as inspected implementation evidence.
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
  changes. Do not fabricate missing revision or license information: state the
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
