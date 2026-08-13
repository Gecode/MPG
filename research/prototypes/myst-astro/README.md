# Production-comparison MyST/Astro spike

This source-only spike implements the shared contract in
[`../authoring-comparison.md`](../authoring-comparison.md). Canonical MyST owns
publication semantics, resolved MyST JSON is the handoff, and Astro owns release
routes, page layout, and Tailwind-compatible CSS. The optional A4 PDF comes from
the same source through a pinned local LaTeX template.

The reference manual is **not** built here. A Gecode release builds and publishes
the reference tree plus a versioned symbol inventory. This spike copies the shared
inventory fixture byte-for-byte and resolves `class:Gecode::Space` to
`/doc/6.4.0/reference/classGecode_1_1Space.html`. A later site release imports the
already-built reference and MPG artifacts.

## Result

The MyST path passes the base and hard-page fixtures. It produces five native
Astro routes under `/doc/6.4.0/modeling/`, plus a fourteen-page A4 PDF. The
expanded pages replace the legacy architecture PSTricks, full crossword
grid/solution, and nonogram tables with deterministic accessible SVG and add
two executable Gecode models. The PDF imports the shared classical design
through a thin MyST adapter and retains its title, part, chapter, program, tip,
and folio grammar.

This is enough to keep MyST in the production gate, not enough to start bulk
migration. It still needs the real `m-started`/`p-started` trial.

## Exact verification

Prerequisites are Node/npm, Apple/Homebrew Gecode 6.4.0 under `/opt/homebrew`, a
C++17 compiler, XeTeX/latexmk, and Poppler. From this directory run:

```sh
npm ci --offline --ignore-scripts
npm run verify:all
```

The first command works after the lockfile packages have entered npm's local
cache. The substantive build is then forced through an invalid local proxy, so a
mutable theme/template download fails rather than going unnoticed. The checked-in
metadata-only `templates/headless-site` satisfies MyST's site-data contract; its
server is never run.

`verify:all` checks:

- a source preflight and negative duplicate/unresolved-reference fixtures;
- strict MyST parsing with the local API-inventory plugin;
- the inventory fixture is byte-identical to `../shared/reference-inventory.json`;
- compilation and execution of the canonical C++ program against Gecode;
- resolved JSON to semantic HTML, then Astro build and `astro check`;
- equation, SVG figure, program, table, callout, citation, bibliography, macro,
  API URL, and release-shaped cross-page links;
- byte identity between canonical source and the content-hashed download;
- an explicit page-to-C++ dependency manifest;
- deliberate failure on an unknown resolved-AST node;
- local TeX generation with no unhandled-node warning;
- fail-closed correction of MyST's code-listing LaTeX kind;
- fail-closed article-to-chapter, duplicate-heading, and admonition-to-tip
  adaptation against exact generated-TeX shapes;
- use of shared `mpg-classic.sty` through the local `mpg-myst.sty` adapter;
- A4 PDF structure and HTML/PDF agreement on Program 1 and Table 1; and
- existence of both final local routes.

The latest clean run passed with zero Astro diagnostics. It took 28.8 seconds on
the prototype machine after installation, including five SVG conversions, three
C++ builds/runs, Astro, and XeTeX. The original model printed:

```text
9 5 6 7 1 0 8 2
```

All fourteen PDF pages were rendered with Poppler and visually inspected. The latest
render has legible/vector math and SVG, no clipping or overlap, correct heading
spacing, the table in source order, and readable wrapped code, tips, and
bibliography. It also has the extracted vector logo, historical part M opening,
blue numbered chapter openings, plain numbered tips with ending markers, Charter
text, Bera Mono code, and centered folios. Verification rejects overfull boxes,
font substitutions, or PDFs that do not embed both Charter and Bera Mono.

## Architecture and release boundary

```text
Gecode release job
  reference HTML + reference-inventory.json
                      |
                      v (import artifact; never run Doxygen here)
canonical MyST + canonical C++ + imported inventory
                      |
               myst build --site
                      |
               resolved site JSON
                      |
          strict semantic Astro adapter
                      |
       /doc/6.4.0/modeling/{,cross-page/}

canonical MyST ----> myst build --tex ----> pinned template ----> A4 PDF
canonical C++ -----> compiler/test and content-hashed exact download
```

