# Preparing MPG for Gecode 6.5.0

The manual now follows the local Gecode branch `feature/6.5.0-cleanups` at
`49e69e12c6da692faafe111092f2c0dcb26854f4` (checked on 2026-10-28).
This combines current main, open variable lists, experimental
heuristic search, and the release's scheduling and FlatZinc follow-ups.
Model, Word/String variables, and the HTML redesign remain outside this release.
The existing Space-based introduction and HTML theme remain the basis of
the manual.

The initial review on 2026-10-21 compared `release-6.4.0` with Gecode `main`
at `c54eec1264`, plus the planned open-list/search branches. The follow-up
on 2026-10-23 checked the cleanup branch against that combined source.
The 2026-10-26 follow-up used OpenCP `6ac85d496a`, OpenSearch `11e7c256be`,
dependency updates through `f0baafb2cf`, and the 24 subsequent cleanup commits.
The 2026-10-28 follow-up uses the reorganized cleanup branch, including its
revised experimental search API. Gecode's build version is now 6.5.0 and its
library ABI is 52. The manual remains the unreleased 6.5.0 edition. Repeat
validation against the final tag before publication.

## Integrated documentation

- `feature/testing`: propagator testing, reusable test libraries, tags and
  failure replay, and custom-variable tests. The examples and build commands
  have been updated from `normal` to the current `standard` tag and target.
- `feature/document-worker-control`: capacity, asynchronous requests, pausing,
  handle lifetime, and worker budgets for portfolio assets.
- `feature/heuristic-search-parallel`: includes the earlier heuristic-search
  branch; covers AStar and CABS, bounds versus ranks, improving solutions and
  proof status, widening, keyed candidate dominance, and parallel search.
  These engines remain an opt-in experimental preview.

## Documentation topics

