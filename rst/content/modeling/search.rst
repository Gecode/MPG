.. _chap:m:search:


.. _modeling:m-search:search:

Search
======

This chapter discusses how *exploration* for search is used for solving Gecode models. Exploration defines a strategy how to explore parts of the search tree and how to possibly modify the tree’s shape during exploration (for example, during branch-and-bound best solution search by adding new constraints). This chapter restricts itself to simple search engines to find solutions, Gist as an interactive and graphical search engine is discussed in :ref:`chap:m:gist`.

.. _modeling:m-search:overview:

.. rubric:: Overview.

:ref:`sec:m:search:re` explains how search in Gecode makes use of hybrid recomputation and why it is efficient. Even though this section does not belong to the basic reading material, you are highly encouraged to read it.

:ref:`sec:m:search:parallel` explains how parallel search can be used in Gecode and what can be expected of parallel search in principle. How search engines can be used is explained in :ref:`sec:m:search:simple`. Restart-based search is discussed in :ref:`sec:m:search:restart` and portfolio-based search is discussed in :ref:`sec:m:search:portfolio`. This is followed by a discussion in :ref:`sec:m:search:nogoods` how no-goods from restarts can be used. :ref:`sec:m:search:trace` describes how the execution of search engines can be traced and :ref:`sec:m:search:cpprofiler` how the CPProfiler can be used for tracing during search.

.. container:: convention

   Note that the same conventions hold as in :ref:`chap:m:int`.

.. _sec:m:search:re:


.. _modeling:m-search:hybrid-recomputation:

Hybrid recomputation
--------------------

A central requirement for search is that it can return to previous states: as spaces constitute nodes of the search tree, a previous state is nothing but a space. Returning to a previous space might be necessary because an alternative suggested by a branching did not lead to a solution, or even if a solution has been found more solutions might be requested. As propagation and branching change spaces, provisions must be taken that search can actually return to a previous space, or an equivalent version of that space.

Two space are *equivalent* if propagation and branching and hence search behave exactly the same on both spaces. Equivalent spaces can be different, for example, they contain different yet equivalent propagators, or are allocated at a different memory area.

Gecode employs a hybrid of two techniques for restoring spaces: *recomputation* and *cloning*.

If you want to know how search engines can be programmed in Gecode, please consult :ref:`part:s`.

.. _modeling:m-search:cloning:

Cloning
~~~~~~~

Cloning creates a clone of a space (this is supported by the virtual ``copy`` member function as discussed in :ref:`chap:m:started`). A clone and the original space are of course equivalent. Restoration with cloning is straightforward: before following a particular alternative during search, a clone of the space is made and used later if necessary.

Remember :ref:`tip:m:started:donotusecopyconstructor`. To create a clone of a Space the clone member function should be called, not the copy function nor the copy constructor.

.. _sec:m:search:recomp:


.. _modeling:m-search:recomputation:

Recomputation
~~~~~~~~~~~~~

Recomputation remembers what has happened during branching: rather than storing an entire clone of a space just enough information to redo the effect of a brancher is stored. The information stored is called a *choice* in Gecode. Redoing the effect is called to *commit* a space: given a space and a choice committing re-executes the brancher as described by the choice and the alternative to be explored (for example, left or right).

Consider the following part of a model, which constrains both the sum and the product of ``x[0]`` and ``x[1]`` to be equal to ``x[2]``:

.. mpg-code:: snippet:m-search:sec:m:search:recomp:code:1
   :direct:


.. figure:: /figures/fig-m-search-tree.svg
   :name: fig:m:search:tree

   Example search tree

The corresponding search tree is shown in :numref:`fig:m:search:tree`. A red box corresponds to a failed node, a green diamond to a solution, and a blue circle to a choice node (a node that has a not-yet finished brancher left). An example choice for node 3 is :math:`\left(\mathtt{x[0]} = \mathtt 2\right) \vee \left(\mathtt{x[0]} \neq \mathtt 2\right)` where the left alternative (or the :math:`0`-th alternative) is :math:`\mathtt{x[0]} = \mathtt 2` and the right alternative (:math:`1`-st alternative) is :math:`\mathtt{x[0]} \neq \mathtt 2`. Committing a space for node 3 to the :math:`1`-st alternative posts the constraint :math:`\mathtt{x[0]} \neq \mathtt 2`.

More precisely, a choice does not store the actual variables but the position among the variables of the brancher (storing ``0`` rather than ``x[0]``). By that, a choice can be used with an equivalent yet different space. This is essential as the space used during recomputation will be different from the space for which the choice has been created.

.. _tip:m:search:wmp:

.. mpg-tip:: Search is indeterministic

   Gecode has been carefully designed to support non-monotonic propagators: they are essential for example for randomized or approximation propagation algorithms. A propagator in Gecode must be *weakly* monotonic: essentially, a propagator must be correct but it does not need to always prune exactly the same way. A consequence of this is that search is indeterministic: it might be that two different searches find solutions in a different order (possibly returning a different first solution) or that the number of explored nodes is different. However, search is always sound and complete: it never misses any solution, it does not duplicate solutions, nor does it report non-solutions as solutions.


   If you want to know more about weakly monotonic propagators and their interaction with search, we recommend to consult :cite:`SchulteTack:CP:2009`.

.. _modeling:m-search:hybrid-recomputation-1:

Hybrid recomputation
~~~~~~~~~~~~~~~~~~~~

The hybrid of recomputation and cloning works as follows. For each new choice node, a choice is stored. Then, every now and then search also stores a clone of a space (say, every eight steps). Now, restoring a space at a certain position in the search tree traverses the path in the tree upwards until a clone :math:`c` is found on the path. Then recomputation creates a clone :math:`c'` of :math:`c` (in certain cases, recomputation might use :math:`c` directly as an optimization). Then all choices on the path are committed on :math:`c'` yielding an equivalent space.

.. figure:: /figures/fig-m-search-hybrid.svg
   :name: fig:m:search:hybrid

   Hybrid recomputation

.. container:: samepage

   To recompute the node ``?`` for the example shown in :numref:`fig:m:search:hybrid`, the following operations are executed:

   .. mpg-code:: snippet:m-search:fig:m:search:hybrid:code:1
      :direct:

.. _modeling:m-search:why-recomputation-is-almost-for-free:

Why recomputation is almost for free
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

An absolutely fundamental property of the above hybrid is that an equivalent space is computed without performing any constraint propagation! Remember: committing just reposts constraints but does not perform constraint propagation.

Reconsider the example from :numref:`fig:m:search:hybrid`. Search has just failed at node 4 and must compute a space for node ``?``.

Suppose that only cloning but no recomputation is used. Then, a clone of the space for node 3 is created (from the clone that is stored in node 3) and that clone is committed to the first alternative of :math:`\mathtt{d3}` (this corresponds to the slightly thicker edge in :numref:`fig:m:search:hybrid`). After that, constraint propagation is performed (by executing the ``status()`` function of a space, see also :ref:`tip:m:started:status`) to find out if and how search must continue. That is: there is one ``clone`` operation, one ``commit`` operation, and one ``status`` operation to perform constraint propagation.

With hybrid recomputation, one ``clone`` operation, three ``commit`` operations, and one ``status`` operation to perform constraint propagation are needed (as shown above). The good news is that ``commit`` operations are very cheap (most often, just modifying a single variable or posting a constraint). What is essential is that in both cases only a *single* ``status`` operation is executed. Hence, the cost for constraint propagation during hybrid recomputation turns out to be not much higher than the cost without recomputation.

For hybrid recomputation, some additional propagation might have to be done compared to cloning. As it turns out, the additional cost is rather small. This is due to the fact that constraint propagation executes all propagators that might be able to remove values for variables until no more propagation is possible (a fixpoint for the propagators is computed). Due to the approximative nature of “might be able to remove values” the additional propagation tends to show only a very small increase in runtime.

.. _modeling:m-search:adaptive-recomputation:

Adaptive recomputation
~~~~~~~~~~~~~~~~~~~~~~

Consider the case that a search engine finds a failed node. That means that some brancher has made an erroneous decision and now search has to recover from that decision. It is quite likely that not only the last decision is wrong but that the decision that lead to failure is somewhere higher up in the search tree. With other words, it is quite likely that search following a depth-first left-most strategy must explore an entire failed subtree to recover from the erroneous decision. In that case it would be better for hybrid recomputation if there was a clone close to the failed node rather than far away.

To optimize recomputation in this example scenario, Gecode uses *adaptive recomputation*: if a node must be recomputed, adaptive recomputation creates an additional clone in the middle of the recomputation path. A clone created during adaptive recomputation is likely to be a good investment. Most likely, an entire failed subtree will be explored. Hence, the clone will be reused several times for reducing the amount of constraint propagation during recomputation.

More information about search based on recomputation (although not using choices) can be found in :cite:`Schulte:LNAI:2002`. Search using choices has been inspired by batch recomputation :cite:`components` and decomposition-based search :cite:`DecoSearch`. For an empirical evaluation of different techniques for search, see :cite:`ReischukSchulteEa:CP:2009`.

.. _modeling:m-search:controlling-recomputation:

Controlling recomputation
~~~~~~~~~~~~~~~~~~~~~~~~~

Hybrid and adaptive recomputation can be easily controlled by two integers :math:`c_d` (*commit distance*) and :math:`a_d` (*adaptive distance*). The value for :math:`c_d` controls how many clones are created during exploration: a search engine creates clones during exploration to ensure that recomputation executes at most :math:`c_d` commit operations. The value for :math:`a_d` controls adaptive recomputation: only if the clone for recomputation is more than :math:`a_d` commit operations away from the node to be recomputed, adaptive recomputation is used.

Values for :math:`c_d` and :math:`a_d` are used to configure the behavior of search engines using hybrid and adaptive recomputation, see more in the next Section.

