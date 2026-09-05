.. _chap:p:advisors:

Advisors
========

This chapter is concerned with advisors for efficient incremental propagation. Advisors can be used to provide information to a propagator which of its views have changed and how they have changed.

.. _propagators:advisors:overview:

.. mpg-paragraph:: Overview.

In :ref:`sec:p:advisors:advisors`, a motivation and a model for advisors is presented. The following two sections demonstrate advisors. :ref:`sec:p:advisors:samedom` shows an example propagator that exploits the information provided by an advisor about which view has changed. :ref:`sec:p:advisors:or` shows an example propagator that exploits information on how the domain of its views have changed. :ref:`sec:p:advisors:force` sketches how advisors can be used for forcing propagators to be re-scheduled.

.. _sec:p:advisors:advisors:

Advisors for incremental propagation
------------------------------------

Consider the following, rather simple, example constraint. The constraint ``samedom`` for an array of integer variables ``x`` and an integer set ``d`` holds, if and only if:

- either all variables in ``x`` take values from ``d`` (that is, :math:`\mathtt{x}_i\in\mathtt d` for :math:`0\leq i<|\mathtt{x}|`),

- or none of the ``x`` take values in ``d`` (that is, :math:`\mathtt{x}_i\not\in\mathtt d` for :math:`0\leq i<|\mathtt{x}|`).

.. _propagators:advisors:more-knowledge-is-needed:

.. mpg-paragraph:: More knowledge is needed.

Obviously, there are two different approaches to realize ``samedom``:

decomposition
   We decompose the ``samedom`` constraint as follows. We create a Boolean variable :math:`\mathtt{b}` and post reified ``dom`` constraints (see :api:`Domain constraints <TaskModelIntDomain>`) such that :math:`\mathtt{b}=\mathtt{1}\Leftrightarrow \mathtt{x}_i\in\mathtt{d}` (for :math:`0\leq i<|\mathtt{x}|`). As the single Boolean variable ``b`` is the same for all reified ``dom`` constraints, ``samedom`` is automatically enforced.

implementation
   A different approach is to implement a dedicated propagator for ``samedom``. Propagation is quite simple: whenever the propagator is executed, try to find a view among the :math:`\mathtt{x}_i` such that either :math:`\mathtt{x}_i\in\mathtt d` or :math:`\mathtt{x}_i\not\in\mathtt d`. If there is no such :math:`\mathtt{x}_i`, the propagator is at fixpoint. Otherwise, the propagator constrains all :math:`\mathtt{x}_i` accordingly.

Let us compare the individual merits of the two approaches (note that both achieve domain consistency). Decomposition requires :math:`O(|\mathtt x|)` propagators consuming quite some memory. Implementation requires a single propagator only and hence has a lower overhead both for runtime (only a single propagator needs to be scheduled) and memory consumption.

However, the implementation approach is dreadful and is in fact less efficient than decomposition! The problem is the “try to find a view” approach: each time the propagator is executed, it only knows that some of its views have changed since last time the propagator has been executed. It just does not know which views changed! That is, each time the propagator is executed, it needs to scan all its views. For ``samedom``, the propagator takes :math:`O(|\mathtt{x}|\cdot|\mathtt d|)` runtime as scanning needs to inspect the entire domain of each view. This is considerably worse than decomposition: when the domain of a :math:`\mathtt{x}_i` changes, only a single reified propagator for ``dom`` is executed with cost :math:`O(|\mathtt d|)`.

The problem is the little amount of information available to a propagator when it is executed. The propagator only knows that some of its views changed but not which views. Hence, just finding out which views have changed always incurs linear cost in the number of views.

For a simple constraint such as ``samedom``, the linear overhead is prohibitive. For more involved constraints, decomposition might be infeasible as it would compromise propagation (think of domain consistent ``distinct`` as an example).

.. _propagators:advisors:advisors:

.. mpg-paragraph:: Advisors.

