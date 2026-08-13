.. _chap:s:engine:

An example engine
=================

This chapter puts all techniques for search and recomputation from :ref:`chap:s:started` and :ref:`chap:s:re` together. It presents a realistic search engine that can be used to search for several solutions.

.. _search-engines:engine:overview:

.. rubric:: Overview.

:ref:`sec:s:engine:design` sketches the design of the example depth-first search engine to be used in this chapter. How the engine is implemented is shown in :ref:`sec:s:engine:imp`. :ref:`sec:s:engine:explore` details how exploration is implemented, whereas :ref:`sec:s:engine:re` details how recomputation is implemented for the search engine.

.. _sec:s:engine:design:

Engine design
-------------

The example engine to be developed in this chapter implements depth-first search using hybrid and adaptive recomputation with full last alternative optimization. It provides an interface similar to the interface of Gecode’s pre-defined search engines: it is initialized with a space (even though the search engine presented here does not make a clone for simplicity) and provides a ``next()`` function that returns a space for the next solution or returns ``NULL`` if there are no more solutions.

.. mpg-covered: caption:docs/src/chapters/search/s-engine.tex.in:34:fig:s:engine:design

.. mpg-covered: figure:docs/src/chapters/search/s-engine.tex.in:34:fig:s:engine:design

.. mpg-covered: literal-projection:docs/src/chapters/search/s-engine.tex.in:35:dfs engine

.. mpg-code:: dfs engine
   :caption: Depth-first search engine
   :name: fig:s:engine:design
   :download:

The outline of the search engine is shown in :numref:`fig:s:engine:design`. To keep things simple, the values for the commit distance ``c_d`` and adaptive distance ``a_d`` are constants. Furthermore, the search engine uses an array of fixed size to implement the path of edges for recomputation. In case the size of the array is exceeded during exploration, an exception of type ``StackOverflow`` is thrown. A real-life engine would of course use a dynamic data structure such as a C++ vector.

.. _sec:s:engine:imp:

Engine implementation
---------------------

.. mpg-covered: caption:docs/src/chapters/search/s-engine.tex.in:53:fig:s:engine:engine

.. mpg-covered: figure:docs/src/chapters/search/s-engine.tex.in:53:fig:s:engine:engine

.. mpg-covered: literal-projection:docs/src/chapters/search/s-engine.tex.in:54:dfs engine:search engine

.. mpg-code:: dfs engine:search engine
   :caption: Implementation of depth-first search engine
   :name: fig:s:engine:engine

:numref:`fig:s:engine:engine` shows the class ``Engine`` implementing depth-first search. The engine maintains a path ``p`` of edges for recomputation (to be explained below), a current space ``s``, and a distance ``d``. The current space ``s`` can be ``NULL``. If the current space ``s`` is not ``NULL``, then the path ``p`` corresponds to ``s``. If the space is ``NULL``, the search engine uses recomputation to compute the next space needed for exploration.

The distance ``d`` describes the number of commit operations needed for recomputation. It is initialized to ``c_d`` to force the immediate creation of a clone on the path (analogous to the search engine in :ref:`sec:s:re:hybrid`).

.. _search-engines:engine:exploration-mode:

.. rubric:: Exploration mode.

The engine operates in two modes: *exploration mode* and *recomputation mode*. It operates in exploration mode while the current space ``s`` is not ``NULL``. Exploration mode continues until the current space ``s`` becomes failed or solved. In both cases, the current space is set to ``NULL``.

If the space ``s`` becomes solved, it is returned as a solution by the ``next()`` function. If the ``next()`` function is called again, then the situation is exactly the same as for failure: the current space is ``NULL`` and the engine switches to recomputation mode. Exploration is detailed in :ref:`sec:s:engine:explore`.

.. _search-engines:engine:recomputation-mode:

.. rubric:: Recomputation mode.

In recomputation mode, the engine tries to recompute the current space. The ``next()`` function of the path ``p`` moves the path to the next alternative. If there is a next alternative (the search space has not yet been completely explored), the ``next()`` function of a path returns ``true``. The ``recompute()`` function tries to recompute the current space ``s`` according to the path ``p``. Due to adaptive recomputation, the ``recompute()`` function might update the distance ``d`` and might actually fail to recompute a space that corresponds to the current path (in which case it returns ``NULL``). Recomputation is detailed in :ref:`sec:s:engine:re`.