The number of commit operations as distance measure is approximately the same as the length of a path in the search tree. It is only an approximation as search engines use additional techniques to avoid some unused clone and commit operations.

.. mpg-tip:: Values for c_d and a_d

   If :math:`c_d=1`, recomputation is never used (you might not want to try that for any other reason but curiosity; it takes too much memory to be useful). Likewise, to switch off cloning, you can use a value for :math:`c_d` that is larger than the expected depth of the search tree. If :math:`a_d\geq c_d`, adaptive recomputation is never used.


.. _sec:m:search:parallel:


.. _modeling:m-search:parallel-search:

Parallel search
---------------

Parallel search has but one motivation: try to make search more efficient by employing several threads (or workers) to explore different parts of the search tree in parallel.

Gecode uses a standard work-stealing architecture for parallel search: initially, all work (the entire search tree to be explored) is given to a single worker for exploration, making the worker busy. All other workers are initially idle, and try to steal work from a busy worker. Stealing work means that part of the search tree is given from a busy worker to an idle worker such that the idle worker can become busy itself. If a busy worker becomes idle, it tries to steal new work from a busy worker.

As work-stealing is indeterministic (depending on how threads are scheduled, machine load, and other factors), the work that is stolen varies over different runs for the very same problem: an idle worker could potentially steal different subtrees from different busy workers. As different subtrees contain different solutions, it is indeterministic which solution is found first.

When using parallel search one needs to take the following facts into account (note that some facts are not particular to parallel search, check :ref:`tip:m:search:wmp`: they are just more likely to occur):

- The order in which solutions are found might be different compared to the order in which sequential search finds solutions. Likewise, the order in which solutions are found might differ from one parallel search to the next. This is just a direct consequence of the indeterministic nature of parallel search.

- Naturally, the amount of search needed to find a first solution might differ both from sequential search and among different parallel searches. Note that this might actually lead to super-linear speedup (for :math:`n` workers, the time to find a first solution is less than :math:`1/n` the time of sequential search) or also to real slowdown.

- For best solution search, the number of solutions until a best solution is found as well as the solutions found are indeterministic. First, any better solution is legal (it does not matter which one) and different runs will sometimes be lucky (or not so lucky) to find a good solution rather quickly. Second, as a better solution prunes the remaining search space the size of the search space depends crucially on how quickly good solutions are found.

- As a corollary to the above items, the deviation in runtime and number of nodes explored for parallel search can be quite high for different runs of the same problem.

- Parallel search needs more memory. As a rule of thumb, the amount of memory needed scales linearly with the number of workers used.

- For parallel search to deliver some speedup, the search tree must be sufficiently large. Otherwise, not all threads might be able to find work and idle threads might slow down busy threads by the overhead of unsuccessful work-stealing.

- From all the facts listed, it should be clear that for depth-first left-most search for just a single solution it is notoriously difficult to obtain consistent speedup. If the heuristic is very good (there are almost no failures), sequential left-most depth-first search is optimal in exploring the single path to the first solution. Hence, all additional work will be wasted and the work-stealing overhead might slow down the otherwise optimal search.

..

.. mpg-tip:: Be optimistic about parallel search

   After reading the above list of facts you might have come to the conclusion that parallel search is not worth it as it does not exploit the parallelism of your computer very well. Well, why not turn the argument upside down: your machine will almost for sure have more than a single processing unit and maybe quite some. With sequential search, all units but one will be idle anyway.


   The point of parallel search is to make search go faster. It is not to perfectly utilize your parallel hardware. Parallel search makes good use (and very often excellent use for large problems with large search trees) of the additional processing power your computer has anyway.

   .. mpg-figure:: Output for Golomb rulers with eight workers
      :name: fig:m:search:out:8

      .. mpg-code:: snippet:m-search:sec:m:search:parallel:cmd:1
         :direct:

   .. container:: samepage

      For example, on my machine with eight cores and using Gecode 4.2.0, running `Finding optimal Golomb rulers <https://www.gecode.dev/doc/6.4.0/reference/golomb-ruler_8cpp.html>`__ for size :math:`12` as follows

      .. mpg-code:: snippet:m-search:fig:m:search:out:8:cmd:1
         :direct:

   prints something like shown in :numref:`fig:m:search:out:8`.

   .. mpg-figure:: Output for Golomb rulers with one worker
      :name: fig:m:search:out:1

      .. mpg-code:: snippet:m-search:fig:m:search:out:8:cmd:2
         :direct:

   Compared to sequential search where one gets something like shown in :numref:`fig:m:search:out:1` one gets a speedup of :math:`7.2`.

Parallel search is controlled by the number of threads (or workers) used for search. If a single worker is requested, sequential search is used. The number of threads to be used for search is controlled by the search options passed to a search engine, see the following section for details.

Gecode also provides parallel portfolio search which is discussed in :ref:`sec:m:search:portfolio`.

.. _tip:m:search:parbab:

.. mpg-tip:: Do not optimize by branching alone



   .. container:: samepage

      A common modeling technique for optimization problems that does not work for parallel search is the following. Suppose, one has a variable ``c`` for the cost of a problem and one wants to minimize the cost. Then, one could use the following code fragment

      .. mpg-code:: snippet:m-search:tip:m:search:parbab:code:1
         :direct:

      which will try the values for ``c`` in increasing order.

   With sequential search, searching for the first solution with a standard depth-first left-most search engine will deliver a best solution, that is, a solution with least cost for ``c``.

   With parallel search, the first solution found might of course not be a best one. Hence, instead of using plain left-most depth-first search, one should use best solution search with a proper constrain function that guarantees that ``c`` will be minimized. This will as always guarantee that the last solution found is the best.

   For an example, see the naive model for the bin packing case study in :ref:`sec:c:bpp:naive` where a branching first branches on the number of required bins.

.. _sec:m:search:simple:


.. _modeling:m-search:search-engines:

Search engines
--------------

.. important::

   Do not forget to add

   .. mpg-code:: snippet:m-search:sec:m:search:simple:code:1
      :direct:

   to your program when you want to use search engines.

.. mpg-figure:: Search statistics (partial)
   :name: fig:m:search:statistics

   .. container:: center

      +---------------+--------------------------------------------------------------------------------+--------------------------------+
      | member        | type                                                                           | meaning                        |
      +===============+================================================================================+================================+
      | ``propagate`` | ``unsigned long long int``                                                     | propagators executed           |
      +---------------+--------------------------------------------------------------------------------+--------------------------------+
      | ``fail``      | ``unsigned long long int``                                                     | failed nodes explored          |
      +---------------+--------------------------------------------------------------------------------+--------------------------------+
      | ``node``      | ``unsigned long long int``                                                     | nodes explored                 |
      +---------------+--------------------------------------------------------------------------------+--------------------------------+
      | ``restart``   | ``unsigned long int``                                                          | restarts performed             |
      +---------------+--------------------------------------------------------------------------------+--------------------------------+
      | ``nogood``    | ``unsigned long int``                                                          | no-goods generated             |
      +---------------+--------------------------------------------------------------------------------+--------------------------------+
      | ``depth``     | ``unsigned long int``                                                          | maximal depth of explored tree |
      +---------------+--------------------------------------------------------------------------------+--------------------------------+

All search engines in Gecode are parametric (are templates) with respect to a subclass ``T`` of `Space <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1Space.html>`__ (for example, ``SendMoreMoney`` in :ref:`sec:m:started:first`). Moreover, all search engines share the same interface:

- The search engine is initialized by a constructor taking a pointer to an instance of the space subclass ``T`` as argument. By default, the search engine takes a clone of the space passed.

  This behavior can be changed, as can be other aspects of a search engine, see :ref:`sec:m:search:options`.

- A next solution can be requested by a ``next()`` member function. If no more solutions exist, ``next()`` returns ``NULL``. Otherwise, the engine returns a solution which again is an instance of ``T``. The client of the search engine is responsible for deleting solutions.

- A search engine can be asked for statistics information by the ``statistics()`` member function. The function returns an object of type `Search::Statistics <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1Search_1_1Statistics.html>`__. The statistics information provided is partially summarized in :numref:`fig:m:search:statistics` (see :ref:`sec:m:search:restart` for the meaning of ``restart`` and :ref:`sec:m:search:nogoods` for the meaning of ``nogood``).

- A search engine can be queried by ``stopped()`` whether the search engine has been stopped by a *stop object*. Stop objects are discussed in :ref:`sec:m:search:stop`.

- The destructor deletes all resources used by the search engine.

Note that search engines use pointers to objects rather than references to objects. The reason is that some pointers might be ``NULL``-pointers (for example, if ``next()`` fails to find a solution) and that users of search engines have to think about deleting solutions computed by search engines.

.. mpg-figure:: Available search engines
   :name: fig:m:search:engine

   .. container:: center

      +----------------------------------------------------------------------------------+----------+-----------------------------------------------------------+---------------+----------+
      | engine                                                                           | shortcut | exploration                                               | best solution | parallel |
      +==================================================================================+==========+===========================================================+===============+==========+
      | `DFS <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1DFS.html>`__     | ``dfs``  | depth-first left-most                                     |               | yes      |
      +----------------------------------------------------------------------------------+----------+-----------------------------------------------------------+---------------+----------+
      | `LDS <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1LDS.html>`__     | ``lds``  | limited discrepancy :cite:`HarveyGinsberg:95`             |               |          |
      +----------------------------------------------------------------------------------+----------+-----------------------------------------------------------+---------------+----------+
      | `BAB <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1BAB.html>`__     | ``bab``  | branch-and-bound                                          | yes           | yes      |
      +----------------------------------------------------------------------------------+----------+-----------------------------------------------------------+---------------+----------+

For each search engine there also exists a convenient shortcut function (of the same name but entirely in lowercase letters) that returns either the first solution or, in the case of best solution search, the last (and hence best) solution. The available search engines are summarized in :numref:`fig:m:search:engine`.

