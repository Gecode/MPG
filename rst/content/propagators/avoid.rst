.. _chap:p:avoid:

Avoiding execution
==================

This chapter serves two purposes. First, it discusses techniques for avoiding propagator execution. Second, the examples used in this chapter introduce view arrays for propagators and Boolean views.

.. _propagators:avoid:overview:

.. mpg-paragraph:: Overview.

Fixpoint reasoning as an important technique for avoiding propagator execution is discussed in detail in :ref:`sec:p:avoid:eqbnd` (we already briefly touched on this subject in :ref:`sec:p:started:better`). The following section (:ref:`sec:p:avoid:ortrue`) presents an example propagator for Boolean disjunction introducing Boolean variable views and view arrays for propagators with arbitrarily many views. The Boolean disjunction propagator is used in :ref:`sec:p:avoid:dynamic` as an example for dynamic subscriptions (a propagator only subscribes to a subset of its views and the subscriptions change while the propagator is being executed) as another technique to avoid propagator execution.

.. _sec:p:avoid:eqbnd:

Fixpoint reasoning reconsidered
-------------------------------

In this section, we develop a propagator for equality :math:`x=y` that performs bounds reasoning to further discuss how a propagator can do fixpoint reasoning. A stronger domain propagator for equality is discussed in :ref:`chap:p:domain`. Background information on fixpoint reasoning can be found in :cite:p:`SchulteStuckey:TOPLAS:2008`.

.. _propagators:avoid:a-naive-propagator:

.. mpg-paragraph:: A naive propagator.




.. mpg-code:: equal naive
   :caption: A naive equality bounds propagator
   :name: fig:p:avoid:equal:naive
   :download:

The ``propagate()`` member function of an equality propagator ``Equal`` is shown in :numref:`fig:p:avoid:equal:naive`. The remaining functions are as to be expected.

The propagation rules implemented by ``Equal`` is that the values of both ``x0`` and ``x1`` must be greater or equal than ``std::max(x0.min(),x1.min())`` and less or equal than ``std::min(x0.max(),x1.max())``. The above implementation follows these rules even though it avoids the computation of ``std::min`` and ``std::max``. Let us look to the adjustment of the lower bounds of ``x0`` and ``x1`` (the upper bounds are analogous):

- If ``x0.min()==x1.min()``, nothing is pruned.

- If ``x0.min()<x1.min()``, then ``x0`` is pruned.

- If ``x0.min()>x1.min()``, then ``x1`` is pruned.

As can be seen, the propagator does not perform any fixpoint reasoning, it always returns ``ES_NOFIX`` (unless it is subsumed or failed).

The propagator might actually sometimes compute a fixpoint and sometimes not. Consider :math:`\mathtt{x0}\in\{1,2,3,4\}` and :math:`\mathtt{x1}\in\{0,1,2,5\}`. Then ``Equal`` propagates that :math:`\mathtt{x0}\in\{1,2,3,4\}` and :math:`\mathtt{x1}\in\{1,2\}` which happens to be not a fixpoint. The reason (which is common when performing bounds propagation) is that a bounds modification (here ``x1.lq(home,4)``) has resulted in an even smaller upper bound (or an even larger lower bound when the lower bound is modified). In a way, the modification operation updating the bound fell into a hole in the variable domain.

.. _propagators:avoid:reporting-fixpoints:

.. mpg-paragraph:: Reporting fixpoints.




.. mpg-code:: equal
   :caption: An equality bounds propagator with fixpoint reasoning
   :name: fig:p:avoid:equal
   :download:

The above example shows that the equality propagator computes a fixpoint if and only if, after propagation, ``x0.min()==x1.min()`` and ``x0.max()==x1.max()``. :numref:`fig:p:avoid:equal` shows the ``propagate()`` member function of an improved ``Equal`` propagator that takes advantage of fixpoint reasoning.

.. _propagators:avoid:an-idempotent-propagator:

.. mpg-paragraph:: An idempotent propagator.




.. mpg-code:: equal idempotent
   :caption: An idempotent equality bounds propagator
   :name: fig:p:avoid:equal:idempotent
   :download:

The previous propagator reports when it computes a fixpoint. However, we can change any propagator so that it always computes a fixpoint. Propagators which always compute a fixpoint (unless they are subsumed) are known as *idempotent* propagators. The idea to turn an arbitrary propagator into an idempotent propagator is simple: repeat propagation until it has computed a fixpoint. :numref:`fig:p:avoid:equal:idempotent` shows the ``propagate()`` member function of an idempotent equality propagator.

