# Figure authoring

Edit diagrams as SVGs directly in this directory. Each SVG needs a useful
`title` and `desc`; authored reST images also need meaningful `:alt:` text.
Keep screenshots as PNG where the information is inherently raster.

After editing or adding an SVG, render its PDF companion:

```sh
uv run --locked -- python rst/figures/scripts/generate.py rst/figures/my-figure.svg
uv run --locked -- python rst/figures/scripts/verify.py
```

With no paths, `generate.py` processes all maintained SVGs. `--check` compares
renderer output without changing companions; use it with the same local renderer
version that created the PDFs. The portable release gate checks SVG accessibility
text, image references, and PDF presence/page structure, because Cairo and font
versions can produce different PDF bytes on different platforms. The scripts use `rsvg-convert`
with a fixed timestamp; no TeX sources, historical inventory, or extraction
workspace are needed. Commit the SVG and its `pdf/<name>.pdf` together.

Reference `/figures/<name>.svg` in the chapter; Sphinx selects the matching PDF
for the printed edition. Give each image figure an intentional width class:
`mpg-figure-narrow`, `mpg-figure-compact`, `mpg-figure-medium`,
`mpg-figure-wide`, or `mpg-figure-full`.

The optional `scripts/generate_recomputation_windows.py` redraws the two
recomputation window diagrams from its small node-state tables. Other SVGs
are edited directly. Verify changes in both HTML and PDF, particularly
labels, clipping, and the relationship between diagrams and their captions.
