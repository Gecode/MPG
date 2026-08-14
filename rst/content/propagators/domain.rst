.. _chap:p:domain:

Domain propagation
==================

The propagators in previous chapters use simple modification operations on variable views in that only a single integer defines how a view’s domain is changed. When programming propagators that perform more elaborate domain reasoning, these modification operations are typically insufficient as they easily lead to incorrect and inefficient propagators.

To conveniently program efficient propagators that perform domain reasoning, Gecode offers modification operations that take entire sets of integers as arguments. To be efficient, these sets are not implemented as a typical set data structure but as *iterators*: the integers (or entire ranges of integers) can be iterated in increasing order (smallest first).

.. _propagators:domain:overview:

.. mpg-paragraph:: Overview.

This chapters motivates why special domain operations on variable views are needed (:ref:`sec:p:domain:crash`) and demonstrates how iterators are used for domain propagation (:ref:`sec:p:domain:iter` and :ref:`sec:p:domain:iterators`). :ref:`sec:p:domain:med` and :ref:`sec:p:domain:staging` describe modification event deltas and staging for efficiently combining bounds with domain propagation.

.. _sec:p:domain:crash:

Why domain operations are needed
--------------------------------

.. mpg-covered: caption:docs/src/chapters/programming/p-domain.tex.in:34:fig:p:domain:incorrect

.. mpg-covered: figure:docs/src/chapters/programming/p-domain.tex.in:34:fig:p:domain:incorrect

.. mpg-covered: literal-projection:docs/src/chapters/programming/p-domain.tex.in:35:incorrect domain equal

.. mpg-code:: incorrect domain equal
   :caption: An incorrect propagator for domain equal
   :name: fig:p:domain:incorrect

Let us consider an attempt to implement domain propagation for an equality constraint on views ``x0`` and ``x1``. The idea for pruning is simple: only keep those values of ``x0`` and ``x1`` that are common to the domains of both ``x0`` and ``x1``. This leads to a first version of a domain equality propagator as shown in :numref:`fig:p:domain:incorrect`. Beware, the “propagator” is not only naive but also incorrect: it will crash Gecode!

The propagator uses iterators of type ``Int::ViewValues`` to iterate over the values of an integer view in increasing order (the template argument defines the type of the view to iterate on). The increment operator ``++`` moves the iterator to the next value, the application operator ``()`` tests whether the iterator has more values to iterate, and the function ``val()`` returns the iterator’s current value. The reason why the propagator will crash is simple: it uses the iterator ``i`` for iterating over the values of ``x0`` and modifies the domain of ``x0`` while iterating! This is illegal: when using an iterator for a view, the view cannot be modified (or, in C++ lingua: modifying the variable invalidates the iterator).

One idea how to fix this problem is to use a temporary data structure in which the newly computed intersection domain is stored. That is not very tempting: allocating and initializing an intermediate data structure is costly.

But even then, the approach is flawed from the beginning: a single ``nq()`` operation on a view has linear runtime in the size of the view’s domain (actually, in the length of its range sequence, see below). As potentially a linear number of ``nq()`` operations are executed, the propagator will have quadratic complexity even though it should have linear (as the values of the domains are available in strictly increasing order).

.. _sec:p:domain:iter:

Iterator-based modification operations
--------------------------------------

.. mpg-covered: caption:docs/src/chapters/programming/p-domain.tex.in:79:fig:p:domain:naive

.. mpg-covered: figure:docs/src/chapters/programming/p-domain.tex.in:79:fig:p:domain:naive

.. mpg-covered: literal-projection:docs/src/chapters/programming/p-domain.tex.in:80:naive domain equal

.. mpg-code:: naive domain equal
   :caption: A naive propagator for domain equal
   :name: fig:p:domain:naive
   :download:

:numref:`fig:p:domain:naive` shows a working, yet still naive, implementation of an equality propagator performing domain reasoning. Note that the ``cost()`` function is overridden: even though the propagator is binary, it now incurs a higher cost due to the domain operations to be performed. The ``propagate()`` function uses two *range iterators* for iterating over the range sequence of the domains of ``x0`` and ``x1``. For the definition of a range sequence, see :ref:`sec:m:int:iter`.

A *range iterator* for a range sequence :math:`s=\left\langle [n_i..m_i]\right\rangle_{i=0}^{k}` is an object that provides iteration over :math:`s`: each of the :math:`\left[m_i\;..\;n_i\right]` can be obtained in sequential order but only one at a time. A range iterator provides the following operations: the application operator ``()`` tests whether there are more ranges to iterate, the increment operator ``++`` moves to the next range, the function ``min()`` (``max()``) returns the smallest (largest) value of the current range, and the function ``width()`` returns the *width* of the current range (that is, its number of elements) as an unsigned integer.

