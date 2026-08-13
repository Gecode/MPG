.. _chap:m:group:


.. _modeling:m-group:groups-and-tracing:

Groups and tracing
==================

Groups are a means to control certain execution aspects of propagators and branchers. Tracing can be used for tracing constraint propagation on variables as well as the general execution of propagators and branchers. Groups are ultimately linked to tracing, as the generated traces can be filtered according to group membership.

.. _modeling:m-group:overview:

.. rubric:: Overview.

:ref:`sec:m:group:prop` explains groups of propagators, whereas :ref:`sec:m:group:branch` explains groups of branchers. Tracing variables is explained in :ref:`sec:m:group:vartrace` and general tracing in :ref:`sec:m:group:trace`. :ref:`sec:m:group:vartracers` shows how variable tracers and :ref:`sec:m:group:tracers` shows how general tracers (the objects that process trace information) can be programmed.

.. _sec:m:group:prop:


.. _modeling:m-group:propagator-groups:

Propagator groups
-----------------

Each propagator belongs to exactly one *propagator group* of type `PropagatorGroup <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1PropagatorGroup.html>`__. When a propagator is created, it is added to a group. Group membership of a propagator remains stable during copying of spaces.

.. _modeling:m-group:adding-propagators-to-groups:

.. rubric:: Adding propagators to groups.

The following code creates a propagator group ``pg``:

.. mpg-code:: snippet:m-group:sec:m:group:prop:code:1
   :direct:


A propagator can be added to the group ``pg`` by passing the group as additional information adjoined to the ``home`` information when the propagator is posted. For example, when assuming that ``home`` refers to a space of type ``Space&``, then

.. mpg-code:: snippet:m-group:sec:m:group:prop:code:2
   :direct:


adds all propagators created by the constraint post function ``distinct()`` to the propagator group ``pg``. Equivalently, one can also use:

.. mpg-code:: snippet:m-group:sec:m:group:prop:code:3
   :direct:


If no propagator group is specified when a propagator is created, then the propagator is added to the default propagator group ``PropagatorGroup::def``.

.. _modeling:m-group:moving-propagators-between-groups:

.. rubric:: Moving propagators between groups.

Propagators can be moved from one group to another. For example, if ``pga`` and ``pgb`` are propagator groups, then

.. mpg-code:: snippet:m-group:sec:m:group:prop:code:4
   :direct:


moves all propagators from group ``pgb`` into group ``pga``. An individual propagator ``p`` (of type ``Propagator&``) can also be moved into a propagator group ``pg`` by

.. mpg-code:: snippet:m-group:sec:m:group:prop:code:5
   :direct:


A propagator ``p`` can also be moved by giving its identity ``p.id()``. For example, the following is equivalent to the previous example:

.. mpg-code:: snippet:m-group:sec:m:group:prop:code:6
   :direct:


If no propagator with a given id exists, an exception of type `UnknownPropagator <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1UnknownPropagator.html>`__ is thrown.

In order to remove a propagator from its group or all propagators of a group from their group, one can use the default group. For example, if ``pg`` is a propagator group, all of its propagators are removed from ``pg`` by

.. mpg-code:: snippet:m-group:sec:m:group:prop:code:7
   :direct:


Move operations can be concatenated as they return their group. For example, if ``pg`` is a propagator group and ``p`` and ``q`` are two propagators, then

.. mpg-code:: snippet:m-group:sec:m:group:prop:code:8
   :direct:


moves both ``p`` and ``q`` to ``pg``.

.. _modeling:m-group:operations-on-propagator-groups:

.. rubric:: Operations on propagator groups.

The number of propagators in a group can be computed by the ``size()`` member function. The following expression:

.. mpg-code:: snippet:m-group:sec:m:group:prop:code:9
   :direct:


evaluates to the number of propagators in the group ``pg``. Each group has a unique identifier of type ``unsigned int`` which can be accessed by:

.. mpg-code:: snippet:m-group:sec:m:group:prop:code:10
   :direct:


One can iterate over all propagators in a group. For example,

