:orphan:

.. _part:c:
.. _part-c:

Case studies
============

.. mpg-part:: Case studies
   :letter: C
   :authors: Christian Schulte, Guido Tack, Mikael Z. Lagerkvist

   .. mpg-part-blurb-start

   This part presents a collection of modeling case studies. The case studies
   are ordered (roughly) according to their complexity.

   **Basic models.**

   The basic models use classic constraint programming problems in order to
   demonstrate how typical modeling tasks are done with Gecode. The basic
   models are:

   - :ref:`chap:c:golomb` shows a simple problem with a single ``distinct``
     constraint and a few ``rel`` constraints. As the problem is so well known,
     it might serve as an initial case study of how to model with Gecode.

   - :ref:`chap:c:magicsequence` shows how to use counting constraints
     (``count``).

   - :ref:`chap:c:photo` shows how to use reified constraints for solving an
     overconstrained problem.

   - :ref:`chap:c:warehouses` shows how to use ``element``, ``linear``, and
     global counting (``count``) constraints.

   - :ref:`chap:c:nonogram` shows how to use regular expressions and extensional
     constraints.

   - :ref:`chap:c:golf` presents a case study on modeling problems using set
     variables and constraints.

   **Advanced models.**

   The following models are slightly more advanced:

   - :ref:`chap:c:knights` demonstrates a problem-specific brancher inspired by
     a classic heuristic for a classic problem.

   - :ref:`chap:c:bpp` also demonstrates a problem-specific brancher including
     techniques for breaking symmetries during branching.

   - :ref:`chap:c:kakuro` presents a model that employs user-defined constraints
     implemented as ``extensional`` constraints using tuple set specifications.
     Interestingly, the tuple set specifications are computed by solving a
     simple constraint problem.

   - :ref:`chap:c:crossword` presents a simple model using nothing but
     ``distinct`` and ``element`` constraints. The simple model is shown to work
     quite well compared to a dedicated problem-specific constraint solver.
     This underlines that an efficient general-purpose constraint programming
     system actually can go a long way.

   Note that the first two case studies require knowledge on programming
   branchers, see :ref:`part:b`.

   **Acknowledgments.** We thank Pierre Flener and Håkan Kjellerstrand for
   numerous detailed and helpful comments on the case studies. Their comments
   have considerably improved the presentation of the case studies.

   .. mpg-part-blurb-end