The idempotent propagator always computes a fixpoint. That means that it does not need to use the generic mechanisms provided by the Gecode kernel for scheduling and executing propagators in order to compute a fixpoint. Instead, a tight inner loop inside the ``propagate()`` function computes the fixpoint. If the propagator is cheap (which it is in our example) it might be better to make the propagator idempotent and hence avoid the overhead of the Gecode kernel (even though the Gecode kernel is very efficient as it comes to scheduling and executing propagators).

.. _propagators:avoid:an-idempotent-propagator-using-modification-events:

.. mpg-paragraph:: An idempotent propagator using modification events.




.. mpg-code:: equal idempotent using modification events
   :caption: An idempotent equality bounds propagator using modification events
   :name: fig:p:avoid:equal:modevent
   :download:

The idempotent propagator shown above tests a propagator-specific criterion to determine whether a fixpoint has been computed. With the help of modification events there is a generic approach to computing a fixpoint within the ``propagate()`` member function of a propagator. :numref:`fig:p:avoid:equal:modevent` shows the ``propagate()`` member function where the Boolean variable ``nafp`` (for: ``n``\ ot ``a``\ t ``f``\ ix\ ``p``\ oint) tracks whether the propagator has computed a fixpoint. The function ``me_modified(me)`` checks whether the modification event ``me`` does not signal failure or that the view did change (that is, for integer views, ``me`` is different from ``Int::ME_INT_FAILED`` and ``Int::ME_INT_NONE``). Whenever a view is modified, ``nafp`` is accordingly set to ``true``. The remaining modification operations are omitted as they are analogous.


.. mpg-tip:: Understanding ``ES_NOFIX``

   The above technique for making a propagator idempotent is based on the idea of repeating propagation until no more views are modified.

   Unfortunately, we have seen (more than once) a similar but not very good idea in propagators for finding out whether a propagator is at fixpoint. The idea can be sketched as follows: record in a Boolean flag ``modified`` whether a modification operation actually modified a view during propagation. For our bounds equality propagator the idea can be sketched as follows:

   .. mpg-code:: snippet:p-avoid:fig:p:avoid:equal:modevent:code:1
      :direct:

   That means, if ``modified`` is ``true`` the propagator might not be at fixpoint and hence ``ES_NOFIX`` is returned. This makes not much sense: ``ES_NOFIX`` means *that a propagator is not considered to be at fixpoint if it has modified a view!* If no view has been modified the propagator must be at fixpoint and just returning ``ES_NOFIX`` does the trick.

   This not-so-hot idea can be summarized as: achieving nothing with quite some effort!

For the equality constraint, checking the propagator-specific fixpoint condition is simple enough. For more involved propagators, the generic approach using modification events always works and is to be preferred. As the generic approach is so useful, a macro ``GECODE_ME_CHECK_MODIFIED`` is available. With this macro, the loop insided the ``propagate()`` function can be expressed as:

.. mpg-code:: snippet:p-avoid:fig:p:avoid:equal:modevent:code:2
   :direct:

.. _sec:p:avoid:ortrue:

A Boolean disjunction propagator
--------------------------------

Before we demonstrate dynamic subscriptions in the next section, we discuss a propagator for Boolean disjunction. The propagator is rather simple, but we use it as an example for Boolean views, arrays of views, and several other aspects.




.. mpg-code:: or true
   :caption: Naive Boolean disjunction
   :name: fig:p:avoid:or:naive
   :download:

:numref:`fig:p:avoid:or:naive` shows the ``OrTrue`` propagator that propagates that an array of Boolean views ``x`` is ``1`` (that is, the Boolean disjunction on ``x`` is true). That is, at least one of the views in ``x`` must be ``1``. The propagator uses an array :api:`ViewArray` of Boolean views (a :api:`ViewArray` is generic with respect to the views it stores). Similar to views, view arrays have ``subscribe()`` and ``cancel()`` functions for subscriptions, where the operations are applied to all views in the view array.


.. mpg-tip:: View arrays also provide STL-style iterators

   View arrays also support STL-style (Standard Template Library) iterators, similar to other arrays provided by Gecode, see :ref:`sec:m:integer:stl`.

.. _propagators:avoid:constraint-post-function:

.. mpg-paragraph:: Constraint post function.

The constraint post function ``dis()`` constrains the disjunction of the Boolean variables in ``x`` to be equal to the integer ``n``:

.. math:: \bigvee_{i=0}^{|\mathtt{x}|-1} \mathtt{x}_i=\mathtt{n}

