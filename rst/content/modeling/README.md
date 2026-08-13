# Modeling migration coverage

This directory is the canonical reStructuredText migration of the complete
legacy modeling part in `docs/src/chapters/modeling/`. `../core/intro.rst`
contains the migrated introduction.

The migration retains all 259 labels occurring in the introduction and
modeling sources. It also retains all 55 tips and all 47 distinct citation
keys. Legacy paragraph headings are represented by `rubric` directives;
chapters, sections, subsections, and subsubsections remain structural reST
headings. Figures and Programs retain their legacy targets for stable links.

All 456 modeling display sites use the semantic `mpg-code` directive and
resolve through `../../manifests/code-projections.json`: 399 direct code or
command displays and 57 literate insertions, including 12 small displays. The
older 353-site transitional map in `../../manifests/code-modeling-sites.json`
is retained only as a migration oracle; the authoritative display sequence is
the expanded canonical manifest. That manifest checks every artifact and
source slice by byte count and SHA-256 before Sphinx reads a chapter; compiled
examples and illustrative fragments remain distinguished by their
`validation` field.

Verify the canonical extraction and source maps with:

```sh
python rst/scripts/migrate_code.py --check
python rst/scripts/verify_code_sites.py
```

Validation also uses isolated, real Sphinx builds for both directories:

```sh
research/prototypes/rst-sphinx-astro/.venv/bin/sphinx-build \
  -E -b dummy -c /tmp/mpg-pandoc --keep-going \
  rst/content/modeling /tmp/mpg-pandoc/build-modeling
```

The migrated sources produce no docutils syntax errors or unresolved local
references. Strict isolated builds suppress only references to other MPG
parts, citations supplied by the assembled book, and publication assets
outside these content directories.

All 76 legacy captions are represented: 38 arbitrary-content semantic
figures, 19 image figures, and 19 captioned code figures. `mpg-figure` keeps
the live tables and command output accessible in HTML while emitting numbered,
floating Figure environments in LaTeX. This includes the four-subtable value
selection figure that the initial Pandoc conversion had omitted.

The authoritative source-coverage contract reports no missing items for the
introduction or modeling destinations. Coverage markers identify captions,
tables, unlabeled tips, and legacy literate insertion occurrences; they
supplement rather than replace the checked projection artifacts.

## Whole-book integration

- PSTricks has not been copied into reST. Visual figures use the agreed
  `/figures/<legacy-label-with-colons-replaced>.svg` release paths. The two
  circuit figures also preserve their historical before/after subfigure
  anchors.
- References to other MPG parts intentionally keep their original labels and
  resolve when the complete book is assembled.
- Mathematics uses Sphinx's normal math roles and directives. There are no raw
  LaTeX directives or PSTricks commands in these authored files.
