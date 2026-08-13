# Classical MPG structure in the Astro website

## Decision

Use the classical MPG design as a restrained documentation language inside the
existing Gecode site, not as a second site theme and not as generated
authoring-tool HTML. The Gecode release job owns the manual's resolved
semantics, tested code, figures, PDF, and version metadata. The Astro repository
owns routes, site chrome, responsive layout, navigation, search integration,
and the rendering of those semantics.

The web edition should look like the PDF has been carefully unfolded into a
scrolling medium. It must not be redesigned as a magazine, product landing page,
or dashboard.

## Negative constraints

The following are not part of the MPG visual language and must not be
introduced:

- oversized editorial or marketing headlines;
- kickers such as “tested examples · web and PDF”;
- calls to action such as “Start reading” or “Browse the contents”;
- full-width brand-color bars added around the manual;
- invented Gecode wordmarks or mock site navigation;
- card grids, dashboard rails, decorative shadows, or promotional statistics;
- uppercase microcopy used as ornament; and
- a bespoke manual landing-page shell.

The reference is the original PDF itself: quiet title and part pages, moderate
Charter type, small blue/orange number boxes, dense linear prose, pale code
panels, plain tips, blue/green links, and generous whitespace only at genuine
book divisions.

## What transfers from print

Transfer the elements that communicate publication structure:

| Classical MPG | Astro/Tailwind expression |
| --- | --- |
| Mnemonic part letter, such as M | A small part-opening block above the part introduction |
| Blue boxed chapter number | Compact chapter opener paired with the page `h1` |
| Orange program panel | `MpgProgram` component with object number, projection name, source link, and copy action |
| Red command panel | `MpgCommand` component clearly distinct from C++ source |
| Numbered theorem-like tip | `MpgTip` landmark retaining its number and restrained closing triangle |
| Four Gecode colors and tints | Shared semantic CSS custom properties with contrast-safe text variants |
| Dense technical hierarchy | Normal document flow, restrained section numbering, readable measure |
| Figure captions and stable numbers | Responsive figure component with stable ID, number, caption, and long description |
| Quiet book navigation | Existing site sidebar plus unobtrusive previous/next and version links |

Do not transfer recto/verso rules, fixed page margins, blank leaves, print float
placement, centered folios, or page-number references. Those are pagination
mechanics, not publication identity.

## Typography and site integration

Keep the existing website's Open Sans, Raleway, and Roboto Mono roles in the
site chrome. A Charter-compatible web font may be scoped to `.mpg-manual` body
text and headings to connect the web edition to the PDF; it must be vendored
with an audited web license and pinned metrics. Use it at ordinary documentation
sizes, not as display typography. If it cannot be shipped, use the site's Open
Sans rather than an unreliable system-only Charter stack.

The manual stays inside the real `BaseLayout` and uses the site's real logo,
primary navigation, footer, focus treatment, content width, and breakpoint
conventions. The MPG layer should add only document-internal structure.

## Page structure

Use the existing two-column site frame. The main column contains one linear
manual page. The existing right sidebar remains the site/navigation area; it may
show the current manual part and chapter list using the same sidebar geometry,
not a second rail.

The manual landing route should begin with a restrained title block modelled on
the PDF title page: existing Gecode logo, title, authors, release, and links to
the PDF and contents. Follow it immediately with an ordinary hierarchical table
of contents. There is no hero, slogan, CTA, card grid, or “six connected parts”
marketing section.

A part route begins with the original small tinted letter box, part title, and
authors centered in the main column, followed by the part blurb as normal prose.
It should not consume a full browser viewport.

A chapter route begins with a compact blue number box to the left and the
chapter title aligned to it, closely following the PDF proportion. Body text
then proceeds in a single column. Section headings, tips, programs, tables, and
figures remain in source order.

## Release and import flow

MPG is built on a Gecode release. It is not rebuilt by the ordinary website
pipeline.

```text
Gecode release job
  authoring resolver + code tests + figure generation
        |                      |
        |                      +--> MPG.pdf
        +--> mpg-web-bundle-v1/
               publication.json
               pages/*.json
               navigation.json
               references.json
               search.json
               assets/*
               downloads/*
               checksums.json
                        |
                        v
website artifact-import step (version + digest pinned)
  validate schema and checksums; stage local immutable files
                        |
                        v
ordinary Astro build
  content loader -> exhaustive semantic renderer -> site-owned components
```

The website build may consume a previously imported local bundle, but it must
never invoke Sphinx, MyST, TeX, CMake, Doxygen, or Gecode. Fetching should be an
explicit artifact-import or dependency-update operation that records the release
version and digest, not an unpinned network request during every site build.

