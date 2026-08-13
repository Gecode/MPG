# MPG figure sources

The canonical format for diagrams is SVG. SVG filenames preserve the complete
legacy label and change only `:` to `-`, so `fig:intro:gecode_architecture`
becomes `fig-intro-gecode_architecture.svg`. Matching PDF derivatives are used by
the Sphinx LaTeX builder. Historical Gist screenshots remain PNG because their
source information is raster; converting them to SVG would only add a wrapper.

Run `python3 rst/figures/scripts/generate.py` from the repository root after the
legacy extraction step has produced `.mpg/extract/MPG.tex` and the expanded
chapter files. The checked-in SVGs are the migrated assets. The legacy LaTeX is
used as a one-time vector conversion source, not as a runtime dependency of the
new documentation build.

Use `--force` to reconvert the historical vector sources, or `--pdf-force` to
rebuild all deterministic PDF companions without repeating the PSTricks pass.

The script also rebuilds `rst/manifests/figures.json`,
`rst/manifests/figures.csv`, and `rst/manifests/raster-assets.json`.
