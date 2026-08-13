.. only:: latex

   .. mpg-part:: Programming search engines
      :letter: S
      :name: pdf-part:s
      :authors: Christian Schulte

      .. include:: ../parts/search-engines.rst
         :start-after: .. mpg-part-blurb-start
         :end-before: .. mpg-part-blurb-end

.. _chap:s:started:

Getting started
===============

This chapters presents how to implement simple search engines. The focus is on understanding the basic operations available on spaces to implement search engines. None of the engines presented here is realistic as they do not use recomputation. The full picture is developed in :ref:`chap:s:re` and :ref:`chap:s:engine`.

.. _search-engines:started:overview:

.. mpg-paragraph:: Overview.

:ref:`sec:s:started:space` sets the stage by explaining space operations for programming search engines. A depth-first search engine that makes the simplifying assumption that all choices explored during search are binary is shown in :ref:`sec:s:started:dfsbin`. The next section, :ref:`sec:s:started:dfs`, shows depth-first search for choices with an arbitrary number of alternatives. How best solution search can be programmed from spaces is exemplified by a simple branch-and-bound search engine in :ref:`sec:s:started:bab`.

.. _sec:s:started:space:

Space-based search
------------------

Search engines compute with spaces: a space implements a constraint model and exploration of its search space is implemented by operation on spaces. The operations on spaces include: computing the status of a space by the ``status()`` function, creating a clone of a space by the ``clone()`` function, and committing to an alternative of a choice by the ``commit()`` function. To commit to an alternative, a space provides the function ``choice()`` that returns a choice defining how the space can be committed to one of its alternatives. Another operation required to program exploration is the function ``alternatives()`` defined by a choice that returns the number of alternatives of a choice.

Spaces implement also a ``constrain()`` function for best solution search. Its discussion is postponed to :ref:`sec:s:started:bab`.

This section reviews the above operations from the perspective of a search engine, the perspective how branchers are controlled by these operations is detailed in :ref:`sec:b:started:overview`. Gecode’s architecture for search is designed such that a search engine does not need to know *which* problem is being solved by a search engine: any problem implemented with spaces can be solved by a search engine, and different search engines can be used for solving the same problem. The basic idea of this factorization is due to :cite:p:`Schulte:LNAI:2002`.

Note that here and in the following, spaces and choices are always assumed to be *pointers* to the respective objects. Pointers are necessary as search engines dynamically create and delete spaces and choices.

.. _search-engines:started:status-computation:

.. mpg-paragraph:: Status computation.

A search engine needs to decide how to proceed during search by computing the *status* of a space by invoking its ``status()`` function. The ``status()`` function performs constraint propagation (see :ref:`sec:p:started:solving`) followed by determining the next brancher for branching, if possible (see :ref:`sec:b:started:overview`). Depending on the result of constraint propagation and brancher selection, the ``status()`` function returns one of the following values of the type ``SpaceStatus`` (see :api:`TaskSearch`):

- ``SS_FAILED``: the space is *failed*. The search engine needs to backtrack and revisit other spaces encountered during exploration.

  An important responsibility of a search engine is to perform resource management for spaces. In the case of failure, the typical action is to delete the failed space.

- ``SS_SOLVED``: the space is *solved*. Hence the search engine has found a solution and typically returns the solution.

  For most engines, the responsibility for deleting a solution lies with the user of a search engine.

  Following the discussion in :ref:`par:b:started:gc`, calling the ``choice()`` function of a solved space performs garbage collection for branchers that are not any longer needed. :ref:`sec:s:started:dfsbin` shows an example search engine that performs garbage collection on solved spaces.

- ``SS_BRANCH``: the space requires branching for search to proceed.

  The first step in branching is to compute a choice by calling the ``choice()`` function of a space. The returned choice can be used for committing to alternatives of a space. In particular, a choice returned by the ``choice()`` function provides a function ``alternatives()`` that returns how many alternatives the choice has.

  The pointer to the choice that is returned by the ``choice()`` function of a space ``s`` is ``const``. That is, the following code:

  .. mpg-code:: snippet:s-started:sec:s:started:space:code:1
     :direct:
     :small:

  gets a ``const`` pointer to a choice (the choice cannot be modified). Note that it is the obligation of the search engine to eventually delete the choice by

  .. mpg-code:: snippet:s-started:sec:s:started:space:code:2
     :direct:
     :small:

