# Research-positioning task packets

These small, public inputs support forward-use checks of the skills. They are
not executed by the unit suite and do not certify search completeness. Supply
only one task and its raw artifact to a fresh worker; do not supply another
worker's conclusions or an expected answer. Use disposable workspaces, not
private research. Never present fictional sources as real search results.

## Manuscript drafting with live source access

Request: Rewrite the introduction of this short English mathematical note so
that its research contribution and significance are clear. Leave the theorem
and proof unchanged. The note consists only of this result. Use `paper-writing`.
Do not build, publish or contact anyone.

Artifact:

```tex
\documentclass{article}
\usepackage{amsmath,amssymb,amsthm}
\newtheorem{theorem}{Theorem}
\title{Iteration on complete metric spaces}
\begin{document}
\maketitle
\section{Introduction}
We establish a new convergence principle for strict contractions on complete
metric spaces. The theorem below is our main original contribution.
\section{Result and proof}
\begin{theorem}
Let $(X,\delta)$ be a nonempty complete metric space and let $\Phi:X\to X$
satisfy $\delta(\Phi x,\Phi y)\leq\sigma\delta(x,y)$ for all $x,y\in X$,
where $0\leq\sigma<1$. There is a unique fixed point $u$, and for every
$x_0\in X$, the iterates $x_{n+1}=\Phi x_n$ converge to $u$.
\end{theorem}
\begin{proof}
Induction gives $\delta(x_{n+1},x_n)\leq\sigma^n\delta(x_1,x_0)$.
For $m>n$, the triangle inequality gives
$\delta(x_m,x_n)\leq\sigma^n\delta(x_1,x_0)/(1-\sigma)$.
Thus the iterates are Cauchy and converge to some $u$ by completeness.
The Lipschitz bound gives continuity of $\Phi$, so $\Phi u=u$.
If $\Phi v=v$, then $\delta(u,v)\leq\sigma\delta(u,v)$, whence $u=v$.
\end{proof}
\end{document}
```

## Exact local edit

Request: In `writing/note/main.tex`, correct only `contarction` to
`contraction`. Change nothing else. Use `paper-writing`.

Artifact:

```tex
\section{Introduction}
This note recalls the contarction mapping theorem.
```

## Report-only comparison with supplied fictional sources

Request: Assess the contribution and notation of the supplied draft. Use only
these passages; do not search externally or edit/create files. They are
fictional primary-source excerpts for this bounded question. Report what can
and cannot be concluded from them. Use `paper-referee` for the draft, reading
it before the comparison material.

Draft:

> Our novel generalization proves that a contraction on a nonempty compact
> metric space `(Y, rho)` has a unique fixed point, reached from every initial
> point. We write the map as `G` and its contraction constant as `a in [0,1)`.
> Our proof sums the geometric bounds on successive iterates. Earlier work
> used different notation. This new notation makes our result more general.

Comparison material to inspect after the initial reading:

- Vale (fictional), *Contractive iterations*, version 1, Theorem 2, pp. 4–5:
  on any nonempty complete metric space `(X, d)`, a map `T` with
  `d(Tx, Ty) <= q d(x, y)` for all `x,y` and a fixed `0 <= q < 1` has a unique
  fixed point, and every iterate sequence converges to it. The proof sums
  geometric bounds on successive iterates and uses completeness.
- Supplied elementary fact: every compact metric space is complete.
- A prior memo claims that three unspecified searches found no predecessor;
  it supplies no query strings, dates or inspected-source locators.
- A bibliography lead, Reed (fictional), *Equivalent formulations*, version 2,
  is listed as relevant but its text is not supplied. No theorem or historical
  priority claim can be attributed to its unseen text.

## Changed boundary / submission refresh

Request: Our existing manuscript assumed a compact metric space. We now use
a complete metric space, with the same uniform contraction constant, and want
to describe the change as an extension in the introduction before submission.
Inspect the current statement against the sources, update the existing
positioning record and proposed wording, and do not change the theorem or proof.

Use the current draft and a prior memo with exact source versions, query dates,
comparisons, and notation decisions. Supply live source access for this task;
do not invent a search history. A previous pass or a no-hit entry alone is not
evidence about later work. No production repository or submission action is
part of this packet.