.. mpg-code:: snippet:m-group:sec:m:group:prop:code:11
   :direct:


prints the unique identifier of each propagator contained in group ``pg``. A propagator also provides access to the group it belongs to, assume that ``p`` is of type ``Propagator&``, then

.. mpg-code:: snippet:m-group:sec:m:group:prop:code:12
   :direct:


evaluates to the group ``p`` belongs to.

The propagators of a group can be disabled and enabled. By

.. mpg-code:: snippet:m-group:sec:m:group:prop:code:13
   :direct:


all propagators in ``pg`` are disabled in that they are not any longer performing any propagation (for more details on disabling and enabling propagators, see also :ref:`par:p:started:disable`). Similarly, propagators can be enabled by

.. mpg-code:: snippet:m-group:sec:m:group:prop:code:14
   :direct:


By default, enabling a disabled propagator will schedule the propagator for execution if necessary. Hence, next time the ``status()`` function of the propagator’s home space is executed, the propagator will be executed again. It is also possible to enable propagators in a group without scheduling them by:

.. mpg-code:: snippet:m-group:sec:m:group:prop:code:15
   :direct:


All propagators in a group can be killed by

.. mpg-code:: snippet:m-group:sec:m:group:prop:code:16
   :direct:


.. _modeling:m-group:groups-for-all-propagators:

.. rubric:: Groups for all propagators.

For convenience, there is one special propagator group ``PropagatorGroup::all`` which refers to all propagators in a space (one can think of it as the union of all propagator groups). For example,

.. mpg-code:: snippet:m-group:sec:m:group:prop:code:17
   :direct:


evaluates to the number of all propagators in the space ``home``.

.. _sec:m:group:branch:


.. _modeling:m-group:brancher-groups:

Brancher groups
---------------

Brancher groups contain branchers and each brancher belongs to exactly one brancher group of type `BrancherGroup <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1BrancherGroup.html>`__. Brancher groups are similar to propagator groups as described in the previous section:

- A brancher group ``bg`` is created as follows:

  .. mpg-code:: snippet:m-group:sec:m:group:branch:code:1
     :direct:
     :small:

- A brancher is added to the group ``bg`` by passing the group as additional information adjoined to the ``home`` information when the propagator is posted. For example, the brancher created by

  .. mpg-code:: snippet:m-group:sec:m:group:branch:code:2
     :direct:
     :small:

  adds the newly created brancher created to the brancher group ``bg``. Equivalently, one can also write ``bg(home)`` instead of ``home(bg)``.

- Brancher groups provide ``move()`` functions for moving branchers into brancher groups that are analogous to the ``move()`` functions for propagator groups.

- If no brancher group is specified, branchers are added to the default group ``BrancherGroup::def``.

- The number of branchers in a group can be computed by the ``size()`` member function. Each group has a unique identifier of type ``unsigned int`` which can be accessed by ``bg.id()``.

- One can iterate over all branchers in a group by using the iterator class `Branchers <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1Branchers.html>`__.

- Each brancher provides access to the group it belongs to, assume that ``b`` is of type ``Brancher&``, then

  .. mpg-code:: snippet:m-group:sec:m:group:branch:code:3
     :direct:
     :small:

  evaluates to the group ``b`` belongs to.

- All branchers in a group can be killed by

  .. mpg-code:: snippet:m-group:sec:m:group:branch:code:4
     :direct:
     :small:

- There is one special brancher group ``BrancherGroup::all`` which refers to all branchers in a space.

.. _sec:m:group:vartrace:


.. _modeling:m-group:variable-tracing:

Variable tracing
----------------

Gecode offers support to trace constraint propagation on an array of variables. Variable tracing distinguishes two components: a *variable trace recorder* that records information about relevant events during constraint propagation and a *variable tracer* that processes the recorded trace information. A very simple variable tracer instance would just print some textual information about recorded trace events. In fact, Gecode offers default tracers for each variable type that comes with Gecode that just print to an output stream of type ``std::ostream``.

.. _modeling:m-group:creating-a-variable-trace-recorder:

Creating a variable trace recorder
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A variable trace recorder can be created by calling the overloaded function ``trace()`` together with an array of variables. For example,

.. mpg-code:: snippet:m-group:sec:m:group:vartrace:code:1
   :direct:


creates a variable trace recorder for an array of variables ``x``. Here, ``x`` can be an array of integer, Boolean, set, or float variables.

The variable trace recorder records the following events:

- A single *init-event* providing some information about the variables for which the variable trace recorder will record information.

- Each time the domain of a variable changes, a *prune-event* is recorded. The variable trace recorder provides information about which variable has been changed, how the variable has been changed, and on behalf of which entity (a propagator, a brancher, or a constraint post function performing pruning outside a propagator or brancher) the variable has been changed.

- A *fixpoint-event* is recorded when the space containing the variable trace recorder reaches a fixpoint, triggered by the execution of the space’s ``status()`` function.

- A *failure-event* is recorded when the space containing the variable trace recorder fails, triggered by the execution of the space’s ``status()`` function.

- A *done-event* that is recorded when all of the variable trace recorder’s variables have been assigned and hence no further recording is needed. Note that this event can occur only once per space, however when using tracing during search the event might occur several times for different spaces.

The information that is recorded for each event depends on the variable trace recorder’s variable type.

.. _modeling:m-group:default-variable-tracers:

Default variable tracers
~~~~~~~~~~~~~~~~~~~~~~~~

The following paragraphs explain the information printed by the default variable tracer for a given variable type.

.. _modeling:m-group:integer-and-boolean-variables:

.. rubric:: Integer and Boolean variables.

.. mpg-code:: snippet:m-group:sec:m:group:vartrace:cmd:1
   :name: fig:m:group:varsmm
   :caption: Abridged output for variable tracing Send More Money
   :direct:


Running the `SEND+MORE=MONEY puzzle <https://www.gecode.dev/doc/6.4.0/reference/money_8cpp.html>`__ (see :ref:`chap:m:started` and :ref:`chap:m:comfy` for the Send More Money problem) with the commandline option ``-trace all`` (trace events to be recorded can be specified on the command line, see :ref:`sec:m:driver:options`), the default variable tracer for integer variables prints information about all trace events to ``std::cerr``. An excerpt of the information printed is shown in :numref:`fig:m:group:varsmm` where the variable trace recorder has been posted with

.. mpg-code:: snippet:m-group:fig:m:group:varsmm:code:1
   :direct:


where ``le`` is the array of eight variables used in Send More Money.

.. mpg-tip:: Enabling tracing with a commandline option

   As mentioned above, the Gecode driver offers also support for tracing. If ``opt`` is an object of class `Options <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1Options.html>`__, then adding the following code


   .. mpg-code:: snippet:m-group:fig:m:group:varsmm:code:2
      :direct:

   enables variable tracing if the ``-trace`` commandline option is used. The option takes ``all`` as value for tracing all events as well as a comma-separated list of ``init``, ``prune``, ``fix``, ``fail``, and ``done`` for the respective event types. Also general tracing can be controlled by this commandline option, see :ref:`sec:m:group:trace`.

The output for each event starts with the information

.. mpg-code:: snippet:m-group:fig:m:group:varsmm:cmd:1
   :direct:


signaling that integer variables are being traced. After that, the type of event is shown (``init``, ``prune``, ``fix`` for fixpoint, ``fail`` for failure, or ``done``). This is followed by information about the identifier of the variable trace recorder (a variable trace recorder is in fact a propagator and hence has a unique identifier, see :ref:`sec:m:group:traceonoff`). If the variable trace recorder belongs to a propagator group different from the default propagator group, also the identifier of the respective propagator group is printed.

The information for each event type is as follows:

- For an init-event, the total slack of all variables is shown where the slack of a variable is the number of values that must be removed before the variable becomes assigned to a single value. This information serves as a measure of how much propagation is still to be done.