.. _search-engines:started:cloning-spaces:

.. mpg-paragraph:: Cloning spaces.

A central requirement for a search engine is that it can return to a previous state: as spaces constitute the nodes of the search tree, a previous state is nothing but a space again. Returning to a previous space might be necessary because an alternative suggested by a branching did not lead to a solution, or, even if a solution has been found, more solutions might be requested.

As propagation and branching modify spaces, provisions must be taken that search can actually return to the clone of a previous space. This is provided by the ``clone()`` function of a space: it returns a clone of a space. This clone can be stored by a search engine such that the engine can return to a previous state. Spaces that are clones of each other are *equivalent*: space operations will have exactly the same effect on equivalent spaces.

The ``clone()`` function of a space can only be called on a space that is stable and not failed (that is, the ``status()`` function on a space must return ``SS_SOLVED`` or ``SS_BRANCH``). Otherwise, Gecode throws an exception of type :api:`SpaceNotStable` if the space is not stable and of type :api:`SpaceFailed` if the space is failed.

.. _search-engines:started:committing-to-alternatives:

.. mpg-paragraph:: Committing to alternatives.

Given a space ``s`` and a choice ``ch`` (assumed to be a ``const`` pointer), the space ``s`` can be committed to the ``i``-th alternative by calling the ``commit()`` function of a space as follows:

.. mpg-code:: snippet:s-started:sec:s:started:space:code:3
   :direct:

The choice ``ch`` must be *compatible* with the space ``s``. Before defining when a choice is compatible with a space, let us look at two examples.

Suppose a search engine has invoked ``status()`` on a space ``s`` which returned ``SS_BRANCH``. The next step is to obtain a choice ``ch`` for ``s`` and a clone ``c`` of ``s`` by:

.. mpg-code:: snippet:s-started:sec:s:started:space:code:4
   :direct:

Further assume that the choice is binary (that is, ``ch->alternatives()`` returns ``2``). A search engine can explore both alternatives (typically, the search engine performs the ``commit()`` for the second [1]_ alternative much later) by:

.. mpg-code:: snippet:s-started:sec:s:started:space:code:5
   :direct:

That is, a choice ``ch`` is compatible with the space ``s`` from which it has been computed and with the clone ``c`` of ``s``.

.. mpg-tip:: Printing information about alternatives.
   :name: tip:s:started:print

   Sometimes it might be helpful to print what the ``commit()`` function does. For this reason, a space provides a ``print()`` function that compared to ``commit()`` takes an output stream of type ``std::ostream&`` as additional argument.

   For example, the following

   .. mpg-code:: snippet:s-started:tip:s:started:print:code:1
      :direct:

   prints information about what the ``commit()`` function in the above example actually does.

A search engine for best solution search performs slightly different operations. Let us follow an example scenario. First, the search engine starts exploring the first alternative by:

.. mpg-code:: snippet:s-started:tip:s:started:print:code:2
   :direct:

Then search continues with ``s``. Let us assume that the search engine finds a better solution when continuing search from ``s``. Hence, the search engine adds additional constraints to the clone ``c`` to make sure that exploration from ``c`` yields a better solution (the constraints are added by calling the ``constrain()`` function of a space, see :ref:`sec:s:started:bab`). And only then the search engine commits the clone ``c`` to the second alternative by:

.. mpg-code:: snippet:s-started:tip:s:started:print:code:3
   :direct:

That is, a choice ``ch`` is also compatible with the clone ``c`` of ``s``, even though additional constraints have been added to ``c`` after it had been created by cloning.

In fact, the relation that a choice is compatible with a space is quite liberal. The full notion of compatibility is needed for recomputation and is discussed in :ref:`sec:s:re:compatible`.

.. _search-engines:started:parallel-search:

.. mpg-paragraph:: Parallel search.

Gecode’s kernel is constructed that clones of spaces can be used in different threads. Howeever, no two threads can simultaneously perform operations on the same space.

.. _search-engines:started:statistics-support:

.. mpg-paragraph:: Statistics support.

The three main space operations (``status()``, ``clone()``, and ``commit()``) provide support for execution statistics. For example, statistics from the execution of ``status()`` on a space ``s`` can be collected in the object ``stat`` by:

