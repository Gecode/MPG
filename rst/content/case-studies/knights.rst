.. _chap:c:knights:

Knight’s tour
=============


This chapter demonstrates a problem-specific brancher inspired by a classic heuristic for a classic problem.

.. important::

   This case study requires knowledge on programming branchers, see :ref:`part:b` .

.. _sec:c:knights:problem:

Problem
-------


The problem of a knight’s tour is to find a series of knight’s moves (a knight can move two fields vertically and simultaneously one field horizontally, or vice versa) on an empty :math:`n\times n` board starting from some initial field such that:

- each field is visited exactly once, and

- there is a further knight’s move from the last field of the tour to the initial field.


.. mpg-figure:: :math:`8\times 8`-knight’s tour
   :name: fig:c:knights:example:8
   :class: mpg-figure-compact

   .. only:: html

      .. image:: /figures/fig-c-knights-example-8.svg
         :alt: 8 by 8 knight’s tour

   .. only:: latex

      .. image:: /figures/pdf/fig-c-knights-example-8.pdf
         :alt: 8 by 8 knight’s tour


:numref:`fig:c:knights:example:8` shows a knight’s tour for :math:`n=8`, where the tour starts at the lower left corner.

.. _case-studies:knights:model:

Model
-----

The model for the knight’s tour uses a successor representation for the knight’s moves to make posting the constraints straightforward. To further simplify posting the constraints, the variables in the model use *fields* on the board as values. The field :math:`0` has :math:`\langle \mathtt x,\mathtt
y\rangle`-coordinates :math:`\langle 0,0\rangle` on the board, the field :math:`1` has coordinates :math:`\langle 1,0\rangle`, the field :math:`n` on an :math:`n\times n` board has coordinates :math:`\langle 0,1\rangle`, and so on. That is, fields on the board are counted first in ``x``-direction and then in ``y``-direction.

The successor representation means that a variable in the model has the field numbers as possible values that can be reached by a knight’s move. The model uses the ``circuit`` constraint (see :ref:`sec:m:integer:circuit` ) to enforce that the tour is in fact a Hamiltonian circuit. The only additional constraints needed are that fields must be reachable only by knight’s moves.


.. _fig:c:knights:script:

.. mpg-code:: knights
   :caption: A script for the knight’s tour problem
   :download:


:ref:`fig:c:knights:script` outlines the program to implement the knight’s tour model. An object of class ``Knights`` stores the size of the board as its member ``n``. The variables for the knight moves are stored in the integer variable array (see :ref:`sec:m:integer:intvararray` ) ``succ``. The array ``succ`` has :math:`\mathtt{n}^2` elements where the variable at position ``f`` stores the successor of the field ``f``. The function ``f(x,y)`` computes the field number for coordinates :math:`\langle\mathtt x,\mathtt
y\rangle`. For example, ``f(0,0)=0``, ``f(1,0)=1``, and ``f(0,1)=n``.

.. _case-studies:knights:enforcing-knight-s-moves:

Enforcing knight’s moves.
'''''''''''''''''''''''''

Domain constraints ``dom`` (see :ref:`sec:m:integer:dom` ) are used to constrain moves to knight’s moves:


.. mpg-code:: knights:knight's moves
   :direct:


The function ``neighbors(i)`` returns an integer set which contains the fields that are reachable from field ``i`` by a knight’s move. For example, for :math:`\mathtt{n}=8`, ``neighbors(0)`` (the field ``0`` has coordinates :math:`\langle\mathtt{0},\mathtt{0}\rangle`) returns the integer set :math:`\{\mathtt{17},\mathtt{10}\}` (that is, the fields with coordinates :math:`\langle\mathtt{2},\mathtt{1}\rangle` and :math:`\langle\mathtt{1},\mathtt{2}\rangle`) and ``neighbors(27)`` (the field ``27`` has coordinates :math:`\langle\mathtt{3},\mathtt{3}\rangle`) returns the integer set :math:`\{\mathtt{17},\mathtt{33},\mathtt{10},\mathtt{42},\mathtt{12},\mathtt{44},\mathtt{21},\mathtt{37}\}` (that is, the fields with coordinates :math:`\langle\mathtt{2},\mathtt{1}\rangle`, :math:`\langle\mathtt{4},\mathtt{1}\rangle`, :math:`\langle\mathtt{1},\mathtt{2}\rangle`, :math:`\langle\mathtt{5},\mathtt{2}\rangle`, :math:`\langle\mathtt{1},\mathtt{4}\rangle`, :math:`\langle\mathtt{5},\mathtt{4}\rangle`, :math:`\langle\mathtt{2},\mathtt{5}\rangle`, and :math:`\langle\mathtt{4},\mathtt{5}\rangle`).

