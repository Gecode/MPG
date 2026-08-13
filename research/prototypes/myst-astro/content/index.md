---
title: A first model
---

(sec-first-model)=
## Send More Money

This page exercises the semantics that MPG needs. The equation is @eq-send-more-money,
the diagram is @fig-search-tree, and the source excerpt is @code-search-loop. The
historical context is described by {cite:p}`schulte1999`.

The model derives from {gecode-api}`class:Gecode::Space`, resolved against the
inventory imported with the Gecode 6.4.0 release. The shared macro renders
$\Model$ consistently on both pages.

:::{math}
:label: eq-send-more-money

SEND + MORE = MONEY
:::

:::{figure} assets/search-tree.svg
:label: fig-search-tree
:alt: A root search node splitting into failed and solved alternatives.
:width: 70%

A small search tree, kept as SVG for both responsive HTML and vector PDF.
:::

The complete program below is canonical. The page includes a delimited region from
that file; the verification command compiles and runs the complete file itself.

:::{literalinclude} ../examples/send-more-money.cpp
:language: cpp
:start-after: // region search-loop
:end-before: // endregion search-loop
:label: code-search-loop
:caption: The checked search loop excerpt
:linenos:
:::

:::{admonition} Release invariant
:class: note

The displayed excerpt, download, and compiled input all come from one canonical
file.
:::

:::{table} Expected execution result
:label: table-results

| Model | Solution | Status |
| --- | ---: | --- |
| $\Model$ | `9567 + 1085 = 10652` | checked |
:::

{download}`Download the complete checked program <../examples/send-more-money.cpp>`.

The [second page](./second-page.md) checks cross-page references.