.. mpg-code:: snippet:s-started:tip:s:started:print:code:4
   :direct:

The classes for the statistics correspond to the space operations:

.. mpg-covered: table:docs/src/chapters/search/s-started.tex.in:243:tabular@docs/src/chapters/search/s-started.tex.in:243

.. container:: center

   ============ ==============================
   ``status()`` :api:`StatusStatistics`
   ``clone()``  :api:`CloneStatistics`
   ``commit()`` :api:`CommitStatistics`
   ============ ==============================

Statistics information is collected by accumulation. That is, for spaces ``s1`` and ``s2``, the following:

.. mpg-code:: snippet:s-started:tip:s:started:print:code:5
   :direct:

collects the combined statistics of performing ``status()`` on ``s1`` and ``s2``.

.. container:: samepage

   The statistics classes also implement addition operators. The following is equivalent to the previous example:

   .. mpg-code:: snippet:s-started:tip:s:started:print:code:6
      :direct:

which is also equivalent to:

.. mpg-code:: snippet:s-started:tip:s:started:print:code:7
   :direct:

.. _sec:s:started:dfsbin:

Binary depth-first search
-------------------------

This section shows a simple search engine that performs left-most depth-first search. It makes the additional simplification that all choices are binary, the general case is discussed in :ref:`sec:s:started:dfs`.

.. mpg-covered: caption:docs/src/chapters/search/s-started.tex.in:293:fig:s:started:dfsbin

.. mpg-covered: figure:docs/src/chapters/search/s-started.tex.in:293:fig:s:started:dfsbin

.. mpg-covered: literal-projection:docs/src/chapters/search/s-started.tex.in:294:dfs binary

.. mpg-code:: dfs binary
   :caption: Depth-first search for binary choices
   :name: fig:s:started:dfsbin
   :download:

:numref:`fig:s:started:dfsbin` shows the definition of the function ``dfs()`` that implements the search engine. It takes a space as input and returns a space as a solution or ``NULL`` if no solution exists. The resource policy it implements is that it takes responsibility for deleting the space ``s`` with which ``dfs()`` is called initially. The solution it returns must eventually be deleted by the caller of ``dfs()`` (if the initial space happens to be a solution, the engine does not delete it). The search engine starts by executing the ``status()`` function on ``s`` and hence triggers propagation and possibly brancher selection.

In this chapter and in :ref:`chap:s:re` we use recursive functions to implement exploration during search. This is rather inefficient with respect to both runtime and space in C++. A more realistic implementation uses an explicit stack, for an example see :ref:`chap:s:engine`.

.. _search-engines:started:failure-and-solutions:

.. mpg-paragraph:: Failure and solutions.

In case the space ``s`` is failed, the search engine deletes the space and returns ``NULL`` as specified:

.. mpg-covered: literal-projection:docs/src/chapters/search/s-started.tex.in:322:dfs binary:failed

.. mpg-code:: dfs binary:failed

.. container:: samepage

   If the space ``s`` is solved, the search engine triggers garbage collection of remaining branchers as mentioned in :ref:`sec:s:started:space` and returns the solution:

.. mpg-covered: literal-projection:docs/src/chapters/search/s-started.tex.in:328:dfs binary:solved

.. mpg-code:: dfs binary:solved

.. _search-engines:started:branching:

.. mpg-paragraph:: Branching.

Following the discussion in :ref:`sec:s:started:space`, before the search engine can start committing to alternatives and perform recursive search, it needs to compute a choice for committing and a clone for backtracking:

.. mpg-covered: literal-projection:docs/src/chapters/search/s-started.tex.in:337:dfs binary:prepare for branching

.. mpg-code:: dfs binary:prepare for branching

The search engine tries the first alternative by committing the space ``s`` to it and continues search recursively:

.. mpg-covered: literal-projection:docs/src/chapters/search/s-started.tex.in:341:dfs binary:first alternative

.. mpg-code:: dfs binary:first alternative

If the recursive call to ``dfs()`` returns a solution (that is, ``t`` is different from ``NULL`` and hence the condition of the ``if`` statement is ``true``) the engine deletes both choice and clone and returns the solution ``t``.