Gecode provides *advisors* to inform propagators about view changes. An advisor belongs to a propagator and can be defined (by inheriting from :api:`Advisor`) to store information as needed by its propagator. The sole purpose of an advisor is to subscribe to a view of its propagator: each time the view changes, an ``advise()`` function of the advisor’s propagator is executed with the advisor as argument (sometimes we will be a little sloppy by saying that the advisor is executed itself).

In more detail:

- An advisor must inherit from the class :api:`Advisor`.

- When an advisor is created, it is created with respect to its propagator and a *council* of advisors. Each advisor belongs to a council and a propagator can have at most one council. The sole purpose of a council is to manage its advisors for cloning and disposal. In particular, when the propagator is disposed, the council must be disposed as well.

  A council also provides access to all of its advisors (we will exploit this in the following sections).

- An advisor can subscribe to views (and, hence, an advisor subscription like any other subscription must eventually be canceled). Unlike subscriptions of propagators to views, subscriptions of advisors do not use propagation conditions: an advisor is always executed when its subscription view changes.

  Also, an advisor is never executed when the subscription is created, only when the subscription view changes. This also means that when using advisors, one also needs to think about how the ``reschedule()`` member function of the propagator should look like, after all, this function has the responsibility to re-schedule a propagator when needed.

- An advisor is executed as follows: the ``advise()`` function of its propagator is executed. The function takes the advisor as argument and an additional argument of type :api:`Delta`. The *delta* describes how the domain of the view has changed. Clearly, which kind of information a delta provides depends on the type of the view. Deltas, in particular, provide access to the modification event of the operation that triggered the advisor’s execution.

  For integer and Boolean views, deltas provide some approximate information about which values have been removed. For an example, see :ref:`sec:p:advisors:or`.

- The ``advise()`` function is *not* allowed to perform propagation by executing modification operations on views. It can change the state of the propagator and must return an execution status: ``ES_FAILED`` means that the propagator is failed; ``ES_FIX`` means that the propagator is at fixpoint (hence, it is not scheduled); ``ES_NOFIX`` means that the propagator is not any longer at fixpoint (hence, it is scheduled). That is, an advisor does exactly what its name suggests as it provides advice to its propagator: when should the propagator be executed and the advisor can also provide information for the next propagator execution.

  The ``advise()`` function can also return after calling the functions ``ES_FIX_DISPOSE()`` or ``ES_NOFIX_DISPOSE()`` which are analogous to ``ES_FIX`` and ``ES_NOFIX`` but also dispose the advisor.

  There are two more functions that force the advisor’s propagator to be re-scheduled. They are discussed in :ref:`sec:p:advisors:force`.

- Advisors have a rather subtle interaction with disabling a propagator: as discussed in :ref:`sec:p:started:solving`, a disabled propagator is scheduled as usual but is not allowed to perform any propagation. While advisors are not allowed to prune variable domains, they can report failure by returning ``ES_FAILED``.

  If a propagator is disabled (this can be checked by the member function ``disabled()`` of a propagator), the advisor is *not* allowed to report failure! Instead, the ``reschedule()`` function must make sure that when the propagator is re-enabled and is re-scheduled that its ``propagate()`` function reports failure instead.

  Note, however, that typically advisors of a disabled propagator execute normally and maintain the information necessary for the next execution of the propagator, which just happens to be if the propagator is enabled again and possibly re-scheduled.

Note that a propagator using advisors must make sure that its advisors schedule the propagator when it is not at fixpoint, this applies to when the propagator is posted and when the ``advise()`` or ``reschedule()`` functions are executed. Otherwise, it would not meet its “subscription complete” obligation (make sure to read :numref:`tip:p:advisors:started`). A propagator is free to mix subscriptions using advisors and subscriptions using propagation conditions, see :ref:`sec:p:advisors:or`.

For more information on advisors including design and evaluation, see :cite:p:`LagerkvistSchulte:CP:2007`.

