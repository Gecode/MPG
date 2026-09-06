
.. only:: latex

   .. mpg-part:: Programming variables
      :letter: V
      :name: pdf-part:v
      :authors: Christian Schulte

      .. include:: ../parts/variables.rst
         :start-after: .. mpg-part-blurb-start
         :end-before: .. mpg-part-blurb-end

.. _chap:v:started:

Getting started
===============

This chapter outlines how a new variable type can be programmed with Gecode. The chapter (and the entire part on programming variables) chooses integer interval variables as its running example.

.. _variables:overview:

.. mpg-paragraph:: Overview.

An overview of what needs to be designed and programmed is presented in :ref:`sec:v:started:overview`. The structure of how the implementation of a variable type is organized is presented in :ref:`sec:v:started:structure`.

.. important::

   Programming variables requires to configure and recompile Gecode from its source code. More details can be found in :ref:`chap:v:all`.

.. _sec:v:started:overview:

Overview
--------

We are going to use *integer interval variables* as the running example for programming variables. Integer interval variables take integer values (like the integer variables that come pre-defined with Gecode do) but their domain is defined by a lower and an upper bound only. That is, the domain is always an interval. This is in contrast to the integer variables that come with Gecode, where their domain can be any finite set of integer values.

The focus of this part is on understanding what needs to be done for implementing new variables, so we deliberately choose very simple variables together with very few operations on them as an example.

Even though integer interval variables seem not very interesting, variants of them could in fact be interesting. For example, the integer values used for the lower and upper bound could be integers of arbitrary precision, or instead of integer values one could choose floating point values.

.. _variables:what-must-be-programmed:

.. mpg-paragraph:: What must be programmed.

Programming variables includes the following tasks:

- *Variable implementations* (:ref:`chap:v:varimp`): Programming a variable implementation consists of two tasks.

  - The first task is to specify domain-independent aspects of a variable implementation. This includes specifying a name for the variable implementation type, scope information, modification events, and propagation conditions. From a simple specification file containing this information a domain-independent base class for a variable implementation and the corresponding C++ definitions of modification events and propagation conditions is generated.

    The generated base class together with the definition of modification events and propagation conditions actually become part of Gecode’s kernel. The kernel needs these definitions to schedule propagators that have subscribed to a variable implementation and to maintain these subscriptions during cloning.

  - The second task consists of programming the domain-dependent operations of a variable implementation. This is achieved by defining a class for a variable implementation that inherits from the generated, domain-independent base class and defines the respective domain operations.

- *Variables* and *variable arrays* (:ref:`chap:v:var`): As a variable is nothing but a simple and read-only interface to a variable implementation, a variable is obtained by inheriting from a base class for variables that depends on the variable implementation type. The actual programming amounts to defining read-only variable operations that invoke the corresponding operations on the variable’s variable implementation.

  Variable arrays and variable argument arrays are, as variables, needed for modeling. Their programming requires the definition of several traits classes so that the defined arrays can be used with Gecode-provided functionality (for example, with the matrix interface for arrays, see :ref:`sec:m:minimodel:matrix`).

- *Views* (:ref:`chap:v:view`): Programming a view depends on the type of the view: whether the view is a direct interface to a variable implementation (a *variable implementation view*), whether it is a *constant view*, or whether it is derived (a *derived view*) from some other view. As examples, we are going to implement an integer view as a variable implementation view, minus and offset views as derived views, and an integer constant view as a constant view.

  In addition to the classes for views, some additional functions on views must be defined for testing in which order views are and whether two views are shared or the same (see :ref:`par:p:views:sameshared`).

- *Constraints* and *branchings*: typically, when implementing variables one also needs to implement constraints and branchings for them. The implementation of constraints for a new variable type is not in any way different from what is described in :ref:`part:p`.

  The situation for implementing branchings is quite different: here one would want to offer at least a common set of variable-value branchings similar to those for integer variables (see :ref:`sec:m:branch:int`). Gecode offers substantial support for implementing variable-value branchings, including support for the specification of variable and value selection strategies, random and action-based selection of variables, tie-breaking, filter functions, no-goods, and much more. How to use Gecode’s support for implementing variable-value branchings is detailed in :ref:`chap:v:branch`.

  In case one implements *reified* constraints, it is possible to use these reified constraints together with Boolean expressions and relations as provided by the MiniModel modeling support. For an example, please consider :ref:`sec:m:minimodel:boolmisc`.

- *Tracing* support (:ref:`chap:v:trace`): in order to support variable tracing, one needs to implement a few classes.

  Only so-called *trace views* require some effort, the remaining functionality that needs to be implemented is straightforward and can be done by following a simple recipe.

.. _variables:putting-everything-together:

.. mpg-paragraph:: Putting everything together.

Even though we are presenting the implementation of integer interval variables only as an example, :ref:`chap:v:all` shows how everything is put together. This includes examples of propagators, post functions using various views, and a simple script (Golomb rulers, see :ref:`chap:c:golomb`) using integer interval variables.

It also shows how Gecode must be configured and compiled such that integer interval variables are supported by Gecode’s kernel.

.. _sec:v:started:structure:

Structure
---------


.. _fig:v:started:header:

.. mpg-figure:: The header file for integer interval variables
   :name: mpg-variable-figure-1

   .. mpg-code:: int.hh

The implementation of integer interval variables is contained in a single header file ``int.hh``, which is shown in :ref:`fig:v:started:header`.

.. _variables:namespaces:

.. mpg-paragraph:: Namespaces.

The implementation is contained in the namespace ``MPG`` (for ``M``\ odeling and ``P``\ rogramming with ``G``\ ecode) to avoid name-clashes with functionality provided by Gecode. To keep the implementation of integer interval variables concise, some important definitions in the ``Gecode`` namespace are made available by ``using`` declarations (see :ref:`fig:v:started:header`).

Similar to the organization of namespaces in Gecode, definitions that are used for modeling (variables and variable arrays) are contained in the namespace ``MPG``, while definitions that are used for programming (variable implementations, views, branchers, and additional support) are in the namespace ``MPG::Int``.

As the structure of namespaces matters (part of the support for variable arrays must be defined inside the ``Gecode`` namespace), each program fragment is shown in its appropriate namespace.

As an example, consider the definition of exceptions. Two are thrown by the constructor of the integer interval variable, in case the variable domain is ill-specified. The third exception is thrown when the variable or value selection for a branching is unknown.

The exceptions are defined as follows:

.. mpg-code:: int.hh:exceptions

As discussed above, :api:`Exception` is ``Gecode::Exception`` (see :api:`Exception`) and has been introduced by a ``using`` declaration.

.. _variables:naming-scheme:

.. mpg-paragraph:: Naming scheme.

The naming scheme follows the same naming scheme for integer variables as defined by Gecode (albeit defined in the namespace ``MPG`` instead of ``Gecode``):

- Variable implementations: The base class is named ``IntVarImpBase`` whereas the variable implementation class is named ``IntVarImp``. The names of modification events start with ``ME_INT_`` whereas the names of propagation conditions start with ``PC_INT_``. As mentioned above, these classes and identifiers are defined within the namespace ``MPG::Int``.

- Variables and variable arrays: Integer interval variables are implemented by the class ``IntVar``. Variable arrays of integer interval variables are implemented by the class ``IntVarArray``, whereas the corresponding variable argument array is implemented by the class ``IntVarArgs``. These classes are defined in the namespace ``MPG``.

- Views: the respective views are implemented by classes ``IntView``, ``ConstIntView``, ``MinusView``, and ``OffsetView``. They are all defined within the namespace ``MPG::Int``.

- Branchings: how variables and values are selected is implemented by functions such as ``INT_VAR_NONE()`` or ``INT_VAL_MIN()`` and the actual branching is implemented by a single ``branch()`` function. The good news is that no actual brancher must in fact be implemented, even though a number of rather straightforward support definitions must be implemented (which are contained in the namespace ``MPG::Int``).

- Variable tracing: variable tracers are implemented by the class ``IntTracer`` (a type definition), a standard variable tracer is implemented by the class ``StdIntTracer``, a variable trace recorder by a class ``IntTraceRecorder`` (also a type definition), and an integer trace delta by a class ``IntTraceDelta``. Additionally, trace views are implemented by a class ``Int::IntTraceView`` and some traits must be defined.

.. _variables:inline-functions-as-simplification:

.. mpg-paragraph:: Inline functions as simplification.

All functions, be they member or non-member functions are defined as ``inline``. The reason for this is to make it easier to follow the example, as only the single header file ``int.hh`` is needed. In a real implementation one would move the definitions of some functions to a source file and only leave the declaration of the functions in the header file. This is in particular true for many of the functions defined in :ref:`chap:v:branch`.

.. _chap:v:varimp:

Variable implementations
========================

This chapter describes how variable implementations can be programmed with Gecode. The chapter uses integer interval variables as introduced in :ref:`chap:v:started` as its running example.

.. _variables:overview-2:

.. mpg-paragraph:: Overview.

The design of integer interval variables is detailed in :ref:`sec:v:varimp:design`. After having finalized the design, :ref:`sec:v:varimp:spec` explains how the domain-independent base class for the variable implementation together with definitions of modification events and propagation conditions can be generated from a simple specification. :ref:`sec:v:varimp:varimp` shows how the actual variable implementation is programmed from the generated base class for a variable implementation. :ref:`sec:v:varimp:add` provides an overview of additional options for generating a variable implementation base class from its specification.

.. _sec:v:varimp:design:

Design decisions
----------------

Before starting with the description of the implementation of integer interval variables, let us detail their design. This includes the design of the variable domain including access and modification operations, deltas for advisors (see :ref:`chap:p:advisors`), modification events, and propagation conditions.

