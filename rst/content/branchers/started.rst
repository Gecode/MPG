.. only:: latex

   .. mpg-part:: Programming branchers
      :letter: B
      :name: pdf-part:b
      :authors: Christian Schulte

      .. include:: ../parts/branchers.rst
         :start-after: .. mpg-part-blurb-start
         :end-before: .. mpg-part-blurb-end

.. _chap:b:started:

Getting started
===============

This chapters presents how to program branchers as implementations of branchings. It focuses on the basic concepts for programming branchers, more advanced topics are discussed in :ref:`chap:b:advanced`.

.. important::

   You need to read about search and programming propagators before reading this chapter. For search, you need to read :ref:`chap:m:search` first, in particular :ref:`sec:m:search:re`. For programming propagators, the initial :ref:`chap:p:started` is sufficient.

.. _branchers:started:overview:

.. mpg-paragraph:: Overview.

:ref:`sec:b:started:overview` sets the stage for programming branchers by explaining how search engines, spaces, and branchers together implement the branching process during search. A simple brancher is used as an initial example in :ref:`sec:b:started:nonemin`. A brancher that chooses its views for branching according to some criterion is demonstrated in :ref:`sec:b:started:sizemin`.

.. _sec:b:started:overview:

What to implement?
------------------

A *branching* is used in modeling for describing the shape of the search tree. A *brancher* implements a branching. That is, a branching is similar to a constraint, whereas a brancher is similar to a propagator. Branchings take variables as arguments and branchers compute with variable views.

.. _branchers:started:brancher-order:

.. mpg-paragraph:: Brancher order.

Creating a brancher registers it with its home space. A space maintains a queue of its branchers in that the brancher that is registered first is also used first for branching. The first brancher in the queue of branchers is referred to as the *current brancher*.

.. _branchers:started:executing-branchers:

.. mpg-paragraph:: Executing branchers.

A brancher in Gecode is implemented as a subclass of the class :api:`Brancher`. Similar to a propagator, a brancher must implement several virtual member functions defining the brancher’s behavior.

The most important functions of a brancher can be sketched as follows:

- The ``status()`` function tests whether the current brancher has anything left to do.

- The ``choice()`` function creates a *choice* that describes the next alternatives for search. The choice must be independent of the brancher’s home space, and must contain all necessary information for the alternatives.

- The ``commit()`` function takes a previously created choice and commits to one of the choice’s alternatives. Note that ``commit()`` must use only the information in the choice, the domains of the brancher’s views might be weaker, stronger, or incomparable to the domains when the choice was created (due to recomputation, see :ref:`sec:s:re:compatible`).

- The ``print()`` function takes a previously created choice and prints some information of one of the choice’s alternatives.

- The ``ngl()`` function takes a previously created choice and returns a *no-good literal* which then can be used as part of a no-good (see also :ref:`sec:m:search:nogoods`). The no-good literal is an implementation of a typically simple constraint that corresponds to an alternative as described by the choice. No-good literals are mostly orthogonal to the other functions and are hence discussed in the next chapter in section :ref:`sec:b:advanced:nogoods`.

Branchers and propagators are both actors, they both inherit from the class :api:`Actor`. That entails that copying and disposal of branchers is the same as it is for propagators and hence does not require any further discussion (see :ref:`sec:p:started:overview`). Also memory management is identical, see :ref:`chap:p:memory`.

How branchers execute is best understood when studying the operations that are performed by a search engine on a space.

.. _branchers:started:status-computation:

.. mpg-paragraph:: Status computation.

A search engine calls the ``status()`` function of a space to determine whether a space is failed, solved, or must be branched on. When the ``status()`` function of a space is executed, constraint propagation is performed as described in :ref:`sec:p:started:solving`. If the space is failed, ``status()`` returns the value ``SS_FAILED`` (a value of type ``SpaceStatus``, see :api:`TaskSearch`).

Assume that constraint propagation has finished (hence, the space is stable) and the space is not failed. Then, ``status()`` computes the status of the current brancher. The status of a brancher is computed by the virtual ``status()`` member function a brancher implements. If the brancher’s ``status()`` function returns ``false``, the space’s ``status()`` function tries to select the next brancher in the queue of branchers as the current brancher. If there are no branchers left in the queue of branchers, the space’s ``status()`` function terminates and reports that the space is solved (by returning ``SS_SOLVED``). Otherwise the process is repeated until the space has a current brancher such that its ``status()`` function has returned ``true``. In this case, the space’s ``status()`` function returns ``SS_BRANCH`` to signal to the search engine that the space requires branching.

