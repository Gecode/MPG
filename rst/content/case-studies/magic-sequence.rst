.. _chap:c:magicsequence:

Magic sequence
==============


This chapter shows how to use counting constraints for solving magic sequence puzzles.

.. _case-studies:magic-sequence:problem:

Problem
-------

The Magic Sequence puzzle ( `CSPLib problem 19 <https://www.csplib.org/Problems/prob019/>`__ , first introduced as a constraint problem in :cite:p:`Hentenryck:1989:0:Constraint` ) requires finding a sequence of integers :math:`x_0,\dots,x_{n-1}` such that for all :math:`0\leq
i< n`, the number :math:`i` occurs exactly :math:`x_i` times in the sequence. For example, a magic sequence of length :math:`n=8` is

.. math:: \langle 4, 2, 1, 0, 1, 0, 0, 0\rangle

.. _case-studies:magic-sequence:model:

Model
-----

The outline of the script for solving magic sequence puzzles is shown in :ref:`fig:c:magic_sequence` . It contains the integer variable array ``x`` (see :ref:`sec:m:integer:intvararray` ), which is initialized according to the problem specification.


.. _fig:c:magic_sequence:

.. mpg-code:: magic sequence
   :caption: A script for solving magic sequence puzzles
   :download:


.. _case-studies:magic-sequence:counting-constraints:

Counting constraints.
'''''''''''''''''''''

The problem can be modeled directly using one counting constraint (see :ref:`sec:m:integer:count` ) per variable. We will see later that there is a global constraint that combines all these individual counting constraints.


.. mpg-code:: magic sequence:counting constraints
   :direct:


.. _case-studies:magic-sequence:implied-linear-constraints:

Implied linear constraints.
'''''''''''''''''''''''''''

The model as described so far completely captures the problem. Therefore, given enough time, Gecode will return all its solutions and only the solutions. However, it is sometimes useful to post additional, *implied constraints*, which do not change the meaning of the model (they do not change the set of solutions), but which provide additional constraint propagation that results in a smaller search tree.

The two implied constraints that we will use for the magic sequence problem result from the fact that any magic sequence of length :math:`n` satisfies the following two equations:

.. math::

   \begin{aligned}
   \sum_{i=0}^{n-1}\mathtt{x}_i &= n &
   \sum_{i=0}^{n-1}{(i-1)\cdot \mathtt{x}_i} &=0
   \end{aligned}

The first equation is true because the sum of all occurrences, i.e. the overall number of items in the sequence, must be equal to the length of the sequence.

The second equation can be rewritten as

.. math::

   \sum_{i=0}^{n-1} i\cdot\mathtt{x}_i=
   \sum_{i=0}^{n-1}\mathtt{x}_i
   \iff
   \sum_{i=0}^{n-1} i\cdot\mathtt{x}_i=n

So it remains to be shown that :math:`\sum_{i=0}^{n-1}i\cdot \mathtt{x}_i` is also equal to the length of the sequence. This follows from the fact that :math:`\mathtt{x}_i` is the number of times :math:`i` occurs in the sequence, so :math:`i\cdot \mathtt{x}_i` is the number of positions occupied by the sequence elements that are equal to :math:`i`, and the sum over those must be equal to the length of the sequence.

The two equations translate easily into linear constraints (see :ref:`sec:m:integer:linear` ), using integer argument arrays of type ``IntArgs`` (see :ref:`sec:m:integer:args` ) to supply coefficients.


.. mpg-code:: magic sequence:implied constraints
   :direct:


You can do your own experiments, comparing runtime and search tree size of the model with and without implied constraints.

.. _case-studies:magic-sequence:branching:

Branching.
''''''''''

For large sequences, many variables in the sequence will be :math:`0` because the overall sum is only :math:`n` (see previous paragraph on implied constraints). Therefore, :math:`\mathtt{x}_0` should take a large value. We simply branch in the given order of the variables, starting with the largest values.


.. mpg-code:: magic sequence:branching
   :direct:


.. _case-studies:magic-sequence:global-counting-constraints:

Global counting constraints.
''''''''''''''''''''''''''''

The global counting constraint (also known as global cardinality constraint, see :ref:`sec:m:integer:count` ) can express the combination of all the individual counting constraints, and yields stronger propagation. It also includes the propagation of the first of the two implied linear constraints. So, as an alternative to the :math:`n` counting constraints above, we can use the code in :ref:`fig:c:magic_sequence_gcc` .

.. _case-studies:magic-sequence:more-information:

More information
----------------

The magic sequence puzzle is also included as a Gecode example, see :api:`magic-sequence` . The example contains both the model using individual counting constraints and the one using a single global counting constraint.


.. _fig:c:magic_sequence_gcc:

.. mpg-code:: magic sequence gcc
   :caption: Magic sequence puzzles with a global counting constraint
   :download:

..
   Migration traceability for the migrated semantic constructs above.

.. mpg-covered: caption:docs/src/chapters/case-studies/c-magic-sequence.tex.in:25:fig:c:magic_sequence
.. mpg-covered: literal-projection:docs/src/chapters/case-studies/c-magic-sequence.tex.in:26:magic sequence
.. mpg-covered: literal-projection:docs/src/chapters/case-studies/c-magic-sequence.tex.in:38:magic sequence:counting constraints
.. mpg-covered: literal-projection:docs/src/chapters/case-studies/c-magic-sequence.tex.in:73:magic sequence:implied constraints
.. mpg-covered: literal-projection:docs/src/chapters/case-studies/c-magic-sequence.tex.in:84:magic sequence:branching
.. mpg-covered: caption:docs/src/chapters/case-studies/c-magic-sequence.tex.in:103:fig:c:magic_sequence_gcc
.. mpg-covered: literal-projection:docs/src/chapters/case-studies/c-magic-sequence.tex.in:104:magic sequence gcc
