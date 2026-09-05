.. _chap:c:nonogram:

Nonogram
========


This chapter shows how to use regular expressions and extensional constraints for solving nonogram puzzles.

.. _case-studies:nonogram:problem:

Problem
-------

Nonograms ( `CSPLib problem 12 <https://www.csplib.org/Problems/prob012/>`__ ) are popular puzzles in which the puzzler shades squares in a matrix. Each instance of the puzzle has constraints on the rows and columns of the matrix, specifying the number and length of the groups of consecutive marks in that row or column. For example, a row that in the solution has the marks

.. math:: \square\square\blacksquare\blacksquare\square\square\blacksquare\blacksquare\blacksquare\square\blacksquare\square\square\square

has the *hint* ``2 3 1``, indicating that there are three separate groups of marks, with lengths 2, 3, and 1. Given two groups of marks, there must be at least one empty square in between. An example nonogram is given in :numref:`fig:c:nonogram:ex` and its solution is shown in :numref:`fig:c:nonogram:ex-sol` . The general nonogram problem is NP-complete, as shown in :cite:p:`Ueda:1996` .


.. mpg-figure:: Example nonogram puzzle
   :name: fig:c:nonogram:ex
   :class: mpg-figure-compact

   .. only:: html

      .. image:: /figures/fig-c-nonogram-ex.svg
         :alt: Example nonogram puzzle

   .. only:: latex

      .. image:: /figures/pdf/fig-c-nonogram-ex.pdf
         :alt: Example nonogram puzzle


.. mpg-figure:: Solution to the example puzzle
   :name: fig:c:nonogram:ex-sol
   :class: mpg-figure-compact

   .. only:: html

      .. image:: /figures/fig-c-nonogram-ex-sol.svg
         :alt: Solution to the example puzzle

   .. only:: latex

      .. image:: /figures/pdf/fig-c-nonogram-ex-sol.pdf
         :alt: Solution to the example puzzle


.. _case-studies:nonogram:model:

Model
-----

The model follows naturally from the constraints of the problem. The variables needed are a matrix :math:`x_{ij}` of ``0``-``1`` variables, representing the squares to shade. For the hint ``2 3 1`` on row :math:`i`, we post the following ``extensional`` constraint (see :ref:`sec:m:integer:extensional` ):

.. math:: \mathtt{extensional}(x_{i\bullet}, 0^*1^20^+1^30^+10^*)

The regular expression starts and ends with zero or more zeroes. Each group is represented by as many ones as the group length. In between the groups, one or more zeroes are placed. Using this construction, we get one constraint per row and column of the matrix. The outline of the script is shown in :ref:`fig:c:nonogram` .


.. _fig:c:nonogram:

.. mpg-code:: nonogram
   :caption: A script for solving nonogram puzzles
   :download:


.. _case-studies:nonogram:puzzle-specification:

Puzzle specification.
'''''''''''''''''''''

The puzzle is specified by an array of integers. The first two integers specify the width and the height of the grid. These are followed first by the column and then the row hints. Each hint specifies the number of groups and the length of each group. For example, the hint used as an example above is specified as ``3, 2, 3, 1``. The puzzle from :numref:`fig:c:nonogram:ex` is written as follows.


.. mpg-code:: nonogram:puzzle
   :direct:


.. _case-studies:nonogram:line-function:

Line function.
''''''''''''''

For the hint that starts at ``p`` (that is, ``p`` points to a position in the array of integers ``spec[]`` where a hint starts), the following code constructs a regular expression (see :ref:`sec:m:minimodel:reg` ) that matches that hint.


.. mpg-code:: nonogram:line function
   :direct:


The variables ``r0`` and ``r1`` represent the constants ``0`` and ``1`` (this is a slight optimization to construct a regular expression for the constants ``0`` and ``1`` just once). The variables ``border`` and ``separator`` represent sequences of zeroes at the borders and between marks. The loop adds all hints (as repeated ``r1``\ s) to the ``result`` expression with ``separator``\ s in between. Note that if the hint is just ``0`` (representing an empty line with no mark), then the ``result`` will be just the same as a ``border+border``, which is :math:`\mathtt{0}^*\mathtt{0}^*=\mathtt{0}^*`.

.. _case-studies:nonogram:constraints:

Constraints.
''''''''''''

Given the ``line()`` function, posting the appropriate constraints is as follows. The pointer ``p`` is initialized to point to the first hint:


.. mpg-code:: nonogram:intialize hint pointer
   :direct:


Two loops go through all the hints, get the regular expression for the line, and post the constraints for the appropriate variables. First, the column constraints are posted:


.. mpg-code:: nonogram:column constraints
   :direct:


followed by the row constraints:


.. mpg-code:: nonogram:row constraints
   :direct:


.. _case-studies:nonogram:branching:

Branching.
''''''''''

Choosing a branching for nonograms is not obvious. For many nonogram puzzles, using an AFC-based branching (see :ref:`sec:m:branch:int` ) is a good idea:


.. mpg-code:: nonogram:branching
   :direct:


The choice to use ``INT_VAL_MAX()`` is because most puzzles will have fewer marks than empty spaces. For the example puzzle from :numref:`fig:c:nonogram:ex` , propagation alone solves the puzzle. To solve really hard puzzles, a custom branching may be needed.

.. _case-studies:nonogram:more-information:

More information
----------------

The nonogram puzzle is also included as a Gecode example, see :api:`nonogram` . The example in particular features several grids to try the model on.

Despite its simplicity, the program for solving nonograms works amazingly well. Extensive information on nonogram puzzles and a comparison of different nonogram solvers (including the model described in this chapter) is `Survey of Paint-by-Number Puzzle Solvers <http://webpbn.com/survey/>`__ .

..
   Migration traceability for the migrated semantic constructs above.