The constraint post function checks that the value for ``n`` is legal. If ``n`` is neither ``0`` nor ``1``, the constraint post function throws an exception. Here, we use an appropriate Gecode-defined exception, but any exception of course works.

If ``n`` is ``0``, all variables in ``x`` must be ``0`` as well: rather than posting a propagator to do that, we assign the views immediately in the constraint post function. Note that we have to get an integer view to be able to assign ``x[i]`` to zero as only views provide modification operations.

Otherwise, a view array ``y`` is created (newly allocated in the space ``home``) and its fields are initialized to views that correspond to the respective integer variables in ``x``. Then, posting the ``OrTrue`` propagator is as expected.

A more general case of Boolean disjunction, where ``n`` is an integer variable instead of an integer value is discussed in :ref:`sec:p:advisors:or`.

.. _propagators:avoid:propagation:

.. mpg-paragraph:: Propagation.




.. mpg-code:: or true:propagation
   :caption: Propagation for naive Boolean disjunction
   :name: fig:p:avoid:ortrue:prop

Propagation for Boolean disjunction is straightforward: first, all views are inspected whether they are assigned to ``1`` (in which case the propagator is subsumed) or to ``0`` (in which case the assigned view is eliminated from the view array). If no views remain, the propagator is failed. If a single (by elimination, an unassigned view) remains, it is assigned to ``1``. This can be implemented as shown in :numref:`fig:p:avoid:ortrue:prop`.

The operation ``x.move_lst(i)`` of a view array ``x`` moves the last element of ``x`` to position ``i`` and shrinks the array by one element. Shrinking from the end is in particular simple if the array elements are iterated backwards as in our example. The class :api:`ViewArray` provides several operations to shrink view arrays. Note that ``x.move_lst(i)`` requires that the view at position ``i`` is actually assigned or has no subscription, otherwise the subscription for ``x[i]`` needs to be canceled before ``x[i]`` is overwritten. View arrays also provide operations for simultaneously moving elements and canceling subscriptions.


.. mpg-tip:: View arrays have non-copying copy constructors

   The constructor for posting in :numref:`fig:p:avoid:or:naive` uses the copy constructor of :api:`ViewArray` to initialize the member ``x``. The copy constructor does *not* copy a view array. Instead, after its execution both original and copy have shared access to the same views.

.. _propagators:avoid:using-propagator-patterns:

.. mpg-paragraph:: Using propagator patterns.




.. mpg-code:: or true concise
   :caption: Naive Boolean disjunction using a propagator pattern
   :name: fig:p:avoid:or:concise
   :download:

How to use a propagator pattern with an array of views is shown in :numref:`fig:p:avoid:or:concise` for Boolean disjunction.

.. _propagators:avoid:boolean-views:

.. mpg-paragraph:: Boolean views.

A Boolean view :api:`Int::BoolView` provides operations for testing whether it is assigned to ``1`` (``one()``) or ``0`` (``zero()``), or whether it is not assigned yet (``none()``). As modification operations Boolean views offer ``one(home)`` and ``zero(home)``. Also, Boolean views only support ``PC_BOOL_NONE`` and ``PC_BOOL_VAL`` as propagation conditions and ``ME_BOOL_NONE``, ``ME_BOOL_FAILED``, and ``ME_BOOL_VAL`` as modification events.

Boolean views (variables and variable implementations likewise) are not related to integer views by design: the very point is that Boolean variable implementations have a specially optimized implementation that is in fact not related to the implementation of integer variables.

Boolean views also implement all operations that integer views implement and integer propagation conditions can also be used with Boolean views. ``PC_INT_DOM``, ``PC_INT_BND``, and ``PC_INT_VAL`` are mapped to the single Boolean propagation condition ``PC_BOOL_VAL``. Having the same interface for integer and Boolean views is essential: :ref:`sec:p:views:inttobool` shows how integer propagators can be reused as Boolean propagators without requiring any modification.

.. _sec:p:avoid:dynamic:

Dynamic subscriptions
---------------------

The previous section has been nothing but a warm-up to the presentation of dynamic subscriptions as another technique to avoid propagator execution.

.. _propagators:avoid:watched-literals:

.. mpg-paragraph:: Watched literals.

The naive propagator presented above is disastrous: every time the propagator is executed, it checks all of its views to determine whether a view has been assigned to ``0`` or ``1``. Worse yet, pretty much all of the propagator executions are entirely pointless for propagation (but not for determining subsumption as is discussed below).

