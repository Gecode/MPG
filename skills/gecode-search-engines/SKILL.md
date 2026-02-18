---
name: gecode-search-engines
description: "Use existing Gecode search engines and meta-engines effectively: DFS/BAB/LDS, restart and portfolio setup, no-goods, parallel behavior, and completeness tradeoffs. Use when selecting/tuning search, not implementing new engines."
---

# Gecode Search Engines

## Core
- This skill is for using built-in engines, not implementing custom engines.
- Base engines: `DFS`, `BAB`, `LDS`.
- Meta engines: `RBS` (restart-based) and `PBS` (portfolio-based).
- Key options live in `Search::Options` (`threads`, `c_d`, `a_d`, `clone`, `stop`, `cutoff`, `nogoods_limit`, `assets`, `slice`, `tracer`).
- For optimization, use `BAB`-style search with a valid model-side objective/constrain setup.

## Engine Selection
- Use `DFS` for baseline complete search/enumeration.
- Use `BAB` for best-solution search.
- Use `LDS` when the branching heuristic is strong and you want discrepancy-ordered exploration.
- Use `RBS` to improve robustness via cutoffs, restart policies, and optional no-goods.
- Use `PBS` to improve robustness via asset diversification (heuristics/models/engines/options).

## Restart, Portfolio, and Incomplete Search Interactions
- `RBS` requires a cutoff generator in options.
- In restart search, `master()` decides restart behavior and can post no-goods; `slave()` configures each restart run.
- In restart search, `slave()` return value matters:
  `true` means complete slave search; `false` means intentionally incomplete search (for example LNS neighborhoods).
- In portfolio search, `slave()` return value has no meaning.
- `PBS<Script,Engine>` uses one engine type per asset; mixed portfolios use `SEBs(...)` to combine `dfs/lds/bab/rbs/pbs` with per-asset options.
- Do not mix best-solution and non-best assets in one SEB portfolio (`Search::MixedBest`).
- For restart-based best-solution assets in portfolios, use `RBS<Script,BAB>`.

## No-Good Nuances
- Restart no-goods are only available from `DFS`/`BAB`, not `LDS`.
- Enable with `nogoods_limit > 0`; depth is a memory/benefit tradeoff.
- Larger no-good depth limits reduce LAO effectiveness near root and can significantly increase memory.
- Not all branchers support no-goods; float branchers and execution branchers do not.
- Parallel search usually yields fewer extractable no-goods.

## Parallel and Portfolio Semantics
- Parallel search is intentionally nondeterministic (solution order, node counts, runtime).
- `assets` and `threads` are allocated conservatively in portfolios.
- Sequential portfolios use failure slices (`slice`) per asset (round-robin).
- With `threads > assets`, extra threads can be used inside asset engines.

## Pitfalls
- Expecting deterministic behavior from restart/portfolio/parallel runs.
- Treating restart/portfolio as complete when stop conditions, cutoffs, or `slave()==false` make runs incomplete.
- Forgetting to diversify assets and then expecting portfolio gains.
- Assuming no-goods are always available/effective regardless of brancher mix and parallelism.
- Forgetting that `master()`/`slave()` policy choices directly change search completeness and restart behavior.
