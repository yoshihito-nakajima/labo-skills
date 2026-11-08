+++
title = "A fictional explanation: why the shortest path ignores the gap"
slug = "example-prose"
language = "en"
+++

## What the page claims

For points $x_1,\dots,x_9$ on a line with one empty gap, the **shortest path** in a nearest-neighbour graph may skip a point. The page explains the one change that prevents this: an edge longer than $1$ costs more.

| Method | Edge cost | Skips the gap? |
|---|---|---|
| plain graph | $d(x,y)$ | yes |
| boosted graph | $d(x,y)\,b$ if $d>1$ | no |

![The nine points and the gap](asset:points.svg)

## The idea

$$
c(x,y)=\begin{cases} d(x,y) & d(x,y)\le 1,\\ b\,d(x,y) & d(x,y)>1. \end{cases}
$$

::: details Why a larger $b$ helps {#why-b}

A path that crosses the gap pays at least $b\cdot g$, where $g>1$ is the gap.

::: details A one-line check {#check}

If $b\ge 2$ and $g=1.5$, the crossing costs at least $3$; the detour costs $2.4$.

:::

Nothing else changes.

:::

- Read the table first.
  - Then the formula.
- See also [the check](#check) and [the source](https://example.org/paper).

> This page is fictional and exists only to exercise the builder.
