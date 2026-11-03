.. _chap:m:open:

Open variable lists
===================

This chapter discusses *open variable lists*: sequences of variables whose
length is decided during search. A model with a fixed-size array must know the
number of decisions before search starts. For a plan of unknown length, this
means either solving once for each candidate length, or fixing an upper bound
and modeling which positions are in use. An open variable list also has an
upper bound, but constructs its positions only when propagation or search
requires them.

Gecode has always allowed variables and constraints to be added to a space
during search. An open variable list organizes this for a sequence. It
consists of the variables constructed so far and an integer variable for the
eventual length. A *transition callback* can create further variables and post
arbitrary constraints whenever a position is added. In addition, some
constraints have open overloads that are posted once for the whole list, and a
list brancher decides both the values and where the list ends.

.. mpg-paragraph:: Overview.

:ref:`sec:m:open:route` introduces :api:`OpenIntVarList` with a model that
uses open constraints only. :ref:`sec:m:open:plan` models a plan whose states
are created by a transition callback. These two sections belong to the basic
reading material. :ref:`sec:m:open:prefix` describes the operations for
growing and closing a list, :ref:`sec:m:open:branch` branching on lists, and
:ref:`sec:m:open:constraints` the constraints that follow growth.
:ref:`sec:m:open:copy` discusses cloning, other variable types, and the rules
for callbacks. The chapter builds on spaces and cloning from
:ref:`chap:m:started`, and on extensional constraints from
:ref:`sec:m:integer:extensional`. Branching is discussed in more detail in
:ref:`chap:m:branch`.

.. container:: convention

   Note that the same conventions hold as in :ref:`chap:m:int`.

.. _sec:m:open:route:

Routes of unknown length
------------------------

The graph in :numref:`program:m:open:route` has five nodes, numbered zero to
four. We want all routes from node zero to node four that visit each node at
most once. There are cycles in the graph, but a simple route can contain at
most five nodes. This gives a finite bound on the list length without
excluding any solution.

.. mpg-code:: open route model
   :caption: Simple routes with an open variable list
   :name: program:m:open:route
   :download: open-route.cpp

The member ``route`` contains the node variables in route order, including
the source and destination. Its constructor supplies their common domain
``IntSet(0,n-1)`` and a maximum length ``n``. It does not create any node
variables. The list has a separate integer variable ``route.length()`` for its
eventual length.

The automaton ``paths`` describes the graph. Its extra start state five
consumes the source node zero. The other transitions consume the destination
of a graph arc, and only state four is accepting. The open-list overload of
``extensional`` therefore constrains the route to start at zero, follow graph
arcs, and end at four. The ``distinct`` constraint excludes revisits. Both
constraints follow the list as it grows.

The automaton states correspond to the graph nodes, so the regular constraint
tracks the current node without any variables for it. The next section keeps
the state in variables instead.

.. _sec:m:open:plan:

Transition callbacks
--------------------

Suppose a robot at a workbench must fetch a packet from a shelf and deliver it
to the workbench. The shelf, the workbench, and a charger are connected in a
line, in that order. Each move uses one unit of charge, each charge action at
the charger adds one unit, and the battery holds five units. With an initial
charge of two units, a plan with four actions exists. With one unit, the robot
must visit the charger first, and the shortest plan has nine actions.

The state of the robot consists of its location, its charge, and the status
of the packet. The legal steps are given by a :api:`TupleSet`, where each tuple
consists of an action, the state before the action, and the state after it.

.. mpg-code:: open delivery steps
   :caption: The steps of the delivery robot
   :name: program:m:open:steps

The model in :numref:`program:m:open:plan` uses one open list for the actions
and three open lists for the states. State :math:`i` holds before action
:math:`i`, so the state lists are one position longer than the action list.
The constructor links the lengths and fixes the initial state, using ``get``
to construct the first position of each state list. The failure check is
needed because ``get`` does not construct a position when the space fails,
here for an initial charge larger than five.

.. mpg-code:: open delivery model
   :caption: A delivery plan with open lists
   :name: program:m:open:plan
   :download: open-delivery.cpp

Only the list ``actions`` has a transition callback. When action :math:`i` is
constructed, the callback calls ``step(i)``. This member function constructs
state :math:`i+1` and posts the extensional constraint for action :math:`i`
and the states before and after it.

.. mpg-code:: open delivery step
   :caption: Posting a step and the goal
   :name: program:m:open:step

