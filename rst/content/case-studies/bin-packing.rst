.. _chap:c:bpp:

Bin packing
===========


This chapter studies the classic bin packing problem. Three models are presented: a first and naive model (presented in :ref:`sec:c:bpp:naive` ) that suffers from poor propagation to be feasible. This is followed by a model ( :ref:`sec:c:bpp:prop` ) that uses the special ``binpacking`` constraint to drastically improve constraint propagation. A final model improves the second model by a problem-specific branching ( :ref:`sec:c:bpp:branch` ) that also breaks many symmetries during search.

.. important::

   This case study requires knowledge on programming branchers, see :ref:`part:b` .

.. _sec:c:bpp:problem:

Problem
-------


The bin packing problem consists of packing :math:`\mathtt{n}` items of sizes :math:`\mathtt{size}_i` (:math:`0\leq i<\mathtt{n}`) into the smallest number of bins such that the capacity :math:`\mathtt{c}` of each bin is not exceeded.


.. mpg-figure:: An example optimal bin packing
   :name: fig:c:bpp:optimal

   .. only:: html

      .. image:: /figures/fig-c-bpp-optimal.svg
         :alt: An example optimal bin packing

   .. only:: latex

      .. image:: /figures/pdf/fig-c-bpp-optimal.pdf
         :alt: An example optimal bin packing


For example, the :math:`11` items of sizes

.. math:: 6,6,6,5,3,3,2,2,2,2,2

require at least four bins of capacity :math:`10` as shown in :numref:`fig:c:bpp:optimal` where the items are numbered starting from zero.

.. _sec:c:bpp:naive:

A naive model
-------------


Before turning our attention to a naive model for the bin packing problem, this section discusses instance data for the bin packing problem and how to compute lower and upper bounds for the number of required bins.

.. _fig:c:bpp:data:

Instance data.
''''''''''''''

.. mpg-code:: bin packing naive:instance data
   :caption: Instance data for a bin packing problem


:ref:`fig:c:bpp:data` shows an example instance of a bin packing problem, where ``n`` defines the number of items, ``c`` defines the capacity of each ``bin``, and the array ``size`` defines the size of each item. For simplicity, we assume that the item size are ordered in decreasing order.

The data corresponds to the instance ``N1C1W1_N`` taken from  :cite:p:`BISON:1997` . More information on other data instances can be found in :ref:`sec:c:bpp:info` .

.. _fig:c:bpp:lower:

Computing a lower bound.
''''''''''''''''''''''''

.. mpg-code:: bin packing naive:compute lower bound
   :caption: Computing a lower bound for the number of bins


A simple lower bound :math:`L_1` (following Martello and Toth  :cite:p:`MartelloToth:1990` ) for the number of bins required for a bin packing problem just considers the size of all items and the bin capacity as follows:

.. math:: L_1=\left\lceil\frac{1}{c}\sum_{i=0}^{\mathtt{n}-1} \mathtt{size}_i\right\rceil

The computation of the lower bound :math:`L_1` is as to be expected and is shown in :ref:`fig:c:bpp:lower` . The ceiling operation is replaced by adding :math:`\mathtt{c}-1` followed by truncating integer division with :math:`\mathtt{c}`.

Note that more accurate lower bounds are known, see :ref:`sec:c:bpp:info` for more information.

.. _case-studies:bin-packing:computing-an-upper-bound:

Computing an upper bound.
'''''''''''''''''''''''''

An obvious upper bound for the number of bins required is the number of items: each item is packed into a separate bin (provided that no item size exceeds the bin capacity ``c``). A better upper bound can be computed by constructing a solution by packing items into bins following a first-fit strategy: pack all items into the first bin of sufficient free capacity.


.. _fig:c:bpp:upper:

.. mpg-code:: bin packing naive:compute upper bound
   :caption: Computing an upper bound for the number of bins


:ref:`fig:c:bpp:upper` shows the function ``upper()`` that returns an upper bound for the number of bins. It initializes an array ``free`` of ``n`` integers with the bin capacity ``c``. The integer ``u`` refers to the index of the last used bin (that is, a bin into which an item has been packed). The function returns the number of used bins (that is, the index ``u`` plus one).

Each item is packed into a bin with sufficient free capacity where ``j`` refers to the next free bin:


