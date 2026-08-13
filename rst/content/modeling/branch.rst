.. _chap:m:branch:


.. _modeling:m-branch:branching:

Branching
=========

This chapter discusses how *branching* is used for solving Gecode models. Branching defines the shape of the search tree. Exploration defines a strategy how to explore parts of the search tree and is discussed in :ref:`chap:m:search`.

.. _modeling:m-branch:overview:

.. rubric:: Overview.

:ref:`sec:m:branch:basics` explains the basics of Gecode’s predefined branchings. An overview of available branchings for integer and Boolean variables is provided in :ref:`sec:m:branch:int`, for set variables in :ref:`sec:m:branch:set`, and for float variables in :ref:`sec:m:branch:float`. These sections belong to the basic reading material of :ref:`part:m`.

Advanced topics for branchings are discussed in the remaining sections: local versus shared variable selection , random selection , user-defined variable and value selection, tie-breaking , dynamic symmetry breaking , branch filter functions , variable-value print functions , assigning variables , and executing code between branchers .

.. container:: convention

   Note that the same conventions hold as in :ref:`chap:m:int`.

.. _sec:m:branch:basics:


.. _modeling:m-branch:branching-basics:

Branching basics
----------------

Gecode offers predefined *variable-value branching*: when calling ``branch()`` to post a branching, the third argument defines which variable is selected for branching, whereas the fourth argument defines which values are selected for branching.

For example, for an array of integer or Boolean variables ``x`` the following call to branch

.. mpg-code:: snippet:m-branch:sec:m:branch:basics:code:1
   :direct:


selects a variable :math:`y` with the smallest minimum value (in case of ties, the first such variable in ``x`` is selected) and creates a choice with two alternatives :math:`y\leq n` and :math:`y>n` where

.. math:: n=\left\lfloor\frac{\min(y)+\max(y)}{2}\right\rfloor

The posted brancher assigns all variables and then ceases to exist. If more branchers exist, search continues with the next brancher. Search *commits* a brancher to alternatives during search.

The ``branch()`` function also accepts a branch filter function and a variable-value print function as optional arguments, see :ref:`sec:m:branch:filter` and :ref:`sec:m:branch:print` for details.

.. _modeling:m-branch:several-branchers:

.. rubric:: Several branchers.

A space in Gecode can have *several* branchers posted on behalf of a *branching* that are executed in order of creation. Assume that in

.. mpg-code:: snippet:m-branch:sec:m:branch:basics:code:2
   :direct:


both calls to ``branch()`` create a brancher. Search branches first on the variables ``x`` and then on the variables ``y``. Here, it does not matter whether propagators are created in between the creation of branchers.

.. _modeling:m-branch:branching-on-single-variables:

.. rubric:: Branching on single variables.

In addition to branching on an array of variables, Gecode also supports branching on a single variable.

For example, if ``x`` is an integer variable of type ``IntVar``, then

.. mpg-code:: snippet:m-branch:sec:m:branch:basics:code:3
   :direct:


branches on the single variable ``x`` by first trying the smallest value of ``x``.

Assume that ``x`` is an array of integer variables. Then the following code

.. mpg-code:: snippet:m-branch:sec:m:branch:basics:code:4
   :direct:


is equivalent, albeit considerably less efficient, to

.. mpg-code:: snippet:m-branch:sec:m:branch:basics:code:5
   :direct:


.. _modeling:m-branch:brancher-groups:

.. rubric:: Brancher groups.

Branchers can be controlled by brancher groups, they are discussed in detail in :ref:`sec:m:group:branch`.

.. _sec:m:branch:int:


.. _modeling:m-branch:branching-on-integer-and-boolean-variables:

Branching on integer and Boolean variables
------------------------------------------

.. important::

   .. container:: samepage

      Do not forget to add

      .. mpg-code:: snippet:m-branch:sec:m:branch:int:code:1
         :direct:

   to your program when you want to branch on integer and Boolean variables.

.. mpg-figure:: Integer variable selection
   :name: fig:m:branch:int:var:int

   .. container:: center

      +-------------------------------------------------------------------+------------------------------------------+
      | ``INT_VAR_NONE()``                                                | first unassigned                         |
      +-------------------------------------------------------------------+------------------------------------------+
      | ``INT_VAR_RND(r)``                                                | randomly                                 |
      +-------------------------------------------------------------------+------------------------------------------+
      | ``INT_VAR_MERIT_MIN(m,t*)``                                       | smallest value of merit function ``m``   |
      +-------------------------------------------------------------------+------------------------------------------+
      | ``INT_VAR_MERIT_MAX(m,t*)``                                       | largest value of merit function ``m``    |
      +-------------------------------------------------------------------+------------------------------------------+
      | ``INT_VAR_DEGREE_MIN(t*)``                                        | smallest degree                          |
      +-------------------------------------------------------------------+------------------------------------------+
      | ``INT_VAR_DEGREE_MAX(t*)``                                        | largest degree                           |
      +-------------------------------------------------------------------+------------------------------------------+
      | ``INT_VAR_AFC_MIN(afc+,t*)``                                      | smallest accumulated failure count (AFC) |
      +-------------------------------------------------------------------+------------------------------------------+
      | ``INT_VAR_AFC_MAX(afc+,t*)``                                      | largest accumulated failure count (AFC)  |
      +-------------------------------------------------------------------+------------------------------------------+
      | ``INT_VAR_ACTION_MIN(act+,t*)``                                   | lowest action                            |
      +-------------------------------------------------------------------+------------------------------------------+
      | ``INT_VAR_ACTION_MAX(act+,t*)``                                   | highest action                           |
      +-------------------------------------------------------------------+------------------------------------------+
      | ``INT_VAR_CHB_MIN(chb+,t*)``                                      | lowest chb Q-score                       |
      +-------------------------------------------------------------------+------------------------------------------+
      | ``INT_VAR_CHB_MAX(chb+,t*)``                                      | highest chb Q-score                      |
      +-------------------------------------------------------------------+------------------------------------------+
      | ``INT_VAR_MIN_MIN(t*)``                                           | smallest minimum value                   |
      +-------------------------------------------------------------------+------------------------------------------+
      | ``INT_VAR_MIN_MAX(t*)``                                           | largest minimum value                    |
      +-------------------------------------------------------------------+------------------------------------------+
      | ``INT_VAR_MAX_MIN(t*)``                                           | smallest maximum value                   |
      +-------------------------------------------------------------------+------------------------------------------+
      | ``INT_VAR_MAX_MAX(t*)``                                           | largest maximum value                    |
      +-------------------------------------------------------------------+------------------------------------------+
      | ``INT_VAR_SIZE_MIN(t*)``                                          | smallest domain size                     |
      +-------------------------------------------------------------------+------------------------------------------+
      | ``INT_VAR_SIZE_MAX(t*)``                                          | largest domain size                      |
      +-------------------------------------------------------------------+------------------------------------------+
      | ``INT_VAR_DEGREE_SIZE_MIN(t*)``                                   | smallest degree divided by domain size   |
      +-------------------------------------------------------------------+------------------------------------------+
      | ``INT_VAR_DEGREE_SIZE_MAX(t*)``                                   | largest degree by domain size            |
      +-------------------------------------------------------------------+------------------------------------------+
      | ``INT_VAR_AFC_SIZE_MIN(afc+,t*)``                                 | smallest AFC by domain size              |
      +-------------------------------------------------------------------+------------------------------------------+
      | ``INT_VAR_AFC_SIZE_MAX(afc+,t*)``                                 | largest AFC by domain size               |
      +-------------------------------------------------------------------+------------------------------------------+
      | ``INT_VAR_ACTION_SIZE_MIN(act+,t*)``                              | smallest action by domain size           |
      +-------------------------------------------------------------------+------------------------------------------+
      | ``INT_VAR_ACTION_SIZE_MAX(act+,t*)``                              | largest action by domain size            |
      +-------------------------------------------------------------------+------------------------------------------+
      | ``INT_VAR_CHB_SIZE_MIN(chb+,t*)``                                 | smallest chb by domain size              |
      +-------------------------------------------------------------------+------------------------------------------+
      | ``INT_VAR_CHB_SIZE_MAX(chb+,t*)``                                 | largest chb by domain size               |
      +-------------------------------------------------------------------+------------------------------------------+
      | ``INT_VAR_REGRET_MIN_MIN(t*)``                                    | smallest minimum-regret                  |
      +-------------------------------------------------------------------+------------------------------------------+
      | ``INT_VAR_REGRET_MIN_MAX(t*)``                                    | largest minimum-regret                   |
      +-------------------------------------------------------------------+------------------------------------------+
      | ``INT_VAR_REGRET_MAX_MIN(t*)``                                    | smallest maximum-regret                  |
      +-------------------------------------------------------------------+------------------------------------------+
      | ``INT_VAR_REGRET_MAX_MAX(t*)``                                    | largest maximum-regret                   |
      +-------------------------------------------------------------------+------------------------------------------+

.. _modeling:m-branch:branching-on-integer-variables:

.. rubric:: Branching on integer variables.

For integer variables, variable selection is defined by a value of class `IntVarBranch <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1IntVarBranch.html>`__ and value selection is defined by a value of type `IntValBranch <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1IntValBranch.html>`__. Values of these types are obtained by calling functions (possibly taking arguments) that correspond to variable and value selection strategies. For example, a call ``INT_VAR_SIZE_MIN()`` returns an object of class `IntVarBranch <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1IntVarBranch.html>`__.

For an overview of the available variable selection strategies, see :numref:`fig:m:branch:int:var:int` (see also `Variable selection for integer and Boolean variables <https://www.gecode.dev/doc/6.4.0/reference/group__TaskModelIntBranchVar.html>`__) where :math:`\cdot`\ * denotes an optional argument and :math:`\cdot`\ + is a special argument to be explained below. Here, an argument ``r`` refers to a random number generator of type `Rnd <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1Rnd.html>`__. Using random number generators for branching is discussed in :ref:`sec:m:branch:rnd`. An argument ``m`` refers to a user-defined merit function of type `IntBranchMerit <https://www.gecode.dev/doc/6.4.0/reference/group__TaskModelIntBranch.html>`__ for integer variables and `BoolBranchMerit <https://www.gecode.dev/doc/6.4.0/reference/group__TaskModelIntBranch.html>`__ for Boolean variables. User-defined merit functions are discussed in :ref:`sec:m:branch:uservar`. An argument ``afc`` refers to accumulated failure count (AFC) information for integer variables (of class `IntAFC <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1IntAFC.html>`__). An argument ``act`` refers to action information for integer variables (of class `IntAction <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1IntAction.html>`__). An argument ``chb`` refers to CHB information for integer variables (of class `IntCHB <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1IntCHB.html>`__). For a discussion of AFC, action, and CHB, see :ref:`sec:m:branch:shared`. Both ``afc``\ + and ``act``\ + can also be optional arguments of type ``double`` defining a decay-factor, whereas the argument ``chb``\ + can be omitted. The optional argument ``t`` refers to a tie-breaking limit function of type `BranchTbl <https://www.gecode.dev/doc/6.4.0/reference/group__TaskModelBranch.html>`__ and is discussed in :ref:`sec:m:branch:tbl`.

Omitting the variable selection strategy is equivalent to using ``INT_VAR_NONE()``.

