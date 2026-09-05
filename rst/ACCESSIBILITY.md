# PDF accessibility status

The HTML edition is the primary accessible MPG publication. The release PDF
preserves the established book design and provides useful PDF navigation, but
it is not currently a tagged or PDF/UA-conforming document. It must not be
described as accessible merely because its metadata and text extraction pass.

## Baseline enforced by the release build

`rst/scripts/build.py pdf` fails unless the PDF has populated title, author,
subject, and keyword metadata; exact `gecode.dev` release URLs; clean text
extraction; and resolved references. The LaTeX adapter sets the
catalog language to British English and enables `DisplayDocTitle`. It avoids
Font Awesome, Dingbats, and CC icon glyphs in published page content so that
admonitions, bullets, and license information do not extract as garbage.

The PDF retains its deep bookmark outline and correct Roman and Arabic page
labels. These are meaningful navigation improvements, but they do not replace
a semantic structure tree.

## Tagged-PDF spike, August 2026

The representative Sphinx fixture was built with TeX Live 2023's experimental
`tagpdf` support under XeLaTeX. The result reported `Tagged: yes`, but the log
reported invalid structure nesting, nested marked content, unmatched marked
content, and lack of inter-word-space support. `xdvipdfmx` also rejected two
nested link annotations. That output is not suitable for publication.

The normal release therefore remains deliberately untagged. Shipping tags that
are structurally invalid would give assistive technology less reliable output
while making the PDF look more capable than it is.

## Requirements for a real tagged-PDF track

A future spike must use a current LaTeX tagging stack and must cover the actual
MPG constructs, not only ordinary prose:

- title and publication pages, contents, Figures, Tips, and bookmarks;
- parts, chapters, sections, rubrics, lists, citations, and links;
- mathematical expressions with associated MathML or equivalent text;
- figures with authored alternative text or explicit artifact status;
- tables with header and cell associations;
- Programs and inline code with useful `ActualText` and reading order;
- MPG tips, run-in important paragraphs, and arbitrary-content figures.

Acceptance requires a strict full-book build, PDF/UA validation with veraPDF,
manual inspection of the structure tree and reading order, and tests with at
least one desktop screen reader. Visual parity must be checked independently;
tagging work is not allowed to silently change the classical PDF design.