.. _sec:p:advisors:samedom:

The ``samedom`` constraint
--------------------------

The idea how the ``SameDom`` propagator implements the ``samedom`` constraint is straightforward. The propagator creates an advisor for each of its views and as soon as the ``advise()`` function decides for one of the views ``x`` that either

.. math::

   \mathtt{x}\subseteq\mathtt{d}\qquad\text{or}
   \qquad\mathtt{x}\cap\mathtt{d}=\emptyset

\ holds, the propagator is informed what it has to do and is scheduled. Then, the propagator performs the required propagation and becomes subsumed. That is, a ``SameDom`` propagator is executed at most once.

.. _propagators:advisors:todo-information:

.. mpg-paragraph:: Todo information.

.. container:: samepage

   A ``SameDom`` propagator stores in ``todo`` what it has to do when it is executed:


.. mpg-code:: samedom:todo information

Initially, ``todo`` is ``NOTHING``. When the propagator is scheduled on behalf of an advisor ``todo`` is either ``INCLUDE`` (that is, the propagator must propagate that :math:`\mathtt{x}_i\subseteq\mathtt d` for :math:`0\leq i<|\mathtt{x}|`) or ``EXCLUDE`` (that is, the propagator must propagate that :math:`\mathtt{x}_i\cap\mathtt d=\emptyset` for :math:`0\leq i<|\mathtt{x}|`).

.. _propagators:advisors:view-advisors:

.. mpg-paragraph:: View advisors.

Each advisor used by the ``SameDom`` propagator stores the view it is subscribed to. By this, the ``advise()`` function can use the view stored with an advisor to decide what the propagator needs to do. A view advisor is defined as follows:


.. mpg-code:: samedom:advisor

An advisor must implement a constructor for creation which takes the home space, the advisor’s propagator, and the council of advisors as arguments. Additionally, a view advisor also takes the view as input and subscribes to the view.

An advisor does neither have an ``update()`` nor a ``copy()`` function, a constructor for cloning with the typical arguments is sufficient. The ``dispose()`` function of an advisor does not have to report the advisor’s size (in contrast to a propagator’s ``dispose()`` function).

The propagator maintains a council of view advisors ``c``. A council controls disposal and copying during cloning. Moreover, a council provides access to all advisors in the council (where already disposed advisors are excluded). The ``SameDom`` propagator does not store its views explicitly in a view array. As the council provides access to its advisors, all views can be accessed from the council’s advisors.


.. mpg-tip:: Different types of advisors for the same propagator

   Any propagator that uses advisors must have exactly one council. As the council depends on the advisor type, only one advisor type per propagator is possible.

   This is not a real restriction. If several different types of advisors are needed, one can either use advisors with virtual member functions or encode the advisor’s type by some member stored by the advisor.

.. _propagators:advisors:the-propagator-proper:

.. mpg-paragraph:: The propagator proper.




.. mpg-code:: samedom
   :caption: A ``samedom`` propagator using advisors
   :name: fig:p:advisors:samedom
   :download:

The ``SameDom`` propagator is shown in :numref:`fig:p:advisors:samedom`. The function ``include(home,x,d)`` constrains the view ``x`` to only take values from ``d``, whereas ``exclude(home,x,d)`` constrains the view ``x`` to not take any values from ``d``. The function ``dom(x,d)`` returns whether the values for ``x`` are included in ``d`` (``INCLUDE`` is returned) or whether values for ``x`` are excluded from ``d`` (``EXCLUDE`` is returned). All these functions are implemented with range iterators as discussed in :ref:`chap:p:domain`.

.. _propagators:advisors:posting-the-propagator:

.. mpg-paragraph:: Posting the propagator.