``BAB`` continues search when a solution is found by adding a constraint (through the ``constrain()`` function as discussed in :ref:`sec:m:started:search-best`) to search for a better solution to all remaining nodes of the search tree.

Note that the version of Gecode (6.4.0) this document corresponds to does not support parallel search for ``LDS``.

.. _sec:m:search:options:


.. _modeling:m-search:search-options:

Search options
~~~~~~~~~~~~~~

All search engines can take a default option value of type `Search::Options <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1Search_1_1Options.html>`__ when being created. The options are summarized in :numref:`fig:m:search:options`. The default values for the options are defined in the namespace `Search::Config <https://www.gecode.dev/doc/6.4.0/reference/namespaceGecode_1_1Search_1_1Config.html>`__.

.. mpg-figure:: Search options
   :name: fig:m:search:options

   .. container:: center

      +-------------------+--------------------------------------+------------------------------------------+
      | member            | type                                 | meaning                                  |
      +===================+======================================+==========================================+
      | ``threads``       | ``double``                           | number of parallel threads to use        |
      +-------------------+--------------------------------------+------------------------------------------+
      | ``c_d``           | ``unsigned int``                     | commit recomputation distance            |
      +-------------------+--------------------------------------+------------------------------------------+
      | ``a_d``           | ``unsigned int``                     | adaptive recomputation distance          |
      +-------------------+--------------------------------------+------------------------------------------+
      | ``clone``         | ``bool``                             | whether engine uses a clone when created |
      +-------------------+--------------------------------------+------------------------------------------+
      | ``d_l``           | ``unsigned int``                     | discrepancy limit (for ``LDS``)          |
      +-------------------+--------------------------------------+------------------------------------------+
      | ``nogoods_limit`` | ``unsigned int``                     | depth limit for no-good generation       |
      +-------------------+--------------------------------------+------------------------------------------+
      | ``assets``        | ``unsigned int``                     | number of assets in a portfolio          |
      +-------------------+--------------------------------------+------------------------------------------+
      | ``stop``          | ``Search::Stop*``                    | stop object (``NULL`` if none)           |
      +-------------------+--------------------------------------+------------------------------------------+
      | ``cutoff``        | ``Search::Cutoff*``                  | cutoff object (``NULL`` if none)         |
      +-------------------+--------------------------------------+------------------------------------------+
      | ``tracer``        | ``SearchTracer*``                    | search tracer (``NULL`` if none)         |
      +-------------------+--------------------------------------+------------------------------------------+

The meaning of the values for the search options are straightforward but for ``threads`` (``cutoff`` is explained in :ref:`sec:m:search:restart`, ``assets`` is explained in :ref:`sec:m:search:portfolio`, ``nogoods_limit`` is explained in :ref:`sec:m:search:nogoods`, and ``tracer`` is explained in :ref:`sec:m:search:trace`).

Assume that your computer has :math:`m` processing units [1]_ and that the value for ``threads`` is :math:`n`.

- If :math:`n=0`, then :math:`m` threads are used (as many as available processing units).

- If :math:`n\geq 1`, then :math:`n` threads are used (absolute number of threads to be used).

- If :math:`n\leq -1`, then :math:`m+n` threads are used (absolute number of processing units not to be used). For example, when :math:`n=-6` and :math:`m=8`, then :math:`2` threads are used.

- If :math:`0<n<1`, then :math:`n\cdot m` threads are used (relative number of processing units to be used). For example, when :math:`n=0.5` and :math:`m=8`, then :math:`4` threads are used.

- If :math:`-1<n<0`, then :math:`(1+n)\cdot m` threads are used (relative number of processing units not to be used). For example, when :math:`n=-0.25` and :math:`m=8`, then :math:`6` threads are used.

Note that all values are of course rounded and that at least one thread will be used.

.. _sec:m:search:stop:


.. _modeling:m-search:stop-objects:

Stop objects
~~~~~~~~~~~~

A stop object (a subclass of `Search::Stop <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1Search_1_1Stop.html>`__) implements a single virtual member function ``stop()`` that takes two arguments, the first of type `Search::Statistics <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1Search_1_1Statistics.html>`__ and the second of type `Search::Options <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1Search_1_1Options.html>`__, and returns either ``true`` or ``false``. If a stop object is passed to a search engine (by passing it as ``stop`` member of a search option), the search engine calls the ``stop()`` function of the stop object before every exploration step and passes the current statistics as argument. If the ``stop()`` function returns true, the search engine stops its execution.

When a search engine is stopped its ``next()`` function returns ``NULL`` as solution. To find out whether a search engine has been stopped or whether there are no more solutions, the ``stopped()`` member function of a search engine can be used. Search can be resumed by calling ``next()`` again after the stop object has been modified (for example, by increasing the node or time limit).

Note that when using several threads for parallel search, each thread checks whether it is stopped independently using the very same stop object. If one thread is stopped, then the entire search engine is stopped.

.. mpg-figure:: Predefined stop objects
   :name: fig:m:search:stop

   .. container:: center

      +--------------------------------------------------------------------------------------------------------------+------------------------+
      | class                                                                                                        | description            |
      +==============================================================================================================+========================+
      | `Search::NodeStop <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1Search_1_1NodeStop.html>`__     | node limit exceeded    |
      +--------------------------------------------------------------------------------------------------------------+------------------------+
      | `Search::FailStop <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1Search_1_1FailStop.html>`__     | failure limit exceeded |
      +--------------------------------------------------------------------------------------------------------------+------------------------+
      | `Search::TimeStop <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1Search_1_1TimeStop.html>`__     | time limit exceeded    |
      +--------------------------------------------------------------------------------------------------------------+------------------------+

Gecode provides several predefined stop objects, see `Stop-objects for stopping search <https://www.gecode.dev/doc/6.4.0/reference/group__TaskModelSearchStop.html>`__. For an overview see :numref:`fig:m:search:stop`. Objects of these classes can be created conveniently by, for example:

.. mpg-code:: snippet:m-search:fig:m:search:stop:code:1
   :direct:


The class `Search::Stop <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1Search_1_1Stop.html>`__ also provides similar static functions ``fail()`` and ``time()``.

.. mpg-tip:: Number of threads for stop objects

   As mentioned above, each thread in parallel search uses the very same stop object. For example, when using the predefined `Search::NodeStop <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1Search_1_1NodeStop.html>`__ stop object with a node limit of :math:`n`, then each thread can explore up to :math:`n` nodes.


   If you want to have finer control (say, only allow each thread to explore up to :math:`n/m` nodes where :math:`m` is the number of threads) you can use the search option argument that is passed as the second argument to the ``stop`` member function to scale the node limit according to the number of available threads.

.. _sec:m:search:restart:


.. _modeling:m-search:restart-based-search:

Restart-based search
--------------------

The idea of restart-based search is to run search with a given *cutoff* (Gecode uses the number of failures during search as cutoff-measure). When search reaches the cutoff, it is stopped and then restarted with a new and typically increased cutoff.

The whole point of restarting search is that it is not restarted on exactly the same problem but on a modified or re-configured problem. Possible modifications include but are not limited to:

- Improved information from the search for branching heuristics such as action (see :ref:`sec:m:branch:action`) or AFC (see :ref:`sec:m:branch:afc`): the now stopped search has gathered some information of which branching can take advantage in the next restart of search.

- The next search can use different random numbers that controls branching. A typical strategy would be to use tie-breaking for combining a branching heuristic with a random branching heuristic (see :ref:`sec:m:branch:tie`) and control the degree of randomness by a tie-breaking limit function.

- The next search uses an entirely different branching heuristic.

- The next search adds so-called no-goods derived from the now stopped search. No-goods are additional constraints that prevent the restarted search to make decisions during search that lead to failure in the stopped search. No-goods are discussed in detail in :ref:`sec:m:search:nogoods`.

- The next search “keeps” only a randomly selected part of a previous solution and tries to find a different solution. This is often used for optimization problems and is known as LNS (Large Neighborhood Search) :cite:`LNS`. How restart-based can be used for LNS is discussed in :ref:`sec:m:search:restart:lns`.

For an example illustrating the effect of restart-based search, see :ref:`sec:c:crossword:info`. A general overview of restart-based search can be found in :cite:`vanBeek:CPH:2006`.

.. _sec:m:search:restart:meta:


.. _modeling:m-search:restart-based-search-as-a-meta-search-engine:

Restart-based search as a meta search engine
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Restart-based search in Gecode is implemented as a *meta search engine*: the meta search engine uses one of the Gecode search engines discussed in :ref:`sec:m:search:simple` to perform search for each individual restart. The meta engine then controls the engine, the cutoff values, and how the problem is configured before each restart. The interface of the meta search engine in Gecode is exactly the same as the interface of a non-meta search engine. In addition to the restart meta search engine, Gecode offers a portfolio meta search engine which is described in :ref:`sec:m:search:portfolio`.

The restart meta search engine `RBS <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1RBS.html>`__ is parametric with respect to both the script to be solved (a subclass of `Space <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1Space.html>`__) and the search engine to be used. For example, when we want to use the `DFS <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1DFS.html>`__ engine for the script ``s`` of class type ``Script``, the meta engine ``e`` can be created by (``o`` are mandatory search options, see below):

.. mpg-code:: snippet:m-search:sec:m:search:restart:meta:code:1
   :direct:


Now ``e`` implements exactly the same interface as the normal engines (that is, ``next()`` to request the next solution, ``statistics()`` to return the meta engine’s statistic, and ``stopped()`` to check whether the meta engine has been stopped).

The meta engine honors all search options as discussed in :ref:`sec:m:search:options`. If parallel search is requested, the engine used by the meta engine will use the specified number of processing units to perform parallel search. The meta engine requires that the search options specify a `Search::Cutoff <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1Search_1_1Cutoff.html>`__ object defining the cutoff sequence.

.. _modeling:m-search:best-solution-search:

.. rubric:: Best solution search.

