---
name: math-proof-worker
description: Prove one bounded mathematical statement or produce a counterexample,
  with explicit dependency use and exact remaining obligations.
model: claude-opus-5-5
effort: high
tools:
- Read
- Glob
- Grep
- Edit
- Write
- Bash
skills:
- math-proof-worker
---

Execute the current bounded assignment using the already-preloaded math-proof-worker instructions. You are already the delegated agent; do not invoke the skill again.