The motivation to iterate over range sequences rather than individual values is efficiency: as there are typically less ranges than indvidual values, iteration over ranges can be more efficient. Moreover, many operations are sufficiently easy to express in terms of ranges rather than values (see :ref:`sec:p:domain:iterators` for an example).

.. _propagators:domain:iterator-based-modification-operations:

.. mpg-paragraph:: Iterator-based modification operations.

The propagator uses two modification operations for range iterators: ``x1.inter_r()`` intersects the current domain of ``x1`` with the set defined by the range iterator ``r0`` for ``x0``. After this operation (provided no failure occurred), the view ``x1`` has the correct domain: the intersection of the domains of ``x0`` and ``x1``. The operation ``x0.narrow_r()`` replaces the current domain of ``x0`` by the set defined by the range iterator ``r1`` (which iterates the intersection of the domains of ``x0`` and ``x1``).

A third operation available for range iterators is ``minus_r()`` which removes the values as described by the range iterator passed as argument.

Instead of using range iterators for modification operations, one can also use value iterators instead. Similarly, a view provides operations ``inter_v()``, ``narrow_v()``, and ``minus_v()`` for intersecting, replacing, and removing values.

.. mpg-covered: tip:docs/src/chapters/programming/p-domain.tex.in:132:unlabeled-tip@docs/src/chapters/programming/p-domain.tex.in:132

.. mpg-tip:: Narrow is dangerous

   The ``narrow_r()`` operation used in the above example is dangerous (as is the ``narrow_v()`` operation). As discussed in :ref:`sec:p:started:obligations`, a propagator must be contracting: the domain of a view is only allowed to get smaller. If ``narrow_r()`` is used incorrectly, then one could actually replace the view’s domain by a larger domain.

   In the above example, the propagator is contracting: ``r1`` refers to the intersection of ``x0`` and ``x1``, which of course has no more values than ``x0``.

.. mpg-covered: tip:docs/src/chapters/programming/p-domain.tex.in:143:unlabeled-tip@docs/src/chapters/programming/p-domain.tex.in:143

.. mpg-tip:: Iterators must be increasing

   The range sequence iterated by a range iterator *must* be sorted in increasing order and *must* not overlap as described above. Otherwise, domain operations using range iterators become incorrect.

   For value iterators, the values must be increasing in value with iteration. But it is okay if the same value is iterated over multiply. That is, the values must be increasing but not necessarily strictly increasing.

.. _propagators:domain:avoiding-shared-iterators:

.. mpg-paragraph:: Avoiding shared iterators.

The problem that made our attempt to implement propagation for equality in :ref:`sec:p:domain:crash` incorrect is to use iterators for iterating over views that are simultaneously modified.

Iterator-based modification operations automatically take care of potential sharing between the iterator they use and the view domain they update. By default, an iterator-based modification operation assumes that iterator and domain are shared. The operation first constructs a new domain and iterates to the end of the iterator. Only then the old domain is replaced by the newly constructed domain. In many cases, however, there is no sharing between iterator and domain and the operations could be performed more efficiently by in-place update operations on the domain.

.. mpg-covered: caption:docs/src/chapters/programming/p-domain.tex.in:171:fig:p:domain:nonshared

.. mpg-covered: figure:docs/src/chapters/programming/p-domain.tex.in:171:fig:p:domain:nonshared

.. mpg-covered: literal-projection:docs/src/chapters/programming/p-domain.tex.in:172:non-shared domain equal

.. mpg-code:: non-shared domain equal
   :caption: A propagator for domain equal without sharing
   :name: fig:p:domain:nonshared
   :download:

In our example, there is no sharing if the views ``x0`` and ``x1`` do not refer to the very same variable implementation. If they do, the propagator should not even be posted as it is subsumed anyway (views of the same type referring to the same variable implementation are trivially equal). :numref:`fig:p:domain:nonshared` shows the propagator post function of an improved propagator for equality: the propagator is posted only if ``x0`` and ``x1`` do not refer to the same variable implementation. The ``propagate()`` function is improved by giving an additional ``false`` argument to both ``inter_r()`` and ``narrow_r()``. Hence, the two operations use more efficient operations performing in-place updates on domains.

.. _sec:p:domain:iterators:

Taking advantage of iterators
-----------------------------

This section shows how the combination of simple iterators can help in implementing domain propagation.