One idea would be to only check until two unassigned views have been encountered. In this case, it is clear that the propagator cannot perform any propagation. Of course, this might prevent the propagator from detecting subsumption as early as possible: as it does not scan all views but stops scanning after two unassigned views, it might miss out on a view already assigned to ``1``.

The idea to stop scanning after two unassigned views have been encountered can be taken even further. A well-known technique for the efficient implementation of Boolean SAT (satisfiability) solvers are *watched literals* :cite:p:`chaff`: it is sufficient to subscribe to two Boolean views for propagating a Boolean disjunction to be satisfied. Subscribing to a single Boolean view is not enough: if all views but the subscription view are assigned to ``0`` the subscription view must be assigned to ``1`` to perform propagation, however the propagator will not be scheduled as the single subscription view is not assigned. More than two subscriptions are not needed for propagation, as the propagator can only propagate if a single unassigned view remains. It might be the case that a view to which the propagator has not subscribed is assigned to ``1``. That means that the propagator is not subsumed as early as possible but that does not affect propagation.




.. mpg-code:: or true with dynamic subscriptions
   :caption: Boolean disjunction with dynamic subscriptions
   :name: fig:p:avoid:or:dynamic
   :download:

.. _propagators:avoid:the-propagator:

.. mpg-paragraph:: The propagator.

The propagator using dynamic subscriptions maintains exactly two subscriptions to its Boolean views. :numref:`fig:p:avoid:or:dynamic` shows the ``OrTrue`` propagator with dynamic subscriptions. It inherits from the ``BinaryPropagator`` pattern and the views ``x0`` and ``x1`` of the pattern are exactly the two views with subscriptions. All remaining views without subscriptions are stored in the view array ``x``. The operation ``drop_fst(n)`` for an integer ``n`` drops the first ``n`` elements of a view array and shortens the array by ``n`` elements accordingly (that is, ``drop_fst()`` is dual to ``drop_lst()`` as used in the previous section). Note that the propagator must define a ``dispose()`` member function: this is needed not because ``dispose()`` must cancel additional subscriptions (the very point is that ``x`` has no subscriptions) but that it must return the correct size of ``OrTrue``.


.. mpg-tip:: ``drop_fst()`` and ``drop_lst()`` are efficient

   Due to the very special memory allocation policy used for view arrays (their memory is allocated in a space and is never freed as they only can shrink, see :ref:`chap:p:memory`), both ``drop_fst()`` and ``drop_lst()`` have constant time complexity.


.. _propagators:avoid:dynamic-subscriptions-propagation:

.. mpg-paragraph:: Propagation.

The idea of how to perform propagation is fairly simple: if one of the views with subscriptions is assigned to ``1``, the propagator is subsumed. If one of the subscription views is assigned to ``0``, say ``x0``, a function ``resubscribe()`` tries to find a yet unassigned view to subscribe to it and store it as ``x0``. If there is no such view but there is a view assigned to ``1``, the propagator is subsumed. If there is no such view, then the propagator tries to assign ``1`` to ``x1``, and, if successful, the propagator is also subsumed. The implementation is as follows:


.. mpg-code:: or true with dynamic subscriptions:propagation

.. _propagators:avoid:resubscribing:

.. mpg-paragraph:: Resubscribing.




.. mpg-code:: or true with dynamic subscriptions:resubscribe
   :caption: Resubscribing for Boolean disjunction with dynamic subscriptions
   :name: fig:p:avoid:ortrue:re

The function ``resubscribe()`` implements the search for a yet unassigned view for subscription and is shown in :numref:`fig:p:avoid:ortrue:re`.

.. _propagators:avoid:copying:

.. mpg-paragraph:: Copying.

The assigned views in ``x`` do not really matter much: all views assigned to ``0`` can be discarded. If there is a view assigned to ``1`` all other views can be discarded (of course, a single view assigned to ``1`` must be kept for correctness). Hence a good idea for copying is: copy only those views that still matter. This leads to a smaller view array requiring less memory. We decide to discard assigned views as much as we can in the ``copy()`` function rather than in the constructor used for copying. By this, also the original and not only the copy profits from fewer views. While the copy benefits because there are less views to be stored, the original propagator benefits because ``resubscribe()`` does not have to scan assigned views as they already have been eliminated. Following this discussion, the ``copy()`` function can be implemented as:


.. mpg-code:: or true with dynamic subscriptions:copy

There is another optimization during copying that looks promising. If all views in ``x`` are eliminated, a propagator without the view array ``x`` is sufficient as a copy. If there is a view assigned to ``1``, then a propagator should be created that is subsumed. How this can be achieved is discussed in :ref:`sec:p:reified:or`.