The propagator post function (not shown) makes sure that the propagator is only posted if for all views :math:`\mathtt{x}_i`, it cannot be decided whether :math:`\mathtt{x}_i\in\mathtt d` or :math:`\mathtt{x}_i\not\in\mathtt d`. If this is not the case, the post function already performs the necessary propagation. Note that the propagator post function by performing some propagation ensures the central invariant of the ``SameDom`` propagator: the value of ``todo`` (which is ``NOTHING`` initially) corresponds to the current domains of the propagator’s views.

The constructor for posting creates the required advisors as follows:


.. mpg-code:: samedom:constructor for posting

.. mpg-tip:: Getting a propagator started with advisors
   :name: tip:p:advisors:started

   The ``SameDom`` propagator has the property that when it is posted, it is known to be at fixpoint (the ``post()`` function ensures this by checking for each view :math:`\mathtt{x}_i` whether :math:`\mathtt{x}_i\in\mathtt d` or :math:`\mathtt{x}_i\not\in\mathtt d`).

   In general, it might not be true that a propagator using advisors is at fixpoint when it is posted. In that case, the constructor of the propagator must not only create advisors but also make sure that the propagator is scheduled for execution.

   A propagator can be scheduled by using the static ``schedule()`` function of a view. For example, assume that the propagator to be scheduled should be scheduled because one of its integer views of type ``IntView`` is assigned. This can be achieved by:

   .. mpg-code:: snippet:p-advisors:tip:p:advisors:started:code:1
      :direct:

   where ``*this`` refers to the current propagator.

   Likewise,

   .. mpg-code:: snippet:p-advisors:tip:p:advisors:started:code:2
      :direct:

   schedules the propagator with the information that the bounds of some of its integer views have changed.

.. _propagators:advisors:re-scheduling-the-propagator:

.. mpg-paragraph:: Re-scheduling the propagator.

The ``reschedule()`` member function just checks whether the propagator needs to be scheduled and uses the ``reschedule()`` member functions of integer views as discussed above:


.. mpg-code:: samedom:re-scheduling

.. _propagators:advisors:mandatory-propagator-disposal:

.. mpg-paragraph:: Mandatory propagator disposal.

The constructor also puts a notice on the propagator that it must always be disposed, even if the home space is deleted (as discussed in :ref:`sec:p:started:obligations`). Putting a notice is required because the integer set ``d`` of type :api:`IntSet` is a proper data structure and must hence be deleted when a ``SameDom`` propagator is disposed.

Accordingly, the ``dispose()`` function deletes the integer set ``d`` as follows:


.. mpg-code:: samedom:disposal

Disposing the council ``c`` also disposes all view advisors. Hence, also all subscriptions are canceled (as the ``dispose()`` function of a ``ViewAdvisor`` cancels its subscription).

It is essential to ignore the notice in ``dispose()`` by calling ``home.notice()``: otherwise Gecode might attempt to dispose a now already disposed propagator just over and over again!

.. _propagators:advisors:propagation-with-advice:

.. mpg-paragraph:: Propagation with advice.

The ``advise()`` function is straightforward:


.. mpg-code:: samedom:advise function

If ``todo`` is already different from ``NOTHING``, the propagator has already been scheduled, and the ``advise()`` function returns ``ES_FIX`` to signal that the propagator does not need to be scheduled again. [1]_ Otherwise, depending on the result of ``dom()``, the ``advise()`` function updates the ``todo`` value of the propagator and returns ``ES_NOFIX`` if the propagator needs scheduling (as ``todo`` is different from ``NOTHING``).

Note that the ``advise()`` function of ``SameDom`` ignores its :api:`Delta` argument. In the next section we will see a complementary design: the advisor does not carry any information, but only uses the information provided by the :api:`Delta`.

The ``propagate()`` member function is exactly as to be expected:


.. mpg-code:: samedom:propagation

The ``Advisors`` class provides an iterator over all advisors in the council ``c``. As mentioned earlier, the iterator (and hence the council) provides sufficient information to retrieve all views of interest for propagation.