.. _variables:variable-domain-and-operations:

.. mpg-paragraph:: Variable domain and operations.

Unsurprisingly, the variable domain of an integer variable implementation is represented by two integers ``l`` (lower bound) and ``u`` (upper bound). The variable implementation provides access operations ``min()`` and ``max()`` that return these integers.

To modify an integer interval variable implementation, the operation ``gq(home,n)`` modifies the domain such that its values must be greater or equal to ``n``, whereas the operation ``lq(home,n)`` modifies the domain such that its values must be less or equal to ``n``.

The values ``l`` and ``u`` can only be initialized (when creating a new variable, see :ref:`sec:v:var:var`) and modified such that they obey the following invariants:

#. The domain is never empty, that is, :math:`\mathtt{l}\leq\mathtt{u}`.

#. The domain values never exceed the limits defined by (``INT_MAX`` is the largest possible value for an ``int``):

   .. mpg-code:: int.hh:limits

   That is, :math:`\mathtt{Int::Limits::min}\leq \mathtt l\leq \mathtt u\leq\mathtt{Int::Limits::max}`.

The choice of values for ``Limits::min`` and ``Limits::max`` are motivated by simplicity only. To keep the example propagators used in :ref:`chap:v:all` simple, the limits are chosen such that the addition and subtraction of two integer values within the limits do not lead to numerical overflow. A real-life variable implementation would try to make as many values as possible available for a variable domain, see for example :ref:`sec:m:integer:limits`.


.. mpg-tip:: Correctness matters

   While the decision to restrict the possible values of a variable implementation is motivated by simplicity, the decision for a real-life variable implementation is absolutely essential.

   Being unclear about which values can correctly be maintained by a variable implementation, not ensuring that no numerical overflow occurs, or not checking for the necessary invariants when a new variable is created, renders the very idea of constraint programming obsolete: that whenever a solution is found by Gecode, it *actually happens to be a solution*. Hence correctness does not only matter for implementing propagators and branchers but also for getting the basic design of variables right.

.. _variables:gecode-integer-domains:

.. mpg-paragraph:: Domains of Gecode integer variables.

The integer interval variables developed here need only the two bounds ``l``
and ``u``. Gecode's predefined integer variables also admit holes in their
domains. They use two representations for this. A domain without holes stores
its lower and upper bound directly in the variable implementation and needs no
additional range buffer. A domain with holes stores a contiguous sequence of
inclusive ``(min,max)`` range pairs in memory managed by its space. These
ranges are ordered, disjoint, and non-adjacent, so there is exactly one
canonical sequence for a domain. This compact representation replaces the
XOR-linked doubly linked range list used by earlier versions of Gecode.

The representation is private to the variable implementation. Public range
and value iterators expose the domain, but not the range-pair storage. The
operations that assign a value, remove a value, restrict a bound, or intersect
or subtract ranges maintain the canonical sequence and its cached cardinality.
They also report the same integer modification events as the corresponding
domain changes require. Operations accepting an iterator take care not to
overwrite storage on which that iterator still depends.

This distinction also affects copying during search. Copying a variable whose
domain has no holes copies only its inline state. A sparse domain receives a
new range buffer sized to the ranges that are live at the time of the copy;
unused buffer capacity is not copied. Recomputation instead reconstructs a
space by replaying choices and their domain modifications. Both mechanisms
therefore preserve the same domains, while the common interval case remains
cheap to copy.

.. _variables:assigned-variables:

.. mpg-paragraph:: Assigned variables.

An integer interval variable is assigned iff :math:`\mathtt l=\mathtt u`.

.. _variables:deltas-for-advisors:

.. mpg-paragraph:: Deltas for advisors.

We design the delta information for an advisor computed by a modification operation on the variable implementation to be an interval as well. The interval defines the values that are removed by a modification operation. Due to the nature of the modification operations ``lq()`` and ``gq()``, the removed values always form an interval.

The design of deltas to be used by advisors for a variable implementation depends directly on the design of the modification operations provided by a variable implementation. For example, if our integer interval variable implementation also featured an operation ``eq()`` to assign a variable implementation to a value, then one also would have to choose a different design for the delta information. Assume a variable implementation with domain :math:`[\mathtt{l},\mathtt{u}]` and that the modification operation ``eq(home,n)`` is executed where :math:`\mathtt{l}<\mathtt n<\mathtt u`. Then one could design the delta information to either accurately represent the set of removed values :math:`[\mathtt{l},\mathtt{n-1}]\cup[\mathtt{n+1},\mathtt{u}]` or to provide support for signaling that the domain has changed arbitrarily (this is the design chosen for integer variables in Gecode, see :ref:`par:p:advisors:delta`).

.. _variables:modification-events:

.. mpg-paragraph:: Modification events.

Any variable implementation must support the mandatory events for no modification (to be implemented as ``ME_INT_NONE``), for failure (to be implemented as ``ME_INT_FAILED``), and for assignment to a value (to be implemented as ``ME_INT_VAL``).

The additional events must be chosen such that they take the following two aspects into account:

- The modification operations should return meaningful values that describe how the domain of a variable implementation has changed. They must return ``ME_INT_VAL`` if the variable implementation becomes assigned. Otherwise, we choose to return ``ME_INT_MIN`` if the lower bound changes and to return ``ME_INT_MAX`` if the upper bound changes.

- When a new propagator is posted and the propagator subscribes to some views (and hence to some variable implementations), the propagator must be scheduled with respect to some modification event. This modification event should capture that “somehow the variable has changed for the propagator”. In case an integer interval variable implementation is not yet assigned (otherwise the propagator will be scheduled with the modification event ``ME_INT_VAL`` anyway), we use an additional modification event ``ME_INT_BND`` capturing that one or both of the bounds have changed.

Again, there is quite some degree of freedom in the choice of modification events. Another design would be to only provide the modification event ``ME_INT_BND`` instead (apart from the mandatory modification events). An important aspect in which design to choose is the relation between modification events and propagation conditions to be discussed below.

.. _par:v:varimp:design:pc:

.. mpg-paragraph:: Propagation conditions.

To make our example variable implementations sufficiently interesting, we design the propagation conditions such that they can take full advantage of the modification events.

That is, apart from the mandatory propagation condition for not creating any subscription (to be implemented as ``PC_INT_NONE``) and the mandatory propagation condition for an assigned variable implementation (to be implemented as ``PC_INT_VAL``), we have three propagation conditions as follows:

- ``PC_INT_MIN``: schedule a propagator if the lower bound of a variable implementation changes.

- ``PC_INT_MAX``: schedule a propagator if the upper bound changes.

- ``PC_INT_BND``: schedule a propagator if lower or upper bound changes.

This design can also be reformulated in terms of modification events that are generated by a modification operation:

- ``PC_INT_MIN``: schedule a propagator for ``ME_INT_VAL``, ``ME_INT_MIN``, and ``ME_INT_BND``.

- ``PC_INT_MAX``: schedule a propagator for ``ME_INT_VAL``, ``ME_INT_MAX``, and ``ME_INT_BND``.

- ``PC_INT_BND``: schedule a propagator for ``ME_INT_VAL``, ``ME_INT_MIN``, ``ME_INT_MAX``, and ``ME_INT_BND``.

A simpler design would be to have the single non-mandatory propagation condition ``PC_INT_BND``. The decision which design is best is not straightforward, as the tradeoff between the cost for additional propagation conditions (see below) and the gain from avoiding propagator executions depends on many different aspects. For a discussion and an evaluation in the context of Gecode’s integer variables, see :cite:p:`SchulteStuckey:TOPLAS:2008`.

.. _par:v:varimp:design:cost:

.. mpg-paragraph:: Costs and limits for modification events and propagation conditions.

The cost per each individual modification event and propagation condition is as follows:

- Assume that a variable implementation uses :math:`n` different modification events (including the mandatory ones). The size of :math:`n` does not affect efficiency. To represent these modification events, the Gecode kernel reserves :math:`\lceil\log_2 (n-1)\rceil` bits in each propagator for maintaining modification event deltas, see :ref:`sec:p:domain:med`.

  The totally available number of bits for all variable implementation types used by Gecode is :math:`32` (independent of whether Gecode is run on a :math:`32` bit or :math:`64` bit platform). That is, if we assume less than ten modification events per variable implementation type, the Gecode kernel can support at least ten different variable implementation types. [1]_

- The number of different propagation conditions :math:`m` per variable implementation type is only limited by the largest value of an unsigned integer in C++.

  For each propagation condition, every variable implementation needs a :math:`32`-bit word, that is a variable implementation requires at least :math:`O(m)` space (which is typically dwarfed by the space consumed for actually storing the subscriptions of a propagator or an advisor to a variable implementation).

  Subscribing to a variable implementation requires :math:`O(m)` time. Canceling a subscription with propagation condition :math:`p` requires :math:`O(m+k)` time, where :math:`k` is the number of subscriptions with propagation condition :math:`p`.

.. _sec:v:varimp:spec:

Base definitions
----------------

The variable implementation base class together with definitions of modification events and propagation conditions are not programmed but are generated from a simple specification file. The specification contains three sections: a general section for naming, a section for modification events, and a section for propagation conditions.

In the following we describe how to turn the parts of the design from the previous section that is concerned with modification events and propagation conditions into the specification. The member functions of the generated base class are used and explained in the next section.

.. _variables:general-section:

.. mpg-paragraph:: General section.


.. _fig:v:varimp:vis:

.. mpg-figure:: Variable implementation specification
   :name: mpg-variable-figure-2

   .. code-block:: ini

      variable implementation specification
      [General]
      Name: Int
      Namespace: MPG::Int
      modification events
      propagation conditions
      [End]