Suppose that we want to implement a close variant of the equality constraint, namely :math:`x=y+c` for integer variables :math:`x` and :math:`y` and some integer value :math:`c`. It is easy to see that the new domain for :math:`x` must be all values of :math:`x` intersected with the values :math:`\{n+c\mid n\in y\}`. Likewise, the new domain for :math:`y` must be all values of :math:`y` intersected with the values :math:`\{n-c\mid n\in x\}`. But how can we implement these simple propagation rules?

.. _propagators:domain:mapping-range-sequences:

.. mpg-paragraph:: Mapping range sequences.

Assume a range sequence :math:`\left\langle \left[m_i\;..\;n_i\right]\right\rangle_{i=0}^{k}` for the values in the domain of :math:`y`. Then, what we want to compute is a range sequence

.. math:: \left\langle \left[m_i+c\;..\;n_i+c\right]\right\rangle_{i=0}^{k}.

\ With other words, we want to map the first into the second range sequence. Luckily, this is easy. Suppose that ``r`` is a range iterator for the view ``y``. A range iterator for our desired range sequence can be constructed using the ``Iter::Range::Map`` iterator and an object that describes how to map the ranges of ``r`` to the desired ranges.

For this, we define the following class:

.. mpg-covered: literal-projection:docs/src/chapters/programming/p-domain.tex.in:219:domain equal with offset:offset map

.. mpg-code:: domain equal with offset:offset map

``OffsetMap`` defines to which values the minimum (``min()``) and the maximum (``max()``) of each input range must be mapped. Using ``OffsetMap``, we can construct a range iterator ``m`` for our desired sequence by

.. mpg-code:: snippet:p-domain:sec:p:domain:iterators:code:1
   :direct:

.. mpg-covered: caption:docs/src/chapters/programming/p-domain.tex.in:231:fig:p:domain:offset

.. mpg-covered: figure:docs/src/chapters/programming/p-domain.tex.in:231:fig:p:domain:offset

.. mpg-covered: literal-projection:docs/src/chapters/programming/p-domain.tex.in:232:domain equal with offset

.. mpg-code:: domain equal with offset
   :caption: A propagator for domain equal with offset
   :name: fig:p:domain:offset
   :download:

With the help of the map range iterator, propagation for ``OffsetEqual`` as shown in :numref:`fig:p:domain:offset` is straightforward. Note that several functions need to be modified to deal with the additional integer constant ``c`` used by the propagator (the details can be inspected by downloading the full program code). Further note that the constraint post function is slightly to liberal in that it does not check whether the values with the integer constant ``c`` added exceed the limits for legal integer values.

While the propagator is reasonably easy to construct using map iterators, :ref:`sec:p:views:int:offset` shows how to obtain exactly the same propagator without any programming effort but the implementation of an additional constraint post function.

.. _propagators:domain:using-and-defining-iterators:

.. mpg-paragraph:: Using and defining iterators.

Gecode comes with a multitude of range and value iterators to transform range and value sequences of other iterators. These iterators are defined in the namespace ``Iter``. Range iterators are defined in the namespace ``Iter::Ranges``\ and value iterators in the namespace ``Iter::Values``. Example iterators include: iterators to convert value into range iterators and vice versa, iterators to compute the union and intersection, iterators to iterate over arrays and bitsets, just to name a few.

But even if the predefined iterators are not sufficient, it is straightforward to implement new iterators: the only requirement is that they implement the appropriate interface mentioned above for range or value iterators. The namespace ``Iter``\ contains a multitude of simple and advanced examples.

.. _propagators:domain:benefits-of-iterators:

.. mpg-paragraph:: Benefits of iterators.

The true benefit of using iterators for performing value or range transformations is that the iterator-based domain modification operation with which an iterator is used is automatically specialized at compile time. Typically, no intermediate data structures are created and the modification operations are optimized at compile time for each individual iterator. [1]_

A scenario where this in particular matters is when iterators are used as *adaptors* of a propagator-specific data structure. Assume that a propagator uses a specific (typically, quite involved) data structure to perform propagation. Most often this data structure encodes in some form which views should take which values. Then, one can implement simple iterators that inspect the propagator-specific data structure and provide the information about values for views so that they can be used directly with iterator-based modification operations. Again, intermediate data structures are avoided by this approach.

.. _sec:p:domain:med:

Modification event deltas
-------------------------

There is a rather obvious approach to improving the efficiency of domain operations performed by propagators: make the domains as small as possible! One typical approach to reduce the size of the domains is to perform bounds propagation first. After bounds propagation, the domains are likely to be smaller and hence the domain operations are likely to be more efficient.

