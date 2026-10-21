# Preparing MPG for Gecode 6.5.0

The release includes Gecode `main` plus the planned `feature/open-cp` and
`feature/open-search` merges. Model, Word variables, and the HTML redesign
are outside this release. The existing Space-based introduction and HTML
theme remain the basis of the manual.

The review on 2026-10-21 compared `release-6.4.0` with Gecode `main` at
`c54eec1264` (25 commits), including the 6.5.0 changelog and public header
changes. The planned features were checked at `feature/open-cp` (`0d80c51e0b`)
and `feature/open-search` (`72e9dafe35`). Recheck those branches after their
final merges.

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

| Change | Where it belongs | Required coverage |
| --- | --- | --- |
| Open variable lists (`open-cp`, carried by `open-search`) | `content/modeling/open-list.rst` | Added a route walkthrough, prefix and length semantics, growing constraints, branching orders, cloning, factories, and transitions. Both branching orders enumerate the five expected routes. Reviewed and copy-edited by a fresh Astra medium agent against the combined Gecode source. |
| GCD, divisibility, and n-ary products (`6e68e4dce7`) | `content/modeling/integer.rst`, arithmetic constraints | Cover `gcd`, reified `divides`, `product`, and `product_mod`; negative operands, zero, empty products, positive moduli, Euclidean residues versus `mod`, full and half reification, and the absence of a consistency guarantee. A historical TeX-only patch exists at MPG `0b4f2eb`; adapt its content to maintained RST and check it against the current API rather than merging the old source tree. |
| Nondeterministic automata (`540dab13a6`) | `content/modeling/integer.rst`, extensional constraints | Extend the current DFA-only account with `DFA::nfa`, array and initializer-list forms, multiple transitions for a state and symbol, no epsilon transitions, and no determinization or minimization. Show a small regular constraint using an NFA. |
| Minimum distance (`bec9ea9465`, #249) | `content/modeling/integer.rst`, constraint overview | Define the minimum pair distance, indexed sites and `IntDistance`, matrix versus callable distances and callback ownership/thread safety, optional pair requirements, repeated sites versus explicit distinctness, single versus decomposed propagation, and the optional matching bound. Distinguish incomplete propagation from bounds or domain consistency. |
| Inter-distance (`456e96dec2`, #247) | `content/modeling/integer.rst`, distinctness or scheduling | Define pairwise separation for fixed and variable distance; explain nonnegative separation, zero/one cases, repeated variables, `IPL_BASIC` versus advanced filtering, bounds(Z) consistency, and quadratic temporary space. Distinguish this constraint from minimum distance over indexed sites. |
| Scoped GPI control (`58298e3dcb`, #257) | `content/modeling/branch.rst`, AFC, and `content/modeling/group.rst` | Explain `Space::NoGPI` and `Space::UseGPI`, which postings they affect, zero AFC for local information, group behavior, cloning, rewriting, and scope restoration. Connect this to open-list callbacks. |
| Cumulative overload checking (`b94715d155`, #246) | `content/modeling/integer.rst`, cumulative scheduling | Update the propagation description for bounded knapsack-augmented overload checks on fixed-processing tasks, their relation to advanced propagation, and the cited CP 2026 algorithm. Keep the existing edge-finding explanation, but check its cost statement against the additional filtering. |
| Optional mimalloc (`e2b91053db`, `c54eec1264`, #258/#260) | `content/modeling/started.rst`, build options | Add a short CMake option note and a pointer to Gecode's build guide. Cover shared and static builds, the unchanged system-allocator default, consumer rebuilds, and workload-dependent parallel-search performance. The detailed allocator configuration belongs in Gecode's build documentation. |

The open-list walkthrough and the new integer constraints are the largest gaps.
After those, update AFC/GPI and the cumulative propagation account. The
mimalloc note is small and does not need a new chapter.

## Changes covered elsewhere

- The MiniZinc/FlatZinc native registry expansion (#253) needs complete solver
  and predicate reference documentation. MPG explicitly teaches the C++ API;
  avoid duplicating the MiniZinc predicate catalogue here. Document the new
  native constraints in the integer overview as listed above.
- Sparse DFA state compaction (#259) and sparse regular-graph construction
  improve implementation memory use without changing model semantics. No
  additional modeling instructions are required beyond the NFA update.
- Float power/logarithm correctness fixes and the CBS cache-removal fix need
  release notes and regression coverage in Gecode; they introduce no new
  modeling API or changed modeling recipe.
- Test-suite reorganizations (#255), CMake configuration/test summaries
  (#252), the restart-float test adjustment, vcpkg pin, attribution updates,
  reference light theme, and release-changelog setup require no separate MPG
  section. The public test-library and tag behavior is covered above.

## Publication work

- Gecode's `doc` target at `c54eec1264` fails while generating `stat.hh`:
  `test/package/allocator/boundary.hh` has no `STATISTICS` annotation. The
  missing annotation is fixed on Gecode's
  `feature/6.5.0-documentation-fixes` branch, ready for a later merge.
- Use 6.5.0 consistently for the manual, example defaults, CI preview, and
  release package. Historical changelog entries remain unchanged.
- Generate the API inventory from current Gecode sources and their matching
  Doxygen output. Regenerate it after the open-list/search merges and after
  adding API links for the missing material.
- Run source checks, the complete example/tooling checks, and both publication
  builds. Review the changed HTML at desktop and narrow widths, and the
  affected PDF pages. Gist execution still requires attended review.
- Before the final release, repeat validation against the matching Gecode tag
  and use the coordinated publication process in [RELEASE.md](RELEASE.md).
  Building a preview does not announce or publish 6.5.0.

## Current validation

The combined manual passes source checks, tooling/platform tests, and example
validation against Gecode `c54eec1264`: 624 checks passed, none failed, and the
three interactive Gist runs were skipped. The strict HTML and PDF builds and
preview packaging also pass. The changed HTML was reviewed at desktop and
narrow widths, and the affected PDF pages were inspected.

The Gecode reference build passes with the statistics annotation from
`feature/6.5.0-documentation-fixes` applied. The open-list and heuristic-search
APIs still need validation against the final combined Gecode release branch.