.. mpg-figure:: Integer value selection
   :name: fig:m:branch:int:val:int

   .. container:: center

      +----------------------------------+------------------------------------------------------------+
      | ``INT_VAL_RND(r)``               | random value                                               |
      +----------------------------------+------------------------------------------------------------+
      | ``INT_VAL(v,c*)``                | defined by value function ``v`` and commit function ``c``  |
      +----------------------------------+------------------------------------------------------------+
      | ``INT_VAL_MIN()``                | smallest value                                             |
      +----------------------------------+------------------------------------------------------------+
      | ``INT_VAL_MED()``                | greatest value not greater than the median                 |
      +----------------------------------+------------------------------------------------------------+
      | ``INT_VAL_MAX()``                | largest value                                              |
      +----------------------------------+------------------------------------------------------------+
      | ``INT_VAL_SPLIT_MIN()``          | values not greater than mean of smallest and largest value |
      +----------------------------------+------------------------------------------------------------+
      | ``INT_VAL_SPLIT_MAX()``          | values greater than mean of smallest and largest value     |
      +----------------------------------+------------------------------------------------------------+
      | ``INT_VAL_RANGE_MIN()``          | values from smallest range, if domain has several ranges;  |
      +----------------------------------+------------------------------------------------------------+
      |                                  | otherwise, values not greater than mean                    |
      +----------------------------------+------------------------------------------------------------+
      | ``INT_VAL_RANGE_MAX()``          | values from largest range, if domain has several ranges;   |
      +----------------------------------+------------------------------------------------------------+
      |                                  | otherwise, values greater than mean                        |
      +----------------------------------+------------------------------------------------------------+
      | ``INT_VALUES_MIN()``             | all values starting from smallest                          |
      +----------------------------------+------------------------------------------------------------+
      | ``INT_VALUES_MAX()``             | all values starting from largest                           |
      +----------------------------------+------------------------------------------------------------+

An overview of the available value selection strategies for integer variables can be found in :numref:`fig:m:branch:int:val:int` (see also `Value selection for integer and Boolean variables <https://www.gecode.dev/doc/6.4.0/reference/group__TaskModelIntBranchVal.html>`__) where :math:`\cdot`\ * denotes an optional argument. Here, an argument ``r`` refers to a random number generator of type `Rnd <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1Rnd.html>`__ which is discussed in :ref:`sec:m:branch:rnd`. An argument ``v`` refers to a value selection function of type `IntBranchVal <https://www.gecode.dev/doc/6.4.0/reference/group__TaskModelIntBranch.html>`__. An optional argument ``c`` refers to a commit function of type `IntBranchCommit <https://www.gecode.dev/doc/6.4.0/reference/group__TaskModelIntBranch.html>`__. Value and commit functions are discussed in :ref:`sec:m:branch:userval`.

Note that variable-value branchers are just common cases for branching based on the idea of selecting variables and values. In Gecode also arbitrary other branchers can be programmed, see :ref:`part:b`.

.. _tip:m:branch:reselected:

.. mpg-tip:: Variables are re-selected during branching

   A variable-value branching selects a variable for each choice it creates. Consider as an example a script using an integer variable array ``x`` with three variables and domains :math:`\left[1..4\right]` created by


   .. mpg-code:: snippet:m-branch:tip:m:branch:reselected:code:1
      :direct:

   .. container:: samepage

      Let us assume that no constraints are posted on the variables in ``x`` and that a branching is posted by

      .. mpg-code:: snippet:m-branch:tip:m:branch:reselected:code:2
         :direct:

   The branching starts by selecting ``x[0]`` as the first variable with the largest domain in the array ``x`` and creates the choice

   .. math::

      (\mbox{\texttt{x[0]}}\leq 2)\vee
      (\mbox{\texttt{x[0]}}> 2)

   Now assume that search explores the first alternative which results in the domain :math:`\{1,2\}` for ``x[0]``. When search continues, the branching again selects the first variable with a largest domain: hence ``x[1]`` is selected and *not* ``x[0]``.

   In other words, a variable-value branching does not stick to a selected variable until the variable becomes assigned. Instead, a variable-value branching re-selects a variable for each choice it creates.

..

.. mpg-tip:: Do not try all values

   Note that for ``INT_VALUES_MIN()`` and ``INT_VALUES_MAX()``, a variable-value branching creates a choice for each selected variable with one alternative per value of the variable.


   This is typically a poor choice, as none of the alternatives can benefit from propagation that arises when other values of the same variable are tried. These branchings exist for instructional purposes (well, they do create beautiful trees in Gist).

.. _modeling:m-branch:branching-on-boolean-variables:

.. rubric:: Branching on Boolean variables.

.. mpg-figure:: Boolean variable selection
   :name: fig:m:branch:int:var:bool

   .. container:: center

      +---------------------------------------------------------------+------------------------------------------+
      | ``BOOL_VAR_NONE()``                                           | first unassigned                         |
      +---------------------------------------------------------------+------------------------------------------+
      | ``BOOL_VAR_RND(r)``                                           | randomly                                 |
      +---------------------------------------------------------------+------------------------------------------+
      | ``BOOL_VAR_MERIT_MIN(m,t*)``                                  | smallest value of merit function ``m``   |
      +---------------------------------------------------------------+------------------------------------------+
      | ``BOOL_VAR_MERIT_MAX(m,t*)``                                  | largest value of merit function ``m``    |
      +---------------------------------------------------------------+------------------------------------------+
      | ``BOOL_VAR_DEGREE_MIN(t*)``                                   | smallest degree                          |
      +---------------------------------------------------------------+------------------------------------------+
      | ``BOOL_VAR_DEGREE_MAX(t*)``                                   | largest degree                           |
      +---------------------------------------------------------------+------------------------------------------+
      | ``BOOL_VAR_AFC_MIN(afc+,t*)``                                 | smallest accumulated failure count (AFC) |
      +---------------------------------------------------------------+------------------------------------------+
      | ``BOOL_VAR_AFC_MAX(afc+,t*)``                                 | largest accumulated failure count (AFC)  |
      +---------------------------------------------------------------+------------------------------------------+
      | ``BOOL_VAR_ACTION_MIN(act+,t*)``                              | lowest action                            |
      +---------------------------------------------------------------+------------------------------------------+
      | ``BOOL_VAR_ACTION_MAX(act+,t*)``                              | highest action                           |
      +---------------------------------------------------------------+------------------------------------------+
      | ``BOOL_VAR_CHB_MIN(chb+,t*)``                                 | lowest CHB Q-score                       |
      +---------------------------------------------------------------+------------------------------------------+
      | ``BOOL_VAR_CHB_MAX(chb+,t*)``                                 | highest CHB Q-score                      |
      +---------------------------------------------------------------+------------------------------------------+

Similar to integer variables, variable selection for Boolean variables is defined by a value of class `BoolVarBranch <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1BoolVarBranch.html>`__ and value selection is defined by a value of type `BoolValBranch <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1BoolValBranch.html>`__. Values of these types are obtained by calling functions (possibly taking arguments) that correspond to variable and value selection strategies.

For an overview of the available variable selection strategies, see :numref:`fig:m:branch:int:var:bool` (see also `Variable selection for integer and Boolean variables <https://www.gecode.dev/doc/6.4.0/reference/group__TaskModelIntBranchVar.html>`__) where :math:`\cdot`\ * denotes an optional argument and :math:`\cdot`\ + is a special argument to be explained below. Here, an argument ``r`` refers to a random number generator of type `Rnd <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1Rnd.html>`__. An argument ``m`` refers to a user-defined merit function of type `BoolBranchMerit <https://www.gecode.dev/doc/6.4.0/reference/group__TaskModelIntBranch.html>`__. An argument ``afc`` refers to accumulated failure count (AFC) information for Boolean variables (of class `BoolAFC <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1BoolAFC.html>`__). An argument ``act`` refers to action information for Boolean variables (of class `BoolAction <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1BoolAction.html>`__). An argument ``chb`` refers to CHB information for Boolean variables (of class `BoolCHB <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1BoolCHB.html>`__). The optional argument ``t`` refers to a tie-breaking limit function of type `BranchTbl <https://www.gecode.dev/doc/6.4.0/reference/group__TaskModelBranch.html>`__.

Omitting the variable selection strategy is equivalent to using ``BOOL_VAR_NONE()``.

.. mpg-figure:: Boolean value selection
   :name: fig:m:branch:int:val:bool

   .. container:: center

      +-----------------------------------+-----------------------------------------------------------+
      | ``BOOL_VAL_RND(r)``               | random value                                              |
      +-----------------------------------+-----------------------------------------------------------+
      | ``BOOL_VAL(v,c*)``                | defined by value function ``v`` and commit function ``c`` |
      +-----------------------------------+-----------------------------------------------------------+
      | ``BOOL_VAL_MIN()``                | smallest value                                            |
      +-----------------------------------+-----------------------------------------------------------+
      | ``BOOL_VAL_MAX()``                | largest value                                             |
      +-----------------------------------+-----------------------------------------------------------+

An overview of the available value selection strategies for Boolean variables can be found in :numref:`fig:m:branch:int:val:bool` (see also `Value selection for integer and Boolean variables <https://www.gecode.dev/doc/6.4.0/reference/group__TaskModelIntBranchVal.html>`__) where :math:`\cdot`\ * denotes an optional argument. Here, an argument ``r`` refers to a random number generator of type `Rnd <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1Rnd.html>`__. An argument ``v`` refers to a value selection function of type `BoolBranchVal <https://www.gecode.dev/doc/6.4.0/reference/group__TaskModelIntBranch.html>`__. An optional argument ``c`` refers to a commit function of type `BoolBranchCommit <https://www.gecode.dev/doc/6.4.0/reference/group__TaskModelIntBranch.html>`__.

.. _sec:m:branch:set:


.. _modeling:m-branch:branching-on-set-variables:

Branching on set variables
--------------------------

.. important::

   Do not forget to add

   .. mpg-code:: snippet:m-branch:sec:m:branch:set:code:1
      :direct:

   to your program when you want to branch on set variables.

