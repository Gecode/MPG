---
name: gecode-propagator-implementation
description: "Implement and optimize custom Gecode propagators: posting, propagate/reschedule lifecycle, propagation conditions, domain iterators, advisors, reification, and rewriting. Use when adding new constraints or improving propagation performance/safety."
---

# Gecode Propagator Implementation

## Core
- Propagator computes on views, not model variables.
- Implement post function + actor lifecycle (`copy`, `dispose`, `cost`, `reschedule`, `propagate`).
- Use `Home` for posting context; use fail/check macros.
- Return honest `ExecStatus`: `ES_FAILED`, `ES_SUBSUMED`, `ES_FIX`, `ES_NOFIX`.
- Respect obligations: correctness, checking, contracting, subscription completeness, update completeness.
- Use patterns (`Unary/Binary/Ternary/Nary`, mixed variants) to reduce boilerplate.

## Key Patterns
- Do cheap pruning in `post()`; skip posting when trivially subsumed/failed.
- Select minimal propagation conditions (`*_VAL`, `*_BND`, `*_DOM`).
- Prefer iterator-based domain ops (`inter_r`, `narrow_r`, `minus_r`) for domain propagation.
- Use advisors for incremental change localization.
- Rewrite propagators (`GECODE_REWRITE`) when state simplifies.
- Template propagators on view types for reuse.
- If decomposition is propagation-weak, prefer dedicated propagator or extensional surrogate.
- Treat expensive support data as cacheable object, not per-post recomputation.

## Pitfalls
- Modifying a view while iterating its domain iterator.
- Returning `ES_FIX` when not actually at fixpoint.
- Missing view updates/subscription cancellation during cloning/disposal.
- Using external resources without `AP_DISPOSE` notice/ignore discipline.
- Continuing execution after subsuming/disposing actor.
- Expecting two weak propagators (`distinct` + `linear`) to match joint reasoning of one stronger constraint.
