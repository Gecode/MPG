:orphan:

.. _part:m:
.. _part-m:

Modeling
========

.. mpg-part:: Modeling
   :letter: M
   :authors: Christian Schulte, Guido Tack, Mikael Z. Lagerkvist

   .. mpg-part-blurb-start

   .. only:: latex

      .. raw:: latex

         \mbox{}\vfill

   This part explains modeling and solving constraint problems, and how to
   program, compile, link, and execute constraint models.

   **Basic material.**

   The basic material needed for modeling with Gecode is as follows:

   * :ref:`chap:m:started` provides an overview of how to program, compile,
     link, and execute a constraint model in Gecode.
   * :ref:`chap:m:comfy` discusses functionality in Gecode that makes
     modeling and execution of models more convenient.
   * The first three sections of :ref:`chap:m:int` explain integer and Boolean
     variables (:ref:`sec:m:integer:var`), variable and argument arrays
     (:ref:`sec:m:integer:proper`), and how constraints are posted
     (:ref:`sec:m:integer:generic`).
   * The first section of :ref:`chap:m:set` gives an overview of set variables
     (:ref:`sec:m:set:var`).
   * The first section of :ref:`chap:m:float` gives an overview of float
     variables (:ref:`sec:m:float:var`).
   * The first sections of :ref:`chap:m:branch` explain branching: basics
     (:ref:`sec:m:branch:basics`), branchings for integer and Boolean variables
     (:ref:`sec:m:branch:int`), branchings for set variables
     (:ref:`sec:m:branch:set`), and branchings for float variables
     (:ref:`sec:m:branch:float`).
   * Even though not strictly necessary for modeling, it is recommended to
     also read :ref:`sec:m:search:re` and :ref:`sec:m:search:parallel`, which
     explain how search—and in particular parallel search—works in Gecode.

   :ref:`part:c` features a collection of example models for Gecode as further
   reading.

   .. only:: latex

      .. raw:: latex

         \mbox{}\vfill\newpage\thispagestyle{empty}\mbox{}\vfill

   **Overview material.**

   The remaining chapters and sections provide an overview of the available
   functionality for modeling and solving:

   * Constraints on integer and Boolean variables are summarized in
     :ref:`sec:m:integer:post` and :ref:`sec:m:integer:exec` of
     :ref:`chap:m:int`.
   * :ref:`sec:m:set:post` and :ref:`sec:m:set:exec` of :ref:`chap:m:set`
     summarize constraints on set variables.
   * :ref:`sec:m:float:post` and :ref:`sec:m:float:exec` of
     :ref:`chap:m:float` summarize constraints on float variables.
   * :ref:`chap:m:minimodel` provides an overview of modeling convenience
     implemented by MiniModel.
   * The remaining sections of :ref:`chap:m:branch` discuss more advanced
     topics for branchings: local versus shared variable selection
     (:ref:`sec:m:branch:shared`), random selection
     (:ref:`sec:m:branch:rnd`), user-defined variable
     (:ref:`sec:m:branch:uservar`) and value (:ref:`sec:m:branch:userval`)
     selection, tie-breaking (:ref:`sec:m:branch:tie`), assigning variables
     (:ref:`sec:m:branch:assign`), and executing code between branchers
     (:ref:`sec:m:branch:code`).
   * :ref:`sec:m:search:simple` of :ref:`chap:m:search` summarizes how to use
     search engines.
   * :ref:`chap:m:gist` summarizes how to use Gist as a graphical and
     interactive search tool for developing constraint models.
   * :ref:`chap:m:driver` summarizes the command-line driver for Gecode
     models.
   * :ref:`chap:m:group` explains how to use groups for tracing constraint
     propagation.

   .. only:: latex

      .. raw:: latex

         \vfill\mbox{}

   .. mpg-part-blurb-end
