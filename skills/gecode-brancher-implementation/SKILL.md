---
name: gecode-brancher-implementation
description: "Implement custom Gecode branchers and choice mechanics: status/choice/commit, archiving, recomputation compatibility, no-good literal support, and brancher view reuse. Use when predefined `branch(...)` is insufficient."
---

# Gecode Brancher Implementation

## Core
- Brancher is actor implementing branching behavior.
- Implement `status`, `choice(Space&)`, `choice(const Space&,Archive&)`, `commit`, `print`, `copy`, `dispose`.
- Choice stores only space-independent commit data.
- `commit` must work with recomputed/cloned spaces using only choice payload.
- Branchers execute in queue order of posting.
- Optional `ngl()` adds no-good support.

## Key Patterns
- Track first candidate index (`start`) to avoid rescanning.
- Keep choice payload minimal (`pos`, `val`, alt count), archive/unarchive deterministically.
- Use binary alternatives (`eq` vs `nq`) unless assignment brancher (single alt).
- Implement NGL class with `status`, `prune`, `subscribe`, `cancel`, `reschedule`.
- Reuse branchers through views (notably minus view for max-style variants).
- Encode problem heuristic explicitly (for example Warnsdorff, best-fit slack).
- Mix assignment-style one-alt choices with pruning alternatives when justified.
- Design second alternatives to embed symmetry breaking when safe.
- Pair brancher with branch print callbacks for explainability/debugging.

## Pitfalls
- Storing views/pointers to space state inside choice objects.
- Disposing brancher too early when `status()` becomes false.
- Depending on mutable brancher state not encoded in choice for `commit()`.
- Not skipping assigned views, causing repeated same choice/infinite tree.
- Violating recomputation invariants and commit order assumptions.
- Using generic variable-value branching when structure-aware heuristic is required.
- Forgetting that brancher disposal is not automatic when external resources exist.

## Source Focus
- `/Users/zayenz/gecode/MPG/docs/src/chapters/search/b-started.tex.in`
- `/Users/zayenz/gecode/MPG/docs/src/chapters/search/b-advanced.tex.in`
- `/Users/zayenz/gecode/MPG/docs/src/chapters/modeling/m-branch.tex.in`
- `/Users/zayenz/gecode/MPG/docs/src/chapters/modeling/m-group.tex.in`
- `/Users/zayenz/gecode/MPG/docs/src/chapters/search/s-recomputation.tex.in`
- `/Users/zayenz/gecode/MPG/docs/src/chapters/case-studies/c-knights.tex.in`
- `/Users/zayenz/gecode/MPG/docs/src/chapters/case-studies/c-bin-packing.tex.in`