.. mpg-figure:: Set variable selection
   :name: fig:m:branch:set:var

   .. container:: center

      +-------------------------------------------------------------------+------------------------------------------+
      | ``SET_VAR_NONE()``                                                | first unassigned                         |
      +-------------------------------------------------------------------+------------------------------------------+
      | ``SET_VAR_RND(r)``                                                | randomly                                 |
      +-------------------------------------------------------------------+------------------------------------------+
      | ``SET_VAR_MERIT_MIN(m,t*)``                                       | smallest value of merit function ``m``   |
      +-------------------------------------------------------------------+------------------------------------------+
      | ``SET_VAR_MERIT_MAX(m,t*)``                                       | largest value of merit function ``m``    |
      +-------------------------------------------------------------------+------------------------------------------+
      | ``SET_VAR_DEGREE_MIN(t*)``                                        | smallest degree                          |
      +-------------------------------------------------------------------+------------------------------------------+
      | ``SET_VAR_DEGREE_MAX(t*)``                                        | largest degree                           |
      +-------------------------------------------------------------------+------------------------------------------+
      | ``SET_VAR_AFC_MIN(afc+,t*)``                                      | smallest accumulated failure count (AFC) |
      +-------------------------------------------------------------------+------------------------------------------+
      | ``SET_VAR_AFC_MAX(afc+,t*)``                                      | largest accumulated failure count (AFC)  |
      +-------------------------------------------------------------------+------------------------------------------+
      | ``SET_VAR_ACTION_MIN(act+,t*)``                                   | lowest action                            |
      +-------------------------------------------------------------------+------------------------------------------+
      | ``SET_VAR_ACTION_MAX(act+,t*)``                                   | highest action                           |
      +-------------------------------------------------------------------+------------------------------------------+
      | ``SET_VAR_CHB_MIN(chb+,t*)``                                      | lowest CHB Q-score                       |
      +-------------------------------------------------------------------+------------------------------------------+
      | ``SET_VAR_CHB_MAX(chb+,t*)``                                      | highest CHB Q-score                      |
      +-------------------------------------------------------------------+------------------------------------------+
      | ``SET_VAR_MIN_MIN(t*)``                                           | smallest minimum unknown element         |
      +-------------------------------------------------------------------+------------------------------------------+
      | ``SET_VAR_MIN_MAX(t*)``                                           | largest minimum unknown element          |
      +-------------------------------------------------------------------+------------------------------------------+
      | ``SET_VAR_MAX_MIN(t*)``                                           | smallest maximum unknown element         |
      +-------------------------------------------------------------------+------------------------------------------+
      | ``SET_VAR_MAX_MAX(t*)``                                           | largest maximum unknown element          |
      +-------------------------------------------------------------------+------------------------------------------+
      | ``SET_VAR_SIZE_MIN(t*)``                                          | smallest unknown set                     |
      +-------------------------------------------------------------------+------------------------------------------+
      | ``SET_VAR_SIZE_MAX(t*)``                                          | largest unknown set                      |
      +-------------------------------------------------------------------+------------------------------------------+
      | ``SET_VAR_DEGREE_SIZE_MIN(t*)``                                   | smallest degree divided by domain size   |
      +-------------------------------------------------------------------+------------------------------------------+
      | ``SET_VAR_DEGREE_SIZE_MAX(t*)``                                   | largest degree divided by domain size    |
      +-------------------------------------------------------------------+------------------------------------------+
      | ``SET_VAR_AFC_SIZE_MIN(afc+,t*)``                                 | smallest AFC divided by domain size      |
      +-------------------------------------------------------------------+------------------------------------------+
      | ``SET_VAR_AFC_SIZE_MAX(afc+,t*)``                                 | largest AFC divided by domain size       |
      +-------------------------------------------------------------------+------------------------------------------+
      | ``SET_VAR_ACTION_SIZE_MIN(act+,t*)``                              | smallest action divided by domain size   |
      +-------------------------------------------------------------------+------------------------------------------+
      | ``SET_VAR_ACTION_SIZE_MAX(act+,t*)``                              | largest action divided by domain size    |
      +-------------------------------------------------------------------+------------------------------------------+
      | ``SET_VAR_CHB_SIZE_MIN(chb+,t*)``                                 | smallest CHB divided by domain size      |
      +-------------------------------------------------------------------+------------------------------------------+
      | ``SET_VAR_CHB_SIZE_MAX(chb+,t*)``                                 | largest CHB divided by domain size       |
      +-------------------------------------------------------------------+------------------------------------------+

For set variables, variable selection is defined by a value of class `SetVarBranch <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1SetVarBranch.html>`__ (see also `Selecting set variables <https://www.gecode.dev/doc/6.4.0/reference/group__TaskModelSetBranchVar.html>`__) and value selection is defined by a value of type `SetValBranch <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1SetValBranch.html>`__ (see also `Value selection for set variables <https://www.gecode.dev/doc/6.4.0/reference/group__TaskModelSetBranchVal.html>`__).

For an overview of the available variable selection strategies, see :numref:`fig:m:branch:set:var` (see also `Selecting set variables <https://www.gecode.dev/doc/6.4.0/reference/group__TaskModelSetBranchVar.html>`__) where :math:`\cdot`\ * denotes an optional argument and :math:`\cdot`\ + is a special argument to be explained below. Here, an argument ``r`` refers to a random number generator of type `Rnd <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1Rnd.html>`__. Using random number generators for branching is discussed in :ref:`sec:m:branch:rnd`. An argument ``m`` refers to a user-defined merit function of type `SetBranchMerit <https://www.gecode.dev/doc/6.4.0/reference/group__TaskModelSetBranch.html>`__. User-defined merit functions are discussed in :ref:`sec:m:branch:uservar`. An argument ``afc`` refers to accumulated failure count (AFC) information for set variables (of class `SetAFC <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1SetAFC.html>`__). An argument ``act`` refers to action information for set variables (of class `SetAction <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1SetAction.html>`__). An argument ``chb`` refers to CHB information for set variables (of class `SetCHB <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1SetCHB.html>`__). For a discussion of AFC, action, and CHB, see :ref:`sec:m:branch:shared`. Both ``afc``\ + and ``act``\ + can also be optional arguments of type ``double`` defining a decay-factor. The argument ?chb?+ can be omitted. The optional argument ``t`` refers to a tie-breaking limit function of type `BranchTbl <https://www.gecode.dev/doc/6.4.0/reference/group__TaskModelBranch.html>`__ and is discussed in :ref:`sec:m:branch:tbl`.

Omitting the variable selection strategy is equivalent to using ``SET_VAR_NONE()``.

.. mpg-figure:: Set value selection
   :name: fig:m:branch:set:val

   .. container:: center

      +----------------------------------+-----------------------------------------------------------+
      | ``SET_VAL_RND_INC(r)``           | include random element                                    |
      +----------------------------------+-----------------------------------------------------------+
      | ``SET_VAL_RND_EXC(r)``           | exclude random element                                    |
      +----------------------------------+-----------------------------------------------------------+
      | ``SET_VAL(v,c*)``                | defined by value function ``v`` and commit function ``c`` |
      +----------------------------------+-----------------------------------------------------------+
      | ``SET_VAL_MIN_INC()``            | include smallest element                                  |
      +----------------------------------+-----------------------------------------------------------+
      | ``SET_VAL_MIN_EXC()``            | exclude smallest element                                  |
      +----------------------------------+-----------------------------------------------------------+
      | ``SET_VAL_MED_INC()``            | include median element (rounding downwards)               |
      +----------------------------------+-----------------------------------------------------------+
      | ``SET_VAL_MED_EXC()``            | exclude median element (rounding downwards)               |
      +----------------------------------+-----------------------------------------------------------+
      | ``SET_VAL_MAX_INC()``            | include largest element                                   |
      +----------------------------------+-----------------------------------------------------------+
      | ``SET_VAL_MAX_EXC()``            | exclude largest element                                   |
      +----------------------------------+-----------------------------------------------------------+

An overview of the available value selection strategies for set variables can be found in :numref:`fig:m:branch:set:val` where :math:`\cdot`\ * denotes an optional argument. Here, an argument ``r`` refers to a random number generator of type `Rnd <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1Rnd.html>`__ which is discussed in :ref:`sec:m:branch:rnd`. An argument ``v`` refers to a value selection function of type `SetBranchVal <https://www.gecode.dev/doc/6.4.0/reference/group__TaskModelSetBranch.html>`__. An optional argument ``c`` refers to a commit function of type `SetBranchCommit <https://www.gecode.dev/doc/6.4.0/reference/group__TaskModelSetBranch.html>`__. Value and commit function are discussed in :ref:`sec:m:branch:userval`.

.. _sec:m:branch:float:


.. _modeling:m-branch:branching-on-float-variables:

Branching on float variables
----------------------------

.. important::

   Do not forget to add

   .. mpg-code:: snippet:m-branch:sec:m:branch:float:code:1
      :direct:

   to your program when you want to branch on float variables.

.. mpg-figure:: Float variable selection
   :name: fig:m:branch:float:var

   .. container:: center

      +---------------------------------------------------------------------+------------------------------------------+
      | ``FLOAT_VAR_NONE()``                                                | first unassigned                         |
      +---------------------------------------------------------------------+------------------------------------------+
      | ``FLOAT_VAR_RND(r)``                                                | randomly                                 |
      +---------------------------------------------------------------------+------------------------------------------+
      | ``FLOAT_VAR_MERIT_MIN(m,t*)``                                       | smallest value of merit function ``m``   |
      +---------------------------------------------------------------------+------------------------------------------+
      | ``FLOAT_VAR_MERIT_MAX(m,t*)``                                       | largest value of merit function ``m``    |
      +---------------------------------------------------------------------+------------------------------------------+
      | ``FLOAT_VAR_DEGREE_MIN(t*)``                                        | smallest degree                          |
      +---------------------------------------------------------------------+------------------------------------------+
      | ``FLOAT_VAR_DEGREE_MAX(t*)``                                        | largest degree                           |
      +---------------------------------------------------------------------+------------------------------------------+
      | ``FLOAT_VAR_AFC_MIN(afc+,t*)``                                      | smallest accumulated failure count (AFC) |
      +---------------------------------------------------------------------+------------------------------------------+
      | ``FLOAT_VAR_AFC_MAX(afc+,t*)``                                      | largest accumulated failure count (AFC)  |
      +---------------------------------------------------------------------+------------------------------------------+
      | ``FLOAT_VAR_ACTION_MIN(act+,t*)``                                   | lowest action                            |
      +---------------------------------------------------------------------+------------------------------------------+
      | ``FLOAT_VAR_ACTION_MAX(act+,t*)``                                   | highest action                           |
      +---------------------------------------------------------------------+------------------------------------------+
      | ``FLOAT_VAR_CHB_MIN(chb+,t*)``                                      | lowest CHB Q-score                       |
      +---------------------------------------------------------------------+------------------------------------------+
      | ``FLOAT_VAR_CHB_MAX(chb+,t*)``                                      | highest CHB Q-score                      |
      +---------------------------------------------------------------------+------------------------------------------+
      | ``FLOAT_VAR_MIN_MIN(t*)``                                           | smallest minimum value                   |
      +---------------------------------------------------------------------+------------------------------------------+
      | ``FLOAT_VAR_MIN_MAX(t*)``                                           | largest minimum value                    |
      +---------------------------------------------------------------------+------------------------------------------+
      | ``FLOAT_VAR_MAX_MIN(t*)``                                           | smallest maximum value                   |
      +---------------------------------------------------------------------+------------------------------------------+
      | ``FLOAT_VAR_MAX_MAX(t*)``                                           | largest maximum value                    |
      +---------------------------------------------------------------------+------------------------------------------+
      | ``FLOAT_VAR_SIZE_MIN(t*)``                                          | smallest domain size                     |
      +---------------------------------------------------------------------+------------------------------------------+
      | ``FLOAT_VAR_SIZE_MAX(t*)``                                          | largest domain size                      |
      +---------------------------------------------------------------------+------------------------------------------+
      | ``FLOAT_VAR_DEGREE_SIZE_MIN(t*)``                                   | smallest degree divided by domain size   |
      +---------------------------------------------------------------------+------------------------------------------+
      | ``FLOAT_VAR_DEGREE_SIZE_MAX(t*)``                                   | largest degree divided by domain size    |
      +---------------------------------------------------------------------+------------------------------------------+
      | ``FLOAT_VAR_AFC_SIZE_MIN(afc+,t*)``                                 | smallest AFC divided by domain size      |
      +---------------------------------------------------------------------+------------------------------------------+
      | ``FLOAT_VAR_AFC_SIZE_MAX(afc+,t*)``                                 | largest AFC divided by domain size       |
      +---------------------------------------------------------------------+------------------------------------------+
      | ``FLOAT_VAR_ACTION_SIZE_MIN(act+,t*)``                              | smallest action divided by domain size   |
      +---------------------------------------------------------------------+------------------------------------------+
      | ``FLOAT_VAR_ACTION_SIZE_MAX(act+,t*)``                              | largest action divided by domain size    |
      +---------------------------------------------------------------------+------------------------------------------+
      | ``FLOAT_VAR_CHB_SIZE_MIN(chb+,t*)``                                 | smallest chb divided by domain size      |
      +---------------------------------------------------------------------+------------------------------------------+
      | ``FLOAT_VAR_CHB_SIZE_MAX(chb+,t*)``                                 | largest chb divided by domain size       |
      +---------------------------------------------------------------------+------------------------------------------+

