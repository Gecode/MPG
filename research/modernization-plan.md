# MPG modernization plan

Status: proposed architecture and executable migration plan
Research date: 2026-08-09
Repository baseline: `19c1eaf` on `main`

## Decision

Keep **MyST and canonical reStructuredText/Sphinx in the final production gate,
with Sphinx now the provisional engineering leader**. Both hardened spikes
passed the same semantic web, PDF, C++, offline, versioned-reference, and hard
illustration fixtures. Sphinx proved that resolved doctrees can be exported
cleanly into Astro and scaled to the overview, crossword, and nonogram pages
with less new release machinery.

Before broad conversion, migrate the same two representative slices in both
formats and prove that each adapter handles every node without scraping
generated HTML:

- `m-started`, which exercises the main modeling tutorial, math, references,
  tips, screenshots, and a complete model; and
- the relevant sections of `p-started`, which exercise deep literate code
  projections, custom figures, API references, and test-wrapper composition.

Choose MyST only if its smaller, single-runtime adapter and clearer authoring
syntax remain decisive on the deeply nested `p-started` material. Choose
reST/Sphinx if its native dependency tracking, diagnostics, domains, exact code
rendering, and PDF semantics continue to avoid local machinery. If neither adapter
remains narrow, use the document-first Quarto/Pandoc pipeline demonstrated in
`research/prototypes/document-first`. Do not fall back to unconstrained MDX.

This is the measured ranking for MPG, not a general ranking of documentation
tools:

| Path | Web integration | Document semantics | PDF | Local infrastructure | Decision |
|---|---:|---:|---:|---:|---|
| MyST AST to Astro + MyST LaTeX | Strong | Strong | Strong with repairs | Medium | Finalist; authoring leader |
| reST/Sphinx doctree to Astro + Sphinx LaTeX | Strong | Strong | Strong | Medium | Provisional engineering leader |
| Native Astro/MDX + browser PDF | Excellent | Medium | Weak to medium | High | Useful web reference, not canonical |
| Quarto/Pandoc book | Weak to medium | Strong | Strong | Low | Fallback |
| Antora, Markdoc, Typst source | Weak for this integration | Mixed | Mixed | Medium to high | Reject as primary path |

The measured head-to-head result is in `research/authoring-spike-results.md`;
official documentation links are in `research/toolchain-landscape.md`.

## Why the migration must start below the authoring syntax

MPG is a 580-page executable publication, not an ordinary LaTeX book. Its
maintained sources contain prose and math, but also the canonical bytes of
downloadable C++, a tree of named code projections, build metadata, API links,
and figure programs.

The current baseline includes:

| Item | Baseline |
|---|---:|
| Maintained chapter source | 38 files, 46,643 lines |
| Named labels / automatic references | 560 / about 1,137 |
| Gecode API references | 613 |
| Inline C++ spans | about 5,348 |
| Literate programs / nested blocks | 85 / 625, depth up to 5 |
| Generated source artifacts | 78 `.cpp` plus `int.hh` |
| Figures / PSTricks pictures | 213 / at least 26 |
| Tables / numbered tips / citation calls | 79 / 78 / 106 |
| Current PDF | 580 A4 pages, untagged PDF 1.4 |

The old projection language distinguishes ordinary named children,
`anonymous`, `ignore`, nested `texonly`, display-only programs, and compact or
label-free displays. A visible-code conversion would lose executable bytes.
The Perl extraction behavior, not the visible PDF, is the migration oracle.

The audit also found validation gaps that must be fixed before conversion:

- extraction emits 79 source artifacts, but only 76 C++ programs enter the
  configured validation manifest;
- all 30 Gecode test-harness programs run with `-help`, so they execute no
  assertions;
- three Gist programs are intentionally compile-only, but the initial manifest
  does not describe that capability;
- `.vis` downloads are not copied, and stale generated files can survive
  extraction; and