The `{gecode-api}` role is deliberately typed: its body is an inventory key such
as `class:Gecode::Space`, not a hand-written URL. An absent key stops the MyST
build. Astro rewrites only MPG's internal resolved routes; imported reference URLs
already have their release-shaped base.

## Literate-source and dependency result

`examples/send-more-money.cpp` is a complete Gecode `Space` with DFS search. The
MyST `literalinclude` selects its named `search-loop` region, while `{download}`
publishes the entire exact file. The verifier compiles that same path and compares
the published bytes.

MyST 1.10.1 still emits `dependencies: []` for every `literalinclude`. The adapter
therefore walks semantic include/static-link nodes and writes
`generated/dependencies.json`. For this fixture it records:

```json
{
  "/content/index.md": ["../examples/send-more-money.cpp"]
}
```

Production must feed this explicit edge into the release orchestrator; it cannot
trust MyST watch invalidation for external code.

## PDF workaround and remaining defects

MyST 1.10.1 emits every labeled code container as a LaTeX `figure`, even though
its references say “Program”. It also changed the literal code sentinel
`-- ++ ->` to `- - ++ ->` in TeX. `scripts/fix-program-latex.mjs` now walks the
resolved AST, restores the exact code bytes inside all four verbatim blocks, and
changes their float kind to `mpgprogram`. A changed upstream shape aborts the build.
This is a format-specific workaround and should become an upstream fix or a
supported project transform.

The exporter also treats every article as a LaTeX section, irrespective of the
book template. `scripts/adapt-classical-latex.mjs` maps the five article wrappers
to chapters, lowers their authored subheadings one level, removes three headings
that merely repeat their article title, and maps two titled admonitions to
`mpgtip`. Exact counts and generated shapes are release invariants, so an exporter
change fails rather than silently degrading the PDF. Part metadata remains in the
pinned book template because the current MyST project tree has no part node. The
build also stages and byte-checks the adapter on every export; MyST otherwise
leaves an existing auxiliary template file untouched and can compile stale LaTeX
presentation code.

A second scaling defect appeared in clean-output testing: MyST retained old
content-hashed downloads in `_build/site/public`. The release command now deletes
that generated site tree before resolution and requires exactly one
byte-identical crossword and nonogram download.

The original bibliography warning is avoided by deriving the web bibliography
from MyST's structured citation data; the book template already emits BibTeX's
bibliography. Fixed float placement also prevents the table moving ahead of its
section. The generated PDF remains untagged. XeTeX/xdvipdfmx reports a benign
duplicate page-object warning on the first pass, and MyST prints an API-base banner
even while the invalid-proxy test proves no request is required.

MyST's own `--strict` accepted a duplicate-label warning during exploration, so
the checked source preflight is not optional. The renderer likewise throws for
every unknown semantic node. Neither implementation is yet a comprehensive MyST
schema adapter.

## Measurements

Pinned direct dependencies are `mystmd` 1.10.1, `astro` 7.2.0, `katex` 0.16.22,
`@astrojs/check` 0.9.6, and `typescript` 5.9.3. The npm lockfile pins transitives.

Measured on arm64 macOS with Node 26.5.1/npm 11.17.0:

| Measurement | Result |
| --- | ---: |
| Complete clean verification | 28.8 s |
| Installed `node_modules` | 224 MiB |
| Resolved MyST site data | 266 KiB |
| Astro output | 1.32 MiB |
| PDF | 118 KiB / 11 A4 pages |
| Semantic adapter | 153 lines |
| API role | 22 lines |
| Exact-code/PDF-kind workaround | 17 lines |
| Source-reference preflight | 38 lines |
| Canonical MyST/config fixture | 111 lines |

Generated JSON, fragments, binaries, assets, TeX, PDF, Astro output, and page
renders are ignored. The deliverable consists only of source, pinned lockfile,
plugins, templates, and verification code.

## Authoring assessment

The canonical source is compact and readable. Labels, references, math, tables,
admonitions, figures, citations, and literal includes remain close to ordinary
Markdown, while the typed API role is explicit without exposing release URLs.
Compared with canonical reStructuredText, MyST's common prose and tables are less
ceremonial; its custom directives are not materially simpler.

The implementation cost is concentrated at the output boundary: strict resolved
AST coverage, missing literal-include dependencies, and the PDF program-kind
repair. The deciding production question is therefore whether that adapter remains
small on the difficult real chapters. If it expands rapidly, reST/Sphinx's more
mature doctree/builders may be the better trade despite denser authoring syntax.
