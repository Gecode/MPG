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
- Respect obligations: correctness, checking, contracting, monotonicity (or waived), subscription completeness, update completeness.
- Respect implementation obligations: subsumption complete, cloning conservative, subscription correct.
- Use patterns (`Unary/Binary/Ternary/Nary`, mixed variants) to reduce boilerplate.

## Key Patterns
- Do cheap pruning in `post()`; skip posting when trivially subsumed/failed.
- Select minimal propagation conditions (`*_VAL`, `*_BND`, `*_DOM`).
- Prefer iterator-based domain ops (`inter_r`, `narrow_r`, `minus_r`) for domain propagation.
- Use fixpoint reasoning deliberately: return `ES_FIX` only when justified.
- Use `ModEventDelta` and staging to combine cheap and expensive propagation phases.
- Use advisors for incremental change localization.
- For advisors, maintain council lifecycle and ensure rescheduling/subscription completeness.
- Rewrite propagators (`GECODE_REWRITE`) when state simplifies.
- Use reified/rewriting patterns to remove reification overhead once control literals decide.
- Template propagators on view types for reuse.
- If decomposition is propagation-weak, prefer dedicated propagator or extensional surrogate.
- Treat expensive support data as cacheable object, not per-post recomputation.

## Pitfalls
- Modifying a view while iterating its domain iterator.
- Returning `ES_FIX` when not actually at fixpoint.
- Returning `ES_NOFIX` when propagation is idempotent and could reach fixpoint inside the same `propagate()` call (causes avoidable re-scheduling).
- Missing view updates/subscription cancellation during cloning/disposal.
- Using external resources without `AP_DISPOSE` notice/ignore discipline.
- Continuing execution after subsuming/disposing actor.
- Failing to check modification-event failure after view updates.
- Breaking subscription completeness when using advisors/dynamic subscriptions.
- Expecting two weak propagators (`distinct` + `linear`) to match joint reasoning of one stronger constraint.
