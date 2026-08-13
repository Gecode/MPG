# Current MPG authoring and pipeline audit

Audit date: 2026-08-09

Repository revision: `19c1eaf` (`main`)

Scope: the maintained sources, extraction and PDF paths, generated programs,
validation harness, legacy utilities, and CI. This is a forensic description,
not a recommendation of a particular authoring syntax.

## Executive finding

MPG is a 580-page program that happens to render as a book. Its maintained
chapter files combine at least four different things:

1. prose, mathematics, references, tables, tips, and figures;
2. a nested code-region graph used to present programs incrementally;
3. the canonical bytes of downloadable C++ and header files; and
4. metadata that is interpreted by unrelated scripts to organize downloads,
   link into the Gecode API, and validate selected outputs.

A migration that treats the input as ordinary LaTeX or converts only its
visible PDF will silently lose executable content. Conversely, preserving the
old TeX token stream as the new canonical representation would carry its most
fragile coupling into the web build. The safe boundary is a format-neutral
content model plus an explicit code-artifact/projection model. Web pages and
PDF should be renderers of that model; compilation and execution should consume
the same declared artifacts.

The current pipeline is healthier than its age suggests: extraction, the full
PDF, and all 76 configured programs built successfully against the sibling
Gecode 6.4.0 checkout during this audit. However, the apparent behavioral test
coverage is overstated. All 30 Gecode test-harness programs are invoked with
`-help`, which exits successfully before running a test. Three Gist programs
are also deliberately compile-only. Two extracted C++ files and one hand-made
test wrapper are outside the configured manifest. These gaps should be fixed or
made explicit before using the old pipeline as a migration oracle.

## Baseline and inventory

### Maintained source set

| Material | Observed size | Notes |
|---|---:|---|
| Chapter sources | 38 files, 46,643 lines, 2.08 MB | 37 ordinary inputs plus `changelog`; `v.tex.in` contains seven actual chapters |
| Template | 495 lines | Part/chapter order, front matter, bibliography, license |
| Shared TeX macros | 388 lines | Layout, code display, tips, math notation, and a substantial PSTricks figure vocabulary |
| Bibliography | 1,108 lines | 102 bibliographic records plus 11 `@String` declarations; 6 generated MPG part records |
| Notes | 1,790 lines | `docs/src/notes/MPG.txt`; not consumed by the build |
| Embedded literate programs | 85 `litcode` units | 79 emit files: 78 `.cpp` and one `.hh`; six are display-only |
| Generated code | 79 files, 22,005 C++ lines plus `int.hh` | 78 C++ files; about 1.12 MB |
| Hand-written wrappers | 31 under `test/`, 21 under `notest/` | One `test/size-min.cpp` wrapper is unconfigured |
| Raster/vector image library | 37 files, about 16 MB | 18 PNG/EPS pairs plus EPS-only logo |
| Inline diagrams | 26 `pspicture` environments | Additional figures are built with macros defined in `macros.tex` |
| Miscellaneous material | 675 files, about 15 MB | Crossword inputs/results/scripts and picture generators |
| Current PDF | 580 A4 pages, 3.83 MB | PDF 1.4, untagged, generated through DVI/PostScript |

The chapter size distribution is very uneven. `c-crossword.tex.in` alone is
14,745 lines because it contains two programs with embedded word lists; the
two extracted C++ files are 7,035 and 7,029 lines. The next largest source is
`v.tex.in` at 3,808 lines. Conversion tooling must stream or parse complete
files and should not assume a “normal article” scale.

The template defines six deliberately lettered parts by manipulating the
numeric LaTeX part counter (`M`, `C`, `P`, `B`, `V`, and `S`). It includes 37
ordinary chapter source names, then includes `changelog` and `license`
separately. Chapter discovery in `tools/mpg/config.py` is derived from those
template `\include` commands, not from directories or page metadata.

### Observed structural constructs

Counts below are direct source counts and therefore describe migration load,
not rendered-object counts.

