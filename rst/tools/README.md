# MPG reST migration tools

These tools make content loss visible during the TeX-to-reStructuredText
migration. They use only Python's standard library and produce deterministic
JSON (no timestamps or absolute paths).

From the repository root:

```sh
python3 rst/tools/inventory.py --check rst/manifests/legacy-parity.json
python3 -m unittest discover -s rst/tools/tests -v
```

Produce a location-rich report of every construct the conservative converter
will refuse (exit status 2 is expected until dedicated migrations exist):

```sh
python3 rst/tools/audit.py --output /tmp/mpg-conversion-audit.json
```

Regenerate the canonical inventory only after reviewing a deliberate legacy
source change:

```sh
python3 rst/tools/inventory.py --output rst/manifests/legacy-parity.json
```

Audit a TeX file before mechanical conversion. Unsupported constructs cause
exit status 2 and no reST output is written:

```sh
python3 rst/tools/convert.py input.tex output.rst --report report.json
```

Compare a migrated tree with the legacy anchors and citations:

```sh
python3 rst/tools/parity.py \
  --manifest rst/manifests/legacy-parity.json \
  --rst-root rst/content \
  --output rst/manifests/current-parity-report.json
```

The stricter per-source coverage contract also requires an assigned destination
for every source chapter. Stable labels and citations are checked directly.
Items whose semantics cannot be inferred safely—captions, unlabeled tips,
raw tables, and literate projections—must carry an invisible marker next to
their migrated representation:

```rst
.. mpg-covered: literal-projection:docs/src/chapters/modeling/m-started.tex.in:67:send more money
```

Generate or verify the contract with:

```sh
python3 rst/tools/coverage.py --generate \
  --manifest rst/manifests/legacy-parity.json \
  --contract rst/manifests/source-coverage.json
python3 rst/tools/coverage.py \
  --manifest rst/manifests/legacy-parity.json \
  --contract rst/manifests/source-coverage.json \
  --output /tmp/mpg-source-coverage-report.json
```

The parity comparison is intentionally strict. Existing `\label` values are
the public deep-link contract and must remain explicit reST targets. Complex
tables, PSTricks figures, generated title macros, and literate programs require
dedicated migrations; the generic converter refuses them.
