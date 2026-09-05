# Release and website import

MPG is built once for a Gecode release and published as static HTML, source
downloads, search data, and a PDF. RST is the only book source. An ordinary
Astro website build does not run Sphinx, XeLaTeX, or the C++ example tests.

## Prepare and validate

Use a checkout and compiled libraries of the matching Gecode release, including
its test framework, generated Doxygen tag file, and reference HTML. Install the
locked Python/Node dependencies and the PDF/figure tools listed in the root
README. From the MPG repository root:

```sh
uv sync --locked
npm ci

uv run --locked -- python rst/scripts/generate_reference_inventory.py \
  --source rst/content \
  --tag ../gecode/doc/gecode-doc.tag \
  --html-root ../gecode/doc/html \
  --version 6.4.0 \
  --output rst/release-reference-inventory.json

make release MPG_VERSION=6.4.0 GECODE_ROOT=../gecode \
  RST_BUILD=/tmp/mpg-release-build MPG_OUTPUT=/tmp/mpg-release-output
```

Use fresh build/output directories for each pinned release. `make release`
runs current code and figure checks, tooling/platform tests, canonical example
compilation and execution, strict HTML/PDF builds, and packaging. Three Gist
examples require interactive review; their execution is recorded as skipped.
There is no TeX extraction or historical coverage prerequisite.

If examples or figures changed, refresh their code selections or PDF companions
as described in `README.md` before running the gate. Do not regenerate a release
inventory from a different Gecode version to make a missing API reference pass.

For the historical 6.4.0 Cloudflare seed, the checked-in inventory is reconciled
with the published reference HTML retained in `gecode.github.io/doc/6.4.0/reference`.
That seed keeps the existing reference edition; regenerating its inventory from
a new local Doxygen build can introduce filenames and anchors absent from the
published edition. Validate the completed MPG links against that retained tree.

## Bundle contract

The example above writes:

- `/tmp/mpg-release-output/releases/6.4.0/modeling/`: complete modeling-manual bundle.
- `/tmp/mpg-release-output/pdf/MPG-6.4.0.pdf`: standalone PDF.

`release-manifest.json` specifies the mount `/doc/6.4.0/modeling/`, entry page,
search index, redirects, and file sizes/hashes. The package contains complete
HTML pages, local styles/scripts/fonts, exact source downloads, and the PDF.
Internal build files are excluded. Packaging rejects unsupported versions,
mismatched HTML/PDF build markers, and an existing version's output.

The HTML builder verifies local links and fragments and rejects API links
pointing to another release. It stages output and publishes it only after a
successful build. Successful markers prevent relabeling an old artifact; they
do not replace clean pinned release builds.

The documentation CI job creates a downloadable **preview** package. The
example CI job independently compiles and tests the canonical examples. Neither
job announces a release, and a preview is not evidence that all coordinated
release gates have run for a final tag.

## Cloudflare integration

Release-support assembles the verified MPG bundle with matching Doxygen output
under `reference/`, `modeling/`, and `MPG.pdf`. Its current consumer validates
paths, hashes, PDF agreement, and the website mount contract. The neighboring
website's `docs/gecode-release-pipeline.md` defines publication and routing.

Release-support provides `scripts/documentation.py` for documentation updates
and the stateful release coordinator for new Gecode releases. Both assemble the
same bundle and use the website's immutable R2 upload helper. `make release`
packages MPG; it does not upload or deploy it.

A documentation revision is separate from the Gecode version. For a text or
HTML correction to 6.4.0, build and validate MPG as 6.4.0, then prepare and upload
a fresh revision with matching 6.4.0 reference HTML. Verify its immutable preview
before selecting it in the website's production Worker configuration. This
updates `/doc/6.4.0/` and, while 6.4.0 remains latest, `/doc/latest/`, without
creating a Gecode or MPG release tag. Previous revisions remain available for
rollback. See release-support's README for the prepare, publish, select, and
verify commands.

The Sphinx template owns complete manual pages. Astro owns the site-level
entry pages; the Cloudflare documentation router serves versioned manual files.
The shared visual contract is the Gecode color/typography tokens in
`_static/mpg.css`. Review dense chapters, figures, search, mobile navigation,
and PDF hyperlinks when changing that contract.

The PDF's metadata/text-extraction baseline and its untagged status are described
in `ACCESSIBILITY.md`. Passing the publication gate does not establish PDF/UA
conformance.