If no more alternatives are to be tried (that is, the ``next()`` function of the path ``p`` has returned ``false``), the ``next()`` function of the search engine terminates by returning ``NULL``.

.. _sec:s:engine:explore:

Exploration
-----------

.. mpg-covered: caption:docs/src/chapters/search/s-engine.tex.in:109:fig:s:engine:explore

.. mpg-covered: figure:docs/src/chapters/search/s-engine.tex.in:109:fig:s:engine:explore

.. mpg-covered: literal-projection:docs/src/chapters/search/s-engine.tex.in:110:dfs engine:exploration

.. mpg-code:: dfs engine:exploration
   :caption: Implementation of exploration
   :name: fig:s:engine:explore

The search engine continues in exploration mode while the current space ``s`` is different from ``NULL`` and executes the code shown in :numref:`fig:s:engine:explore`. In case the current space ``s`` is failed, it is discarded, ``s`` is set to ``NULL``, and the engine switches to recomputation mode. The same is true if the engine finds a solution, however it garbage collects branchers on the solution found and returns it. With another invocation of the ``next()`` function, the engine will operate in recomputation mode.

.. _search-engines:engine:edge-implementation:

.. rubric:: Edge implementation.

.. mpg-covered: caption:docs/src/chapters/search/s-engine.tex.in:127:fig:s:engine:edge

.. mpg-covered: figure:docs/src/chapters/search/s-engine.tex.in:127:fig:s:engine:edge

.. mpg-covered: literal-projection:docs/src/chapters/search/s-engine.tex.in:128:dfs engine:edge

.. mpg-code:: dfs engine:edge
   :caption: Implementation of edges
   :name: fig:s:engine:edge

:numref:`fig:s:engine:edge` shows how an edge is implemented. The implementation is analogous to the edge classes used in :ref:`chap:s:re`. Edges support choices with an arbitrary number of alternatives, the test ``la()`` whether an edge is at its last alternative takes the number of alternatives of the choice into account.

Rather than having a default constructor and a destructor, edges use the ``init()`` and ``reset()`` functions. This is more convenient as edges are maintained in an array implementing a stack, see below for details.

.. _search-engines:engine:path-implementation:

.. rubric:: Path implementation.

.. mpg-covered: caption:docs/src/chapters/search/s-engine.tex.in:147:fig:s:engine:path

.. mpg-covered: figure:docs/src/chapters/search/s-engine.tex.in:147:fig:s:engine:path

.. mpg-covered: literal-projection:docs/src/chapters/search/s-engine.tex.in:148:dfs engine:path

.. mpg-code:: dfs engine:path
   :caption: Implementation of path of edges
   :name: fig:s:engine:path

:numref:`fig:s:engine:path` shows how a path of edges is implemented. The array ``e`` stores the edges of the path. The array implements a stack of edges and the unsigned integer ``n`` defines the number of edges that are currently on the stack. The edge at position ``n-1`` of the array of edges ``e`` corresponds to the top of the stack.

.. _search-engines:engine:pushing-edges-on-the-path:

.. rubric:: Pushing edges on the path.

During exploration, the engine pushes new edges on the path ``p`` as shown in :numref:`fig:s:engine:explore`. If the distance ``d`` has reached the commit distance ``c_d``, the engine pushes an edge to the path that has an additional clone and resets the distance ``d`` accordingly.

Pushing an edge checks for stack overflow and initializes the field of the edge array that corresponds to the top of stack as follows:

.. mpg-covered: literal-projection:docs/src/chapters/search/s-engine.tex.in:170:dfs engine:push edge

.. mpg-code:: dfs engine:push edge

Note that the push operation also performs the ``commit()`` operation on the current space ``s`` that corresponds to the edge just pushed onto the path.

.. _sec:s:engine:re:

Recomputation
-------------

In recomputation mode, the engine uses operations to move the engine to the next alternative and to perform recomputation of a space corresponding to the current path.

.. _search-engines:engine:move-to-next-alternative:

.. rubric:: Move to next alternative.