Restart-based search can be used for both finding any solution or finding a best solution. For searching for a best solution, the meta engine should be used with the `BAB <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1BAB.html>`__ engine, for example as:

.. mpg-code:: snippet:m-search:sec:m:search:restart:meta:code:2
   :direct:


The behavior whether the engine performs a restart when a better solution is performed or whether the ``BAB`` engine continues to find a better solution with a restart can be controlled as described in :ref:`sec:m:search:restart:configure`.

When using restart-based search for finding a best solution it is essential to use the `BAB <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1BAB.html>`__ engine when used as part of a portfolio-based search engine, see :ref:`sec:m:search:portfolio:arbitrary`.

.. _modeling:m-search:parallel-search-2:

.. rubric:: Parallel search.

The restart-based search engine supports parallel search in that the engine used for performing the restarts can be run in parallel. The number of threads used can be described by the search options passed to the restart-based search engine as described in :ref:`sec:m:search:parallel`.

.. _tip:m:search:restartcmd:

.. mpg-tip:: Controlling restart-based search with the commandline driver

   The commandline driver transparently supports restart-based search. Depending on which options are passed on the commandline, either a search engine or the restart-based meta search engine is used for search. See :ref:`sec:m:driver:options` for details.


.. _sec:m:search:restart:cutoff:


.. _modeling:m-search:cutoff-generators:

Cutoff generators
~~~~~~~~~~~~~~~~~

The meta engine uses a cutoff generator that generates a sequence of cutoff values. A cutoff generator must be implemented by inheriting from the class `Search::Cutoff <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1Search_1_1Cutoff.html>`__. This abstract class requires that two virtual member functions ``operator()()`` and ``operator++()`` are implemented, where the first returns the current cutoff value and the second increments to the next cutoff value and returns it. Cutoff values are of type ``unsigned long long int``.

When using the restart meta engine, an instance of a subclass of `Search::Cutoff <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1Search_1_1Cutoff.html>`__ must be passed to the engine by using the search options (see :ref:`sec:m:search:options`). For example, when ``s`` is a space to be solved and ``c`` a cutoff generator, then the restart engine can be created by:

.. mpg-code:: snippet:m-search:sec:m:search:restart:cutoff:code:1
   :direct:


Gecode provides some commonly used cutoff generators:

Geometric.
   A geometric cutoff sequence is defined by the scale-factor ``s`` and the base ``b``. Then, the sequence consists of the cutoff values:

   .. math:: \mathtt{s}\cdot\mathtt{b}^i\qquad\text{for }i=0,1,2,\ldots

   .. container:: samepage

      A cutoff generator ``c`` for a geometric cutoff sequence with scale-factor ``s`` (of type ``unsigned long long int``) and base ``b`` (of type ``double``) is created by:

      .. mpg-code:: snippet:m-search:sec:m:search:restart:cutoff:code:2
         :direct:
         :small:

   The generator is implemented by the class `Search::CutoffGeometric <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1Search_1_1CutoffGeometric.html>`__.

Luby.
   A Luby cutoff sequence is based on the Luby-sequence from :cite:`Luby`. The sequence starts with a ``1``. The next part of the sequence is the entire previous sequence (only ``1``) with the last value of the previous sequence (``1`` again) doubled. This construction is then repeated, leading to the sequence:

   .. math:: 1,1,2,1,1,2,4,1,1,2,1,1,2,4,8,\ldots

   To be practically useful, the values in the Luby sequence are scaled by multiplying them with a scale-factor ``s``.

   A cutoff generator ``c`` for a Luby cutoff sequence with scale-factor ``s`` (of type ``unsigned long long int``) is created by:

   .. mpg-code:: snippet:m-search:sec:m:search:restart:cutoff:code:3
      :direct:
      :small:

   The generator is implemented by the class `Search::CutoffLuby <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1Search_1_1CutoffLuby.html>`__.

Random.
   A random cutoff sequence consists of uniformly randomly chosen values between a lower bound ``min`` and an upper bound ``max``. To focus on rather different values, only values from the set of :math:`\mathtt n+1` values:

   .. math:: \{\mathtt{min}+\lfloor i\cdot(\mathtt{max}-\mathtt{min})/\mathtt{n}\rfloor\mid i=0,\ldots,\mathtt{n}\}

   are chosen randomly.

   A cutoff generator ``c`` for a random sequence with lower bound ``min``, upper bound ``max``, and number of values ``n`` (all of type ``unsigned long long int``) is created by:

   .. mpg-code:: snippet:m-search:sec:m:search:restart:cutoff:code:4
      :direct:
      :small:

   where ``seed`` (of type ``unsigned int``) defines the seed value for the random number generator used. The generator is implemented by the class `Search::CutoffRandom <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1Search_1_1CutoffRandom.html>`__.

Constant.
   A constant cutoff sequence is defined by the scale-factor ``s``. Then, the sequence consists of the cutoff values:

   .. math:: \mathtt{s},\mathtt{s},\mathtt{s},\ldots

   The generator is implemented by the class `Search::CutoffConstant <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1Search_1_1CutoffConstant.html>`__.

   .. container:: samepage

      A cutoff generator ``c`` for a constant cutoff sequence with scale-factor ``s`` (of type ``unsigned long long int``) is created by:

      .. mpg-code:: snippet:m-search:sec:m:search:restart:cutoff:code:5
         :direct:
         :small:

Linear.
   A linear cutoff sequence is defined by the scale-factor ``s``. Then, the sequence consists of the cutoff values:

   .. math:: 1\cdot\mathtt{s},2\cdot\mathtt{s},3\cdot\mathtt{s},\ldots

   .. container:: samepage

      A cutoff generator ``c`` for a linear cutoff sequence with scale-factor ``s`` (of type ``unsigned long long int``) is created by:

      .. mpg-code:: snippet:m-search:sec:m:search:restart:cutoff:code:6
         :direct:
         :small:

   The generator is implemented by the class `Search::CutoffLinear <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1Search_1_1CutoffLinear.html>`__.

Append.
   An appended cutoff sequence ``c`` for ``n`` values from the cutoff sequence :math:`\mathtt{c}_1` (with values :math:`k_0,k_1,k_2,\ldots`) followed by the values from the cutoff sequence :math:`\mathtt{c}_2` (with values :math:`l_0,l_1,l_2,\ldots`) consists of the following values:

   .. math:: k_0,k_1,\ldots,k_{\mathtt{n}-2},k_{\mathtt{n}-1},l_0,l_1,l_2,\ldots

   A cutoff generator ``c`` for an appended cutoff sequence with ``n`` (of type ``unsigned long long int``) values from cutoff generator ``c1`` followed by values from cutoff generator ``c2`` is created by:

   .. mpg-code:: snippet:m-search:sec:m:search:restart:cutoff:code:7
      :direct:
      :small:

   The generator is implemented by the class `Search::CutoffAppend <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1Search_1_1CutoffAppend.html>`__.

Merge.
   A merged cutoff sequence ``c`` for values from the cutoff sequence :math:`\mathtt{c}_1` (with values :math:`k_0,k_1,k_2,\ldots`) merged with the values from the cutoff sequence :math:`\mathtt{c}_2` (with values :math:`l_0,l_1,l_2,\ldots`) consists of the following values:

   .. math:: k_0,l_0,k_1,l_1,k_2,l_2,\ldots

   A cutoff generator ``c`` for a merged cutoff sequence with values from cutoff generator ``c1`` merged with values from cutoff generator ``c2`` is created by:

   .. mpg-code:: snippet:m-search:sec:m:search:restart:cutoff:code:8
      :direct:
      :small:

   The generator is implemented by the class `Search::CutoffMerge <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1Search_1_1CutoffMerge.html>`__.

Repeat.
   A repeated cutoff sequence ``c`` with repeat factor ``n`` (of type ``unsigned long long int``) for the cutoff sequence :math:`\mathtt{c}'` (with values :math:`k_0,k_1,k_2,\ldots`) consists of the following values:

   .. math::

      \begin{array}{c@{}c@{}c@{}l}
      \underbrace{k_0,k_0,\ldots,k_0},&
      \underbrace{k_1,k_1,\ldots,k_1},&
      \underbrace{k_2,k_2,\ldots,k_2},&
      \ldots\\
      \mbox{\texttt{n} times}&
      \mbox{\texttt{n} times}&
      \mbox{\texttt{n} times}
      \end{array}

   A cutoff generator ``c`` for a repeated cutoff sequence with repeat factor ``n`` (of type ``unsigned long long int``) and values from the cutoff generator ``c1`` is created by:

   .. mpg-code:: snippet:m-search:sec:m:search:restart:cutoff:code:9
      :direct:
      :small:

   The generator is implemented by the class `Search::CutoffRepeat <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1Search_1_1CutoffRepeat.html>`__.

.. _sec:m:search:restart:next:


.. _modeling:m-search:computing-a-next-solution:

Computing a next solution
~~~~~~~~~~~~~~~~~~~~~~~~~

When the restart meta engine is asked for a next solution by calling ``next()``, there are three possible scenarios:

- ``next()`` returns a pointer to a space (which might be ``NULL`` in case there are no more solutions or the engine has been stopped). Deleting the space is as with other engines the responsibility of the meta engine’s user.

  By default, asking the meta engine for another solution will perform a restart. However, this behavior can be changed such that the current cutoff value (minus the failed nodes it took to find the current solution) is used for finding a next solution. For details, see :ref:`sec:m:search:restart:configure`.

- The meta engine reaches the current cutoff value. It restarts search with the next cutoff value.

- The meta engine is stopped by the stop object passed to it. Then ``next()`` returns ``NULL`` and ``stopped()`` returns ``true`` (to be able to distinguish this scenario from the one where there are no more solutions).

.. _sec:m:search:restart:configure:


.. _modeling:m-search:master-and-slave-configuration:

Master and slave configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The meta engine maintains a *master* space and each time the meta engine performs a restart, it passes a *slave* space (a clone of the master space) to the engine. Configuration is as follows: the master is configured, the slave is created as a clone of the master, and then the slave is configured. Initially, when the meta engine starts and creates a first slave space, it also configures the slave space.

More accurately, it leaves the actual configuration to the user: it calls the virtual member function ``master()`` on the master space and then calls the virtual member function ``slave()`` on the slave space. As mentioned above, the ``slave()`` function is also called the first time a slave is created. In that way, by redefining ``master()`` and ``slave()`` the user can control how master and slave are being configured (this is exactly the same idea how ``constrain()`` works for best solution search).

.. mpg-figure:: Meta information member functions
   :name: fig:m:search:mi

   .. container:: center

      +---------------------------+--------------------------------------------------------------------------------+----------------------------------------+
      | function                  | type                                                                           | meaning                                |
      +===========================+================================================================================+========================================+
      | ``type()``                | ``MetaInfo::Type``                                                             | type of meta information               |
      +---------------------------+--------------------------------------------------------------------------------+----------------------------------------+
      | restart-based information |                                                                                |                                        |
      +---------------------------+--------------------------------------------------------------------------------+----------------------------------------+
      | ``restart()``             | ``unsigned long int``                                                          | number of restart                      |
      +---------------------------+--------------------------------------------------------------------------------+----------------------------------------+
      | ``solution()``            | ``unsigned long long int``                                                     | number of solutions since last restart |
      +---------------------------+--------------------------------------------------------------------------------+----------------------------------------+
      | ``fail()``                | ``unsigned long long int``                                                     | number of failures since last restart  |
      +---------------------------+--------------------------------------------------------------------------------+----------------------------------------+
      | ``last()``                | ``const Space*``                                                               | last solution found (or ``NULL``)      |
      +---------------------------+--------------------------------------------------------------------------------+----------------------------------------+
      | ``nogoods()``             | ``const NoGoods&``                                                             | no-goods recorded from restart         |
      +---------------------------+--------------------------------------------------------------------------------+----------------------------------------+
      | portfolio information     |                                                                                |                                        |
      +---------------------------+--------------------------------------------------------------------------------+----------------------------------------+
      | ``asset()``               | ``unsigned int``                                                               | number of asset (slave)                |
      +---------------------------+--------------------------------------------------------------------------------+----------------------------------------+

By default, every space implements the two member functions ``master()`` and ``slave()``. Both functions take an argument of class `MetaInfo <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1MetaInfo.html>`__ that contains information about the current restart (and also for different assets in a portfolio, see :ref:`sec:m:search:portfolio`). The class ``MetaInfo`` provides the member functions as shown in :numref:`fig:m:search:mi`.

For a meta information object ``mi``, the function ``mi.type()`` returns either ``MetaInfo::RESTART`` or ``MetaInfo::PORTFOLIO``. In this section, we are only interested in the functions that are concerned with restart-based search.

The default ``slave()`` function does nothing and returns ``true``, indicating that the search in the slave space is going to be complete. This means that if the search in the slave space finishes exhaustively, the meta search will also finish. Returning ``false`` instead would indicate that the slave search is incomplete, for example if it only explores a limited neighborhood of the previous solution.

The default ``master()`` function does the following (for a restart, that is):

- It calls the ``constrain()`` member function with the last solution found as argument (if a solution has already been found).

- It possibly posts no-goods as explained in :ref:`sec:m:search:nogoods`.

- It returns ``true`` forcing a restart even if a solution has been found. Returning ``false`` instead would continue search without a restart.

For example, a class ``Script`` can define the member functions as follows:

.. mpg-code:: snippet:m-search:fig:m:search:mi:code:1
   :direct:


.. mpg-code:: default master and slave functions
   :name: fig:m:search:restart:default
   :caption: Default master()and slave()functions


The default ``master()`` and ``slave()`` member functions are shown in :numref:`fig:m:search:restart:default`. The part of the ``master()`` function that is specific for restart-based search is as follows:

.. mpg-code:: default master and slave functions:restart-based search


.. _sec:m:search:restart:lns:


.. _modeling:m-search:large-neighborhood-search:

Large Neighborhood Search
~~~~~~~~~~~~~~~~~~~~~~~~~

The design of restart-based search in Gecode is general enough to support LNS (Large Neighborhood Search) :cite:`LNS`. The idea of LNS is quite simple, where LNS looks for a good solution:

- Search finds a first solution where typically preference is given to find a reasonably good solution quickly.

- During LNS, a new problem is generated that only keeps part of the so-far best solution (typically, the part to keep is randomly selected). This is often referred to as *relaxing* the so-far best solution. Then, search tries to find a next and better solution within a given cutoff.

  If the cutoff is reached without finding a solution, search can either decide to terminate or randomly retry again.

.. mpg-code:: model sketch for LNS
   :name: fig:m:search:restart:sketch
   :caption: Model sketch for LNS


:numref:`fig:m:search:restart:sketch` sketches a model that supports LNS. The constructor ``Model()`` initializes the model with all variables and constraints that are common for finding the first solution as well as for finding further solutions. Note that the model has a random number generator of class `Rnd <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1Rnd.html>`__ as member ``r`` to illustrate that typically some form of randomness is needed for restarting. However, in a real life problem additional data structures might be needed.

.. container:: samepage

   The ``first()`` function is responsible for posting additional constraints and branchings such that search can find the first solution. The ``next()`` function takes the so-far best solution ``b`` and posts additional constraints and branchings to find a next and better solution than ``b``. This will typically mean that some but not all variables in the current space are assigned to values as defined by the so-far best solution ``b`` or that additional constraints are posted that depend on ``b``.

.. container:: samepage

   Both ``first()`` and ``next()`` are executed on the slave space when the restart-based search engine performs a restart or executes search for the first time. This can be achieved by defining the ``slave()`` function as follows. Note how it returns ``true`` to indicate that the search is going to be complete until it has found a first solution [2]_ but ``false`` for subsequent restarts, which only explore a neighborhood and are therefore incomplete:

   .. mpg-code:: model sketch for LNS:slave function

The default ``master()`` function as shown in :ref:`sec:m:search:restart:configure` is already general enough to support LNS.

.. _par:m:search:relax:


.. _modeling:m-search:relaxing-variable-assignments:

.. rubric:: Relaxing variable assignments.

A typical way to relax a given solution, is to assign some but not all variables before a restart to a value from a previous solution. This is supported by the ``relax()`` function for integer, Boolean, set, and float variables.

Assume that ``x`` is an array of integer variables in the ``Model`` script sketched in :numref:`fig:m:search:restart:sketch`. Then, the following ``next()`` function:

.. mpg-code:: snippet:m-search:par:m:search:relax:code:1
   :direct:


relaxes each variable in ``x`` with a probability of :math:`0.7` (or, with other words: each variable in ``x`` would be assigned the value from ``b.x`` with a probability of :math:`0.3`). The random numbers are drawn from the random number generator ``r``.

The ``relax()`` function makes sure that at least one of the variables in ``x`` remains unassigned (if needed, the variable to remain unassigned is determined uniformly randomly).

For an example using LNS and the ``relax()`` function please consult `Placing people on a photo <https://www.gecode.dev/doc/6.4.0/reference/examples_2photo_8cpp.html>`__.

.. _sec:m:search:portfolio:


.. _modeling:m-search:portfolio-search:

Portfolio search
----------------

The idea of portfolio search is to run several copies, where each copy is called an *asset* or a *slave*, of the same problem independently where each copy typically uses a different branching heuristic (the copies might of course also differ in how the same problem is modeled). The goal is to increase the likelihood of finding a solution to the problem quickly and hence to increase search robustness.

Portfolio search in Gecode is provided as a meta search engine, for the general idea of a meta search engine, please consult :ref:`sec:m:search:restart:meta`. For more information on portfolios in constraint programming, see :cite:`portfolios`.

.. _sec:m:search:portfolio:meta:


.. _modeling:m-search:simple-portfolio-search-as-a-meta-search-engine:

Simple portfolio search as a meta search engine
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Portfolio search is, like restart-based search, implemented as a meta search engine. The meta engine creates one slave search engine per asset of the portfolio and coordinates their execution. The portfolio search engine has two interfaces, a simple one that is very similar to the interfaces of non-meta search engines and of restart-based search engines, and a second interface that is considerably more powerful in that it can mix different types of search engines in one portfolio. The advanced interface is described in :ref:`sec:m:search:portfolio:arbitrary`.

The key parameter for portfolio search is the number of assets. For example, a portfolio engine with four assets can be created by:

.. mpg-code:: snippet:m-search:sec:m:search:portfolio:meta:code:1
   :direct:


Here, for each asset an engine of type ``DFS`` is created for a clone of the master space ``s``.

Before the clones are created, the ``master()`` member function as implemented by the ``Script`` class is called. On each clone, the ``slave()`` function is called where the slave function is called with information about the number of the asset (ranging from ``0`` to ``3``, the number of assets minus one). The following section explains the details of how the master and the slaves are configured, whereas :ref:`sec:m:search:portfolio:parallel` explains how assets of a portfolio are executed sequentially or in parallel.

.. _sec:m:search:portfolio:configure:


.. _modeling:m-search:master-and-slave-configuration-3:

Master and slave configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The ``master()`` function provided by a script is called exactly once on the master space from which clones are created for each asset. The purpose of the ``master()`` function can be to setup certain aspects of a script specific to portfolio search.

The portfolio-specific part of the default ``master()`` function is as follows, the entire ``master()`` function is shown in :numref:`fig:m:search:restart:default`:

.. mpg-code:: default master and slave functions:portfolio search


That is, by default all branchers contained in the master space are deleted before the slave spaces are created, for more on killing branchers see :ref:`sec:m:group:branch`. This provides the opportunity to create branchers specific to each asset by the ``slave()`` function.