The specification file (named ``int.vis``, where ``vis`` stands for ``v``\ ariable ``i``\ mplementation ``s``\ pecification; however the file extension does not matter) is shown in :ref:`fig:v:varimp:vis`. The specification file must start with ``[General]`` defining the start of the general section and must end with a line ``[End]``. The ``Name`` option defines the names of the entities to be generated. In our example, a variable implementation base class ``IntVarImpBase`` (that is, the specified name is prepended to ``VarImpBase``) generated, the identifiers for modification events start with ``ME_INT_`` (that is, the specified name is put after the ``ME_`` in capital letters), and the identifiers for propagation conditions start with ``PC_INT_``. All these definitions are contained within the namespace as defined by the ``Namespace`` option.

The general section (and also the other sections discussed below) supports additional specification options, see :ref:`sec:v:varimp:add` for a summary and a specification file template for download.

.. _variables:modification-event-section:

.. mpg-paragraph:: Modification event section.


.. _fig:v:varimp:vis:me:

.. mpg-figure:: Modification event section
   :name: mpg-variable-figure-3

   .. code-block:: ini

      modification events
      [ModEvent]
      Name: FAILED=FAILED
      [ModEvent]
      Name: NONE=NONE
      [ModEvent]
      Name: VAL=ASSIGNED
      Combine: VAL=VAL, MIN=VAL, MAX=VAL, BND=VAL
      [ModEvent]
      Name: BND=SUBSCRIBE
      Combine: VAL=VAL, MIN=BND, MAX=BND, BND=BND
      [ModEvent]
      Name: MIN
      Combine: VAL=VAL, MIN=MIN, MAX=BND, BND=BND
      [ModEvent]
      Name: MAX
      Combine: VAL=VAL, MIN=BND, MAX=MAX, BND=BND

Every modification event requires a definition that is preceded by a line containing ``[ModEvent]`` as shown in :ref:`fig:v:varimp:vis:me`. The option ``Name`` defines the name of the modification event (in fact, just the part after ``ME_INT_`` for our example). The values on the right-hand side of ``=`` specify that some modification events are special:

- The modification events named ``FAILED`` (that is, ``ME_INT_FAILED``) and ``NONE`` (that is, ``ME_INT_NONE``) are defined to be the events for failure (``=FAILED``) and no change (``=NONE``).

- The modification event named ``VAL`` is defined to be the event when a variable implementation becomes assigned (``=ASSIGNED``) to a value.

- The modification event named ``BND`` is defined to be used for scheduling a propagator when the propagator subscribes to a non-assigned variable implementation (``=SUBSCRIBE``).

Any variable implementation must define special events with ``=NONE``, ``=FAILED``, ``=ASSIGNED``, and ``=SUBSCRIBE``. In case there are only three modification events (all of them special with ``=NONE``, ``=FAILED``, ``=ASSIGNED``), the modification event used for scheduling a propagator (that is, ``=SUBSCRIBE``) is defined to be the event for a variable becoming assigned (that is, ``=ASSIGNED``).

The section for modification events also defines how modification events are combined with a ``Combine`` option. The combination of modification events is needed for the correctness of scheduling propagators and also for modification event deltas, see :ref:`sec:p:domain:med`. An entry :math:`l=r` for the modification event :math:`m` defines that :math:`m` combined with :math:`l` is :math:`r`.

The definition of the combination of modification events can be expressed as a table:


.. container:: center

   === === === === ===
   \   VAL MIN MAX BND
   === === === === ===
   VAL VAL VAL VAL VAL
   MIN VAL MIN BND BND
   MAX VAL BND MAX BND
   BND VAL BND BND BND
   === === === === ===

This table is exactly what is specified by the ``Combine`` options. The special modification events ``NONE`` and ``FAILED`` do not have a ``Combine`` option.

We will not present the full mathematical detail of the properties that must hold for the combination of modification events, the theory is presented in :cite:p:`Tack:PhD:2009`.

.. _variables:propagation-condition-section:

.. mpg-paragraph:: Propagation condition section.


.. _fig:v:varimp:vis:pc:

.. mpg-figure:: Propagation condition section
   :name: mpg-variable-figure-4

   .. code-block:: ini

      propagation conditions
      [PropCond]
      Name: NONE=NONE
      [PropCond]
      Name: VAL=ASSIGNED
      ScheduledBy: VAL
      [PropCond]
      Name: BND
      ScheduledBy: VAL, BND, MIN, MAX
      [PropCond]
      Name: MIN
      ScheduledBy: VAL, BND, MIN
      [PropCond]
      Name: MAX
      ScheduledBy: VAL, BND, MAX

Every propagation condition requires a definition that is preceded by a line containing ``[PropCond]`` as shown in :ref:`fig:v:varimp:vis:pc`. The option ``Name`` defines the name of the propagation condition (in fact, just the part after ``PC_INT_`` for our example). The values on the right-hand side of ``=`` specify that some propagation conditions are special:

- The propagation condition named ``NONE`` (that is, ``PC_INT_NONE``) is defined to be the propagation condition for not creating any subscription (``=NONE``).

- The propagation condition named ``VAL`` (that is, ``PC_INT_VAL``) is defined to be the condition when a propagator wants to subscribe to the event that a variable implementation becomes assigned (``=ASSIGNED``).

Any variable implementation must define the special propagation conditions ``=NONE`` and ``=ASSIGNED``.

For each propagation condition (but for ``=NONE``), it must be defined by a ``ScheduledBy`` option which modification events schedule a propagator for execution. That is, when defining a propagation condition :math:`p`, an entry :math:`m` in the list of modification events defines the following: a propagator subscribed to a variable implementation :math:`x` with propagation condition :math:`p` is scheduled for execution when a modification operation on :math:`x` returns the modification event :math:`m`. The modification events in our example correspond to the design presented in :ref:`par:v:varimp:design:pc`.

.. _sec:v:varimp:varimp:

Variable implementation
-----------------------


.. _fig:v:varimp:varimp:

.. mpg-figure:: Variable implementation
   :name: mpg-variable-figure-5

   .. mpg-code:: int.hh:variable implementation

The variable implementation for integer interval variables is shown in :ref:`fig:v:varimp:varimp`. As discussed in the previous sections, the variable implementation inherits from the generated base class ``IntVarImpBase`` and implements a lower bound ``l`` and an upper bound ``u``.

.. _variables:access-operations:

.. mpg-paragraph:: Access operations.

Every variable implementation must implement a member function ``assigned()`` that tests whether the variable is assigned to a value:

.. mpg-code:: int.hh:varimp:assignment test

The test for assignment is used in the implementation of other member functions of the variable implementation. Furthermore, variables and views automatically provide implementations of a member function ``assigned()`` that calls the ``assigned()`` function of their variable implementation.

The access operations for the lower and upper bound are straightforward. Here, and in the following, we only show one of the operations, the operation for the other bound is analogous:

.. mpg-code:: int.hh:varimp:access operations

.. _variables:modification-operations:

.. mpg-paragraph:: Modification operations.

The modification operations must notify the Gecode kernel if a variable implementation is modified. As a description how a variable implementation changes, they must pass a modification event and delta information for advisors to a member function ``notify()``. The ``notify()`` function executes subscribed advisors and schedules subscribed propagators (depending on the passed modification event and the propagators’ propagation conditions). The ``notify()`` function is inherited from the generated variable implementation base class and depends on the specified modification events and propagation conditions.

The delta information is implemented as discussed in :ref:`sec:v:varimp:design` as an interval with lower and upper bound:

.. mpg-code:: int.hh:varimp:delta for advisors

The actual modification operations first test whether the variable implementation does not require modification or whether the operation fails and only then perform the actual modification. Before updating the upper bound ``u`` to ``n``, the ``lq()`` operation creates the delta information ``d`` that describes that values between ``n+1`` and ``u`` are being removed.

The ``notify()`` function is given the ``home`` space, a modification event, and the variable delta ``d`` as argument. The modification event passed to ``notify()`` must capture how the domain has changed. In particular, it must reflect whether the variable implementation has been assigned. The ``notify()`` function executes the advisors subscribed to this variable implementation and schedules all subscribed propagators with appropriate propagation conditions. Note that the ``notify()`` function returns a modification event. In case an advisor reports failure after its execution, ``notify()`` returns ``ME_INT_FAILED``. Otherwise it returns the modification event that has been passed as argument:

.. mpg-code:: int.hh:varimp:modification operations

If a modification operation fails it must return ``ME_INT_FAILED`` as modification event and must call the ``fail()`` function. The ``fail()`` function is similar to ``notify()`` and executes advisors that have registered to be executed on failure. For convenience, the ``fail()`` function itself returns ``ME_INT_FAILED``.


.. mpg-tip:: Variable implementations must always be consistent

   Even if a modification operation fails, the data structures for the variable implementation must be still consistent. That is, all operations must still work. See also :ref:`sec:m:integer:empty`.

.. _variables:delta-information-access:

.. mpg-paragraph:: Delta information access.

The variable implementation must also implement functions that provide access to the delta information:

.. mpg-code:: int.hh:varimp:delta information

This construction appears nonsensical at first sight, however there are two good reasons why a variable implementation interprets the information stored in the delta information (of course, in that case one would have to declare the operation as ``const`` but not ``static``). First, the variable implementation can change the information based on its own state. Second, the very same idea is needed for views (see :ref:`sec:v:view:offset` for an example) and hence this design keeps the interfaces of views and variable implementations as similar as possible.

.. _variables:subscriptions:

.. mpg-paragraph:: Subscriptions.