Moving to a next alternative discards all edges from the path that are already at their last alternative (that is, the function ``la()`` returns true). If the engine finds an edge with remaining alternatives, it moves the edge to the next alternative. If no edges are left, the function ``next()`` returns ``false`` as follows:

.. mpg-covered: literal-projection:docs/src/chapters/search/s-engine.tex.in:190:dfs engine:move to next alternative

.. mpg-code:: dfs engine:move to next alternative

.. _search-engines:engine:perform-recomputation:

.. rubric:: Perform recomputation.

.. mpg-covered: caption:docs/src/chapters/search/s-engine.tex.in:194:fig:s:engine:re

.. mpg-covered: figure:docs/src/chapters/search/s-engine.tex.in:194:fig:s:engine:re

.. mpg-covered: literal-projection:docs/src/chapters/search/s-engine.tex.in:195:dfs engine:perform recomputation

.. mpg-code:: dfs engine:perform recomputation
   :caption: Implementation of recomputation
   :name: fig:s:engine:re

The ``recompute()`` function shown in :numref:`fig:s:engine:re` performs recomputation. LAO and adaptive recomputation are orthogonal optimizations and are discussed later. First, ``i`` is initialized such that it points to the closest edge on the path that has a clone. Then, ``s`` is initialized to a clone of the edge’s clone and the distance ``d`` is updated accordingly. Finally, all ``commit()`` operations between ``i`` and ``n`` are performed on ``s``.

.. _search-engines:engine:last-alternative-optimization:

.. rubric:: Last alternative optimization.

Before actually starting recomputation, the ``recompute()`` function checks whether it can perform LAO. It checks whether the last edge of the path can perform LAO (in which case ``t`` is different from NULL) as follows:

.. mpg-covered: literal-projection:docs/src/chapters/search/s-engine.tex.in:215:dfs engine:path:perform lao

.. mpg-code:: dfs engine:path:perform lao

The edge is removed from the path and the distance ``d`` is set to ``c_d`` to force the immediate creation of a new clone when the engine continues in exploration mode.

LAO for an edge checks whether the edge is at the latest alternative and whether the edge stores a clone:

.. mpg-covered: literal-projection:docs/src/chapters/search/s-engine.tex.in:222:dfs engine:edge:perform lao

.. mpg-code:: dfs engine:edge:perform lao

If this is the case, the clone from the edge is removed and is committed to the last alternative.

.. _search-engines:engine:adaptive-recomputation:

.. rubric:: Adaptive recomputation.

.. container:: samepage

   If the current distance ``d`` reaches the adaptive distance ``a_d``, recomputation tries to perform adaptive recomputation as follows:

.. mpg-covered: literal-projection:docs/src/chapters/search/s-engine.tex.in:232:dfs engine:perform adaptive recomputation

.. mpg-code:: dfs engine:perform adaptive recomputation

The value of ``m`` is the middle between the position of the clone ``i`` and the position of the last edge on the path. The position ``m`` is a candidate position where the additional clone might be stored. All commit operations for edges between the clone and edge at position ``m`` are executed.

It is entirely pointless to store the additional clone at an edge that is already at its last alternative (this is what LAO is all about). Hence, adaptive recomputation skips over all edges that are already at their last alternative as follows:

.. mpg-covered: literal-projection:docs/src/chapters/search/s-engine.tex.in:245:dfs engine:skip over last alternatives

.. mpg-code:: dfs engine:skip over last alternatives

An additional clone for an edge is only created if the edge is not already the topmost edge of the path:

.. mpg-covered: literal-projection:docs/src/chapters/search/s-engine.tex.in:249:dfs engine:create additional clone

.. mpg-code:: dfs engine:create additional clone

After storing the clone, the distance ``d`` is adapted accordingly.

Before being able to create a clone, adaptive recomputation performs constraint propagation by executing the ``status()`` function of the space ``s`` as follows:

.. mpg-covered: literal-projection:docs/src/chapters/search/s-engine.tex.in:256:dfs engine:perform propagation

.. mpg-code:: dfs engine:perform propagation

If constraint propagation leads to a failed space (see :ref:`sec:s:re:wmp`), all edges below the failed space are discarded and recomputation returns ``NULL`` to signal that recomputation did not succeed in recomputing a space for the current path.