| Change | Location | Coverage and review |
| --- | --- | --- |
| Open variable lists (`open-cp`, carried by `open-search`) | `content/modeling/open-list.rst` | Added a route walkthrough, prefix and length semantics, growing constraints, branching orders, cloning, factories, and transitions. Both branching orders enumerate the five expected routes. |
| GCD, divisibility, and n-ary products (`6e68e4dce7`) | `content/modeling/integer.rst`, arithmetic constraints | Added posting examples and the sign, zero, empty-product, modulus, reification, and propagation semantics. Adapted the historical material to maintained RST and checked the calls in a compiled harness. |
| Nondeterministic automata (`540dab13a6`) | `content/modeling/integer.rst`, extensional constraints | Added `DFA::nfa`, acceptance, both construction forms, and the epsilon/determinization/minimization restrictions. A compiled check enumerates exactly the three expected words for the illustrated language. |
| Minimum distance (`bec9ea9465`, #249) | `content/modeling/integer.rst`, constraint overview | Added indexed sites and exact minimum-pair semantics, matrix and callable distances, pair requirements, repeated sites, and propagation options. The compiled example agrees with an independent coordinate-based enumeration. |
| Inter-distance (`456e96dec2`, #247) | `content/modeling/integer.rst`, distinctness or scheduling | Added fixed and variable pairwise separation, edge cases, alias restrictions, and the basic and advanced propagation costs and guarantees. The compiled example agrees with a complete brute-force solution set. |
| Scoped GPI control (`58298e3dcb`, #257) | `content/modeling/branch.rst`, AFC, and `content/modeling/group.rst` | Added a scoped posting example, local AFC and group semantics, lifetime and restoration rules, cloning and rewriting, and open-list callback links. Corrected the AFC sum explanation. A compiled check confirms the example's local/global AFC values. |
| Cumulative overload checking (`b94715d155`, #246) | `content/modeling/integer.rst`, cumulative scheduling | Updated advanced propagation for knapsack-augmented overload checking on fixed-processing tasks and mandatory optional-task subsets, with the CP 2026 citation. Scoped the complexity claim to edge-finding. A compiled source fixture confirms the added overload detection. |
| Optional mimalloc (`e2b91053db`, `c54eec1264`, #258/#260) | `content/modeling/started.rst`, build options | Added the CMake option, allocator scope and compatibility, shared/static support, consumer rebuilds, and a build-guide link. Performance advice remains workload-dependent. |

All eight topics have been added and independently reviewed. Each topic used
a fresh Astra medium agent for copyediting and factual verification, with
authoring and review recorded in separate commits.

On 2026-10-22, a fresh Astra high agent also reviewed the full release prose,
including the integrated testing, worker-control, and heuristic-search
material. Source checks, publication builds, and visual review were repeated
after its copyedits.

## Cleanup-branch follow-up

- Open regular constraints now prune the constructed prefix using the
  maximum eventual length and shortest accepting continuations. The chapter
  states the remaining limitations: future variable domains and holes in the
  length domain are not used, and the length variable is not directly pruned.
- The Boolean-expression overview includes C++ Boolean constants and the
  distinction between posting a `BoolExpr` and a raw C++ `bool`.
- The float-propagator chapter explains restoration of the caller's rounding
  mode by `Float::Rounding`, including nested scopes.
- Experimental search takes guidance through `Search::Options::guidance`.
  The guidance also holds CABS dominance callbacks; `max_width` and
  `frontier_limit` are ordinary search options. A* orders by bound and uses
  rank only to break ties. The manual removes the previous rank-first ordering
  and public engine-seeding instructions, and explains guidance lifetime and
  commandline-driver setup.
- The TSPTW description follows the current fixed-array model and its
  propagated travel-time bound. The previous transition formulation, bound
  selectors, and residual-propagation switches are no longer taught. The
  CABS dominance progress condition and parallel frontier reservations remain
  documented. The worker-count description explains when requests take effect
  between and within batches.
- The open-list chapter clarifies window filtering, empty-list closure for
  extrema, result aliases, and the rejection of repeated unassigned elements.
  Its factory, callback, and regular-language explanations still apply to the
  native incremental propagators. The route example remains unchanged.
  The open-list sum constraint uses its current name, `sliding_sum`.
- The views chapter introduces `OpenViewList<View>` for propagator authors,
  including shared growth, independent cloning, and separate growth, value,
  and length subscriptions. The testing chapter introduces
  `Test::Int::OpenTest` and its bounded randomized growth histories alongside
  ordinary closed-list tests.
- The CMake build-guide link still resolves within the consolidated source
  documentation at `docs/cmake-build.md`. Build and release instructions now
  state the Doxygen 1.18.0 minimum for reference generation. Existing
  `standard` tag and `check-standard` instructions remain current.

## Changes covered elsewhere

- The MiniZinc/FlatZinc native registry expansion (#253) needs complete solver
  and predicate reference documentation. MPG explicitly teaches the C++ API;
  avoid duplicating the MiniZinc predicate catalogue here. Document the new
  native constraints in the integer overview as listed above.
- Sparse DFA state compaction (#259) and sparse regular-graph construction
  improve implementation memory use without changing model semantics. No
  additional modeling instructions are required beyond the NFA update.
- Float power/logarithm fixes, signed `cumulatives` profile corrections, and
  scheduling bounds, shared-start, and overflow fixes retain their C++ posting
  interfaces. Their correctness cases belong in Gecode's regression suite.
  MiniZinc scheduling dispatch and explicit-end bindings belong in the solver
  reference rather than a separate MPG section.
- Test-suite reorganizations (#255), CMake configuration/test summaries
  (#252), the restart-float test adjustment, vcpkg pin, attribution updates,
  reference light theme, and release-changelog setup require no separate MPG
  section. The public test-library and tag behavior is covered above.

## Publication work

- The cleanup branch includes the statistics annotations previously collected
  on `feature/6.5.0-documentation-fixes` and
  `feature/6.5.0-open-documentation-fixes`. Its Doxygen build passes without
  additional source patches.
- Use 6.5.0 consistently for the manual, example defaults, CI preview, and
  release package. Historical changelog entries remain unchanged.
- Generate the API inventory from current Gecode sources and their matching
  Doxygen 1.18.0 or newer output. Regenerate it after changes to the release
  source or the manual's API links.
- Run source checks, the complete example/tooling checks, and both publication
  builds. Review the changed HTML at desktop and narrow widths, and the
  affected PDF pages. Gist execution still requires attended review.
- Before the final release, repeat validation against the matching Gecode tag
  and use the coordinated publication process in [RELEASE.md](RELEASE.md).
  Building a preview does not announce or publish 6.5.0.

## Current validation

Validation on 2026-10-28 used a fresh Git archive of
`49e69e12c6da692faafe111092f2c0dcb26854f4`, with Release libraries,
experimental search, Gist, and the public test libraries enabled. The build
reports Gecode 6.5.0 with library ABI 52. The earlier validation of
`e681aed226` was not reused for this input.

An Astra medium agent copyedited the updated prose using `unslop` and
`zayenz-writing-style`. The API descriptions were checked against the current
headers and implementations.

- `make check-sources` passed for 552 artifacts, 1179 code projections,
  and 42 SVG/PDF pairs. No executable examples or projections changed.
- `make check GECODE_ROOT=/private/tmp/mpg-650-49e69e1/gecode` passed the
  tooling/platform and example checks: 632 passed, none failed, and
  three interactive Gist runs were skipped. Both open-route branching orders
  still enumerate exactly the expected five routes.
- Focused Gecode runs passed all 59 `Int::OpenList::` tests and the three
  heuristic-search tests, including their parallel and mixed-engine cases.
  Each used one iteration on one test-runner thread. No exhaustive Gecode
  sweep was run.
- Twelve example smoke checks passed. BAB, A*, and CABS reached travel time
  671 on TSPTW instance zero with one and two workers. Both fifteen-puzzle
  models reached four moves with each engine using scramble four, seed one,
  move limit six, and Manhattan branching.
- Doxygen 1.18.0 generated the matching reference without warnings. The
  executable remains `/private/tmp/gecode-doxygen-1.18.0/doxygen-1.18.0/doxygen`.
  The regenerated inventory has 376 references, including `AStar`, `CABS`,
  and `Search::UninitializedGuidance`. It no longer includes
  `Search::CABSOptions`.
- `make docs MPG_VERSION=6.5.0` passed strict HTML/PDF builds, local-link and
  search checks, reference URL checks, and PDF metadata/text checks. The three
  changed HTML pages, a dense code page, and a table page were reviewed at
  1440- and 390-pixel widths. The affected PDF pages and nearby page breaks
  were inspected.
- `rst/scripts/package_release.py` passed against that build, producing a
  local preview with 317 files and a 633-page PDF under
  `/private/tmp/mpg-650-49e69e1/preview-output`. Build and check logs are in
  `/private/tmp/mpg-650-49e69e1/`.

The preview remains a local preparation artifact. Repeat validation against
the final Gecode tag and complete attended Gist review before publication.
