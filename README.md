# Modeling and Programming with Gecode (MPG)

This repository contains the LaTeX source and generated code examples for **Modeling and Programming with Gecode**.

## Modern Tooling

The project now uses a Python CLI as the primary interface:

```bash
uv run -- python bin/mpg.py doctor
uv run -- python bin/mpg.py extract
uv run -- python bin/mpg.py build --kind all
uv run -- python bin/mpg.py run --kind all
uv run -- python bin/mpg.py test --kind all
uv run -- python bin/mpg.py docs
```

A thin `Makefile` is kept for compatibility (`make quick`, `make gcc`, `make gcc-test`, `make gcc-notest`, `make clean`).
You can pass Gecode location through make variables, for example:
`make test GECODE_ROOT=/Users/zayenz/gecode/gecode` or `make gcc GECODE_PREFIX=/usr/local`.
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
uv run -- python bin/mpg.py test --kind all --gecode-root ../gecode
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

`uv run -- python bin/mpg.py docs` uses the layout-compatible legacy pipeline:

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

- `examples.yml` runs `doctor`, `extract`, and `test --kind all` on Linux/macOS/Windows.
- `docs.yml` builds the PDF on Linux and publishes it as an artifact.