.. _search-engines:started:saving-memory:

.. mpg-paragraph:: Saving memory.

It is *absolutely essential* that the search engine uses the original space ``s`` for further exploration and stores the clone ``c`` for backtracking. Exchanging the roles of ``s`` and ``c`` by:

.. mpg-code:: snippet:s-started:fig:s:started:dfsbin:code:1
   :direct:

would also find the same solution. However, this search engine would most likely need more memory. Spaces that already have been used for propagation (such as ``s``) typically require more memory than a pristine clone (see also :ref:`sec:p:memory:state`). Hence, any search engine should maintain the invariant that it stores pristine clones for backtracking, but never spaces that have been used for propagation.

If the first alternative did not lead to a solution, search commits the clone ``c`` to the second alternative, deletes the now unneeded choice, and recursively continues search:

.. mpg-covered: literal-projection:docs/src/chapters/search/s-started.tex.in:372:dfs binary:second alternative

.. mpg-code:: dfs binary:second alternative

.. _sec:s:started:dfs:

Depth-first search
------------------

This section demonstrates how left-most depth-first search with choices having an arbitrary number of alternatives can be implemented. By this, the section presents the general version of the search engine from :ref:`sec:s:started:dfsbin`.

.. mpg-covered: caption:docs/src/chapters/search/s-started.tex.in:383:fig:s:started:dfs

.. mpg-covered: figure:docs/src/chapters/search/s-started.tex.in:383:fig:s:started:dfs

.. mpg-covered: literal-projection:docs/src/chapters/search/s-started.tex.in:384:dfs

.. mpg-code:: dfs
   :caption: Depth-first search
   :name: fig:s:started:dfs
   :download:

:numref:`fig:s:started:dfs` outlines the depth-first search engine, where computing the space status and handling failed and solved spaces is the same as in :ref:`sec:s:started:dfsbin`. If the search engine needs to branch, it computes the choice ``ch`` for branching and the number of alternatives ``n``.

Choices can actually have a single alternative, for example for assigning variables (see :ref:`sec:m:branch:assign`). This special case should be optimized as in fact no clone needs to be stored for backtracking. Hence:

.. mpg-covered: literal-projection:docs/src/chapters/search/s-started.tex.in:401:dfs:single alternative

.. mpg-code:: dfs:single alternative

.. container:: samepage

   If the choice has more than a single alternative, a clone ``c`` is created and a loop iterates over all alternatives:

.. mpg-covered: literal-projection:docs/src/chapters/search/s-started.tex.in:406:dfs:several alternatives

.. mpg-code:: dfs:several alternatives

If the loop terminates, no solution has been found and hence ``NULL`` is returned.

When trying the ``a``-th alternative, the search engine determines which space ``e`` to choose to continue exploration:

.. mpg-covered: literal-projection:docs/src/chapters/search/s-started.tex.in:414:dfs:space to explore

.. mpg-code:: dfs:space to explore

The choice of ``e`` avoids the creation of an unnecessary clone for the last alternative.

After committing the space to explore the ``a``-th alternative, search continues recursively. If a solution ``t`` has been found, it is returned after the search engine deletes the clone (unless it has already been used for the last alternative) and the choice:

.. mpg-covered: literal-projection:docs/src/chapters/search/s-started.tex.in:422:dfs:recursive search

.. mpg-code:: dfs:recursive search

.. _sec:s:started:bab:

Branch-and-bound search
-----------------------

This section shows how to program a best solution search engine. It chooses branch-and-bound search as an example where choices are again assumed to binary for simplicity. The non-binary case can be programmed similar to :ref:`sec:s:started:dfs`.

.. _search-engines:started:constraining-spaces:

.. mpg-paragraph:: Constraining spaces.

A space to be used for best solution search must implement a ``constrain()`` function as discussed in :ref:`sec:m:started:search-best`. The key aspect of a best solution search engine is that it must be able to add constraints to a space such that the space can only lead to solutions that are better than a previously found solution.

Assume that a best solution search engine has found a so-far best solution ``b`` (a space). Then, by

.. mpg-code:: snippet:s-started:sec:s:started:bab:code:1
   :direct:

the engine can add constraints to the space ``s`` that guarantee that only solutions that are better than ``b`` are found by search starting from ``s``.