- the production parser remains Perl; the partial Python literate parser is
  not equivalent and is not the production path.

`research/current-pipeline-audit.md` contains the complete inventory and test
evidence.

## Target architecture

The new working set separates publication semantics, authored content,
executable artifacts, and presentation:

```text
canonical pages ─────────┐
publication manifest ───┼─> selected resolver ─> resolved semantic tree
bibliography + figures ─┘                              │
                                                       ├─> strict MPG adapter ─> release bundle ─> Astro/Tailwind pages
                                                       └─> vendored LaTeX template ───────────────> PDF

canonical C++ + region metadata ─> artifact/projection engine ─> standard AST code/link nodes
                 │
                 └────────────────> build/run/test profiles ────> CI evidence + downloads
```

The selected document engine owns labels, typed references,
equation/figure/program numbering, citations, bibliography resolution, and book
assembly. Astro owns routes, navigation, site chrome, Tailwind tokens,
responsive layout, and search. The MPG release build emits a versioned semantic
bundle; the website imports it. The existing Python tooling continues to own
C++ extraction, compilation, execution, and manifests until deliberately
replaced.

The adapter must consume a resolved MyST tree or resolved Sphinx doctree. It
must never parse generated HTML. It maps a small, versioned node set to the
release schema and fails on every unknown node. Engine upgrades are therefore
explicit compatibility work.

### Proposed repository layout

```text
publication/
  publication.yml            # order, stable page IDs, versions, aliases, bundles
  pages/                      # canonical MyST or reStructuredText after gate
  bibliography/MPG.bib
  notation.yml                # shared math notation/macros
examples/
  <artifact-id>/
    artifact.yml              # regions, authorship, downloads, validation profiles
    *.cpp / *.hh              # canonical source by default
    test-wrapper.cpp          # where Gecode's test framework is required
figures/
  <figure-id>/
    figure.yml                # caption-independent metadata, alt text, license, derivatives
    source.svg|source.dot|... # one declared canonical source
schemas/
  publication.schema.json
  artifact.schema.json
tools/
  mpg/                        # orchestration, migration, manifests, code validation
web/
  publication-adapter/        # resolved tree to semantic release bundle
pdf/
  template/                   # vendored, pinned book template and fonts
```

Stable entity IDs must not depend on filenames, titles, chapter numbers, or
display names. Page frontmatter can remain pleasant for authors; the
publication and artifact manifests carry release-critical identity.

## Authoring contract

Use the winning format's ordinary syntax for headings, prose, lists, tables,
TeX-style math, figures, citations, labels, and cross-references. Prefer
directives and roles that resolve to standard semantic nodes. Keep raw HTML,
raw LaTeX, JSX, and renderer-specific conditionals out of canonical pages
except for quarantined, target-declared escape blocks.

Add only three MPG-specific extensions at first:

1. `mpg:code` selects a declared artifact and region projection. The plugin
   emits ordinary code, caption, link, and download AST nodes.
2. `gecode:ref` resolves a versioned API symbol through an inventory emitted by
   the Gecode release-documentation build and emits an ordinary external link.
3. `mpg:terminal` distinguishes commands and captured output from C++ source.

A production code projection should name stable entities, not a relative file
and line range:

```md
:::{mpg:code} artifact.send-more-money
:region: posting.linear-equation
:caption: Posting the cryptarithmetic equation
:download: true
:::
```

The authoring contract must have a conformance suite. Fixtures should cover all
math macros, every directive option, nested references, citations, tables,
figures, all legacy projection modes, and deliberately invalid inputs.

## Code and literate-programming model

Invert the default code ownership. Store a complete, compilable `.cpp` file as
the canonical artifact and select named regions for the prose. The file shown
to readers, offered for download, and compiled by CI is then the same file.
Use inert C++ comment markers or a sidecar span map; never use line numbers as
public identity.

