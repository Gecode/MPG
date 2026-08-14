# MPG reStructuredText edition

The maintained manual lives in `content/`. reStructuredText is the source for
both editions: Sphinx writes release-shaped HTML for the Gecode website and
XeLaTeX writes the classical MPG PDF. The website build does not run Sphinx.
The tested, versioned output is built by the Gecode release job and imported as
an immutable bundle; see `RELEASE.md`.

The numbered book is a flat sequence of chapters. Part pages in
`content/parts/` provide the unnumbered HTML entry points. The first chapter of
each part includes the same blurb inside an `only:: latex` `mpg-part`
directive, which produces the lettered classical part opening without changing
chapter numbers.

For web development, run `npm install` once and then `npm run dev` from the
repository root. It performs the initial strict build, serves the output with
live reload, compiles the Tailwind CSS v4 shell, and watches all web publication
inputs. Use `npm run build` for a production-shaped HTML build and
`npm run preview` to inspect the last build without rebuilding it. The authored
stylesheet is `_static/mpg.css`; the build expands its Tailwind import and
template utilities into the release copy of that file.

## Authoring conventions

Every public section has an explicit source label. Colon labels are internal
authoring identifiers used for cross-references and shared PDF numbering; they
are never emitted into HTML. Web links use readable, title-derived fragments. Use
`:ref:` for named sections and `:numref:` for numbered programs, figures,
tables, equations, and tips.

Use `mpg-code` for published source. Its key resolves through
`manifests/code-projections.json` to a hash-checked canonical artifact or
fragment. `:caption:` makes the block a numbered Program; `:name:` gives it a
stable target; `:download:` links the exact source that the release test
compiled. Do not paste a second copy of executable C++ into a chapter.

Use `mpg-figure` when a numbered figure contains anything more complicated
than one image. Maintained visual sources are SVG files in `figures/`; the
deterministic PDF derivatives in `figures/pdf/` are used by XeLaTeX. Keep a
useful SVG title and description, and add meaningful reST alternative text.

Use `mpg-tip` for the manual's numbered, plain typographic tips. Its Sphinx
number is shared by the heading and every cross-reference in HTML and PDF.
Use ordinary admonitions only when the material is not an MPG tip.

API links are resolved against `release-reference-inventory.json`, generated
from the matching Gecode release. Citations live in `content/references.bib`.

## Required checks

The release gate is deliberately redundant. Source coverage proves that the
legacy book was not silently shortened; code projection checks prove that each
display is known; example validation compiles and runs the published programs;
figure checks verify both media; and strict Sphinx builds reject broken links
and unknown semantic nodes. The exact commands and packaging contract are in
`RELEASE.md`.

For visual review, inspect at least the root page, a part opening, a dense code
chapter, the nonogram and crossword pages, and a narrow viewport. For the PDF,
inspect the title, all six part openings, representative chapter and program
pages, the architecture figure, both puzzle figures, and the back matter.
