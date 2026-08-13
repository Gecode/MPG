# MPG figure migration

## Result

The legacy source contains 213 `figure` environments and 217 distinct figure
labels. All are represented in `figures.json` and `figures.csv`; figures with
multiple historical subfigure labels retain every label in the `labels` field.

The migration deliberately does not turn every LaTeX figure float into an
image. The inventory classifies them as follows:

| Class | Count | New representation |
|---|---:|---|
| Executable code | 119 | Literate RST code/program directive |
| Semantic tables | 51 | Native RST tables, not screenshots |
| Legacy vector conversion | 24 | Canonical outlined SVG plus PDF |
| Historical screenshots | 11 | Original PNG embedded in a self-contained SVG plus PDF |
| Literal output or code | 5 | Native literal/code block |
| Data-authored diagrams | 2 | Generated SVG/PDF from the exact nonogram clues and cells |
| Semantic redraw | 1 | Authored SVG/PDF architecture overview |

There are therefore 38 shared SVG/PDF figure pairs. The cover logo is an
additional outlined SVG/PDF pair migrated from EPS. All 18 historical Gist PNG
assets and their EPS counterparts are recorded in `raster-assets.json`,
including the captures that are currently not referenced.

## Authoring decisions

- SVG is the checked-in source for diagrams and the HTML asset.
- PDF is a deterministic derivative for Sphinx/LaTeX. `rsvg-convert` runs with
  a fixed `SOURCE_DATE_EPOCH`; the verifier performs a byte-for-byte rebuild
  check.
- The 24 mechanically converted PSTricks figures retain the original MPG line,
  shape, color, and typographic language. Text is outlined, avoiding font
  substitution in browsers and PDF release builders.
- The architecture overview is a maintainable semantic SVG generated from
  explicit elements in `generate.py`. It removes stale document-part numbers
  while preserving the original rectangular layered composition and MPG
  colors.
- The nonogram puzzle and solution are regenerated from the exact 9 by 9 clue
  and solution data. They use a restrained white, Charter, and Gecode-green
  treatment rather than the unrelated heart prototype.
- Gist images remain raster. Their SVG wrappers only supply a stable figure
  URL, self-contained embedding, multi-image layout where needed, and
  accessibility metadata; they do not pretend to add resolution.
- Data tables, API summaries, code listings, and program outputs remain native
  document structures so they are selectable, searchable, accessible, and
  usable at narrow HTML widths.

Every SVG has a `title` and `desc`; captions, labels, alt text, legacy source
locations, and HTML/PDF asset paths are kept together in the JSON manifest.

## Naming and use

The stable filename is the complete legacy label with only colons replaced by
hyphens. For example:

```
fig:intro:gecode_architecture -> /figures/fig-intro-gecode_architecture.svg
```

RST should keep the original label immediately before its figure or table. The
SVG path above is used for HTML; Sphinx selects the same-basename PDF for LaTeX.

## Rebuild and verification

From the repository root, after the normal MPG extraction step:

```
python3 rst/figures/scripts/generate.py
python3 rst/figures/scripts/verify.py
```

`verify.py` checks the legacy counts, unique labels, SVG XML and accessibility
metadata, one-page PDF companions, reproducible dates and bytes, raster/EPS
inventory, and every figure/image reference currently present in the RST tree.

The complete PDF set was rendered to PNG and reviewed as a contact sheet. The
final architecture overview and both nonogram pages were also inspected at
full resolution.
