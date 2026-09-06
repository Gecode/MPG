# Modeling and Programming with Gecode

The manual is authored only in reStructuredText. `rst/content/` produces both
the website HTML and the classical PDF. The former TeX book sources and
migration tools have been removed; their history remains in Git. XeLaTeX is
still used to typeset Sphinx's generated PDF input.

## Setup and preview

Use Python 3.11 or newer (CI uses 3.12), Node 22.12 or newer, and uv:

```sh
uv sync --locked
npm ci
npm run dev
```

The development server builds and watches the manual at
<http://127.0.0.1:8000/>. A failed rebuild preserves the last successful output.
Use `npm run dev -- --port 8765` for another port, `npm run build` for HTML,
and `npm run preview` to serve the latest build.

PDF and figure checks also require XeLaTeX, latexmk, Poppler (`pdfinfo`,
`pdftotext`, `pdffonts`), and `rsvg-convert`. The TeX packages installed in
[the documentation workflow](.github/workflows/docs.yml) define the CI setup.

## Maintained files

- `rst/content/`: prose, bibliography, and page ordering.
- `rst/examples/src/`: canonical C++ examples; `fragments/` contains display-only material.
- `rst/examples/int.vis`: the variable implementation specification used by the example build.
- `rst/manifests/code-projections.json`: code selections and their integrity checks.
- `rst/figures/`: canonical SVGs and screenshots, with PDF companions in `pdf/`.
- `rst/extensions/`, `_templates/`, `_static/`: publication behavior and styling.
- `test/` and `notest/`: harnesses used to compile and exercise examples.

See [the authoring guide](rst/README.md) for editing procedures and
[release instructions](rst/RELEASE.md) for publication.

## Checks and releases

```sh
make check-sources
make docs MPG_VERSION=6.4.0
make check GECODE_ROOT=../gecode
make release MPG_VERSION=6.4.0 GECODE_ROOT=../gecode
```

`make check-sources` checks current code selections and figure assets.
`make docs` runs those checks and builds strict HTML and PDF output under
`rst/_build/`. `make check` also runs tooling/platform tests and compiles and
executes the canonical examples against the selected Gecode checkout.
Three interactive Gist examples are compiled but require manual execution.
`make release` runs the checks, builds both formats, and packages them under
`output/`. Packaging refuses to overwrite a version that already exists.

For a final release, build the matching Gecode tag first, generate its API
inventory as described in `rst/RELEASE.md`, and use a fresh output location:

```sh
make release MPG_VERSION=6.4.0 GECODE_ROOT=../gecode \
  RST_BUILD=/tmp/mpg-release-build MPG_OUTPUT=/tmp/mpg-release-output
```

The Gecode checkout must include its test framework sources and compiled
libraries. The `less-test` example also needs a Gecode installation
built with `BUILD_TESTING=ON`; pass it as
`GECODE_PREFIX=/path/to/install`. Validation of the set, float, and
other examples that use internal test support requires `GECODE_ROOT`.
The Makefile automatically selects `../gecode` if its test sources exist.

`make build`, `make build-test`, `make build-notest`, `make test`, and
`uv run -- python -m tools.mpg run --kind all --gecode-root ../gecode`
remain available for focused example work. Generated C++ build trees, binaries,
and reports live in `.mpg/`. `make clean` removes those and the known publication
build outputs. There is no extraction step.

The optional `mpg.toml` configures example selection, compiler flags, timeouts,
and per-example runners. It does not select chapters; book order is authored
in `rst/content/index.rst`.

CI builds and packages an HTML/PDF preview in `docs.yml` and independently
compiles and tests examples in `examples.yml`. A preview artifact is not an
announced release. Release-support assembles the website bundle; Cloudflare
publication is coordinated separately, as described in `rst/RELEASE.md`.