.. _case-studies:knights:fixing-the-first-move:

Fixing the first move.
''''''''''''''''''''''

Without loss of generality we fix that the knight’s first move goes to field ``f(1,2)``:


.. mpg-code:: knights:fix first move
   :direct:


Fixing the first move can be seen as breaking a symmetry in the model and hence reduces the amount of search needed for finding a knight’s tour.

.. _case-studies:knights:enforcing-a-hamiltonian-circuit:

Enforcing a Hamiltonian circuit.
''''''''''''''''''''''''''''''''

The ``circuit`` constraint (see :ref:`sec:m:integer:circuit` ) enforces that the tour of knight’s moves forms a Hamiltonian circuit:


.. mpg-code:: knights:Hamiltonian circuit
   :direct:


We request domain propagation for the ``circuit`` constraint by providing ``IPL_DOM`` as argument (see :ref:`sec:m:integer:ipl` ). (Of course, domain propagation for ``circuit`` does not achieve domain consistency, as the problem of finding Hamiltonian circuits is NP-complete  (p. 199; :cite:p:`GareyJohnson:79`) .) Intuitively, we want to have the strongest possible propagation available for ``circuit`` as it is the only constraint.

.. _case-studies:knights:branching:

Branching
---------

The really interesting aspect of solving the knight’s tour puzzle is to find a branching that works well. A classic approach is Warnsdorff’s heuristic  :cite:p:`Warnsdorff` : move the knight to a field that has the least number of further possible moves.

In terms of our model, Warnsdorff’s heuristic has of course no procedural notion of *moving* the knight! Instead, our branching finds a yet unassigned field :math:`i` on the board (a field whose successor is not known yet). Then, it first tries a value for :math:`\mathtt{succ}_i` that moves the knight to a field with the least number of further possible moves. That is, the branching first tries a value ``n`` for :math:`\mathtt{succ}_i` such that the domain size of :math:`\mathtt{succ}_\mathtt{n}` is smallest. If there are several such values, it just tries the smallest first (as it is most natural to implement).

.. _fig:c:knights:branching:

The brancher.
'''''''''''''

.. mpg-code:: knights:brancher
   :caption: A brancher for Warnsdorff’s heuristic


:ref:`fig:c:knights:branching` shows an outline of a branching and a brancher implementing Warnsdorff’s heuristic. The members of ``Warnsdorff`` are exactly the same as for the example brancher in :ref:`sec:b:started:nonemin:improved` : the view array ``x`` stores the knight’s moves, the ``mutable`` integer ``start`` points to the current unassigned view in ``x``, and the ``PosVal`` choice stores the position of the view and the value to be used for branching.

.. _case-studies:knights:status-computation:

Status computation.
'''''''''''''''''''

The ``status()`` function tries to find a yet unassigned view for branching in the view array ``x``. It starts inspecting the views from position ``start``. If it finds an assigned view, it moves ``start`` to the position in the view array as defined by the assigned view’s value. In other words, ``status()`` follows partially constructed knight’s tours. If ``status()`` finds an unassigned view, it returns ``true``:


.. mpg-code:: knights:status function
   :direct:


The number of attempts to find an unassigned view is limited by the number of views in the view array ``x``. If the limit is exceeded, all views are assigned and hence the ``status()`` function returns ``false``.

.. _case-studies:knights:choice-computation:

Choice computation.
'''''''''''''''''''

The ``choice()`` function implements the actual heuristic. It chooses the value of ``x[start]`` for branching that has the smallest domain size as follows:


.. mpg-code:: knights:choice function
   :direct:


As mentioned above, to keep the implementation simple, if there are several values that have smallest domain size, the first is chosen (and hence the smallest).

Note that the value ``UINT_MAX`` is larger than the size of any view domain. (``UINT_MAX`` (for the maximal value of an unsigned integer) is available as the program includes the header file.) Hence, it is guaranteed that the ``for``-loop will always choose a value from the domain of ``x[start]``. The choice returned is the typical implementation to store position and value, similar to the examples in :ref:`sec:b:started:nonemin:improved` .

.. _case-studies:knights:more-information:

More information
----------------

The model is also available as a Gecode example, see :api:`knights:KnightsCircuit` . The Gecode example also features a simple standard branching that can be compared to Warnsdorff’s branching and a naive model using reification instead of ``circuit`` (see :api:`knights:KnightsReified` ).

..
   Migration traceability for the migrated semantic constructs above.
