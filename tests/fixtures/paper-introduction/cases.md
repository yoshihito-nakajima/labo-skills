# Synthetic introduction tasks

Use each case independently. All named works, excerpts and research records
below are fictional task-local artifacts, not leads for real-world citation.
Treat the supplied comparisons as the entire synthetic source corpus. These
are raw task packets for forward use, not expected answers or quality scores.

## Case A

Request: Write an introduction of about 300 words for a mathematical audience
who knows functions on finite sets. I care about why observing only recurrent
states can lose information, not about selling a new periodicity theorem.

Author note: On the set {a,b,c}, compare f(a)=b, f(b)=b, f(c)=c with
g(a)=c, g(b)=b, g(c)=c. The recurrent states and their transitions agree,
but the eventual destination of a differs. This is the motivating example.

Current result: For a function f on a finite set X, label each x by the cycle
eventually reached by its forward orbit. A subset of X is a union of these
label classes if and only if its membership indicator is constant on each
basin of attraction. This is a restatement of the basin partition, not a
stronger periodicity result. The paper uses the labels to express exactly
which unions of basins a cycle-only description fails to specify.

Proof note: A finite forward orbit repeats. Determinism gives a unique eventual
cycle. The resulting assignment partitions X. Each union of its fibers has
constant membership on every fiber, and the converse follows fiber by fiber.

Inspected predecessor excerpt: Example [P], Section 2, defines the same basin
partition and proves eventual periodicity for every finite self-map. Section 3
classifies cycles; it does not claim that cycle transitions identify every
point's basin. Its notation is a partition rather than labels.

Positioning record: The mathematical partition and eventual periodicity are
inherited from [P]. Both current examples have been checked. No claim about
historical priority is recorded. There are no computational timing results.

## Case B

Request: Draft a short introduction for specialists familiar with constrained
minimization. Keep the exact theorem conditions visible.

Current theorem: Let F be continuously differentiable on a neighborhood of
[-1,1], with F'' existing and strictly positive there. If F'(-1)<0<F'(1),
there is a unique minimizer in (-1,1), characterized by F'(x)=0.

Proof record: Continuity of F' and the endpoint signs give a zero by the
intermediate value theorem. The mean value theorem applied to F' makes it
strictly increasing because F''>0. Hence there is one zero, and the sign of
F' on either side establishes the minimum. No multidimensional or nonsmooth
argument appears in the record.

Prior excerpt [Q], Theorem 4: A quadratic polynomial ax²+bx+c with a>0
and derivative of opposite strict signs at -1 and 1 has a unique interior
minimum, obtained by solving 2ax+b=0.

Current notes: The theorem admits nonquadratic examples such as F(x)=x⁴+x².
The useful point is the one-dimensional derivative mechanism rather than a
closed-form formula. The introduction currently says “We solve general convex
optimization.” Author asks to preserve the simple interval example.

Synthetic positioning record: Only the stated [Q] comparison is inspected;
the broader literature relation is unresolved. The manuscript has no Lean
formalization. Its figures plot two examples, not a benchmark study.

## Case C

Request: Assess this introduction and suggest a better telling order. Do not
edit any files or write replacement paragraphs yet. Audience: applied scientists.

Introduction: “Our algorithm is the first complete solution to inference under
measurement error. Its universal guarantee opens the way to reliable scientific
discovery. Section 2 defines the method. Measurement is important throughout
science. We prove consistency and run experiments.”

Record: The current proof establishes convergence in probability of the sample
mean for independent identically distributed real observations with finite
variance. It does not model measurement error. An experiment compares sample
means for two simulated distributions, with 20 replicates per sample size.
There is no finite-sample coverage theorem. The author says the interesting
point is the contrast between the two simulated convergence paths. No
comparison sources or positioning memo are supplied.

## Case D

Request: Write an introduction from these notes for a broad mathematical
audience. The author likes the question of what local observations determine.

Plan: A reconstruction theorem should recover a graph from all radius-two
neighborhoods. The draft abstract says the theorem holds for every finite graph.
Proof file excerpt supplied: “Assume the graph is a tree and each vertex carries
a distinct label. Match equal labels across neighborhoods. [Need to check the
unlabelled case.]” No theorem statement or remainder of proof is available.
There is no literature-comparison record. The author has not authorized a
change to the mathematical claim or a new research direction.