The constraints posted by ``goal(i)`` allow the plan to end after :math:`i`
actions only if the packet has been delivered in state :math:`i`, and end the
plan as soon as it has been delivered. As steps and goals are posted only for
constructed positions, the model contains only the part of the plan that has
been constructed.

Propagation already constructs part of the plan before search starts. With an
initial charge of one unit, the packet cannot be delivered with fewer than
four actions. Hence, the root space has four actions and five states, and the
first action is restricted to moving to the shelf or to the charger.

The script minimizes ``actions.length()`` using branch-and-bound. The initial
charge is passed as the size argument:

.. code-block:: console

   ./open-delivery
   ./open-delivery 3

For an initial charge of one unit, the first solution is the plan with nine
actions. For three units, search finds plans with eleven, seven, and four
actions. Constructing a plan position by position does not by itself find a
shortest plan first, see :ref:`sec:m:open:branch`.

The callback is shared between clones. It therefore accesses the model
through the space passed to it instead of capturing ``this``; the rules for
callbacks are summarized in :ref:`sec:m:open:copy`.

.. mpg-paragraph:: States as automaton states.

As in the route example, the regular constraint can also encode the state as a
transition system. The location, the charge, and the status of the packet are
then encoded by the states of an automaton, and each tuple of the table
becomes a transition labeled by its action. A single open ``extensional``
constraint on ``actions`` then replaces the state lists and the transition
callback. Explicit state variables are required when there are too many states
to enumerate, for example for the boards in the fifteen-puzzle example that
comes with Gecode. That example also uses the heuristic search engines
discussed in :ref:`sec:m:search:heuristic`.

.. _sec:m:open:prefix:

The prefix and the eventual length
----------------------------------

``known_length()`` counts the positions that have been constructed. Their
variables can still be unassigned. Indexed access with ``x[i]`` is limited to
this prefix; it does not construct a new position.

The minimum of ``length()`` requires that many positions to exist.
Propagation constructs them, using the list's variable factory and transition
callback. Constructing a position can post constraints that require a longer
prefix. This continues until the required positions have been constructed or
the space fails.

.. mpg-paragraph:: Growing a list.

``materialize(home,n)`` requires at least ``n`` positions, and ``get(home,i)``
requires and returns the variable at position ``i``. Both restrict the
eventual length. After ``get``, check whether the space has failed before
using the returned variable; on failure the variable can be uninitialized. An
index at or beyond the maximum eventual length raises ``Int::OutOfLimits``.

``append(home,x)`` adds an existing variable belonging to the current space,
requires the length to include it, and calls the transition callback.
Appending the same unassigned variable twice throws ``Int::ArgumentSame``;
this also applies to variables returned by a factory. Equal assigned values
can occur at different positions, subject to the constraints on the list.

.. mpg-paragraph:: Closing a list.

``close(home)`` first constructs any positions required by the minimum length,
then assigns the eventual length to the number of constructed positions.
Closing determines the number of positions. It does not assign their
variables.

.. _sec:m:open:branch:

Choosing values and length
--------------------------

The open-list brancher selects among the constructed variables using ordinary
variable and value selectors. In the route example, ``INT_VAR_NONE()`` and
``INT_VAL_MIN()`` assign positions from left to right, trying smaller node
numbers first. Once these variables are assigned, the brancher first tries
closing the list. Its other alternative requires one more position and
continues selecting values. Propagation can require more than one new
position when the list grows.

.. mpg-paragraph:: Choosing the length first.

To choose the complete length first, post a brancher on ``x.length()`` before
the list brancher. Branchers run in posting order, so the length is assigned
and propagation constructs the required positions before the list brancher
selects their values. The route example supports both orders. Build the
downloaded source as described in :ref:`sec:m:started:run`, then run:

.. code-block:: console

   ./open-route
   ./open-route -branching length

Both searches find the same five routes. They use different search trees and
can return the routes in different orders. The default search constructs a
route incrementally; the second search tries the shorter lengths first. The
better order depends on the problem.

.. mpg-paragraph:: Selectors and filters.

Selectors and filters operate on the constructed prefix. Filter and print
callbacks receive the position in the list. Variables rejected by the filter
can remain unassigned when the list brancher finishes. Action and CHB
selection (see :ref:`sec:m:branch:action` and :ref:`sec:m:branch:chb`)
require the whole list to have been constructed when the brancher is posted;
otherwise posting throws ``Int::UnknownBranching``.

