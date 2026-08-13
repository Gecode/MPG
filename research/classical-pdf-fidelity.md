# Retaining the classical MPG PDF

## Conclusion

Retaining the original MPG's look and feel is feasible. It is not primarily an
authoring-format problem: both finalists eventually produce LaTeX. It is a
question of how reliably each document engine exposes the book semantics that a
local LaTeX design package must style.

On the evidence from the hardened spikes, canonical reStructuredText with
Sphinx has a material advantage. It already produces a manual with chapters,
page furniture, contents, numbered figures, tables and programs, bibliography,
and index machinery. Sphinx can load a local style package, replace individual
LaTeX support components, select a custom LaTeX theme, and map semantic
containers to named LaTeX environments. The current spike is visually generic,
but its generated LaTeX has the right structural joints.

MyST can also use a completely local `jtex` template, so a classical-looking
PDF is possible. The present spike owns its 71-line template and is therefore
easy to restyle at the page level. Its harder problem is semantic: the current
export emits release pages as repeated section/subsection pairs, exports named
code blocks through a figure-like path, needs a fail-closed repair to preserve
some verbatim C++, and has no demonstrated index or MPG-style part-blurb path.
Those are solvable, but they put more correctness and upgrade risk in the local
adapter.

Therefore the classical PDF requirement strengthens the provisional choice of
Sphinx. It does not rule MyST out, but the final pilot should require MyST to
prove the same book structure rather than merely demonstrate that its template
can use the same colors and fonts.

## Implemented spike result

The extraction and both integrations have now been built, not merely estimated.
The shared `prototypes/shared/classical-pdf/mpg-classic.sty` is 135 lines and
contains the palette, Charter/Bera typography, historical mnemonic part
openings, chapter openings, part blurbs, plain numbered tips, and page
furniture. It excludes all PSTricks illustrations. Thin backend packages adapt
Sphinx and MyST without putting raw LaTeX in canonical prose.

The reST/Sphinx pipeline produces a visually inspected 19-page, two-sided A4
PDF. It uses semantic `mpg-part` and `mpg-tip` directives, Sphinx's native
chapters and programs, and the public LaTeX customization interface. Its full
semantic, Astro, C++, dependency-invalidation, PDF, embedded-font, and rendering
verification passes.

The MyST pipeline produces a visually inspected 14-page A4 PDF with the same
logo, part M opening, chapter treatment, plain tips, orange programs, Charter,
Bera Mono, and centered folios. Its full Astro, C++, generated-TeX, PDF, font,
and semantic verification passes. However, this required a 70-line fail-closed
generated-TeX adapter to map five article wrappers to chapters, remove three
duplicate headings, map two tips, and restore four exact code/program nodes.
The current MyST project tree also provides no useful part node, so part M
metadata remains in the pinned PDF template.

The experiment therefore confirms the predicted distinction: both can retain
the design, but Sphinx retains the book structure with less backend-specific
repair. Neither PDF is tagged.

## What “retain the look and feel” should mean

There are three materially different targets:

1. **Visual continuity**: A4, Charter-family text, Bera Mono code, Gecode
   colors, similar margins, link colors, and restrained use of tinted boxes.
   Either finalist can do this.
2. **Structural fidelity**: two-sided book layout; Roman front matter; part and
   chapter openings; restrained page furniture; stable chapter-based numbering; lists of
   figures and tips; characteristic program blocks; bibliography and index.
   Sphinx is currently closer and presents lower implementation risk.
3. **Facsimile fidelity**: the same line breaks, floats, and page numbers as the
   580-page legacy PDF. This is neither realistic nor desirable after rewriting
   prose, repairing examples, and replacing figures. It would turn pagination
   into a compatibility interface and prevent ordinary editorial improvement.

The production acceptance criterion should be level 2: readers should
immediately recognize the PDF as a new edition of the same book, without
requiring page-for-page identity.

## The original design is unusually recoverable

The legacy appearance is an explicit design system in
`docs/src/static/macros.tex`, not an emergent side effect of a proprietary
formatter:

- A4, 12-point, two-sided `report`, with chapters opening on right-hand pages.
- Charter text and MathDesign Charter mathematics, with Bera Mono at 88% for
  source code.
- Four named Gecode colors and a small set of fixed tint levels.
- Large boxed alphabetic part numbers in orange and boxed chapter numbers in
  blue, with right-aligned titles.
- Sparse, asymmetric title and part-opening pages followed by dense technical
  body pages.
- Orange program panels, red command panels, semantic green/red/blue code
  accents, green URLs, and blue internal references.
- Chapter-numbered tips with a closing triangular mark and a dedicated list of
  tips.
- Roman-numbered front matter, plain centered folios without running headers,
  contents, list of figures, list of tips,
  bibliography, changelog, and license.

The current corpus gives this design package a substantial workout: 42 chapter
declarations, six part blurbs, 78 tips, 213 figure environments, and at least 79
table or tabular environments. The existing PDF embeds the expected Charter,
MathDesign Charter, and Bera Mono fonts. All are still available in the local
TeX environment; a modern build can either retain the packages or use a
metrically close OpenType Charter setup.

Only some of the 388-line legacy macro file is publication styling. Much of the
remainder draws domain-specific PSTricks figures. Once those illustrations move
to generated SVG/PDF assets, the reusable classical book layer becomes smaller,
clearer, and compatible with a direct XeLaTeX or LuaLaTeX release build.

## Evidence from the two spikes

### reStructuredText and Sphinx

The 12-page hard-page PDF already has a real manual skeleton: title matter,
contents, chapter openings, configurable headers and footers, chapter-numbered
figures/tables/programs, code captions, admonitions, bibliography, and an index
step. The default FreeSerif/FreeSans presentation and `fncychap` chapter style
do not resemble the MPG, but those are configuration defaults rather than
limitations. In particular, production styling should remove the current
Sphinx running chapter headers to recover the legacy PDF's quieter pages.

Sphinx's documented LaTeX interface supports the required approach:

- `latex_elements` can set point size, fonts, preamble, chapter package, page
  geometry, and other book settings;
- `latex_additional_files` can vendor `mpg-book.sty` and, if required, replace a
  narrowly selected Sphinx LaTeX component;
- a custom LaTeX theme can choose the document class and top-level sectioning;
- semantic reST containers become `sphinxclass...` environments, giving custom
  MPG nodes explicit styling hooks;
- program listings and admonitions already have stable public LaTeX
  environments.

This means most fidelity work is declarative LaTeX. The custom Sphinx extension
should identify semantics such as an MPG tip, command transcript, program
projection, part blurb, and download marker; the style package decides how they
look. The Astro adapter need not know any of the PDF styling.

Main risks:

- Sphinx's own LaTeX support evolves, so overrides must use public hooks and
  pin the release toolchain. Copying all of `sphinx.sty` would create an
  unnecessary maintenance fork.
- MPG part pages have an unusual two-page structure: a sparse letter/title page
  followed by a prose blurb. This needs a small custom directive/node or a
  carefully controlled sectioning convention.
- The classic 12-point density must be tested on code-heavy pages. Sphinx's
  default code environment is sound, but its spacing and wrapping need MPG
  tuning.
- The current Font Awesome `ToUnicode` warning should disappear when the default
  icon-heavy admonitions are replaced by the simpler MPG tip treatment.

Assessment: **high feasibility, moderate effort, low-to-moderate ongoing risk**.

### MyST

The 11-page hard-page PDF proves that a fully local MyST LaTeX template can
produce clean A4 output and reuse the exact SVG/PDF figures used on the web.
Replacing Latin Modern with Charter/Bera, changing geometry, adding two-sided
layout, and copying the part/chapter definitions are straightforward template
work.

The difficulty lies before the template. In the current generated TeX:

- each imported page is emitted as both `\section` and a same-named
  `\subsection`, so it is not yet a 42-chapter book tree;
- program labels required a post-export repair for correct object kind and exact
  verbatim content;