Retain document-driven tangling only where progressive construction is itself
the lesson. Model those cases as an explicit artifact DAG with line-level
source maps. Do not encode tangling behavior inside the renderer.

Each `CodeArtifact` declares:

- stable ID, output path, language, authorship, and license;
- canonical sources or ordered fragments;
- a region tree and projection defaults;
- Gecode components and capabilities such as Gist or test-framework sources;
- validation profiles with exact compile flags, arguments, timeouts, expected
  exit values, output checks, and registered-test counts; and
- current and compatibility download URLs.

Projection policies map the old semantics explicitly:

| New policy | Legacy meaning |
|---|---|
| `expanded` | show descendant bytes |
| `linked` | replace named child with a link to its own projection |
| `ellipsis` | legacy `anonymous` child |
| `hidden` | legacy `ignore` child |
| `display-only` | nested `texonly`; show but do not emit |

The content-model prototype in `research/prototypes/content-model` provides a
Draft 2020-12 schema, a real `less` propagator manifest, a dependency-free
semantic checker, and eight passing invariant tests. Use it as the starting
contract, not as a final schema.

## Figures and other assets

Prefer semantic SVG for diagrams. Keep the diagram source—SVG, DOT, Mermaid,
data plus generator, or another declared format—and render deterministic web
and PDF derivatives in CI. Reuse one SVG in both outputs when the PDF backend
handles it correctly.

Inventory each of the 213 figures before conversion:

- convert PSTricks search trees, propagator diagrams, grids, and dependency
  figures to accessible SVG or a deterministic diagram source;
- keep screenshots as raster originals, with responsive derivatives and real
  alt text or long descriptions;
- treat generated result tables and plots as reproducible data products; and
- use a temporary rendered-vector derivative only for figures whose redraw
  cost would block a vertical slice.

Every figure manifest must declare stable ID, canonical source, generation
command, alt text or long description, dimensions, credit/license, and the
web/PDF derivatives. A screenshot of an old PSTricks figure is a transition
artifact, not the final representation.

## PDF strategy

Use the winning engine's vendored LaTeX book template as the production PDF
path. This keeps book-wide numbering, contents, bibliography, indexes, page
furniture, floats, and pagination in a document engine while the web remains
native to Astro.

Pin the document engine, Node/Python dependencies, TeX Live release, fonts,
bibliography style, syntax theme, diagram renderers, and template checksum in a
Linux build image. Record normalized PDF facts and visual snapshots; do not
require byte-identical PDFs when metadata or object ordering makes that
misleading.

The PDF gate must check:

- A4 page size, embedded fonts, bookmarks, links, page labels, title metadata,
  and no unresolved references;
- no clipped or overlapping text, broken tables, unreadable code, missing
  glyphs, blank accidental pages, or rasterized vector diagrams;
- selected visual-regression pages: cover, contents, dense prose/math, large
  table, code projection, complex figure, bibliography, and index; and
- accessibility metadata measured explicitly. Every prototype and the legacy
  PDF is currently untagged, so the project must not claim tagged-PDF or PDF/UA
  compliance until a tested template/backend supplies it.

Keep browser PDF as a fast preview, not the release book. The Astro prototype
showed that Chromium can make an attractive A4 handout, but it lacks robust
page-number references, running matter, and other book mechanics.

Retain the original MPG's classical design grammar in the release PDF: Charter
text and compatible mathematics, Bera Mono code, A4 two-sided layout, Gecode
color tints, sparse part and chapter openings, dense technical pages, numbered
tips, characteristic program blocks, and complete front/back matter. Do not
require identical pagination after the content and figures change. Extract this
as a small `mpg-book.sty` semantic design package rather than carrying forward
the PSTricks illustration macros. The detailed feasibility assessment and
representative-page gate are in
[`classical-pdf-fidelity.md`](classical-pdf-fidelity.md).