.. mpg-tip:: Advisors and propagator obligations

   The astute reader might have wondered whether a ``SameDom`` propagator is actually “update complete” in the sense of :ref:`sec:p:started:obligations`. The answer is yes, because the council copies all of its view advisors and each view advisor updates its view in turn.

   Likewise, the obligations “subscription complete” and “subscription correct” need to be satisfied regardless of whether a propagator uses propagator condition-based or advisor-based subscriptions to views.

.. _propagators:advisors:advisor-disposal:

.. mpg-paragraph:: Advisor disposal.

The ``SameDom`` propagator leaves the disposal of its advisors to its own ``dispose()`` function. However, it could also request disposal of an advisor in the ``advise()`` function itself. A different implementation of the advise function would be:

.. mpg-code:: snippet:p-advisors:tip:p:advisors:started:code:3
   :direct:

With this design, all advisors would be disposed on behalf of the ``advise()`` function and not by the propagator’s ``dispose()`` function. This is due to the following two facts:

- A single advisor finds out that ``todo`` must be either ``EXCLUDE`` or ``INCLUDE``. This advisor returns ``ES_NOFIX_DISPOSE()`` and hence is disposed.

- All other advisors will be executed at the very latest when the propagator performs propagation and are disposed as well.

.. _propagators:advisors:using-predefined-view-advisors:

.. mpg-paragraph:: Using predefined view advisors.




.. mpg-code:: samedom using predefined view advisors
   :caption: A ``samedom`` propagator using predefined view advisors
   :name: fig:p:advisors:samedomview
   :download:

Unsurprisingly, view advisors are a common abstraction for propagators using advisors. Hence, Gecode provides view advisors as predefined abstractions that are parametric with respect to their view type. :numref:`fig:p:advisors:samedomview` shows how ``SameDom`` can be implemented using predefined view advisors.

.. _sec:p:advisors:or:

General Boolean disjunction
---------------------------

Let us consider an efficient propagator ``Or`` for implementing the Boolean disjunction

.. math:: \bigvee_{i=0}^{|\mathtt{x}|-1} \mathtt{x}_i=\mathtt{y}

where all :math:`\mathtt{x}_i` and :math:`\mathtt y` are Boolean views. When ``y`` becomes assigned, propagation is straightforward. If ``y`` is assigned to ``0``, all :math:`\mathtt{x}_i` must be assigned to ``0`` as well. If ``y`` is assigned to ``1``, ``Or`` is rewritten into the propagator ``OrTrue`` from :ref:`sec:p:avoid:dynamic`.

As it comes to the :math:`\mathtt{x}_i`, the ``Or`` propagator uses a similar technique to the ``SameDom`` propagator. It can use advisors to find out which view has been assigned instead of inspecting all :math:`\mathtt{x}_i`. However, the propagator requires very little information: it does not need to know which view has changed, it only needs to know whether a view among the :math:`\mathtt{x}_i` has been assigned to ``0`` or ``1``. Our ``Or`` propagator uses the delta information passed to the ``advise()`` function to determine the value to which a view has been assigned. The advantage is that the propagator only needs a single advisor instead of one advisor per view.


.. mpg-tip:: Advisor space requirements

   A subscription requires one pointer, regardless of whether a propagator or an advisor is subscribed to a view. Without any additional information stored by an advisor, an advisor requires two pointers. Hence, it pays off to use as few advisors as possible.

.. _propagators:advisors:the-or-propagator:

.. mpg-paragraph:: The ``Or`` propagator.




.. mpg-code:: or
   :caption: A Boolean disjunction propagator using advisors
   :name: fig:p:advisors:or
   :download:

The ``Or`` propagator inherits from the :api:`MixNaryOnePropagator` template (to increase readability, a base class ``OrBase`` is defined as a type) and uses ``PC_BOOL_NONE`` as propagation condition for the views in the view array ``x``. That actually means that no subscriptions are created for the views in ``x``. A subscription with propagation condition ``PC_BOOL_VAL`` is created for the single Boolean view ``y``. The constructor for posting creates a single advisor which subscribes to all views in ``x``. In fact, the ``Or`` propagator mixes advisors with normal subscriptions.