For float variables, variable selection is defined by a value of class `FloatVarBranch <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1FloatVarBranch.html>`__ (see also `Variable selection for float variables <https://www.gecode.dev/doc/6.4.0/reference/group__TaskModelFloatBranchVar.html>`__) and value selection is defined by a value of type `FloatValBranch <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1FloatValBranch.html>`__ (see also `Value selection for float variables <https://www.gecode.dev/doc/6.4.0/reference/group__TaskModelFloatBranchVal.html>`__).

For an overview of the available variable selection strategies, see :numref:`fig:m:branch:float:var` (see also `Variable selection for float variables <https://www.gecode.dev/doc/6.4.0/reference/group__TaskModelFloatBranchVar.html>`__) where :math:`\cdot`\ * denotes an optional argument and :math:`\cdot`\ + is a special argument to be explained below. Here, an argument ``r`` refers to a random number generator of type `Rnd <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1Rnd.html>`__. Using random number generators for branching is discussed in :ref:`sec:m:branch:rnd`. An argument ``m`` refers to a user-defined merit function of type `FloatBranchMerit <https://www.gecode.dev/doc/6.4.0/reference/group__TaskModelFloatBranch.html>`__. User-defined merit functions are discussed in :ref:`sec:m:branch:uservar`. An argument ``afc`` refers to accumulated failure count (AFC) information for float variables (of class `FloatAFC <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1FloatAFC.html>`__). An argument ``act`` refers to action information for float variables (of class `FloatAction <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1FloatAction.html>`__). An argument ``chb`` refers to CHB information for float variables (of class `FloatCHB <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1FloatCHB.html>`__). For a discussion of AFC, action, and CHB, see :ref:`sec:m:branch:shared`. Both ``afc``\ + and ``act``\ + can also be optional arguments of type ``double`` defining a decay-factor. The argument ``chb``\ + can be ommitted. The optional argument ``t`` refers to a tie-breaking limit function of type `BranchTbl <https://www.gecode.dev/doc/6.4.0/reference/group__TaskModelBranch.html>`__ and is discussed in :ref:`sec:m:branch:tbl`.

Omitting the variable selection strategy is equivalent to using ``FLOAT_VAR_NONE()``.

.. mpg-figure:: Float value selection
   :name: fig:m:branch:float:val

   .. container:: center

      +------------------------------------+-----------------------------------------------------------+
      | ``FLOAT_VAL(v,c*)``                | defined by value function ``v`` and commit function ``c`` |
      +------------------------------------+-----------------------------------------------------------+
      | ``FLOAT_VAL_SPLIT_RND(r)``         | values not smaller or larger than mean                    |
      +------------------------------------+-----------------------------------------------------------+
      |                                    | (smaller or larger is randomly selected)                  |
      +------------------------------------+-----------------------------------------------------------+
      | ``FLOAT_VAL_SPLIT_MIN()``          | values not greater than mean                              |
      +------------------------------------+-----------------------------------------------------------+
      | ``FLOAT_VAL_SPLIT_MAX()``          | values not smaller than mean                              |
      +------------------------------------+-----------------------------------------------------------+

An overview of the available value selection strategies for float variables can be found in :numref:`fig:m:branch:float:val` where :math:`\cdot`\ \* denotes an optional argument. Here, an argument ``r`` refers to a random number generator of type `Rnd <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1Rnd.html>`__ which is discussed in :ref:`sec:m:branch:rnd`. An argument ``v`` refers to a value selection function of type `FloatBranchVal <https://www.gecode.dev/doc/6.4.0/reference/group__TaskModelFloatBranch.html>`__. An optional argument ``c`` refers to a commit function of type `FloatBranchCommit <https://www.gecode.dev/doc/6.4.0/reference/group__TaskModelFloatBranch.html>`__. Value and commit function are discussed in :ref:`sec:m:branch:userval`.

.. _sec:m:branch:shared:


.. _modeling:m-branch:local-versus-shared-variable-selection-criteria:

Local versus shared variable selection criteria
-----------------------------------------------

The criteria used for selecting variables are either *local* or *shared*. A *local* variable selection criterion depends only on a brancher’s home space. A *shared* variable selection criterion depends not only on the brancher’s home space but also on all spaces that have been created during search sharing the same root space where the brancher had originally been posted. That entails that a shared criterion can use information that is collected during search. In terms of :ref:`sec:m:search:re`, a shared variable selection criterion depends on all equivalent spaces created by cloning.

.. _modeling:m-branch:local-variable-selection-criteria:

Local variable selection criteria
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

All selection criteria but those based on *AFC*, *action*, and *CHB* are local: they either select variables without using any information on a variable (``INT_VAR_NONE()``), select variables randomly (``INT_VAR_RND(r)``, see also :ref:`sec:m:branch:rnd`), or use the degree or domain of a variable for selection. The user-defined selection criteria ``INT_VAR_MERIT_MIN()`` and ``INT_VAR_MERIT_MAX()`` in addition have access to the home space and the selected variable’s position, see :ref:`sec:m:branch:uservar` for details.

The *degree* of a variable is the number of propagators depending on the variable (useful as an approximate measure of how constrained a variables is).

The *minimum-regret* for integer and Boolean variables is the difference between the smallest and second smallest value in the domain of a variable (*maximum-regret* is analogous).

.. _sec:m:branch:afc:


.. _modeling:m-branch:selection-using-accumulated-failure-count:

Selection using accumulated failure count
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The accumulated failure count (AFC) of a variable is a shared selection criterion. It is defined as the sum of the AFCs of all propagators depending on the variable plus its degree (to give a good initial value if the AFCs of all propagators are still zero). The AFC of a propagator counts how often the propagator has failed during search. The AFC of a variable is also known as the weighted degree of a variable :cite:`AFC`.

AFC in Gecode supports decay as follows. Each time a propagator fails during constraint propagation (by executing the ``status()`` function of a space, see also :ref:`tip:m:started:status`), the AFC of all propagators is updated:

- If the propagator ``p`` failed, the AFC :math:`\mathtt{afc}(\mathtt p)` of ``p`` is incremented by :math:`1`:

  .. math:: \mathtt{afc}(\mathtt p)=\mathtt{afc}(\mathtt p)+1

  For all other propagators ``q``, the AFC :math:`\mathtt{afc}(\mathtt q)` of ``q`` is updated by a decay-factor :math:`\mathtt{d}` (:math:`0<\mathtt{d}\leq 1`):

  .. math:: \mathtt{afc}(\mathtt q)=\mathtt{d}\cdot\mathtt{afc}(\mathtt q)

- The AFC :math:`\mathtt{afc}(\mathtt x)` of a variable ``x`` is then defined as:

  .. math::

     \mathtt{afc}(\mathtt
       x)=\mathtt{afc}(\mathtt{p}_1)+\cdots+\mathtt{afc}(\mathtt{p}_n)

  where the propagators :math:`\mathtt{p}_i` depend on ``x``.

- The AFC :math:`\mathtt{afc}(\mathtt p)` of a propagator ``p`` is initialized to :math:`1`. That entails that the AFC of a variable ``x`` is initialized to its degree.

In order to use AFC for branching, one must create an object of class `IntAFC <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1IntAFC.html>`__ for integer variables, an object of class `BoolAFC <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1BoolAFC.html>`__ for Boolean variables, an object of class `SetAFC <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1SetAFC.html>`__ for set variables, or an object of class `FloatAFC <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1FloatAFC.html>`__ for float variables. The object is responsible for recording AFC information [1]_.

.. container:: samepage

   If ``x`` is an integer variable array, then

   .. mpg-code:: snippet:m-branch:sec:m:branch:afc:code:1
      :direct:

initializes the AFC information ``afc`` for the variables in ``x`` with decay-factor :math:`\mathtt{d}=\mathtt{0.99}`. The decay-factor is optional and defaults to no decay (:math:`\mathtt{d}=1`).

.. container:: samepage

   The decay-factor can be changed later, say to :math:`\mathtt{d}=\mathtt{0.95}`, by

   .. mpg-code:: snippet:m-branch:sec:m:branch:afc:code:2
      :direct:

and ``afc.decay()`` returns the current decay-factor of ``afc``.

A branching for integer variables using AFC information must be given an object of type ``IntAFC`` as argument:

.. mpg-code:: snippet:m-branch:sec:m:branch:afc:code:3
   :direct:


Here the integer variable array ``x`` must be exactly the same that has been used for creating the integer AFC object ``afc``.

The AFC object can be omitted if one does not want to change the decay-factor later, hence it is sufficient to pass the decay-factor as argument. For example:

.. mpg-code:: snippet:m-branch:sec:m:branch:afc:code:4
   :direct:


uses AFC information with a decay-factor of ``0.99``. Even the decay-factor can be omitted and defaults to ``1`` (that is, no decay).

AFC for other variable types is analogous.

For an example using a decay-factor with AFC, see :ref:`sec:c:crossword:info`.

.. _sec:m:branch:action:


.. _modeling:m-branch:selection-using-action:

Selection using action
~~~~~~~~~~~~~~~~~~~~~~

The action of a variable is a shared criterion and captures how often the domain of a variable has been reduced during constraint propagation.

The action of a variable is maintained by constraint propagation as follows. Each time constraint propagation finishes (even if it finishes with failure) during search (by executing the ``status()`` function of a space, see also :ref:`tip:m:started:status`), the action of a variable :math:`\mathtt x` is updated :cite:`activity`:

- If the variable ``x`` has not been pruned (that is, no values have been removed from the domain of ``x`` through propagation), the action :math:`\mathtt{action}(\mathtt x)` of ``x`` is updated by a decay-factor :math:`\mathtt{d}` (:math:`0<\mathtt{d}\leq 1`):

  .. math:: \mathtt{action}(\mathtt x)=\mathtt{d}\cdot\mathtt{action}(\mathtt x)

- If the variable ``x`` has been pruned, the action :math:`\mathtt{action}(\mathtt x)` of ``x`` is incremented by :math:`1`:

  .. math:: \mathtt{action}(\mathtt x)=\mathtt{action}(\mathtt x)+1

- The action of a variable ``x`` is initialized to be one.