The ``status()`` function of a brancher does not do anything to actually perform branching, it just checks whether there is something left to do for the brancher (for example, whether there are unassigned views left in an array of views to be branched on).

.. _branchers:started:choice-creation:

.. mpg-paragraph:: Choice creation.

In case the space’s ``status()`` function has returned ``SS_BRANCH``, the search engine typically branches. In order to actually branch, the search engine must know how to branch. To keep search engines orthogonal to the space type they compute with (that is, the problem a search engine tries to find solutions for), a search engine can request a *choice* as a description of how to branch. With a choice, a search engine can *commit* a space to a particular alternative as defined by the choice. Alternatives are numbered from zero to the number of alternatives minus one, where the number of alternatives is defined by the choice. A choice is specific to a brancher and must provide sufficient information such that the brancher together with the choice can commit to all possible alternatives.

A search engine requests the computation of a choice by executing the ``choice()`` function of a space. The space’s ``choice()`` function does nothing but returning the choice created by the ``choice()`` function of the current brancher. Let us postpone the discussion of how a choice can store the information needed for branching. A choice always provides two important pieces of information:

- The number of its alternatives (an unsigned integer greater than zero) is available through the function ``alternatives()``.

- A unique identity inherited from the brancher that has created the choice. This information is not available to a programmer but makes it possible for a space to find the corresponding brancher for a given choice (to be detailed below).

A search engine must execute the ``choice()`` function of a space *immediately* after executing the space’s ``status()`` function. Any other action on the space (such as adding propagators or modifying views) might change the current brancher of the space and hence ``choice()`` might fail to compute the correct choice.

.. _branchers:started:committing-to-alternatives:

.. mpg-paragraph:: Committing to alternatives.

Assume that the engine has a choice ``ch`` with two alternatives and that the engine has created a clone ``c`` of the current space ``s`` by [1]_

.. mpg-code:: snippet:b-started:sec:b:started:overview:code:1
   :direct:

The search engine typically commits ``s`` to the first alternative (the alternative with number ``0``) as defined by the space and later it might commit ``c`` to the second alternative (the alternative with number ``1``). Let us first consider committing the space ``s`` to the first alternative by:

.. mpg-code:: snippet:b-started:sec:b:started:overview:code:2
   :direct:

The space’s ``commit()`` function attempts to find a brancher that corresponds to the choice ``ch`` (based on the identity that is stored by the choice). Assume, the space’s ``commit()`` function finds a brancher ``b``. Then it invokes the ``commit()`` function of the brancher ``b`` as follows:

.. mpg-code:: snippet:b-started:sec:b:started:overview:code:3
   :direct:

Now the brancher ``b`` executes its ``commit()`` function. The function typically modifies a view as defined by the choice (``*ch`` in our example) and the number of the alternative (``0`` in our example) passed as arguments. The brancher’s ``commit()`` function must return an executions status that captures whether the operations performed by ``commit()`` have failed (``ES_FAILED`` is returned) or not (``ES_OK`` is returned).

If the space’s ``commit()`` function does not find a brancher that corresponds to the choice ``ch``, an exception of type :api:`SpaceNoBrancher` is thrown. The reason for being unable to find a corresponding brancher is that the search engine is implemented incorrectly (see :ref:`part:s`).

.. container:: samepage

   At some later time, the search engine might decide to explore the second alternative of the choice ``ch`` by using the clone ``c``:

   .. mpg-code:: snippet:b-started:sec:b:started:overview:code:4
      :direct:

Then, the ``commit()`` function of the space ``c`` tries to find the brancher corresponding to ``ch``. This of course will be a different brancher in a different space: however, the brancher found will be a copy of the brancher ``b``.

.. _branchers:started:more-on-choices:

.. mpg-paragraph:: More on choices.

A consequence of the discussion of ``commit()`` is that choices cannot store information that belongs to a particular space: the very idea of a choice is that it can be used with different spaces (above: original and clone)! That also entails that a choice is allocated independently from any space and must be deleted explicitly by a search engine.