| Construct | Count | Required semantic treatment |
|---|---:|---|
| Named labels | 560, all unique | Stable IDs for chapters, sections, figures, tips, and paragraphs |
| `autoref` references | about 1,137 | Typed, automatically titled internal links |
| Gecode API references | 613 uses of `\gecoderef` | Versioned external API symbol/group/example links |
| Inline C++ spans | about 5,348 `\?...\?` spans | Code semantics and syntax styling, including in headings/prose |
| Nested literate blocks | 625 | Named region tree, with a maximum observed depth of five |
| Literate insertions | 353 normal, 14 small, 1 direct | Region projections, labels, downloads, and a label-free projection |
| Raw display-only code | 398 normal, 14 small | Code examples that are not extracted |
| Command/output blocks | 43 normal, 1 small | Terminal commands and program output, distinct from C++ artifacts |
| Figures | 213 | Many contain tables, diagrams, or code rather than image files |
| Tables (`tabular`) | 79 | Complex spans and rules occur; five tables include generated result files |
| Tips | 78 | Numbered callouts also populate a dedicated “Tips” list |
| Citations | 106 calls, 71 unique keys | BibTeX-backed citations and bibliography |
| `CAT` annotations | 63 | Gecode/global-constraint-catalog mappings and generated external links |
| Acknowledgment names | 35 | Parsed out of changelog syntax into front matter |

Mathematics ranges from inline expressions to arrays, four `eqnarray*`
environments, and one `align*` environment. Much mathematical vocabulary is
hidden behind custom macros (`range`, `seq`, nonterminals, reification arrows,
domain operators, and so on), so counting explicit math environments
understates its importance.

Figures are also not reducible to the 18 screenshot pairs. The source contains
search trees, propagator diagrams, boards, grids, and dependency illustrations
implemented in PSTricks and a large set of bespoke commands such as
`DefineNode`, `DefineLink`, `knboard`, and Kakuro/crossword/bin-packing macros.
The 26 explicit `pspicture` environments are therefore a lower bound on
diagram complexity. All 18 screenshots have both `.png` and `.eps` forms; the
current DVI pipeline selects EPS, while a web build naturally needs PNG or a
new SVG equivalent.

## The real extraction path

The primary CLI is Python, but the primary document parser is still Perl.
`python -m tools.mpg extract` currently performs this sequence:

1. Resolve configuration and discover 37 chapter names from the template.
2. Create a PID-specific temporary work directory under `.mpg/extract/`.
3. Symlink/copy `bin/` and copy shared static TeX into the temporary directory.
4. Run `bin/gl.perl YEAR` independently over every `.tex.in` chapter. The
   script emits rendered TeX on stdout and writes tangled code beside it.
5. Process `changelog` separately and run `gen-ack.perl` over its source.
6. Run `gen-titles.perl` over chapter sources, then pass its output through
   `gl.perl`.
7. Substitute version/year in the template; expand only its top-level
   `\include` and `\input` statements with `include.perl`; shorten all labels
   with `shorten.perl`; and run the resulting monolithic document through
   `gl.perl` once more.
8. Copy TeX, `.cpp`, `.hh`, and `.vis` outputs to `.mpg/generated/` and write a
   JSON summary and example manifest.

The second `gl.perl` pass is mostly a transformation of the assembled document
(inline code, raw code blocks, API references, and catalog annotations).
Literate program definitions have already been removed by the per-chapter
passes. Includes inside a chapter, such as the five crossword result tables,
are not recursively expanded by `include.perl`; LaTeX reads them later.

### Literate-programming semantics that must be preserved

`gl.perl` implements a small, implicit projection language:

- `\begin{litcode}{logical name}{authors}` starts a downloadable artifact.
  Spaces in the logical name become hyphens; `.cpp` is appended unless the
  name already contains a dot. Author aliases generate a license header whose
  ending year is the configured build year.
- `\begin{litcode}[texonly]{name}` starts an illustrative program that has
  projections but no downloadable file. Six such units exist.
- `litblock` regions nest. Their effective identity is
  `artifact-name:block-name`; block names can themselves contain colon-delimited
  hierarchy. The deepest observed structural nesting is five.
- Ordinary named child blocks are present in the full tangled file. A marker
  comment derived from the block name is inserted into that file. In a parent
  display, the child is replaced by a hyperlink to its own projection.
- An `anonymous` child is present in the tangled file but is replaced by an
  ellipsis in its parent projection. This is common: 335 of 625 blocks are
  anonymous.
- An `ignore` child is present in the tangled file but omitted entirely from
  its parent projection. Five explicit ignore blocks exist. Standalone C-style
  multiline comments whose delimiters occupy their own lines are treated as
  implicit ignore blocks as well.
- A nested `texonly` block has the inverse behavior: it remains in displayed
  code but is excluded from the tangled artifact. Two occur.