The implemented extraction is in
[`prototypes/shared/classical-pdf`](prototypes/shared/classical-pdf/README.md).
Both finalists now build visually inspected classical PDFs with Charter, Bera
Mono, the vector logo, historical part M, blue chapter openings, orange
programs, plain numbered tips, and centered folios. Sphinx reaches this through
semantic nodes and public LaTeX hooks. MyST additionally requires a fail-closed
generated-TeX structure adapter and pins part metadata in its PDF template.

## Astro and release integration

The Astro repository should load a versioned MPG content artifact during its
normal build. Do not deploy a second server or iframe a separately themed site.
The Gecode release process separately builds the reference documentation and
publishes both its rendered tree and a versioned symbol inventory. The website
imports those release artifacts. Normal website and MPG builds only consume the
inventory and imported URLs; they never run Doxygen or rebuild the reference
documentation.
MPG is built with each Gecode release, separately from the ordinary website
build. That release job runs the selected resolver, validates code, creates the
PDF, and emits a pinned semantic web bundle. The Astro release flow imports the
bundle and renders it with site layouts and Tailwind tokens. This keeps MPG
independently reproducible and lets the site select a specific manual version.
The import contract exposes:

- resolved page AST plus validated page metadata;
- ordered navigation and previous/next relationships;
- copied, fingerprinted figures and download artifacts;
- the imported release's link/inventory table for Gecode API symbols; and
- a route/alias manifest.

Preserve existing public products and paths unless a redirect is tested:

- `/doc/<version>/MPG.pdf`;
- `/doc/<version>/MPG/<example>.cpp` and companion downloads;
- `MPG.tar.gz` and the chosen modern archive format; and
- stable historical anchors where the web edition has an equivalent target.

The active edition can use readable routes such as
`/doc/<version>/modeling/getting-started/`. Historical editions remain frozen.

The classical web structure, strict bundle-loader contract, site/release
ownership boundary, restrained responsive component mapping, and implementation
sequence are specified in
[`website-classical-design-plan.md`](website-classical-design-plan.md). It must
be implemented directly inside the actual site's `BaseLayout`; a separate
manual shell or marketing-style landing page is explicitly out of scope.

## Migration phases

The estimates below are planning ranges for one primary engineer with reviews
from a Gecode maintainer and the website maintainer. Figure redraw and content
editing can run in parallel.

### Phase 0: seal the legacy oracle (1–2 weeks)

Deliver:

- a clean-build baseline containing every logical label, reference, citation,
  API link, artifact hash, region tree, projection text, figure usage, and
  public path;
- one explicit manifest for all 79 generated sources and all wrappers;
- fixed extraction that clears destinations and packages `.vis` assets;
- honest validation modes, with propagator tests running selected registered
  tests instead of `-help`; and
- normalized PDF facts plus selected rendered-page snapshots.

Exit gate: no emitted artifact is unmanifested, no stale file survives a clean
rebuild, and every profile reports whether it compiled, ran, tested, skipped,
or required an unavailable capability.

### Phase 1: production vertical slice (2–3 weeks)

Deliver:

- versioned publication/artifact schemas based on the content-model prototype;
- parallel MyST and canonical reST conversions of the same `m-started` and hard
  `p-started` slices;
- equivalent initial MPG roles/directives in both candidates;
- resolved-tree release artifacts rendered inside the real Astro/Tailwind
  layout;
- vendored A4 PDF templates; and
- actual versioned routes, downloads, API links, and compatibility aliases.

Exit gate:

- every resolved node is mapped or causes a build failure;
- all labels, references, equations, figures, tips, citations, and API symbols
  resolve in both outputs;
- the same code declaration feeds display, download, and validation;
- HTML passes link, semantic, accessibility, and visual checks;
- PDF passes the gate above; and
- the website maintainer accepts the routing and styling contract.