- the hard spike does not exercise native part/blurb, list-of-tips, or index
  output;
- bibliography works, but the previous resolved-tree run reported an unhandled
  bibliography node;
- literal-include dependencies need an explicit external manifest.

MyST's official `jtex` system permits arbitrary local LaTeX templates and custom
template options. That is enough for visual continuity, but a template cannot
repair missing or misclassified semantics on its own. Achieving structural
fidelity requires either improving the resolved-tree-to-LaTeX projections or
maintaining a strict, tested transformation before typesetting.

Assessment: **high visual feasibility, medium structural feasibility,
moderate-to-high effort and ongoing adapter risk** with the currently tested
engine.

## Comparative effort

These are planning ranges for one engineer familiar with LaTeX and the chosen
document engine. They are not migration estimates for the 580-page content.

| Work package | Sphinx/reST | MyST |
| --- | ---: | ---: |
| Extract and modernize the shared `mpg-book.sty` | 1–2 weeks | 1–2 weeks |
| Fonts, geometry, colors, title, page furniture | 2–4 days | 2–4 days |
| Part/chapter openers and front/back matter | 3–6 days | 1–2 weeks |
| Programs, commands, tips, tables, lists | 1–2 weeks | 2–3 weeks |
| Representative-page tuning and regression tests | 1–2 weeks | 1–2 weeks |
| **Likely total PDF-template effort** | **4–7 weeks** | **6–10 weeks** |

The ranges include hardening and visual regression, not just obtaining one
attractive sample. MyST could close the gap if its deep pilot demonstrates a
cleaner chapter/part mapping and eliminates the code repair. Conversely, a
requirement for exact legacy pagination would make both estimates much larger
and should be rejected.

## Recommended implementation

Create a backend-independent classical style package with a very small semantic
API rather than importing the legacy macro file wholesale:

- book metadata and title-page commands;
- part opener plus optional authors and blurb;
- chapter opener;
- `mpgtip`, `mpgprogram`, and `mpgcommand` environments;
- figure/table/program caption policies;
- contents, lists, bibliography, changelog, license, and index setup;
- fonts, geometry, colors, links, page furniture, and code typography.

Keep puzzle, architecture, search-tree, and other illustration macros out of
this package. Their generated SVG/PDF replacements are assets, not book-theme
primitives.

For Sphinx, load the package through `latex_additional_files` and map semantic
nodes to these environments. Use `latex_elements` and public Sphinx macros
before considering component replacement. For MyST, put the same package under
the local `jtex` template and add a fail-closed test that verifies the complete
book hierarchy and every custom node kind in generated TeX.

## Fidelity acceptance set

The final authoring pilot should migrate enough real material to render this
fixed comparison set against the legacy PDF:

1. cover and publication page;
2. a multi-page table of contents;
3. the Modeling part opener and its blurb page;
4. Chapter 2's opener and first dense prose page;
5. the full-page Send More Money program and a page of nested literate
   projections;
6. a page containing multiple numbered tips;
7. one difficult table and one equation-heavy page;
8. modern overview, crossword, and nonogram figures;
9. bibliography, changelog, license, and a populated index.

For each page class, store the legacy reference rendering and the new rendering
at the same resolution. Review typography, margins, hierarchy, color, wrapping,
floats, widows/orphans, and page parity. Automated image diffs should flag
change, not demand pixel equality; approval remains visual because corrected
content will legitimately reflow.

The PDF gate should also verify embedded fonts, bookmarks, internal and external
links, extracted text, page size, and object numbering. Tagged-PDF work remains
a separate explicit requirement: the legacy PDF and both current prototypes are
untagged.

## Sources

- [Sphinx LaTeX customization](https://www.sphinx-doc.org/en/master/latex.html)
- [Sphinx LaTeX configuration](https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-latex-output)
- [MyST: create a PDF](https://mystmd.org/guide/creating-pdf-documents)
- [MyST `jtex`: create a LaTeX template](https://mystmd.org/jtex/create-a-latex-template)
- [MyST document parts](https://mystmd.org/guide/document-parts)