The default ``slave()`` function does nothing, in order to be meaningful for portfolio search a user needs to define one. Assume that you have four different variants of your model, each using a different brancher. Then the following ``slave()`` function creates branchers specific for each asset:

.. mpg-code:: snippet:m-search:sec:m:search:portfolio:configure:code:1
   :direct:


where the function ``mi.asset()`` returns the number of the asset being created. Creating more than four asset for this particular example seems to be not that useful, but in :ref:`sec:m:search:portfolio:arbitrary` we are going to discuss how different search engines can be run in one portfolio. Here one could imagine a portfolio that includes an engine running sequential search together with an engine that runs exactly the same script, however with parallel search using more than one thread. Note that the return value of the ``slave()`` function has no meaning for portfolio search (but it has for restart-based search).

For an example using several branchers using different random seeds in a portfolio, see `Quasigroup completion <https://www.gecode.dev/doc/6.4.0/reference/qcp_8cpp.html>`__.

.. _tip:m:search:kill:

.. mpg-tip:: Kill your branchers, or maybe not…

   Instead of killing your branchers in the master space of a portfolio as shown above, a different option is to not post them in the master space of a portfolio in the first place. Whether a script should become the master of a portfolio is typically easy to detect when using the options provided by the script commandline driver. Here the number of assets can be queried by the ``assets()`` member function. If the value returned is larger than ``0``, the script will be run in a portfolio.


.. _sec:m:search:portfolio:parallel:


.. _modeling:m-search:parallel-and-sequential-portfolios:

Parallel and sequential portfolios
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Whether the assets in a portfolio are run in parallel or just concurrently is controlled by the number of assets in relation to the number of threads requested. The way how threads are allocated to assets is *conservative*: there will be never more threads running than requested, possibly at the expense of running fewer assets than requested.

.. _modeling:m-search:sequential-portfolios:

.. rubric:: Sequential portfolios.

A sequential portfolio consisting of :math:`n` assets is executed in a simple round-robin scheme: the first asset is given a certain slice, measured in the number of failures encountered during search for that asset. If a solution is found within this slice, the portfolio search engine reports this solution (as a result of its ``next()`` function). If no solution is found, the portfolio engine gives a slice to the second assets, and so on. If the last asset exceeds its slice, search continues with the first asset again.

The size of the slice can be controlled by the options passed to the portfolio engine. For example,

.. mpg-code:: snippet:m-search:sec:m:search:portfolio:parallel:code:1
   :direct:


creates a portfolio with three assets, where a slice is :math:`50` failures. The default value for a slice is defined in the namespace `Search::Config <https://www.gecode.dev/doc/6.4.0/reference/namespaceGecode_1_1Search_1_1Config.html>`__.

.. _modeling:m-search:parallel-portfolios:

.. rubric:: Parallel portfolios.

If parallel execution is requested (the numbers of threads requested is greater than one, see :ref:`sec:m:search:options`), a parallel portfolio engine is created where each asset is run in its own thread. For example,

.. mpg-code:: snippet:m-search:sec:m:search:portfolio:parallel:code:2
   :direct:


will create three threads each running a (sequential) depth-first search engine.

As mentioned before, threads are created conservatively. That is,

.. mpg-code:: snippet:m-search:sec:m:search:portfolio:parallel:code:3
   :direct:


creates only two threads for two assets.

If more threads than assets are requested, the remaining threads are passed on to the assets. For example,

.. mpg-code:: snippet:m-search:sec:m:search:portfolio:parallel:code:4
   :direct:


creates a portfolio with assets where each asset is a parallel search engine using two threads. In more detail, requesting :math:`n` assets and :math:`m` threads and :math:`m>n`, then for each asset :math:`\left\lfloor \frac{m}{n} \right\rfloor` threads are requested.

.. mpg-tip:: Always use parallel portfolios

   The only reasons for not using parallel portfolios is that the executing platform does not have threads (then a sequential instead of a parallel portfolio is chosen automatically anyway) or for debugging. Otherwise, an operating system scheduling several threads even on a single processing unit tends to be the better approach.


..

.. mpg-tip:: Controlling portfolios from the commandline

   The commandline driver transparently supports portfolio search. Depending on which options are passed on the commandline, either a search engine or a portfolio engine is used for search. The number of assets (by ``-assets``), the size of a slice for a sequential portfolio (by ``-slice``), and the number of threads for a parallel portfolio (by ``-threads``) can be specified. See :ref:`sec:m:driver:options` for details.


.. _sec:m:search:portfolio:arbitrary:


.. _modeling:m-search:mixed-portfolios:

Mixed portfolios
~~~~~~~~~~~~~~~~

The interface discussed in the previous section creates only assets where each asset runs the same search engine. This is often not desirable. For example, a common strategy is to mix assets using search with and without restarts.

Therefore a more expressive interface to portfolio search is provided that is based on the idea of *search engine builders* (SEBs). A search engine builder is defined by its *type* and is created using search options as input (that is, each engine to be built can have its own search options). Then the portfolio search engine creates an engine as defined by the type and the options of all SEBs passed as arguments. The type of a SEB can be either ``dfs`` (depth-first search), ``lds`` (limited discrepancy search), ``bab`` (branch-and-bound solution search for a best solution), ``rbs`` (restart-based search), or ``pbs`` (portfolio search). The types ``dfs``, ``lds``, and ``bab`` are parametric with respect to a script type (as the engines ``DFS``, ``LDS``, and ``BAB`` are) and the ``rbs`` and ``pbs`` types are parametric with respect to both the script type and the engine type (as the meta engines ``RBS`` and ``PBS`` are).

Consider the following example: we would like to create a portfolio for the master space ``master`` of type ``Script`` which consists of the following assets:

#. A depth-first search engine using two threads; and

#. Another depth-first search engine using a single thread; and

#. A restart-based meta engine using a depth-first engine with a single thread and a Luby cutoff sequence with scale factor ``10`` (see :ref:`sec:m:search:restart:cutoff`).

The portfolio engine should use one thread for each asset.

The respective portfolio engine can be created as follows:

.. mpg-code:: snippet:m-search:sec:m:search:portfolio:arbitrary:code:1
   :direct:


Note that the number of assets is defined by the number of SEBs passed as argument and not by ``s.assets`` as with the simpler interface. Executing a function such as ``dfs()`` in fact creates a new SEB ``seb`` that eventually must be deleted by ``delete seb``. When creating a portfolio engine from a SEB, the engine takes care of deleting the SEB.

.. _best-solution-search.-1:

.. _modeling:m-search:best-solution-search-4:

.. rubric:: Best solution search.

Whether a portfolio search engine created from SEBs performs best solution search is determined by the SEBs. If the SEBs are created by ``bab<Script>()``, ``rbs<Script,BAB>()``, or ``pbs<Script,BAB>()`` then the engine performs best solution search. Mixing best solution search SEBs with non-best solution search SEBs throws an exception of type `Search::MixedBest <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1Search_1_1MixedBest.html>`__.

.. mpg-tip:: Mixing parallel and sequential portfolios

   In case a really large number of assets ``n`` is required but one needs to keep the number of threads ``m`` sufficiently small, one can use SEBs to create a parallel portfolio search engine consisting of assets which are sequential portfolios themselves. Let us assume in the following for simplicity that ``n`` is a multiple of ``m`` and that ``master`` is the master space of type ``Script``.


   Then the following code snippet creates a parallel portfolio containing ``m`` assets each being a sequential portfolio having :math:`\frac{\mathtt{n}}{\mathtt{m}}` assets:

   .. mpg-code:: snippet:m-search:sec:m:search:portfolio:arbitrary:code:2
      :direct:

.. _sec:m:search:nogoods:


.. _modeling:m-search:no-goods-from-restarts:

No-goods from restarts
----------------------

As discussed in :ref:`sec:m:search:restart`, the idea of using restarts effectively is to restart with an improved problem with the hope that search is capable of solving the improved problem. No-goods are constraints that can be learned from the configuration of a depth-first search engine after it has stopped. The no-goods encode failures during search as constraints: after restarting, propagation of the no-goods ensures that decisions that lead to failure are avoided. Note that no-goods are only available from the depth-first search engines ``DFS`` and ``BAB`` but not from limited discrepancy search ``LDS``.

.. figure:: /figures/fig-m-search-nogoods.svg
   :name: fig:m:search:nogoods

   Search tree after cutoff :math:`3` has been reached

Consider the simple example depicted in :numref:`fig:m:search:nogoods`. It shows a search tree that has been explored by the restart-based search engine with a cutoff of :math:`3` failures. The thick edges in the tree depict the path that is stored by a search engine using depth-first search (such as `DFS <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1DFS.html>`__ or `BAB <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1BAB.html>`__).

What can be immediately derived from this configuration is that the following two constraints (they correspond to conjunctions of alternatives shown in :numref:`fig:m:search:nogoods`):

.. math::

   (\mathtt{x}\leq\mathtt{7})\wedge(\mathtt{y}=\mathtt{0})
   \qquad\text{and}\qquad
   (\mathtt{x}\leq\mathtt{7})\wedge(\mathtt{y}\neq\mathtt{0})\wedge(\mathtt{z}=\mathtt{3})

are *no-goods*: they cannot be satisfied by any solution of the problem (after all, search just proved that). The alternatives in the conjunction are also known as *no-good literals*.

When restarting search, the negation of the no-goods can be added to the master space as constraints and can be propagated. That is, the following constraints can be added:

.. math::

   \neg\left((\mathtt{x}\leq\mathtt{7})\wedge(\mathtt{y}=\mathtt{0})\right)
   \qquad\text{and}\qquad
   \neg\left((\mathtt{x}\leq\mathtt{7})\wedge(\mathtt{y}\neq\mathtt{0})\wedge(\mathtt{z}=\mathtt{3})\right)

or, equivalently, the constraints:

.. math::

   \neg(\mathtt{x}\leq\mathtt{7})\vee\neg(\mathtt{y}=\mathtt{0})
   \qquad\text{and}\qquad
   \neg(\mathtt{x}\leq\mathtt{7})\vee\neg(\mathtt{y}\neq\mathtt{0})\vee\neg(\mathtt{z}=\mathtt{3})

Now assume that when restarting, after some search the constraint :math:`\mathtt{x}\leq\mathtt{7}` becomes subsumed. Then, it can be propagated that :math:`\mathtt{y}\neq\mathtt{0}`. With other words, whenever :math:`\mathtt{x}\leq\mathtt{7}` holds, then also :math:`\mathtt{y}\neq\mathtt{0}` holds. This explains (if you know about resolution, you have figured out that one already anyway) that it is equivalent to use the following two constraints:

.. math::

   \neg(\mathtt{x}\leq\mathtt{7})\vee\neg(\mathtt{y}=\mathtt{0})
   \qquad\text{and}\qquad
   \neg(\mathtt{x}\leq\mathtt{7})\vee\neg(\mathtt{z}=\mathtt{3})

No-goods from restarts in Gecode follow the idea from :cite:`NogoodsRestarts`, however the implementation differs. Moreover, the no-good literals used in Gecode can be arbitrary constraints and hence generalize the ideas from :cite:`gnogoods` and :cite:`NogoodsRestarts`. Also no-goods in Gecode support choices of arbitrary arity and are not restricted to binary choices. For more details, see :ref:`chap:b:advanced` and in particular :ref:`sec:b:advanced:nogoods`.

.. _modeling:m-search:generating-and-posting-no-goods:

.. rubric:: Generating and posting no-goods.

When the restart-based search engine reaches the current cutoff limit or finds a solution it calls the ``master()`` member function as discussed in the previous section.

From the argument of class `MetaInfo <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1MetaInfo.html>`__ that is passed to the ``master()`` function a no-good of class `NoGoods <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1NoGoods.html>`__ can be retrieved by calling the ``nogoods()`` function. A no-good has really only ``post()`` as its single important member function. The following ``master()`` function posts all constraints corresponding to the no-goods that can be derived from a restart (this is also the default ``master()`` function defined by the class `Space <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1Space.html>`__, see also :ref:`sec:m:search:restart:configure`):

.. mpg-code:: snippet:m-search:fig:m:search:nogoods:code:1
   :direct:


In order to post no-goods it must be enabled that a search engine maintains its internal state such that no-goods can be extracted. This is done by setting the no-goods depth limit (the member ``nogoods_limit`` of a search option of type ``unsigned int``) to a value larger than zero. The value of ``nogoods_limit`` describes to which depth limit no-goods should be extracted from the path of the search tree maintained by the search engine. For example, the following code (it assumes that ``c`` refers to a cutoff object):

.. mpg-code:: snippet:m-search:fig:m:search:nogoods:code:2
   :direct:


instructs the search engine to extract no-goods up to a depth limit of ``128``.

The larger the depth limit, the more no-goods can of course be extracted. However, this comes at a cost:

- Gecode’s search engines use an optimization that is called LAO (last alternative optimization, see also :ref:`sec:s:re:lao`). LAO saves space by avoiding to store choices on the search engine’s stack when the last alternative of a choice is being explored. But no-goods can only be extracted if LAO is disabled as the last alternatives are required for the computation of no-goods. LAO is automatically disabled for the part of the search tree with a depth less than the no-goods depth limit. That is, an engine requires more memory during search with a larger depth limit. This can pose an issue for very deep search trees.

  What also becomes clear from this discussion is that the peak search depth reported by a search engine increases with an increased depth limit.

- It is easy to see that no-goods get longer (with more literals) with increasing search tree depth. The larger a no-good gets, the less useful it gets: the likelihood that all literals but one are subsumed but not failed (which is required for propagation) decreases.

- When the no-goods are posted, a single propagator for all no-goods is created. This propagator requires :math:`O(n)` memory for :math:`n` no-good literals. Hence, increasing the depth limit also increases the memory required by the propagator.

..

.. _tip:m:search:cmdnogoods:

.. mpg-tip:: Controlling no-goods with the commandline driver

   Whether no-goods are used and which no-goods depth limit is used can also be controlled from the commandline via the ``-nogoods`` and ``-nogoods-limit`` commandline options, see :ref:`chap:m:driver`.


.. _modeling:m-search:no-goods-from-solutions-restarts:

.. rubric:: No-goods from solutions restarts.

The ``master()`` function shown above posts no-goods even when the restart meta search engine has found a solution. When the engine continues this means that the same solution might not be found again as it has been excluded by a no-good. The situation is even slightly more complicated: the solution might not be excluded if it has been found at a depth that exceeds the no-good depth limit.

If no-goods should not be posted when a solution has been found, the ``master()`` function can be redefined as:

.. mpg-code:: snippet:m-search:tip:m:search:cmdnogoods:code:1
   :direct:


.. _modeling:m-search:limitations:

.. rubric:: Limitations.

Not all branchers support the generation of no-goods. In that case the longest sequence of no-goods starting from the root of the search tree up to the first choice that belongs to a brancher that does not support no-goods is used.

All pre-defined branchers for integer, Boolean, and set variables support no-goods unless user-defined commit functions are used (see :ref:`sec:m:branch:userval`). Branchers for float variables and branchers for executing code (see :ref:`sec:m:branch:code`) do not support no-goods.

.. _modeling:m-search:no-goods-and-parallel-search:

.. rubric:: No-goods and parallel search.

The reason why after a restart no-goods can be extracted is because search computed the no-goods by exploring entire failed subtrees during search. This might not be true during parallel search. While parallel search engines also support the extraction of no-goods, the number of no-goods that can be extracted tend to be rather small.

.. _sec:m:search:trace:


.. _modeling:m-search:tracing-search:

Tracing search
--------------

The execution of search engines can be traced, where all important events of a search engine can be recorded and processed by a *search tracer*. A search tracer is implemented by a subclass of `SearchTracer <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1SearchTracer.html>`__ where several virtual member functions must be implemented that are called when a corresponding event occurs:

- A single *init-event* occurs when the initialization of a search engine together with all of its components such as sub-engines and workers is complete. See below for more details about sub-engines and workers.

- A single *done-event* occurs when all components (workers) of a search engine have been deleted.

- Each time a new node of the search tree is created, a *node-event* occurs that provides information about the newly created node and the edge leading to it (unless it is the root node).

- Some search engines perform several *rounds*: each time a new round starts, a *round-event* occurs. Restart-based search (RBS) starts a new round by performing a restart (see :ref:`sec:m:search:restart`) and limited-discrepancy search (LDS) starts a new round for each probe with a different discrepancy.

- Some search engines might skip edges, in these cases a *skip-event* is generated. See below for more details.

.. _modeling:m-search:search-tracers:

.. rubric:: Search tracers.

.. mpg-code:: example search tracer
   :name: fig:m:search:tracer
   :caption: A simple tracer printing to std::cout


A simple search tracer printing information to ``std::cout`` is shown in :numref:`fig:m:search:tracer`. A similar search tracer is defined by the class `StdSearchTracer <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1StdSearchTracer.html>`__.

As mentioned above, all events correspond to virtual member functions that are called when an event occurs. The member functions are executed in mutual exclusion as the events might occur in parallel from search engines using multiple workers (threads).

.. _modeling:m-search:defining-a-search-tracer:

.. rubric:: Defining a search tracer.

A search tracer can be defined as part of the search options (see :ref:`sec:m:search:options`). For example, if ``t`` is a search tracer, then creating a depth-first search engine using the tracer ``t`` can be done as follows:

.. mpg-code:: snippet:m-search:fig:m:search:tracer:code:1
   :direct:


.. _modeling:m-search:init-event:

.. rubric:: Init-event.

After the search engine(s) have completed their initialization, the member function ``init()`` is called. The class `SearchTracer <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1SearchTracer.html>`__ provides member functions with which the configuration of the search engine can be inspected. Search engines are identified by engine identifiers of type ``unsigned int``.

The root engine has always the identifier ``0U``. Meta engines such as restart-based search (RBS) and portfolio-based search (PBS) have sub engines whereas non-meta engines have workers that perform the actual exploration of the search tree. The following code:

.. mpg-code:: example search tracer:init


lists all engines together with their engine identifiers starting with the root engine (the member function ``engines()`` returns the number of engines). Information about an engine is provided by the member function ``engine()`` which takes an engine identifier and returns a reference to an object of type `SearchTracer::EngineInfo <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1SearchTracer_1_1EngineInfo.html>`__ providing information about an engine.

For simple engines (that is, non-meta engines) such as depth-first (DFS), branch-and-bound (BAB), and limited-discrepancy search (LDS), the following code prints information about their workers:

.. mpg-code:: example search tracer:init for engines


An engine of type AOE (for any other engine) is an engine that Gecode creates in certain situations if the root of the search tree is already known to be failed.

For meta engines, the following code prints information about their sub-engines:

.. mpg-code:: example search tracer:init for meta engines


For example, for a branch-and-bound engine with a single worker (using a single thread), the ``init()`` function prints:

.. mpg-code:: snippet:m-search:fig:m:search:tracer:cmd:1
   :direct:


For a branch-and-bound engine with four workers (using four threads), the ``init()`` function prints:

.. mpg-code:: snippet:m-search:fig:m:search:tracer:cmd:2
   :direct:


For a restart-based search engine using a depth-first engine with a single worker (using a single thread), the ``init()`` function prints:

.. mpg-code:: snippet:m-search:fig:m:search:tracer:cmd:3
   :direct:


For a portfolio-based search engines with two depth-first search engines as assets using four threads, the ``init()`` function prints:

.. mpg-code:: snippet:m-search:fig:m:search:tracer:cmd:4
   :direct:


Note that assets can be also restart-based search engines.

.. _modeling:m-search:node-events:

.. rubric:: Node-events.