A variable implementation must implement ``subscribe()`` operations for both propagators and advisors. The implementation of these operations always follow the same structure as shown below.

The reason why these functions have to be implemented in the variable implementation class even though they are (in slightly different form) already defined in the variable implementation base class is that they require information about whether a variable implementation is assigned. The definitions are as follows:

.. mpg-code:: int.hh:varimp:subscriptions

.. _variables:re-scheduling:

.. mpg-paragraph:: Re-scheduling.

A variable implementation must implement a ``reschedule()`` operation for propagators. The implementation of this operation is almost identical to the ``subscribe()`` member function discussed previously. The definition is as follows:

.. mpg-code:: int.hh:varimp:re-scheduling

.. _variables:copying-during-cloning:

.. mpg-paragraph:: Copying during cloning.

Copying a variable implementation during cloning is implemented by a constructor and a ``copy()`` function. The constructor is straightforward and the ``copy()`` function only creates a new variable implementation if the variable implementation has not been copied before. If it has been copied before (that is, ``copied()`` returns ``true``), the ``copy()`` function must return the forwarding pointer to the previously created copy as follows:

.. mpg-code:: int.hh:varimp:copying

.. _variables:additional-inherited-member-functions:

.. mpg-paragraph:: Additional inherited member functions.


.. _fig:v:varimp:inherited:

.. mpg-figure:: Summary of member functions predefined by variable implementations
   :name: mpg-variable-figure-6

   .. list-table::
      :header-rows: 0
      :widths: 28 32 40

      * - **access operations**
        -
        -
      * -
        - ``degree()``
        - returns degree (number of subscriptions)
      * -
        - ``afc()``
        - returns accumulated failure count
      * - **subscriptions**
        -
        -
      * -
        - ``cancel()``
        - cancel subscription of propagator
      * -
        - ``cancel()``
        - cancel subscription of advisor
      * - **scheduling support**
        -
        -
      * -
        - ``schedule()``
        - schedule propagator
      * -
        - ``reschedule()``
        - re-schedule propagator
      * - **modification event deltas**
        -
        -
      * -
        - ``me()``
        - extract modification event
      * -
        - ``med()``
        - construct modification event delta
      * - **delta information access**
        -
        -
      * -
        - ``modevent()``
        - return modification event from delta

In addition to the constructor and the member functions defined and used by our variable implementation, several other member functions are typically just inherited and are defined by the class :api:`VarImp`. The most important inherited member functions are summarized in :ref:`fig:v:varimp:inherited`. For an explanation of degree and accumulated failure count, see :ref:`sec:m:branch:shared`.

.. _sec:v:varimp:add:

Additional specification options
--------------------------------

This section provides an overview of additional specification options not discussed in :ref:`sec:v:varimp:spec`.

.. _variables:comments:

.. mpg-paragraph:: Comments.

Any line starting with ``#`` is discarded and hence can serve as a comment in the specification file.

.. _variables:generating-headers-footers-and-comments:

.. mpg-paragraph:: Generating headers, footers, and comments.

Any text after the options for a ``[ModEvent]`` and ``[PropCond]`` definition until the next definition is added to the generated C++-code before the generated identifier definition. This can be used for defining comments to be added to the generated C++-code. For example, by

.. code-block:: console

   [PropCond]

   Name: NONE=NONE

   // Propagation condition to be ignored

   [PropCond]

   ...

the comment

.. mpg-code:: snippet:v:sec:v:varimp:add:code:1
   :direct:

is put before the definition of the generated propagation condition.

Related support exists for putting a header before (or a footer after) all generated definitions for modification events and propagation conditions: The text following ``[ModEventHeader]``, ``[ModEventFooter]``, ``[PropCondHeader]``, and ``[PropCondFooter]`` is inserted at the respective places in the generated code.

.. _variables:conditional-compilation:

.. mpg-paragraph:: Conditional compilation.

Giving an option ``Ifdef`` in the general section followed by some C++-preprocessor identifier ``IDENT`` wraps the entire generated code in preprocessor directives as follows:

.. mpg-code:: snippet:v:sec:v:varimp:add:code:2
   :direct:

By this, the Gecode kernel can be compiled with or without a particular variable type without being forced to reconfigure the Gecode kernel, see also :ref:`sec:v:all:conf`.

.. _par:v:varimp:dispose:

.. mpg-paragraph:: Explicitly disposing variable implementations.

Our example variables are entirely space-allocated and do not require external memory or other resources. However, for some variable types, the variable implementation might use external resources or memory that is not space-allocated and must explicitly be freed.

For an example, suppose the integer interval variables had been implemented by using arbitrary precision integers for the lower and upper bound and that these bounds must explicitly be freed.

By specifying in the general section

.. code-block:: console

   Dispose: true

and implementing in the variable implementation class a ``dispose(Space& home)`` member function, all variable implementations are disposed by calling their ``dispose()`` functions. The variable implementations are disposed when their home space is deleted.

Additionally, an object must be created that controls the disposal of variable implementations. Assume that our example integer variables used external memory and that its specification file contains

.. code-block:: console

   Dispose: true

and that ``MPG::IntVarImp`` implements a ``dispose()`` function. Then, your program must create a variable implementation disposer as follows:

.. mpg-code:: snippet:v:par:v:varimp:dispose:code:1
   :direct:

The ``disposer`` object must be initialized before the first variable using ``MPG::IntVarImp`` is created.

.. _variables:reserving-bits:

.. mpg-paragraph:: Reserving bits.

A limited number of bits :math:`b` can be reserved within each variable implementation by specifying in the general section

.. code-block:: console

   Bits: $b$

Then, the variable implementation can get a reference to a value of type ``unsigned int`` by calling the member function ``bits()`` where the least :math:`b` bits can be used freely. However, the maximal number of subscriptions (both propagators and advisors) for that variable implementation type is reduced from :math:`2^{31}-1` to :math:`2^{31-b}-1`. Furthermore, any attempt to use more than the specified number of bits will crash Gecode in a truly spectacular fashion!

.. _variables:specification-file-template:

.. mpg-paragraph:: Specification file template.

The specification template contains all possible specification options to assist in defining your own variable types.

.. _chap:v:var:

Variables and variable arrays
=============================

This chapter describes how variables can be programmed from variable implementations and how variable arrays and variable argument arrays can be programmed. The chapter uses integer interval variables as introduced in :ref:`chap:v:started` together with their implementations as defined in :ref:`chap:v:varimp` as its running example.

.. _variables:overview-3:

.. mpg-paragraph:: Overview.

How integer interval variables are implemented is detailed in :ref:`sec:v:var:var`. Variable arrays and variable argument arrays are discussed in :ref:`sec:v:var:array`.

.. _sec:v:var:var:

Variables
---------


.. _fig:v:var:var:

.. mpg-figure:: Variable programmed from a variable implementation
   :name: mpg-variable-figure-7

   .. mpg-code:: int.hh:var:variable

As a variable is just a read-only interface to a variable implementation, its implementation is straightforward. The definition of integer variables is shown in :ref:`fig:v:var:var`. The copy constructor uses the member function ``varimp()`` that returns the pointer to the variable’s variable implementation. Note that every variable must have a constructor that takes a pointer to the corresponding variable implementation as argument.

Note that within the class ``IntVar``, a pointer to the corresponding variable implementation is available as protected member ``x`` (see :ref:`tip:p:views:using` for information on ``using``).

One also must define an output operator ``<<`` for a variable as shown in :ref:`fig:v:var:var`.

It is important to remember that variables are defined in the namespace ``MPG``. This is in contrast to variable implementations, which are defined in the namespace ``MPG::Int``.

.. _variables:variable-creation:

.. mpg-paragraph:: Variable creation.

Creating a new variable is done with the following constructor that creates a new variable implementation as follows:

.. mpg-code:: int.hh:var:variable creation

Note that the constructor ensures the invariants for the lower and upper bound of a variable as discussed in :ref:`sec:v:varimp:design` by possibly throwing exceptions.

.. _variables:access-operations-2:

.. mpg-paragraph:: Access operations.

In addition to constructors, variables typically implement the same access operations as their corresponding variable implementation:

.. mpg-code:: int.hh:var:access operations

.. _variables:additional-inherited-member-functions-2:

.. mpg-paragraph:: Additional inherited member functions.


.. _fig:v:var:inherited:

.. mpg-figure:: Summary of member functions predefined by variables
   :name: mpg-variable-figure-8

   .. list-table::
      :header-rows: 0
      :widths: 28 32 40

      * - **access operations**
        -
        -
      * -
        - ``varimp()``
        - returns pointer to variable implementation
      * -
        - ``assigned()``
        - whether variable is assigned
      * -
        - ``degree()``
        - returns degree (number of subscriptions)
      * -
        - ``afc()``
        - returns accumulated failure count
      * - **update during cloning**
        -
        -
      * -
        - ``update()``
        - updates variable during cloning

In addition to the constructor and member functions defined by our variables, several other member functions are typically just inherited and are defined by the class :api:`VarImpVar`. The most important inherited member functions are summarized in :ref:`fig:v:var:inherited`. For an explanation of degree and accumulated failure count, see :ref:`sec:m:branch:shared`.

.. _sec:v:var:array:

Variable arrays and variable argument arrays
--------------------------------------------

Defining variable arrays and variable argument arrays (see also :ref:`sec:m:integer:proper`) requires the implementation of the arrays proper together with some traits. The traits classes for variable arrays and variable argument arrays ensure that Gecode-provided functionality for arrays can be used with the newly defined arrays.

.. _variables:array-traits:

.. mpg-paragraph:: Array traits.


.. _fig:v:var:traits:

.. mpg-figure:: Array traits for variable arrays
   :name: mpg-variable-figure-9

   .. mpg-code:: int.hh:array traits

The definition of the array traits classes is shown in :ref:`fig:v:var:traits`. The definition is done in two steps. The first step provides forward declarations of the array types ``IntVarArgs`` and ``IntVarArray`` in the namespace ``MPG`` (because that is where these arrays will be defined).

The second step requires to define traits for these two array types. The trait classes must be defined in the namespace ``Gecode``. For each array type, two traits classes are needed: one for the base class (for example, ``Gecode::VarArray<MPG::IntVar>``) and one for the class to be implemented (for example, ``MPG::IntVarArray``). The definitions for the array type and its base class must be identical and follow the examples shown in :ref:`fig:v:var:traits`.

.. _variables:variable-arrays:

.. mpg-paragraph:: Variable arrays.


.. _fig:v:var:array:

.. mpg-figure:: Variable arrays
   :name: mpg-variable-figure-10

   .. mpg-code:: int.hh:variable arrays

The implementation of variable arrays and variable argument arrays typically only require the implementation of various constructors when inheriting from the base classes :api:`VarArray` and :api:`VarArgArray`. The minimal set of constructors such that the arrays are compatible to arrays as used by Gecode is shown in :ref:`fig:v:var:array`.

.. _chap:v:view:

Views
=====

This chapter describes how views as needed for programming propagators and branchers can be programmed. The chapter uses integer interval variables as introduced in :ref:`chap:v:started` together with their implementations as defined in :ref:`chap:v:varimp` as its running example.

.. _variables:overview-4:

.. mpg-paragraph:: Overview.

:ref:`sec:v:view:types` provides an overview of the different types of views available in Gecode. The remaining sections provide examples for each different view type: :ref:`sec:v:view:varview` shows how an integer view ``IntView`` is constructed as a variable implementation view; :ref:`sec:v:view:const` shows how a constant integer view ``ConstIntView`` is programmed as a constant view; :ref:`sec:v:view:derived` shows how a minus view ``MinusView`` and an offset view ``OffsetView`` are programmed as derived views.

.. _sec:v:view:types:

View types
----------

Gecode provides three different types of views:

- *Variable implementation views*: a variable implementation view is nothing but a direct interface to a variable implementation. A variable implementation view must inherit from :api:`VarImpView`. The class :api:`VarImpView` is parametric with respect to a variable and *not a variable implementation* (as one might expect). This is due to the fact that the type of the variable implementation can be obtained automatically from the type of a variable. Making a variable implementation view parametric with respect to a variable type has the advantage that information on both the variable type and variable implementation type become available.

- *Constant views*: a constant view must implement the same interface and must perform the same operations as some assigned variable implementation view. This particular variable implementation view is called the *corresponding* variable implementation view. A constant view must inherit from :api:`ConstView` which is parametric with respect to the corresponding variable implementation view.

- *Derived views*: a derived view is a view that is implemented in terms of some other view (all view types are possible: variable implementation, constant, and derived). The view from which the derived view is derived, is called the *base* view. A derived view must inherit from :api:`DerivedView` which is parametric with respect to the base view.

.. _variables:predefined-member-functions:

.. mpg-paragraph:: Predefined member functions.


.. _fig:v:view:predefined:

.. mpg-figure:: Summary of member functions predefined by views
   :name: mpg-variable-figure-11

   .. list-table::
      :header-rows: 0
      :widths: 28 32 40

      * - **access operations**
        -
        -
      * -
        - ``varimp()``
        - returns pointer to variable implementation
      * -
        - ``assigned()``
        - whether variable is assigned
      * -
        - ``degree()``
        - returns degree (number of subscriptions)
      * -
        - ``afc()``
        - returns accumulated failure count
      * - **subscriptions**
        -
        -
      * -
        - ``subscribe()``
        - subscribe propagator/advisor
      * -
        - ``cancel()``
        - cancel propagator/advisor
      * - **scheduling support**
        -
        -
      * -
        - ``schedule()``
        - schedule propagator
      * -
        - ``reschedule()``
        - re-schedule propagator
      * - **modification event deltas**
        -
        -
      * -
        - ``me()``
        - extract modification event
      * -
        - ``med()``
        - construct modification event delta
      * - **delta information access**
        -
        -
      * -
        - ``modevent()``
        - return modification event from delta
      * - **update during cloning**
        -
        -
      * -
        - ``update()``
        - updates view during cloning

The classes :api:`VarImpView`, :api:`ConstView`, and :api:`DerivedView` define already many member functions that simplify the implementation of new views. The most important predefined member functions are summarized in :ref:`fig:v:view:predefined`.

Note that the ``varimp()`` function for a constant view or for a view derived from a constant view returns ``NULL``, as no variable implementation exists.

.. _variables:view-test-functions:

.. mpg-paragraph:: View test functions.

There are three different functions predefined for views:

- The function ``shared(x,y)`` returns ``true``, if both views ``x`` and ``y`` share a common variable implementation (see :ref:`par:p:views:sameshared`). Typically, the definition of ``shared()`` does not need to be overloaded for newly defined views.

- The operator ``x==y`` returns ``true``, if both views ``x`` and ``y`` are identical (see :ref:`par:p:views:sameshared`). For constant views and derived views, the definition of ``operator ==()`` must be overloaded for newly defined views (see :ref:`sec:v:view:const` and :ref:`sec:v:view:offset` for examples). The operator ``x!=y`` is analogous.

- The operator ``x<y`` returns ``true``, if ``x`` comes before ``y`` in some arbitrary total and strict order for ordering views. The function is mainly used for sorting arrays of views into some order (in particular for detecting duplicate views). For constant views and derived views, the definition of ``operator <()`` must be overloaded for newly defined views (see :ref:`sec:v:view:const` and :ref:`sec:v:view:offset` for examples).

.. _variables:output-operator:

.. mpg-paragraph:: Output operator.

For every view also an output operator ``<<`` must be defined. We sketch this only for integer views in :ref:`sec:v:view:varview`, for all other views the definition is analogous.

.. _sec:v:view:varview:

Variable implementation views: integer view
-------------------------------------------


.. _fig:v:view:int:

.. mpg-figure:: Integer view
   :name: mpg-variable-figure-12

   .. mpg-code:: int.hh:integer view

:ref:`fig:v:view:int` shows the definition of the class ``IntView`` for integer views from the class :api:`VarImpView` for variable implementation views. Please remember that a variable implementation view is parametric with respect to a variable type (``IntVar`` in our example, such that ``IntView`` uses the same variable implementation type ``IntVarImp`` as ``IntVar`` does).

Similar to variables obtained from variable implementations, a variable implementation view has a protected member ``x`` that is a pointer to its variable implementation (see :ref:`tip:p:views:using` for information on ``using``). A variable implementation view must implement at least the shown constructors such that it can be initialized both from the corresponding variable type and from the corresponding variable implementation type.

The remaining implementation tasks for variable implementation views are straightforward: all operations that are specific to a variable type (in our case, specific to integer interval variables) must be implemented. The implementation is straightforward as only the corresponding operations of the variable implementation are invoked:

- The access operations must be implemented:

  .. mpg-code:: int.hh:intview:access operations

- The modification operations must be implemented:

  .. mpg-code:: int.hh:intview:modification operations

- Finally, the operations for accessing delta information must be implemented:

  .. mpg-code:: int.hh:intview:delta information

.. _sec:v:view:const:

Constant views: constant integer view
-------------------------------------


.. _fig:v:view:const:

.. mpg-figure:: Constant integer view
   :name: mpg-variable-figure-13

   .. mpg-code:: int.hh:constant integer view

:ref:`fig:v:view:const` shows the implementation of a constant integer view with ``IntView`` as the corresponding variable implementation view. A constant integer view ``ConstIntView`` stores an integer value ``x`` and must implement all variable-specific operations that are implemented by the corresponding ``IntView`` class (as shown in :ref:`fig:v:view:const`).

Slightly less obvious is the implementation of operations that access delta information. While these operations must be implemented such that constant integer views can be used instead of integer views, they will never be executed (by definition, a constant view can never change). Hence we use the macro ``GECODE_NEVER`` (see :ref:`tip:b:started:never`) to clarify that the delta information operations are never executed:

.. mpg-code:: int.hh:constintview:delta information

.. _variables:update-during-cloning:

.. mpg-paragraph:: Update during cloning.

The definition of the ``update()`` member function of :api:`ConstView` does not take care of the integer value ``x``. Hence we need to provide a new ``update()`` function that updates the value of ``x`` as follows:

.. mpg-code:: int.hh:constintview:update during cloning

.. _variables:view-tests:

.. mpg-paragraph:: View tests.

Also the default definitions of the view test operators ``==``, ``!=``, and ``<`` for constant views do not take the integer value ``x`` of the view into account. Overloaded versions for constant integer views are as follows:

.. mpg-code:: int.hh:constintview:view tests

.. _sec:v:view:derived:

Derived views
-------------

This section exemplifies two different derived views: minus views and offset views. Why these views are useful and what their semantics is can be seen in :ref:`sec:p:views:int:minus` for minus views and in :ref:`sec:p:views:int:offset` for offset views.

.. _sec:v:view:minus:

Minus views
~~~~~~~~~~~


.. _fig:v:view:minus:

.. mpg-figure:: Minus view
   :name: mpg-variable-figure-14

   .. mpg-code:: int.hh:minus view

:ref:`fig:v:view:minus` shows that a minus view is derived from an integer view ``IntView``. The protected member ``x`` refers to the base view, that is the integer view from which the minus view is derived (see :ref:`tip:p:views:using` for information on ``using``).