For propagating equality, the simplest idea is to first perform bounds propagation for equality as discussed in :ref:`sec:p:avoid:eqbnd`, directly followed by domain propagation. However, we can improve further by exploiting an additional token of information about the views of a propagator that is supplied to both the ``cost()`` and ``propagate()`` function of a propagator.

The ``cost()`` and ``propagate()`` functions of a propagator take an additional *modification event delta* value of type ``ModEventDelta`` (see ``TaskActor``) as argument. Every propagator maintains a modification event delta that describes how its views have changed since the last time the propagator has been executed. For each view type (that is, integer, Boolean, set, :math:`\ldots`) a modification event delta stores a modification event that can be extracted from the modification event delta: If ``med`` is a modification event delta, then ``Int::IntView::me(med)`` returns the modification event for integer views.

The extracted modification event describes how all views of a certain view type have changed. For example, for integer views, the modification event ``Int::ME_INT_VAL`` signals that there is at least one integer view that has been assigned since the propagator has been executed last (analogous for ``Int::ME_INT_BND`` and ``Int::ME_INT_DOM``). Even the modification event ``Int::ME_INT_NONE`` carries some information: none of the propagator’s integer views have been modified (which, of course, can only happen if the propagator also uses views of some other type).

.. mpg-covered: caption:docs/src/chapters/programming/p-domain.tex.in:340:fig:p:domain:bounds

.. mpg-covered: figure:docs/src/chapters/programming/p-domain.tex.in:340:fig:p:domain:bounds

.. mpg-covered: literal-projection:docs/src/chapters/programming/p-domain.tex.in:341:domain equal using bounds propagation

.. mpg-code:: domain equal using bounds propagation
   :caption: A propagator for domain equal using bounds propagation
   :name: fig:p:domain:bounds
   :download:

:numref:`fig:p:domain:bounds` shows a propagator that combines both bounds and domain propagation for propagating equality. It first extracts the modification event for integer views from the modification event delta ``med``. Only if the bounds (that is, modification events ``Int::ME_INT_VAL`` or ``Int::ME_INT_BND``, hence different from ``Int::ME_INT_DOM``) have changed for at least one of the views ``x0`` and ``x1``, the propagator performs bounds propagation.

After performing bounds propagation, the propagator checks whether it is subsumed. Then it does some more fixpoint reasoning: if the domains of ``x0`` and ``x1`` are ranges (that is, they do not have holes), the propagator is at fixpoint. Otherwise, domain propagation is done as shown before.

.. _sec:p:domain:staging:

Staging
-------

Taking the perspective of a single propagator, first performing bounds propagation directly followed by domain propagation seems to be appropriate. However, when taking into account that some other cheap propagators (at least cheaper than performing domain propagation by this propagator) might already be able to take advantage of the results of bounds propagation, it might actually be better to postpone domain propagation and give cheaper propagators the opportunity to execute. This idea is known as *staging* and has been introduced in Gecode :cite:p:`SchulteStuckey:TOPLAS:2008`. Note that staging is not limited to bounds and domain propagation but captures any stages in propagation that differ in cost.

Here, we focus on staging for first performing bounds propagation (stage “bounds”) and then domain propagation (stage “domain”) for equality. Additionally, a propagator can be idle (stage “idle”). The stage of a propagator is controlled by how its modification event delta changes:

- Initially, the propagator is idle, its modification event delta is empty, and the propagator is in stage “idle”.

- When the modification event delta for integer views changes to ``Int::ME_INT_DOM`` and the propagator is in stage “idle”, the propagator is put into stage “domain” with high propagation cost.

- When the modification event delta for integer views changes to ``Int::ME_INT_VAL`` or ``Int::ME_INT_BND``, the propagator is put into stage “bounds” with low propagation cost.

  Note that this in particular includes the case where the modification event delta for integer views has been ``Int::ME_INT_DOM`` and where the propagator had already been in stage “domain”. As soon as the modification event delta changes to ``Int::ME_INT_BND`` or ``Int::ME_INT_VAL`` the propagator is put into stage “bounds”.

By the very construction of modification event deltas, the modification event delta for integer views can neither change from ``Int::ME_INT_VAL`` to ``Int::ME_INT_BND`` nor from ``Int::ME_INT_BND`` (or ``Int::ME_INT_VAL``) to ``Int::ME_INT_DOM``. That is, if the equality propagator using staging is in stage “bounds” it stays in that stage until it is executed.

.. mpg-covered: caption:docs/src/chapters/programming/p-domain.tex.in:409:fig:p:domain:transitions

