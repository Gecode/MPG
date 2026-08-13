# Canonical reStructuredText / Sphinx / Astro spike

This source-only prototype tests the stability-first candidate for MPG. Canonical
reStructuredText is parsed and resolved by Sphinx; a strict custom builder exports
a small semantic JSON release artifact; Astro owns routes, layout, KaTeX rendering,
and CSS. Sphinx's LaTeX writer creates the optional book PDF from the same source.

The result is positive. This is a credible alternative to MyST and should remain
in the `m-started` / `p-started` production gate. Its strongest result is that
Sphinx supplies mature, consistent reference semantics without forcing the web
presentation to use Sphinx HTML. Its main costs are reST's heavier authoring syntax,
a Python-to-JavaScript artifact boundary, and a narrow custom builder that must be
maintained as an explicit supported-node contract.

## Release integration boundary

The Gecode release documentation is **not** built here or by the normal Astro site
build. The prototype consumes the shared checked-in
`../shared/reference-inventory.json`, representing a versioned artifact produced
alongside the Gecode 6.4.0 reference documentation and imported into the website:

```text
Gecode release job
  -> rendered /doc/6.4.0/reference/ tree
  -> reference-inventory.json

MPG release job
  reST + canonical examples + imported inventory
  -> Sphinx resolved doctrees
  -> publication.json + tested downloads + PDF

Website release/import
  publication.json -> Astro layouts/CSS -> /doc/6.4.0/mpg/
```

The fixture's typed key `class:Gecode::Space` becomes
`/doc/6.4.0/reference/classGecode_1_1Space.html`. No Doxygen executable or
reference source is present in the spike.