Consider as an example a brancher that wants to create the choice :math:`(\mathtt{x}_i = \mathtt n)\vee(\mathtt{x}_i \neq \mathtt n)` where ``x`` is an array of integer views (that is, :math:`\mathtt{x}_i = \mathtt n` is alternative ``0`` and :math:`\mathtt{x}_i \neq \mathtt n` is alternative ``1``). The choice is not allowed to store :math:`\mathtt{x}_i` directly (as :math:`\mathtt{x}_i` belongs to a space), instead it stores the position :math:`i` in the array ``x`` and the integer value ``n``. When the brancher’s ``commit()`` function is executed, the brancher provides the view array ``x`` (the part that is specific to a space) and the choice provides the position :math:`i` and the value ``n`` (the parts that are space-independent). A choice must inherit from the class :api:`Choice`.

.. _branchers:started:even-more-on-archives-of-choices:

.. mpg-paragraph:: Even more on (archives of) choices.

Branchers and choices must support one more operation, the *(un-)archiving* of choices. Archiving enables choices to be used not only in the same search engine with a different space, but transferred to a search engine in a different process, possibly on a different computer. The main application for this are distributed search engines.

An :api:`Archive` is simply an array of unsigned integers, which is easy to transmit e.g. over a network. Every choice must implement a virtual ``archive()`` member function, which in turn calls ``archive()`` on the super class and then writes the contents of the choice into the archive. Conversely, branchers must implement a virtual ``choice()`` member function that gets an archive as the argument and returns a new choice.

.. _branchers:started:brancher-invariants-and-life-cycle:

.. mpg-paragraph:: Brancher invariants and life cycle.

The very idea of a choice is that it is a space-independent description of how to perform commits on a space. Consider the following example scenario: a search engine has a space ``s`` and a clone ``c`` of ``s``. Then, the search engine explores part of the search tree starting from ``s`` and stores a sequence of choices while exploring. Then, the engine wants to recompute a node in the search tree and uses the clone ``c`` for it: it can recompute by performing commits with the choices it has stored.

In this scenario, the brancher to which the choices correspond *must* be able to perform the commits as described by the choices. That in particular entails that a brancher cannot modify its state arbitrarily: it must always guarantee that choices it created earlier (actually, that a copy of it created earlier) can be interpreted correctly.

The ``status()`` and ``choice()`` functions of a brancher can be seen as being orthogonal to its ``commit()`` function. The former functions compute new choices. The latter function must be capable to commit according to other choices that are unrelated to the choice that might be computed by the ``choice()`` function. Even if the ``status()`` function of a brancher has already returned ``false``, the brancher must still be capable of performing commits. Hence, a brancher cannot be disposed immediately when its ``status()`` returns ``false``.

Spaces impose an important invariant on the use of its ``commit()`` and ``choice()`` function. After having executed the ``choice()`` function, no calls to ``commit()`` are allowed with choices created earlier (that is, ``choice()`` invalidates all previously created choices for ``commit()``). That also clarifies when branchers are disposed: the ``choice()`` function of a space disposes all branchers for which their ``status()`` functions have returned ``false`` before. This invariant is essential for recomputation, see :ref:`sec:s:re:compatible`.

.. _par:b:started:gc:

.. mpg-paragraph:: Garbage collection of branchers.

As the ``choice()`` function of a space performs garbage collection of branchers, it can also be called in case the space’s ``status()`` function returned ``SS_SOLVED`` (signaling that no more branchers are left). In this case, the branchers are garbage collected but no choice is returned (instead, ``NULL`` is returned). See :ref:`sec:s:started:dfsbin` for an example and :ref:`sec:s:started:space` for a discussion.

.. _sec:b:started:nonemin:

Implementing a ``nonemin`` branching
------------------------------------

This section presents an example for a branching and its implementing brancher.

The branching

.. mpg-code:: snippet:b-started:sec:b:started:nonemin:code:1
   :direct:

branches by selecting the first unassigned variable :math:`\mathtt{x}_i` in ``x`` and tries to assign :math:`\mathtt{x}_i` to the smallest possible value of :math:`\mathtt{x}_i`.

That is, ``nonemin`` is equivalent to the predefined branching (see :ref:`sec:m:branch:int`) used as

.. mpg-code:: snippet:b-started:sec:b:started:nonemin:code:2
   :direct:

For examples of problem-specific branchers see :ref:`chap:c:knights` and :ref:`chap:c:bpp`.

.. _sec:b:started:nonemin:naive:

A naive brancher
~~~~~~~~~~~~~~~~

.. mpg-covered: caption:docs/src/chapters/search/b-started.tex.in:334:fig:b:started:nonemin

.. mpg-covered: figure:docs/src/chapters/search/b-started.tex.in:334:fig:b:started:nonemin

.. mpg-covered: literal-projection:docs/src/chapters/search/b-started.tex.in:335:none min

.. mpg-code:: none min
   :caption: A branching and brancher for ``nonemin``
   :name: fig:b:started:nonemin
   :download:

:numref:`fig:b:started:nonemin` shows the class ``NoneMin`` implementing the brancher for the branching ``nonemin``. ``NoneMin`` inherits from the class :api:`Brancher`. The branching post function creates a view array and posts a brancher of class ``NoneMin``. The brancher post function does not return an execution status as posting a brancher does not fail (in contrast to a propagator post function, see :ref:`par:p:started:post`). The constructor as well as the brancher post function of ``NoneMin`` are exactly as to be expected from our knowledge on implementing propagators (of course, branchers do not use subscriptions).


.. _branchers:started:status-computation-2:

.. mpg-paragraph:: Status computation.

The status computation of a ``NoneMin`` brancher is straightforward. The ``status()`` function scans all views in the view array ``x`` and returns ``true`` if there is an unassigned view left:

.. mpg-covered: literal-projection:docs/src/chapters/search/b-started.tex.in:358:none min:status

.. mpg-code:: none min:status

.. _branchers:started:choice-computation:

.. mpg-paragraph:: Choice computation.

Computing the choice for a brancher involves two aspects: the definition of the class for the choice object and the ``choice()`` member function of a brancher that creates choice objects.

The choice object ``PosVal`` inherits from the class :api:`Choice`. The information that is required for committing is which view and which value should be used. As discussed above, the ``PosVal`` choice does not store the view directly, but the position ``pos`` of the view in the view array ``x``. A ``PosVal`` choice stores both position and value as integers as follows:

.. mpg-covered: literal-projection:docs/src/chapters/search/b-started.tex.in:373:none min:choice definition

.. mpg-code:: none min:choice definition

The constructor of ``PosVal`` uses the constructor of ``Choice`` for initialization, where both the brancher ``b`` and the number of alternatives of the choice (``2`` for ``PosVal``) are passed as arguments. The ``archive()`` function calls ``Choice::archive()`` and then writes the position and value to the archive.

The ``choice(Space& home)`` member function of the brancher is called directly (by the ``choice(Space& home)`` function of a space) after the ``status()`` function of the brancher in case the ``status()`` of the brancher has returned ``true``. That is, the brancher is the current brancher of the space and still needs to create choices for branching. For a ``NoneMin`` brancher that means that there is definitely a not yet assigned view in the view array ``x``, and that the brancher must choose the first unassigned view:

.. mpg-covered: literal-projection:docs/src/chapters/search/b-started.tex.in:388:none min:choice

.. mpg-code:: none min:choice

The ``choice(Space& home)`` function returns a new ``PosVal`` object for position ``i`` and the smallest value of ``x[i]``. The ``choice(const Space&, Archive& e)`` function creates a choice from the information contained in the archive.

.. mpg-tip:: Never execute
   :name: tip:b:started:never

   The macro ``GECODE_NEVER`` states that it will never be executed. If compiled in debug mode, ``GECODE_NEVER`` corresponds to the assertion ``assert(false)``. If compiled in release mode, the macro informs the compiler (depending on the platform) that ``GECODE_NEVER`` is never executed so that the compiler can take advantage of this information for optimization.


.. _branchers:started:committing-to-alternatives-2:

.. mpg-paragraph:: Committing to alternatives.

The ``commit()`` function of ``NoneMin`` can safely assume that the choice ``c`` passed as argument is in fact an object ``pv`` of class ``PosVal``. This is due to the fact that the space ``commit()`` function uses the identity stored in a choice object to find the corresponding brancher.

.. mpg-covered: literal-projection:docs/src/chapters/search/b-started.tex.in:411:none min:commit

.. mpg-code:: none min:commit

