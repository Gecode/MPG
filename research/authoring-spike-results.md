# MyST versus reStructuredText production-spike results

Research date: 2026-08-09

## Outcome

Both candidates passed the common two-page production fixture and the expanded
architecture, crossword, and nonogram fixture. Canonical
reStructuredText/Sphinx is therefore a first-class candidate, not a fallback to
MyST. The expanded evidence gives Sphinx a provisional engineering lead, but the
deepest literate slices from `p-started` still need to select the format.

The classical-PDF analysis strengthens that provisional lead. Both finalists
can load a local LaTeX design package, but Sphinx already exposes the book-level
structure and public LaTeX hooks needed to reproduce the MPG's part and chapter
openers, page furniture, program and tip treatment, lists, bibliography, and
index. MyST first needs to prove a clean chapter/part projection and remove its
current exact-code repair. See
[`classical-pdf-fidelity.md`](classical-pdf-fidelity.md).

The follow-up implementation confirmed the visual result in both backends.
Sphinx produced a 19-page classical two-sided PDF through semantic directives
and public LaTeX hooks. MyST produced a 14-page classical PDF, but required a
70-line fail-closed generated-TeX adapter and still pins part metadata in the
PDF template because its current project tree has no useful part node. Both
complete verification commands pass; both PDFs remain untagged.

MyST has the better authoring experience and the smaller integration boundary.
Sphinx has the stronger demonstrated build semantics. Its semantic builder did
not grow for the hard pages; the JavaScript adapter grew by eight lines. MyST's
adapter remained reasonably small, but the pages exposed additional release
repairs for exact PDF code, code-listing kinds, and stale hashed downloads.

## Hard-page extension

The second fixture is derived from three real legacy locations:

- the PSTricks architecture overview in `core/intro.tex.in`;
- the 15 by 15 PSTricks crossword grid and positioned-letter solution in
  `case-studies/c-crossword.tex.in`; and
- the puzzle and solution LaTeX tables in `case-studies/c-nonogram.tex.in`.

A shared 125-line dependency-free generator now creates five accessible SVGs
from one JSON fixture: architecture, crossword puzzle, full crossword solution,
an executable miniature crossword, and the heart nonogram puzzle/solution. The
assets use the rebuilt site's Gecode colors and font roles. Both outputs consume
the same SVG files; there is no HTML/PDF illustration fork.

Two complete C++ models compile against current Gecode. The verifier requires
their exact output to match the illustration fixture. Displayed excerpts,
downloads, compiled inputs, and generated cells therefore remain traceable.

Both candidates added lists, several large vector figures, three labeled code
projections, a second numbered equation, two downloads, and three new routes.
Both Astro builds report zero diagnostics, and all PDF pages were rendered and
inspected. The modern nonogram is materially clearer than the legacy pair of
tables; the full crossword preserves every legacy block and letter while
remaining responsive and vector-sharp.

The extension separated the candidates more clearly:

- MyST's strict adapter grew from 135 to 153 lines. Its source stayed markedly
  easier to read.
- MyST still reported no external-code dependencies. A clean-output test also
  found stale content-hashed downloads in `_build/site/public`.
- MyST exported all four labeled code blocks as figures and changed the code
  punctuation sentinel `-- ++ ->` to `- - ++ ->` in TeX. The now 17-line
  fail-closed repair reconstructs exact verbatim code from the resolved AST and
  restores Program floats.
- Sphinx's 204-line doctree exporter needed no new node mapping. Its JavaScript
  adapter grew from 56 to 64 lines for generic downloads and page titles.
- Sphinx natively tracked all three external source dependencies; touching each
  hard example reread exactly its owning page. Code punctuation and Program
  kinds survived PDF export without repair.
- Sphinx initially inserted blank recto pages between these short chapters. The
  local template now uses `openany`, reducing the verified PDF to twelve pages.
  Its Font Awesome `ToUnicode` warnings and untagged output remain unresolved.

Final expanded artifacts measure 1.32 MiB web / 118 KiB eleven-page PDF for
MyST and 1.22 MiB web / 167 KiB twelve-page PDF for Sphinx. These sizes are not
decision drivers; the semantic repair surface is.

## Common result

Both spikes:

- resolve labels, cross-page references, numbered equations, SVG figures,
  program listings, tables, admonitions, BibTeX citations, and shared math;
- consume `class:Gecode::Space` from a versioned release inventory and link to
  `/doc/6.4.0/reference/classGecode_1_1Space.html` without building the Gecode
  reference documentation;
- export resolved semantic data into Astro-owned layouts and CSS rather than
  importing generated document-site HTML;