.. mpg-covered: figure:docs/src/chapters/programming/p-domain.tex.in:409:fig:p:domain:transitions

.. mpg-covered: table:docs/src/chapters/programming/p-domain.tex.in:413:tabular@docs/src/chapters/programming/p-domain.tex.in:413

.. mpg-figure:: Stage transitions for the equality propagator
   :name: fig:p:domain:transitions
   :class: mpg-figure-medium

   .. only:: html

      .. image:: /figures/fig-p-domain-transitions.svg
         :alt: Stage transitions for the equality propagator

   .. only:: latex

      .. image:: /figures/pdf/fig-p-domain-transitions.pdf
         :alt: Stage transitions for the equality propagator

When the propagator is executed, it can be either in stage “bounds” or stage “domain”. If it is executed in stage “bounds”, it performs bounds propagation and then returns that it wants to be put into stage “domain”. The essential point is that the propagator does not continue with domain propagation but gives other propagators the opportunity to execute first. If the propagator is executed in stage “domain”, it performs domain propagation and returns that it is at fixpoint (and hence the propagator is put into stage “idle”). :numref:`fig:p:domain:transitions` summarizes the stage transitions, where a blue transition is triggered by a change in the modification event delta (``Int::ME_INT_DOM`` is abbreviated by ``DOM`` and so on) and a green transition is performed be executing the propagator.

.. _propagators:domain:re-scheduling-propagators:

.. mpg-paragraph:: Re-scheduling propagators.

The cost of a propagator depends on its modification event delta. This connection goes even further: only if the modification event delta of a propagator changes, a propagator is re-scheduled according to its cost by recomputing the ``cost()`` function.

Not recomputing cost each time a propagator might be scheduled is done for two reasons. First, the number of possibly expensive cost computations is reduced. Second, always re-scheduling would also violate the fairness among all propagators already scheduled with same cost. If a propagator is scheduled often, it would be penalized as its execution would be deferred.

:ref:`sec:p:advisors:force` discusses a technique to force re-scheduling of a propagator, irrespective of its modification event delta.

.. _propagators:domain:controlling-staging-by-modification-event-deltas:

.. mpg-paragraph:: Controlling staging by modification event deltas.

.. mpg-covered: caption:docs/src/chapters/programming/p-domain.tex.in:466:fig:p:domain:staging

.. mpg-covered: figure:docs/src/chapters/programming/p-domain.tex.in:466:fig:p:domain:staging

.. mpg-covered: literal-projection:docs/src/chapters/programming/p-domain.tex.in:467:domain equal using staging

.. mpg-code:: domain equal using staging
   :caption: A propagator for domain equal using staging
   :name: fig:p:domain:staging
   :download:

The ``cost()`` function and the essential parts of the ``propagate()`` function of a propagator that uses staging to combine bounds and domain propagation for equality are shown in :numref:`fig:p:domain:staging`.

The ``cost()`` function returns the cost based on the modification event delta ``med``: if ``med`` only includes ``Int::ME_INT_DOM``, then the propagator returns that next time it executes, it executes at high-binary cost (according to stage “domain”). Otherwise, the propagator returns that next time it executes, it executes at low-binary cost (according to stage “bounds”).

The ``propagate()`` function is almost identical to the function shown in the previous section. The only difference is that ``propagate()`` returns after having performed bounds propagation. The call to ``ES_FIX_PARTIAL()`` specifies that the current propagator ``*this`` has computed a partial fixpoint for all modification events but ``Int::ME_INT_DOM``. The function ``Int::IntView::med`` creates a modification event delta from a modification event for integer views. As an effect, the modification event delta of the current propagator is set to include nothing but ``Int::ME_INT_DOM`` and the propagator is scheduled: as defined by the ``cost()`` function, the propagator is scheduled for high binary cost. That means that other propagators of lower cost might be executed first.

.. _propagators:domain:constructing-modification-event-deltas:

.. mpg-paragraph:: Constructing modification event deltas.

Every view type provides a static ``med()`` function that translates a modification event of that view type into a modification event delta. Modification event deltas for different view types can be combined with the ``|`` operator. For example, the following expression combines the modification event ``ME_INT_BND`` for integer views with the modification event ``ME_BOOL_VAL`` for Boolean views:

.. mpg-code:: snippet:p-domain:fig:p:domain:staging:code:1
   :direct:

Note that only modification event deltas for different view types can be combined using ``|``.

.. [1]
   Some predefined iterators actually have to resort to intermediate data structures. For example, iterators that need to revert the order of its values or ranges (think of a value iterator for values that are the negation of values of some other value iterator).