.. _variables:access-operations-3:

.. mpg-paragraph:: Access operations.

The access operations are as to be expected for a minus view. That is, the lower bound of the derived view is the negation of the upper bound of the base view:

.. mpg-code:: int.hh:minusview:access operations

.. _variables:modification-operations-2:

.. mpg-paragraph:: Modification operations.


.. _fig:v:view:minusmepc:

.. mpg-figure:: Negation of modification events and propagation conditions
   :name: mpg-variable-figure-15

   .. mpg-code:: int.hh:minusview:modification events and propagation conditions

The modification operations are slightly more involved than the access operations as they return a modification event. If the modification event of the base view is ``ME_INT_MAX`` (the upper bound of the base view has changed), then the modification event for the derived view must be ``ME_INT_MIN`` (the lower bound of the derived view has changed).

:ref:`fig:v:view:minusmepc` shows functions ``minusme()`` and ``minuspc()`` that return the negation of modification events and propagation conditions (to be discussed later).

Using the function ``minusme``, the modification operations can be defined as follows:

.. mpg-code:: int.hh:minusview:modification operations

.. _variables:accessing-delta-information:

.. mpg-paragraph:: Accessing delta information.

Accessing delta information must also take into account that the modification event stored in a delta must be converted with ``minusme()``. Also the other operations for accessing delta information must be adopted accordingly:

.. mpg-code:: int.hh:minusview:delta information

.. _variables:additional-operations:

.. mpg-paragraph:: Additional operations.

Any operation that is concerned with either modification events or propagation conditions must be implemented to take the switch between lower bound and upper bound into account. These operations include the operations for handling subscriptions of propagators (the function ``minuspc()`` is defined analogously to ``minusme()`` in :ref:`fig:v:view:minusmepc`):

.. mpg-code:: int.hh:minusview:subscriptions

Note that the operations that subscribe advisors must be re-implemented even though they are unchanged. This is due to inheritance in C++: as the overloaded functions for propagators are redefined, also the functions for advisors are considered to be redefined.

Likewise, the member function for re-escheduling must also be implemented following the same idea:

.. mpg-code:: int.hh:minusview:re-scheduling

The remaining operations to be implemented are support operations:

.. mpg-code:: int.hh:minusview:support operations

.. _sec:v:view:offset:

Offset views
~~~~~~~~~~~~


.. _fig:v:view:offset:

.. mpg-figure:: Offset view
   :name: mpg-variable-figure-16

   .. mpg-code:: int.hh:offset view

:ref:`fig:v:view:offset` shows that an offset view is derived from an integer view ``IntView`` and stores an additional integer value ``c`` for the offset. The protected member ``x`` refers to the base view, that is the integer view from which the offset view is derived (see :ref:`tip:p:views:using` for information on ``using``). The access, modification, and delta information access operations of an offset view are as to be expected.

The ``update()`` function must also update the integer offset ``c`` as follows:

.. mpg-code:: int.hh:offsetview:update during cloning

Likewise, the view test operators ``==``, ``!=`` and ``<`` must take into account the integer offset ``c``:

.. mpg-code:: int.hh:offsetview:view tests

.. _chap:v:branch:

Variable-value branchings
=========================

This chapter explains how to program common variable-value branchings using the abstractions provided by Gecode.

.. _variables:overview-5:

.. mpg-paragraph:: Overview.

:ref:`sec:v:branch:type` explains which simple types must be defined for variable-value branchings. How functions for variable selection and value selection are implemented is demonstrated in :ref:`sec:v:branch:varval`. :ref:`sec:v:branch:viewsel` shows how a function that creates an object for selecting views during branching is implemented. How functions for selecting values and committing to these values are implemented is shown in :ref:`sec:v:branch:valcommit`. This section also explains how to add support for no-goods to a variable-value brancher. How the actual branchings are implemented is then detailed in :ref:`sec:v:branch:branch`.


.. _fig:v:branch:structure:

.. mpg-figure:: Part of header file concerned with branching
   :name: mpg-variable-figure-17

   .. mpg-code:: int.hh:branching

This structure is reflected in the part of the ``int.hh`` header file that is concerned with branching (shown in :ref:`fig:v:branch:structure`).

.. _sec:v:branch:type:

Type, traits, action, and more
------------------------------

The way how a variable-value branching works can to some extent be controlled by the user by functions:

- A branching filter function defines which variables are actually considered for branching, see :ref:`sec:m:branch:filter`.

- A variable value print function defines how to print information on alternatives of variable value branchers during search. Variable value branchers print some default information even if the user does not supply a variable value print function, see :ref:`sec:m:branch:print`.

- A branch merit function can define which variable is selected for branching, see :ref:`sec:m:branch:uservar`.

- A branch value function selects a value that is used for branching, see :ref:`sec:m:branch:userval`.

- A branch commit function constrains a variable with respect to a value passed as argument, see :ref:`sec:m:branch:userval`.

In the following type definitions, the type ``IntVar`` of the argument ``x``, the return type ``int`` of the branch value function of type ``IntBranchVal``, and the type ``int`` of the argument ``n`` is dependent on our integer interval variables (they are of type ``IntVar`` and they take values of type ``int``).

The remaining argument and return types are required by Gecode and are as follows:

.. mpg-code:: int.hh:branch function types

These function type definitions must be connected to the variable type ``IntVar`` by means of a traits-class of type ``BranchTraits``. As the functionality for variable-value branching is defined in the ``Gecode`` namespace, the trait class must also be defined there:

.. mpg-code:: int.hh:branch traits

The last remaining definitions specializes AFC, action, and CHB information for integer interval variables by defining a class ``IntAFC`` as follows:

.. mpg-code:: int.hh:variable AFC

a class ``IntAction`` as follows:

.. mpg-code:: int.hh:variable action

and a class ``IntCHB`` as follows:

.. mpg-code:: int.hh:variable CHB

The actual implementations are omitted as they contain nothing more than the type specialization and creation of view arrays in the initializing constructor and the ``init()`` function.

.. _sec:v:branch:varval:

Variable and value selection
----------------------------

An important part of the interface of the branching is support for specifying how variables and values are selected for branching. This is implemented by a set of variable and value selection functions that are used for specification. These functions return objects that are then used for creating the appropriate branchers. In this section we are not interested in describing a complete set of variable and value selection functions but in a set that demonstrates the features of variable-value branchings.

.. _variables:variable-selection:

.. mpg-paragraph:: Variable selection.

The variable selection functions we are considering here are defined as follows (their names and what they do coincides with the variable selection functions for normal integer variables in Gecode, see :ref:`sec:m:branch:int`):

.. mpg-code:: int.hh:variable selection functions

All but ``INT_VAR_NONE()`` take arguments: unsurprisingly, a random number generator must be passed to ``INT_VAR_RND()`` and a double as decay-factor or an integer action object to ``INT_VAR_ACTION_MAX()``. Both ``INT_VAR_NONE()`` and ``INT_VAR_RND()`` are special in that they are not useful for tie-breaking. All other variable selection functions take an optional argument of type ``BranchTbl`` as a branch tie-breaking limit function (we will abbreviate this here as tbl-function), see :ref:`sec:m:branch:tbl` for a description of tie-breaking and tbl-functions.


.. _fig:v:branch:intvarbranch:

.. mpg-figure:: Variable selection class
   :name: mpg-variable-figure-18

   .. mpg-code:: int.hh:variable selection class

The implementation of the variable selection functions is simple: each function returns an object of class ``IntVarBranch`` that stores all necessary information required for creating the appropriate brancher. As an example of an implementation consider the following, the other functions are similar:

.. mpg-code:: int.hh:variable selection function implementation

The implementation of the class ``IntVarBranch`` is shown in :ref:`fig:v:branch:intvarbranch`. It defines an enumeration of all variable selection strategies and a set of constructors for the different types of arguments the variable selection functions take. The ``select()`` function returns a value of the enumeration type that is stored by the object. All other information is handled by the base class :api:`VarBranch` that is parametric with respect to the variable type.

The class must also implement an ``expand()`` member function. It checks whether ``INT_VAR_ACTION_MAX()`` had been called just with a decay-factor instead of an integer action object. In this case it creates an integer action object and stores it as follows:

.. mpg-code:: int.hh:expand action

.. _variables:value-selection:

.. mpg-paragraph:: Value selection.

Value selection functions are implemented similarly to variable selection functions. They return an object of class ``IntValBranch`` (inheriting from the template base class :api:`ValBranch`) which stores the necessary information for creating the appropriate brancher. We are considering the following value selection functions as examples:

.. mpg-code:: int.hh:value selection functions

Note that the last argument of the value selection function ``INT_VAL()`` is optional, the default behavior will be defined in :ref:`sec:v:branch:valcommit`.

.. _sec:v:branch:viewsel:

View selection creation
-----------------------


.. _fig:v:branch:viewsel:

.. mpg-figure:: View selection creation function
   :name: mpg-variable-figure-19

   .. mpg-code:: int.hh:view selection creation function

The view selection creation function shown in :ref:`fig:v:branch:viewsel` takes an object ``ivb`` of class ``IntVarBranch`` as an argument, creates an object of class :api:`ViewSel` and returns a pointer to it. The object ``ivb`` is a specification of which object should be returned. The returned object is used to select views during brancher execution.

Selection of the first unassigned view (corresponding to ``SEL_NONE``, that is, the object ``ivb`` has been created by calling the function ``INT_VAR_NONE()``) is implemented by the Gecode-defined class :api:`ViewSelNone`. Also random view selection is provided by Gecode through the class :api:`ViewSelRnd`. Both classes are parametric with respect to a view type.