- `insertlitcode`, `insertsmalllitcode`, and the single `[direct]` insertion
  choose projections. Normal/small variants create hyperlink targets and, for
  whole files, download links; `direct` suppresses the label.
- Inline `\?...\?` spans and raw `code`/`smallcode` environments go through a
  hand-written C++ lexer/highlighter. `cmd`/`smallcmd` use a distinct visual
  treatment.
- Missing block insertions are fatal in Perl. Block identity and indentation
  are presentation semantics: indentation at `\end{litblock}` controls where
  the generated region reference is placed.

This is neither conventional noweb-style tangling nor ordinary fenced code.
The canonical artifact is the concatenation of most source lines, while the
named block graph defines multiple abbreviated views of it. A converter must
model those two products separately.

### The parallel Python implementation is not the production parser

`tools/mpg/literate.py` and much of `tools/mpg/preprocess.py` are only exercised
by small golden unit tests. No production CLI command calls `process_many`,
`process_literate_file`, or `render_mpg_tex`. The CLI directly invokes Perl for
chapter parsing, title generation, include expansion, and label shortening.

The Python literate implementation is not behaviorally equivalent to Perl. It
emits a different file header, lacks the raw code/command transforms and Perl's
syntax styling, does not perform Gecode/CAT link replacement, and tolerates
some unresolved insertions that Perl rejects. It should not be promoted to a
migration oracle without differential tests over all 38 chapter files.

### Generated-artifact gaps

Extraction currently emits 78 C++ files and `int.hh`. The configured validation
manifest contains 76 C++ artifacts:

- 25 standalone models;
- 30 generated propagator fragments combined with hand-written `test/*.cpp`
  wrappers; and
- 21 examples historically called `notest`, which are in fact built and run as
  standalone programs.

`Boolean-domain-expression.cpp` and `putting-everything-together.cpp` are
extracted but absent from the manifest. `test/size-min.cpp` is present but
unused. The `.vis` source assets referenced as downloads in the variable
implementation part are under `docs/src/assets`, but extraction never copies
that directory into its temporary work area; consequently no `.vis` artifact
appears in `.mpg/generated/src`.

The destination directories are not cleared before copying. A renamed or
deleted output can therefore survive as a stale file and enter a later source
archive. There is no source map from a compiler error in a generated C++ file
back to the chapter and literate block that produced it.

## Build, validation, and release behavior

### Example compilation

`tools/mpg/examples.py` writes a generated CMake project for each requested
kind. It finds Gecode headers/libraries from an explicit source tree, prefix,
common system prefix, or sibling checkout. Generated fragments and wrappers
are concatenated into one translation unit. All examples use a broad fixed
library set; Gist is detected by source-text regex and library availability.
Test fragments also compile Gecode's `test.cpp`, `int.cpp`, `float.cpp`, and
`set.cpp` as object sources, which means full test validation requires a Gecode
source checkout rather than only an installed SDK.

Run arguments are partly inferred from source text. Tests always receive
`-help`; driver-based examples receive `-help` when selected constructor text
is detected. This avoids expensive or interactive executions, but it also
means:

- the 30 propagator tests compile and link but execute no assertions, because
  Gecode's test runner exits successfully on `-help`;
- several model examples validate option parsing rather than model behavior;
- three Gist examples compile but are always marked skipped at run time; and
- success generally means exit code zero, with no expected-output or semantic
  assertions.

The extraction manifest initially records `requires_gist: false` for every
program. The build step reparses prepared source, mutates this field, and
rewrites the kind-specific and legacy manifests. Thus an extraction-only
manifest is not a complete artifact description.

### PDF production

`make docs` invokes extraction followed by:

1. `latex` to DVI;
2. `bibtex`;
3. a bookmark rewrite (`fixout`) for selected unnumbered sections;
4. additional `latex` passes until the limited rerun check settles;
5. `dvips`; and
6. `ps2pdf -dALLOWPSTRANSPARENCY`.

This path is required by PSTricks and EPS. It successfully rebuilt the full
580-page PDF during the audit, but it produces an untagged PDF 1.4 document and
depends on a large TeX/PSTricks/font/Ghostscript installation. The final label
shortening pass rewrites descriptive source IDs to sequential `l:N` IDs to
work around historical PDF hyperlink issues. A migration must preserve the
logical IDs before this lossy rewrite, not recover IDs from the PDF.