The :api:`Space` class actually already implements a ``constrain()`` function which does nothing. That is, a space to be used with a best solution search engine must redefine the default ``constrain()`` function by inheritance.

.. _search-engines:started:search-engine:

.. mpg-paragraph:: Search engine.

.. mpg-covered: caption:docs/src/chapters/search/s-started.tex.in:459:fig:s:started:bab

.. mpg-covered: figure:docs/src/chapters/search/s-started.tex.in:459:fig:s:started:bab

.. mpg-covered: literal-projection:docs/src/chapters/search/s-started.tex.in:460:bab

.. mpg-code:: bab
   :caption: Branch-and-bound search
   :name: fig:s:started:bab
   :download:

The basic structure of the branch-and-bound search engine is shown in :numref:`fig:s:started:bab`. A user of the search engine calls the function ``bab()`` taking a single space as argument. The function either returns the best solution or ``NULL`` if no solution exists.

The function ``bab()`` that takes three arguments implements the actual exploration. The space ``s`` is the space that is currently being explored, the unsigned integer ``n`` counts the number of solutions found so far, and the space ``b`` is the so-far best solution. Note that both ``n`` and ``b`` are passed by reference and hence the variables are shared between all recursive invocations of the search engine. The number of solutions ``n`` is used for deciding when a space must be constrained to yield better solutions.

The single argument ``bab()`` function initializes ``n`` and ``b`` to capture that no solution has been found yet. After executing the ``bab()`` search engine, ``b`` refers to the best solution (or is ``NULL``) and is returned after garbage collecting remaining branchers.

.. _search-engines:started:finding-a-solution:

.. mpg-paragraph:: Finding a solution.

The search engine is constructed such that every solution found is better than the previous. Hence, when a solution is found, the previous so-far best solution is deleted [2]_ and is updated to the newly found solution. As a new solution is found also the number of solutions ``n`` is incremented:

.. mpg-covered: literal-projection:docs/src/chapters/search/s-started.tex.in:496:bab:solved

.. mpg-code:: bab:solved

The search engine first garbage collects branchers (by calling ``choice()``) and remembers a pristine clone of the solution found.


.. _search-engines:started:branching-2:

.. mpg-paragraph:: Branching.

Exploring the first alternative differs considerably from exploring the second alternative of a choice. When exploring the first alternative, it is guaranteed that the current space ``s`` can only lead to better solutions. If a solution is found by exploring the first alternative (or if several solutions are found), then a constraint must be added to the clone ``c`` such that only better solutions can be found when continuing exploration with ``c`` for the second alternative. To detect whether a solution has been found when exploring the first alternative, the search engine remembers the number of solutions ``m`` before starting to explore the first alternative as follows:

.. mpg-covered: literal-projection:docs/src/chapters/search/s-started.tex.in:514:bab:remember number of solutions

.. mpg-code:: bab:remember number of solutions

Exploring the first alternative is as to be expected:

.. mpg-covered: literal-projection:docs/src/chapters/search/s-started.tex.in:517:bab:explore first alternative

.. mpg-code:: bab:explore first alternative

Before exploring the second alternative, the engine checks whether new solutions have been found during the exploration of the first alternative. If new solutions have been found, the clone ``c`` is constrained to yield better solutions:

.. mpg-covered: literal-projection:docs/src/chapters/search/s-started.tex.in:523:bab:constrain clone

.. mpg-code:: bab:constrain clone

.. container:: samepage

   The second alternative is explored as follows:

.. mpg-covered: literal-projection:docs/src/chapters/search/s-started.tex.in:527:bab:explore second alternative

.. mpg-code:: bab:explore second alternative

Note that execution of the ``constrain()`` function might constrain some variables and possibly add new propagators (even new variables). Even though ``c`` might not be any longer an identical clone of ``s``, the choice ``ch`` is still compatible with the space ``c`` (see :ref:`sec:s:started:space`).

.. [1]
   Even though the alternatives are numbered starting from ``0`` we refer to the alternative with number ``0`` as the first alternative and the alternative with number ``1`` as the second alternative.

.. [2]
   Actually, ``b`` is ``NULL`` for the first solution found. However, it is legal in C++ to invoke the ``delete`` operator on a ``NULL``-pointer.
