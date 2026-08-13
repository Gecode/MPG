# MyST and reStructuredText spike contract

The MyST and canonical reStructuredText/Sphinx spikes must implement the same
publication slice. The comparison measures the complete production boundary,
not isolated parser features.

## Reference-documentation assumption

Gecode builds its reference documentation as part of a Gecode release. That
release job must also emit a small, versioned symbol inventory. The website
imports the rendered reference tree and inventory as release artifacts. Normal
website and MPG builds consume them; they never run Doxygen or rebuild the
reference documentation.

The fixture at `shared/reference-inventory.json` models this contract. A
production inventory can contain more metadata or an `objects.inv` derivative,
but it must retain stable symbol kind/name keys, relative URLs, titles, and the
Gecode release version. MPG links combine the imported release base URL with
the inventory's relative URL.

Validate the fixture alone, or validate that every target exists after the
release documentation has been imported into a site tree:

```sh
python3 shared/validate_reference_inventory.py shared/reference-inventory.json
python3 shared/validate_reference_inventory.py shared/reference-inventory.json \
  --site-root ../../../gecode.github.io
```

## Required content

Both spikes contain two pages and demonstrate:

1. stable page and section IDs plus cross-page references;
2. numbered section, equation, SVG figure, program listing, and table;
3. a callout/admonition;
4. BibTeX citation and bibliography;
5. a shared mathematical macro;
6. a canonical external C++ file, a named excerpt, and a download of the exact
   compiled file;
7. a typed `Gecode::Space` API reference resolved from the imported inventory;
8. Astro-owned routes, layout, and CSS from semantic resolved data rather than
   scraped standalone-site HTML; and
9. an A4 book PDF from the same canonical source.

## Required verification

One documented command must verify:

- strict source parsing with unresolved/duplicate-reference failures;
- failure on an unsupported semantic node;
- consistent object kind, number, and link in web and PDF outputs;
- correct citation, bibliography, math, figure, table, callout, and API URL;
- byte identity among the canonical, downloaded, and compiled C++ file;
- actual C++ compilation and execution;
- explicit dependency tracking from the external C++ file to its pages;
- a clean build without mutable template downloads;
- an offline rebuild after dependencies are installed;
- Astro type/build checks and local-link checks; and
- PDF structure plus rendered-page visual inspection.

## Decision measurements

Record direct dependency versions, clean build time, output size, adapter and
extension source lines, generated web/PDF size, unmapped constructs, warnings,
and any format-specific workaround. Discuss authoring clarity separately from
implementation size.

The winning path must still pass the larger `m-started`/`p-started` production
gate. This fixture selects between credible candidates; it does not authorize a
bulk migration.
