.. _chap:m:open:

Open variable lists
===================

A fixed-size array works well when the number of decisions is known before
search starts. Some problems instead have solutions of different lengths:
routes can visit different numbers of nodes, for example, and a pattern can
contain different numbers of symbols. An open variable list lets the model
decide its length and creates variables as they are needed.

This chapter uses :api:`OpenIntVarList` to find simple routes in a directed
graph. It builds on spaces and cloning from :ref:`chap:m:started`, and on
automata from :ref:`sec:m:integer:extensional`. Branching is discussed in
more detail in :ref:`chap:m:branch`.

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
``IntSet(0,n-1)`` and a maximum length ``n``. It does not create an array of
``n`` node variables. The list has a separate integer variable
``route.length()`` for its eventual length.

The automaton ``paths`` describes the graph. Its extra start state five
consumes the source node zero. The other transitions consume the destination
of a graph arc, and only state four is accepting. The open-list overload of
``extensional`` therefore constrains the route to start at zero, follow
graph arcs, and end at four. The ``distinct`` constraint excludes revisits.
Both constraints follow the list as it grows.

The regular constraint prunes the node variables as the prefix grows.
When the list closes, it requires the route to end in an accepting state.
It does not prune the eventual-length variable or check whether an open
prefix can reach an accepting state within the remaining length bound.

.. _sec:m:open:prefix:

The prefix and the eventual length
----------------------------------

``known_length()`` counts the positions that have been constructed. Their
variables can still be unassigned. Indexed access with ``route[i]`` is
limited to this prefix; it does not create a new position.

The minimum of ``length()`` requires that many positions to exist.
Propagation constructs them, using the list's variable factory and any
transition callback. Requiring more positions can itself post constraints
that require a longer prefix. This continues until the required positions
have been constructed or the space fails.

There are also explicit operations for growing a list. ``materialize(home,n)``
requires at least ``n`` positions, and ``get(home,i)`` requires and returns
the variable at position ``i``. Both restrict the eventual length. After
``get``, check whether the space has failed before using the returned
variable; on failure the handle can be uninitialized. ``append(home,x)``
adds an existing variable belonging to the current space and requires the
length to include it.

``close(home)`` first constructs any positions required by the minimum
length, then assigns the eventual length to the number of constructed
positions. Closing determines the number of positions. It does not assign
their variables.

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

To choose the complete length first, post a brancher on ``route.length()``
before the list brancher. Branchers run in posting order, so the length is
assigned and propagation constructs the required positions before the list
brancher selects their values. The conditional brancher in the program
supports this comparison. Build the downloaded source as described in
:ref:`sec:m:started:run`, then run:

.. code-block:: console

   ./open-route
   ./open-route -branching length

Both searches find the same five routes. They use different search trees and
can return the routes in different orders. The default search constructs a
route incrementally; the second search tries the shorter lengths first.
The better order depends on the problem.

Selectors and filters operate on the constructed prefix. Filter and print
callbacks receive the position in the list. Action and CHB selectors require
the whole list to have been constructed when the brancher is posted;
otherwise posting throws ``Int::UnknownBranching``. Give the list a finite
application bound whenever possible. Exploring longer routes can be very
expensive even if a few short solutions are easy to find.

.. _sec:m:open:constraints:

Constraints that follow growth
------------------------------

An open list has its own constraint overloads. Passing the current prefix
to a constraint on a fixed array would constrain only the variables already
present. It would not arrange for later positions to join that constraint.

Besides ``distinct`` and the regular ``extensional`` constraint used above,
integer lists support relations between consecutive variables, ``sequence``
and ``slidingsum`` over each complete window, ``min`` and ``max`` of the
eventual nonempty sequence, and value precedence through ``precede``. The
open ``distinct`` constraint is value consistent; its propagation-level
argument does not select stronger filtering.

Regular constraints are available for integer and Boolean lists. The
complete sequence must be accepted by the automaton when the list closes;
intermediate prefixes need not be accepted words.

.. _sec:m:open:copy:

Cloning and callbacks
---------------------

The copy constructor updates ``route`` just as it updates an ordinary
variable array. Handles referring to the same list in one space continue
to share a list in the clone, but the clone has its own mutable state.
Growing or closing one space's list does not change the other space.

.. mpg-code:: open route copy and output
   :caption: Cloning and printing the route
   :name: program:m:open:copy

The print function visits ``known_length()`` positions. In a solution,
branching has determined the length and assigned the variables, so this is
the complete route.

:api:`OpenBoolVarList` supplies the corresponding factory for Boolean
variables. The generic :api:`OpenVarList` template also accepts a factory
for another variable type, such as ``SetVar`` or ``FloatVar``. This shares
the storage and cloning machinery; it does not supply all integer-list
constraints or branching overloads for that variable type.

A factory creates the variable at a position in the space passed to it.
An optional transition callback can post constraints after a position is
added. The function objects are shared between clones. They must be
deterministic and safe for concurrent calls, and must own or share any
captured data. They must not capture a space or its variable handles.
Use the space and list passed to the callback to access the current model.

Factories and transitions run inside ``Space::NoGPI`` scopes, including
transitions called by direct ``append``. Propagators posted there have
space-local information and zero AFC; identifiers and groups remain
available. A callback can use a local ``Space::UseGPI`` scope for postings
that should accumulate ordinary AFC. Nested list construction starts its
own ``NoGPI`` scope. Each scope restores the previous setting when it exits.
