.. _chap:c:kakuro:

Kakuro
======


This chapter studies Kakuro puzzles, a variant of the well-known Sudoku puzzles. Two models are presented: a first and obvious model that suffers from too little propagation to be feasible. This is followed by a model that employs user-defined constraints implemented as ``extensional`` constraints using tuple set specifications. Interestingly, the tuple set specifications are computed by solving a simple constraint problem.

.. _sec:c:kakuro:problem:

Problem
-------


.. mpg-figure:: A Kakuro puzzle
   :name: fig:c:kakuro:board

   .. only:: html

      .. image:: /figures/fig-c-kakuro-board.svg
         :alt: A Kakuro puzzle

   .. only:: latex

      .. image:: /figures/pdf/fig-c-kakuro-board.pdf
         :alt: A Kakuro puzzle


Solving a Kakuro puzzle (see :numref:`fig:c:kakuro:board` for an example) amounts to finding digits between 1 and 9 for the non-hint fields on a board. A hint field can specify a *vertical hint* and/or a *horizontal hint*:

- A vertical hint contains a number :math:`s` above the diagonal in the hint field. It requires that all digits on the fields extending from the field left of the hint up to the next hint field or to the end of the row are pairwise distinct and sum up to the value :math:`s`.

- A horizontal hint contains a number :math:`s` below the diagonal in the hint field. The requirements are analogous.

The number contained in a hint is called its *value* and the number of fields constrained by a hint is called its *length*.


.. mpg-figure:: Solution for Kakuro puzzle from :numref:`fig:c:kakuro:board`
   :name: fig:c:kakuro:solution

   .. only:: html

      .. image:: /figures/fig-c-kakuro-solution.svg
         :alt: Solution for the example Kakuro puzzle

   .. only:: latex

      .. image:: /figures/pdf/fig-c-kakuro-solution.pdf
         :alt: Solution for the example Kakuro puzzle


The solution for the Kakuro puzzle from :numref:`fig:c:kakuro:board` is shown in :numref:`fig:c:kakuro:solution` . Kakuro puzzles are always designed (at least meant to be) to have a unique solution.

.. _sec:c:kakuro:model:naive:

A naive model
-------------


.. _fig:c:kakuro:script:naive:

.. mpg-code:: kakuro naive
   :caption: A naive script and board specification for solving Kakuro puzzles
   :download:

.. mpg-code:: kakuro naive:board specification
   :direct:


A script for the Kakuro model is shown in :ref:`fig:c:kakuro:script:naive` . The script stores the width (``w``) and height (``h``) of the board. The fields are stored in an integer variable array ``f`` which is initialized to have :math:`\mathtt{w}\cdot\mathtt{h}` elements. Note that none of the fields is initialized in the constructor of ``Kakuro``; their initialization is discussed below.

.. _case-studies:kakuro:board-specification:

Board specification.
''''''''''''''''''''

The specification of the Kakuro board, as shown in :ref:`fig:c:kakuro:script:naive` , stores width and height of the board, followed by a specification of the hints. The hints are provided in two groups: first vertical hints, then horizontal hints, separated by the integer ``-1``. A hint is described by its coordinates on the board, followed by its length and value. Note that the specification assumes that the field with coordinate :math:`\langle 0,0\rangle` is in the left upper corner.

.. _case-studies:kakuro:initializing-fields:

Initializing fields.
''''''''''''''''''''

All fields are initialized to a single shared integer variable ``black`` that is assigned to zero:


.. mpg-code:: kakuro naive:field initialization
   :direct:


Only if a field is actually used by a hint, the field will be initialized to an integer variable taking digit values by the following ``init()`` function:


.. mpg-code:: kakuro naive:init function
   :direct:


The test whether the minimum of variable ``x`` equals zero is true, if and only if ``x`` still refers to the variable ``black``. In this case, a new variable is created with non-zero digits as variable domain. As ``x`` is passed by reference, assigning ``x`` to the newly created variable also assigns the corresponding field on the board to the newly created variable. This guarantees that a new variable is created at most once for each field.

.. _case-studies:kakuro:posting-hint-constraints:

Posting hint constraints.
'''''''''''''''''''''''''

Posting hint constraints is done best by using a matrix interface ``b`` (see :ref:`sec:m:minimodel:matrix` ) to the fields in ``f``. The specification of the hints will be accessed by the variable ``k``, where the dimension of the board has already been skipped:


.. mpg-code:: kakuro naive:setup
   :direct:


Processing the vertical hints is straightforward. After retrieving the coordinates ``x`` and ``y``, the length ``n``, and the value ``s`` for a hint from the board specification, the variables covered by the hint are collected in the integer variable argument array (see :ref:`sec:m:integer:args` ) ``col``. The constraint for the hint on the collected variables is posted by the member function ``hint()``:


.. mpg-code:: kakuro naive:process vertical hints
   :direct:


The ``hint()`` function must constrain that all variables are distinct (using a ``distinct`` constraint) and that they sum up to the value of the hint (using a ``linear`` constraint). To achieve strong propagation, we want to use domain propagation for both ``distinct`` and ``linear``. However, the complexity of domain propagation for ``linear`` is exponential, hence it is a good idea to avoid posting ``linear`` constraints as much a possible.

Consider a hint of length :math:`9`. Then obviously, the single possible value of the hint is :math:`\sum_{i=1}^{9} i=9(9+1)/2` and hence no ``linear`` constraint needs to be posted. Now consider a hint of length :math:`8` with value :math:`s`. Then, the fields covered by the hint take on all but one digit. That is, all fields must be different from :math:`\sum_{i=1}^9 i -s = 9(9+1)/2 -s`. Taking these two observations into account, the constraints for a hint can be posted as follows, where the value ``IPL_DOM`` requests domain propagation (see :ref:`sec:m:integer:ipl` ):


.. mpg-code:: kakuro naive:posting hint constraints
   :direct:


Note that there are other special cases where no ``linear`` constraint needs to be posted, for example if for a hint of length :math:`n` and value :math:`s` it holds that :math:`\sum_{i=1}^n i=s` (that is, only digits from :math:`1` to :math:`n` are possible). See :ref:`sec:c:kakuro:info` for more information.

Vertical hints are of course analogous and are hence omitted.

.. _case-studies:kakuro:branching:

Branching.
''''''''''

We choose a branching that selects the variable where the quotient of AFC and domain size is largest smallest (see :ref:`sec:m:branch:int` ). Values are tried by interval bisection:


.. mpg-code:: kakuro naive:branching
   :direct:


.. _case-studies:kakuro:why-the-model-is-poor:

Why the model is poor.
''''''''''''''''''''''

.. mpg-figure:: Propagation for the Kakuro puzzle
   :name: fig:c:kakuro:prop

   .. only:: html

      .. image:: /figures/fig-c-kakuro-prop.svg
         :alt: Propagation for the Kakuro puzzle

   .. only:: latex

      .. image:: /figures/pdf/fig-c-kakuro-prop.pdf
         :alt: Propagation for the Kakuro puzzle


When running the script, solving even the tiny board of :numref:`fig:c:kakuro:board` requires :math:`19` search nodes. There exist commercially available boards with thousands of hints, which are of course completely out of reach with the naive model. :numref:`fig:c:kakuro:prop` shows the possible digits for each field after performing propagation for the Kakuro script but before any search. Consider the two green fields for the hint of length :math:`2` and value :math:`4`. The only possible combination for the two fields is :math:`\langle 3,1\rangle`. However, propagation does not prune the value :math:`2` for both fields. The reason is that a ``hint`` constraint is decomposed into a ``distinct`` constraint and into a ``linear`` constraint and neither constraint by itself warrants more pruning than shown.

.. _sec:c:kakuro:model:work:

A working model
---------------


The naive model from the previous section suffers from the fact that ``hint`` constraints are decomposed into a ``distinct`` constraint and a ``linear`` constraint. One remedy would be to implement a dedicated propagator for a ``distinctlinear`` constraint. This is impractical: too complicated and too much effort for such a specialized constraint.

.. _case-studies:kakuro:model-idea:

Model idea.
'''''''''''

This section implements ``distinctlinear`` constraints as ``extensional`` constraints using tuple sets as specification of the possible solutions of ``distinctlinear`` constraints. For example, for a hint of length :math:`3` and value :math:`8`, the possible solutions for the corresponding ``distinctlinear`` constraint are:

.. math::

   \begin{array}{c@{\quad}c@{\quad}c@{\quad}c}
   \langle 1,2,5 \rangle &
   \langle 1,3,4 \rangle &
   \langle 1,4,3 \rangle &
   \langle 1,5,2 \rangle \\
   \langle 2,1,5 \rangle &
   \langle 2,5,1 \rangle &
   \langle 3,1,4 \rangle &
   \langle 3,4,1 \rangle \\
   \langle 4,1,3 \rangle &
   \langle 4,3,1 \rangle &
   \langle 5,1,2 \rangle &
   \langle 5,2,1 \rangle
   \end{array}

The model needs a method to compute all solutions of a ``distinctlinear`` constraint. To simplify matters, we are going to compute all solutions of a ``distinctlinear`` constraint by computing all solutions of a trivial constraint problem: the decomposition of a ``distinctlinear`` constraint into a ``distinct`` and ``linear`` constraint.


.. _fig:c:kakuro:script:work:

.. mpg-code:: kakuro
   :caption: A working script for solving Kakuro puzzles
   :download:


:ref:`fig:c:kakuro:script:work` shows the outline for a working script for solving Kakuro puzzles. The class ``DistinctLinear`` defines the script used for computing all solutions of a ``distinctlinear`` constraint and the function ``distinctlinear()`` serves as constraint post function. Apart from how ``hint`` constraints are posted, the ``Kakuro`` script is the same as in the previous section.

.. _case-studies:kakuro:computing-distinct-linear-solutions:

Computing distinct linear solutions.
''''''''''''''''''''''''''''''''''''

As mentioned, the script for ``DistinctLinear`` just posts a ``linear`` and ``distinct`` constraint for ``n`` variables and value ``s``. As the search space of the problem is small anyway, we neither need strong propagation for ``distinct`` and ``linear`` nor do we need a clever branching:


.. mpg-code:: kakuro:distinct linear script
   :direct:


When solving the ``DistinctLinear`` script, we need its solutions as integer argument arrays for computing a tuple set. The ``solution()`` member function of ``DistinctLinear`` returns an integer argument array for a solution as follows:


.. mpg-code:: kakuro:returning a solution
   :direct:


.. _case-studies:kakuro:posting-distinctlinear-constraints:

Posting ``distinctlinear`` constraints.
'''''''''''''''''''''''''''''''''''''''

The search engine (see :ref:`sec:m:search:simple` ) for computing all solutions of a ``DistinctLinear`` script is initialized as follows:


.. mpg-code:: kakuro:set up search engine
   :direct:


Computing a tuple set (see :ref:`sec:m:integer:extensional` ) for all solutions of a ``distinctlinear`` constraints is straightforward:


.. mpg-code:: kakuro:compute tuple set
   :direct:


Note that after all solutions have been added to the tuple set ``ts``, it must be finalized before it can be used by an ``extensional`` constraint (see :ref:`sec:m:integer:extensional` ).

Finally, posting the ``extensional`` constraint using the tuple set ``ts`` is as to be expected:


.. mpg-code:: kakuro:post extensional constraint
   :direct:



.. _case-studies:kakuro:posting-hint-constraints-2:

Posting hint constraints.
'''''''''''''''''''''''''

Posting a ``hint`` constraint follows a similar line of reasoning as in the previous section. If the length of a hint is :math:`0`, no constraint needs to be posted (hints of length :math:`0` are black fields without hints). If the length is :math:`1`, the single variable is constrained to ``s`` directly. For lengths :math:`8` and :math:`9`, ``distinct`` is used as it achieves the same propagation as ``distinctlinear``. Note that the case for length :math:`8` continues (as it does not have a ``break`` statement) with the case for length :math:`9` and hence also posts a ``distinct`` constraint. In all other cases, ``distinctlinear`` is used:


.. mpg-code:: kakuro:posting hint constraints
   :direct:


There is a further important optimization which we will not show (but see :ref:`sec:c:kakuro:info` ). Each time ``distinctlinear`` is called, it computes a new tuple set, even though the tuple set is exactly the same for all hints of equal length and value. To guarantee that the same tuple set is computed at most once, one could cache tuple sets: if a tuple set for a certain length and value has already been computed earlier, it is not computed again but taken from a cache (where it had been stored when it was computed for the first time).

.. _case-studies:kakuro:this-model-works:

This model works.
'''''''''''''''''

For the example puzzle, propagation alone is sufficient to solve the puzzle. Even puzzles with thousands of hints are solved without search in a fraction of a second (including computing the tuple sets, provided they are cached as sketched above).

.. _sec:c:kakuro:info:

More information
----------------


Kakuro puzzles with some more examples are available as a Gecode example, see :api:`kakuro` . In particular, the model caches tuple sets such that for each type of hint its corresponding tuple set is computed at most once as discussed in :ref:`sec:c:kakuro:model:work` . Furthermore, the example exploits further special cases where posting a ``distinct`` constraint rather than a complete ``hint`` constraint is sufficient as discussed in :ref:`sec:c:kakuro:model:naive` .

More constraint-based techniques for solving Kakuro puzzles are discussed in  :cite:p:`HelmutKakuro` .

..
   Migration traceability for the migrated semantic constructs above.

.. mpg-covered: caption:docs/src/chapters/case-studies/c-kakuro.tex.in:36:fig:c:kakuro:board
.. mpg-covered: caption:docs/src/chapters/case-studies/c-kakuro.tex.in:68:fig:c:kakuro:solution
.. mpg-covered: caption:docs/src/chapters/case-studies/c-kakuro.tex.in:105:fig:c:kakuro:script:naive
.. mpg-covered: literal-projection:docs/src/chapters/case-studies/c-kakuro.tex.in:106:kakuro naive
.. mpg-covered: literal-projection:docs/src/chapters/case-studies/c-kakuro.tex.in:108:kakuro naive:board specification
.. mpg-covered: literal-projection:docs/src/chapters/case-studies/c-kakuro.tex.in:136:kakuro naive:field initialization
.. mpg-covered: literal-projection:docs/src/chapters/case-studies/c-kakuro.tex.in:141:kakuro naive:init function
.. mpg-covered: literal-projection:docs/src/chapters/case-studies/c-kakuro.tex.in:159:kakuro naive:setup
.. mpg-covered: literal-projection:docs/src/chapters/case-studies/c-kakuro.tex.in:168:kakuro naive:process vertical hints
.. mpg-covered: literal-projection:docs/src/chapters/case-studies/c-kakuro.tex.in:188:kakuro naive:posting hint constraints
.. mpg-covered: literal-projection:docs/src/chapters/case-studies/c-kakuro.tex.in:204:kakuro naive:branching
.. mpg-covered: caption:docs/src/chapters/case-studies/c-kakuro.tex.in:209:fig:c:kakuro:prop
.. mpg-covered: caption:docs/src/chapters/case-studies/c-kakuro.tex.in:295:fig:c:kakuro:script:work
.. mpg-covered: literal-projection:docs/src/chapters/case-studies/c-kakuro.tex.in:296:kakuro
.. mpg-covered: literal-projection:docs/src/chapters/case-studies/c-kakuro.tex.in:316:kakuro:distinct linear script
.. mpg-covered: literal-projection:docs/src/chapters/case-studies/c-kakuro.tex.in:322:kakuro:returning a solution
.. mpg-covered: literal-projection:docs/src/chapters/case-studies/c-kakuro.tex.in:329:kakuro:set up search engine
.. mpg-covered: literal-projection:docs/src/chapters/case-studies/c-kakuro.tex.in:334:kakuro:compute tuple set
.. mpg-covered: literal-projection:docs/src/chapters/case-studies/c-kakuro.tex.in:342:kakuro:post extensional constraint
.. mpg-covered: literal-projection:docs/src/chapters/case-studies/c-kakuro.tex.in:356:kakuro:posting hint constraints
