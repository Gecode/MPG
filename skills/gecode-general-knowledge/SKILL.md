---
name: gecode-general-knowledge
description: "Core Gecode architecture and runtime model: spaces, propagators, branchers, status/choice/clone/commit lifecycle, cloning/recomputation semantics, groups/tracing. Use when explaining solver behavior, search flow, or high-level debugging/design decisions."
---

# Gecode General Knowledge

## Core
- Space is home for variables, propagators, branchers, optimization order.
- Propagation is explicit: call `status()`.
- Search primitives: `status()`, `choice()`, `clone()`, `commit()`, `constrain()`.
- Space status: `SS_FAILED`, `SS_SOLVED`, `SS_BRANCH`.
- Choice is space-independent descriptor; alternatives indexed `0..n-1`.
- Clone only stable, non-failed spaces.
- Branchers run in posting order.

## Key Patterns
- Model as `class M : public Space`.
- Implement copy constructor + virtual `copy()`.
- Seed search engine with model, then delete seed model.
- Treat solution as space closure over member variables.
- Use groups/tracing for observability, selective control.
- Iterate model quality in loops: baseline -> improve propagation -> improve branching -> tune search.
- Measure with nodes/time/restarts, not runtime only.
- Treat symmetry handling as first-class design work, not post-processing.

## Pitfalls
- Assuming posting runs full propagation.
- Calling `Space` copy constructor directly instead of `clone()`.
- Using stale choices after invalidating via later `choice()` usage.
- Forgetting ownership/deletion of choices and returned solution spaces.
- Cloning unstable/failed spaces.
- Assuming one modeling pass is enough; most case studies need staged refinement.

## Source Focus
- `/Users/zayenz/gecode/MPG/docs/src/chapters/core/intro.tex.in`
- `/Users/zayenz/gecode/MPG/docs/src/chapters/modeling/m-started.tex.in`
- `/Users/zayenz/gecode/MPG/docs/src/chapters/search/s-started.tex.in`
- `/Users/zayenz/gecode/MPG/docs/src/chapters/modeling/m-group.tex.in`
- `/Users/zayenz/gecode/MPG/docs/src/chapters/case-studies/c-bin-packing.tex.in`
- `/Users/zayenz/gecode/MPG/docs/src/chapters/case-studies/c-crossword.tex.in`
