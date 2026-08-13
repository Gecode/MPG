# Release and website import

The MPG is a Gecode release artifact. The Gecode release job builds the HTML
manual and PDF from the same reStructuredText sources, tests every published
program against that release, and freezes links to the matching reference
manual. An ordinary Astro website build does none of this work.

## Gecode release job

The release job needs the Gecode source tree, its compiled libraries, the
Doxygen tag file and generated reference HTML, Sphinx, XeLaTeX, Poppler, and
the SVG conversion tools listed in `figures/README.md`.

For a release `6.4.0`, run from the MPG repository root:

```sh
python3 rst/scripts/generate_reference_inventory.py \
  --source rst/content \
  --tag ../gecode/doc/gecode-doc.tag \
  --html-root ../gecode/doc/html \
  --version 6.4.0 \
  --output rst/release-reference-inventory.json

python3 rst/tools/inventory.py --check rst/manifests/legacy-parity.json
python3 rst/tools/coverage.py \
  --manifest rst/manifests/legacy-parity.json \
  --contract rst/manifests/source-coverage.json
python3 rst/scripts/migrate_code.py --check
python3 rst/scripts/verify_code_sites.py
python3 rst/figures/scripts/verify.py
python3 rst/scripts/verify_examples.py --gecode-root ../gecode
research/prototypes/rst-sphinx-astro/.venv/bin/python rst/scripts/verify_platform.py

GECODE_VERSION=6.4.0 \
  research/prototypes/rst-sphinx-astro/.venv/bin/python \
  rst/scripts/build.py all

python3 rst/scripts/package_release.py --version 6.4.0
```

`build.py` stages `rst/content` together with the canonical figure tree before
calling Sphinx. This gives the published manual clean routes such as
`modeling/started/`, while the source repository keeps figures and their
generators outside the prose tree.

The package command writes two outputs:

- `output/releases/6.4.0/modeling/` is the website import bundle.
- `output/pdf/MPG-6.4.0.pdf` is the independently published PDF.

The bundle contains complete static HTML, local search data, exact source
downloads, redirects, the PDF, and `release-manifest.json`. The manifest fixes
the mount point, page routes, file sizes, and SHA-256 hashes. Packaging refuses
to replace an existing version. Replacing a published manual should therefore
be an explicit release operation rather than a side effect of rebuilding the
site.

## Astro import

The website release-import job verifies every file against
`release-manifest.json`, checks that the manifest version matches the target
release, and copies the bundle to:

```text
dist/doc/6.4.0/modeling/
```

The website uses the manifest's `pages` list to add the manual to its release
navigation and search indexing. It also exposes `MPG.pdf` next to the HTML
edition and merges the bundle's redirects with the site's release redirects.
The imported files are immutable for that version.

The PDF accessibility baseline and the separately gated tagged-PDF work are
documented in `ACCESSIBILITY.md`. A successful visual PDF build must not be
reported as tagged or PDF/UA conforming unless that document's tagged-PDF gate
has also been satisfied.

The Sphinx template owns each complete manual page, including its compact
manual header, local contents, previous/next links, code downloads, and offline
search. Astro owns the site-level documentation index and release chooser that
lead into the versioned manual. Their visual contract is the small set of
Gecode colour and typography tokens in `_static/mpg.css`; it is not a second
landing-page design. Changes to that contract should be checked on a dense
chapter, a part opening, a case study with figures, and a narrow screen before
a release bundle is accepted.

This import runs when a Gecode release is published. The normal website build
consumes the already imported, versioned files and must not invoke Sphinx,
XeLaTeX, the Gecode compiler, or the literate extraction tools.
