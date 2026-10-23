# Preparing MPG for Gecode 6.5.0

The manual now follows the local Gecode branch `feature/6.5.0-cleanups` at
`3c9d4221ce`. This combines current main, open variable lists, experimental
heuristic search, and the release's scheduling and FlatZinc follow-ups.
Model, Word variables, and the HTML redesign remain outside this release.
The existing Space-based introduction and HTML theme remain the basis of
the manual.

The initial review on 2026-10-21 compared `release-6.4.0` with Gecode `main`
at `c54eec1264`, plus the planned open-list/search branches. The follow-up
on 2026-10-23 checked the cleanup branch against that combined source.
Gecode's build metadata still says 6.4.0; its changelog and this manual
prepare the unreleased 6.5.0 edition. Repeat validation against the final
tag before publication.

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
- The CABS explanation makes the progress condition on dominance replacements
  explicit. The simplified TSPTW example still supports all options described
  in the manual.

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
  Doxygen output. Regenerate it after changes to the release source or the
  manual's API links.
- Run source checks, the complete example/tooling checks, and both publication
  builds. Review the changed HTML at desktop and narrow widths, and the
  affected PDF pages. Gist execution still requires attended review.
- Before the final release, repeat validation against the matching Gecode tag
  and use the coordinated publication process in [RELEASE.md](RELEASE.md).
  Building a preview does not announce or publish 6.5.0.

## Current validation

The updated manual passes source checks, tooling/platform tests, and example
validation against an exact export of `feature/6.5.0-cleanups` at
`3c9d4221ce`. The example report covers 552 artifacts: 632 checks passed,
none failed, and three interactive Gist runs were skipped. A focused compiled
check confirms maximum-length pruning of an open regular prefix, Boolean
constant posting, and scoped rounding-mode restoration.

A fresh Astra high review checked the cleanup additions against the source
and clarified the wording about scalar constants.

The API inventory contains 370 references generated from that source and its
Doxygen output. Strict HTML and PDF builds pass, including local links,
search, reference URLs, and PDF metadata/text checks. The affected HTML was
reviewed at desktop and narrow widths, and the changed PDF pages were
inspected.

Preview packaging passes with 317 files and a 633-page PDF. The preview remains
a local preparation artifact. Repeat validation against the final Gecode tag
and complete attended Gist review before publication.