Note that in :cite:`activity` action is called activity. However, as the activity of a variable during search in SAT is a well-established and different concept (see for example :cite:`minisat`), Gecode uses the term action instead.

In order to use action for branching, one must create an object of class `IntAction <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1IntAction.html>`__ for integer variables, an object of class `BoolAction <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1BoolAction.html>`__ for Boolean variables, an object of class `SetAction <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1SetAction.html>`__ for set variables, or an object of class `FloatAction <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1FloatAction.html>`__ for float variables. The object is responsible for recording action information.

.. container:: samepage

   If ``x`` is an integer variable array, then

   .. mpg-code:: snippet:m-branch:sec:m:branch:action:code:1
      :direct:

initializes the action information ``act`` for the variables in ``x`` with decay-factor :math:`\mathtt{d}=\mathtt{0.99}`. The decay-factor is optional and defaults to no decay (:math:`\mathtt{d}=1`).

Note that it can be specified whether the action counter is incremented when a variable is pruned (propagation) or when a variable domain has been wiped out (failure). For example, the following creates action information that onky considers propagation:

.. mpg-code:: snippet:m-branch:sec:m:branch:action:code:2
   :direct:


whereas the following only considers failure:

.. mpg-code:: snippet:m-branch:sec:m:branch:action:code:3
   :direct:


By default, both are considered which corresponds to:

.. mpg-code:: snippet:m-branch:sec:m:branch:action:code:4
   :direct:


The action of each variable in an array ``x`` can be initialized by a merit function, see :ref:`sec:m:branch:uservar`. Here

.. mpg-code:: snippet:m-branch:sec:m:branch:action:code:5
   :direct:


initializes the action of ``x[i]`` to ``1.0``.

The decay-factor can be changed later, say to :math:`\mathtt{d}=\mathtt{0.95}`, by

.. mpg-code:: snippet:m-branch:sec:m:branch:action:code:6
   :direct:


and ``act.decay()`` returns the current decay-factor of ``act``.

A branching for integer variables using action information must be given an object of type ``IntAction`` as argument:

.. mpg-code:: snippet:m-branch:sec:m:branch:action:code:7
   :direct:


Here the integer variable array ``x`` must be exactly the same that has been used for creating the integer action object ``act``.

The action object can be omitted if one does not want to change the decay-factor later, hence it is sufficient to pass the decay-factor as argument. For example:

.. mpg-code:: snippet:m-branch:sec:m:branch:action:code:8
   :direct:


uses action information with a decay-factor of ``0.99``. Even the decay-factor can be omitted and defaults to ``1`` (that is, no decay).

Action for other variable types is analogous.

.. _sec:m:branch:chb:


.. _modeling:m-branch:selection-using-chb:

Selection using CHB
~~~~~~~~~~~~~~~~~~~

The CHB (for conflict-history based branching) Q-score of a variable is a shared criterion and combines how often the domain of a variable has been reduced during constraint propagation with how recently the variable has been reduced during failure. CHB in Gecode is based on :cite:`chb` which presents the heuristic for a SAT solver. Here, we use the term failure instead of conflict as originally in :cite:`chb`.

The *Q-score* :math:`\mathtt{qs}(\mathtt x)` of a variable :math:`\mathtt x` is maintained by constraint propagation as follows. For the computation of the Q-score, the following two variables are used:

- The *failure counter* :math:`\mathtt{\#f}` counts how often failure has been encountered. That is, each time a space is failed, :math:`\mathtt{\#f}` is incremented by one and it is initialized to zero.

- The *step size* :math:`\alpha` is also updated when a failure occurs, it is updated by

  .. math:: \alpha = \alpha - \mathtt{10}^{-\mathtt 6}

  provided :math:`\alpha>0.06`. If :math:`\alpha\leq 0.06`, its value does not change. :math:`\alpha` is initialized to :math:`0.4`.

In addition to the Q-score for a variable, CHB also maintains the *last failure* :math:`\mathtt{lf}(\mathtt x)` of a variable :math:`\mathtt x`. Each time constraint propagation finishes during search (by executing the ``status()`` function of a space, see also :ref:`tip:m:started:status`), the Q-score :math:`\mathtt{qs}(\mathtt x)` and the last failure :math:`\mathtt{lf}(\mathtt x)` of a variable :math:`\mathtt x` are updated as follows:

- If the variable ``x`` has not been pruned (that is, no values have been removed from the domain of ``x`` through propagation), the Q-score :math:`\mathtt{qs}(\mathtt x)` and the last failure :math:`\mathtt{lf}(\mathtt x)` do not change.

