# Worked examples of every card (fictional, parity)

Create a card with `book new` (it writes the front matter and placeholder sections), then fill it by editing the file.
The shapes below are exactly what `check` reads. Section headings may be Japanese or English.

## A6 convention, A1 definition (`pool/parity/`)

```markdown
---
id: conv-integers
kind: A6
title: Numbers are integers
area: parity
requires: []
sources: [{src: src-toy, loc: "Ch.2 opening, p.14"}]
status: self-checked
---
## 規約
All numbers in this part are integers.

## 適用範囲
The chapter on parity; a book that uses another number system states its own convention.
```

```markdown
---
id: def-even
kind: A1
variant: predicate
title: Even integer
area: parity
requires: [conv-integers]
symbols: []
index: [even integer]
sources: [{src: src-toy, loc: "Def 2.1, p.14"}]
status: self-checked
---
## 定義
An integer $n$ is *even* if $n=2k$ for some integer $k$; otherwise it is *odd*.
```

## A2 claim and its A3 proof

```markdown
---
id: claim-odd-product
kind: A2
variant: equation-inclusion
title: Product of two odd integers is odd
area: parity
requires: [def-even]
sources: [{src: src-toy, loc: "Prop 2.3, p.15 (the source states 'even': corrected)"}]
relations: [{to: claim-even-sum, type: variant, diff: "about products of odd integers, not sums of even ones"}]
status: self-checked
---
## 仮定
$m,n$ are odd integers.

## 結論
$mn$ is odd.

## 量化子
For all odd integers $m,n$.

## 境界の場合
$m=n=1$ gives $1$; negative odd integers are included.
```

```markdown
---
id: proof-odd-product            # create with: book new A3 proof-odd-product --proves claim-odd-product
kind: A3
variant: direct
title: Proof of the product of two odd integers   # `book new A3` writes one
proves: claim-odd-product
owner: true                      # one owning proof per claim; an alternative proof has owner: false
requires: [def-even]             # exactly the cards cited below
status: self-checked
---
## 方針
Write odd integers as $2a+1$, multiply out.

## 段階
1. $m=2a+1$, $n=2b+1$ for integers $a,b$, since an odd integer is not even [by: def-even].
2. $mn=2(2ab+a+b)+1$, which is odd [by: def-even].
```

## A4 example, A5 exercise (a solution is an A3 that `proves` the exercise)

```markdown
---
id: ex-odd-product-counter
kind: A4
variant: counterexample
title: Source's claim fails
area: parity
illustrates: claim-odd-product
requires: [def-even]
status: self-checked
---
## 設定
Take $m=3$, $n=5$, both odd.

## 確認
$mn=15=2\cdot 7+1$ is odd, so "the product of two odd integers is even" is false.
```

An A5 has `## 問` (the question restated in the book's own words) and `## 解答` (the worked solution).

## B glue (`route/<slug>/card/`)

```markdown
---
id: parity-glue-1
kind: B2
variant: forward
status: drafted
between: [claim-even-sum, def-odd]
anchors: {claim-even-sum: 1a2b3c4d, def-odd: 5e6f7a8b}   # filled by `book anchor parity-glue-1`
---
## 済んだこと
Sums of even integers stay even [[claim-even-sum]].

## 足りないこと
We have no name or test for the integers that are left over.

## 次にすること
Name them and see how products behave.
```

A B5 entrance lists the borrowed results: `borrows: [{card: conv-integers, owner: pool, why: "numbers are integers"}]`
with sections 問いと終点, 前提とする既知事実, 規約.

## C1 source, C2 mapping (`src/`, `route/<slug>/map/`)

```markdown
---
id: src-toy
kind: C1
title: Elementary Number Theory for Beginners
role: primary
edition: 1st edition        # front matter, not only the section: `check` looks here
sha256: <hash of the file, if there is one>
---
## 書誌
...
## 版・ハッシュ
...
## 頁対応
printed page + 14 = PDF page
```

```markdown
---
id: map-prop-2-3
kind: C2
sources: [{src: src-toy, loc: "Prop 2.3 and proof, p.15"}]   # every source covering this unit, with locators
maps_to:
  - {card: claim-odd-product, relation: variant, diff: "conclusion corrected: odd, not even"}
  - {card: proof-odd-product, relation: alt-proof, diff: "source's argument does not prove its statement"}
  - {card: def-odd-form, relation: supplied, diff: "lemma the source lacks; the corrected proof needs it"}
adoption: adopted           # adopted | partial | not-adopted | outlook (the last three need `reason`)
scope_audit: OK             # TODO | OK | PARTIAL | MISSING | OUT (OUT needs `reason`: who owns it)
anchors: {claim-odd-product: 5e6af378}                        # `book anchor` fills it
---
## 原著との差
The source says even; that is false. Corrected, and two lemmas supplied.
```

Relations: `same`, `implies`, `special-case`, `variant` (needs `diff`), `alt-proof`, `equivalent`, `supplied` (a card the
book adds that the source does not have).

## D1 finding and route

`book new D1 f-1 --route toy --target claim-odd-product --severity major --summary "..."` writes the finding with the
target's current fingerprint. A route is `route/<slug>/route.yaml`:

```yaml
title: Parity
sections:
  - title: Even and odd
    items:
      - conv-integers
      - def-even
      - claim-even-sum              # its owning proof follows automatically
      - {card: claim-odd-product, proof: later}
      - {proof_of: claim-odd-product}   # only together with `proof: later`; otherwise the proof appears twice
```