This follows Sphinx's intended extension boundary: builders are registered with
`add_builder`, and Sphinx resolves cross-references before writing documents. See
the official [builder documentation](https://www.sphinx-doc.org/en/master/development/howtos/builders.html)
and [resolved-doctree build event](https://www.sphinx-doc.org/en/master/development/tutorials/extending_build.html#the-event-callback-api).

## What the spike proves

- Five Astro routes are generated from resolved doctrees, not scraped Sphinx HTML.
- Section 1, Equation 1.1, Figure 1.1, Program 1.1, and Table 1.1 agree in source
  references, web captions/links, and PDF output.
- The fixture includes an SVG figure, tip admonition, shared `\Gecode` math macro,
  BibTeX citation and bibliography, and a typed imported Gecode API reference.
- `literalinclude` selects the named `posting` region from one canonical complete
  C++ file. The same bytes are compiled, run, and published as the download.
- Sphinx records `../examples/send-more-money.cpp` in `first-page`'s dependency
  set. With the builder's own outdated set empty, touching that file caused Sphinx
  to report exactly one changed source and reread `first-page`; this is not an
  unconditional full rebuild.
- Both the Python semantic builder and JavaScript Astro adapter deliberately fail
  on unknown node kinds.
- A poisoned HTTP proxy clean rebuild succeeds after installation. The build does
  not download themes, templates, reference docs, or other mutable resources.
- Sphinx/XeLaTeX creates a nineteen-page, two-sided A4 PDF with classical title,
  part, blurb, and chapter openings. All pages were
  rendered with Poppler and visually inspected with no clipping, overlap, or
  illegible text. Six SVG figures remain sharp and code, math, and callouts fit.
- The shared `../shared/classical-pdf/mpg-classic.sty` package is backend-neutral;
  `mpg-sphinx.sty` is a thin adapter. The PDF embeds Charter for prose and Bera
  Sans Mono for programs, reproduces centered folios, and uses native semantic
  `mpg-part` and `mpg-tip` directives rather than raw LaTeX in reST.

Sphinx documents `literalinclude` as the facility for including external code and
supports named captions and selected ranges; it also numbers figures, tables, and
code blocks. See the official [directive reference](https://www.sphinx-doc.org/en/master/usage/restructuredtext/directives.html#directive-literalinclude).
The prototype uses `sphinxcontrib-bibtex` for global BibTeX-backed citations, as
described in its [official documentation](https://sphinxcontrib-bibtex.readthedocs.io/en/latest/).

## Install and verify

Prerequisites are Python 3.13, `uv`, Node/npm, CMake/Ninja, a Gecode 6.4 source and
build tree, XeTeX/latexmk, Inkscape, and Poppler (`pdfinfo`, `pdftotext`, and
`pdftoppm`). The SVG-to-PDF conversion uses Sphinx's official `imgconverter`
extension and the locally installed Inkscape; the SVG remains the canonical figure.

From this directory:

```sh
uv venv --python 3.13 .venv
uv pip install --python .venv/bin/python -r requirements.lock
npm ci
GECODE_SOURCE_DIR=/path/to/gecode/source \
GECODE_BUILD_DIR=/path/to/gecode/build \
  ./scripts/verify-all.sh
```

On the machine used for this spike the script's default sibling Gecode paths work,
so the final command was simply:

```sh
./scripts/verify-all.sh
```

Generated virtual environments, semantic data, Astro source routes, published
assets, website, CMake output, LaTeX output, PDF, and rendered page PNGs are ignored.
Only source and lockfiles are delivered.

## Observed verification result (2026-08-09)

The complete command passed:

- Sphinx 8.2.3 completed both semantic and LaTeX builds with `-W -n` and no Sphinx
  warnings; `sphinxcontrib-bibtex` is pinned at 2.6.5.
- Astro 7.2.0 generated exactly five publication routes; `astro check`
  reported zero errors and zero warnings.
- CMake compiled the complete 45-line example against the local Gecode 6.4.0
  source/build tree. CTest ran one test in 0.33 seconds and matched
  `{9, 5, 6, 7, 1, 0, 8, 2}`.
- `cmp` confirmed byte identity between the canonical example, staged download,
  and final Astro download.
- Incremental verification inspected Sphinx's pickled dependency set, touched the
  C++ source, and observed `0 added, 1 changed, 0 removed` with `first-page` read.
- The structural checker passed section/equation/figure/program/table agreement,
  accessible KaTeX MathML, SVG, callout, citation/bibliography, API URL, cross-page
  link, PDF content, and both unknown-node failure paths.
- `pdfinfo` reports nineteen A4 pages, approximately 176 KB, and `Tagged: no`.
  Poppler renders of all pages are under `tmp/pdfs/` after verification.

XeTeX emitted an upstream Font Awesome `ToUnicode` warning for Sphinx's tip icon.
The prose itself extracts correctly, but the warning and untagged PDF mean the
default template does not yet satisfy a strong PDF accessibility target.

## Measurements

Measured on arm64 macOS with Python 3.13.2, Node 24.19.0, npm 11.17.0, AppleClang
21.0.0, TeX Live 2023, and Poppler 25.03.0:

| Measurement | Result |
|---|---:|
| Direct Python dependencies | Sphinx 8.2.3; sphinxcontrib-bibtex 2.6.5 |
| Direct npm dependencies | Astro 7.2.0; KaTeX 0.16.22; @astrojs/check 0.9.6; TypeScript 5.9.3 |
| Python extension | 204 lines |
| JavaScript semantic-to-Astro adapter | 64 lines |
| Combined owned semantic bridge | 268 lines |
| Semantic JSON | 49,283 bytes |
| Final web tree | 1,217,928 bytes (mostly local KaTeX fonts) |
| Final PDF | approximately 176 KB; 19 two-sided A4 pages |
| Clean semantic build | 0.81 s wall time |
| Semantic-to-Astro production build | 1.53 s wall time |
| Installed Python environment | 72 MiB |
| Installed npm tree | 210 MiB |

## Authoring assessment and workarounds

Canonical reST is precise and mature. Labels, roles, directives, admonitions,
tables, `literalinclude`, and bibliography markup have stable, explicit meanings.
For a long-lived technical book this explicitness is valuable. Compared with MyST,
however, ordinary source is visibly noisier: directive option indentation, grid or
list tables, separate targets, and role syntax create more punctuation around the
prose. Occasional web contributors will likely find MyST quicker to learn.

The prototype needed four format-specific choices:

1. A small unrendered root `toctree` establishes chapter order and numbering; only
   its five child documents enter the Astro publication manifest.
2. The semantic builder prefixes Sphinx's local equation number with the document's
   chapter number. Resolved equation references already contain the full number;
   this small normalization makes the exported equation node match them.
3. A custom `:api:` role validates typed symbols against the imported JSON. A
   production implementation could instead generate a Sphinx domain/inventory,
   but this spike intentionally tests the agreed release JSON contract.
4. `sphinx.ext.imgconverter` invokes local Inkscape because XeTeX does not consume
   SVG directly.

The strict builder currently supports only the constructs exercised by the shared
comparison fixture. This is intentional: every unmapped doctree node is a build
error rather than silently disappearing. The larger production pilot must add and
test nodes for indexes/glossaries, footnotes, nested lists, complex tables,
subfigures, custom MPG callouts, and all structures found in `m-started` and
`p-started`.

## Decision implication

The spike weakens the earlier claim that MyST has a uniquely cheap Astro boundary.
Canonical reST/Sphinx required 268 lines for the complete strict bridge and gave us
correct PDF/web numbering, native external-file dependency invalidation, mature
cross-document diagnostics, and no mutable build downloads. The JSON boundary is
simple enough to be imported as part of the release flow described above.

MyST still has the clearer source syntax and a single JavaScript ecosystem. Sphinx
has the stronger demonstrated semantics and PDF behavior. The fair next step is to
run both against the same difficult `m-started` / `p-started` slices and compare
supported-node growth, source readability after real conversion, API inventory
coverage, PDF design effort, and maintenance cost. This spike is sufficient to keep
reST/Sphinx in that gate; it is not sufficient to begin wholesale migration.
