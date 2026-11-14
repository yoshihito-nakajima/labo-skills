---
id: thm-sum-settled
kind: theorem
label: thm:sum
title: "Sums \\cite[Lemma~2]{Fictional2001}"
requires: [def-settled, lem-tail]
status: drafted
questions: ["Is the bound N(a+b) <= max(N(a),N(b)) sharp?"]
---
## Statement
If $(a_n)$ and $(b_n)$ are settled, so is $(a_n+b_n)$, and $N(a+b)\le\max\{N(a),N(b)\}$.
## Proof
(1) Let $M=\max\{N(a),N(b)\}$ and $n\ge M$. (2) By lem-tail, $a_n=a_M$ and $b_n=b_M$. (3) Hence $a_n+b_n=a_M+b_M$, so the sum is settled with index at most $M$ (def-settled).
