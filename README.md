# Modeling and Programming with Gecode (MPG)

This repository contains the LaTeX source and generated code examples for **Modeling and Programming with Gecode**.

## Source Layout

Document inputs now live under `docs/src/`:

- `docs/src/template/` main template (`MPG.tex.in.in`)
- `docs/src/chapters/` chapter sources grouped by domain
- `docs/src/static/` static TeX includes (`macros.tex`, `license.tex`)
- `docs/src/bib/` bibliography inputs
- `docs/src/assets/` non-TeX source assets (for example `.vis`, `.xsd`)
- `docs/src/notes/` plain-text companion material

During migration, tooling still supports legacy root paths with runtime warnings.

## Gecode Skills

Canonical Gecode skills are now maintained in:

- `Gecode/gecode-skills`

Install from the canonical repository:

```bash
npx skills add Gecode/gecode-skills
```

List available skills:

```bash
npx skills add Gecode/gecode-skills --list
```

Install a single skill:

```bash
npx skills add Gecode/gecode-skills --skill gecode-modeling
```

The `skills/` directory in this repository is retained as a reference snapshot for MPG work and is not the release source for published skills.

## Modern Tooling

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

A thin `Makefile` is kept with modern targets:
`make quick`, `make docs`, `make extract`, `make build`, `make build-test`, `make build-notest`, `make test`, `make clean`.
You can pass Gecode location through make variables, for example:
`make test GECODE_ROOT=/Users/zayenz/gecode/gecode` or `make build GECODE_PREFIX=/usr/local`.
If neither is set and `../gecode/test/test.cpp` exists, the Makefile auto-uses `../gecode` for full test coverage.

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
- `.mpg/manifest.json` extracted example manifest

## Docs Build

`uv run -- python -m tools.mpg docs` uses the standard document pipeline:

- `latex`
- `bibtex`
- `dvips`
- `ps2pdf`

This preserves chapter/code structure and link behavior while modernizing orchestration.

## Configuration

`mpg.toml` is optional and supports overrides:

- `version`, `year`
- `chapters`, `models`, `tests`, `notest`
- `compile_flags`
- `run_timeout_sec`
- per-example metadata in `[examples.<id>]`

## CI

- `examples.yml` runs periodic checks for `make test` and `make docs` on Linux.
- `docs.yml` builds the PDF on Linux and publishes it as an artifact.
