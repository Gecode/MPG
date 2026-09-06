.. _chap:p:testing:

Testing propagators
===================

A propagator is small enough that its code can look convincing even when one
boundary case is wrong. The test library compares the propagator with a direct
description of its constraint, then changes how and when propagation happens.
This gives us a practical way to exercise the obligations from
:ref:`sec:p:started:obligations`.

The installed test API covers the core runner and helpers for integer
constraints. The set, float, brancher, assignment, and FlatZinc test helpers
used inside Gecode are not part of this API.

.. _sec:p:testing:establish:

What a propagator test must establish
-------------------------------------

The test needs a specification independent of the propagator. For a constraint
over integer variables, the simplest specification is often a predicate over
a complete assignment. It says whether that assignment is a solution without
calling the propagator or another implementation of the same algorithm.

This separates two questions. The first is whether propagation is correct and
checking: a valid assignment must not fail, and an invalid complete assignment
must fail. The second is how much propagation the implementation promises. A
correct propagator may be weaker than another correct propagator, but it must
meet the consistency level claimed by its test.

Testing a small finite domain can cover every complete assignment in that
domain. It does not prove correctness for arbitrary integers, nor does it cover
every possible partial domain or execution order. The randomized parts of the
harness broaden the exercised cases, and a reported seed makes a failure
repeatable.

.. _sec:p:testing:build:

Building a standalone test
--------------------------

Gecode must be built and installed with ``BUILD_TESTING=ON``. The test
component also requires the integer and search modules. A consumer requests
the component and links the integer helper target as follows.

.. mpg-code:: less test CMake project
   :caption: CMake project for the ``less`` propagator test
   :name: program:p:testing:cmake
   :download: CMakeLists.txt

Place :download:`less.cpp <../../examples/src/less.cpp>`, the test from
:numref:`program:p:testing:less`, and ``CMakeLists.txt`` in one directory. Then
configure and run it with:

.. code-block:: console

   cmake -S . -B build -DCMAKE_PREFIX_PATH=/path/to/gecode
   cmake --build build
   ./build/less-test -iter 1

``Gecode_ROOT`` or ``Gecode_DIR`` can be used instead of
``CMAKE_PREFIX_PATH`` when that better matches the installation. The imported
target ``Gecode::gecodetestint`` brings in the core runner and the required
Gecode libraries. The test executable supplies its own ``main()``; the Gecode
installation does not provide a runner executable for consumer tests.

.. _sec:p:testing:less:

Testing the less propagator
---------------------------

The test in :numref:`program:p:testing:less` uses the ``less`` propagator from
:ref:`chap:p:started`. It has two variables with domains from ``-3`` through
``3``. Of the 49 complete assignments, 21 satisfy strict less-than and 28 do
not. Equal values, reversed values, negative values, and both domain boundaries
are all present.

.. mpg-code:: less propagator test
   :caption: A test for the ``less`` propagator
   :name: program:p:testing:less
   :download: less-test.cpp

The ``solution()`` method is the specification. Its comparison is deliberately
plain. The ``post()`` method calls the same ``less()`` posting function used by
a model. If the posting function did nothing, the invalid assignments would
not fail and the test would catch the error.

Constructing ``less_test`` registers the test. It has static lifetime so it
remains alive while ``run_registered_tests()`` runs. Runner calls use a
process-wide registry and must not overlap. The registered name printed by
``-list`` is ``Int::Less``.

.. _sec:p:testing:coverage:

What the test library exercises
-------------------------------

The two methods in :numref:`program:p:testing:less` stay fixed while the test
library varies the state of the variables and the point at which the
propagator is posted.

.. list-table:: Checks performed by an integer propagator test
   :header-rows: 1
   :widths: 38 62

   * - Check
     - Purpose
   * - Complete satisfying and violating assignments
     - Detects rejection of solutions and acceptance of non-solutions.
   * - Assignment before and after posting, including partial assignment
     - Exercises both posting-time behavior and later propagation.
   * - Random bounds changes and removal of domain values
     - Exercises subscriptions and propagation as domains change.
   * - The selected consistency check
     - Detects pruning weaker than the propagator promises.
   * - Cloning and fixpoint checks
     - Exercises copied actor state and detects missed propagation in the
       sampled cases.
   * - Disabling and re-enabling propagation
     - Exercises ``reschedule()`` and compares the resulting domains or
       failure.
   * - Subsumption on successful complete assignments
     - Checks that an entailed completed case retires the propagator.
   * - Search compared with the assignment predicate
     - Detects a disagreement between the solutions reached by search and the
       independent specification.

Complete assignments in the declared domain are enumerated. Domain pruning
and some fixpoint checks are randomized, so the number of iterations still
matters even for this small example.

.. _sec:p:testing:consistency:

Choosing the promised consistency
----------------------------------

The last constructor argument records the propagation level passed to the
constraint. ``IPL_DOM`` also asks the harness to check domain consistency. The
``less`` propagator meets that promise: every remaining value of ``x0`` has
support at ``x1.max()``, and every remaining value of ``x1`` has support at
``x0.min()``. Its two bound updates therefore remove every unsupported value,
including values inside a domain with holes.

The propagation level and the checked consistency are separate fields in the
test class. A specialized test can set ``contest`` to ``CTL_NONE``,
``CTL_BOUNDS_D``, or ``CTL_BOUNDS_Z`` when that is the propagator's actual
contract. A consistency check should describe the implementation's promise.
Turning it off merely because it finds a failure hides useful evidence.

.. _sec:p:testing:selection:

Selecting tests and reproducing failures
----------------------------------------

The test declares both ``check`` and ``normal`` membership. Tags are explicit
sets rather than levels: membership in ``normal`` does not imply membership in
``check``. A constructor without a tag argument assigns only ``normal``.

The runner accepts one or more tag selections:

.. code-block:: console

   ./build/less-test -tag check
   ./build/less-test -tag normal
   ./build/less-test -tag check -tag normal
   ./build/less-test -tag all

Repeated ``-tag`` options form a union. A ``-test`` name filter and a tag
filter must both match. With no ``-tag`` option, the runner applies no tag
filter. This is different from the default ``normal`` membership assigned to a
test whose constructor omits tags. ``-list-tags`` prints the known tags, while
``-list-with-tags`` prints every registration and its tags. Listing commands
ignore name, tag, and starting-point filters.

Failures report the test name and random seed. Reproduce one case in a single
thread and request its buffered log with:

.. code-block:: console

   ./build/less-test -test Int::Less -seed 12345 -iter 1 \
     -threads 1 -log -stop true

``-log`` cannot be combined with a multithreaded run. For example, replacing
``x[0] < x[1]`` in the specification with ``x[0] <= x[1]`` makes equal
assignments valid according to the specification, while the propagator rejects
them. The reported assignment shows the boundary error directly.

.. _sec:p:testing:extending:

Extending the test
------------------

Exhaustive assignment grows exponentially with the arity, so a larger
propagator normally needs smaller representative domains, a random assignment
generator, or a custom ``assignment()`` method. Sparse domains deserve explicit
attention when the propagator inspects holes. Once a random failure has been
found, keep its seed or turn the case into a small fixed regression test.

A reified propagator passes ``true`` to the test constructor and implements the
``post()`` overload that receives a ``Reify`` object. The ``rms`` mask limits
the test to supported modes. See :ref:`chap:p:reified` for the propagator side
of reification. The ``less`` interface used here is not reified, so adding that
machinery would obscure the basic test.

The generic integer harness does not replace tests for every special case.
Aliased arguments, exceptional inputs, arithmetic near integer limits, memory
safety, and performance need their own checks when the propagator depends on
them.
