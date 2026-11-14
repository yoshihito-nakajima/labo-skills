---
id: lem-tail
kind: lemma
label: lem:tail
title: Tails
requires: [def-settled]
status: gap-free
lean: []
---
## Statement
If $(a_n)$ is settled, then $a_n=a_m$ for all $n,m\ge N(a)$.
## Proof
(1) By def-settled, $a_n=a_{N(a)}$ and $a_m=a_{N(a)}$ for $n,m\ge N(a)$. (2) Hence $a_n=a_m$ (transitivity of equality).