.. mpg-code:: bin packing naive:pack items into free bins
   :direct:


The next free bin ``j`` is searched for as follows:


.. mpg-code:: bin packing naive:find free bin
   :direct:


The loop always terminates as there is one bin for each item.

Note that ``upper()`` has :math:`O(\mathtt{n}^2)` complexity in the worst case but could be made more efficient by speeding up finding a fitting bin.


.. mpg-figure:: A non-optimal bin packing found during upper-bound computation
   :name: fig:c:bpp:greedy

   .. only:: html

      .. image:: /figures/fig-c-bpp-greedy.svg
         :alt: A non-optimal bin packing found during upper-bound computation

   .. only:: latex

      .. image:: /figures/pdf/fig-c-bpp-greedy.pdf
         :alt: A non-optimal bin packing found during upper-bound computation


The solution constructed during computation of ``upper()`` is not necessarily optimal. As an example, consider the packing computed by ``upper()`` for the example from :ref:`sec:c:bpp:problem` shown in :numref:`fig:c:bpp:greedy` : it takes five rather than four bins because one of the items 4 and 5 should be packed together with item 3 rather than with one of the items 0, 1, and 2.

If both lower and upper bound coincide the solution constructed is of course optimal and we are done solving the bin packing problem. For reasons of simplicity, our model just forsakes this opportunity and re-computes an optimal solution by constraint programming.

.. _fig:c:bpp:naive:

Model proper.
'''''''''''''

.. mpg-code:: bin packing naive
   :caption: A naive script for solving a bin packing problem
   :download:


:ref:`fig:c:bpp:naive` shows a script for the bin packing model. The script defines integers ``l`` and ``u`` that store the lower and upper bound as discussed above. A *load variable* :math:`\mathtt{load}_i` (taking values from :math:`\{0,\ldots,\mathtt{c}\}`) defines the total size of all items packed into bin :math:`i`. The script uses ``u`` load variables as the upper bound guarantees that ``u`` bins are sufficient to find an optimal solution. A *bin variable* :math:`\mathtt{bin}_i` (taking values from :math:`\{0,\ldots,\mathtt{u}-1\}` defines for each item :math:`i` into which bin it is packed. The variable ``bins`` defines the number of *used bins*. A bin is *used* if at least one item is packed into it, otherwise it is an *excess* bin.

The integer ``s`` is initialized as the size of all items and ``sizes`` is initialized as an integer argument array of all sizes.

The ``cost()`` function as required by the class ``MinimizeScript`` (see :ref:`sec:m:driver:script` ) returns the number of ``bins``.

.. _case-studies:bin-packing:excess-bins:

Excess bins.
''''''''''''

If the script finds a solution that uses less than ``u`` bins, say ``k`` (the value of the ``bins`` variable), then :math:`\mathtt{u}-\mathtt{k}` of the load variables corresponding to excess bins are zero. To remove many symmetrical solutions that only differ in which bins are excess bins, the script constrains the excess bins to be the bins :math:`\mathtt{k},\ldots,\mathtt{u}-1`:


.. mpg-code:: bin packing naive:excess bins
   :direct:


.. _case-studies:bin-packing:constraining-load-and-bin-variables:

Constraining load and bin variables.
''''''''''''''''''''''''''''''''''''

The sum of all load variables must be equal to the size of all items:


.. mpg-code:: bin packing naive:loads add up to item sizes
   :direct:


The load variable for a bin must be constrained according to which items are packed into the bin. A standard formulation of this constraint uses Boolean variables :math:`\mathtt{x}_{i,j}` which determine whether item :math:`i` has been packed into bin :math:`j`. That is, for each item :math:`0\leq i<\mathtt{n}` the following constraint must hold:

.. math::

   \mathtt{x}_{i,j}=1\iff \mathtt{bin}_i=j\qquad (0\leq
   j<\mathtt{u})

A more efficient propagator for the very same constraint is available as a ``channel`` constraint between an array of Boolean variables and a single integer variable, see :ref:`sec:m:integer:channel` . That is, for each item :math:`0\leq
i<\mathtt{n}` the following constraint must hold:

.. math::

   \mathtt{channel}(\langle
   \mathtt{x}_{i,0},\mathtt{x}_{i,1},\ldots,
   \mathtt{x}_{i,u-1}\rangle,\mathtt{bin}_i)

Note that :math:`\langle
\mathtt{x}_{i,0},\mathtt{x}_{i,1},\ldots,
\mathtt{x}_{i,u-1}\rangle` corresponds to ``x.col(``\ :math:`i`\ ``)``.

Furthermore, the size of all items packed into a bin must equal the corresponding load variable. Both constraints are expressed as follows, using a matrix ``x`` (see :ref:`sec:m:minimodel:matrix` ) of Boolean variables ``_x``:


.. mpg-code:: bin packing naive:loads are equal to packed items
   :direct:


.. _case-studies:bin-packing:symmetry-breaking:

Symmetry breaking.
''''''''''''''''''

Items of the same size are equivalent as far as the model is concerned. To break symmetries, the bins for items of the same size are ordered:


.. mpg-code:: bin packing naive:symmetry breaking
   :direct:


The loop exploits that items are ordered according to size and hence items of the same size are adjacent.

.. _case-studies:bin-packing:pack-items-that-require-a-bin:

Pack items that require a bin.
''''''''''''''''''''''''''''''

If the size :math:`s` of an item exceeds :math:`\lceil\frac{\mathtt{c}}{2}\rceil` (or, equivalently, :math:`2s>\mathtt{c}`), the item cannot share a bin with any other item also exceeding half of the capacity. That is, items exceeding half of the capacity can be directly assigned to different bins:


.. mpg-code:: bin packing naive:pack items that require a bin
   :direct:


The assignment of items to bins is compatible with the symmetry breaking constraints discussed previously.

.. _case-studies:bin-packing:branching:

Branching.
''''''''''

We choose a naive branching strategy that first branches on the number of required ``bins``, followed by trying to assign items to bins.


.. mpg-code:: bin packing naive:branching
   :direct:


Note that by choosing the ``bin`` variables with order ``INT_VAR_NONE()`` assigns the largest item to a bin first as items are sorted by decreasing size.

The script in :ref:`fig:c:bpp:naive` does not show that the script uses branch-and-bound search to find a best solution. Why depth-first search is not sufficient with parallel search is discussed in :ref:`tip:m:search:parbab` .

.. _case-studies:bin-packing:running-the-model:

Running the model.
''''''''''''''''''

When running the naive model (All measurements in this chapter have been made on a laptop with an Intel i5 M430 processor (2.27 GHz, two cores, hyper-threading), 4 GB of main memory, running Windows 7 x64, and using Gecode 3.4.3.), it becomes apparent that the model is indeed naive. Finding the best solution takes :math:`29.5` seconds and :math:`2\,451\,018` failures. Clearly, that leaves ample room for improvement in the following sections!

.. _sec:c:bpp:prop:

Improving propagation
---------------------


This section improves (and simplifies) the naive model from the previous section by using a dedicated ``binpacking`` constraint.


.. _fig:c:bpp:prop:

.. mpg-code:: bin packing propagation
   :caption: A script with improved propagation for solving a bin packing problem
   :download:


.. _case-studies:bin-packing:model:

Model.
''''''

The improved model is shown in :ref:`fig:c:bpp:prop` . Instead of using Boolean variables ``x``, ``linear`` constraints, and ``channel`` constraints it uses the ``binpacking`` constraint (see also :ref:`sec:m:integer:bpp` ). The constraint enforces that the packing of items as defined by the ``bin`` variables corresponds to the ``load`` variables.


.. _case-studies:bin-packing:running-the-model-2:

Running the model.
''''''''''''''''''

Finding a best solution using the model with improved propagation takes :math:`1.5` seconds and :math:`64\,477` failures. That is, this model runs almost :math:`20` times faster than the naive model and reduces the number of failures by a factor of :math:`38`.

.. _sec:c:bpp:branch:

Improving branching
-------------------


This section describes a problem specific branching to improve the model of the previous section even further.

.. _case-studies:bin-packing:complete-decreasing-best-fit-branching:

Complete decreasing best fit branching.
'''''''''''''''''''''''''''''''''''''''

The improved branching for bin packing is called complete decreasing best-fit (CDBF) and is due to Gent and Walsh  :cite:p:`CDBF` . The branching uses some additional improvements suggested by Shaw in  :cite:p:`Shaw:CP:2004` .

The branching tries to assign items to bins during search where the items are tried in order of decreasing size. The bin is selected according to a best fit strategy: try to put the item into a bin with sufficient but least free space. The space of the bin after packing an item is called the bin’s *slack*. If there is no bin with sufficient free space left, CDBF fails.

Suppose that CDBF selects item ``i`` and bin ``b``. Then the following actions are taken during branching:

- If there is a perfect fit (that is, the slack is zero), branching assigns item ``i`` to bin ``b``. This corresponds to a branching with a single alternative.

- If all possible bins have the same slack, branching assigns item ``i`` to bin ``b``. Again, this corresponds to a branching with a single alternative.

- Otherwise, CDBF tries two alternatives in the following order:

  - Assign item ``i`` to bin ``b``.

  - Not only prune bin ``b`` from the potential bins for item ``i`` but also prune all bins with the same slack as ``b`` from the potential bins for all items with the same size as ``i``.

Note that the second alternative of CDBF performs symmetry breaking during search as it prunes also with respect to equivalent items and bins.

Also note that the symmetry breaking based on items of same size as discussed in :ref:`sec:c:bpp:naive` cannot be used as it is incompatible with rule for a perfect fit (Thanks to Florian ??? for pointing this out.).


.. _fig:c:bpp:branch:

Model.
''''''

.. mpg-code:: bin packing branching
   :caption: A script with improved branching for solving a bin packing problem
   :download:


The only change to the model compared to :ref:`sec:c:bpp:prop` is that it uses the branching ``cdbf`` for assigning items to bins during search.

.. _fig:c:bpp:cdbf:

Brancher creation.
''''''''''''''''''

.. mpg-code:: bin packing branching:CDBF
   :caption: CDBF brancher and branching


The ``cdbf`` branching takes load variables (for computing the free space of a bin), bin variables (to pack items into bins), and the item sizes (to compute how much space an item requires) as input and posts the ``CDBF`` brancher as shown in :ref:`fig:c:bpp:cdbf` .

The branching post function ``cdbf()`` creates view arrays for the respective variables, creates a shared integer array of type ``IntSharedArray`` (see :ref:`tip:m:integer:sharedelement` ) and posts a ``CDBF`` brancher. The advantage of using a shared array is that the sizes are stored only once in memory and branchers in different spaces have shared access to the same memory area (see also :ref:`sec:p:memory:shared` ).

The brancher ``CDBF`` stores the load variables, bin variables, and item sizes together with an integer ``item``. The integer ``item`` is used to find the next unassigned item. It is declared ``mutable`` so that the ``const`` ``status()`` function (see below) can modify it. The brancher exploits that the items are sorted by decreasing size: by initializing ``item`` to zero the brancher is trying to pack the largest item first.

By default, the ``dispose()`` member function of a brancher is not called when the brancher’s home space is deleted. However, the ``dispose()`` function of the ``CDBF`` brancher must call the destructor of the shared integer array ``size``. Hence, the constructor of ``CDBF`` calls the ``notice()`` function of the home space so that the brancher’s ``dispose()`` function is called when home is deleted (see also :ref:`par:p:started:dispose` ). Likewise, the ``dispose()`` function calls the ``ignore()`` function before the brancher is disposed.

.. _case-studies:bin-packing:status-computation:

Status computation.
'''''''''''''''''''

The ``status()`` function tries to find a yet unassigned view for branching in the view array ``bin``. It starts inspecting the views at position ``item`` and skips all already assigned views. If there is a not yet assigned view left, ``item`` is updated to that unassigned view and ``true`` is returned (that is, more branching is needed). Otherwise, the brancher returns ``false`` as no more branching is needed:


.. mpg-code:: bin packing branching:status function
   :direct:


As the items are sorted by decreasing size, the integer ``item`` refers to the largest not-yet packed item.

.. _case-studies:bin-packing:choice-computation-initialization:

Choice computation: initialization.
'''''''''''''''''''''''''''''''''''

The ``choice()`` function implements the actual heuristic. The function uses ``n`` for the number of items, ``m`` for the number of bins, and initializes a ``region`` for managing temporary memory (see :ref:`par:p:memory:region` ) as follows:


.. mpg-code:: bin packing branching:choice function
   :direct:


The ``choice()`` function can rely on the fact that it is immediately executed after the ``status()`` function has been executed. That entails that ``item`` refers to the largest not-yet packed item.

.. container:: samepage

   The function computes in ``free`` the free space of each bin. From the maximal load the size of items that have already been packed (that is, the item’s ``bin`` variable is already assigned) is subtracted:


.. mpg-code:: bin packing branching:initialize free space in bins
   :direct:


The ``choice()`` function uses the integer ``slack`` to track the slack of the so-far best fit (initialized with ``INT_MAX`` such that any fit will be better). The integer ``n_possible`` counts the number of possible bins for the item whereas ``n_same`` counts the number of best fits. The array ``same`` stores all bins with the same so-far smallest slack.


.. mpg-code:: bin packing branching:initialize bins with same slack
   :direct:


The array ``same`` is initialized to contain the bin ``-1``: if no bin has sufficient space for the current item this will guarantee that the ``commit()`` function (see below) leads to failure.

.. _case-studies:bin-packing:choice-computation-create-choice:

Choice computation: create choice.
''''''''''''''''''''''''''''''''''

In order to find all best fits, all bins are examined. If the current item fits into a bin, the number of possible bins ``n_possible`` is incremented and all best fits are remembered in the array ``same`` as follows:


.. mpg-code:: bin packing branching:find best fit
   :direct:


Note that finding a better fit updates ``slack`` and resets the bins stored in ``same``.

.. container:: samepage

   Now, the ``choice()`` function determines whether a special case needs to be dealt with:

   - Is the best fit a perfect fit: that is, ``slack`` is zero?

   - Are all fits a best fit: that is, ``n_same`` is equal to ``n_possible``?

   - Is there no fitting bin: that is, ``n_possible`` is zero?

In these cases a choice with a single alternative and otherwise a choice with two alternatives is created:


.. mpg-code:: bin packing branching:create choice
   :direct:


.. _fig:c:bpp:choice:

.. mpg-code:: bin packing branching:CDBF choice
   :caption: CDBF choice


The definition of the choice class is shown in :ref:`fig:c:bpp:choice` . The choice stores the current item and in the array ``same`` all bins with the same slack. The choice does not need to store any information regarding items of same size as this information is available from the brancher.

.. _case-studies:bin-packing:commit-function:

Commit function.
''''''''''''''''

.. container:: samepage

   The ``commit()`` function takes a choice of type ``CDBF::Choice`` and the alternative ``a`` (either ``0`` or ``1``) as input:


.. mpg-code:: bin packing branching:commit function
   :direct:


Committing to the first alternative tries to pack ``item`` into the first bin stored in ``same`` as follows:


.. mpg-code:: bin packing branching:commit to first alternative
   :direct:


Committing to the second alternative removes all ``n_same`` bins stored in ``same`` from all items that have the same size as ``item`` as follows:


.. mpg-code:: bin packing branching:commit to second alternative
   :direct:


The iterator :api:`Iter::Values::Array` iterates over all values stored in an array (they must be in sorted order) and the operation ``minus_v()`` prunes all values as defined by an iterator from a view, see :ref:`sec:p:domain:iter` .


.. _case-studies:bin-packing:running-the-model-3:

Running the model.
''''''''''''''''''

Finding a best solution using the model with improved propagation and improved branching takes :math:`84` milliseconds and :math:`3\,098` failures. That is, this model runs :math:`352` times faster than the naive model and reduces the number of failures by a factor of :math:`791`.

.. _sec:c:bpp:info:

More information
----------------


Bin packing featuring all models presented in this chapter is also available as a Gecode example, see :api:`bin-packing` . The example also makes use of a more accurate lower bound known as :math:`L_2`  :cite:p:`MartelloToth:1990` .

..
   Migration traceability for the migrated semantic constructs above.

.. mpg-covered: caption:docs/src/chapters/case-studies/c-bin-packing.tex.in:40:fig:c:bpp:optimal
.. mpg-covered: caption:docs/src/chapters/case-studies/c-bin-packing.tex.in:94:fig:c:bpp:data
.. mpg-covered: literal-projection:docs/src/chapters/case-studies/c-bin-packing.tex.in:95:bin packing naive:instance data
.. mpg-covered: caption:docs/src/chapters/case-studies/c-bin-packing.tex.in:112:fig:c:bpp:lower
.. mpg-covered: literal-projection:docs/src/chapters/case-studies/c-bin-packing.tex.in:113:bin packing naive:compute lower bound
.. mpg-covered: caption:docs/src/chapters/case-studies/c-bin-packing.tex.in:144:fig:c:bpp:upper
.. mpg-covered: literal-projection:docs/src/chapters/case-studies/c-bin-packing.tex.in:145:bin packing naive:compute upper bound
.. mpg-covered: literal-projection:docs/src/chapters/case-studies/c-bin-packing.tex.in:159:bin packing naive:pack items into free bins
.. mpg-covered: literal-projection:docs/src/chapters/case-studies/c-bin-packing.tex.in:162:bin packing naive:find free bin
.. mpg-covered: caption:docs/src/chapters/case-studies/c-bin-packing.tex.in:170:fig:c:bpp:greedy
.. mpg-covered: caption:docs/src/chapters/case-studies/c-bin-packing.tex.in:219:fig:c:bpp:naive
.. mpg-covered: literal-projection:docs/src/chapters/case-studies/c-bin-packing.tex.in:220:bin packing naive
.. mpg-covered: literal-projection:docs/src/chapters/case-studies/c-bin-packing.tex.in:254:bin packing naive:excess bins
.. mpg-covered: literal-projection:docs/src/chapters/case-studies/c-bin-packing.tex.in:260:bin packing naive:loads add up to item sizes
.. mpg-covered: literal-projection:docs/src/chapters/case-studies/c-bin-packing.tex.in:292:bin packing naive:loads are equal to packed items
.. mpg-covered: literal-projection:docs/src/chapters/case-studies/c-bin-packing.tex.in:299:bin packing naive:symmetry breaking
.. mpg-covered: literal-projection:docs/src/chapters/case-studies/c-bin-packing.tex.in:310:bin packing naive:pack items that require a bin
.. mpg-covered: literal-projection:docs/src/chapters/case-studies/c-bin-packing.tex.in:319:bin packing naive:branching
.. mpg-covered: caption:docs/src/chapters/case-studies/c-bin-packing.tex.in:350:fig:c:bpp:prop
.. mpg-covered: literal-projection:docs/src/chapters/case-studies/c-bin-packing.tex.in:351:bin packing propagation
.. mpg-covered: caption:docs/src/chapters/case-studies/c-bin-packing.tex.in:425:fig:c:bpp:branch
.. mpg-covered: literal-projection:docs/src/chapters/case-studies/c-bin-packing.tex.in:426:bin packing branching
.. mpg-covered: caption:docs/src/chapters/case-studies/c-bin-packing.tex.in:437:fig:c:bpp:cdbf
.. mpg-covered: literal-projection:docs/src/chapters/case-studies/c-bin-packing.tex.in:439:bin packing branching:CDBF
.. mpg-covered: literal-projection:docs/src/chapters/case-studies/c-bin-packing.tex.in:486:bin packing branching:status function
.. mpg-covered: literal-projection:docs/src/chapters/case-studies/c-bin-packing.tex.in:496:bin packing branching:choice function
.. mpg-covered: literal-projection:docs/src/chapters/case-studies/c-bin-packing.tex.in:506:bin packing branching:initialize free space in bins
.. mpg-covered: literal-projection:docs/src/chapters/case-studies/c-bin-packing.tex.in:515:bin packing branching:initialize bins with same slack
.. mpg-covered: literal-projection:docs/src/chapters/case-studies/c-bin-packing.tex.in:527:bin packing branching:find best fit
.. mpg-covered: literal-projection:docs/src/chapters/case-studies/c-bin-packing.tex.in:546:bin packing branching:create choice
.. mpg-covered: caption:docs/src/chapters/case-studies/c-bin-packing.tex.in:548:fig:c:bpp:choice
.. mpg-covered: literal-projection:docs/src/chapters/case-studies/c-bin-packing.tex.in:549:bin packing branching:CDBF choice
.. mpg-covered: literal-projection:docs/src/chapters/case-studies/c-bin-packing.tex.in:566:bin packing branching:commit function
.. mpg-covered: literal-projection:docs/src/chapters/case-studies/c-bin-packing.tex.in:571:bin packing branching:commit to first alternative
.. mpg-covered: literal-projection:docs/src/chapters/case-studies/c-bin-packing.tex.in:576:bin packing branching:commit to second alternative
