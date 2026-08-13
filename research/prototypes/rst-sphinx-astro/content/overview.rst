.. _sec-architecture-overview:

Architecture overview
=====================

Gecode's architecture is organized around a small kernel. Variable and
constraint modules build on that kernel, search explores spaces created by a
model, and extension APIs let users add propagators, branchers, variables, and
search engines. The new overview in :numref:`fig-gecode-architecture` replaces a
PSTricks drawing embedded in the legacy LaTeX chapter.

.. _fig-gecode-architecture:

.. figure:: assets/hard/architecture.svg
   :alt: Layered Gecode architecture with modeling above the integer, set, float, and search modules, all resting on the kernel, with extension points at the sides.
   :width: 100%

   The principal Gecode layers and extension points. One accessible SVG is used
   by the responsive site and vector PDF.

The diagram makes three relationships explicit:

* models use facilities supplied by the modules;
* modules share spaces, actors, and memory services from the kernel; and
* extension points compose with the public architecture rather than sitting in
  a separate implementation layer.

The :doc:`crossword` and :doc:`nonogram` pages exercise the same publication
pipeline with data-heavy figures and executable models.