The ``advise()`` function uses the delta information to decide whether one of the views the advisor has subscribed to is assigned to ``0`` (then ``Int::BoolView::zero()`` returns true):


.. mpg-code:: or:advise

The ``advise()`` function counts the number of views assigned to zero in ``n_zero``. By returning ``ES_NOFIX`` it reports that the propagator must be scheduled, if all views have been assigned to zero (that is, ``n_zero`` equals the number of views in ``x``) or if a view has been assigned to one. Note that the propagator post function makes sure that the propagator is only posted when none of the views in ``x`` are assigned.

The ``reschedule()`` function checks whether the propagator needs to be re-scheduled. This is the case when ``y`` has been assigned, or a view in ``x`` has been assigned to one, or if all views in ``x`` have been assigned zero.


.. mpg-code:: or:re-scheduling

The ``propagate()`` function is straightforward:


.. mpg-code:: or:propagation

It first checks whether the propagator has been executed because ``y`` has been assigned and propagates as sketched before. Then it uses the value of ``n_zero`` to determine how to propagate.

.. _par:p:advisors:delta:

.. mpg-paragraph:: Delta information for integer views.

The delta information provided to the ``advise()`` function can be interpreted through the view the advisor has subscribed to. Boolean views provide static member functions ``zero()`` and ``one()`` to find out whether the view has been assigned to ``0`` or ``1``.

For integer views (and set views, see :ref:`sec:p:sets:propagation_conditions_etc`), one must use the view to which the advisor has subscribed to for accessing the delta.

.. container:: samepage

   For example, suppose that the advisor ``a`` has subscribed to the view ``x`` by

   .. mpg-code:: snippet:p-advisors:par:p:advisors:delta:code:1
      :direct:

When the ``advise()`` function is executed for the advisor ``a`` with delta ``d``, the view ``x`` provides access to the delta information (typically, this will mean that ``a`` in fact stores the view ``x``).

The modification event of the operation that modified the view ``x`` is available by ``x.modevent(d)``. If ``x.any(d)`` returns true, no further information about how the domain of ``x`` has changed is available.

Only if ``x.any(d)`` is false, ``x.min(d)`` returns the smallest value and ``x.max(d)`` returns the largest value of the values that have been removed from ``x``. With other words, the delta ``d`` only provides approximate information on how the old view domain has been changed.

For example, if ``x`` has the domain :math:`\{0,1,4,5,6\}` and the value :math:`4` is removed from ``x``, then a delta ``d`` is passed where ``x.any(d)`` is true. If the values :math:`\{0,1,4\}` are removed and the new domain is :math:`\{5,6\}` then a delta ``d`` is passed where ``x.any(d)`` is false and ``x.min(d)`` returns :math:`0` and ``x.max(d)`` returns :math:`4`.

For Boolean views, one can rely on the fact that the delta information is always accurate. For integer views, it might be the case that ``x.any(d)`` returns true even though only the bounds of ``x`` have changed.

.. _sec:p:advisors:force:

Forced propagator re-scheduling
-------------------------------

An advisor can force its propagator to be re-scheduled even though the propagator’s modification event delta has not changed. As discussed in :ref:`sec:p:domain:staging`, the ``cost()`` function of a propagator is only recomputed when its modification event delta changes.

When the ``advise()`` of a propagator returns ``ES_NOFIX_FORCE`` (or, the ``advise()`` function calls ``ES_NOFIX_DISPOSE_FORCE()``), the propagator is rescheduled regardless of its current modification event delta. See also :api:`Status of constraint propagation and branching commit <TaskActorStatus>`.

.. [1]
   Actually, it would also be okay to return ``ES_NOFIX``. Scheduling an already scheduled propagator is okay.