.. _variables:view-selection-with-tbl-function:

.. mpg-paragraph:: View selection with tbl-function.

The other strategies for view selection exist in two variants: one variant that uses a tbl-function and one variant that does not. In case a tbl-function has been supplied as additional argument to one of the variable selection functions, the following creates the appropriate object for view selection:

.. mpg-code:: int.hh:view selection with tbl-function

Depending on how the view is to be selected, different objects are created. An object of class :api:`ViewSelMaxTbl` selects a variable with maximal merit (for the definition of merit, see :ref:`sec:m:branch:int`), whereas an object of class :api:`ViewSelMinTbl` selects a variable with minimal merit. Objects of both classes take a tbl-function during selection into account. Both classes expect a class as template argument that computes the actual merit value for a given view.

The classes :api:`MeritFunction`, :api:`MeritDegree`, and :api:`MeritAction` are defined by Gecode and are parametric with respect to the actual view type.


.. _fig:v:branch:meritsize:

.. mpg-figure:: Size merit class
   :name: mpg-variable-figure-20

   .. mpg-code:: int.hh:size merit class

Selecting a view with minimal size is specific to our integer interval variables and views. The implementation of the class ``MeritSize`` inherits from :api:`MeritBase` and is shown in :ref:`fig:v:branch:meritsize`.

The class :api:`MeritBase` is parametric with respect to the view type (``IntView`` in our case) and the type of the merit value (``unsigned int`` in our case). The constructors are as to be expected and the call operator must return the merit value of type ``unsigned int`` (the same as the second template argument to :api:`MeritBase`) of the view ``x`` (``i`` refers to the position of the view ``x`` in the array of views used in the brancher).

In case the merit class uses members that must be deallocated when the home-space is deleted, the merit class must redefine the member functions ``notice()`` and ``dispose()``, for example by:

.. mpg-code:: snippet:v:fig:v:branch:meritsize:code:1
   :direct:

.. _variables:view-selection-without-tbl-function:

.. mpg-paragraph:: View selection without tbl-function.

Implementing view selection without a tbl-function is analogous, the only difference is that the classes :api:`ViewSelMax` (instead of :api:`ViewSelMaxTbl`) and :api:`ViewSelMin` (instead of :api:`ViewSelMinTbl`) must be used:

.. mpg-code:: int.hh:view selection without tbl-function

.. _sec:v:branch:valcommit:

Value selection and commit creation
-----------------------------------


.. _fig:v:branch:valcommit:

.. mpg-figure:: Value selection and commit creation function
   :name: mpg-variable-figure-21

   .. mpg-code:: int.hh:value selection and commit creation function

The value selection and commit creation function is very similar to the variable selection creation function from the previous section. It creates and returns an object that performs value selection and value commit during branching depending on a specification object of class ``IntValBranch``.

The function is shown in :ref:`fig:v:branch:valcommit` and returns an object of class :api:`ValSelCommitBase`. Again, this class is parametric with respect to the view type (``IntView``) and the value type (``int``). Depending on which value selection strategy is defined by the argument ``ivb``, a corresponding object of class :api:`ValSelCommit` is created.

The class :api:`ValSelCommit` is parametric with respect to a value selection class and a value commit class (to be discussed below). The classes ``ValSelMin``, ``ValSelRnd``, and ``ValCommitLq`` are specific to integer interval variables and views and are discussed below.

.. _variables:value-selection-classes:

.. mpg-paragraph:: Value selection classes.

A value selection class must inherit from the class :api:`ValSel` which again is parametric with respect to the view and value type. The constructors (one for creation and for cloning) are exactly the same as for merit classes discussed in the previous section.

Also, similar to merit classes, a value selection class can redefine the member functions ``notice()`` and ``dispose()`` if explicit disposal is required when the home-space is deleted.

In addition, the classes must define a member function ``val()`` that returns a value for a given view ``x`` as follows (``i`` again is the position in the view array):

.. mpg-code:: int.hh:value selection classes

.. _variables:value-commit-classes:

.. mpg-paragraph:: Value commit classes.

For our integer interval variables and views we need a single value commit class only (how many classes are needed depends of course on which value selection strategies are provided). A value commit class must inherit from the parametric class :api:`ValCommit` and must implement one constructor for creation and one for cloning. In addition, it must define a ``commit()`` function, an ``ngl()`` function (to be discussed later), and a default ``print()`` function. The ``commit()`` function returns a modification event and takes the number of the alternative ``a``, a view ``x``, its position ``i``, and a value ``n`` as arguments. The ``print()`` function takes an output stream ``o`` as additional argument:

.. mpg-code:: int.hh:value commit class

.. _variables:no-good-support:

.. mpg-paragraph:: No-good support.

The value commit class must also implement a function ``ngl()`` that returns a no-good literal for an alternative. The idea is exactly the same as described in :ref:`sec:b:advanced:nogoods`, the only difference is that the ``ngl()`` function here gets a view and a value as arguments rather than a choice.

The ``ngl()`` function of the ``ValCommitLq`` class returns a no-good literal implemented by the class ``LqNGL`` for the first alternative and ``NULL`` for the second alternative as follows:

.. mpg-code:: int.hh:no-good literal creation

The no-good literal class ``LqNGL`` used by the ``ngl()`` function is defined as follows:

.. mpg-code:: int.hh:no-good literal class

It inherits from the template class :api:`ViewValNGL`, which expects a view type, a value type, and a propagation condition as argument. The definition of the constructors, the ``copy()`` function, the ``status()`` function, and the ``prune()`` function are exactly as discussed in :ref:`sec:b:advanced:nogoods`. The remaining functions for disposal and subscription are pre-defined by :api:`ViewValNGL`.

.. _variables:user-defined-value-selection-and-commit-functions:

.. mpg-paragraph:: User-defined value selection and commit functions.

For the value selection function ``INT_VAL(v,c)`` for a user-defined value selection function ``v`` and a user-defined commit function ``c`` it is possible to leave out ``c``, as it has been declared as an optional argument. When the argument is not provided, ``c`` is equal to ``nullptr``. This is taken into account as follows:

.. mpg-code:: int.hh:user-defined value selection and commit functions

The classes :api:`ValSelFunction` and :api:`ValCommitFunction` are defined by Gecode and are parametric with respect to a view. They use the functions as specified by the object ``ivb``.

.. _sec:v:branch:branch:

Branchings
----------

Implementing the actual ``branch()`` functions with and without tie-breaking is straightforward. They only have to create a brancher that uses the view selection creation function ``viewsel()`` from :ref:`sec:v:branch:viewsel` and the value selection and commit creation function ``valselcommit()`` from :ref:`fig:v:branch:valcommit`.

.. _variables:branching-without-tie-breaking:

.. mpg-paragraph:: Branching without tie-breaking.


.. _fig:v:branch:branch:

.. mpg-figure:: Branch function
   :name: mpg-variable-figure-22

   .. mpg-code:: int.hh:branch function

The ``branch()`` function is shown in :ref:`fig:v:branch:branch`. It creates an array of integer views ``IntView``, expands a possibly missing integer action object, creates an array with a single view selector object returned by the function ``viewsel()`` as discussed in :ref:`sec:v:branch:viewsel` and posts the view-value brancher of class :api:`ViewValBrancher` through the function ``postviewvalbrancher()``. The function is parametric, where the arguments describe the following:

#. The view type which is ``IntView`` in our case.

#. The number of view selection objects to be used during view selection. As we are not using tie-breaking, the number is ``1`` and corresponds to the number of elements in the array ``vs``.

#. The value type which is ``int`` in our case.

#. The number of alternatives that should be created during branching, which is ``2`` in our example [2]_.

.. _variables:branching-with-tie-breaking:

.. mpg-paragraph:: Branching with tie-breaking.


.. _fig:v:branch:branchtb:

.. mpg-figure:: Branch function with tie-breaking
   :name: mpg-variable-figure-23

   .. mpg-code:: int.hh:branch function with tie-breaking

The ``branch()`` function with tie-breaking is shown in :ref:`fig:v:branch:branchtb`. It takes an object ``vars`` of class :api:`TieBreak` as argument, where ``vars.a`` is the first variable selection strategy of class ``IntVarBranch``, ``vars.b`` the second, ``vars.c`` the third, and ``vars.d`` the forth and last to be used during tie-breaking.

Before creating the brancher, the variable selection strategies are normalized. As mentioned earlier, there should be no tie-breaking after the variable selection strategies ``INT_VAR_NONE()`` and ``INT_VAR_RND()`` (corresponding to ``SEL_NONE`` and ``SEL_RND``, respectively). The normalization first tries to normalize ``var.b``, then ``var.c`` and finally ``var.d`` as follows (the ``var.c`` and ``var.d`` case is analogous and hence omitted):

.. mpg-code:: int.hh:normalizing tie-breaking

After normalization, the ``branch()`` function shown in :ref:`fig:v:branch:branchtb` posts a brancher of class :api:`ViewValBrancher` with the appropriate number of view selection objects by calling the ``postviewvalbrancher()`` function. In :ref:`fig:v:branch:branchtb`, only the cases for two and three objects is shown, the other cases are analogous.

.. _chap:v:trace:

Variable tracing support
========================

This chapter shows how to add variable tracing support for a new variable type.


.. _fig:v:trace:tracing:

.. mpg-figure:: Part of header file concerned with tracing
   :name: mpg-variable-figure-24

   .. mpg-code:: int.hh:tracing

.. _variables:overview-6:

.. mpg-paragraph:: Overview.

