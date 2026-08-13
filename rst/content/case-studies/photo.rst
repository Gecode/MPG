.. _chap:c:photo:

Photo alignment
===============


This chapter shows how to use reified constraints for solving an overconstrained problem.

.. _case-studies:photo:problem:

Problem
-------

Betty, Chris, Donald, Fred, Gary, Mary, Paul, Peter, and Susan want to align in a row for taking a photo. They have the following preferences:

#. Betty wants to stand next to Donald, Gary, and Peter.

#. Chris wants to stand next to Gary and Susan.

#. Donald wants to stand next to Fred and Gary.

#. Fred wants to stand next to Betty and Gary.

#. Gary wants to stand next to Mary and Betty.

#. Mary wants to stand next to Betty and Susan.

#. Paul wants to stand next to Donald and Peter.

#. Peter wants to stand next to Susan and Paul.

These preferences are obviously not satisfiable all at once (e.g., Betty cannot possibly stand next to three people at once). The problem is *overconstrained*. To solve an overconstrained problem, we turn it into an optimization problem: The task is to find an alignment that violates as few preferences as possible.

.. _case-studies:photo:model:

Model
-----

We model the photo alignment as an array of integer variables ``pos`` such that ``pos[p]`` represents the position of person ``p`` in the final left-to-right order. The outline of a script for this problem is shown in :ref:`fig:c:photo:script` .

The ``cost()`` function as required by the class ``MinimizeScript`` (see :ref:`sec:m:driver:script` ) just returns the number of violations.


.. _fig:c:photo:script:

.. mpg-code:: photo
   :caption: A script for the photo alignment problem
   :download:


There are only two hard constraints for this model: no person can be in more than one place, and no two persons can stand in the same place. The first constraint is enforced automatically by the choice of variables, as each ``pos`` variable represents the unique position of a person (see also :ref:`tip:c:warehouses:varchoice` ). For the second constraint, the variables in the ``pos`` array must be pairwise distinct (see :ref:`sec:m:integer:distinct` ):


.. mpg-code:: photo:constrain positions
   :direct:


We choose the bounds consistent variant of ``distinct`` (by giving the extra argument ``IPL_BND``, see :ref:`sec:m:integer:ipl` ) as also the other propagators perform only bounds reasoning.

The remaining constraints implement the preferences and turn them into a measure of *violation*, which expresses how many preferences are not fulfilled in a solution. A preference :math:`(i,j)` is not fulfilled if the distance between the positions of person :math:`i` and person :math:`j` is greater than one. This can be implemented using a linear constraint, an absolute value constraint, and a reified constraint for each preference, as well as one linear constraint that constrains the sum of the violations:


.. mpg-code:: photo without modeling support
   :direct:
   :download:


Using the MiniModel library (see :ref:`fig:m:minimodel:bool` and :ref:`sec:m:minimodel:exprrel` ) yields more compact and readable code:


.. mpg-code:: photo:compute violations
   :direct:


We can observe that this problem has a symmetry, as reversing a solution yields again a solution. Symmetric solutions like this can be ruled out by arbitrarily picking two persons, and always placing one somewhere to the left of the other. For example, let us always place Betty somewhere to the left of Chris:


.. mpg-code:: photo:symmetry breaking
   :direct:


.. _case-studies:photo:more-information:

More information
----------------

This case study is also available as a Gecode example, see :api:`photo` .

..
   Migration traceability for the migrated semantic constructs above.

.. mpg-covered: caption:docs/src/chapters/case-studies/c-photo.tex.in:44:fig:c:photo:script
.. mpg-covered: literal-projection:docs/src/chapters/case-studies/c-photo.tex.in:45:photo
.. mpg-covered: literal-projection:docs/src/chapters/case-studies/c-photo.tex.in:57:photo:constrain positions
.. mpg-covered: literal-projection:docs/src/chapters/case-studies/c-photo.tex.in:70:photo without modeling support
.. mpg-covered: literal-projection:docs/src/chapters/case-studies/c-photo.tex.in:75:photo:compute violations
.. mpg-covered: literal-projection:docs/src/chapters/case-studies/c-photo.tex.in:80:photo:symmetry breaking