- For a prune-event, it is printed which variable has been pruned where the variable is identified by its position in the variable array of the variable trace recorder (for example, the first prune event in :numref:`fig:m:group:varsmm` shows ``[0]`` as the variable at position ``0`` has been pruned).

  Next, the current domain of the variable is printed (that is, ``[1..9]``) and that the value ``0`` has been pruned (that is, ``- {0}``).

  This is followed by information which entity has pruned the variable: a constraint post function (as is the case for the first two prune-events in :numref:`fig:m:group:varsmm`), a propagator (as is the case for the third prune-event in :numref:`fig:m:group:varsmm`), a brancher (as is the case for the last prune-event in :numref:`fig:m:group:varsmm`), or unknown. In case the prune-event has been caused by a propagator or brancher, their identifiers are shown. In case the propagator or brancher belong to a group different from the respective default group, also the group’s identifier is shown. This is also true if the event has been caused by a constraint post function where some group information had been passed to the constraint post function.

- For a fixpoint-event, the current slack and its change since the last fixpoint are shown.

- For a failure-event, the current slack and its change since the last fixpoint are shown.

- For a done-event, the current slack is shown (unsurprisingly, the slack is :math:`0\%` as all variables have been assigned).

The information printed by the default variable tracer for Boolean variables is exactly the same as for integer variables.

Defining custom variable tracers is straightforward, this is explained in :ref:`sec:m:group:vartracers`.

.. _modeling:m-group:set-variables:

.. rubric:: Set variables.

The information printed for init-, fixpoint-, failure-, and done-events for set variables is analogous to the information for integer variables. The slack of a set variable here is defined as the number of values that can be still included in or excluded from the set variable (that is, it corresponds to ``x.unknownSize()`` where ``x`` is a set variable of type `SetVar <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1SetVar.html>`__).

For a prune-event, it is shown which values have been included in the set and which values have been excluded from the set. For example in

.. mpg-code:: snippet:m-group:fig:m:group:varsmm:cmd:2
   :direct:


the value ``6`` has been included into the variable and no value has been excluded whereas in

.. mpg-code:: snippet:m-group:fig:m:group:varsmm:cmd:3
   :direct:


the values ``4``, ``5``, and ``6`` have been excluded. You can try the `Generating Hamming codes <https://www.gecode.dev/doc/6.4.0/reference/hamming_8cpp.html>`__ example that supports tracing.

.. _modeling:m-group:float-variables:

.. rubric:: Float variables.

For float variables, the slack is defined as the width of the variable domain. The information printed for the events is analogous to the information for integer variables, where for a prune-event the interval containing the pruned values is printed.

For an example that supports tracing for float variables, you might want to try the `Folium of Descartes <https://www.gecode.dev/doc/6.4.0/reference/descartes-folium_8cpp.html>`__ example.

.. _sec:m:group:filters:


.. _modeling:m-group:using-trace-filters:

Using trace filters
~~~~~~~~~~~~~~~~~~~

The amount of prune-events that are generated during tracing can be prohibitive and often one is only interested in events generated by a subset of the propagators, branchers, or post functions. Therefore, one can pass as an optional argument a *trace filter* of type `TraceFilter <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1TraceFilter.html>`__ defined by a *trace filter expression* (or *TFE*) of type `TFE <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1TFE.html>`__ to a trace recorder.

.. container:: samepage

   Assume that ``pga`` and ``pgb`` are two propagator groups and ``bg`` is a brancher group. Then

   .. mpg-code:: snippet:m-group:sec:m:group:filters:code:1
      :direct:

traces only prune-events that have been caused by a propagator or a post function associated with the group ``pga``. Prune-events caused by propagators or post functions from groups ``pga`` and ``pgb`` are traced by

.. mpg-code:: snippet:m-group:sec:m:group:filters:code:2
   :direct:


Likewise, prune-events caused by branchers in the group ``bg`` or by propagators or post functions not associated with ``pga`` are traced by

.. mpg-code:: snippet:m-group:sec:m:group:filters:code:3
   :direct:


The following only traces post functions associated with ``pga`` and propagators included in ``pgb``:

.. mpg-code:: snippet:m-group:sec:m:group:filters:code:4
   :direct:


In summary, TFEs can be constructed from the unary and binary operators ``+`` and ``-`` and the functions ``post()`` and ``propagator()`` taking a propagator group as argument.

.. _modeling:m-group:selecting-the-events-to-trace:

Selecting the events to trace
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When creating a trace recorder, it can be defined which events should be recorded by providing an additional argument. For example

.. mpg-code:: snippet:m-group:sec:m:group:filters:code:5
   :direct:


only records prune-events, whereas

.. mpg-code:: snippet:m-group:sec:m:group:filters:code:6
   :direct:


records prune- and fixpoint-events. All events (the default) are recorded by

.. mpg-code:: snippet:m-group:sec:m:group:filters:code:7
   :direct:


.. _sec:m:group:traceonoff:


.. _modeling:m-group:enabling-and-disabling-variable-trace-recorders:

Enabling and disabling variable trace recorders
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A variable trace recorder is implemented by a propagator, hence it can be controlled by propagator groups. In particular, a variable trace recorder can be disabled and enabled.

For example, by creating a propagator group ``t`` by

.. mpg-code:: snippet:m-group:sec:m:group:traceonoff:code:1
   :direct:


.. container:: samepage

   and then creating a variable trace recorder so that it belongs to the group ``t`` by

   .. mpg-code:: snippet:m-group:sec:m:group:traceonoff:code:2
      :direct:

the variable trace recorder can be controlled through the group ``t``.

.. container:: samepage

   For example, the variable trace recorder can be disabled by

   .. mpg-code:: snippet:m-group:sec:m:group:traceonoff:code:3
      :direct:

and the later enabled by

.. mpg-code:: snippet:m-group:sec:m:group:traceonoff:code:4
   :direct:


One can easily add several variable trace recorders (either for different variables or different variable types) to the same propagator group and jointly control all variable trace recorders in that group.

.. _sec:m:group:trace:


.. _modeling:m-group:general-tracing:

General tracing
---------------

In addition to variable tracing, Gecode offers support to trace the execution of propagators and branchers. Like with variable tracing, *general tracing* distinguishes two components: a *general trace recorder* (or, *trace recorder* for short) that records information about relevant events during constraint propagation as well as branching, and a *general tracer* (or, *tracer* for short) that processes the recorded trace information.

.. _modeling:m-group:creating-a-general-trace-recorder:

Creating a general trace recorder
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A trace recorder can be created by calling the overloaded function ``trace()``. For example,

.. mpg-code:: snippet:m-group:sec:m:group:trace:code:1
   :direct:


creates a trace recorder.

A general trace recorder records the following events:

- Each time a constraint is posted, a *post-event* is recorded. The recorder provides information whether posting has lead to failure, the posted constraint is subsumed (that is, no propagator has been posted for the constraint), or one or several propagators have been created.

- Each time a propagator is executed, a *propagate-event* is recorded. The recorder provides information about which propagator has been executed and what the status of the execution is (that is, whether the propagator computed a fixpoint, did not compute a fixpoint, became subsumed, or resulted in failure).

- Each time a commit operation on a brancher is executed, a *commit-event* is recorded.

.. _modeling:m-group:default-general-tracers:

Default general tracers
~~~~~~~~~~~~~~~~~~~~~~~

The following paragraphs explain the information printed by the default general tracer.

.. mpg-code:: snippet:m-group:sec:m:group:trace:cmd:1
   :name: fig:m:group:smm
   :caption: Abridged output for general tracing of Send More Money
   :direct:


Running the `SEND+MORE=MONEY puzzle <https://www.gecode.dev/doc/6.4.0/reference/money_8cpp.html>`__ (see :ref:`chap:m:started` and :ref:`chap:m:comfy` for the Send More Money problem) with the commandline option ``-trace propagate,commit`` (trace events to be recorded can be specified on the command line, see :ref:`sec:m:driver:options`), the default tracer prints information about all trace events to ``std::cerr``. An excerpt of the information printed is shown in :numref:`fig:m:group:smm` where the trace recorder has been posted with

