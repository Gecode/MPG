:orphan:

.. _part:p:

Programming propagators
=======================

.. mpg-part:: Programming propagators
   :letter: P
   :authors: Christian Schulte, Guido Tack

   .. mpg-part-blurb-start

   This part explains how to program propagators as implementations of
   constraints.

   **Basic material.** :doc:`../propagators/started` shows how to implement
   simple propagators for simple constraints over integer variables. It
   introduces the basic concepts and techniques that are necessary for any
   propagator. :doc:`../propagators/testing` uses one of these propagators to
   explain how to test correctness, propagation strength, cloning, and
   scheduling with Gecode's test library.

   **Programming techniques.** The bulk of this part describes a wide range of
   techniques for programming efficient propagators:

   * :doc:`../propagators/avoid` discusses techniques for avoiding propagator
     execution. The examples used in this chapter introduce view arrays for
     propagators and Boolean views.
   * :doc:`../propagators/reified` discusses how to implement propagators for
     reified constraints and how to optimize constraint propagation by
     propagator rewriting.
   * :doc:`../propagators/domain` explains various programming techniques for
     propagators that perform domain propagation. The chapter also describes
     modification event deltas as information available to propagators and
     staging as a technique for speeding up domain propagation.
   * :doc:`../propagators/advisors` is concerned with advisors for efficient
     incremental propagation. Advisors can be used to provide information to a
     propagator which of its views have changed and how they have changed.
   * :doc:`../propagators/views` shows how to straightforwardly and efficiently
     reuse propagators for implementing several different constraints by using
     views. As it comes to importance, this chapter ranks second after
     :ref:`chap:p:started`. However, it comes rather late to be able to draw on
     the example propagators presented in the previous chapters.

   **Overview material.** The following chapters summarize or provide an
   overview of topics related to programming propagators:

   * :doc:`../propagators/sets` summarizes how to implement propagators for
     constraints over set variables.
   * :doc:`../propagators/floats` summarizes how to implement propagators for
     constraints over float variables.
   * :doc:`../propagators/memory` provides an overview of memory management for
     propagators (and branchers, see :ref:`part:b`).

   .. mpg-part-blurb-end
