# Astro + MDX MPG prototype

This isolated prototype asks one narrow question: can native Astro/MDX be the web-first source for an MPG chapter while keeping math, figures, references, canonical executable examples, and a credible PDF path? The answer from the spike is **yes for the web path, and yes with limitations for browser-generated PDF**.

## What it demonstrates

- Astro static output at the release-shaped base path `/doc/current/mpg/`.
- A typed content collection and a generic chapter route, ready to be mounted in the rebuilt website or emitted as a standalone static subtree.
- Tailwind CSS 4 through its Vite plugin, using the current website's Gecode brand/link colors and font roles.
- Display math via `remark-math` + `rehype-katex` (rendered at build time; no client JavaScript).
- BibTeX-backed citations and bibliography via `rehype-citation`.
- A semantic SVG figure, a linked figure cross-reference, and an Astro callout component.
- A C++ listing imported with `?raw` from `examples/send-more-money.cpp`. The `.mdx` file does not duplicate executable code; the same `.cpp` is the download and CMake test input.
- An optional PDF generated from the built web page by headless Chrome, with dedicated print CSS.

The visual shell is deliberately more editorial than the current site, but reuses the stable integration tokens found in the sibling `gecode.github.io` checkout: Tailwind 4, `#0b7646` brand green, `#005ba1` links, and the sans/display/mono font roles. No Astro implementation was present on the sibling checkout's `explore/astro-rework` branch when this was created.

## Exact commands

From this directory:

```sh
npm install
npm test
npm run dev
```

The dev URL is normally `http://localhost:4321/doc/current/mpg/`.

To compile and run the canonical example against a Gecode build:

```sh
cmake -S examples -B build/example -DGecode_DIR=/path/to/gecode/build
cmake --build build/example
./build/example/send-more-money
```

For an uninstalled development tree whose build directory has libraries but no exported `GecodeTargets.cmake`, use:

```sh
cmake -S examples -B build/example \
  -DGECODE_SOURCE_DIR=/path/to/gecode/source \
  -DGECODE_BUILD_DIR=/path/to/gecode/build
cmake --build build/example
./build/example/send-more-money
```

To render PDF with an installed Chrome/Chromium:

```sh
npm run pdf
```

The script detects Google Chrome on macOS and common Linux locations. Set `CHROME_PATH=/path/to/chromium` elsewhere. The result is `dist/mpg-prototype.pdf`.

## What was actually run (2026-08-09)

The following were run on macOS with Node 26.5.1, npm 11.17.0, the sibling Gecode 6.4.0 build, and installed Google Chrome:

```sh
npm install
npm test
cmake -S examples -B build/example \
  -DGECODE_SOURCE_DIR=/Users/zayenz/gecode/gecode-mpg-6.4.0 \
  -DGECODE_BUILD_DIR=/Users/zayenz/gecode/gecode-mpg-6.4.0/build
cmake --build build/example
./build/example/send-more-money
npm run pdf
```

See the final section below for the observed results; it is updated after verification rather than predicting success.

## PDF pathway assessment

Browser-to-PDF is the smallest web-first path: it preserves KaTeX, SVG, syntax highlighting, links, and most site styling with no second authoring format. It is appropriate for an attractive downloadable/manual snapshot. It does **not** provide TeX-quality book mechanics automatically: running headers, robust page-number cross-references, floats, widow/orphan control, indexes, and a book-wide table of contents need further work. Chromium also does not implement the `target-counter()` page-number extension used by specialist paged-media engines, so the prototype's cross-reference remains linked but does not gain a page number. The generated file is not a tagged PDF, so a production accessibility target needs either a post-processing/tagging stage or a renderer with suitable tagged-PDF support.

The full 44-line example can be kept intact on an A4 page, but only at a small type size. That is acceptable as a pipeline proof, not as the final book design. Production chapters should print pedagogically selected fragments extracted from the canonical `.cpp`, then provide the complete file through the download link or an appendix.

For production, evaluate two renderers against a full chapter:

1. Headless Chromium as the zero-cost baseline, using print CSS and explicit page-break rules.
2. PrinceXML as the quality benchmark (commercial), because CSS paged-media features can recover page-number references, running matter, footnotes, and stronger book layout without introducing a second source format.

Pandoc should remain an export/interop experiment, not the primary PDF path for native MDX. Imports and Astro components are executable module syntax rather than portable Markdown, so direct MDX-to-Pandoc requires a normalization/export pass. Maintaining such a pass risks creating a second renderer for every custom component.

## Integration and scaling notes

- Put the book content collection and components in the Astro website monorepo if the release cadence is shared. If MPG remains independent, build with a configurable `base` and copy `dist/` into the site's versioned documentation subtree.
- Replace handwritten `number="1.1"` and `label="Figure 1.1"` with a build-time reference registry before migration. The prototype proves anchors and semantics, not automatic numbering.
- Keep each executable example as a normal `.cpp` file. Add a small fragment component that extracts named line regions from that file at build time; never place independently maintained code fences in prose.
- Keep figures as SVG where possible, with source diagrams (Graphviz, Mermaid, Typst/CeTZ, or a checked-in drawing source) compiled in CI. Raster screenshots remain ordinary static assets.
- Build a book manifest for chapter order, navigation, PDF concatenation, version metadata, and redirects from old anchors. Astro collection frontmatter should describe content, while the manifest owns publication structure.
- Citation support works, but bibliography style and the existing `MPG.bib` corpus need migration tests. `rehype-citation` is a community dependency, so pin it and retain a fixture suite for citation IDs and generated anchors.

## Verification results

All final checks passed:

- `npm test` reported zero Astro/TypeScript diagnostics, built two static routes plus the C++ download endpoint, and found KaTeX output, figure/cross-reference anchors, a linked citation, bibliography, Shiki listing, and callout in the generated HTML.
- CMake compiled the canonical source against the local Gecode 6.4.0 source/build trees. Running it printed `{9, 5, 6, 7, 1, 0, 8, 2}`, the SEND + MORE = MONEY solution.
- `npm run pdf` generated a 246 KB, two-page A4 PDF with Chrome. Poppler rendered both pages to PNG for visual inspection: the equation no longer clips, the SVG is sharp, callout and references are aligned, syntax colors render correctly, and no elements overlap. The known limitation is the small full-file code type noted above.
- `pdfinfo` reports `Tagged: no`, confirming that Chromium output alone does not meet a tagged-PDF accessibility requirement.

The only build-time noise was Node's upstream `punycode` deprecation warning; npm reported zero package vulnerabilities.