.. mpg-code:: snippet:m-group:fig:m:group:smm:code:1
   :direct:


The output for each event starts with the information

.. mpg-code:: snippet:m-group:fig:m:group:smm:cmd:1
   :direct:


After that, the type of event is shown (``propagate``, ``choice``, or ``post``).

The information for each event type is as follows:

- For a propagate-event, the propagator identifier is printed, potentially followed by the propagator group. This is followed by status information.

- For a choice-event, the brancher identifier is printed, potentially followed by the brancher group. This is followed by information which alternative the brancher has been committed to, see also :ref:`sec:m:branch:print`.

- For a post-event, potentially the propagator group is printed. This is followed by status information.

Defining custom general tracers is straightforward, this is explained in :ref:`sec:m:group:tracers`.

.. _modeling:m-group:additional-features:

.. rubric:: Additional features.

Like for variable tracers, general tracers can also be controlled by trace filters (see :ref:`sec:m:group:filters`) and can be disabled (see :ref:`sec:m:group:traceonoff`).

When creating a trace recorder, it can be defined which events should be recorded by providing an additional argument. For example,

.. mpg-code:: snippet:m-group:fig:m:group:smm:code:2
   :direct:


only records propagate-events, whereas

.. mpg-code:: snippet:m-group:fig:m:group:smm:code:3
   :direct:


only records choice-events. All events (the default) are recorded by

.. mpg-code:: snippet:m-group:fig:m:group:smm:code:4
   :direct:


.. _sec:m:group:vartracers:


.. _modeling:m-group:programming-variable-tracers:

Programming variable tracers
----------------------------

Programming variable tracers is straightforward and is done by inheriting from a class that depends on the variable type and implements one virtual member function for each trace event type. These virtual member functions are called when an event of that type is being recorded and the event type has been selected for tracing. For integer variables, the tracer class to inherit from is `IntTracer <https://www.gecode.dev/doc/6.4.0/reference/group__TaskIntTrace.html>`__, for Boolean variables `BoolTracer <https://www.gecode.dev/doc/6.4.0/reference/group__TaskIntTrace.html>`__, for set variables `SetTracer <https://www.gecode.dev/doc/6.4.0/reference/group__TaskSetTrace.html>`__, and for float variables `FloatTracer <https://www.gecode.dev/doc/6.4.0/reference/group__TaskFloatTrace.html>`__.

In the following we are discussing variable tracers for integer and Boolean variables in some detail in :ref:`sec:m:group:tracers:int` and summarize variable tracers for set and float variables in :ref:`sec:m:group:tracers:set` and :ref:`sec:m:group:tracers:float` respectively.

.. _sec:m:group:tracers:int:


.. _modeling:m-group:tracers-for-integer-and-boolean-variables:

Tracers for integer and Boolean variables
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. mpg-code:: integer variable tracer
   :name: fig:m:group:tracer
   :caption: An integer variable tracer printing to std::cout


The example tracer we discuss is implemented by a class ``StdCoutIntTracer``, prints trace information to ``std::cout``, and is shown in :numref:`fig:m:group:tracer`. The ``init()``, ``fail()``, and ``done()`` member functions are not discussed as they are similar to the member function ``fix()`` which is discussed below.

.. _modeling:m-group:printing-propagator-information:

.. rubric:: Printing propagator information.

The example tracer prints information about propagators and branchers using overloaded static member functions ``ids()`` (for identifiers). Printing information about propagators is implemented as follows:

.. mpg-code:: integer variable tracer:print propagator information


The function always prints the identifier ``p.id()`` of the propagator ``p``. If ``p`` is in a propagator group ``p.group()`` which is different from the default propagator group (tested by the ``in()`` function of a propagator group), then also the group identifier is printed. The overloaded function ``ids()`` for branchers is identical and hence only shown in abbreviation in :numref:`fig:m:group:tracer`.

.. _modeling:m-group:printing-variable-trace-information:

.. rubric:: Printing variable trace information.