`gl.db` is a checked-in snapshot derived by `gendocref.perl` from a Gecode
Doxygen tag file. It maps API kinds/symbols to relative reference-documentation
URLs and titles. There is no CI step that regenerates or validates the map
against the chosen Gecode ref. The 63 `CAT` annotations also expand to links for
the historical Global Constraint Catalog host. These are semantic cross-links,
but their URL data is stale infrastructure and should be refreshed separately
from content conversion.

### Distribution and CI

`docs.yml` builds and uploads only `MPG.pdf`. `examples.yml` builds Gecode
`main` (or a manually selected ref), runs the 11 Python unit tests, runs all
configured examples, then builds the PDF. The scheduled weekly build is useful
API drift detection, but its test-execution caveat above applies.

The `dist` command archives the entire generated source directory as
`dist/MPG.tar.gz`, then creates `MPG.zip` containing that tarball and the PDF.
It does not generate the `MPG.7z` advertised in the introduction. The older
`gen-files.perl` can place downloads in a part/chapter/section hierarchy based
on `%% FILES: PARTONLY/CHAPTERONLY`, but the Python CLI never calls it. Other
unused legacy utilities generate Global Constraint Catalog data and a solver
questionnaire. These scripts encode historical release products and should be
classified explicitly as retained, replaced, or retired.

## Verification performed

The following checks were run from a clean tracked worktree (generated `.mpg`
state is ignored):

| Check | Result |
|---|---|
| `uv run -- python -m unittest discover -s tests -p 'test_*.py'` | 11/11 passed |
| `uv run -- python -m tools.mpg extract` | 37 ordinary chapters; 78 C++ outputs |
| `make docs` | passed; 580-page PDF produced |
| `make test` against `/Users/zayenz/gecode/gecode` | 76/76 built; 73 pass statuses, 3 deliberate Gist skips, 0 failures |

The full build emitted many warnings caused by combining `-ffast-math` with
Gecode floating-point interval code (`infinity` under disabled NaN/infinity
semantics). That is a validation-profile concern, not a document conversion
failure, but a future manifest should make compile flags profile-specific.

## Migration hazards and preservation requirements

### Must-preserve contracts

1. Stable document hierarchy, human-readable IDs, typed cross-references, and
   old public URL aliases where they exist.
2. Inline and display mathematics, including the semantics hidden in custom
   notation macros.
3. Numbered captions, figures, tips, tables, citations, bibliography, and
   acknowledgement generation.
4. The complete region/projection behavior of all 85 literate units, including
   the three special nested block modes and display-only programs.
5. Exact downloadable artifacts (modulo a deliberate license-header policy),
   their authorship/license metadata, and download links from code displays.
6. Ordered composition of generated fragments with Gecode test wrappers.
7. Explicit compile/run capability requirements: Gist, Gecode test sources,
   link components, flags, arguments, timeouts, and expected validation mode.
8. Versioned Gecode reference links, catalog annotations, and the six MPG part
   bibliography records.
9. Screenshot pairs, source diagrams, and generated result tables, with an
   auditable decision for each asset rather than a screenshot-only fallback.
10. Both web and PDF output from one semantic source, with deterministic
    manifests and no stale artifacts.

### Highest-risk conversion mistakes

- Converting visible code blocks from the PDF loses lines hidden behind
  anonymous/ignore folds and therefore produces incomplete programs.
- Treating every visible `texonly` line as executable introduces deliberately
  invalid or illustrative code into downloads.
- Replacing custom macros textually can corrupt nested arguments, headings,
  math, or symbol links; regex conversion alone is insufficient.
- Using final shortened PDF labels discards stable logical anchors.
- Rendering PSTricks to one large image preserves appearance but destroys
  responsive layout, accessibility, text selection, and theme integration.
- Inferring validation from directories perpetuates the misleading `notest`
  name and misses unmanifested artifacts.
- Keeping artifact identity derived from display names makes renaming prose a
  breaking download/URL change.
- Continuing annual license-header generation makes builds change merely
  because the configured year changes.
- Validating only “compiled and exited zero” preserves the present false sense
  that propagator tests ran.
- Running old and new extraction implementations without a single conformance
  suite allows silent semantic drift.

## Proposed format-neutral canonical model

The canonical model should be defined independently of Markdown, MDX,
AsciiDoc, MyST, or any PDF engine. Those are serialization or rendering
choices. A minimal useful model has the following entities.

### `Publication`