- compile and execute the same canonical Gecode DFS example, obtain
  `9 5 6 7 1 0 8 2`, and prove that compiled, displayed, and downloaded source
  originate in the same file;
- fail on an unsupported output node and exercise negative reference tests;
- build without mutable template or theme downloads after dependency install;
  and
- produce visually inspected A4 PDFs with no clipping or overlap. Both PDFs
  are currently untagged.

The fixture and release boundary are specified in
`prototypes/authoring-comparison.md`. The release job produces the reference
HTML tree and symbol inventory. MPG consumes that inventory and publishes its
own semantic bundle and PDF. The Astro site imports those already-built release
artifacts; its ordinary build does not run Doxygen, Sphinx, MyST, CMake, or TeX.

## Measured comparison

| Property | MyST engine to Astro | canonical reST/Sphinx to Astro |
|---|---:|---:|
| Document engine | MyST 1.10.1 | Sphinx 8.2.3 |
| Owned semantic adapter | 153 lines | 204 Python + 64 JavaScript = 268 lines |
| Additional API role | 22 lines | included in Python extension |
| Required source-reference preflight | 35 lines | native Sphinx diagnostics |
| Required exact-code/PDF semantic repair | 17 lines | none for code bytes/numbering/kinds |
| External-code dependency | explicit generated manifest | native incremental dependency |
| Installed main environment | 224 MiB npm | 72 MiB Python + 210 MiB npm |
| Semantic output | 266 KiB | 49,283 bytes |
| Astro output | 1.32 MiB | 1.22 MiB |
| PDF | 118 KiB / 11 A4 pages | 167 KiB / 12 A4 pages |
| Latest complete clean verification | 28.8 s | 43.7 s before `openany` PDF rebuild |
| Runtime boundary | JavaScript | Python to JSON to JavaScript |

The timings vary with concurrent TeX/SVG work and are useful only for detecting
gross cost, not declaring a speed winner.

## MyST result

The source is compact and close to ordinary Markdown. The implementation stays
inside the JavaScript ecosystem, and the strict semantic renderer is smaller.
The hardened spike fixed the earlier remote-template, bibliography, float, and
Program-numbering failures and now produces matching Program 1 and Table 1 in
web and PDF.

Four local controls remain mandatory:

1. MyST emitted an empty dependency array for `literalinclude`, so the adapter
   must generate an explicit page-to-source dependency manifest.
2. `--strict` accepted a duplicate-label warning during testing, so a checked
   duplicate/unresolved-reference preflight remains necessary.
3. MyST emitted labeled code listings as LaTeX figures and altered `--` inside
   verbatim code. A 17-line, fail-closed repair restores exact AST code and the
   Program kind; this should be fixed upstream or replaced by a supported
   transform.
4. A clean release must clear MyST's generated site tree or stale
   content-hashed downloads survive into later output.

See `prototypes/myst-astro/README.md` for the exact command and artifacts.

## reStructuredText/Sphinx result

Sphinx's custom builder receives resolved Docutils doctrees and exports a
strict semantic JSON artifact. Native `literalinclude` dependency tracking was
tested without a full-rebuild shortcut: touching only the canonical C++ file
caused exactly one source page to be reread. Sphinx also produced consistent
section, equation, figure, program, and table identities across the web bundle
and PDF without a post-export numbering repair.

Its costs are visible rather than hypothetical:

1. reST source is denser, especially for targets, directives, tables, and
   nested options.
2. The integration crosses Python and JavaScript and owns a 268-line strict
   bridge for this small fixture.
3. The XeTeX path invokes local Inkscape for SVG conversion.
4. The default PDF is untagged and emits a Font Awesome `ToUnicode` warning for
   the tip icon.

See `prototypes/rst-sphinx-astro/README.md` for the exact command and artifacts.

## Decision gate

Convert the same `m-started` slice and the same deep `p-started` literate-code
slice in both formats. Select a winner using recorded evidence for:

- author review of readability and editing friction;
- growth in supported AST/doctree nodes and adapter code;
- preservation of all legacy labels, references, code projections, and files;
- API-inventory coverage and failure behavior;
- incremental rebuild correctness;
- PDF template work, warnings, accessibility facts, and visual quality; and
- clean, offline, pinned release production.

Choose MyST only if the deep literate pilot shows that its clearer source
outweighs the now demonstrated dependency, clean-output, and PDF-fidelity
machinery. Choose reST/Sphinx if its node coverage remains stable through nested
projections and custom programming figures. Retain
Quarto/Pandoc only as the document-first fallback if neither semantic adapter
remains maintainable. Do not begin bulk conversion before this gate.