:ref:`fig:v:trace:tracing` shows the part of the header file concerned with tracing. Trace views are used to save the state of a view’s domain after it has been modified by a prune-event and trace deltas are used to compute the values that have been removed by a prune-event. They are discussed in :ref:`sec:v:trace:views`. How tracers and trace recorders are instantiated is described in :ref:`sec:v:trace:tracer`. Finally, :ref:`sec:v:trace:post` describes how to actually post trace recorders through trace post functions.

.. _sec:v:trace:views:

Trace views and deltas
----------------------

Trace views are used to save the domain of a view after a prune-event has occurred. When another prune event occurs, a trace view is used to compute a trace delta between the previously recorded domain and the current domain of the view. For our integer interval variables, the integer trace view stores the lower and upper bound as follows:

.. mpg-code:: int.hh:trace view

The trace view is initialized by its constructor. It does not have to implement all functions of a view, only an ``update()`` function is needed and two functions that are specific to trace views.

.. _variables:prune-function:

.. mpg-paragraph:: Prune function.

The prune function is executed when a prune-event has occurred. Here the integer view ``x`` is the view after the prune event and the modification delta ``d`` contains information about the prune-event. For integer interval variables it is sufficient to update the lower and upper bound of the trace view as follows:

.. mpg-code:: int.hh:prune function

.. _variables:slack-function:

.. mpg-paragraph:: Slack function.

For all other event types, the slack of a variable must be available, computed by a ``slack()`` function as follows:

.. mpg-code:: int.hh:slack function

Here the slack is defined as the values that are still to be removed and to avoid numeric overflow for several views the return type is defined as ``unsigned long long int``.

.. _variables:trace-delta:

.. mpg-paragraph:: Trace delta.

The trace delta provides information about which values have been removed by a prune-event. For integer interval variables, the trace delta is defined and computed as follows:

.. mpg-code:: int.hh:trace delta

Note as integer interval variables are so simple, it would also have been possible to not store the lower and upper bound in the trace view but to extract the information from the modification delta ``d`` directly.

.. _sec:v:trace:tracer:

Tracers and trace recorders
---------------------------

For tracers and trace recorders it is sufficient to define some traits for tracing as follows:

.. mpg-code:: int.hh:trace traits

Here the type names are self explanatory.

An integer tracer and trace recorder can be obtained by simple type definitions as follows:

.. mpg-code:: int.hh:tracer and trace recorder

If desired, one can also define a standard tracer for convenience:

.. mpg-code:: int.hh:standard tracer

The implementation is not detailed here, see :ref:`sec:m:group:tracers` for details.

.. _sec:v:trace:post:

Trace post functions
--------------------

The trace post function is like a constraint post function: it creates integer views for the variables and then posts the trace recorder as follows:

.. mpg-code:: int.hh:trace post function

For convenience, the following post function allows to post a trace recorder without specifying any trace filter:

.. mpg-code:: int.hh:trace post function convenience

.. _chap:v:all:

Putting everything together
===========================

This chapter explains how to build Gecode with integer interval variables,
use them in a model, and test their implementation.

.. _variables:overview-7:

.. mpg-paragraph:: Overview.

:ref:`sec:v:all:golomb` sketches an example script together with implementations of constraints and branchings using integer interval variables. The following section, :ref:`sec:v:all:conf`, shows how Gecode can be configured to use integer interval variables and how to compile and run the example script. :ref:`sec:v:all:testing` tests domain updates and cloning with Gecode's test runner.

.. important::

   Please make sure to carefully read :ref:`sec:m:started:compile`, before reading any further in this chapter!

.. _sec:v:all:golomb:

Golomb rulers à la integer interval variables
---------------------------------------------


.. _fig:v:all:golomb:

.. mpg-figure:: Golomb rulers à la integer interval variables
   :name: mpg-variable-figure-25

   .. mpg-code:: putting everything together

:ref:`fig:v:all:golomb` shows the top-level structure of a single C++-file containing a script together with all required implementations of post functions, propagators, and branchers. The example script implements a naive version of the Golomb ruler model presented in :ref:`chap:c:golomb`. The reason to package everything into a single C++-file is to simplify compiling the example.

The implementations of the constraints in the C++-file are carefully constructed to exercise most of the functionality described in the previous chapters in this part. In particular, some constraints have a slightly non-standard implementation to exercise all views presented in :ref:`chap:v:view`.

.. _sec:v:all:conf:

Configuring and compiling Gecode
--------------------------------

The following steps configure and compile Gecode with integer interval variables:

#. Start a POSIX shell (for example, Bash or Zsh).

#. Create a new directory, say ``MPG``, and make it the current directory:

   .. mpg-code:: snippet:v:sec:v:all:conf:cmd:1
      :direct:
      :small:

#. Download the Gecode |release| source release from the Gecode GitHub releases page. Unpack it in the current directory and rename the extracted source directory to ``gecode``.

#. If you have not yet done so, download and copy all files required for integer interval variables and the example into the current directory:

   - The header file ``int.hh`` containing the implementation of integer interval variables.

   - The variable implementation specification file :download:`int.vis </examples/int.vis>`.

   - The file ``putting-everything-together.cpp`` from the previous section.

#. Configure Gecode to incorporate integer interval variables and install into a local prefix:

   .. code-block:: sh

      cmake -S gecode -B gecode/build \
        -DCMAKE_BUILD_TYPE=Release \
        -DGECODE_WITH_VIS="$PWD/int.vis" \
        -DCMAKE_INSTALL_PREFIX="$PWD/gecode-install"

   After this step, Gecode has been configured to incorporate the generated definitions as described by the specification file ``int.vis``. Add any other CMake options required by your build environment.

#. Compile and install Gecode:

   .. code-block:: sh

      cmake --build gecode/build --config Release
      cmake --install gecode/build --config Release

#. Add the local installation's executables to the search path:

   .. code-block:: sh

      export PATH="$PWD/gecode-install/bin:$PATH"

   On systems that require it, also add the installation's ``lib`` directory to the library search path; for example, on Linux:

   .. code-block:: sh

      export LD_LIBRARY_PATH="$PWD/gecode-install/lib${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"

Finally, compile, link, and run ``putting-everything-together.cpp`` as described in :ref:`sec:m:started:run`, using ``gecode-install`` as the installation prefix. Its ``include`` and ``lib`` directories contain the headers and libraries for the custom variable implementation.

.. _sec:v:all:testing:

Testing integer interval variables
----------------------------------

A variable implementation must update its domain, report the appropriate
modification events, and copy its state when its space is cloned. The test in
:numref:`program:v:all:int-test` checks these operations for our integer
interval variables. It uses the core test class ``Test::Base``. The integer
propagator test class from :ref:`chap:p:testing` operates on Gecode's
predefined integer variables and cannot be used directly with ``MPG::IntVar``.

The class ``IntTestSpace`` contains one variable with initial domain
:math:`[-3,3]`. Its copy constructor updates the variable to refer to its
copied implementation. The class ``IntTest`` implements ``run()``, which returns
``true`` if all checks succeed and ``false`` otherwise. Constructing the global
object ``int_test`` registers the test under the name ``MPG::Int::Bounds``.

.. raw:: latex

   \Needspace{12\baselineskip}

.. mpg-code:: integer interval variable test
   :caption: Testing domain updates and cloning of an integer interval variable
   :name: program:v:all:int-test
   :download: int-test.cpp

The test modifies the variable through an ``IntView``. An upper bound of
``3`` leaves the domain unchanged and must return ``ME_INT_NONE``. Raising
the lower bound to ``-1`` must return ``ME_INT_MIN``; lowering the upper bound
to ``1`` must return ``ME_INT_MAX``. Each check also inspects the resulting
domain, since a correct modification event alone does not establish that the
domain was updated correctly.

Before cloning, the test calls ``status()`` to make the space stable. There
are no branchers, so this call reports ``SS_SOLVED`` even though the variable
is unassigned. The clone must contain the same domain, :math:`[-1,1]`.
Assigning its variable to ``1`` must return ``ME_INT_VAL`` and leave the
original variable unchanged. Finally, restricting the clone's upper bound to
``0`` must return ``ME_INT_FAILED``. The caller then fails the cloned space
explicitly, just as a propagator must report failure after a failed domain
operation. The original space must remain usable.

The messages written to ``Test::olog`` identify the stage that failed. They
are displayed with the runner's ``-log`` option. This test covers domain
updates and clone independence; testing subscriptions also requires
propagators that subscribe to the different propagation conditions.

.. _sec:v:all:testing-build:

.. mpg-paragraph:: Building and running the test.

Use the Gecode installation built with ``int.vis`` in
:ref:`sec:v:all:conf`, with ``BUILD_TESTING=ON``. The test library and the test
program must use the same generated kernel definitions. Linking against a
Gecode installation built without ``int.vis`` is not sufficient.

Place :download:`int.hh <../../examples/src/int.hh>`, ``int-test.cpp``, and
the CMake project in :numref:`program:v:all:int-test-cmake` in one directory.
The target ``Gecode::gecodetest`` supplies the core runner; no helper for a
predefined variable type is needed.

.. mpg-code:: integer interval test CMake project
   :caption: CMake project for the integer interval variable test
   :name: program:v:all:int-test-cmake
   :download: CMakeLists.txt

Configure and run the test with the custom Gecode installation:

.. code-block:: console

   cmake -S . -B build -DCMAKE_PREFIX_PATH=/path/to/gecode-install
   cmake --build build
   ./build/int-test -iter 1 -threads 1 -log

.. [1]
   If you ever exceed this limit, please let us know. Adding more bits is easy, even though we do not expect that to happen anytime soon.

.. [2]
   By choosing the value ``1`` here, one can obtain branchers that perform value assignment similar to the ``assign()`` function described in :ref:`sec:m:branch:assign`.
