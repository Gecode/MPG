# MPG authoring and publishing toolchain landscape

Research date: 2026-08-09. Technical claims below link to primary project documentation.

## Recommendation after production-comparison spikes

Keep **MyST and canonical reStructuredText/Sphinx in the final gate, with
Sphinx now the provisional engineering leader**, until the difficult
`p-started` literate slices have been converted. Do not adopt either engine's
standalone website. Build MPG on Gecode releases, emit a semantic web bundle
and PDF, and let the Astro/Tailwind site import that bundle later.

The initial desk-research preference was MyST because its JavaScript AST looked
materially easier to compose with Astro. The hardened comparison disproved the
strength of that assumption: a strict Sphinx builder exported resolved doctrees
through a small Python/JavaScript bridge and preserved native incremental
dependencies and document numbering. The later architecture/crossword/nonogram
extension strengthened that result: Sphinx's doctree exporter did not grow,
while MyST required clean-output handling and exact-code/PDF-kind repair. MyST
retains the clearer source and smaller bridge. See
`authoring-spike-results.md`.

This direction best separates concerns:

- The selected document engine owns numbered equations, figures, citations,
  labels, cross-references, bibliography data, and book assembly. MyST exposes
  a resolved AST ([developer guide](https://mystmd.org/guide/developer)); Sphinx
  supports custom builders over resolved doctrees
  ([builder documentation](https://www.sphinx-doc.org/en/master/development/howtos/builders.html),
  [resolved-doctree event](https://www.sphinx-doc.org/en/master/development/tutorials/extending_build.html)).
- Astro owns the website: routing, navigation, site chrome, Tailwind tokens, responsive behavior, search integration, and release flow. Astro can render content collections and lets Markdown processing be extended, while Starlight adds documentation navigation and overridable components if the new site wants those pieces ([Astro Markdown](https://docs.astro.build/en/guides/markdown-content/), [Starlight authoring](https://starlight.astro.build/guides/authoring-content/), [Starlight customization](https://starlight.astro.build/guides/customization/)).
- The existing MPG tooling keeps ownership of example extraction, compilation,
  execution, and manifests. Authoring extensions consume that pipeline and
  return ordinary code, figure, and link nodes.

Both expanded fixtures now pass. The remaining gate is the deepest nested
literate-code coverage, authoring clarity, adapter growth, and PDF
maintenance—not basic feasibility or complex vector illustration support.

Gecode's reference documentation has a separate release lifecycle. Its release
build should emit a versioned symbol inventory beside the rendered reference
tree; the website later imports both artifacts. MPG and ordinary website builds
consume that inventory and must not rebuild the reference documentation.

## The requirement that changes the decision

MPG's current literate layer does more than show code. A chapter owns named and nested fragments, expands fragment references, creates complete downloadable C++ files, and then compiles/tests those generated files. A replacement must preserve the invariant:

> What readers see, download, and what CI compiles must have one traceable source.

The long-term design should invert most examples: keep a complete, buildable `.cpp` file as canonical and include tagged regions in prose. That makes the tested file the downloaded file. Retain document-driven tangling only for the few pedagogical examples whose construction order is itself the lesson. Antora/AsciiDoc has first-class tagged and line-range includes ([Antora partial includes](https://docs.antora.org/antora/latest/page/include-a-partial/)); Quarto has source-file inclusion through extensions ([Quarto extensions](https://quarto.org/docs/extensions/)); MyST directives are programmable and can return standard AST nodes ([MyST JavaScript plugins](https://mystmd.org/guide/javascript-plugins)). All three can implement this invariant. Plain MDX and Markdoc require a custom component/build plugin to do it.

## Comparison

Ratings are relative to MPG's requirements, not general product quality. `5` is the strongest fit. “Astro” means visual and release-flow integration into the new Gecode site, not merely the ability to emit HTML.

| Candidate | Astro | Math, figures, xrefs, cites | Literate/test path | PDF | Maintenance | Main issue |
|---|---:|---:|---:|---:|---:|---|
| MyST engine + Astro adapter | 4 | 5 | 5 | 5 | 4 | Small bridge; local dependency/strict/PDF controls |
| canonical reST/Sphinx + Astro adapter | 4 | 5 | 5 | 5 | 5 | Larger two-runtime bridge; denser source |
| Astro Markdown/MDX + Starlight | 5 | 3 | 4 | 2 | 4 | PDF and book semantics become local infrastructure |
| Quarto/Pandoc | 2 | 5 | 5 | 5 | 4 | Its Bootstrap website is a second design system |
| Antora/AsciiDoc | 2 | 4 | 5 | 3 | 4 | Separate site generator; weaker citations/PDF math |
| Asciidoctor.js embedded in Astro | 4 | 4 | 5 | 3 | 3 | Two runtimes/converters and custom integration |
| Markdoc in Astro | 5 | 2 | 3 | 1 | 3 | No native scholarly/book or PDF pipeline |
| Typst as canonical source | 1 | 4 | 3 | 5 | 3 | Production HTML is explicitly not ready |

### MyST Markdown

MyST is the best authoring fit. It labels and references sections, equations, figures, tables, arbitrary blocks, and other documents; consumes BibTeX; supports file downloads; emits LaTeX- or Typst-based PDFs from local templates; and can resolve external Sphinx `objects.inv` inventories ([references](https://mystmd.org/guide/cross-references), [PDF exports](https://mystmd.org/guide/creating-pdf-documents), [downloads](https://mystmd.org/guide/website-downloads), [intersphinx](https://mystmd.org/guide/external-references#sphinx-documentation)). The last feature could replace many current `\gecoderef` links if Gecode's API documentation exposes an inventory, or provide a model for generating an equivalent inventory from Doxygen.

MyST's default web themes use React/Remix and Tailwind, not Astro. Custom CSS exists, but the project labels parts of it work in progress ([website styling](https://mystmd.org/guide/website-style)). Shipping the default MyST book alongside Astro would therefore look adjacent rather than integrated. Consuming its resolved AST within Astro is the key architectural move.

MyST plugins can add directives, roles, and transforms, but renderer plugins are still listed as planned ([plugin status](https://mystmd.org/guide/plugins)). Therefore `gecode-code` should transform into standard code and link nodes rather than invent a permanent output-specific node.

### Astro Markdown/MDX and Starlight

This is the best web shell. Astro content is directly available to layouts and components, supports Markdown/MDX, heading IDs, content collections, and configurable Markdown processors; Tailwind can style rendered Markdown in the same build ([Markdown](https://docs.astro.build/en/guides/markdown-content/), [styling](https://docs.astro.build/en/guides/styling/)). Starlight supplies documentation navigation, asides, Expressive Code, search-oriented page structure, and component overrides ([authoring](https://starlight.astro.build/guides/authoring-content/), [configuration](https://starlight.astro.build/reference/configuration/)). If the Gecode site already has equivalent navigation and search, use its layouts directly rather than adding a visibly separate Starlight shell.

The weakness is portability. MDX embeds JSX and imports; Pandoc/LaTeX cannot interpret those components. Math can be added through the Markdown plugin layer, but numbered cross-format figures, citations, references, and a book-quality PDF are not one coherent Astro feature. An Astro-first solution therefore needs a constrained semantic Markdown dialect and a second renderer. At that point it is recreating part of MyST or Quarto.

Markdoc improves schema validation and maps tags to Astro components; it also supports partials ([Astro Markdoc integration](https://docs.astro.build/en/guides/integrations-guide/markdoc/)). It does not solve scholarly cross-references, citations, math, or PDF. It is a good website CMS syntax, not the best book source.

### Quarto and Pandoc

Quarto is the strongest low-custom-code dual-output option. Its Pandoc Markdown handles TeX math, citations, cross-references, figures, callouts, Mermaid/Graphviz, raw format-specific blocks, books, and LaTeX or Typst PDF ([Markdown](https://quarto.org/docs/authoring/markdown-basics.html), [figures](https://quarto.org/docs/authoring/figures-and-layout.html), [diagrams](https://quarto.org/docs/authoring/diagrams.html), [PDF options](https://quarto.org/docs/reference/formats/pdf.html)). Lua filters can manipulate Pandoc's AST and are well suited to an MPG code directive ([Pandoc Lua filters](https://pandoc.org/lua-filters.html)).

Its web output uses Bootstrap 5 by default, though the theme can be disabled ([HTML theming](https://quarto.org/docs/output-formats/html-themes.html)). A Quarto website would duplicate Astro routing, navigation, search, and styling. Rendering content fragments into Astro is possible in principle, but then cross-page assets and links, heading metadata, and rebuild invalidation become a custom bridge comparable to the MyST bridge, with a less Astro-native AST ecosystem. Keep Quarto/Pandoc as the fallback PDF renderer or migration tool, not the default web generator.

### Canonical reStructuredText with Sphinx

Sphinx is the conservative documentation choice. It has mature
cross-references and domains, extensions, incremental dependencies, and a
standard LaTeX/PDF build ([Sphinx overview](https://www.sphinx-doc.org/en/master/),
[cross-references](https://www.sphinx-doc.org/en/master/usage/referencing.html),
[PDF quickstart](https://www.sphinx-doc.org/en/master/usage/quickstart.html)).

The spike did not integrate Sphinx HTML. A strict custom builder consumed
resolved doctrees and emitted a small semantic JSON release artifact for
Astro. This made the site integration comparable to MyST and retained native
`literalinclude` invalidation. The costs are reST's denser punctuation, a
Python/JavaScript boundary, and a larger supported-node bridge. It is now a
finalist rather than a rejected standalone-site option.

### Antora and AsciiDoc

AsciiDoc is excellent for code-heavy manuals: tagged source includes are standard, cross-references are explicit, STEM passes TeX/AsciiMath to a renderer, and Asciidoctor Diagram supports many text diagram formats ([includes](https://docs.antora.org/antora/latest/page/include-a-partial/), [STEM](https://docs.asciidoctor.org/asciidoc/latest/stem/), [diagrams](https://docs.asciidoctor.org/diagram-extension/latest/)). Antora adds versioned, multi-repository documentation and a replaceable UI bundle ([content sources](https://docs.antora.org/antora/latest/content-source-repositories/), [pipeline](https://docs.antora.org/antora/latest/how-antora-works/)). Those strengths exceed MPG's immediate needs and introduce a second site generator.

Asciidoctor PDF is reproducible and supports internal links, SVG, outlines, syntax highlighting, print mode, and YAML themes, but its theme has limited influence over layout and its bibliography support is basic without an extension ([PDF features](https://docs.asciidoctor.org/pdf-converter/latest/features/), [theme limits](https://docs.asciidoctor.org/pdf-converter/latest/theme/), [bibliography](https://docs.asciidoctor.org/asciidoc/latest/sections/bibliography/)). It is a sound alternative for a code manual, but weaker than MyST/Quarto for MPG's mathematical book and current PDF expectations.

### Typst

Typst is compelling only as a PDF backend. Its language has first-class math, figures, references, bibliography, scripting, and fast PDF generation ([syntax](https://typst.app/docs/reference/syntax/), [math](https://typst.app/docs/reference/math/)). Quarto and MyST can both target it.

Do not use Typst as the canonical web-primary source now. Typst's own documentation says HTML export is incomplete, behind a feature flag, unsuitable for production, and cannot yet emit embeddable fragments or CSS ([HTML status](https://typst.app/docs/reference/html/)).

## Completed fixture and remaining decision gate

The two-page fixture covered the core forms. The overview/crossword/nonogram
extension added five deterministic SVGs, three code projections, two complete
executable models, exact downloads, lists, a second equation, and multi-chapter
PDF pressure. The real production slice must still add the cases most likely to
separate the candidates:

1. the deepest nested `p-started` projections and a genuinely progressive
   tangled artifact;
2. subfigures or composite layouts, a generated Graphviz/Mermaid diagram, and
   an existing raster screenshot;
3. footnotes, indexes/glossaries, dense tables, and the full MPG math macro set;
4. broad API-inventory coverage rather than one typed symbol;
5. import into the actual rebuilt Astro/Tailwind layout and navigation; and
6. chapter-scale PDF pagination, code wrapping, bibliography, and index work.

Both MyST and reST/Sphinx fixtures proved these baseline properties:

- Astro gets resolved labels, numbering, headings, metadata, and stable URLs without scraping generated HTML.
- The same directive expansion feeds HTML and PDF.
- CI fails on unresolved references, duplicate labels, stale generated files, extraction errors, compile/test failures, and PDF errors.
- All network-fetched templates and tool versions can be pinned or vendored. MyST otherwise fetches independently updated templates, so an unpinned build is not reproducible ([template update behavior](https://mystmd.org/guide/update-myst#update-the-myst-markdown-command-line-interface)).
- Each adapter is a strict resolved-tree mapping rather than a fork or an HTML
  scraper.

The remaining proof converts the same real `m-started` and `p-started` slices in
both formats and compares authoring review, supported-node and adapter growth,
incremental invalidation, PDF repair effort, and preservation of legacy
semantics. If neither candidate stays narrow, choose **portable Pandoc/Quarto
Markdown plus a local Lua filter**, generate semantic HTML fragments for Astro,
and render PDF with Quarto's LaTeX backend. Avoid MDX components in canonical
prose; reserve Astro components for page layouts around generated content.

## Reproducible release baseline

Whichever route wins, pin the document compiler, Node/Python dependencies, TeX Live year or Typst binary, fonts, syntax-highlighting theme, diagram renderers, and PDF template. Vendor the book template and fonts. Build in a fixed Linux container, set deterministic metadata/timestamps where the backend permits, retain an extracted-source manifest, and test both website link integrity and PDF creation in CI. Keep visual regression snapshots for one HTML page and a small set of PDF pages; byte-identical PDF output is useful when achievable but should not replace structural and visual checks.
