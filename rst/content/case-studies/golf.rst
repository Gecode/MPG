.. _chap:c:golf:

Social golfers
==============


This chapter presents a case study on modeling problems using set variables and constraints.

.. _sec:c:golf:problem:

Problem
-------


The social golfers’ problem ( `CSPLib problem 10 <https://www.csplib.org/Problems/prob010/>`__ ) requires finding a schedule for a golf tournament. There are :math:`g\cdot s` golfers who want to play a tournament in :math:`g` groups of :math:`s` golfers each over :math:`w` weeks, such that no two golfers play against each other more than once during the tournament.

Here is a solution for the instance :math:`w=4`, :math:`g=3`, and :math:`s=3`, where the players are numbered from 0 to 8:

.. container:: center

   ======== ========= = = ========= = = ========= = =
   \        *Group 0*     *Group 1*     *Group 2*
   ======== ========= = = ========= = = ========= = =
   *Week 0* 0         1 2 3         4 5 6         7 8
   *Week 1* 0         3 6 1         4 7 2         5 8
   *Week 2* 0         4 8 1         5 6 2         3 7
   *Week 3* 0         5 7 1         3 8 2         4 6
   ======== ========= = = ========= = = ========= = =

.. _sec:c:golf:model:

Model
-----


The model for the social golfers’ problem closely follows the above problem description. Its outline is shown in :ref:`fig:c:golf:script` . The script defines an array of set variables ``groups`` of size :math:`\mathtt g\cdot \mathtt w`, where each group can contain the players :math:`0\dots \mathtt g\cdot
\mathtt s-1` and has cardinality :math:`\mathtt s` (see :ref:`sec:m:set:var` ).

The script also defines a matrix ``schedule`` with :math:`g` columns and :math:`w` rows on top of the variable array, such that ``schedule(i,j)`` is the set of members of group :math:`\mathtt i` in week :math:`\mathtt j`.

The constraints are straightforward. For each week, the union of all groups must be disjoint and contain all players. This can be expressed directly using a disjoint union constraint (see :ref:`sec:m:minimodel:exprrel` ) on the rows of the ``schedule``:


.. mpg-code:: golf:groups in a week
   :direct:


Each group can have at most one player in common with any other group. This can be expressed by a constraint that states that the cardinality of the intersection between any two groups must be at most :math:`1`:


.. mpg-code:: golf:overlap between groups
   :direct:


.. _fig:c:golf:script:

.. mpg-code:: golf
   :caption: A script for the social golfers’ problem
   :download:


.. _case-studies:golf:symmetry-breaking:

Symmetry breaking.
''''''''''''''''''

Using set variables to model the groups already avoids introducing symmetry among the players in a group. For example, if we had modeled each group as :math:`s` integer variables, any permutation of these variables would produce an equivalent solution.

But there are more symmetries in this problem, and some of them can be avoided easily by introducing additional *symmetry breaking constraints*.

Within a week, the order of the groups is irrelevant. Therefore, we can impose a static order requiring that all minimal elements of each group are ordered increasingly (see :ref:`m:set:set_int` for the minimal element constraint, :ref:`sec:m:minimodel:exprrel` for the MiniModel support, and :ref:`sec:m:integer:rel:int` for ordering integer variables):


.. mpg-code:: golf:break group symmetry
   :direct:


Similarly to the group symmetry, the order of the weeks is irrelevant. Again, the symmetry can be broken by imposing an order on the group elements. The previous constraint made sure that player ``0`` will always be in ``schedule(0,j)`` for any week ``j``. So imposing an order on the second smallest element of ``schedule(0,j)`` will do the trick:


.. mpg-code:: golf:break week symmetry
   :direct:


Finally, the players can be permuted arbitrarily. For example, swapping the numbers :math:`2` and :math:`6` in the initial example produces a symmetric solution:

.. container:: center

   ======== ========= = = ========= = = ========= = =
   \        *Group 0*     *Group 1*     *Group 2*
   ======== ========= = = ========= = = ========= = =
   *Week 0* 0         1 6 3         4 5 2         7 8
   *Week 1* 0         3 2 1         4 7 6         5 8
   *Week 2* 0         4 8 1         5 2 6         3 7
   *Week 3* 0         5 7 1         3 8 6         4 2
   ======== ========= = = ========= = = ========= = =

This symmetry can be broken using the ``precede`` constraint (see :ref:`sec:m:set:precede` ):


.. mpg-code:: golf:break player symmetry
   :direct:


It enforces for any pair of players :math:`s` and :math:`t` that :math:`t` can only appear in a group without :math:`s` if there is an earlier group where :math:`s` appears without :math:`t`. This establishes an order that breaks the value symmetry between the players. In the example above, the constraint rules out that :math:`6` appears in group 0, week 0, because that would require :math:`2` to appear in an earlier group. The only solution that remains after symmetry breaking is the one in the initial table in :ref:`sec:c:golf:problem` .

Note that these symmetry breaking constraints do not necessariyl break all symmetries of the problem completely. We mainly discussed them as additional examples of modeling with set variables and constraints.

.. _sec:c:golf:info:

More information
----------------


The case study is also available as a Gecode example, see :api:`golf` . You can find a discussion of the symmetry breaking constraints presented here and a number of additional implied constraints in  :cite:p:`Barnier:2005:KirkmansSchoolgirlProblem` .

..
   Migration traceability for the migrated semantic constructs above.

.. mpg-covered: table:docs/src/chapters/case-studies/c-golf.tex.in:18:tabular@docs/src/chapters/case-studies/c-golf.tex.in:18
.. mpg-covered: literal-projection:docs/src/chapters/case-studies/c-golf.tex.in:48:golf:groups in a week
.. mpg-covered: literal-projection:docs/src/chapters/case-studies/c-golf.tex.in:53:golf:overlap between groups
.. mpg-covered: caption:docs/src/chapters/case-studies/c-golf.tex.in:55:fig:c:golf:script
.. mpg-covered: literal-projection:docs/src/chapters/case-studies/c-golf.tex.in:56:golf
.. mpg-covered: literal-projection:docs/src/chapters/case-studies/c-golf.tex.in:73:golf:break group symmetry
.. mpg-covered: literal-projection:docs/src/chapters/case-studies/c-golf.tex.in:81:golf:break week symmetry
.. mpg-covered: table:docs/src/chapters/case-studies/c-golf.tex.in:85:tabular@docs/src/chapters/case-studies/c-golf.tex.in:85
.. mpg-covered: literal-projection:docs/src/chapters/case-studies/c-golf.tex.in:97:golf:break player symmetry