From the ``PosVal`` object the position of the view ``pos`` and the value ``val`` are extracted. Then, if the commit is for the first alternative (``a`` is ``0``), the brancher assigns the view ``x[pos]`` to ``val`` using the view modification operation ``eq`` (see :numref:`fig:p:started:modify`). If the modification operation returns a modification event signaling failure, ``me_failed`` is true and hence the execution status ``ES_FAILED`` is returned. Otherwise, ``ES_OK`` is returned as execution status. If the commit is for the second alternative (``a`` is ``1``), the value ``val`` is excluded from the view ``x[pos]``.

.. _par:b:started:print:

.. mpg-paragraph:: Printing information on alternatives.

The ``print()`` function of ``NoneMin`` is straightforward, it prints on the standard output stream ``o`` information about an alternative (it prints what ``commit()`` does):

.. mpg-covered: literal-projection:docs/src/chapters/search/b-started.tex.in:430:none min:print

.. mpg-code:: none min:print

The ``print()`` function is used for displaying information about alternatives explored during search. For example, it is used in Gist (see :ref:`sec:m:gist:print`) or can be used in other search engines (see :numref:`tip:s:started:print`).

.. _sec:b:started:nonemin:improved:

Improving status and choice
~~~~~~~~~~~~~~~~~~~~~~~~~~~

The ``status()`` and ``choice()`` functions of ``NoneMin`` as defined in :numref:`fig:b:started:nonemin` are inefficient as they always inspect the entire view array for finding the first unassigned view.

.. mpg-covered: caption:docs/src/chapters/search/b-started.tex.in:446:fig:b:started:improved

.. mpg-covered: figure:docs/src/chapters/search/b-started.tex.in:446:fig:b:started:improved

.. mpg-covered: literal-projection:docs/src/chapters/search/b-started.tex.in:447:none min improved

.. mpg-code:: none min improved
   :caption: An improved brancher for ``nonemin``
   :name: fig:b:started:improved
   :download:

The brancher shown in :numref:`fig:b:started:improved` stores an integer ``start`` to remember which of the views in ``x`` are already assigned. The brancher maintains the invariant that all :math:`\mathtt{x}_i` are assigned for :math:`0\leq i<\mathtt{start}`. The value of ``start`` will be updated by the ``status()`` function which must be declared as ``const``. As ``start`` is updated by a ``const``-function, it is declared as ``mutable``.

The ``choice()`` function of an improved ``NoneMin`` brancher can rely on the fact that ``x[start]`` is the first unassigned view in the view array ``x``.

.. _sec:b:started:sizemin:

Implementing a ``sizemin`` branching
------------------------------------

This section presents an example for a brancher that implements a more interesting selection of the view to branch on. The branching

.. mpg-code:: snippet:b-started:sec:b:started:sizemin:code:1
   :direct:

branches by selecting the variable in ``x`` with smallest domain size first and tries to assign the selected variable to its smallest possible value. That is, ``sizemin`` is equivalent to the predefined branching (see :ref:`sec:m:branch:int`) if used as

.. mpg-code:: snippet:b-started:sec:b:started:sizemin:code:2
   :direct:

.. mpg-covered: caption:docs/src/chapters/search/b-started.tex.in:484:fig:b:started:sizemin

.. mpg-covered: figure:docs/src/chapters/search/b-started.tex.in:484:fig:b:started:sizemin

.. mpg-covered: literal-projection:docs/src/chapters/search/b-started.tex.in:485:size min

.. mpg-code:: size min
   :caption: A brancher for ``sizemin``
   :name: fig:b:started:sizemin
   :download:

:numref:`fig:b:started:sizemin` shows the brancher ``SizeMin`` implementing the ``sizemin`` branching. The ``status()`` function is not shown as it is exactly the same function as for ``NoneMin`` from the previous section: after all, the brancher is done only after all of its views are assigned. Likewise, the ``PosVal`` choice and the ``commit()`` and ``print()`` functions are unchanged.

The ``choice()`` function uses the integer ``p`` for the position of the unassigned view with the so-far smallest domain size and the unsigned integer ``s`` for the so-far smallest size. Then, all views that are not known to be assigned are scanned to find the view with smallest domain size. Keep in mind that due to the invariant enforced by the brancher’s ``status()`` function, ``x[start]`` is not assigned.

It is absolutely essential to skip already assigned views. If assigned views were not skipped, then the same choice would be created over and over again leading to an infinite search tree.

.. [1]
   Note that search engines compute with pointers to spaces and choices rather than references, hence ``s``, ``c``, and ``ch`` are pointers.
