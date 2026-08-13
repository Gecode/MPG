# MPG modernization research

Start with [`modernization-plan.md`](modernization-plan.md). It records the
recommended architecture, decision gate, target content model, release
integration, migration phases, acceptance criteria, and verified prototype
results.

Supporting work:

- [`current-pipeline-audit.md`](current-pipeline-audit.md) inventories the real
  Perl/Python/TeX/C++ pipeline and identifies current validation gaps.
- [`toolchain-landscape.md`](toolchain-landscape.md) compares authoring and
  publishing systems using official primary sources.
- [`authoring-spike-results.md`](authoring-spike-results.md) compares the
  hardened MyST and canonical reStructuredText/Sphinx spikes and defines the
  remaining production decision gate.
- [`classical-pdf-fidelity.md`](classical-pdf-fidelity.md) inventories the
  original MPG's book design, evaluates how faithfully each finalist can retain
  it, and defines the representative-page fidelity gate.
- [`website-classical-design-plan.md`](website-classical-design-plan.md) maps
  that book grammar to site-owned Astro components and defines the separately
  built release-bundle import contract.
- [`prototypes/myst-astro`](prototypes/myst-astro/README.md) tests the
  MyST-resolved-AST to Astro path.
- [`prototypes/rst-sphinx-astro`](prototypes/rst-sphinx-astro/README.md) tests a
  strict resolved-Sphinx-doctree to Astro release artifact.
- [`prototypes/astro-mdx`](prototypes/astro-mdx/README.md) establishes the
  web-native and browser-PDF baseline.
- [`prototypes/document-first`](prototypes/document-first/README.md) establishes
  the Quarto/Pandoc fallback.
- [`prototypes/content-model`](prototypes/content-model/README.md) makes the
  format-neutral publication, code-region, and validation contracts concrete.
- [`prototypes/shared/classical-pdf`](prototypes/shared/classical-pdf/README.md)
  contains the extracted backend-independent LaTeX design package and thin
  backend adapters.
- [`prototypes/authoring-comparison.md`](prototypes/authoring-comparison.md)
  defines the common MyST/reStructuredText production-spike contract and the
  imported Gecode release-reference boundary.
- [`prototypes/shared/hard-pages`](prototypes/shared/hard-pages/README.md)
  supplies the shared overview, crossword, and nonogram fixture, deterministic
  accessible SVG generator, and executable illustration models.

Each prototype is source-only and documents one exact verification command.
Generated sites, binaries, caches, and PDFs are ignored.