The member function ``prune()`` receives as an argument a reference to an object of class `ViewTraceInfo <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1ViewTraceInfo.html>`__ providing information about which entity triggered the corresponding prune-event. The following function illustrates the information provided by an object of class `ViewTraceInfo <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1ViewTraceInfo.html>`__.

.. mpg-code:: integer variable tracer:print view trace information


.. _modeling:m-group:printing-prune-events:

.. rubric:: Printing prune-events.

A ``prune()`` member function takes arguments that provide information about *what* is being pruned (this is given by the integer ``i`` as the position of the variable in the array passed to the ``trace()`` function), *how* the variable has been pruned (this is given by the argument ``d`` of class `IntTraceDelta <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1IntTraceDelta.html>`__), and by *whom* (this is given by the class `ViewTraceInfo <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1ViewTraceInfo.html>`__, which has been discussed in the previous paragraph). It also gets access to the trace recorder of type `IntTraceRecorder <https://www.gecode.dev/doc/6.4.0/reference/group__TaskIntTrace.html>`__.

.. container:: samepage

   The example ``prune()`` function prints information as follows:

   .. mpg-code:: integer variable tracer:prune event

As can be seen, the argument ``d`` of type `IntTraceDelta <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1IntTraceDelta.html>`__ is a range iterator with the same interface as described in :ref:`sec:m:int:iter` and iterates of the integer ranges that correspond to the values that have been removed. The trace recorder ``t`` provides access to its variables through the array operator ``[]``.

.. _modeling:m-group:printing-fixpoint-events:

.. rubric:: Printing fixpoint-events.

The ``fix()`` function also receives an argument of type `IntTraceRecorder <https://www.gecode.dev/doc/6.4.0/reference/group__TaskIntTrace.html>`__ as shown here:

.. mpg-code:: integer variable tracer:fixpoint event


The integer trace recorder ``t`` provides access to *slack* information about all of its variables through a ``slack()`` member function.

For integer variables, the slack is the number of values that still need to be pruned before all variables become assigned and is of type ``unsigned long long int``. Here, the function ``initial()`` of ``t.slack()`` returns the initial slack when the trace recorder has been created, ``previous()`` returns the slack at the previous fixpoint (or, the initial slack if it is the first fixpoint), and ``current()`` returns the current slack.

Note that the slack information is only updated when a fixpoint-, init-, or done-event occurs.

.. _tip:m:group:name:

.. mpg-tip:: Naming propagators, branchers, variables, and groups

   Note that all entities relevant for tracing carry a *unique* and *global* identity: propagators, branchers, propagator groups, and brancher groups all provide a function ``id()`` that returns a unique identifier for that entity of type ``unsigned int``. The identity is global in that it does not change when a space is being cloned during search. Hence naming entities through a hash table mapping identities to user-defined names is straightforward.


.. _modeling:m-group:variable-tracers-for-boolean-variables:

.. rubric:: Variable tracers for Boolean variables.

Variable tracers for Boolean variables are exactly like variable tracers for integer variables: a Boolean variable trace recorder is of type `BoolTraceRecorder <https://www.gecode.dev/doc/6.4.0/reference/group__TaskIntTrace.html>`__, the trace delta is also a range iterator of class `BoolTraceDelta <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1BoolTraceDelta.html>`__, and the slack is defined as for integer variables and is also of type ``unsigned long long int``.

.. _modeling:m-group:memory-and-concurrency-properties-of-tracers:

.. rubric:: Memory and concurrency properties of tracers.

There is no automatic memory management for tracers, the user is responsible for creating and deleting tracers. A tracer can be used across several threads where it is ensured that the execution of a trace function is synchronized in that at most one thread executes any trace function at any given time.

.. _sec:m:group:tracers:set:


.. _modeling:m-group:variable-tracers-for-set-variables:

Variable tracers for set variables
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The types and classes for set variable tracers are as follows:

- The variable trace recorder is of type `SetTraceRecorder <https://www.gecode.dev/doc/6.4.0/reference/group__TaskSetTrace.html>`__.

