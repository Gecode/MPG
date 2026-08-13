# Shared hard-page fixture

This format-neutral fixture extends both authoring candidates with material
derived from the real MPG architecture overview, crossword case study, and
nonogram case study.

`fixture.json` is the illustration data. `generate-assets.mjs` deterministically
creates five accessible SVG files:

- a layered replacement for the legacy PSTricks architecture overview;
- the legacy 15 by 15 crossword grid and its filled solution;
- a compact crossword solution tied to an executable model; and
- a combined puzzle/solution rendering of the legacy heart nonogram.

The SVGs carry `<title>`, `<desc>`, a stable `viewBox`, and site-aligned Gecode
colors and font roles. They are generated for each prototype rather than
maintained separately for HTML and PDF.

The two complete C++ programs under `examples/` compile against current Gecode.
Their output is compared byte-for-line with `fixture.json`, so the colored
nonogram cells and miniature crossword solution cannot silently drift from the
models.

Run the shared core independently:

```sh
mkdir -p tmp/assets tmp/bin
node generate-assets.mjs tmp/assets
for example_source in examples/*.cpp; do
  example_name="${example_source##*/}"
  example_name="${example_name%.cpp}"
  c++ -std=c++17 -Wall -Wextra -pedantic -I/opt/homebrew/include \
    "$example_source" -L/opt/homebrew/lib \
    -lgecodesearch -lgecodeminimodel -lgecodeint -lgecodekernel \
    -lgecodesupport -o "tmp/bin/$example_name"
done
node verify.mjs tmp/bin
```

The complete MyST and Sphinx verification commands also generate these assets,
compile both programs, verify exact downloads, and build their web/PDF pages.
