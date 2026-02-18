---
name: gecode-search-engine-implementation
description: "Implement custom Gecode search engines: status/choice/clone/commit orchestration, recomputation strategies (full/hybrid/adaptive), last-alternative optimization, branch-and-bound integration, and invariants for choice compatibility and completeness."
---

# Gecode Search Engine Implementation

## Core
- Implement engines against the `Space` interface (`status`, `choice`, `clone`, `commit`).
- Maintain explicit ownership for all `Space*` and `Choice*` objects.
- Respect compatibility invariants: choices are valid only for clone-related spaces.
- Treat `choice()` as invalidating earlier choices on that space.
- Handle all `SpaceStatus` cases: `SS_FAILED`, `SS_SOLVED`, `SS_BRANCH`.

## Key Patterns
- Keep a clear split between exploration mode and recomputation mode.
- Use edge/path state to store choices, alternatives, and optional clones.
- For recomputation, replay commits from nearest stored clone (or root clone).
- Apply LAO (last-alternative optimization) to avoid unnecessary stored choices/commits.
- Use hybrid recomputation with commit distance to cap recomputation cost.
- Use adaptive recomputation to add clones where repeated failures indicate benefit.
- Integrate branch-and-bound by constraining future spaces against best solution.
- Keep restart/meta-engine hooks explicit (`master`, `slave`) when required.
- Wire statistics and stop-object checks consistently.

## Invariants
- Recomputed spaces must follow the same decision path as stored edge choices.
- Commit order must match original choice generation order.
- If recomputation fails due to nondeterminism/weak monotonicity effects, recover path state safely and continue search.
- Cloning/copying must never mutate model state outside allowed operations.

## Pitfalls
- Reusing stale choices after another `choice()` call.
- Mixing incompatible choices/spaces and triggering `SpaceNoBrancher`.
- Forgetting to delete choices and returned solution spaces.
- Assuming deterministic node order under parallel execution.
- Overusing no-goods depth without accounting for memory and LAO tradeoffs.
- Reporting completeness when stop/cutoff/meta policy makes the run incomplete.
