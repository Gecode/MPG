# MPG classical PDF package

This directory extracts the reusable visual grammar of the original *Modeling
and Programming with Gecode* PDF. It intentionally excludes PSTricks figures,
document-specific cross-reference macros, and authoring-format syntax.

`mpg-classic.sty` owns the Gecode palette, Charter/Bera typography, vector logo,
alphabetical part openings, blue chapter openings, and the small public part metadata API.
`mpg-sphinx.sty` is a thin Sphinx adapter for title matter, page furniture,
program boxes, and tips. Other writers should import the core and provide their
own similarly thin adapter.

The stable API needed by authoring adapters is:

```tex
\usepackage{mpg-classic}
\MPGLogo
\MPGSetPartAuthors{Christian Schulte, Guido Tack, Mikael Z. Lagerkvist}
\MPGSetPartBlurb{Introductory prose, lists, and other normal LaTeX content.}
\MPGPartNumber{13}{Modeling} % historical part M
\begin{MPGTip}{A short descriptive title}
Tip content.
\end{MPGTip}
```

Normal `\chapter` and `\part` commands acquire the classical design.
`\MPGPartNumber` preserves the original non-sequential mnemonic letters (13 is
M for Modeling, 3 is C for case studies). Adapters
should map their native titled-tip node to `MPGTip` and native program nodes onto
the shared colors rather than turn those constructs into raw LaTeX in source
documents.

The package requires an engine supported by `fontspec` when exact Charter text
is desired. It falls back to the document's existing serif face when Charter is
not installed. Bera Mono comes from TeX Live's `beramono` package.
`gecode-logo.pdf` is a direct vector conversion of the historical EPS logo; it
is a book-brand asset, not one of the explanatory illustrations being replaced.

## Sphinx integration test

The reST spike imports both style files through `latex_additional_files`. Its
native `mpg-part` directive writes the shared part metadata API, and `mpg-tip`
maps to the shared numbered `MPGTip` environment. Ordinary Sphinx
`literalinclude` remains the source of programs, so dependency tracking and
numbering are unchanged.

From `research/prototypes/rst-sphinx-astro`:

```sh
./scripts/verify-all.sh
```

The verification checks that the generated LaTeX contains the adapter and an
explicit historical part number, that the PDF embeds Charter and Bera Sans Mono, that no Font
Awesome icon font remains, and that the extracted PDF text contains the part
blurb and numbered tip. It also rejects overfull boxes and LaTeX font warnings.
The 19-page A4 result is rendered at 110 dpi under `tmp/pdfs/` for inspection.

Observed on 2026-08-09: the complete semantic, Astro, C++, incremental,
XeLaTeX, text, font, and render verification passed. The only TeX warning is
Sphinx's existing harmless `cmap` notice that it is inactive under XeTeX. The
PDF remains untagged; classical fidelity does not solve PDF accessibility.
