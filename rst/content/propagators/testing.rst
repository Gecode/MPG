.. _chap:p:testing:

Testing propagators
===================

Gecode's test library checks a propagator against a specification of its
constraint. It tests propagation on complete assignments and partially
assigned variables, as well as cloning, scheduling, and subsumption. These
checks exercise the obligations discussed in
:ref:`sec:p:started:obligations`. This chapter uses the ``less`` propagator
from :ref:`chap:p:started` to show how to write and run such a test.

The installed test library provides a test runner and support for testing
integer constraints. Gecode's internal tests for set and float constraints,
branchers, assignments, and FlatZinc use additional support that is not part
of the installed library.

.. _sec:p:testing:establish:

Correctness and consistency
---------------------------

The test needs a specification independent of the propagator. For a constraint
over integer variables, this is often a predicate that decides whether a
complete assignment satisfies the constraint. Computing the predicate directly
from the constraint avoids reproducing errors in the propagation algorithm.

As discussed in :ref:`sec:p:started:obligations`, a propagator must be correct
and checking: it must preserve all solutions and detect failure for every
complete assignment that violates the constraint. A test can also check
whether the propagator achieves a particular consistency level. Correctness
alone does not require the propagator to remove every unsupported value.

Testing a small finite domain can cover every complete assignment in that
domain. It does not prove correctness for arbitrary integers, nor does it cover
every possible partial domain or execution order. The test library also uses
random domain changes to exercise propagation and reports a seed for
reproducing failures.

.. _sec:p:testing:build:

Building a standalone test
--------------------------

Gecode must be built and installed with ``BUILD_TESTING=ON``. The test
component also requires the integer and search modules.
:numref:`program:p:testing:cmake` shows how to request the test component and
link the libraries needed for an integer propagator test.

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
``CMAKE_PREFIX_PATH`` to locate the installation. The imported target
``Gecode::gecodetestint`` links the test runner and the required Gecode
libraries. The test program defines ``main()`` and calls
``Test::run_registered_tests()`` to run its registered tests.

.. _sec:p:testing:less:

Testing the less propagator
---------------------------

The class ``LessTest`` in :numref:`program:p:testing:less` derives from
``Test::Int::Test``. Its constructor specifies the test's tags and name,
followed by the number of variables and their common domain bounds. Here,
the two variables range from ``-3`` to ``3``. Of the 49 complete assignments,
21 satisfy the constraint and 28 violate it. The argument ``false`` disables
reification tests, and ``IPL_DOM`` selects a domain consistency check.

.. raw:: latex

   \Needspace{12\baselineskip}

.. mpg-code:: less propagator test
   :caption: A test for the ``less`` propagator
   :name: program:p:testing:less
   :download: less-test.cpp

The member function ``solution()`` specifies the constraint by comparing the
two assigned values. The member function ``post()`` posts the constraint on
the variables supplied by the test library, using the constraint post function
``less()``. The test library compares the results of propagation with
``solution()``.

The global object ``less_test`` registers the test during initialization and
remains alive throughout the call to ``run_registered_tests()``. The integer
test class prefixes the name with ``Int::``, so the runner lists this test as
``Int::Less``. Calls to ``run_registered_tests()`` share the registry and must
not overlap.

.. _sec:p:testing:coverage:

What the test library exercises
-------------------------------

Using ``solution()`` and ``post()``, the test library performs the following
checks with different variable domains and posting orders.

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
     - Checks propagation in cloned spaces and looks for further pruning
       after a reported fixpoint.
   * - Disabling and re-enabling propagation
     - Exercises ``reschedule()`` and compares the resulting domains or
       failure.
   * - Subsumption on successful complete assignments
     - Checks that the propagator is subsumed when all variables are assigned
       and the constraint is satisfied.
   * - Search compared with the assignment predicate
     - Detects a disagreement between the solutions reached by search and the
       independent specification.

By default, the test library enumerates complete assignments in the declared
domain. Domain pruning and some fixpoint checks are randomized. Increasing
the number of iterations therefore exercises additional cases even when all
complete assignments are enumerated.

.. _sec:p:testing:consistency:

Checking consistency
--------------------

The last constructor argument initializes the propagation level ``ipl`` stored
by the test class. A test can pass this value to its constraint post function
when that function accepts a propagation level. The ``less()`` function has
no such argument. Here, ``IPL_DOM`` selects the test library's domain
consistency check. The ``less`` propagator is domain consistent: every
remaining value of ``x0`` has support at ``x1.max()``, and every remaining
value of ``x1`` has support at
``x0.min()``. Its two bound updates therefore remove every unsupported value,
even when the domains contain holes.

The propagation level and the checked consistency are separate fields in the
test class. The field ``contest`` selects the check: ``CTL_DOMAIN`` for domain
consistency, ``CTL_BOUNDS_D`` for bounds(D) consistency, ``CTL_BOUNDS_Z`` for
bounds(Z) consistency, or ``CTL_NONE`` for no consistency check. A test can
set this field in its constructor to match the consistency level of the
propagator.

.. _sec:p:testing:selection:

Selecting tests and reproducing failures
----------------------------------------

The test belongs to both ``check`` and ``normal``. Tags select groups of tests;
membership in one group does not imply membership in another. A constructor
without a tag argument assigns only ``normal``.

The runner accepts one or more tag selections:

.. code-block:: console

   ./build/less-test -tag check
   ./build/less-test -tag normal
   ./build/less-test -tag check -tag normal
   ./build/less-test -tag all

Repeated ``-tag`` options form a union. A ``-test`` name filter and a tag
filter must both match. With no ``-tag`` option, the runner applies no tag
filter, so tests with any tags can run. ``-list-tags`` prints the known tags,
while ``-list-with-tags`` prints every registration and its tags. Listing commands
ignore name, tag, and starting-point filters.

Failures report the test name and random seed. To reproduce a failure, select
the test and supply the reported seed. For example, for ``Int::Less`` with
seed ``12345``, run:

.. code-block:: console

   ./build/less-test -test Int::Less -seed 12345 -iter 1 \
     -threads 1 -log -stop true

The option ``-log`` prints the test's buffered log and requires a single
thread. The log includes the assignment that caused the failure. For example,
replacing ``x[0] < x[1]`` in the specification with ``x[0] <= x[1]`` makes equal
assignments valid according to the specification, while the propagator rejects
them. The reported assignment shows the boundary error directly.

.. _sec:p:testing:extending:

Extending the test
------------------

The number of complete assignments grows exponentially with the number of
variables. For constraints with many arguments, use small representative
domains or override ``assignment()`` to supply a suitable assignment
generator. Include domains with holes when these affect the propagation
algorithm. A failing random case can be retained by recording its seed or
writing a separate test for that case.

A test for a reified constraint passes ``true`` to the base class constructor
and implements the ``post()`` overload that receives a ``Reify`` object.
The ``rms`` mask limits
the test to supported modes. See :ref:`chap:p:reified` for the propagator side
of reification.

Further tests may be needed for shared variables, invalid arguments, and
arithmetic near the integer limits. Memory safety and performance also require
checks beyond those provided by the integer test class.
