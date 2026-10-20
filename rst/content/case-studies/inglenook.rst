.. _chap:c:inglenook:

Inglenook shunting puzzle
=========================

This chapter models an Inglenook shunting puzzle as a bounded-string container
relocation problem.

.. _sec:c:inglenook:problem:

Problem
-------

An Inglenook consists of three sidings and a head-shunt. Each track has a
capacity, and each string symbol identifies one wagon. A move transfers a
non-empty consecutive group of wagons between one siding and the head-shunt.
The goal is to transform an initial arrangement into a requested arrangement
using as few moves as possible.

The instance uses wagons ``1`` through ``5`` and three indistinguishable
symbols ``x``. Siding ``A`` initially contains ``x4312``, siding ``B`` contains
``xx5``, and the other tracks are empty. The target is ``12345`` on ``A`` and
``xxx`` on ``B``.

.. _sec:c:inglenook:representation:

String representation
---------------------

Arrays ``A``, ``B``, ``C``, and ``X`` record every track after each possible
move. Their indices include zero for the initial state. Length constraints
enforce track capacities, and regular-language constraints restrict every
symbol to the wagon alphabet.

.. mpg-code:: inglenook:state variables
   :direct:

The integer arrays ``DiffA`` through ``DiffX`` record the length change of each
track. ``Moves[i]`` selects siding ``A``, ``B``, or ``C`` at step ``i``; zero
means that the solution has already stopped.

.. _sec:c:inglenook:moves:

Modeling a move
---------------

A move between siding ``A`` and the head-shunt preserves their concatenation:

.. math::

   A_i \mathbin{+\!\!+} X_i = A_{i-1} \mathbin{+\!\!+} X_{i-1}.

The other two sidings remain unchanged. Requiring a non-zero length difference
excludes an empty transfer, while opposite differences on the participating
tracks preserve the number of wagons. The same construction is used for
sidings ``B`` and ``C``.

.. mpg-code:: inglenook:move transitions
   :direct:

The indexed Boolean array selects exactly one of the no-move, ``A``, ``B``, or
``C`` alternatives. Once a no-move is selected, all later states are fixed and
all later move selectors are zero. This permits a fixed-size model while
minimizing the actual number of moves.

The additional constraints on the four length differences are redundant but
useful: either two tracks change by opposite amounts or all four differences
are zero.

.. _sec:c:inglenook:symmetry:

Redundant constraints and move normalization
--------------------------------------------

Using the same siding twice in succession can be replaced by a single transfer,
so two equal consecutive non-zero move selectors are forbidden. The model also
requires the head-shunt length to change at every non-zero move and preserves
the total length difference across the complete sequence.

These conditions do not change the feasible shunting plans. They eliminate
representations containing empty or immediately mergeable transfers and expose
failures earlier.

.. _sec:c:inglenook:objective:

Objective and result
--------------------

The objective subtracts the number of zero selectors from the fixed move
horizon.

.. mpg-code:: inglenook:objective
   :direct:

The validated optimum for this instance is ``tot_moves = 11``. The complete
model is shown in :numref:`program:c:inglenook`.

.. mpg-code:: inglenook
   :caption: A bounded-string model of the Inglenook puzzle
   :name: program:c:inglenook
   :download:

The case study illustrates why strings are more than a textual convenience:
concatenation directly expresses conservation of an ordered sequence, string
length expresses capacity, and regular-language membership defines the symbol
alphabet.