.. mpg-code:: example search tracer:node
   :name: fig:m:search:tracer:node
   :caption: Member function for node-events


The virtual member function called for a node-event takes information about an edge of type `SearchTracer::EdgeInfo <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1SearchTracer_1_1EdgeInfo.html>`__ and a node of type `SearchTracer::NodeInfo <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1SearchTracer_1_1NodeInfo.html>`__ as input. The code shown in :numref:`fig:m:search:tracer:node` prints the type of the node. It then prints information about the worker identifier (``ni.wid()``) and node identifier (``ni.nid()``). Both worker and node identifiers are of type ``unsigned int``. Note that the edge also has information about the parent node of the current node and which worker created it. In case the edge does not exist (that is, the test ``ei`` is false), the node is in fact the root node of the search tree. The string printed is the output printed by the brancher corresponding to the edge (see :ref:`sec:m:branch:print` for more information).

Note that the node identifiers are unique per worker. As the number of workers is available with the ``workers()`` member function, the numbers can be made easily unique globally.

.. _modeling:m-search:round-events:

.. rubric:: Round-events.

A round-event is generated either before a restart by a restart-based search engine or when a limited-discrepancy search engine starts a new probe with an increased discrepancy. The information passed to the ``round()`` member function is the engine identifier corresponding to the engine starting a new round:

.. mpg-code:: example search tracer:round


Note that the node identifiers are not reset at a round-event.

.. _modeling:m-search:skip-events:

.. rubric:: Skip-events.

A skip event occurs when a worker decides that a certain node does not need to be explored. This can happen for branch-and-bound search engines where an entire subtree is pruned or for limited discrepancy search where a solution is omitted as it had already been found during a previous probe with a smaller discrepancy limit. The information provided to the ``skip()`` member function is of type `SearchTracer::EdgeInfo <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1SearchTracer_1_1EdgeInfo.html>`__:

.. mpg-code:: example search tracer:skip


.. _modeling:m-search:done-event:

.. rubric:: Done-event.

The done event is executed if all workers have terminated. Here it just prints this fact:

.. mpg-code:: example search tracer:done


Note that, however that the tracer is not deleted after a done event. This is the obligation of the user of the tracer.

.. _sec:m:search:cpprofiler:


.. _modeling:m-search:using-the-cpprofiler:

Using the CPProfiler
--------------------

The CPProfiler is a graphical tool for better understanding the search space of a problem :cite:`cpprofiler`. It can be downloaded from `github.com/cp-profiler <https://github.com/cp-profiler/cp-profiler>`__.

Gecode can connect to an already running instance of the CPProfiler by means of creating a search tracer. The tracer then sends all search trace information to the respective instance of the CPProfiler, which then can use the trace information for visualization and analysis.

A search tracer to connect to a running CPProfiler instance can be created by creating an object of class `CPProfilerSearchTracer <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1CPProfilerSearchTracer.html>`__ as follows:

.. mpg-code:: snippet:m-search:sec:m:search:cpprofiler:code:1
   :direct:


where ``id`` (an integer) defines the execution identifier to be displayed by the CPProfiler, ``name`` (a string of type ``std::string``) defines the name displayed by the CPProfiler, ``port`` (an unsigned integer) defines the network port used by the CPProfiler, and ``gi`` is a pointer to an object of class `CPProfilerSearchTracer::GetInfo <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1CPProfilerSearchTracer_1_1GetInfo.html>`__ for information about a search tree to be displayed by the CPProfiler. The arguments for ``port`` and ``gi`` are optional, the default for ``port`` is defined by ``Search::Config::cpprofiler_port`` (currently ``6565``) and the default for ``gi`` is ``nullptr``.

Note that commandline support for the CPProfiler is provided, see :ref:`sec:m:driver:options`. There are options to specify the execution identifier, the port, and whether default information about nodes in the search tree should be transferred to the CPProfiler.

An object that determines which information about a search tree node should be displayed when the node is inspected in the CPProfiler, can be defined by inheriting from the class `CPProfilerSearchTracer::GetInfo <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1CPProfilerSearchTracer_1_1GetInfo.html>`__ and defining the virtual member function:

.. mpg-code:: snippet:m-search:sec:m:search:cpprofiler:code:2
   :direct:


that must return an information string of type ``std::string`` for the search tree node ``home``.

.. [1]
   This is a very rough characterization: a processing unit could be a CPU, a processor core, or a multi-threading unit. If you want to find out how many processing units Gecode believes your machine has, invoke the configuration summary as described in :ref:`tip:m:comfy:conf`.

.. [2]
   Please note that the engine might restart several times until a first solution has been found.

.. mpg-covered: caption:docs/src/chapters/modeling/m-search.tex.in:97:fig:m:search:tree
.. mpg-covered: table:docs/src/chapters/modeling/m-search.tex.in:100:tabular@docs/src/chapters/modeling/m-search.tex.in:100
.. mpg-covered: table:docs/src/chapters/modeling/m-search.tex.in:101:tabular@docs/src/chapters/modeling/m-search.tex.in:101
.. mpg-covered: table:docs/src/chapters/modeling/m-search.tex.in:140:tabular@docs/src/chapters/modeling/m-search.tex.in:140
.. mpg-covered: caption:docs/src/chapters/modeling/m-search.tex.in:211:fig:m:search:hybrid
.. mpg-covered: tip:docs/src/chapters/modeling/m-search.tex.in:359:unlabeled-tip@docs/src/chapters/modeling/m-search.tex.in:359
.. mpg-covered: caption:docs/src/chapters/modeling/m-search.tex.in:453:fig:m:search:out:8
.. mpg-covered: caption:docs/src/chapters/modeling/m-search.tex.in:490:fig:m:search:out:1
.. mpg-covered: caption:docs/src/chapters/modeling/m-search.tex.in:572:fig:m:search:statistics
.. mpg-covered: table:docs/src/chapters/modeling/m-search.tex.in:574:tabular@docs/src/chapters/modeling/m-search.tex.in:574
.. mpg-covered: caption:docs/src/chapters/modeling/m-search.tex.in:632:fig:m:search:engine
.. mpg-covered: table:docs/src/chapters/modeling/m-search.tex.in:634:tabular@docs/src/chapters/modeling/m-search.tex.in:634
.. mpg-covered: caption:docs/src/chapters/modeling/m-search.tex.in:678:fig:m:search:options
.. mpg-covered: table:docs/src/chapters/modeling/m-search.tex.in:680:tabular@docs/src/chapters/modeling/m-search.tex.in:680
.. mpg-covered: caption:docs/src/chapters/modeling/m-search.tex.in:772:fig:m:search:stop
.. mpg-covered: table:docs/src/chapters/modeling/m-search.tex.in:774:tabular@docs/src/chapters/modeling/m-search.tex.in:774
.. mpg-covered: tip:docs/src/chapters/modeling/m-search.tex.in:802:unlabeled-tip@docs/src/chapters/modeling/m-search.tex.in:802
.. mpg-covered: caption:docs/src/chapters/modeling/m-search.tex.in:1160:fig:m:search:mi
.. mpg-covered: table:docs/src/chapters/modeling/m-search.tex.in:1162:tabular@docs/src/chapters/modeling/m-search.tex.in:1162
.. mpg-covered: caption:docs/src/chapters/modeling/m-search.tex.in:1244:fig:m:search:restart:default
.. mpg-covered: literal-projection:docs/src/chapters/modeling/m-search.tex.in:1245:default master and slave functions
.. mpg-covered: literal-projection:docs/src/chapters/modeling/m-search.tex.in:1254:default master and slave functions:restart-based search
.. mpg-covered: caption:docs/src/chapters/modeling/m-search.tex.in:1322:fig:m:search:restart:sketch
.. mpg-covered: literal-projection:docs/src/chapters/modeling/m-search.tex.in:1323:model sketch for LNS
.. mpg-covered: literal-projection:docs/src/chapters/modeling/m-search.tex.in:1359:model sketch for LNS:slave function
.. mpg-covered: literal-projection:docs/src/chapters/modeling/m-search.tex.in:1454:default master and slave functions:portfolio search
.. mpg-covered: tip:docs/src/chapters/modeling/m-search.tex.in:1572:unlabeled-tip@docs/src/chapters/modeling/m-search.tex.in:1572
.. mpg-covered: tip:docs/src/chapters/modeling/m-search.tex.in:1580:unlabeled-tip@docs/src/chapters/modeling/m-search.tex.in:1580
.. mpg-covered: tip:docs/src/chapters/modeling/m-search.tex.in:1660:unlabeled-tip@docs/src/chapters/modeling/m-search.tex.in:1660
.. mpg-covered: caption:docs/src/chapters/modeling/m-search.tex.in:1699:fig:m:search:nogoods
.. mpg-covered: caption:docs/src/chapters/modeling/m-search.tex.in:1970:fig:m:search:tracer
.. mpg-covered: literal-projection:docs/src/chapters/modeling/m-search.tex.in:1971:example search tracer
.. mpg-covered: literal-projection:docs/src/chapters/modeling/m-search.tex.in:2012:example search tracer:init
.. mpg-covered: literal-projection:docs/src/chapters/modeling/m-search.tex.in:2025:example search tracer:init for engines
.. mpg-covered: literal-projection:docs/src/chapters/modeling/m-search.tex.in:2032:example search tracer:init for meta engines
.. mpg-covered: caption:docs/src/chapters/modeling/m-search.tex.in:2069:fig:m:search:tracer:node
.. mpg-covered: literal-projection:docs/src/chapters/modeling/m-search.tex.in:2070:example search tracer:node
.. mpg-covered: literal-projection:docs/src/chapters/modeling/m-search.tex.in:2103:example search tracer:round
.. mpg-covered: literal-projection:docs/src/chapters/modeling/m-search.tex.in:2117:example search tracer:skip
.. mpg-covered: literal-projection:docs/src/chapters/modeling/m-search.tex.in:2123:example search tracer:done