Astro's build-time Content Loader API is a good fit for the staged JSON bundle:
it can validate entries with a schema and expose them through content collection
queries. A custom loader should reject unsupported bundle schema versions,
duplicate IDs, unknown semantic nodes, missing assets, and checksum mismatches.

## Bundle contract

The release bundle should contain resolved semantics, not HTML scraped from a
document generator. Each page entry needs:

- stable page ID, route, title, description, release, part, chapter, and order;
- a closed list of typed nodes with stable IDs and resolved object numbers;
- resolved internal targets and versioned Gecode API links;
- previous/next relationships and ordered navigation;
- figure metadata, accessible descriptions, and fingerprinted asset paths;
- code artifact/projection IDs, exact displayed text, language, source-map
  metadata, and fingerprinted canonical downloads;
- citation and bibliography data needed by the page;
- search title, headings, summary, and plain text; and
- bundle/schema version plus checksums.

The renderer maps these nodes to a small site-owned component set:

```text
MpgPage
MpgPartOpening      MpgChapterOpening
MpgSection         MpgCrossReference
MpgProgram         MpgCommand
MpgTip             MpgFigure
MpgEquation        MpgTable
MpgBibliography    MpgDownload
```

This mapping must be exhaustive. A new node from a Sphinx or MyST upgrade should
fail the release adapter or website import, not silently degrade into unstyled
HTML.

## Design-token ownership

Use one checked token source for facts that truly cross media:

- exact Gecode green, blue, red, and orange values;
- tint values and semantic roles;
- object names (`Part`, `Chapter`, `Program`, `Tip`, `Figure`);
- print and web font-role declarations; and
- accessibility-safe foreground colors for web use.

Generate or validate both `mpg-classic.sty` and an `mpg-tokens.css` derivative
from that source. Do not try to share layout code between TeX and CSS. The
prototype's `design-tokens.json` is the starting contract, not yet the production
generator.

## Routing and versioning

Recommended active routes:

```text
/doc/<version>/modeling/
/doc/<version>/modeling/getting-started/
/doc/<version>/case-studies/nonogram/
```

Preserve `/doc/<version>/MPG.pdf` and existing example download URLs. The import
manifest must carry redirects or aliases for historical anchors that have web
equivalents. `/doc/current/...` may redirect to the selected current release,
but canonical URLs should include the concrete version.

For old bundle-schema versions, either retain the compatible renderer or freeze
that release's already-built static output. Do not reinterpret historical
content with an incompatible current adapter.

## Responsive and accessibility contract

- Wide screens use the site's existing main/sidebar proportions; do not add a
  third column.
- At phone width, use the site's existing mobile navigation and an optional
  native `details` manual contents control.
- The part and chapter openings stack only when needed, and their title text
  must remain fully inside the viewport.
- Programs scroll within their own region; the document itself must never gain
  horizontal overflow.
- Figures remain selectable or accessible SVG, with captions and long
  descriptions available independently of color.
- Object identity cannot rely on color alone.
- Keyboard focus, skip navigation, 200% zoom, reduced motion, forced colors,
  and print styles are release gates.

## Verification

Every imported release should run:

1. bundle schema, checksum, ID, route, reference, and asset validation;
2. Astro type checking and static build;
3. exhaustive node/component coverage checks;
4. HTML validation, link checking, canonical URL checking, and search-record
   validation;
5. byte comparison between declared canonical code downloads and the release
   artifacts that were compiled;
6. an automated assertion that `scrollWidth <= clientWidth` for the document at
   the supported phone viewport;
7. fixed screenshots for landing, dense chapter, code-heavy chapter, large
   table, and modern figure pages at desktop and phone widths; and
8. keyboard, 200% zoom, reduced-motion, forced-color, and screen-reader spot
   checks before template releases.

## Implementation sequence

1. Finalize the semantic bundle schema using the winning authoring adapter.
2. Implement the small part, chapter, program, command, tip, and figure
   components directly in the actual Gecode site's `BaseLayout`.
3. Implement a local, build-time `mpg` content loader with strict schema and
   checksum validation.
4. Render the hard-page bundle through the real dynamic version/page routes.
5. Add the manual to site search and the documentation/version navigation.
6. Run the responsive/accessibility gate and compare the same overview,
   crossword, nonogram, first-model, program, and tip fixtures used by PDF.
7. Publish one release candidate alongside the legacy PDF before making the web
   edition the default MPG destination.

## Primary references

- [Astro content collections](https://docs.astro.build/en/guides/content-collections/)
- [Astro Content Loader API](https://docs.astro.build/en/reference/content-loader-reference/)
- [Astro scoped and global styling](https://docs.astro.build/en/guides/styling/)
