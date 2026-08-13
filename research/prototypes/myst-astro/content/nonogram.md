---
title: Nonogram case study
---

(sec-nonogram-case-study)=
## Nonogram case study

A nonogram describes each row and column by the lengths of its consecutive
filled runs. The legacy page represents the puzzle and answer as two large
LaTeX tables. @fig-nonogram-heart combines them into one accessible, responsive
illustration with aligned hints and a restrained solution color.

:::{figure} assets/hard/nonogram-heart.svg
:label: fig-nonogram-heart
:alt: Side-by-side nine by nine heart nonogram. The puzzle has row and column hints; the solution fills coral cells in a heart shape.
:width: 100%

The heart puzzle and its checked solution, generated from the same fixture.
:::

For a line with runs $2,3,1$, the model posts the regular language

:::{math}
:label: eq-nonogram-line

0^*1^2 0^+1^3 0^+1 0^*
:::

rather than enumerating line assignments. The complete program constructs that
expression from an arbitrary hint sequence:

:::{literalinclude} ../../shared/hard-pages/examples/nonogram-heart.cpp
:language: cpp
:start-after: // region nonogram-regex
:end-before: // endregion nonogram-regex
:label: code-nonogram-regex
:caption: Constructing a regular expression from line hints
:linenos:
:::

The resulting automaton is posted once for every row and column:

:::{literalinclude} ../../shared/hard-pages/examples/nonogram-heart.cpp
:language: cpp
:start-after: // region nonogram-posting
:end-before: // endregion nonogram-posting
:label: code-nonogram-posting
:caption: Posting row and column constraints
:linenos:
:::

:::{admonition} Executable illustration
:class: note

The verifier compiles this model against the current Gecode installation and
requires its nine output rows to equal the data used for the colored cells in
@fig-nonogram-heart.
:::

{download}`Download the complete checked nonogram model <../../shared/hard-pages/examples/nonogram-heart.cpp>`.
