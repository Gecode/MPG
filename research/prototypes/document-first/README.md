# Document-first prototype: Quarto book

## Outcome

Quarto is the strongest document-first candidate for MPG. Its book model treats
HTML as a multi-page website and PDF as a second rendering of the same source.
It supplies chapter-wide cross-references, citations, MathJax/LaTeX math, search,
navigation, and download links without rebuilding those systems locally.

This prototype proves the hard content path:

- `modeling.qmd` contains math, a numbered equation and reference, a citation,
  a numbered vector figure and reference, and a complete C++ listing.
- `figures/propagation.dot` is the only hand-edited figure source. Graphviz emits
  SVG for HTML and PDF vector art for XeLaTeX.
- `examples/magic-sequence.cpp` is the only hand-edited program source. A
  dependency filter includes it in the book; extraction copies and fingerprints
  it; CMake compiles the extracted copy; CTest runs it against Gecode 6.4.0.
- `scripts/check_outputs.py` checks evidence in the rendered HTML, verifies that
  canonical and extracted programs match byte for byte, and checks the PDF.

Quarto books natively produce an HTML website and a continuous PDF, and Quarto
cross-references span chapters. These are documented in the official
[book guide](https://quarto.org/docs/books/),
[book cross-reference guide](https://quarto.org/docs/books/book-crossrefs.html),
and [cross-reference guide](https://quarto.org/docs/authoring/cross-references).
The two small filters use Pandoc's built-in Lua API, which avoids a separate
filter runtime; see the official [Pandoc Lua filter guide](https://pandoc.org/lua-filters.html).

## Exact experiment

The machine already provided Pandoc 3.6.4, Graphviz, XeLaTeX, CMake, Ninja, and
a sibling Gecode 6.4.0 installation. Quarto was absent, so the experiment used
the official macOS archive for Quarto 1.10.18 from its GitHub release.

From this directory:

```sh
curl -fL \
  https://github.com/quarto-dev/quarto-cli/releases/download/v1.10.18/quarto-1.10.18-macos.tar.gz \
  -o /tmp/quarto-1.10.18-macos.tar.gz
mkdir -p /tmp/quarto-1.10.18
tar -xzf /tmp/quarto-1.10.18-macos.tar.gz -C /tmp/quarto-1.10.18
make verify \
  QUARTO=/tmp/quarto-1.10.18/bin/quarto \
  GECODE_PREFIX=../../../../gecode/build/release-readiness-nompfr-install
```

The archive extraction directory can differ; pass its `bin/quarto` path. The
test on 2026-08-09 used Quarto 1.10.18 and the commands above. See **Observed
results** below for the recorded result. `quarto render` must render both formats
in one project invocation: separate `--to html` and `--to pdf` invocations clean
the shared output directory and remove the other format.

The downloaded macOS archive's SHA-256 digest was
`ddd6a71a9e0448ab15fb655bc589e11cb6589a248ec35ccd7f7f44137531688e`;
it matched Quarto's published `quarto-1.10.18-checksums.txt` entry.

## Astro and Tailwind integration

The cleanest initial integration is a versioned `/doc/MPG/` subtree in the same
release artifact as the Astro site. Astro builds the main site; Quarto builds
the book into the subtree; the release job validates internal links and deploys
their combined output. A small shared design-token file can feed Quarto's Sass
theme and Astro's Tailwind theme.

This is integration at the site and release layers, not one rendering engine.
Quarto emits complete Bootstrap-based pages, so Astro cannot directly wrap each
page in its own layout or reuse Tailwind components. If identical page chrome
and component reuse outweigh mature book behavior, an Astro/MDX pipeline is the
better architecture. Do not try to make Tailwind style Quarto's generated DOM;
that couples the book to unstable implementation details.

## Literate-programming direction

Use canonical external source files as the default. Documents include whole
files or named regions; CI discovers every declared dependency, produces a
manifest, compiles every complete file, and runs selected examples. This
prototype implements whole-file inclusion because its semantics are obvious.

Before migration, design named regions with these properties:

1. Region markers remain valid C++ comments and nest predictably.
2. The include filter and test manifest share one parser.
3. CI rejects missing, duplicate, overlapping, and unreferenced regions.
4. The downloadable file is always the compiled canonical source, never a
   concatenation reconstructed from prose.

This inverts the current TeX-first literate system: code stays valid and
testable before documentation processing, while prose selects views of it.

## Dependency gaps and risks

- Quarto is a large additional release dependency (the tested macOS archive was
  about 236 MB compressed). Pin its version and checksum in CI.
- PDF still requires a TeX distribution for the current XeLaTeX path. Quarto can
  target Typst later, but migration should first prove MPG's custom macros,
  indexing, floats, and typography against both engines.
- The prototype sets A4 explicitly, but its tiny three-chapter assembly leaves
  underfilled pages around the long, unsplittable code listing. Full-book
  pagination needs a representative migration sample. The generated PDF is not
  tagged; accessible-PDF requirements and engine support need a separate test.
- Graphviz is an explicit build dependency. Other complex figures should keep a
  checked-in source plus deterministic SVG/PDF render commands. Hand-authored
  SVG can bypass Graphviz while following the same dual-format contract.
- Quarto's HTML shell uses Bootstrap, not Astro/Tailwind. The recommended subtree
  release gives consistent brand, URL ownership, and navigation links, but not
  shared components.
- A future region extractor needs source maps so diagnostics point back to the
  canonical C++ file and region, not generated output.

## Observed results

`make verify` completed successfully on 2026-08-09:

- Quarto rendered `index.qmd`, `modeling.qmd`, and `references.qmd` to three
  navigable HTML pages, then produced the PDF with two XeLaTeX passes.
- The A4 PDF contained 7 pages; its final byte size is recorded by the output
  checker rather than treated as a stable fixture.
- CMake configured against the sibling Gecode 6.4.0 installation; Ninja built
  the extracted model; CTest passed `magic-sequence-smoke` (1/1 tests).
- The output check found Equation 1.1, Figure 1.1, the linked citation, the SVG,
  the code provenance attribute, and the included model in HTML. It verified 80
  local asset/link targets and proved the extracted model's SHA-256 digest
  matched its canonical source.
- A Poppler render of all seven PDF pages showed sharp vector art and code,
  readable mathematics and citations, working page references, and no clipped,
  overlapping, or missing content.
