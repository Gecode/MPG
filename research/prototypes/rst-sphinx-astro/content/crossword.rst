.. _sec-crossword-case-study:

Crossword case study
====================

A crossword model connects word choices through the letters at their crossing
cells. The historical chapter draws :numref:`fig-crossword-grid` directly with
hundreds of PSTricks commands. The replacement is generated from grid data,
retains the full 15 by 15 blocked-cell pattern, and remains sharp at any web or
print size.

.. _fig-crossword-grid:

.. figure:: assets/hard/crossword-puzzle.svg
   :alt: A fifteen by fifteen crossword grid with a symmetric pattern of dark green blocked cells.
   :width: 78%

   The legacy crossword grid regenerated as semantic SVG.

.. _fig-crossword-legacy-solution:

.. figure:: assets/hard/crossword-solution.svg
   :alt: The solved fifteen by fifteen crossword grid with dark green blocks and uppercase letters in every open cell.
   :width: 78%

   The corresponding legacy solution, regenerated from the same grid data
   rather than hundreds of positioned LaTeX commands.

For an executable check, the compact model uses a five by five word square. Its
across and down dictionaries are extensional relations over character codes.

.. literalinclude:: ../../shared/hard-pages/examples/crossword-grid.cpp
   :language: cpp
   :start-after: // region crossword-posting
   :end-before: // endregion crossword-posting
   :caption: Posting the across and down table constraints
   :name: program-crossword-posting
   :linenos:

.. _fig-crossword-solution:

.. figure:: assets/hard/crossword-mini-solution.svg
   :alt: A five by five crossword solution reading BALSA, AVAIL, TIDED, HALVE, and SNEER across.
   :width: 58%

   The checked miniature solution. Its rows are produced by the compiled model
   and compared with the illustration fixture.

:download:`Download the complete checked crossword model <../../shared/hard-pages/examples/crossword-grid.cpp>`.

The next page applies the same data-first illustration approach to a
:doc:`nonogram`.
