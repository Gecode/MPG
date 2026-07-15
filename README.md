# Modeling and Programming with Gecode (MPG)

This repository contains the LaTeX source and generated code examples for **Modeling and Programming with Gecode**. This checkout targets Gecode 6.4.0.

## Source Layout

Document inputs live under `docs/src/`:

- `docs/src/template/` main template (`MPG.tex.in.in`)
- `docs/src/chapters/` chapter sources grouped by domain
- `docs/src/static/` static TeX includes (`macros.tex`, `license.tex`)
- `docs/src/bib/` bibliography inputs
- `docs/src/assets/` non-TeX source assets (for example `.vis`, `.xsd`)
- `docs/src/notes/` plain-text companion material

The tooling also recognizes the legacy root paths and warns when it uses them.

## Tooling

The project now uses a Python CLI as the primary interface:

```bash
uv run -- python -m tools.mpg doctor
uv run -- python -m tools.mpg extract
uv run -- python -m tools.mpg build --kind all
uv run -- python -m tools.mpg run --kind all
uv run -- python -m tools.mpg test --kind all
uv run -- python -m tools.mpg docs
uv run -- python -m unittest discover -s tests -p "test_*.py"
```

A thin `Makefile` is kept with the common targets:
`make quick`, `make docs`, `make extract`, `make build`, `make build-test`, `make build-notest`, `make test`, `make clean`.
You can pass Gecode location through make variables, for example:
`make test GECODE_ROOT=/Users/zayenz/gecode/gecode` or `make build GECODE_PREFIX=/usr/local`.
If neither is set and `../gecode/test/test.cpp` exists, the Makefile auto-uses `../gecode` for full test coverage.

For release validation, build the current Gecode `main` branch and pass that checkout as `GECODE_ROOT`:

```bash
git clone --depth=1 --branch main https://github.com/Gecode/gecode.git ../gecode
cmake -S ../gecode -B ../gecode/build -G Ninja -DCMAKE_BUILD_TYPE=Release \
  -DGECODE_ENABLE_QT=OFF -DGECODE_ENABLE_GIST=OFF \
  -DGECODE_ENABLE_MPFR=OFF -DGECODE_ENABLE_CPPROFILER=OFF
cmake --build ../gecode/build --parallel
make test GECODE_ROOT=../gecode
make docs
```

Once the Gecode release tag exists, use `--branch release-6.4.0` for the final release check. The 6.3.0 sources remain available as the `release-6.3.0` tag.

## Dependency Resolution

MPG supports three dependency modes:

1. System install (default): no path flags.
2. Explicit install prefix: `--gecode-prefix /path/to/prefix`.
3. Explicit source/build tree: `--gecode-root /path/to/gecode`.

### Important: full test coverage

Some `test` examples require Gecode test framework sources (`test.cpp`, `int.cpp`, `float.cpp`, `set.cpp`).
If these are unavailable from the current configuration, MPG fails with guidance.
For full coverage, use:

```bash
uv run -- python -m tools.mpg test --kind all --gecode-root ../gecode
```

## Workspace Layout

Generated files are written to `.mpg/`:

- `.mpg/generated/tex/` processed TeX files
- `.mpg/generated/src/` extracted C++ snippets
- `.mpg/build/` CMake/Ninja build trees
- `.mpg/bin/` compiled executables
- `.mpg/results/` machine-readable run summaries
- `.mpg/manifests/` per-kind example manifests used by `run`
- `.mpg/manifest.json` copy of the last manifest, kept for older tooling

## Docs Build

`uv run -- python -m tools.mpg docs` uses the standard document pipeline:

- `latex`
- `bibtex`
- `dvips`
- `ps2pdf`

This keeps the existing chapter, code, and link structure while using the Python CLI to run the build steps.

## Configuration

`mpg.toml` is optional and supports overrides:

- `version`, `year`
- `chapters`, `models`, `tests`, `notest`
- `compile_flags`
- `run_timeout_sec`
- per-example metadata in `[examples.<id>]`

## CI

- `examples.yml` runs periodic checks for `make test` and `make docs` on Linux. By default, it checks out and builds `Gecode/gecode` at `main`. It can also be run manually against another repository or ref through the `gecode_repository` and `gecode_ref` workflow inputs. For the final release check, set `gecode_ref` to `release-6.4.0` once that tag exists.
- `docs.yml` builds the PDF on Linux and publishes it as an artifact.
