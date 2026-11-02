# Terminology-audit task packets

These synthetic packets support forward-use checks, not automated semantic
tests. Use a disposable workspace and the actual skills. Supply the manuscript
first, then the relevant fictional corpus sources. Keep findings report-only;
do not edit manuscripts, populate a live corpus or present fictional sources
as real literature. Record initial local understanding before comparison.

## Supremum role label

Request: Audit the names and notation in this paragraph, using the supplied
same-role corpus material where relevant. Give findings and the smallest
repair obligations; preserve the exact mathematical claim.

Manuscript:

```text
Let A=(0,1) and J(a)=a for a in A. Set S=sup_{a in A} J(a)=1.
Every test a satisfies J(a)<S. The bound S need not belong to A.
```

Fictional corpus source, *Suprema of real sets*, synthetic version 1,
Definition 1 and Example 2: a supremum is a least upper bound. In
`sup_{a in A} J(a)`, `a` ranges over elements of the admissible set A.
For A=(0,1) and J(a)=a, the supremum is 1 and is not attained.

An additional fictional distribution-theory source defines test functions
as smooth compactly supported functions. Its word “test” occurs frequently.

## Defined test functions

Request: Review terminology in this passage against the relevant supplied
definition, retaining coherent mathematical names and stating source scope.

Manuscript:

```text
Let D(R)=C_c^infinity(R), the space of smooth compactly supported functions
on R. We call its elements test functions. Fix a test function phi in D(R).
```

Fictional corpus source, *Distributions: local definitions*, synthetic
version 1, Definition 2: D(R) is C_c^infinity(R); its elements are called
test functions. Here “compactly supported” and “smooth” apply on R.

## Fourier normalization with an actual source page

Request: Check the draft's Fourier convention against this corpus entry.
Inspect the rendered source page and identify its exact version; an extracted
text derivative is also available. Report any inconsistency or valid convention
translation, with the effect on the formulas. Do not rewrite the draft.

Manuscript:

```text
For a Schwartz function f on R, define
hat f(xi)=integral_R f(x) exp(-i*x*xi) dx.
Our inversion convention is
f(x)=(1/(2*pi))*integral_R hat f(xi) exp(i*x*xi) dxi.
```

Build the following fictional source into a temporary PDF with printed page 1;
retain the TeX as its source. Identify it as synthetic version 1. A derivative
extraction to supply separately reads `exp(+2*pi*i*x*eta)` for its forward
transform and omits the inversion line.

```tex
\documentclass{article}
\usepackage{amsmath,amssymb}
\begin{document}
\section*{Fourier conventions: synthetic version 1}
Definition 3. For a Schwartz function $f$ on $\mathbb R$, set
\[
  \mathcal F f(\eta)=\int_{\mathbb R}f(x)e^{-2\pi i x\eta}\,dx.
\]
The inversion formula is
\[
  f(x)=\int_{\mathbb R}\mathcal F f(\eta)e^{2\pi i x\eta}\,d\eta.
\]
This is a fictional source for a terminology-audit exercise.
\end{document}
```

## Absent corpus coverage

Request: Check the local definition and terminology using only the supplied
material. No relevant corpus source or external access is available for this
bounded exercise. State what can be checked and what remains unverified.

Manuscript:

```text
An admissible probe is, by definition here, a pair p=(u,v) of nonnegative
real numbers with u+v=1. Write P for the set of these pairs. For p in P,
let L(p)=u-v. We use this local terminology only in this section.
```