Record authoring review, adapter growth, dependency behavior, PDF repairs,
warnings, and build footprint for both candidates. Select one format at the
exit gate and remove the losing spike from the production path. If neither
adapter remains maintainable, adopt the Quarto fallback. Do not build a private
document engine around MDX.

### Phase 2: harden shared infrastructure (2–3 weeks)

Deliver:

- stable-ID and alias registries;
- source-first region extraction plus explicit tangled-artifact support;
- a documented consumer for the versioned symbol inventory emitted beside the
  Gecode release reference documentation, replacing the stale `gl.db` snapshot;
- complete bibliography and math-macro migration;
- asset generation pipeline and figure manifest;
- contributor preview, link-check, code-check, PDF, and clean-build commands;
- pinned container/toolchain and dependency-update tests.

Exit gate: fixtures cover every legacy construct class, differential extraction
matches approved artifact hashes, and a clean checkout produces all declared
outputs without network-fetched mutable templates.

### Phase 3: migrate by vertical part slices (6–12 weeks)

Migrate one coherent part at a time. Each slice includes pages, examples,
figures, cross-links, tests, web routes, and PDF pages. A suggested order is:

1. Modeling, to stabilize the public tutorial and ordinary examples.
2. Search, to exercise trees and engine examples.
3. Programming propagators and branchers, to exercise the deepest code graph.
4. Case studies, including the large crossword sources and generated results.
5. Variables/implementation material, appendices, changelog, front matter, and
   license.

Exit gate per slice: semantic baseline reconciled, all declared code profiles
pass, figures are accounted for, web/PDF visual review passes, and old routes
redirect or remain available.

Avoid a repository-wide mechanical conversion followed by cleanup. It delays
all integration evidence and makes executable omissions hard to localize.

### Phase 4: release integration and parallel publication (2–3 weeks)

Publish the old PDF and new web/PDF outputs together for at least one release
candidate. Run scheduled validation against Gecode `main` and the release ref.
Collect broken-link reports, contributor friction, print issues, and route
compatibility failures.

Exit gate: the Astro release consumes a pinned MPG artifact, every legacy
download contract is tested, both editions agree on artifact hashes, and the
new PDF has completed visual sign-off.

### Phase 5: cut over and retire legacy rendering (1–2 weeks)

Make web pages the default MPG destination and retain the PDF as a download.
Freeze the final legacy PDF for comparison. Remove Perl/TeX production steps
only after every legacy semantic construct and release product is classified
as migrated, replaced, frozen, or retired.

Keep the legacy extractor available in a tagged maintenance branch or container
for historical releases; do not carry it as an undocumented parallel source of
truth.

## Verification matrix

| Layer | Required checks |
|---|---|
| Source model | Schema, semantic references, stable-ID uniqueness, region DAG, path existence |
| Document engine | Unknown-node failure, duplicate/unresolved labels, citation and bibliography fixtures, include invalidation |
| Code | Exact artifacts, source maps, compile matrix, actual test count, output/exit assertions, capability skips |
| Figures | Reproducible derivatives, missing/unused assets, SVG accessibility, visual snapshots |
| Web | Astro type/build checks, HTML validation, internal/external links, accessibility, search metadata, screenshots |
| PDF | Structural `pdfinfo` checks, text extraction sanity, bookmark/link checks, rendered-page visual regression |
| Release | Clean checkout, pinned tools, no stale outputs, route aliases, archive contents, reproducible manifests |

One top-level command should run the contributor gate, even if it orchestrates
Python, Node, CMake, and TeX internally. For example:

```sh
uv run -- python -m tools.mpg check --gecode-root ../gecode
uv run -- python -m tools.mpg preview
uv run -- python -m tools.mpg build --format web
uv run -- python -m tools.mpg build --format pdf
uv run -- python -m tools.mpg release --version 6.4.0
```

Command names can change, but contributors should not need to know which
renderer owns each stage.

## Prototype evidence

### MyST to Astro