- If the variable ``x`` has been pruned and propagation has failed, the last failure :math:`\mathtt{lf}(\mathtt x)` is updated to

  .. math:: \mathtt{lf}(\mathtt x)=\mathtt{\#f}

  and the Q-score is updated to

  .. math::

     \mathtt{qs}(\mathtt x)=(1-\alpha)\mathtt{qs}(\mathtt x) +
     \alpha r

  where the reward :math:`r` is defined as

  .. math:: r=\frac{1}{\mathtt{\#f}-\mathtt{lf}(\mathtt x) + 1}

- If the variable ``x`` has been pruned and propagation has not failed, the last failure :math:`\mathtt{lf}(\mathtt x)` remains unchanged and the Q-score is updated to

  .. math::

     \mathtt{qs}(\mathtt x)=(1-\alpha)\mathtt{qs}(\mathtt x) +
     \alpha r

  where the reward :math:`r` is defined as

  .. math:: r=\frac{0.9}{\mathtt{\#f}-\mathtt{lf}(\mathtt x) + 1}

- The Q-score :math:`\mathtt{qs}(\mathtt x)` of a variable ``x`` is by default initialized to be :math:`0.05`.

In order to use CHB Q-scores for branching, one must create an object of class `IntCHB <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1IntCHB.html>`__ for integer variables, an object of class `BoolCHB <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1BoolCHB.html>`__ for Boolean variables, an object of class `SetCHB <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1SetCHB.html>`__ for set variables, or an object of class `FloatCHB <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1FloatCHB.html>`__ for float variables. The object is responsible for recording CHB Q-score information.

.. container:: samepage

   If ``x`` is an integer variable array, then

   .. mpg-code:: snippet:m-branch:sec:m:branch:chb:code:1
      :direct:

initializes the CHB information ``chb`` for the variables in ``x``.

The Q-score of each variable in an array ``x`` can be initialized by a merit function, see :ref:`sec:m:branch:uservar`. Here

.. mpg-code:: snippet:m-branch:sec:m:branch:chb:code:2
   :direct:


initializes the Q-score of ``x[i]`` to ``1.0``.

A branching for integer variables using CHB information must be given an object of type ``IntCHB`` as argument. For example, the following brancher will select variables with largest Q-score as defined by ``chb`` first:

.. mpg-code:: snippet:m-branch:sec:m:branch:chb:code:3
   :direct:


Here the integer variable array ``x`` must be exactly the same that has been used for creating the integer CHB object ``chb``.

The CHB object can be omitted if one does not want to initialize the Q-score explicitly as described above.

CHB for other variable types is analogous.

.. _sec:m:branch:rnd:


.. _modeling:m-branch:random-variable-and-value-selection:

Random variable and value selection
-----------------------------------

One particular strategy for variable and value selection is by random. For integer variables, ``INT_VAR_RND(r)`` selects a random variable and ``INT_VAL_RND(r)`` selects a random value where ``r`` is a random number generator of class `Rnd <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1Rnd.html>`__. For Boolean variables, ``BOOL_VAR_RND(r)`` selects a random variable and ``BOOL_VAL_RND(r)`` selects a random value. For set variables, ``SET_VAR_RND(r)`` selects a random variable and ``SET_VAL_RND_INC(r)`` and ``SET_VAL_RND_EXC(r)`` include and exclude a random value from a set variable. For float variables, ``FLOAT_VAR_RND(r)`` selects a random variable and ``FLOAT_VAL_SPLIT_RND(r)`` randomly selects the lower or upper half of the domain of a float variable.

.. container:: samepage

   The random number generators used for random variable and value selection follow a uniform distribution and must be initialized by a seed value. For example, a random number generator ``r`` is created and initialized with a seed value of ``1`` (the seed value must be an ``unsigned int``) by

   .. mpg-code:: snippet:m-branch:sec:m:branch:rnd:code:1
      :direct:

The seed value can be changed with the ``seed()`` function (if needed, the ``seed()`` function initializes the random number generator). For example, by

.. mpg-code:: snippet:m-branch:sec:m:branch:rnd:code:2
   :direct:


the seed value is set to ``2`` (the ``seed()`` function also expects an argument of type ``unsigned int``).

A random number generator is passed by reference to the brancher.

.. container:: samepage

   It is possible to use the same random number generator for both variable and value selection. For example, by

   .. mpg-code:: snippet:m-branch:sec:m:branch:rnd:code:3
      :direct:

both the variable in ``x`` as well as its value are randomly selected using the numbers generated by ``r``. It is of course also possible to use two separate random number generators as in:

.. mpg-code:: snippet:m-branch:sec:m:branch:rnd:code:4
   :direct:


.. _sec:m:branch:uservar:


.. _modeling:m-branch:user-defined-variable-selection:

User-defined variable selection
-------------------------------

Variables can be selected according to user-defined criteria implemented as a *merit function*. For integer variables, the type of the merit function is `IntBranchMerit <https://www.gecode.dev/doc/6.4.0/reference/group__TaskModelIntBranch.html>`__, for Boolean variables `BoolBranchMerit <https://www.gecode.dev/doc/6.4.0/reference/group__TaskModelIntBranch.html>`__, for set variables `SetBranchMerit <https://www.gecode.dev/doc/6.4.0/reference/group__TaskModelSetBranch.html>`__, and for float variables `FloatBranchMerit <https://www.gecode.dev/doc/6.4.0/reference/group__TaskModelFloatBranch.html>`__. For integer variables, the type ``IntBranchMerit`` is defined as

.. mpg-code:: snippet:m-branch:sec:m:branch:uservar:code:1
   :direct:


where ``home`` refers to the home space, ``x`` is the integer variable for which a merit value should be computed and ``i`` refers to the position of ``x`` in the integer variable array passed as argument to the ``branch()`` function. The merit function types for Boolean, set, and float variables are analogous.

For example, the following merit function

.. mpg-code:: snippet:m-branch:sec:m:branch:uservar:code:2
   :direct:


simply returns the domain size of the integer variable ``x`` as the merit value. The merit function can be used to select a variable with either smallest or largest merit value. By

.. mpg-code:: snippet:m-branch:sec:m:branch:uservar:code:3
   :direct:


a variable with least merit value according to the merit function ``m()`` is selected (that is, the first variable in the array with smallest size). A variable with maximal merit value is selected by:

.. mpg-code:: snippet:m-branch:sec:m:branch:uservar:code:4
   :direct:


.. _sec:m:branch:userval:


.. _modeling:m-branch:user-defined-value-selection:

User-defined value selection
----------------------------

The value selected for branching and how the selected value is used for branching can be defined by *branch value functions* and *branch commit functions*.

.. mpg-figure:: Branch value functions
   :name: fig:m:branch:val

   .. container:: center

      +--------------------------------------------------------------------------------------------+------------------------------------------------------------------------------------------------------+--------------------------------------------------------------------------------------------------------+
      | Variable type                                                                              | Value function type                                                                                  | Value type                                                                                             |
      +============================================================================================+======================================================================================================+========================================================================================================+
      | `IntVar <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1IntVar.html>`__         | `IntBranchVal <https://www.gecode.dev/doc/6.4.0/reference/group__TaskModelIntBranch.html>`__         | ``int``                                                                                                |
      +--------------------------------------------------------------------------------------------+------------------------------------------------------------------------------------------------------+--------------------------------------------------------------------------------------------------------+
      | `BoolVar <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1BoolVar.html>`__       | `BoolBranchVal <https://www.gecode.dev/doc/6.4.0/reference/group__TaskModelIntBranch.html>`__        | ``int``                                                                                                |
      +--------------------------------------------------------------------------------------------+------------------------------------------------------------------------------------------------------+--------------------------------------------------------------------------------------------------------+
      | `SetVar <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1SetVar.html>`__         | `SetBranchVal <https://www.gecode.dev/doc/6.4.0/reference/group__TaskModelSetBranch.html>`__         | ``int``                                                                                                |
      +--------------------------------------------------------------------------------------------+------------------------------------------------------------------------------------------------------+--------------------------------------------------------------------------------------------------------+
      | `FloatVar <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1FloatVar.html>`__     | `FloatBranchVal <https://www.gecode.dev/doc/6.4.0/reference/group__TaskModelFloatBranch.html>`__     | `FloatNumBranch <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1FloatNumBranch.html>`__     |
      +--------------------------------------------------------------------------------------------+------------------------------------------------------------------------------------------------------+--------------------------------------------------------------------------------------------------------+

A branch value function takes a constant reference to a space, a variable, and the variable’s position and returns a value, where the type of the value depends on the variable type. :numref:`fig:m:branch:val` lists the branch value function types and the value types for the different variable types. For example, the type `IntBranchVal <https://www.gecode.dev/doc/6.4.0/reference/group__TaskModelIntBranch.html>`__ for value functions for integer variables is defined as:

.. mpg-code:: snippet:m-branch:fig:m:branch:val:code:1
   :direct:


A branch commit function takes a reference to a space, the number of the alternative ``a`` (``0`` for the first alternative and ``1`` for the second alternative), a variable, the variable’s position, and a value selected by a branch value function. For example, the type `IntBranchCommit <https://www.gecode.dev/doc/6.4.0/reference/group__TaskModelIntBranch.html>`__ for branch commit functions for integer variables is defined as:

.. mpg-code:: snippet:m-branch:fig:m:branch:val:code:2
   :direct:


Let us consider ``INT_VAL_MIN()`` as an example, but re-implemented by value and commit functions. The value function can be defined as:

.. mpg-code:: snippet:m-branch:fig:m:branch:val:code:3
   :direct:


and the commit function as:

.. mpg-code:: snippet:m-branch:fig:m:branch:val:code:4
   :direct:


A branching using the value and commit function then can be posted by:

.. mpg-code:: snippet:m-branch:fig:m:branch:val:code:5
   :direct:


The commit function is optional. If the commit function is omitted, a default commit function depending on the variable type is used. For integer variables, for example, the commit function corresponds to the commit function from the previous example. Hence, it is sufficient to post the brancher as:

.. mpg-code:: snippet:m-branch:fig:m:branch:val:code:6
   :direct:


.. mpg-figure:: Branch commit functions
   :name: fig:m:branch:commit

   .. container:: center

      +--------------------------------------------------------------------------------------------+---------------------------------------------------------------------------------------------------------+--------------------------------------------------------------------+
      | Variable type                                                                              | Commit function type                                                                                    | Default behavior                                                   |
      +============================================================================================+=========================================================================================================+====================================================================+
      | `IntVar <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1IntVar.html>`__         | `IntBranchCommit <https://www.gecode.dev/doc/6.4.0/reference/group__TaskModelIntBranch.html>`__         | :math:`(\mathtt{x}=\mathtt{n})\vee(\mathtt{x}\neq\mathtt{n})`      |
      +--------------------------------------------------------------------------------------------+---------------------------------------------------------------------------------------------------------+--------------------------------------------------------------------+
      | `BoolVar <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1BoolVar.html>`__       | `BoolBranchCommit <https://www.gecode.dev/doc/6.4.0/reference/group__TaskModelIntBranch.html>`__        | :math:`(\mathtt{x}=\mathtt{n})\vee(\mathtt{x}\neq\mathtt{n})`      |
      +--------------------------------------------------------------------------------------------+---------------------------------------------------------------------------------------------------------+--------------------------------------------------------------------+
      | `SetVar <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1SetVar.html>`__         | `SetBranchCommit <https://www.gecode.dev/doc/6.4.0/reference/group__TaskModelSetBranch.html>`__         | :math:`(\mathtt{n}\in\mathtt{x})\vee(\mathtt{n}\not\in\mathtt{x})` |
      +--------------------------------------------------------------------------------------------+---------------------------------------------------------------------------------------------------------+--------------------------------------------------------------------+
      | `FloatVar <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1FloatVar.html>`__     | `FloatBranchCommit <https://www.gecode.dev/doc/6.4.0/reference/group__TaskModelFloatBranch.html>`__     | :math:`(\mathtt{x}\leq\mathtt{n})\vee(\mathtt{x}\geq\mathtt{n})`   |
      +--------------------------------------------------------------------------------------------+---------------------------------------------------------------------------------------------------------+--------------------------------------------------------------------+

:numref:`fig:m:branch:commit` lists the commit function types and the behavior of the default commit function for the different variable types. The variable ``x`` refers to the variable selected by the brancher and ``n`` to the value selected by the branch value function.

For examples which use value functions to implement problem-specific branching, see `Black hole patience <https://www.gecode.dev/doc/6.4.0/reference/black-hole_8cpp.html>`__ and `The balanced academic curriculum problem <https://www.gecode.dev/doc/6.4.0/reference/bacp_8cpp.html>`__.

.. _sec:m:branch:tie:

.. _sec:m:branch:tbl:


.. _modeling:m-branch:tie-breaking:

Tie-breaking
------------

The default behavior for tie-breaking during variable selection is that the first variable (that is the variable with the lowest index in the array) satisfying the selection criteria is selected. For many applications that is not sufficient.

A typical example for integer variables is to select a most constrained variable first (the variable most propagators depend on, that is, with largest degree). Then, among the most constrained variables select the variable with the smallest domain. This can be achieved by using the ``tiebreak()`` function:

.. mpg-code:: snippet:m-branch:sec:m:branch:tbl:code:1
   :direct:


The overloaded function ``tiebreak()`` (see `Tie-breaking for variable selection <https://www.gecode.dev/doc/6.4.0/reference/group__TaskModelBranchTieBreak.html>`__) takes up to four variable selection values.

.. container:: samepage

   Random selection is particularly interesting for tie-breaking. For example, breaking ties by first selecting a variable with smallest domain and then selecting a random variable among those with smallest domain is obtained by:

   .. mpg-code:: snippet:m-branch:sec:m:branch:tbl:code:2
      :direct:

Here, ``r`` must be a random number generator as discussed in :ref:`sec:m:branch:rnd`.

.. _modeling:m-branch:using-tie-breaking-limit-functions:

.. rubric:: Using tie-breaking limit functions.

In the discussion so far only exact ties have been considered. Often it is necessary to consider several variables as ties even though some of them are not among the best variables. Which variables are considered as ties can be controlled by *tie-breaking limit functions*.

A tie-breaking limit function has the type `BranchTbl <https://www.gecode.dev/doc/6.4.0/reference/group__TaskModelBranch.html>`__ which is defined as:

.. mpg-code:: snippet:m-branch:sec:m:branch:tbl:code:3
   :direct:


The function takes a constant reference to a space ``home``, the worst merit value ``w``, and the best merit value ``b`` as arguments. The value returned by the function determines which variables are considered as ties.

Let us consider an example where we branch over four integer variables from the integer variable array ``x`` where the domains of the variables are as follows:

.. math::

   \mbox{\texttt{x[0]}}\in\{1,2,3,4\}\qquad
   \mbox{\texttt{x[1]}}\in\{2,3,4\}\qquad
   \mbox{\texttt{x[2]}}\in\{1,2,4\}\qquad
   \mbox{\texttt{x[3]}}\in\{1,2,3,4,5,6,7\}

Without a tie-breaking limit function as in (here, ``r`` is a random number generator):

.. mpg-code:: snippet:m-branch:sec:m:branch:tbl:code:4
   :direct:


the variables ``x[1]`` and ``x[2]`` (both with size as the merit value :math:`3.0`) are considered as ties and random variable selection will choose one of them.

.. container:: samepage

   Likewise, when branching with

   .. mpg-code:: snippet:m-branch:sec:m:branch:tbl:code:5
      :direct:

only variable ``x[3]`` will be considered as the single variable with the best merit value :math:`7.0`.

The following tie-breaking limit function

.. mpg-code:: snippet:m-branch:sec:m:branch:tbl:code:6
   :direct:


returns the average of the worst merit value ``w`` and the best merit value ``b``. Using the function ``tbl()`` for tie-breaking is done by passing it as additional argument.

.. container:: samepage

   For example, when using ``tbl()`` with

   .. mpg-code:: snippet:m-branch:sec:m:branch:tbl:code:7
      :direct:

the function ``tbl()`` is called with :math:`\mathtt{w}=7.0` and :math:`\mathtt{b}=3.0` and returns :math:`(7.0 + 3.0)/2.0=5.0`. Hence, the three variables ``x[0]``, ``x[1]``, and ``x[2]`` are considered for tie-breaking and random selection will make a choice among these three variables.

For example, when using ``tbl()`` with

.. mpg-code:: snippet:m-branch:sec:m:branch:tbl:code:8
   :direct:


the function ``tbl()`` is called with :math:`\mathtt{w}=3.0` and :math:`\mathtt{b}=7.0` and returns :math:`(3.0 + 7.0)/2.0=5.0`. Hence, only variable ``x[3]`` is considered for tie-breaking.

Note that worse and best depends on whether the variable selection tries to minimize or maximize the merit value. If a tie-breaking limit function returns a value that is worse than the worst merit value, all variables are considered for tie-breaking. If a function returns a value that is better than the best value, the returned value is ignored and the best value is considered as limit (in which case, tie-breaking works exactly the same as if not using a tie-breaking limit function at all).

.. _sec:m:branch:sym:


.. _modeling:m-branch:lightweight-dynamic-symmetry-breaking:

Lightweight Dynamic Symmetry Breaking
-------------------------------------

Gecode supports automatic symmetry breaking with *Lightweight Dynamic Symmetry Breaking* (LDSB :cite:`LDSB`). To use LDSB, you specify your problem’s symmetries as part of the ``branch()`` function.

.. mpg-code:: latin square ldsb
   :name: fig:m:branch:latin:ldsb
   :caption: A Gecode model for Latin Squares with LDSB


Consider the model for the Latin Square problem in :numref:`fig:m:branch:latin:ldsb`. A Latin Square is an :math:`\mathtt{n}\times\mathtt{n}` matrix (see :ref:`sec:m:minimodel:matrix`) where each cell takes a value between :math:`0` and :math:`\mathtt n-1` and no two values in a row or a column are the same. This is easily implemented using integer variables and ``distinct`` constraints.

The model has many solutions that are essentially the same due to symmetry. For example, the four solutions in :numref:`fig:m:branch:latin:syms` are symmetric: from the top-left solution, we can get the top-right one by exchanging the first two rows, the bottom-left one by exchanging the second and third column, and the bottom-right one by swapping the values :math:`1` and :math:`3`.

.. mpg-figure:: Symmetric solutions of the Latin Square problem
   :name: fig:m:branch:latin:syms

   = = = =
   0 1 2 3
   = = = =
   1 0 3 2
   2 3 0 1
   3 2 1 0
   = = = =

   = = = =
   1 0 3 2
   = = = =
   0 1 2 3
   2 3 0 1
   3 2 1 0
   = = = =

   = = = =
   0 2 1 3
   = = = =
   1 3 0 2
   2 0 3 1
   3 1 2 0
   = = = =

   = = = =
   0 3 2 1
   = = = =
   3 0 1 2
   2 1 0 3
   1 2 3 0
   = = = =

Gecode supports *dynamic symmetry breaking*, i.e., given a specification of the symmetries, it can avoid visiting symmetric states during the search, which can result in dramatically smaller search trees and greatly improved runtime for some problems.

Symmetries are specified by passing an object of type `Symmetries <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1Symmetries.html>`__ to the ``branch()`` function. In the case of Latin Squares, we can easily break the value symmetry (that is, values that are interchangeable) as follows:

.. mpg-code:: latin square ldsb:symmetry breaking


Here, ``IntArgs::create(n,0)`` creates an array of integers with values :math:`\mathtt 0, \mathtt 1, \ldots, \mathtt{n}-1` which specifies that all these values are symmetric, that is, interchangeable.

For the row and column symmetries, we need to declare a ``VariableSequenceSymmetry`` (see `Symmetry declarations <https://www.gecode.dev/doc/6.4.0/reference/group__TaskModelIntBranchSymm.html>`__), which states that certain *sequences* of variables (in this case the rows and columns) are interchangeable:

.. mpg-code:: latin square ldsb:row/column symmetry


Now the number of Latin squares found and the search effort required are greatly reduced. The code for the example in :numref:`fig:m:branch:latin:ldsb` has command line options for toggling between no symmetry breaking and LDSB.

For examples, consider `Clique-based graph coloring <https://www.gecode.dev/doc/6.4.0/reference/graph-color_8cpp.html>`__ and `Steel-mill slab design problem <https://www.gecode.dev/doc/6.4.0/reference/steel-mill_8cpp.html>`__.

.. _modeling:m-branch:specifying-symmetry:

Specifying Symmetry
~~~~~~~~~~~~~~~~~~~

LDSB supports four basic types of symmetry (see `Symmetry declarations <https://www.gecode.dev/doc/6.4.0/reference/group__TaskModelIntBranchSymm.html>`__). Collections of symmetries are stored in a ``Symmetries`` object, which is passed to the ``branch()`` function. Any combination of symmetries is allowed.

- A ``VariableSymmetry`` represents a set of *variables* that are interchangeable.

- A ``ValueSymmetry`` represents a set of *values* that are interchangeable.

- A ``VariableSequenceSymmetry`` represents a set of *sequences of variables* that are interchangeable.

- A ``ValueSequenceSymmetry`` represents a set of *sequences of values* that are interchangeable.

In addition to constructing these symmetries directly, there are also some convenient functions for creating common kinds of symmetry:

- ``values_reflect()``, to map :math:`L` to :math:`U`, :math:`L+1` to :math:`U-1` and so on, where :math:`L` and :math:`U` are the bounds of a variable

- ``rows_interchange()``, to specify that the rows of a matrix are interchangeable (see `Gecode::Matrix <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1Matrix.html>`__)

- ``columns_interchange()``, to specify that the columns of a matrix are interchangeable (see `Gecode::Matrix <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1Matrix.html>`__)

- ``rows_reflect()``, to specify that a matrix’s rows can be reflected (first row to last row, second row to second-last row and so on, see `Gecode::Matrix <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1Matrix.html>`__)

- ``columns_reflect()``, to specify that a matrix’s columns can be reflected (see `Gecode::Matrix <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1Matrix.html>`__)

- ``diagonal_reflect()``, to specify that a matrix can be reflected around its main diagonal (the matrix must be square, see `Gecode::Matrix <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1Matrix.html>`__)

.. _modeling:m-branch:notes:

Notes
~~~~~

Symmetry breaking by LDSB is not guaranteed to be complete. That is, a search may still return two distinct solutions that are symmetric.

Combining LDSB with other forms of symmetry breaking — such as static ordering constraints — is not safe in general, and can cause the search to miss some solutions.

LDSB works with integer, Boolean, and set variables, and with any variable selection strategy. For integer variables, only value selection strategies that result in the variable being assigned on the left branch (such as ``INT_VAL_MIN()``, ``INT_VAL_MED()``, ``INT_VAL_MAX()`` or ``INT_VAL_RND()``) are supported, other parameters throw an exception.

.. _sec:m:branch:filter:


.. _modeling:m-branch:using-branch-filter-functions:

Using branch filter functions
-----------------------------

By default, a variable-value branching continues to branch until all variables passed to the branching are assigned. This behavior can be changed by using a *branch filter function*.

A branch filter function is called during branching for each variable to be branched on. If the filter function returns ``true``, the variable is considered for branching. Otherwise, the variable is simply ignored.

A branch filter function can be passed as the second to last (optional) argument when calling the ``branch()`` function.

.. container:: samepage

   The type of a branch filter function depends on the variable type. For integer variables, the type `IntBranchFilter <https://www.gecode.dev/doc/6.4.0/reference/group__TaskModelIntBranch.html>`__ is defined as

   .. mpg-code:: snippet:m-branch:sec:m:branch:filter:code:1
      :direct:

That is, a branch filter function takes the ``home`` space and the position ``i`` of the variable ``x`` as argument. The position ``i`` refers to the position of the variable ``x`` in the array of variables used for posting the branching. For Boolean variables, the type is `BoolBranchFilter <https://www.gecode.dev/doc/6.4.0/reference/group__TaskModelIntBranch.html>`__, for set variables `SetBranchFilter <https://www.gecode.dev/doc/6.4.0/reference/group__TaskModelSetBranch.html>`__, and for float variables `FloatBranchFilter <https://www.gecode.dev/doc/6.4.0/reference/group__TaskModelFloatBranch.html>`__.

.. mpg-code:: branch filter function sketch
   :name: fig:m:branch:filter:sketch
   :caption: Model sketch for branch filter function


Assume, for example, that we want to branch only on variables from a variable array ``x`` for branching with a domain size of at least ``4``. Consider the sketch of a model shown in :numref:`fig:m:branch:filter:sketch`.

The branch filter function can be defined as a static member function of the class ``Model`` as follows:

.. mpg-code:: branch filter function sketch:define filter function


Specifying that the branching should use the filter function is done as follows:

.. mpg-code:: branch filter function sketch:post branching


.. _sec:m:branch:print:


.. _modeling:m-branch:using-variable-value-print-functions:

Using variable-value print functions
------------------------------------

Search engines such as Gist (see :ref:`sec:m:gist:print`) or others (see :ref:`tip:s:started:print`) use ``print()`` functions provided by branchers to display information about the alternatives that are explored during search. The information displayed for variable-value branchers can be programmed by using a *variable-value print function*.

A variable-value print function can be passed as the last (optional) argument when calling the ``branch()`` function.

The type of a variable-value print function depends on the variable type. For integer variables, the type `IntVarValPrint <https://www.gecode.dev/doc/6.4.0/reference/namespaceGecode.html>`__ is defined as

.. mpg-code:: snippet:m-branch:sec:m:branch:print:code:1
   :direct:


That is, a variable-value print function takes the ``home`` space, a brancher ``b``, the number of the alternative ``a``, the position ``i`` of the variable ``x``, and the integer value ``n`` as argument. The information will be printed on the standard output stream ``o``. The position ``i`` refers to the position of the variable ``x`` in the array of variables used for posting the branching. For Boolean variables, the type is `BoolVarValPrint <https://www.gecode.dev/doc/6.4.0/reference/namespaceGecode.html>`__, for set variables `SetVarValPrint <https://www.gecode.dev/doc/6.4.0/reference/namespaceGecode.html>`__, and for float variables `FloatVarValPrint <https://www.gecode.dev/doc/6.4.0/reference/namespaceGecode.html>`__.

For an example of how to use variable-value print functions, see :ref:`chap:c:crossword`.

.. _sec:m:branch:assign:


.. _modeling:m-branch:assigning-integer-boolean-set-and-float-variables:

Assigning integer, Boolean, set, and float variables
----------------------------------------------------

A special variant of branching is *assigning* variables: for a not yet assigned variable the branching creates a single alternative which assigns the variable a value. The effect of assigning is that assignment is interleaved with constraint propagation. That is, after an assignment has been done, the next assignment will be done only after the effect of the previous assignment has been propagated.

.. mpg-figure:: Value selection for assigning variables
   :name: fig:m:branch:assign

   .. list-table::
      :widths: 44 56

      * - ``INT_ASSIGN_MIN()``
        - smallest value
      * - ``INT_ASSIGN_MED()``
        - median value (rounding downwards)
      * - ``INT_ASSIGN_MAX()``
        - maximum value
      * - ``INT_ASSIGN_RND(r)``
        - random value
      * - ``INT_ASSIGN(v, c*)``
        - defined by value function ``v`` and commit function ``c``

   .. list-table::
      :widths: 44 56

      * - ``BOOL_ASSIGN_MIN()``
        - smallest value
      * - ``BOOL_ASSIGN_MAX()``
        - maximum value
      * - ``BOOL_ASSIGN_RND(r)``
        - random value
      * - ``BOOL_ASSIGN(v, c*)``
        - defined by value function ``v`` and commit function ``c``

   .. list-table::
      :widths: 44 56

      * - ``SET_ASSIGN_MIN_INC()``
        - include smallest element
      * - ``SET_ASSIGN_MIN_EXC()``
        - exclude smallest element
      * - ``SET_ASSIGN_MED_INC()``
        - include median element (rounding downwards)
      * - ``SET_ASSIGN_MED_EXC()``
        - exclude median element (rounding downwards)
      * - ``SET_ASSIGN_MAX_INC()``
        - include largest element
      * - ``SET_ASSIGN_MAX_EXC()``
        - exclude largest element
      * - ``SET_ASSIGN_RND_INC(r)``
        - include random element
      * - ``SET_ASSIGN_RND_EXC(r)``
        - exclude random element
      * - ``SET_ASSIGN(v, c*)``
        - defined by value function ``v`` and commit function ``c``

   .. list-table::
      :widths: 44 56

      * - ``FLOAT_ASSIGN_MIN()``
        - median value of lower part
      * - ``FLOAT_ASSIGN_MAX()``
        - median value of upper part
      * - ``FLOAT_ASSIGN_RND(r)``
        - median value of randomly chosen part
      * - ``FLOAT_ASSIGN(v, c*)``
        - defined by value function ``v`` and commit function ``c``

For example, the next code fragment assigns all integer variables in ``x`` to their smallest possible value:

.. mpg-code:: snippet:m-branch:fig:m:branch:assign:code:1
   :direct:


with the default variable selection strategy to select the next unassigned variable. All other variable selection criteria can also be used, the following is equivalent to the previous example:

.. mpg-code:: snippet:m-branch:fig:m:branch:assign:code:2
   :direct:


The strategy to select the value for assignment is defined by a value of class `IntAssign <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1IntAssign.html>`__ (see also `Value selection for assigning integer variables <https://www.gecode.dev/doc/6.4.0/reference/group__TaskModelIntBranchAssign.html>`__) for integer variables, by a value of class `BoolAssign <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1BoolAssign.html>`__ (see also `Value selection for assigning integer variables <https://www.gecode.dev/doc/6.4.0/reference/group__TaskModelIntBranchAssign.html>`__) for Boolean variables, by a value of class `SetAssign <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1SetAssign.html>`__ (see also `Assigning set variables <https://www.gecode.dev/doc/6.4.0/reference/group__TaskModelSetBranchAssign.html>`__) for set variables, and by a value of class `FloatAssign <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1FloatAssign.html>`__ (see also `Value selection for assigning float variables <https://www.gecode.dev/doc/6.4.0/reference/group__TaskModelFloatBranchAssign.html>`__) for float variables.

:numref:`fig:m:branch:assign` summarizes the value selection strategies for assigning integer, Boolean, set, and float variables. Here, an argument ``r`` refers to a random number generator of type `Rnd <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1Rnd.html>`__ which is discussed in :ref:`sec:m:branch:rnd`. An argument ``v`` refers to a value selection function of type `IntBranchVal <https://www.gecode.dev/doc/6.4.0/reference/group__TaskModelIntBranch.html>`__ for integer variables, `BoolBranchVal <https://www.gecode.dev/doc/6.4.0/reference/group__TaskModelIntBranch.html>`__ for Boolean variables, `SetBranchVal <https://www.gecode.dev/doc/6.4.0/reference/group__TaskModelSetBranch.html>`__ for set variables, and `FloatBranchVal <https://www.gecode.dev/doc/6.4.0/reference/group__TaskModelFloatBranch.html>`__ for float variables. An optional argument ``c`` refers to a commit function of type `IntBranchCommit <https://www.gecode.dev/doc/6.4.0/reference/group__TaskModelIntBranch.html>`__ for integer variables, of type `BoolBranchCommit <https://www.gecode.dev/doc/6.4.0/reference/group__TaskModelIntBranch.html>`__ for Boolean variables, of type `SetBranchCommit <https://www.gecode.dev/doc/6.4.0/reference/group__TaskModelSetBranch.html>`__ for set variables, and of type `FloatBranchCommit <https://www.gecode.dev/doc/6.4.0/reference/group__TaskModelFloatBranch.html>`__ for float variables. Value and commit function can be used in the same way for assigning than for branching as described in :ref:`sec:m:branch:userval`. The only difference is that the number of the alternative passed to the commit function is always zero (as there is only a single alternative).

The ``assign()`` function also accepts a branch filter function as described in :ref:`sec:m:branch:filter` as well as a variable-value print function as optional argument, see :ref:`sec:m:branch:print` for details, and can assign a single variable.

.. _sec:m:branch:code:


.. _modeling:m-branch:executing-code-between-branchers:

Executing code between branchers
--------------------------------

A common scenario is to post some constraints only after part of the branching has been executed. This is supported in Gecode by a brancher (see `Branch with a function <https://www.gecode.dev/doc/6.4.0/reference/group__TaskModelBranchExec.html>`__) that executes a function (any function that is compatible with the type ``std::function``).

.. container:: samepage

   Suppose the following code fragment defining a model ``Model``:

   .. mpg-code:: exec
      :direct:

where the constructor posts two branchers

.. mpg-code:: exec:post branchings


.. container:: samepage

   The second branching takes a function pointer to the static member function ``Model::post`` which is defined as

   .. mpg-code:: exec:define functions

As soon as the first branching is finished, the second branching is executed. This branching provides just a single alternative that calls the function ``Model::post`` with the current space as its argument. Then, the function casts the ``home`` to ``Model&`` and calls ``more`` on ``home``. While one could post the additional constraints and/or branchings in ``Model::post`` directly, the member function ``Model::more`` is more convenient to use.

.. mpg-tip:: Propagation is still explicit

   It is tempting to believe that the variables in ``x`` in the above example are all assigned when ``more()`` is executed. This is not necessarily true.


   It will be true for the first time ``more()`` is executed. But ``more()`` will be executed possibly quite often during recomputation (see the following Chapter). And then, the only guarantee one can rely on is that the brancher has created enough alternatives to guarantee that the variables in ``x`` are assigned *but only after constraint propagation has been performed* (see :ref:`tip:m:started:status`).

.. [1]
   Gecode cheats a little bit with the implementation of AFC: while it is possible (but not common) to have more than a single AFC object, all will use the same decay-factor ``d``. The decay-factor used is the one defined by the AFC object created last. But as using several AFC objects with different decay-factors is not really that useful, Gecode takes a shortcut here.

.. mpg-covered: caption:docs/src/chapters/modeling/m-branch.tex.in:119:fig:m:branch:int:var:int
.. mpg-covered: table:docs/src/chapters/modeling/m-branch.tex.in:121:tabular@docs/src/chapters/modeling/m-branch.tex.in:121
.. mpg-covered: caption:docs/src/chapters/modeling/m-branch.tex.in:205:fig:m:branch:int:val:int
.. mpg-covered: table:docs/src/chapters/modeling/m-branch.tex.in:207:tabular@docs/src/chapters/modeling/m-branch.tex.in:207
.. mpg-covered: tip:docs/src/chapters/modeling/m-branch.tex.in:286:unlabeled-tip@docs/src/chapters/modeling/m-branch.tex.in:286
.. mpg-covered: caption:docs/src/chapters/modeling/m-branch.tex.in:299:fig:m:branch:int:var:bool
.. mpg-covered: table:docs/src/chapters/modeling/m-branch.tex.in:301:tabular@docs/src/chapters/modeling/m-branch.tex.in:301
.. mpg-covered: caption:docs/src/chapters/modeling/m-branch.tex.in:353:fig:m:branch:int:val:bool
.. mpg-covered: table:docs/src/chapters/modeling/m-branch.tex.in:355:tabular@docs/src/chapters/modeling/m-branch.tex.in:355
.. mpg-covered: caption:docs/src/chapters/modeling/m-branch.tex.in:391:fig:m:branch:set:var
.. mpg-covered: table:docs/src/chapters/modeling/m-branch.tex.in:393:tabular@docs/src/chapters/modeling/m-branch.tex.in:393
.. mpg-covered: caption:docs/src/chapters/modeling/m-branch.tex.in:464:fig:m:branch:set:val
.. mpg-covered: table:docs/src/chapters/modeling/m-branch.tex.in:466:tabular@docs/src/chapters/modeling/m-branch.tex.in:466
.. mpg-covered: caption:docs/src/chapters/modeling/m-branch.tex.in:507:fig:m:branch:float:var
.. mpg-covered: table:docs/src/chapters/modeling/m-branch.tex.in:509:tabular@docs/src/chapters/modeling/m-branch.tex.in:509
.. mpg-covered: caption:docs/src/chapters/modeling/m-branch.tex.in:582:fig:m:branch:float:val
.. mpg-covered: table:docs/src/chapters/modeling/m-branch.tex.in:584:tabular@docs/src/chapters/modeling/m-branch.tex.in:584
.. mpg-covered: caption:docs/src/chapters/modeling/m-branch.tex.in:1051:fig:m:branch:val
.. mpg-covered: table:docs/src/chapters/modeling/m-branch.tex.in:1053:tabular@docs/src/chapters/modeling/m-branch.tex.in:1053
.. mpg-covered: caption:docs/src/chapters/modeling/m-branch.tex.in:1127:fig:m:branch:commit
.. mpg-covered: table:docs/src/chapters/modeling/m-branch.tex.in:1129:tabular@docs/src/chapters/modeling/m-branch.tex.in:1129
.. mpg-covered: caption:docs/src/chapters/modeling/m-branch.tex.in:1295:fig:m:branch:latin:ldsb
.. mpg-covered: literal-projection:docs/src/chapters/modeling/m-branch.tex.in:1296:latin square ldsb
.. mpg-covered: caption:docs/src/chapters/modeling/m-branch.tex.in:1318:fig:m:branch:latin:syms
.. mpg-covered: table:docs/src/chapters/modeling/m-branch.tex.in:1321:tabular@docs/src/chapters/modeling/m-branch.tex.in:1321
.. mpg-covered: table:docs/src/chapters/modeling/m-branch.tex.in:1329:tabular@docs/src/chapters/modeling/m-branch.tex.in:1329
.. mpg-covered: table:docs/src/chapters/modeling/m-branch.tex.in:1339:tabular@docs/src/chapters/modeling/m-branch.tex.in:1339
.. mpg-covered: table:docs/src/chapters/modeling/m-branch.tex.in:1347:tabular@docs/src/chapters/modeling/m-branch.tex.in:1347
.. mpg-covered: literal-projection:docs/src/chapters/modeling/m-branch.tex.in:1369:latin square ldsb:symmetry breaking
.. mpg-covered: literal-projection:docs/src/chapters/modeling/m-branch.tex.in:1380:latin square ldsb:row/column symmetry
.. mpg-covered: caption:docs/src/chapters/modeling/m-branch.tex.in:1499:fig:m:branch:filter:sketch
.. mpg-covered: literal-projection:docs/src/chapters/modeling/m-branch.tex.in:1500:branch filter function sketch
.. mpg-covered: literal-projection:docs/src/chapters/modeling/m-branch.tex.in:1512:branch filter function sketch:define filter function
.. mpg-covered: literal-projection:docs/src/chapters/modeling/m-branch.tex.in:1516:branch filter function sketch:post branching
.. mpg-covered: caption:docs/src/chapters/modeling/m-branch.tex.in:1568:fig:m:branch:assign
.. mpg-covered: table:docs/src/chapters/modeling/m-branch.tex.in:1572:tabular@docs/src/chapters/modeling/m-branch.tex.in:1572
.. mpg-covered: table:docs/src/chapters/modeling/m-branch.tex.in:1582:tabular@docs/src/chapters/modeling/m-branch.tex.in:1582
.. mpg-covered: table:docs/src/chapters/modeling/m-branch.tex.in:1591:tabular@docs/src/chapters/modeling/m-branch.tex.in:1591
.. mpg-covered: table:docs/src/chapters/modeling/m-branch.tex.in:1605:tabular@docs/src/chapters/modeling/m-branch.tex.in:1605
.. mpg-covered: literal-projection:docs/src/chapters/modeling/m-branch.tex.in:1705:exec
.. mpg-covered: literal-projection:docs/src/chapters/modeling/m-branch.tex.in:1708:exec:post branchings
.. mpg-covered: literal-projection:docs/src/chapters/modeling/m-branch.tex.in:1712:exec:define functions
.. mpg-covered: tip:docs/src/chapters/modeling/m-branch.tex.in:1723:unlabeled-tip@docs/src/chapters/modeling/m-branch.tex.in:1723
