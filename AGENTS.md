# Working on MPG

Keep changes simple. Do not add abstractions or tests that merely mirror an
implementation. Use focused regression checks for actual behavior changes.

The maintained book is `rst/content/`; examples are under `rst/examples/`.
Read `rst/README.md` before authoring. Never recreate TeX book sources, duplicate
executable examples in prose, or use files in `.mpg/` as source inputs.

- Edit prose directly, preserve explicit labels, and use the semantic directives.
- After editing an example, run `uv run --locked -- python rst/scripts/code.py refresh`,
  inspect the projection diff, and verify the affected listings. See the guide
  for deliberate boundary changes and new examples.
- After editing SVGs, regenerate and commit their PDF companions.
- Use `make check-sources` for source changes, `make check GECODE_ROOT=../gecode`
  for example/tooling changes, and `make docs` for full publication verification.
- Review changed HTML at desktop and narrow widths and inspect affected PDF pages.

`make release` validates and packages the manual. It does not publish to
Cloudflare; release-support owns cross-repository publication. Do not treat a
CI preview package as an announced release.