- The trace delta information is of class `SetTraceDelta <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1SetTraceDelta.html>`__ which implements two member functions ``glb()`` (for greatest lower bound) and ``lub()`` (for least upper bound) which return range iterators. The function ``glb()`` returns a range iterator of class `SetTraceDelta::Glb <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1SetTraceDelta_1_1Glb.html>`__ which iterates over the values that have been included into a set variable by a prune-event. The function ``lub()`` returns a range iterator of class `SetTraceDelta::Lub <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1SetTraceDelta_1_1Lub.html>`__ which iterates over the values that have been excluded from a set variable by a prune-event.

- The slack of a set variable is defined as the number of values where membership has not been decided and is of type ``unsigned long long int``.

.. _sec:m:group:tracers:float:


.. _modeling:m-group:variable-tracers-for-float-variables:

Variable tracers for float variables
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The types and classes for float variable tracers are as follows:

- The variable trace recorder is of type `FloatTraceRecorder <https://www.gecode.dev/doc/6.4.0/reference/group__TaskFloatTrace.html>`__.

- The trace delta information is of class `FloatTraceDelta <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1FloatTraceDelta.html>`__ which implements two member functions ``min()`` and ``max()`` defining the interval of float values that have been pruned.

- The slack of a float variable is defined as its width and is of type `FloatNum <https://www.gecode.dev/doc/6.4.0/reference/group__TaskModelFloatVars.html>`__.

.. _sec:m:group:tracers:


.. _modeling:m-group:programming-general-tracers:

Programming general tracers
---------------------------

Programming general tracers is straightforward and is done by inheriting from the class `Tracer <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1Tracer.html>`__ that implements one virtual member function for each trace event type. These virtual member functions are called when an event of that type is being recorded and the event type has been selected for tracing.

.. mpg-code:: general tracer
   :name: fig:m:group:gtracer
   :caption: A general tracer printing to std::cout


The example tracer we discuss is implemented by a class ``StdCoutTracer``, prints trace information to ``std::cout``, and is shown in :numref:`fig:m:group:gtracer`.

The virtual member function ``commit()`` takes a space and an object ``cti`` of class `CommitTraceInfo <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1CommitTraceInfo.html>`__ as input. Information about the brancher, the choice, and the alternative to commit to can be accessed through the member functions of ``cti``.

The virtual member function ``post()`` takes a space and an object ``pti`` of class `PostTraceInfo <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1PostTraceInfo.html>`__ as input. Information about propagator group, status, and the number of posted propagators can be accessed through the member functions of ``pti``.

The virtual member function ``propagate()`` takes a space and an object ``pti`` of class `PropagateTraceInfo <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1PropagateTraceInfo.html>`__ as input. Information about the propagator and the status of propagation can be accessed through the member functions of ``pti``.

.. mpg-covered: caption:docs/src/chapters/modeling/m-group.tex.in:275:fig:m:group:varsmm
.. mpg-covered: tip:docs/src/chapters/modeling/m-group.tex.in:308:unlabeled-tip@docs/src/chapters/modeling/m-group.tex.in:308
.. mpg-covered: caption:docs/src/chapters/modeling/m-group.tex.in:556:fig:m:group:smm
.. mpg-covered: caption:docs/src/chapters/modeling/m-group.tex.in:658:fig:m:group:tracer
.. mpg-covered: literal-projection:docs/src/chapters/modeling/m-group.tex.in:659:integer variable tracer
.. mpg-covered: literal-projection:docs/src/chapters/modeling/m-group.tex.in:677:integer variable tracer:print propagator information
.. mpg-covered: literal-projection:docs/src/chapters/modeling/m-group.tex.in:695:integer variable tracer:print view trace information
.. mpg-covered: literal-projection:docs/src/chapters/modeling/m-group.tex.in:713:integer variable tracer:prune event
.. mpg-covered: literal-projection:docs/src/chapters/modeling/m-group.tex.in:728:integer variable tracer:fixpoint event
.. mpg-covered: caption:docs/src/chapters/modeling/m-group.tex.in:822:fig:m:group:gtracer
.. mpg-covered: literal-projection:docs/src/chapters/modeling/m-group.tex.in:823:general tracer