- stable publication ID, title, description, authors, license;
- Gecode version/ref and release channel;
- ordered `Part`/`Chapter` navigation tree;
- bibliography sources and citation style;
- output base paths and compatibility aliases; and
- declared web/PDF/download bundles.

### `Page`

- stable ID and slug independent of filename/title;
- title, short title, authors, part, order, and previous public URLs;
- ordered semantic blocks: prose, heading, math, list, table, figure, callout,
  citation, API reference, code projection, terminal session, and raw escape;
- named anchors with typed targets; and
- page-level assets and validation dependencies.

Only a small, quarantined raw escape should exist, with a declared target such
as `web`, `pdf`, or `legacy-pdf`. It must not be the default representation for
ordinary content.

### `CodeArtifact`

- immutable stable ID plus output path and language;
- authorship/license metadata separate from generated bytes;
- one or more ordered canonical sources or fragments;
- a tree of stable `CodeRegion` IDs with exact source spans;
- a generation recipe and generated-file source map;
- capabilities and dependencies (`gist`, test framework, Gecode components);
- one or more validation profiles; and
- download/public URL aliases.

For ordinary complete examples, the canonical source should preferably be an
actual compilable C++ sidecar with inert named-region markers. This gives
editors, clang-format, clangd, and compilers the real file directly and makes
tangling unnecessary. Fragment examples and genuinely shared compositions can
use an explicit artifact DAG, but the generated result must remain inspectable
and source-mapped.

### `CodeRegion` and `CodeProjection`

A region records `id`, `parent`, source span, display title, and default fold
policy. A projection is a page-owned view that names an artifact/region and
declares how descendants appear:

- `expanded`: show descendant bytes;
- `linked`: replace with a link to another projection (ordinary named child);
- `ellipsis`: replace with an ellipsis (legacy `anonymous`);
- `hidden`: omit from this projection (legacy `ignore`); and
- `display-only`: include in a projection but exclude from artifact generation
  (legacy nested `texonly`).

Whole illustrative snippets use `artifact: none` rather than pretending to be
downloadable. Projection size/style (`normal`, `compact`, `direct`) is renderer
metadata, not code identity. Every generated line maps back to an artifact
source and region; every code display can link to the complete file and to the
relevant source repository location.

### `ValidationProfile`

- profile ID and applicable Gecode refs/platforms;
- ordered sources and generated-artifact dependency;
- compile standard, definitions, warnings, optimization/sanitizer flags;
- linked Gecode components and required optional features;
- execution mode: `compile-only`, `run`, `test-harness`, `interactive`, or
  `expected-failure`;
- arguments, environment, timeout/resource limits;
- expected exit status plus output matcher/snapshot or registered test count;
- skip reason expressed as a capability predicate, not imperative CI logic.

This makes the current distinctions honest: Gist examples can be declared
`compile-only` in headless CI, while propagator examples can run the harness
without `-help` and assert that their registered test executed.

### `FigureAsset`

- stable ID, caption, alt text/long description, credit/license;
- one canonical source (SVG, diagram source, data + generator, or original
  raster) and deterministic derivatives for web/PDF;
- intrinsic dimensions and responsive intent;
- source dependency and generation command for computed tables/plots; and
- optional light/dark variants.

The existing PNG/EPS pairs should become derivatives of one declared asset.
PSTricks diagrams should be inventoried individually: semantic diagrams are
best redrawn/generated as SVG plus PDF-compatible vector output; archival or
exceptionally costly diagrams can temporarily use deterministic rendered
derivatives with accessible descriptions.

## Canonical invariants and migration oracle

Before changing authoring format, capture a machine-readable baseline with:

- every page/section/figure/tip label and resolved target;
- every citation key and API/catalog reference;
- every artifact path, SHA-256, region ID/tree, and projection text;
- every asset and all page usages;
- the explicit set of 79 emitted source artifacts and 52 wrappers;
- a complete validation manifest, including the three Gist compile-only cases
  and the presently unmanifested files; and
- normalized PDF facts (page count, bookmarks, links, and selected visual
  snapshots) rather than a byte-for-byte PDF expectation.

A converter is acceptable only when it can parse all sources without fallback,
produce the same artifact bytes or approved semantic equivalents, resolve all
internal and API links, compile every declared artifact, execute the profiles
that claim behavioral coverage, and render both web and PDF from a clean output
directory. The old PDF remains a visual reference during migration, but the
old Perl extraction semantics—not the PDF's visible text—are the executable
oracle.