The hardened prototype now resolves five pages to JSON, renders five versioned
Astro routes, compiles and runs three Gecode models, and produces a visually
checked eleven-page A4 PDF. It includes deterministic SVG replacements for the
architecture, full crossword puzzle/solution, and heart nonogram.

The strict semantic adapter grew from 135 to 153 lines, plus a 22-line API role.
MyST 1.10.1 still reports no `literalinclude` dependencies and accepts a
duplicate-label warning under `--strict`. The hard pages also exposed stale
hashed downloads, Figure instead of Program floats, and mutation of `--` inside
PDF verbatim code. The 17-line fail-closed PDF repair now reconstructs all code
from resolved AST and restores Program kinds. See `research/prototypes/myst-astro`.

### Canonical reStructuredText/Sphinx to Astro

The Sphinx prototype uses a strict custom builder over resolved Docutils
doctrees and emits a semantic JSON release artifact, not Sphinx HTML. It passes
the same web, reference-inventory, C++, offline, and PDF fixture. Native
`literalinclude` invalidation was verified by touching only the external C++
file and observing exactly one source page reread. The hard fixture repeats
that test for all three examples. Its twelve-page A4 PDF has
consistent section, equation, figure, Program, and table numbering without a
post-export semantic repair.

The owned bridge is larger: 204 Python lines plus a 64-line JavaScript adapter.
reST is more ceremonial to author, the release boundary crosses Python and
JavaScript, XeTeX requires local Inkscape for SVG conversion, and the untagged
PDF emits a Font Awesome `ToUnicode` warning. See
`research/prototypes/rst-sphinx-astro`.

The complete fair comparison and measurements are in
`research/authoring-spike-results.md`.

### Native Astro/MDX

`research/prototypes/astro-mdx` passed Astro/TypeScript checks and rendered
KaTeX math, a semantic SVG, a callout, BibTeX citation/bibliography, syntax
highlighting, and a canonical raw-imported C++ download. CMake compiled that
same file against Gecode 6.4.0 and the program printed the expected solution.
Chrome produced a visually clean two-page A4 PDF.

The prototype also exposed the architectural cost: figure numbering and labels
are handwritten, bibliography support is a pinned community plugin, full-file
code prints too small, and Chromium produces an untagged PDF without full book
mechanics.

### Quarto/Pandoc

`research/prototypes/document-first` rendered multi-page HTML and a seven-page
A4 PDF from the same `.qmd` sources. It proved math, numbered cross-references,
citations, Graphviz SVG/PDF figures, Lua-filtered canonical C++ inclusion,
SHA-256 extraction, CMake compilation, CTest execution, and local-link checks.

This is the strongest fallback. Its limitation is structural: Quarto owns a
Bootstrap page shell, so deployment beside Astro can share branding, routes,
and release ownership but not the site's layouts and components.

### Format-neutral content model

`research/prototypes/content-model` validates the publication/artifact model
independently of authoring syntax. Its sample maps the real `less` propagator,
regions, projections, test wrapper, and an honest `test-harness` profile. All
eight invariant tests pass, including rejection of the current `-help` test
pattern.

## Decisions to make during Phase 1

These choices need evidence from the real Astro rebuild and hard chapter
slices; deciding them now would be guesswork:

- whether MPG content remains a separate repository artifact or joins an Astro
  monorepo;
- whether the web adapter emits HTML AST, Astro components, or a small hybrid;
- whether source-region markers live in C++ comments or sidecar maps;
- which PSTricks figures merit redraw versus temporary vector derivatives;
- whether tagged PDF is a cutover requirement or a separately scheduled
  accessibility milestone; and
- whether the active, continuously updated edition uses `current`, a Gecode
  version, or both with canonical URLs.

The phase must also select MyST or canonical reST/Sphinx using the recorded
production-slice evidence. None of these choices changes the format-neutral
content/artifact model. Quarto remains the fallback only if neither strict
Astro release adapter stays maintainable.
