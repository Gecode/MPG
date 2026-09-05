# Authoring MPG

`content/` is the sole book source for HTML and PDF. Edit it directly. The old
TeX sources, conversion scripts, and frozen migration inventories have been
removed. The PDF's LaTeX styles remain publication tooling, not a second book.

## Prose and structure

Run `npm run dev` from the repository root for a watched HTML preview.
Every public section needs an explicit label immediately before its heading.
Use `:ref:` for named sections, and `:numref:` for numbered programs, figures,
tables, equations, and tips. Keep existing labels when revising a heading;
check public fragments if a title changes.

Use `mpg-paragraph` for a run-in heading, `mpg-tip` for a numbered tip, and
`mpg-figure` for a figure containing tables or several images. Use `:api:` for
Gecode reference links; its target must appear in the release inventory.
Use `:reference:` only for a known Doxygen page absent from the tag inventory.
Never paste a release number into an API URL. Citations belong in
`content/references.bib`.

To add a chapter, create its labeled RST file, add it to the numbered toctree
in `content/index.rst`, and add it to its part page and `mpg_navigation` in
`conf.py`. Part pages are unnumbered HTML entry points. The first chapter of a
part includes its shared PDF opening using `only:: latex` and `mpg-part`.
Build the full book to verify numbering and cross-chapter references.

## Examples and code excerpts

Executable C++ lives in `examples/src/`; illustrative snippets live in
`examples/fragments/`. Published `mpg-code` directives select excerpts from
`manifests/code-projections.json`. Avoid pasting a second executable copy into
RST. Existing listings can show a skeleton with child-fragment placeholders
while downloading the complete program.

For an existing example:

1. Edit the canonical C++ file.
2. Run `uv run --locked -- python rst/scripts/author_code.py refresh` from the repository root.
3. Inspect the code and manifest diff, then the affected HTML listings.
4. Run `make check GECODE_ROOT=../gecode`, and inspect the PDF if layout changed.
5. Commit the example and manifest together.

Refresh relocates excerpts against the committed source and manifest (`HEAD`
by default); `--base <ref>` selects another committed baseline. Repeated refreshes
before committing use that same baseline. Boundary insertions stay outside an
excerpt, while whole-file excerpts grow with the file. The helper rejects a
deleted excerpt or an edit crossing an excerpt boundary instead of guessing.
For a deliberate selection change, edit that projection's inclusive
`start_line`/`end_line` and any source segments, then run `refresh --no-relocate`
to keep those authored ranges and update their hashes. That option also works
without Git when the ranges have been reviewed explicitly.

To register a new whole-file example or a small excerpt:

```sh
uv run --locked -- python rst/scripts/author_code.py add 'my example' \
  rst/examples/src/my-example.cpp --validation compiled
uv run --locked -- python rst/scripts/author_code.py add 'my excerpt' \
  rst/examples/fragments/my-excerpt.cpp --lines 2:12
```

Use `--title 'Explanation'` for an unnumbered listing title. Then reference it:

```rst
.. mpg-code:: my example
   :caption: A complete example
   :name: program:my-example
   :download:
```

A new compiled example also needs a runner: add it to the applicable example
list in `tools/mpg/config.py` (or a local `mpg.toml` override), provide a harness
if needed, and define a meaningful output expectation in
`rst/scripts/verify_examples.py`. `--validation compiled` alone does not create
a test. Use `display-only` only for material that is intentionally not executable.

There are no fixed limits on the number or order of code listings, figures,
or tips. `author_code.py check` checks the current source selections and RST keys.

## Figures and checks

Edit SVG figures and regenerate their PDF companions as described in
[figures/README.md](figures/README.md). No extraction or legacy figure inventory
is required. Commit both media together and supply useful alternative text.

`make check-sources` checks code integrity and current figure companions.
`make check` adds tooling/platform tests and compiled example validation.
`make docs` builds strict HTML and PDF; `make release` runs the checks and
packages both. See [RELEASE.md](RELEASE.md) for exact release inputs.

For visual review, inspect the affected pages plus a dense code chapter,
a figure/table page, and a narrow viewport. In the PDF check object numbering,
clipping, hyperlinks, and nearby page breaks. A successful build does not
replace those visual checks.