.. mpg-tip:: Bound the length of open lists

   Whenever the application permits it, give an open list a finite maximum
   length. Exploring long lists can be very expensive even if a few short
   solutions are easy to find. Positions that have not been constructed take
   no memory, but their domains do not take part in propagation either. A
   model with a fixed number of positions can therefore detect some failures
   earlier.

.. _sec:m:open:constraints:

Constraints that follow growth
------------------------------

An open list has its own constraint overloads. Passing the current prefix to a
constraint on a fixed array would constrain only the variables already
present; later positions would not be included. The open overloads are posted
once and include each position when it is constructed. They differ from their
fixed-array counterparts in how they treat positions that do not exist yet.

.. mpg-paragraph:: Regular constraints.

Regular constraints (``extensional`` with a :api:`DFA`) are available for
integer and Boolean lists. The complete sequence must be accepted by the
automaton when the list closes; intermediate prefixes need not be accepted
words. While the list is open, the constraint prunes the constructed variables
and removes values that require more further positions than the maximum
length allows. This filtering does not use the domains of positions not yet
constructed or holes in the length domain, and it does not directly prune the
length variable.

.. mpg-paragraph:: Distinct values.

``distinct`` removes an assigned value from the other positions, including
positions constructed later. It is value consistent; its propagation-level
argument does not select stronger filtering.

.. mpg-paragraph:: Relations and windows.

``rel`` constrains each pair of consecutive variables by a relation.
``sequence`` and ``sliding_sum`` constrain each complete window. A list
shorter than the window size has no complete windows and satisfies either
constraint. ``sequence`` filters each window separately; it does not provide
domain consistency across overlapping windows, and its propagation-level
argument is ignored. ``sliding_sum`` uses bounds propagation when its lower
and upper sum bounds differ. For equality, it supports bounds or domain
propagation; the default is domain propagation for windows of size at most two
and bounds propagation for larger windows.

.. mpg-paragraph:: Minimum and maximum.

For ``min`` and ``max``, bounds are enforced as positions appear. Once the
list closes, at least one position must equal the result. Closing an empty
list therefore fails. The result variable can also occur as a list element.

.. mpg-paragraph:: Value precedence.

For ``precede``, every occurrence of the later value requires an earlier
occurrence of its predecessor; neither value is required to occur. Its
propagation-level argument is ignored.

Propagator authors can follow growth through :api:`OpenViewList`, described
in :ref:`sec:p:views:open`.

.. _sec:m:open:copy:

Cloning and callbacks
---------------------

The copy constructor updates an open list just as it updates an ordinary
variable array. Handles referring to the same list in one space continue to
share a list in the clone, but the clone has its own mutable state. Growing or
closing one space's list does not change the other space.

.. mpg-code:: open route copy and output
   :caption: Cloning and printing the route
   :name: program:m:open:copy

The print function visits ``known_length()`` positions. In a solution,
branching has determined the length and assigned the variables, so this is
the complete route.

.. mpg-paragraph:: Other variable types.

:api:`OpenBoolVarList` supplies the corresponding factory for Boolean
variables. The generic :api:`OpenVarList` template also accepts a factory for
another variable type, such as ``SetVar`` or ``FloatVar``. Such a list shares
the storage and cloning machinery, but not all integer-list constraints and
branching overloads exist for that variable type.

.. mpg-paragraph:: Factories and transitions.

A factory creates the variable at a position in the space passed to it. A
transition callback is called after a position has been added, whether by
propagation, ``materialize``, ``get``, or ``append``. Both function objects
are shared between clones. They must be deterministic and safe for concurrent
calls, and must own or share any captured data. They must not capture a space
or its variable handles. Use the supplied space and, in a transition callback,
the supplied list to access the current model.

.. mpg-paragraph:: Propagator information.

Factories and transitions run inside ``Space::NoGPI`` contexts, including
transitions called by a direct ``append``. Propagators posted there have
space-local information and zero AFC; identifiers and groups remain
available. A callback can use a local ``Space::UseGPI`` context for postings
that should accumulate ordinary AFC. Nested list construction starts its own
``NoGPI`` context. Each context restores the previous setting when it is
destroyed. For the lifetime, cloning, and rewriting rules of these contexts,
see :ref:`sec:m:branch:gpi`.
