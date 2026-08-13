.. _chap:m:int:


.. _modeling:m-integer:integer-and-boolean-variables-and-constraints:

Integer and Boolean variables and constraints
=============================================

This chapter gives an overview of integer and Boolean variables and the constraints available for them in Gecode. The chapter focuses on variables and constraints, a discussion of branching for integer and Boolean variables can be found in :ref:`sec:m:branch:int`.

The chapter does not make an attempt to duplicate the reference documentation (see `Using integer variables and constraints <https://www.gecode.dev/doc/6.4.0/reference/group__TaskModelInt.html>`__). It is concerned with the most important ideas and principles underlying integer and Boolean variables and constraints. In particular, the chapter provides entry points into the reference documentation and points to illustrating examples.

.. _modeling:m-integer:overview:

.. rubric:: Overview.

:ref:`sec:m:integer:var` details how integer and Boolean variables (and variables in general) can be used for modeling. Variable arrays and argument arrays are discussed in :ref:`sec:m:integer:proper`. Important aspects of how constraints are posted in Gecode are explained in :ref:`sec:m:integer:generic`. These sections belong to the basic reading material of :ref:`part:m`.

The remaining sections :ref:`sec:m:integer:post` and :ref:`sec:m:integer:exec` provide an overview of the constraints that are available for integer and Boolean variables in Gecode.

.. important::

   Do not forget to add

   .. mpg-code:: snippet:m-integer:chap:m:int:code:1
      :direct:

   to your program when you want to use integer or Boolean variables and constraints.

.. container:: convention

   All program fragments and references to classes, namespaces, and other entities assume that declarations and definitions from the ``Gecode`` namespace are visible: for example, by adding

   .. mpg-code:: snippet:m-integer:chap:m:int:code:2
      :direct:

   to your program.

   The variable ``home`` refers to a space reference (of type ``Space&``) and defines the home space in which new variables, propagators, and branchers are posted. Often (as in :ref:`chap:m:started` and :ref:`chap:m:comfy`) ``home`` will be ``*this``, referring to the current space.

.. _sec:m:integer:var:


.. _modeling:m-integer:integer-and-boolean-variables:

Integer and Boolean variables
-----------------------------

Variables in Gecode are for modeling. They provide operations for creation, access, and update during cloning. By design, the only way to modify (constrain) a variable is by post functions for constraints and branchers.

Integer variables are instances of the class `IntVar <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1IntVar.html>`__ while Boolean variables are instances of the class `BoolVar <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1BoolVar.html>`__. Integer variables are *not* related to Boolean variables. A Boolean variable is *not* an integer variable with a domain that is included in :math:`\{0,1\}`. The only way to get an integer variable that is equal to a Boolean variable is by posting a channeling constraint between them (see :ref:`sec:m:integer:channel`).

.. mpg-tip:: Do not use views for modeling

   If you — after some browsing of the reference documentation — should come across integer views such as ``IntView``, you might notice that views have a richer interface than integer variables. You might feel that this interface looks too powerful to be ignored. Now, you really should put some trust in this document: views are *not* for modeling.


   The more powerful interface only works within propagators and branchers, see :ref:`part:p` and :ref:`part:b`.

.. _sec:m:integer:create:


.. _modeling:m-integer:creating-integer-variables:

Creating integer variables
~~~~~~~~~~~~~~~~~~~~~~~~~~

A variable provides a read-only interface to a *variable implementation* where the same variable implementation can be referred to by arbitrarily many variables.

New integer variables are created by using a constructor. A new integer variable ``x`` is created by

.. mpg-code:: snippet:m-integer:sec:m:integer:create:code:1
   :direct:


This declares a variable ``x`` of type `IntVar <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1IntVar.html>`__ in the space ``home``, creates a new integer *variable implementation* with domain :math:`\{-4,\ldots,20\}`, and points ``x`` to the newly created integer variable implementation.

The domain of a variable can also be specified by an integer set `IntSet <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1IntSet.html>`__, for example by

.. mpg-code:: snippet:m-integer:sec:m:integer:create:code:2
   :direct:


which creates a new variable with domain :math:`\{-4,\ldots,20\}`. An attempt to create an integer variable with an empty domain throws an exception of type `Int::VariableEmptyDomain <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1Int_1_1VariableEmptyDomain.html>`__.

Integer sets can be initialized by an array of integers, for example

.. mpg-code:: snippet:m-integer:sec:m:integer:create:code:3
   :direct:


initializes ``c`` to have the four elements (as defined by the second argument ``4`` in the constructor call) :math:`\{\mathtt{1},\mathtt{2},\mathtt{3},\mathtt{4}\}`, whereas

.. mpg-code:: snippet:m-integer:sec:m:integer:create:code:4
   :direct:


initializes ``d`` to have the elements :math:`\{\mathtt{1},\mathtt{2},\mathtt{5},\mathtt{6},\mathtt{7}\}` where ``r`` is an array of pairs expressing ranges of values. The same can be expressed with initializer lists as in

.. mpg-code:: snippet:m-integer:sec:m:integer:create:code:5
   :direct:


Please note the difference between ``IntSet({1,3})`` and ``IntSet(1,3)``: the former has the elements :math:`\{\mathtt{1},\mathtt{3}\}`. while the latter has the elements :math:`\{\mathtt{1},\mathtt{2},\mathtt{3}\}`.

The default or copy constructor of a variable does not create a new variable (that is, a new variable implementation). Instead, the variable does not refer to any variable implementation (default constructor) or to the same variable implementation (copy constructor). For example, in

.. mpg-code:: snippet:m-integer:sec:m:integer:create:code:6
   :direct:


both ``x`` and ``y`` refer to the same integer variable implementation. Using a default constructor and an assignment operator is equivalent:

.. mpg-code:: snippet:m-integer:sec:m:integer:create:code:7
   :direct:


.. _sec:m:integer:limits:


.. _modeling:m-integer:limits-for-integer-values:

Limits for integer values
~~~~~~~~~~~~~~~~~~~~~~~~~

The set of values for an integer variable is a subset of the values of the type ``int``. The set of values is symmetric: :math:`-\mbox{\texttt{Int::Limits::min}}=\mbox{\texttt{Int::Limits::max}}` for the smallest possible integer variable value ``Int::Limits::min`` and the largest possible integer variable value ``Int::Limits::max``. Moreover, ``Int::Limits::max`` is strictly smaller than the largest possible integer value ``INT_MAX`` and ``Int::Limits::min`` is strictly larger than the smallest possible integer value ``INT_MIN``. These limits are defined in the namespace `Int::Limits <https://www.gecode.dev/doc/6.4.0/reference/namespaceGecode_1_1Int_1_1Limits.html>`__.

Any attempt to create a variable with values outside the defined limits throws an exception of type `Int::OutOfLimits <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1Int_1_1OutOfLimits.html>`__. The same holds true for any attempt to use an integer value outside the defined limits when posting a constraint or brancher.

.. _sec:m:integer:empty:


.. _modeling:m-integer:variable-domains-are-never-empty:

Variable domains are never empty
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

An important invariant in Gecode is that the domain of a variable is never empty. When a variable domain should become empty during propagation, the space is failed but the variable’s domain is kept. In fact, this is the very reason why an attempt to create a variable with an empty domain, for example by

.. mpg-code:: snippet:m-integer:sec:m:integer:empty:code:1
   :direct:


throws an exception of type `Int::VariableEmptyDomain <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1Int_1_1VariableEmptyDomain.html>`__.

.. _tip:m:integer:beautifuldomains:

.. mpg-tip:: Small variable domains are beautiful

   It is not an omission that an integer variable has no constructor that creates a variable with the largest possible domain. One could argue that a constructor like that would come in handy for creating temporary variables. After all, one would not have to worry about the exact domain!


   Sorry, but one has to worry. The apparent omission is deliberate to make you worry indeed. For many propagators posted for a constraint a small domain is essential. For example, when posting a ``linear`` constraint (as in :ref:`sec:m:started:first`), variable domains that are too large might result in an exception of type `Int::OutOfLimits <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1Int_1_1OutOfLimits.html>`__ as during propagation numerical overflow might occur (even if Gecode resorts to a number type supporting larger numbers than ``int`` for propagating ``linear``). Moreover, the runtime of other propagators (for example, many domain propagators such as domain consistent ``distinct``) depend critically on the size of a domain. Again, Gecode tries to be clever in most of the cases. But, it is better to make it a habit to think about initial variable domains carefully (please remember: better safe than sorry).

   For examples where small variable domains matter, see :ref:`tip:c:golomb:beautifuldomains` and :ref:`tip:c:warehouses:beautifuldomains`.

.. _modeling:m-integer:creating-boolean-variables:

Creating Boolean variables
~~~~~~~~~~~~~~~~~~~~~~~~~~

The only difference between integer and Boolean variables is that Boolean variables can only take the values ``0`` or ``1``. Any attempt to create a Boolean variable with values different from ``0`` or ``1`` throws an exception of type `Int::NotZeroOne <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1Int_1_1NotZeroOne.html>`__.

.. container:: convention

   If Boolean variables are not explicitly mentioned in the following, the same functionality for integer variables is also available for Boolean variables and has the same behavior.

.. _modeling:m-integer:variable-access-functions:

Variable access functions
~~~~~~~~~~~~~~~~~~~~~~~~~

Variables provide member functions for access, such as ``x.min()`` for the minimum value of the current domain for an integer or Boolean variable ``x``. In particular, the member function ``x.val()`` accesses the integer value of an already assigned variable (if the variable is not yet assigned, an exception of type `Int::ValOfUnassignedVar <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1Int_1_1ValOfUnassignedVar.html>`__ is thrown). In addition, variables can be printed by the standard output operator ``<<``.

.. _sec:m:int:iter:


.. _modeling:m-integer:iterating-over-integer-variable-domains:

Iterating over integer variable domains
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The entire domain of an integer variable can be accessed by a *value iterator* `IntVarValues <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1IntVarValues.html>`__ or a *range iterator* `IntVarRanges <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1IntVarRanges.html>`__. For example, the loop

.. mpg-code:: snippet:m-integer:sec:m:int:iter:code:1
   :direct:


uses the value iterator ``i`` to print all values of the domain of the integer variable ``x``. The call operator ``i()`` tests whether there are more values to iterate for ``i``, the prefix increment operator ``++i`` moves the iterator ``i`` to the next value, and ``i.val()`` returns the current value of the iterator ``i``. The values are iterated in strictly increasing order.

Similarly, the following loop

.. mpg-code:: snippet:m-integer:sec:m:int:iter:code:2
   :direct:


uses the range iterator ``i`` to print all *ranges* of the integer variable ``x``. Given a finite set of integers :math:`d`, the *range sequence* of :math:`d` is the shortest (and unique) sequence of ranges (intervals)

.. math:: \langle\left[n_0..m_0\right]\},\ldots,\left[n_k..m_k\right]\}\rangle

such that the sequence is ordered and non-adjacent (:math:`m_i+1<n_{i+1}` for :math:`0\leq i<k`). A range iterator iterates over the ranges in the range sequence of a variable’s domain. Like a value iterator, a range iterator implements the call operator ``i()`` to test whether there are more ranges to iterate for ``i`` and the prefix increment operator ``++i`` to move ``i`` to the next range. As a range iterator ``i`` iterates over ranges, it implements the member functions ``i.min()`` and ``i.max()`` for the minimal, respectively maximal, value of the current range.

Iteration of values and ranges for Boolean variables is not available (as it is not needed).

.. _sec:m:integer:inspect:


.. _modeling:m-integer:when-to-inspect-a-variable:

When to inspect a variable
~~~~~~~~~~~~~~~~~~~~~~~~~~

Note that one must not change the domain of a variable (for example, by posting a constraint on that variable) while an iterator for that variable is still in use. This is the same as for most iterators, for example, for iterators in the C++ Standard Template Library (STL).

Otherwise, a variable can always be inspected: at any place (that is, not only in member functions of the variable’s home) and at any time (regardless of the status of a space). If the variable’s home is failed, the variable can still be inspected. However, it might be the case that the variable domain has more values than expected. For example, after creating a variable ``x`` with the singleton domain :math:`\{0\}` and posting the constraint that ``x`` must be different from ``0`` by (read :ref:`tip:m:started:status` about ``status()``):

.. mpg-code:: snippet:m-integer:sec:m:integer:inspect:code:1
   :direct:


the space ``home`` is failed but the variable ``x`` still contains the value ``0`` in its domain.

.. _sec:m:integer:update:


.. _modeling:m-integer:updating-variables:

Updating variables
~~~~~~~~~~~~~~~~~~

As discussed in :ref:`sec:m:started:first`, a variable must be updated during cloning in the copy constructor used by a space’s ``copy()`` member function. For example, a variable ``x`` is updated by

.. mpg-code:: snippet:m-integer:sec:m:integer:update:code:1
   :direct:


where ``y`` is the variable from which ``x`` is to be updated. While ``x`` belongs to ``home``, ``y`` belongs to the space being cloned.

A space only needs to update the variables that are part of the solution, so that their values can be accessed after a solution space has been found. Temporary variables do not need to be copied.

Assume that we want to constrain the integer variable ``p`` to be the product of ``x``, ``y``, and ``z``. Gecode only offers multiplication of two variables, hence a temporary variable ``t`` is created (assume also that we know that the values for ``t`` are between ``0`` and ``1000``):

.. mpg-code:: snippet:m-integer:sec:m:integer:update:code:2
   :direct:


Here, ``t`` does not require updating. The multiplication propagators created by ``mult`` take care of updating the variable implementation of ``t``.

.. _sec:m:integer:proper:


.. _modeling:m-integer:variable-and-argument-arrays:

Variable and argument arrays
----------------------------

Gecode has very few *proper* data structures. The proper data structures for integer and Boolean variables are the variables themselves, integer sets, and arrays of variables. Proper means that these data structures can be updated and hence be stored in a space.

Of course, data structures that themselves do not contain proper data structures can be stored in a space, such as integers, pointers, and strings.

Gecode supports the programming of new proper data structures, this is discussed in :ref:`sec:p:memory:shared`.

.. _sec:m:integer:intvararray:


.. _modeling:m-integer:integer-and-boolean-variable-arrays:

Integer and Boolean variable arrays
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Integer variable arrays of type `IntVarArray <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1IntVarArray.html>`__ can be used like variables. For example,

.. mpg-code:: snippet:m-integer:sec:m:integer:intvararray:code:1
   :direct:


creates a new integer variable array with four variables containing newly created variables with domain :math:`\{-10,\ldots,10\}`. Boolean variable arrays of type `BoolVarArray <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1BoolVarArray.html>`__ are analogous.

Creation of a variable array allocates memory from the home space. The memory is freed when the space is deleted (not when the destructor of the variable array is called). Variable arrays can be created without creating new variables by just passing the size. That is,

.. mpg-code:: snippet:m-integer:sec:m:integer:intvararray:code:2
   :direct:


is equivalent to the previous example.

The other operations on variable arrays are as one would expect. For example, one can check whether all variables are assigned using the ``assigned()`` function. More importantly, variable arrays like variables have an update function and variable arrays must be updated during cloning. In the following, we will refer to the size of a variable array ``x`` by :math:`|\mathtt x|` (which can be computed by ``x.size()``).

.. _modeling:m-integer:matrix-interface:

.. rubric:: Matrix interface.

Many models are naturally expressed by using matrices. Gecode offers support that superimposes a matrix interface for modeling on an array, see :ref:`sec:m:minimodel:matrix`.

.. _sec:m:integer:args:


.. _modeling:m-integer:argument-arrays:

Argument arrays
~~~~~~~~~~~~~~~

As mentioned above, the memory allocated for a variable array is freed only when its home space is deleted. That makes variable arrays *unsuited* for temporary variable arrays, in particular for arrays that are built dynamically or used as arguments for post functions.

For this reason, Gecode provides argument arrays: ``IntVarArgs`` for integer variables, ``BoolVarArgs`` for Boolean variables, ``IntArgs`` for integers, and ``IntSetArgs`` for integer sets (see `Argument arrays <https://www.gecode.dev/doc/6.4.0/reference/group__TaskModelIntArgs.html>`__). Internally, they allocate space from the heap [1]_ and the memory is freed when their destructor is executed.

Argument arrays can be created empty:

.. mpg-code:: snippet:m-integer:sec:m:integer:args:code:1
   :direct:


with a certain size but without initializing the elements:

.. mpg-code:: snippet:m-integer:sec:m:integer:args:code:2
   :direct:


using standard initializer lists (assuming that ``a``, ``b``, ``c``, and ``d`` are integer variables):

.. mpg-code:: snippet:m-integer:sec:m:integer:args:code:3
   :direct:


or fully initialized:

.. mpg-code:: snippet:m-integer:sec:m:integer:args:code:4
   :direct:


For a typical example, consider :ref:`sec:m:started:first` where an integer argument array and an integer variable argument array are used to pass coefficients and variables to the ``linear`` post function.

.. _modeling:m-integer:dynamic-argument-arrays:

.. rubric:: Dynamic argument arrays.

In contrast to variable arrays, argument arrays can grow dynamically by adding elements or whole arrays using ``operator<<``:

.. mpg-code:: snippet:m-integer:sec:m:integer:args:code:5
   :direct:


Furthermore, argument arrays can be concatenated using ``operator+``:

.. mpg-code:: snippet:m-integer:sec:m:integer:args:code:6
   :direct:


.. _modeling:m-integer:slices:

.. rubric:: Slices.

It is sometimes necessary to post constraints on a subsequence of the variables in an array. This is made possible by the ``slice(start,inc,n)`` method of variable and argument arrays. The ``start`` parameter gives the starting index of the subsequence. The ``inc`` optional parameter gives the increment, i.e., how to get from one element to the next (its default is :math:`1`). The ``n`` parameter gives the maximal length of the resulting array (its default is :math:`-1`, meaning as long as possible).

The following examples should make this clearer. Assume that the integer variable argument array ``x`` is initialized as follows:

.. mpg-code:: snippet:m-integer:sec:m:integer:args:code:7
   :direct:


Then the following calls of ``slice()`` return:

- ``x.slice(5)`` returns an array with elements ``x[5],x[6],…,x[9]``.

- ``x.slice(5,1,3)`` returns ``x[5],x[6],x[7]``.

- ``x.slice(5,-1)`` returns ``x[5],x[4],…,x[0]``.

- ``x.slice(3,3)`` returns ``x[3],x[6],x[9]``.

- ``x.slice(8,-2)`` returns ``x[8],x[6],x[4],x[2],x[0]``.

- ``x.slice(8,-2,3)`` returns ``x[8],x[6],x[4]``.

..

.. mpg-tip:: Reversing argument arrays

   The ``slice()`` method can be used to compute an array with the elements of ``x`` in reverse order like this:


   .. mpg-code:: snippet:m-integer:sec:m:integer:args:code:8
      :direct:

.. _modeling:m-integer:creating-integer-argument-arrays:

.. rubric:: Creating integer argument arrays.

Integer argument arrays support standard initializer lists, for example

.. mpg-code:: snippet:m-integer:sec:m:integer:args:code:9
   :direct:


creates an array with the four elements ``0``, ``1``, ``2``, and ``3``.

Integer argument arrays with simple sequences of integers can be generated using the static method ``IntArgs::create(n,start,inc)``. The ``n`` parameter gives the length of the generated array. The ``start`` parameter is the starting value, and ``inc`` determines the increment from one value to the next.

Here are a few examples:

- ``IntArgs::create(5,0)`` creates an array with elements ``0,1,2,3,4``.

- ``IntArgs::create(5,4,-1)`` creates ``4,3,2,1,0``.

- ``IntArgs::create(3,2,0)`` creates ``2,2,2``.

- ``IntArgs::create(6,2,2)`` creates ``2,4,6,8,10,12``.

..

.. mpg-tip:: Dynamically constructing models

   Sometimes the number of variables cannot be determined easily, for example when it depends on data read from a file.


   .. container:: samepage

      Suppose the following script with a variable array ``x``:

      .. mpg-code:: dynamic script

   It is easy to use a variable argument array ``_x`` for collecting variables as follows:

   .. mpg-code:: dynamic script:read data

   and then initialize the variable array ``x`` using the argument array:

   .. mpg-code:: dynamic script:initialize variable array

In the following we do not distinguish between arrays and argument arrays unless operations require a certain type of array. In fact, all post functions for constraints and branchers only accept variable argument arrays. A variable array is automatically casted to a variable argument array if needed.

.. _sec:m:integer:stl:


.. _modeling:m-integer:stl-style-iterators:

STL-style iterators
~~~~~~~~~~~~~~~~~~~

All arrays in Gecode (including variable arrays and argument arrays) also support STL-style (Standard Template Library) iterators. For example, assume that ``a`` is an integer variable argument array. Then

.. mpg-code:: snippet:m-integer:sec:m:integer:stl:code:1
   :direct:


creates an iterator ``i`` for the elements of ``a`` and iterates from the first to the last element in ``a``.

More powerfully, iterators give you the ability to work with STL algorithms. Suppose that ``f()`` is a function that takes an integer variable by reference such as in

.. mpg-code:: snippet:m-integer:sec:m:integer:stl:code:2
   :direct:


and ``a`` is an integer variable argument array. Then

.. mpg-code:: snippet:m-integer:sec:m:integer:stl:code:3
   :direct:


applies the function ``f()`` to each integer variable in ``a``.

.. _sec:m:integer:generic:


.. _modeling:m-integer:posting-constraints:

Posting constraints
-------------------

This section provides information about general principles for posting constraints over integer and Boolean variables.

.. _modeling:m-integer:post-functions-are-clever:

Post functions are clever
~~~~~~~~~~~~~~~~~~~~~~~~~

A constraint post function carefully analyzes its arguments. Based on this analysis, the constraint post function chooses the best possible propagator for the constraint.

For example, when posting a ``distinct`` constraint (see :ref:`sec:m:integer:distinct`) for the variable array ``x`` by

.. mpg-code:: snippet:m-integer:sec:m:integer:generic:code:1
   :direct:


where ``x`` has two elements, the much more efficient propagator for disequality :math:`\mathtt{x}_0 \neq \mathtt{x}_1` is created.

.. _modeling:m-integer:everything-is-copied:

Everything is copied
~~~~~~~~~~~~~~~~~~~~

When passing arguments to a post function, all data structures that are needed for creating a propagator (or several propagators) implementing a constraint are copied. That is, none of the data structures that are passed as arguments are needed after a constraint has been posted.

.. _sec:m:integer:reify:


.. _modeling:m-integer:reified-constraints:

Reified constraints
~~~~~~~~~~~~~~~~~~~

Many constraints also exist as *reified* variants: the validity of a constraint is reflected to a Boolean control variable (reified constraints are also known as meta-constraints). In addition to full reification also half reification :cite:`HalfReify` is supported for reified constraints. Whether a reified version exists for a given constraint can be found in the reference documentation. If a reified version does exist, the Boolean control variable (and possibly information about the reification mode, to be discussed in :ref:`sec:m:integer:halfreify`) is passed as the last non-optional argument.

For example, posting

.. mpg-code:: snippet:m-integer:sec:m:integer:reify:code:1
   :direct:


for integer variables ``x`` and ``y`` and a Boolean control variable ``b`` creates a propagator for the reified constraint :math:`\reifyeqv{\mathtt{b}}{\mathtt{x}=\mathtt{y}}` that propagates according to the following rules:

- If ``b`` is assigned to ``1``, the constraint :math:`\mathtt{x}=\mathtt{y}` is propagated.

- If ``b`` is assigned to ``0``, the constraint :math:`\mathtt{x}\neq\mathtt{y}` is propagated.

- If the constraint :math:`\mathtt{x}=\mathtt{y}` holds, then :math:`\mathtt{b}=\mathtt{1}` is propagated.

- If the constraint :math:`\mathtt{x}\neq\mathtt{y}` holds, then :math:`\mathtt{b}=\mathtt{0}` is propagated.

.. _sec:m:integer:halfreify:


.. _modeling:m-integer:half-reification:

Half reification
~~~~~~~~~~~~~~~~

Reification as discussed in the previous paragraph is also known as *full* reification as it propagates a full equivalence between the constraint :math:`c` and the constraint that a Boolean control variable is equal to ``1``. *Half reification* propagates only one direction of the equivalence :cite:`HalfReify`. Half reification can be used by passing an object of class `Reify <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1Reify.html>`__ that combines a Boolean control variable and a *reification mode* of type ``ReifyMode`` (see `Using integer variables and constraints <https://www.gecode.dev/doc/6.4.0/reference/group__TaskModelInt.html>`__).

For example, the half reified constraint :math:`\reifyimp{\mathtt{b}}{\mathtt{x}=\mathtt{y}}` for integer variables ``x`` and ``y`` and a Boolean control variable ``b`` can be posted by

.. mpg-code:: snippet:m-integer:sec:m:integer:halfreify:code:1
   :direct:


and is propagated as follows (``RM_IMP`` suggests *implication* :math:`\Rightarrow`):

- If ``b`` is assigned to ``1``, the constraint :math:`\mathtt{x}=\mathtt{y}` is propagated.

- If the constraint :math:`\mathtt{x}\neq\mathtt{y}` holds, then :math:`\mathtt{b}=\mathtt{0}` is propagated.

Likewise, the half reified constraint :math:`\reifypmi{\mathtt{b}}{\mathtt{x}=\mathtt{y}}` for integer variables ``x`` and ``y`` and a Boolean control variable ``b`` can be posted by

.. mpg-code:: snippet:m-integer:sec:m:integer:halfreify:code:2
   :direct:


and is propagated as follows (``RM_PMI`` suggests *inverse implication* :math:`\Leftarrow`):

- If ``b`` is assigned to ``0``, the constraint :math:`\mathtt{x}\neq\mathtt{y}` is propagated.

- If the constraint :math:`\mathtt{x}=\mathtt{y}` holds, then :math:`\mathtt{b}=\mathtt{1}` is propagated.

Full reification can be requested by the reification mode ``RM_EQV`` (for equivalence :math:`\Leftrightarrow`) as follows:

.. mpg-code:: snippet:m-integer:sec:m:integer:halfreify:code:3
   :direct:


As the constructor for `Reify <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1Reify.html>`__ has ``RM_EQV`` as default value for its second argument, this can be written shorter as:

.. mpg-code:: snippet:m-integer:sec:m:integer:halfreify:code:4
   :direct:


or even shorter as:

.. mpg-code:: snippet:m-integer:sec:m:integer:halfreify:code:5
   :direct:


For convenience, three functions ``eqv()``, ``imp()``, and ``pmi()`` exist that take a Boolean variable and return a corresponding object of class `Reify <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1Reify.html>`__. For example, instead of writing:

.. mpg-code:: snippet:m-integer:sec:m:integer:halfreify:code:6
   :direct:


one can write more concisely:

.. mpg-code:: snippet:m-integer:sec:m:integer:halfreify:code:7
   :direct:


.. _sec:m:integer:ipl:


.. _modeling:m-integer:selecting-the-propagation-level:

Selecting the propagation level
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For many constraints, Gecode provides different propagators with different levels of propagation. All constraint post functions take an optional argument of type ``IntPropLevel`` (see `Using integer variables and constraints <https://www.gecode.dev/doc/6.4.0/reference/group__TaskModelInt.html>`__) controlling which propagator is chosen for a particular constraint.

The different simple values for ``IntPropLevel`` have the following meaning:

- ``IPL_VAL``: perform value propagation. A typical example is naive ``distinct``: wait until a variable becomes assigned to a value :math:`n`, then prune :math:`n` from all other variables.

- ``IPL_BND``: perform bounds propagation or achieve bounds consistency. This captures both bounds consistency over the integers (for example, for ``distinct``, see :ref:`sec:m:integer:distinct`) or bounds consistency over the real numbers (for example, for ``linear``, see :ref:`sec:m:integer:linear`). For more information on bounds consistency over integers or real numbers, see :cite:`bounds-consistency`.

  Some propagators that are selected might not even achieve bounds consistency but the idea is that the propagator performs propagation by reasoning on the bounds of variable domains.

- ``IPL_DOM``: perform domain propagation or achieve domain consistency. Most propagators selected by ``IPL_DOM`` achieve domain consistency but some just perform propagation by taking entire variable domains for propagation into account (for example, ``circuit``, see :ref:`sec:m:integer:circuit`).

- ``IPL_DEF``: choose default propagation level for this constraint.

Whether bounds or domain consistency is achieved and the default propagation level for a constraint are mentioned in the reference documentation for each post function.

In addition to the basic propagation levels listed above, the following pre-defined values exist:

- ``IPL_BASIC``: try to optimize for execution performance at the expense of performing less propagation.

- ``IPL_ADVANCED``: try to optimize for more propagation at the expensive of being less efficient.

The propagation levels can be specified as disjunctions, for example ``IPL_DEF|IPL_BASIC`` requests basic default propagation which is equivalent to ``IPL_BASIC`` (the ``IPL_DEF`` can always be omitted). Note that in particular the combination ``IPL_BASIC|IPL_ADVANCED`` is meaningful requesting both basic and advanced propagation to be performed.

Some scheduling constraints, see :ref:`sec:m:integer:scheduling`, support basic and advanced propagation levels.

.. mpg-tip:: Different propagation levels have different costs

   Note that propagators of different propagation level for the very same constraint can have vastly different cost. In general, propagation for ``IPL_VAL`` will be cheapest, while propagation for ``IPL_DOM`` will be most expensive.


   The reference documentation for a constraint lists whether a particular propagation level might have prohibitive cost for a large number of variables or a large number of values in the variables’ domains. For example, for the ``linear`` constraint with :math:`n` variables and at most :math:`d` values for each variable, the complexity to perform bounds propagation (that is, ``IPL_BND``) is :math:`O(n)` whereas the complexity for domain propagation (that is, ``IPL_DOM``) is :math:`O(d^n)`.

.. _modeling:m-integer:exceptions:

Exceptions
~~~~~~~~~~

Many post functions check their arguments for consistency before attempting to create a propagator. For each post function, the reference documentation lists which exceptions might be thrown.

.. _modeling:m-integer:unsharing-arguments:

Unsharing arguments
~~~~~~~~~~~~~~~~~~~

Some constraints can only deal with *non-shared* variable arrays: a variable is not allowed to appear more than once in the array (more precisely: no unassigned variable implementation appears more than once in the array). An attempt to post one of these constraints with shared variable arrays will throw an exception of type `Int::ArgumentSame <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1Int_1_1ArgumentSame.html>`__.

To be able to post one of these constraints on shared variable arrays, Gecode provides a function ``unshare`` (see `Unsharing variables <https://www.gecode.dev/doc/6.4.0/reference/group__TaskModelIntUnshare.html>`__) that takes a variable argument array ``x`` as argument as in:

.. mpg-code:: snippet:m-integer:sec:m:integer:ipl:code:1
   :direct:


It replaces each but the first occurrence of a variable :math:`y` in ``x`` by a new variable :math:`z`, and creates a propagator :math:`y=z` for each new variable :math:`z`.

Note that ``unshare`` requires a variable argument array and *not* a variable array. If ``x`` is a variable array, the following

.. mpg-code:: snippet:m-integer:sec:m:integer:ipl:code:2
   :direct:


creates a variable argument array ``y`` containing the same variables as ``x``.

.. mpg-tip:: Unsharing is expensive

   It is important to keep in mind that ``unshare`` creates new variables and propagators. This is also the reason why unsharing is not done implicitly by a post function for a constraint that does not accept shared variable arrays.


   .. container:: samepage

      Consider the following example using ``extensional`` constraints for a variable argument array ``x`` possibly containing a variable more than once, where ``a`` and ``b`` are two different DFAs (see :ref:`sec:m:integer:extensional` for ``extensional`` constraints). By

      .. mpg-code:: snippet:m-integer:sec:m:integer:ipl:code:3
         :direct:

   multiple occurrences of the same variable in ``x`` are unshared *once* and the propagators for extensional can work on the same non-shared array.

   If unsharing were implicit, the following

   .. mpg-code:: snippet:m-integer:sec:m:integer:ipl:code:4
      :direct:

   would unshare ``x`` twice and create many more (useless) propagators and variables. Rather than implicitly unsharing the same array over and over again (and hence creating variables and propagators), unsharing is made explicit and should be done only once, if possible.

.. _sec:m:integer:post:


.. _modeling:m-integer:constraint-overview:

Constraint overview
-------------------

This section provides an overview of the constraints and their post functions available for integer and Boolean variables.

.. _sec:m:integer:dom:


.. _modeling:m-integer:domain-constraints:

Domain constraints
~~~~~~~~~~~~~~~~~~

`Domain constraints <https://www.gecode.dev/doc/6.4.0/reference/group__TaskModelIntDomain.html>`__ constrain integer variables and variable arrays to values from a given domain. For example, by

.. mpg-code:: snippet:m-integer:sec:m:integer:dom:code:1
   :direct:


the values of the variable ``x`` (or of all variables in a variable array ``x``) are constrained to be between :math:`2` and :math:`12`. Domain constraints also take integers (assigning variables to the integer value) and integer sets of type `IntSet <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1IntSet.html>`__. For example,

.. mpg-code:: snippet:m-integer:sec:m:integer:dom:code:2
   :direct:


constrains the variable ``x`` (or, the variables in ``x``) to take values from the set :math:`\{-7,-3,1,5\}` (see also GCCat: `domain <http://www.emn.fr/z-info/sdemasse/gccat/Cdomain.html>`__, `in <http://www.emn.fr/z-info/sdemasse/gccat/Cin.html>`__, `in_interval <http://www.emn.fr/z-info/sdemasse/gccat/Cin_interval.html>`__, `in_intervals <http://www.emn.fr/z-info/sdemasse/gccat/Cin_intervals.html>`__, `in_set <http://www.emn.fr/z-info/sdemasse/gccat/Cin_set.html>`__).

Note that there are no domain constraints for Boolean variables, please use relation constraints instead, see :ref:`sec:m:integer:rel:bool`.

The domain of an integer or Boolean variable ``x`` can be constrained according to the domain of another variable ``d`` by

.. mpg-code:: snippet:m-integer:sec:m:integer:dom:code:3
   :direct:


Here, ``x`` and ``d`` can also be arrays of integer or Boolean variables. Note that this needs to be used carefully, the domain to which the variable ``x`` is constrained depends on the domain to which ``d`` is constrained. Only use this constraint post function if you are sure that all propagation that could influence the domain of ``d`` has been performed!

Domain constraints for a single variable also support reification. For examples using domain constraints, see `n-Knight’s tour (simple model) <https://www.gecode.dev/doc/6.4.0/reference/examples_2knights_8cpp.html>`__ and `Packing squares into a rectangle <https://www.gecode.dev/doc/6.4.0/reference/perfect-square_8cpp.html>`__.

.. _sec:m:integer:member:


.. _modeling:m-integer:membership-constraints:

Membership constraints
~~~~~~~~~~~~~~~~~~~~~~

`Membership constraints <https://www.gecode.dev/doc/6.4.0/reference/group__TaskModelIntMember.html>`__ constrain integer or Boolean variables to be included in an array of integer or Boolean variables. That is, for an integer variable array ``x`` and an integer variable ``y``, the constraint

.. mpg-code:: snippet:m-integer:sec:m:integer:member:code:1
   :direct:


forces that ``y`` is included in ``x``:

.. math:: \mathtt{y}\in\left\{\mathtt{x}_0,\ldots,\mathtt{x}_{|\mathtt{x}|-1}\right\}

As mentioned, ``x`` and ``y`` can also be Boolean variables. Membership constraints also support reification.

.. _sec:m:integer:rel:int:


.. _modeling:m-integer:simple-relation-constraints-over-integer-variables:

Simple relation constraints over integer variables
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. mpg-figure:: Integer relation types
   :name: fig:m:integer:irt

   .. container:: center

      +------------+-----------------------------------------+------------+--------------------------------------------+
      | ``IRT_EQ`` | equality (:math:`=`)                    | ``IRT_NQ`` | disequality (:math:`\neq`)                 |
      +------------+-----------------------------------------+------------+--------------------------------------------+
      | ``IRT_LE`` | strictly less inequality (:math:`<`)    | ``IRT_LQ`` | less or equal inequality (:math:`\leq`)    |
      +------------+-----------------------------------------+------------+--------------------------------------------+
      | ``IRT_GR`` | strictly greater inequality (:math:`>`) | ``IRT_GQ`` | greater or equal inequality (:math:`\geq`) |
      +------------+-----------------------------------------+------------+--------------------------------------------+

`Simple relation constraints over integer variables <https://www.gecode.dev/doc/6.4.0/reference/group__TaskModelIntRelInt.html>`__ enforce relations between integer variables and between integer variables and integer values. The relation depends on an integer relation type ``IntRelType`` (see `Simple relation constraints over integer variables <https://www.gecode.dev/doc/6.4.0/reference/group__TaskModelIntRelInt.html>`__). :numref:`fig:m:integer:irt` lists the available integer relation types and their meaning.

.. _modeling:m-integer:binary-relation-constraints:

.. rubric:: Binary relation constraints.

Assume that ``x`` and ``y`` are integer variables. Then

.. mpg-code:: snippet:m-integer:fig:m:integer:irt:code:1
   :direct:


constrains ``x`` to be strictly less than ``y``. Similarly, by

.. mpg-code:: snippet:m-integer:fig:m:integer:irt:code:2
   :direct:


``x`` is constrained to be different from ``4``. Both variants of ``rel`` also support reification (see also GCCat: `eq <http://www.emn.fr/z-info/sdemasse/gccat/Ceq.html>`__, `neq <http://www.emn.fr/z-info/sdemasse/gccat/Cneq.html>`__, `lt <http://www.emn.fr/z-info/sdemasse/gccat/Clt.html>`__, `leq <http://www.emn.fr/z-info/sdemasse/gccat/Cleq.html>`__, `gt <http://www.emn.fr/z-info/sdemasse/gccat/Cgt.html>`__, `geq <http://www.emn.fr/z-info/sdemasse/gccat/Cgeq.html>`__).

.. _modeling:m-integer:constraints-between-variable-arrays-and-a-single-variable:

.. rubric:: Constraints between variable arrays and a single variable.

If ``x`` is an integer variable array and ``y`` is an integer variable, then

.. mpg-code:: snippet:m-integer:fig:m:integer:irt:code:3
   :direct:


constrains all variables in ``x`` to be less than or equal to ``y``. Likewise,

.. mpg-code:: snippet:m-integer:fig:m:integer:irt:code:4
   :direct:


constrains all variables in ``x`` to be larger than ``7`` (see also GCCat: `arith <http://www.emn.fr/z-info/sdemasse/gccat/Carith.html>`__).

.. _modeling:m-integer:constraints-between-array-elements:

.. rubric:: Constraints between array elements.

If ``x`` is an integer variable array, then

.. mpg-code:: snippet:m-integer:fig:m:integer:irt:code:5
   :direct:


constrains the variables in ``x`` to be sorted in increasing order as follows:

.. math::

   \mathtt{x}_0 \leq \mathtt{x}_1 \leq \cdots \leq
   \mathtt{x}_{|\mathtt x|-1}

The integer relation type values for inequalities (that is, ``IRT_LE``, ``IRT_GQ``, and ``IRT_GR``) are analogous. For an example, see :ref:`chap:c:golomb` and `Finding optimal Golomb rulers <https://www.gecode.dev/doc/6.4.0/reference/golomb-ruler_8cpp.html>`__.

.. container:: samepage

   By

   .. mpg-code:: snippet:m-integer:fig:m:integer:irt:code:6
      :direct:

   all variables in the integer variable array ``x`` are constrained to be equal:

   .. math::

      \mathtt{x}_0 = \mathtt{x}_1 = \cdots =
      \mathtt{x}_{|\mathtt x|-1}

By

.. mpg-code:: snippet:m-integer:fig:m:integer:irt:code:7
   :direct:


the variables in ``x`` are constrained to be not all equal:

.. math::

   \neg\left(\mathtt{x}_0 = \mathtt{x}_1 = \cdots =
   \mathtt{x}_{|\mathtt x|-1}\right)

For an example, see `Schur’s lemma <https://www.gecode.dev/doc/6.4.0/reference/schurs-lemma_8cpp.html>`__ (see also GCCat: `all_equal <http://www.emn.fr/z-info/sdemasse/gccat/Call_equal.html>`__, `decreasing <http://www.emn.fr/z-info/sdemasse/gccat/Cdecreasing.html>`__, `increasing <http://www.emn.fr/z-info/sdemasse/gccat/Cincreasing.html>`__, `not_all_equal <http://www.emn.fr/z-info/sdemasse/gccat/Cnot_all_equal.html>`__, `strictly_decreasing <http://www.emn.fr/z-info/sdemasse/gccat/Cstrictly_decreasing.html>`__, `strictly_increasing <http://www.emn.fr/z-info/sdemasse/gccat/Cstrictly_increasing.html>`__).

.. _modeling:m-integer:lexicographic-constraints-between-variable-arrays:

.. rubric:: Lexicographic constraints between variable arrays.

.. container:: samepage

   If ``x`` and ``y`` are integer variable arrays (where the sizes of ``x`` and ``y`` can be different),

   .. mpg-code:: snippet:m-integer:fig:m:integer:irt:code:8
      :direct:

constrains ``x`` and ``y`` such that ``x`` is lexicographically strictly smaller than ``y`` (analogously for the other inequality relations). For ``IRT_EQ`` and :math:`|\mathtt x|=|\mathtt y|`, it is propagated that :math:`\mathtt x_i=\mathtt y_i` for :math:`0\leq i<|\mathtt x|`. For ``IRT_NQ`` and :math:`|\mathtt x|=|\mathtt y|`, it is propagated that :math:`\mathtt x_i\neq \mathtt y_i` for at least one :math:`i` such that :math:`0\leq i<|\mathtt x|`. If :math:`|\mathtt x|\neq|\mathtt y|`, for ``IRT_EQ`` the space ``home`` is failed whereas for ``IRT_NQ`` the constraint is ignored (see also GCCat: `lex_greater <http://www.emn.fr/z-info/sdemasse/gccat/Clex_greater.html>`__, `lex_greatereq <http://www.emn.fr/z-info/sdemasse/gccat/Clex_greatereq.html>`__, `lex_less <http://www.emn.fr/z-info/sdemasse/gccat/Clex_less.html>`__, `lex_lesseq <http://www.emn.fr/z-info/sdemasse/gccat/Clex_lesseq.html>`__).

See `Balanced incomplete block design (BIBD) <https://www.gecode.dev/doc/6.4.0/reference/bibd_8cpp.html>`__ for an example (albeit over Boolean variables).

.. _sec:m:integer:rel:bool:


.. _modeling:m-integer:simple-relation-constraints-over-boolean-variables:

Simple relation constraints over Boolean variables
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. mpg-figure:: Boolean operation types
   :name: fig:m:integer:bot

   .. container:: center

      +-------------+-----------------------------------------+-------------+---------------------------------------+
      | ``BOT_AND`` | conjunction (:math:`\wedge`)            | ``BOT_OR``  | disjunction (:math:`\vee`)            |
      +-------------+-----------------------------------------+-------------+---------------------------------------+
      | ``BOT_IMP`` | implication (:math:`\rightarrow`)       | ``BOT_EQV`` | equivalence (:math:`\leftrightarrow`) |
      +-------------+-----------------------------------------+-------------+---------------------------------------+
      | ``BOT_XOR`` | exclusive or (:math:`\nleftrightarrow`) |             |                                       |
      +-------------+-----------------------------------------+-------------+---------------------------------------+

`Simple relation constraints over Boolean variables <https://www.gecode.dev/doc/6.4.0/reference/group__TaskModelIntRelBool.html>`__ include the same post functions as simple relation constraints over integer variables. In addition, simple relation constraints over Boolean constraints provide support for the typical Boolean operations such as conjunction and disjunction. Boolean operations are defined by values of the type ``BoolOpType`` (see `Simple relation constraints over integer variables <https://www.gecode.dev/doc/6.4.0/reference/group__TaskModelIntRelInt.html>`__). :numref:`fig:m:integer:bot` lists the available Boolean operation types.

.. container:: samepage

   For example, for Boolean variables ``x``, ``y``, and ``z``,

   .. mpg-code:: snippet:m-integer:fig:m:integer:bot:code:1
      :direct:

posts the constraint :math:`\mathtt{x}\wedge\mathtt{y}=\mathtt{z}`. Similarly,

.. mpg-code:: snippet:m-integer:fig:m:integer:bot:code:2
   :direct:


posts that :math:`\mathtt{x}\vee\mathtt{y}` must be true (see also GCCat: `and <http://www.emn.fr/z-info/sdemasse/gccat/Cand.html>`__, `equivalent <http://www.emn.fr/z-info/sdemasse/gccat/Cequivalent.html>`__, `imply <http://www.emn.fr/z-info/sdemasse/gccat/Cimply.html>`__, `or <http://www.emn.fr/z-info/sdemasse/gccat/Cor.html>`__, `xor <http://www.emn.fr/z-info/sdemasse/gccat/Cxor.html>`__).

Note that the integer value must be either zero or one, otherwise an exception of type `Int::NotZeroOne <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1Int_1_1NotZeroOne.html>`__ is thrown.

For an example, see `Balanced incomplete block design (BIBD) <https://www.gecode.dev/doc/6.4.0/reference/bibd_8cpp.html>`__.

.. mpg-tip:: Boolean negation

   Boolean negation can be easily obtained by using ``IRT_NQ`` as relation type. The constraint :math:`\mathtt{x}=\neg\mathtt{y}` for Boolean variables ``x`` and ``y`` can be posted by


   .. mpg-code:: snippet:m-integer:fig:m:integer:bot:code:3
      :direct:

.. container:: samepage

   Additional constraints are available for Boolean variable arrays. For a Boolean variable array ``x`` and a Boolean variable ``y``,

   .. mpg-code:: snippet:m-integer:fig:m:integer:bot:code:4
      :direct:

posts the constraint

.. math:: \bigvee_{i=0}^{|\mathtt x|-1}\mathtt{x}_i=\mathtt{y}

Again, ``y`` can also be ``0`` or ``1``.

Note that Boolean implication is special in that it is not associative and Gecode follows normal notational convention. Hence for a Boolean variable array ``x`` and a Boolean variable ``y``,

.. mpg-code:: snippet:m-integer:fig:m:integer:bot:code:5
   :direct:


posts the constraint

.. math::

   \mathtt{x}_0 \to \left(\mathtt{x}_1 \to
   \left(\ldots\to\left(\mathtt{x}_{|\mathtt{x}|-2}\to
   \mathtt{x}_{|\mathtt{x}|-1}\right)\right)\right)=\mathtt{y}

Again, ``y`` can also be ``0`` or ``1``.

.. _modeling:m-integer:clause-constraint:

.. rubric:: Clause constraint.

.. container:: samepage

   In order to avoid many propagators for negation, the clause constraint accepts both positive and negative Boolean variables. For Boolean variable arrays ``x`` and ``y`` and a Boolean variable ``z`` (again, ``z`` can also be ``0`` or ``1``)

   .. mpg-code:: snippet:m-integer:fig:m:integer:bot:code:6
      :direct:

posts the constraint

.. math::

   \bigwedge_{i=0}^{|\mathtt{x}|-1}\mathtt{x}_i\wedge
   \bigwedge_{i=0}^{|\mathtt{y}|-1}\neg\mathtt{y}_i=\mathtt z

(see also GCCat: `clause_and <http://www.emn.fr/z-info/sdemasse/gccat/Cclause_and.html>`__, `clause_or <http://www.emn.fr/z-info/sdemasse/gccat/Cclause_or.html>`__, `nand <http://www.emn.fr/z-info/sdemasse/gccat/Cnand.html>`__, `nor <http://www.emn.fr/z-info/sdemasse/gccat/Cnor.html>`__).

Note that only ``BOT_AND`` and ``BOT_OR`` as Boolean operation types are supported, other Boolean operations types throw an exception of type `Int::IllegalOperation <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1Int_1_1IllegalOperation.html>`__.

For an example, see `CNF SAT solver <https://www.gecode.dev/doc/6.4.0/reference/sat_8cpp.html>`__.

.. _modeling:m-integer:if-then-else-constraint:

.. rubric:: If-then-else constraint.

An if-then-else constraint can be posted by

.. mpg-code:: snippet:m-integer:fig:m:integer:bot:code:7
   :direct:


where ``b`` is a Boolean variable and ``x``, ``y``, and ``z`` are integer or Boolean variables. In case ``b`` is one, then :math:`\mathtt{x}=\mathtt{z}` must hold, otherwise :math:`\mathtt{y}=\mathtt{z}` must hold.

.. _sec:m:integer:arithmetic:


.. _modeling:m-integer:arithmetic-constraints:

Arithmetic constraints
~~~~~~~~~~~~~~~~~~~~~~

.. mpg-figure:: Arithmetic constraints (``x``, ``y``, ``z``, ``d``, and ``m`` are integer variables; ``n`` is an integer)
   :name: fig:m:integer:arithmetic

   .. container:: center

      +-------------------------------+-------------------------------------------------------------------------------------------+-----+-----+-----------------------------------------------------------------------------+
      | post function                 | constraint posted                                                                         | bnd | dom | GCCat                                                                       |
      +===============================+===========================================================================================+=====+=====+=============================================================================+
      | ``min(home, x, y, z);``       | :math:`\min(\mathtt x, \mathtt y)=\mathtt z`                                              | yes | yes | `minimum <http://www.emn.fr/z-info/sdemasse/gccat/Cminimum.html>`__         |
      +-------------------------------+-------------------------------------------------------------------------------------------+-----+-----+-----------------------------------------------------------------------------+
      | ``max(home, x, y, z);``       | :math:`\max(\mathtt x, \mathtt y)=\mathtt z`                                              | yes | yes | `maximum <http://www.emn.fr/z-info/sdemasse/gccat/Cmaximum.html>`__         |
      +-------------------------------+-------------------------------------------------------------------------------------------+-----+-----+-----------------------------------------------------------------------------+
      | ``abs(home, x, y);``          | :math:`|\mathtt x|=\mathtt y`                                                             | yes | yes | `abs_value <http://www.emn.fr/z-info/sdemasse/gccat/Cabs_value.html>`__     |
      +-------------------------------+-------------------------------------------------------------------------------------------+-----+-----+-----------------------------------------------------------------------------+
      | ``mult(home, x, y, z);``      | :math:`\mathtt x \cdot \mathtt y=\mathtt z`                                               | yes | yes |                                                                             |
      +-------------------------------+-------------------------------------------------------------------------------------------+-----+-----+-----------------------------------------------------------------------------+
      | ``sqr(home, x, y);``          | :math:`{\mathtt x}^2=\mathtt y`                                                           | yes | yes |                                                                             |
      +-------------------------------+-------------------------------------------------------------------------------------------+-----+-----+-----------------------------------------------------------------------------+
      | ``sqrt(home, x, y);``         | :math:`\lfloor\sqrt{\mathtt x}\rfloor=\mathtt y`                                          | yes | yes |                                                                             |
      +-------------------------------+-------------------------------------------------------------------------------------------+-----+-----+-----------------------------------------------------------------------------+
      | ``pow(home, x, n, y);``       | :math:`{\mathtt x}^{\mathtt n}=\mathtt y`                                                 | yes | yes |                                                                             |
      +-------------------------------+-------------------------------------------------------------------------------------------+-----+-----+-----------------------------------------------------------------------------+
      | ``nroot(home, x, n, y);``     | :math:`\lfloor\sqrt[{\mathtt n}]{\mathtt x}\rfloor=\mathtt y`                             | yes | yes |                                                                             |
      +-------------------------------+-------------------------------------------------------------------------------------------+-----+-----+-----------------------------------------------------------------------------+
      | ``div(home, x, y, z);``       | :math:`\mathtt{x} \div \mathtt{y}=\mathtt{z}`                                             | yes |     |                                                                             |
      +-------------------------------+-------------------------------------------------------------------------------------------+-----+-----+-----------------------------------------------------------------------------+
      | ``mod(home, x, y, z);``       | :math:`\mathtt{x} \bmod \mathtt{y}=\mathtt{z}`                                            | yes |     |                                                                             |
      +-------------------------------+-------------------------------------------------------------------------------------------+-----+-----+-----------------------------------------------------------------------------+
      | ``divmod(home, x, y, d, m);`` | :math:`\mathtt{x} \div \mathtt{y}=\mathtt{d}\wedge\mathtt{x} \bmod \mathtt{y}=\mathtt{m}` | yes |     |                                                                             |
      +-------------------------------+-------------------------------------------------------------------------------------------+-----+-----+-----------------------------------------------------------------------------+

`Arithmetic constraints <https://www.gecode.dev/doc/6.4.0/reference/group__TaskModelIntArith.html>`__ exist only over integer variables. In addition to the constraints summarized in :numref:`fig:m:integer:arithmetic` (bnd abbreviates bounds consistency and dom abbreviates domain consistency), the minimum and maximum constraints are also available for integer variable arrays. That is, for an integer variable array ``x`` and an integer variable ``y``

.. mpg-code:: snippet:m-integer:fig:m:integer:arithmetic:code:1
   :direct:


constrains ``y`` to be the minimum of the variables in ``x`` (``max`` is analogous) (see also GCCat: `min <http://www.emn.fr/z-info/sdemasse/gccat/Cmin.html>`__, `max <http://www.emn.fr/z-info/sdemasse/gccat/Cmax.html>`__).

Also constraints for the arguments of minimum and maximum are available. For an integer variable array ``x`` and an integer variable ``y``

.. mpg-code:: snippet:m-integer:fig:m:integer:arithmetic:code:2
   :direct:


constrains ``y`` to be :math:`\argmin(\mathtt{x})`, that is, the element in ``x`` at position ``y`` is equal to :math:`\min(\mathtt{x})` (see also GCCat: `min_index <http://www.emn.fr/z-info/sdemasse/gccat/Cmin_index.html>`__). By default, ``argmin`` uses tie-breaking and constrains ``y`` to be the first position of the minimum in ``x``. By posting

.. mpg-code:: snippet:m-integer:fig:m:integer:arithmetic:code:3
   :direct:


no tie-breaking is used. Of course, ``argmax`` is analogous. ``argmin`` and ``argmax`` without tie-breaking are domain consistent (see also GCCat: `max_index <http://www.emn.fr/z-info/sdemasse/gccat/Cmax_index.html>`__).

.. _sec:m:integer:linear:


.. _modeling:m-integer:linear-constraints:

Linear constraints
~~~~~~~~~~~~~~~~~~

`Linear constraints over integer variables <https://www.gecode.dev/doc/6.4.0/reference/group__TaskModelIntLI.html>`__ and `Linear constraints over Boolean variables <https://www.gecode.dev/doc/6.4.0/reference/group__TaskModelIntLB.html>`__ provide essentially the same post functions for integer and Boolean constraints (to be discussed below). The most general variant

.. mpg-code:: snippet:m-integer:sec:m:integer:linear:code:1
   :direct:


posts the linear constraint

.. math::

   \sum_{i=0}^{|\mathtt x|-1} \mathtt{a}_i \cdot \mathtt{x}_i =
   \mathtt c

with integer coefficients ``a`` (of type ``IntArgs``), integer variables ``x``, and an integer constant ``c``. Note that ``a`` and ``x`` must have the same size. Of course, all other integer relation types are supported, see :numref:`fig:m:integer:irt` for a table of integer relation types. Multiple occurrences of the same variable in ``x`` are explicitly allowed and common terms :math:`a\cdot y` and :math:`b\cdot y` for the same variable :math:`y` are rewritten to :math:`(a+b)\cdot y` to increase propagation. For an example, see :ref:`sec:m:started:first`.

.. container:: samepage

   The array of coefficients can be omitted if all coefficients are one. That is,

   .. mpg-code:: snippet:m-integer:sec:m:integer:linear:code:2
      :direct:

   posts the linear constraint

   .. math:: \sum_{i=0}^{|\mathtt x|-1} \mathtt{x}_i > \mathtt c

   for a variable array ``x`` and an integer ``c``.

Instead of an integer constant ``c`` as the right-hand side of the linear constraint, an integer variable can be used as well. This is true for linear constraints over both integer and Boolean variables: the right-hand side is always an integer value or an integer variable, even if the left-hand side involves Boolean variables. For example, when assuming that ``x`` is an array of Boolean variables,

.. mpg-code:: snippet:m-integer:sec:m:integer:linear:code:3
   :direct:


imposes the constraint that there are at least ``y`` ones among the Boolean variables in ``x``.

All variants of ``linear`` support reification and exist in variants that perform both bounds propagation (the default) and domain propagation (see also GCCat: `scalar_product <http://www.emn.fr/z-info/sdemasse/gccat/Cscalar_product.html>`__, `sum_ctr <http://www.emn.fr/z-info/sdemasse/gccat/Csum_ctr.html>`__).

.. _sec:m:integer:distinct:


.. _modeling:m-integer:distinct-constraints:

Distinct constraints
~~~~~~~~~~~~~~~~~~~~

The ``distinct`` constraint (see `Distinct constraints <https://www.gecode.dev/doc/6.4.0/reference/group__TaskModelIntDistinct.html>`__) enforces that integer variables take pairwise distinct values (also known as ``alldifferent`` constraint). Obviously, ``distinct`` does not exist for Boolean variables.

.. container:: samepage

   Posting

   .. mpg-code:: snippet:m-integer:sec:m:integer:distinct:code:1
      :direct:

constrains all variables in ``x`` to be pairwise different.

.. container:: samepage

   Posting

   .. mpg-code:: snippet:m-integer:sec:m:integer:distinct:code:2
      :direct:

for an array of integer values ``c`` (of type ``IntArgs``) and an array of integer variables ``x`` of same size, constrains the variables in ``x`` such that

.. math::

   \mathtt{x}_i+\mathtt{c}_i \neq\mathtt{x}_j+\mathtt{c}_j
   \qquad\mbox{for }0\leq i,j< |\mathtt{x}|\mbox{ and }i\neq j

Additionally, two variants of ``distinct`` are available where not all variables need to be pairwise different. Posting

.. mpg-code:: snippet:m-integer:sec:m:integer:distinct:code:3
   :direct:


for an array of integer variables ``x`` and an integer value ``c`` constrains all variables in ``x`` to be different or equal to ``c``:

.. math::

   \mathtt{x}_i=\mathtt{c}\vee\mathtt{x}_j=\mathtt{c}\vee\mathtt{x}_i \neq\mathtt{x}_j
   \qquad\mbox{for }0\leq i,j< |\mathtt{x}|\mbox{ and }i\neq j

For an array of Boolean variables ``b`` and an array of integer variables ``x`` of same size, posting

.. mpg-code:: snippet:m-integer:sec:m:integer:distinct:code:4
   :direct:


constrains all variables in ``x`` to be different provided the respective Boolean variable is one:

.. math::

   \mathtt{b}_i=0\vee\mathtt{b}_j=0\vee\mathtt{x}_i \neq\mathtt{x}_j
   \qquad\mbox{for }0\leq i,j< |\mathtt{x}|\mbox{ and }i\neq j

Gecode offers value (the default), bounds (based on :cite:`distinctbnd`), and domain propagation (based on :cite:`Regin94`) for ``distinct`` (see also GCCat: `alldifferent <http://www.emn.fr/z-info/sdemasse/gccat/Calldifferent.html>`__, `alldifferent_cst <http://www.emn.fr/z-info/sdemasse/gccat/Calldifferent_cst.html>`__, `alldifferent_except_0 <http://www.emn.fr/z-info/sdemasse/gccat/Calldifferent_except_0.html>`__).

For examples, see in particular :ref:`chap:c:golomb`, `n-Queens puzzle <https://www.gecode.dev/doc/6.4.0/reference/queens_8cpp.html>`__, and `Crowded chessboard <https://www.gecode.dev/doc/6.4.0/reference/crowded-chess_8cpp.html>`__.

.. _sec:m:integer:count:


.. _modeling:m-integer:counting-constraints:

Counting constraints
~~~~~~~~~~~~~~~~~~~~

.. _modeling:m-integer:counting-single-values:

.. rubric:: Counting single values.

`Counting constraints <https://www.gecode.dev/doc/6.4.0/reference/group__TaskModelIntCount.html>`__ count how often values are taken by an array of integer variables. The simplest case is

.. mpg-code:: snippet:m-integer:sec:m:integer:count:code:1
   :direct:


which constrains ``z`` to be equal (controlled by ``IRT_EQ``, all integer relation types are supported, see :numref:`fig:m:integer:irt`) to the number of integer variables in ``x`` that are equal to ``y``. Here ``y`` and ``z`` can be integer variables as well as integer values (see also GCCat: `atleast <http://www.emn.fr/z-info/sdemasse/gccat/Catleast.html>`__, `atmost <http://www.emn.fr/z-info/sdemasse/gccat/Catmost.html>`__, `count <http://www.emn.fr/z-info/sdemasse/gccat/Ccount.html>`__, `exactly <http://www.emn.fr/z-info/sdemasse/gccat/Cexactly.html>`__).

The ``count`` constraints also support counting how many integer variables are included in an integer set. If ``y`` is an integer set, then

.. mpg-code:: snippet:m-integer:sec:m:integer:count:code:2
   :direct:


constrains ``z`` to be equal to the number of integer variables in ``x`` that are included in ``y`` (see also GCCat: `among <http://www.emn.fr/z-info/sdemasse/gccat/Camong.html>`__, `among_var <http://www.emn.fr/z-info/sdemasse/gccat/Camong_var.html>`__, `counts <http://www.emn.fr/z-info/sdemasse/gccat/Ccounts.html>`__).

The following

.. mpg-code:: snippet:m-integer:sec:m:integer:count:code:3
   :direct:


where ``x`` is an array of integer variables and ``c`` is an array of integers (of type ``IntArgs``) with same size and ``z`` is an integer variable or value, constrains ``z`` to how often :math:`\mathtt{x}_i=\mathtt{c}_i`, that is

.. math:: \mathtt{z}=\#\{i\in\{0,\ldots,|\mathtt{x}|-1\}\mid\mathtt{x}_i=\mathtt{c}_i\}

Here, :math:`\#s` denotes the cardinality (number of elements) of a set :math:`s`.

.. _modeling:m-integer:counting-multiple-values:

.. rubric:: Counting multiple values.

The ``count`` constraint also supports counting multiple values (also known as gcc, or *g*\ lobal *c*\ ardinality *c*\ onstraint). Suppose that ``x`` and ``y`` (the *counting variables*) are two integer variable arrays (not necessarily of the same size). Then

.. mpg-code:: snippet:m-integer:sec:m:integer:count:code:4
   :direct:


posts the constraints that the number of variables in ``x`` that are equal to a value :math:`j` is :math:`\mathtt{y}_j` (for :math:`0\leq j<|\mathtt y|`):

.. math::

   \#\{i\in\{0,\ldots,|\mathtt{x}|-1\}\mid\mathtt{x}_i=j\}=\mathtt{y}_j
   \qquad\mbox{for }0\leq j<|\mathtt{y}|

and that no other values are taken by ``x``:

.. math::

   \bigcup_{i=0}^{|\mathtt{x}|-1} \{\mathtt{x}_i\} =
   \{0,\ldots,|\mathtt y|-1\}

Rather than using counting variables, one can also use an array of integer sets (``IntSetArgs``). Then the number of values taken must be included in each individual set.

A more general variant also takes into account that the values under consideration are non contiguous but are defined by an additional array of integer values. Suppose that ``x`` and ``y`` (the counting variables) are two integer variable arrays (not necessarily of the same size) and ``c`` is an array of integers with the same size as ``y``.

.. container:: samepage

   Then,

   .. mpg-code:: snippet:m-integer:sec:m:integer:count:code:5
      :direct:

   posts the constraints that the number of variables in ``x`` that are equal to the value :math:`\mathtt{c}_j` is :math:`\mathtt{y}_j` (for :math:`0\leq j<|\mathtt y|`):

   .. math::

      \#\{i\in\{0,\ldots,|\mathtt{x}|-1\}\mid\mathtt{x}_i=\mathtt{c}_j\}
      =\mathtt{y}_j
      \qquad\mbox{for }0\leq j<|\mathtt{y}|

   and that no other values but those in ``c`` are taken by ``x``:

   .. math::

      \bigcup_{i=0}^{|\mathtt{x}|-1} \{\mathtt{x}_i\} =
      \bigcup_{i=0}^{|\mathtt{c}|-1} \{\mathtt{c}_i\}

   Again, ``y`` can also be an array of integer sets, where equality :math:`=` is replaced by set inclusion :math:`\in`.

A slightly simpler variant replaces the cardinality variables by a single integer set. That is, for an array of integer variables ``x``, an integer set ``d``, and an array of integer values ``c``

.. mpg-code:: snippet:m-integer:sec:m:integer:count:code:6
   :direct:


posts the constraints that the number of variables in ``x`` that are equal to the value :math:`\mathtt{c}_j` is included in :math:`\mathtt{d}` (for :math:`0\leq j<|\mathtt c|`):

.. math::

   \#\{i\in\{0,\ldots,|\mathtt{x}|-1\}\mid\mathtt{x}_i=\mathtt{c}_j\}
      \in\mathtt{d}
   \qquad\mbox{for }0\leq j<|\mathtt{c}|

and that no other values but those in ``c`` are taken by ``x``:

.. math::

   \bigcup_{i=0}^{|\mathtt{x}|-1} \{\mathtt{x}_i\} =
   \bigcup_{i=0}^{|\mathtt{c}|-1} \{\mathtt{c}_i\}

The last variant of ``count`` clarifies that ``count`` is a generalization of ``distinct`` (see :ref:`sec:m:integer:distinct`): ``distinct`` constrains a value to occur at most once, whereas ``count`` offers more flexibility to constrain which values and how often these values can occur.

.. container:: samepage

   For example, if we know that the variables in the variable array ``x`` take values between ``0`` and ``n-1``, then

   .. mpg-code:: snippet:m-integer:sec:m:integer:count:code:7
      :direct:

is equivalent to

.. mpg-code:: snippet:m-integer:sec:m:integer:count:code:8
   :direct:


Counting constraints only support integer variables, ``linear`` constraints can be used for Boolean variables, see :ref:`sec:m:integer:linear`. For examples, see the case studies in :ref:`chap:c:magicsequence` and :ref:`chap:c:warehouses` or the examples `Crowded chessboard <https://www.gecode.dev/doc/6.4.0/reference/crowded-chess_8cpp.html>`__ and `Magic sequence <https://www.gecode.dev/doc/6.4.0/reference/magic-sequence_8cpp.html>`__.

Note that Gecode implements the semantics of the original paper on the global cardinality constraint by Régin :cite:`DBLP:conf/aaai/Regin96`, where no other values except those specified may occur. This differs from the semantics in the Global Constraint Catalog :cite:`GlobalConstraintCatalog`, where values that are not mentioned can occur arbitrarily often.

Gecode offers value (the default), bounds (based on :cite:`gccbnd`), and domain propagation (based on :cite:`DBLP:conf/aaai/Regin96`) for the global ``count`` constraint (see also GCCat: `global_cardinality <http://www.emn.fr/z-info/sdemasse/gccat/Cglobal_cardinality.html>`__).

.. _sec:m:integer:nvalues:


.. _modeling:m-integer:number-of-values-constraints:

Number of values constraints
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

`Number of values constraints <https://www.gecode.dev/doc/6.4.0/reference/group__TaskModelIntNValues.html>`__ constrain how many values can be taken by an array of variables.

Assume that ``x`` is an array of integer variables and ``y`` is an integer variable. Then

.. mpg-code:: snippet:m-integer:sec:m:integer:nvalues:code:1
   :direct:


constrains the number of distinct values in ``x`` to be equal to ``y``, that is

.. math:: \#\{\mathtt{x}_0,\ldots,\mathtt{x}_{|\mathtt{x}|-1}\}=\mathtt y

.. container:: samepage

   Instead of ``IRT_EQ`` any other integer relation type can be used, see :numref:`fig:m:integer:irt` for an overview. For example,

   .. mpg-code:: snippet:m-integer:sec:m:integer:nvalues:code:2
      :direct:

constrains the number of distinct values in ``x`` to be less than or equal to ``y``. The array ``x`` can also be an array of Boolean variables and ``y`` can be an integer value.

The constraint is implemented by the propagators introduced in :cite:`nvalue` (see also GCCat: `nvalue <http://www.emn.fr/z-info/sdemasse/gccat/Cnvalue.html>`__, `nvalues <http://www.emn.fr/z-info/sdemasse/gccat/Cnvalues.html>`__). For an example using the ``nvalues`` constraint, see `Dominating Queens <https://www.gecode.dev/doc/6.4.0/reference/dominating-queens_8cpp.html>`__.

.. _sec:m:integer:sequence:


.. _modeling:m-integer:sequence-constraints:

Sequence constraints
~~~~~~~~~~~~~~~~~~~~

`Sequence constraints <https://www.gecode.dev/doc/6.4.0/reference/group__TaskModelIntSequence.html>`__ constrain how often values are taken by repeated subsequences of variables in an array of integer or Boolean variables. By

.. mpg-code:: snippet:m-integer:sec:m:integer:sequence:code:1
   :direct:


where ``x`` is an array of integer or Boolean variables, ``s`` is an integer set, and ``q``, ``l``, and ``u`` are integers, all subsequences of length ``q`` in the variable array ``x``, that is, the sequences

.. math::

   \begin{array}{c}
   \langle \mathtt{x}_0,\ldots,\mathtt{x}_{\mathtt{q}+0-1} \rangle\\
   \langle \mathtt{x}_1,\ldots,\mathtt{x}_{\mathtt{q}+1-1} \rangle\\
   \cdots\\
   \langle \mathtt{x}_{|\mathtt{x}|-\mathtt{q}},\ldots,\mathtt{x}_{|\mathtt{x}|-1} \rangle\\
   \end{array}

are constrained such that at least ``l`` and at most ``u`` variables in each subsequence are assigned to values from the integer set ``s``.

In more mathematical notation, the constraint enforces

.. math::

   \bigwedge_{i=0}^{|\mathtt{x}|-\mathtt{q}}
          \operatorname{among}(\langle
          \mathtt{x}_i,\ldots,\mathtt{x}_{i+\mathtt{q}-1}\rangle,
          \mathtt{s},\mathtt{l},\mathtt{u})

where the :math:`\operatorname{among}` constraint for the subsequence starting at position :math:`i` is defined as

.. math:: l\leq\#\{j\in\{i,\ldots,i+\mathtt{q}-1\}\;|\;x_j\in \mathtt{s}\} \leq u

The constraint is implemented by the domain consistent propagator introduced in :cite:`DBLP:journals/constraints/HoevePRS09` (see also GCCat: `among_seq <http://www.emn.fr/z-info/sdemasse/gccat/Camong_seq.html>`__). For an example, see `Car sequencing <https://www.gecode.dev/doc/6.4.0/reference/car-sequencing_8cpp.html>`__.

.. _sec:m:integer:channel:


.. _modeling:m-integer:channel-constraints:

Channel constraints
~~~~~~~~~~~~~~~~~~~

`Channel constraints <https://www.gecode.dev/doc/6.4.0/reference/group__TaskModelIntChannel.html>`__ channel Boolean to integer variables and integer variables to integer variables.

.. _modeling:m-integer:channeling-integer-variables:

.. rubric:: Channeling integer variables.

For two integer variable arrays ``x`` and ``y`` of same size,

.. mpg-code:: snippet:m-integer:sec:m:integer:channel:code:1
   :direct:


posts the constraint

.. math::

   \mathtt{x}_i=j\iff\mathtt{y}_j=i
   \qquad\mbox{for }0\leq i,j<|\mathtt x|

(see also GCCat: `inverse <http://www.emn.fr/z-info/sdemasse/gccat/Cinverse.html>`__). The ``channel`` constraint between two integer variable arrays also supports integer offsets. For integers ``n`` and ``m``,

.. mpg-code:: snippet:m-integer:sec:m:integer:channel:code:2
   :direct:


posts the constraint

.. math::

   \mathtt{x}_i-\mathtt n=j\iff\mathtt{y}_j-\mathtt m=i
   \qquad\mbox{for }0\leq i,j<|\mathtt x|

(see also GCCat: `inverse_offset <http://www.emn.fr/z-info/sdemasse/gccat/Cinverse_offset.html>`__). For examples, see `n-Knight’s tour (simple model) <https://www.gecode.dev/doc/6.4.0/reference/examples_2knights_8cpp.html>`__ and `Black hole patience <https://www.gecode.dev/doc/6.4.0/reference/black-hole_8cpp.html>`__.

.. _modeling:m-integer:channeling-between-integer-and-boolean-variables:

.. rubric:: Channeling between integer and Boolean variables.

As integer and Boolean variables are unrelated (see :ref:`sec:m:integer:var`), the only way to express that a Boolean variable ``x`` is equal to an integer variable ``y`` is by posting either

.. mpg-code:: snippet:m-integer:sec:m:integer:channel:code:3
   :direct:


.. container:: samepage

   or

.. mpg-code:: snippet:m-integer:sec:m:integer:channel:code:4
   :direct:

The ``channel`` constraint can also map an integer variable ``y`` to an array of Boolean variables ``x``. The constraint

.. math:: \mathtt{x}_i=1 \iff \mathtt y = i\qquad\mbox{for }0\leq i<|x|

is posted by

.. mpg-code:: snippet:m-integer:sec:m:integer:channel:code:5
   :direct:


(see also GCCat: `domain_constraint <http://www.emn.fr/z-info/sdemasse/gccat/Cdomain_constraint.html>`__). Note that an optional offset argument is supported. The constraint

.. math:: \mathtt{x}_i=1 \iff \mathtt y = i+\mathtt n\qquad\mbox{for }0\leq i<|x|

for an integer value ``n`` is posted by

.. mpg-code:: snippet:m-integer:sec:m:integer:channel:code:6
   :direct:


For an example, see `Pentominoes <https://www.gecode.dev/doc/6.4.0/reference/pentominoes_8cpp.html>`__.

.. _sec:m:integer:element:


.. _modeling:m-integer:element-constraints:

Element constraints
~~~~~~~~~~~~~~~~~~~

`Element constraints <https://www.gecode.dev/doc/6.4.0/reference/group__TaskModelIntElement.html>`__ generalize array access to integer variables. For example,

.. mpg-code:: snippet:m-integer:sec:m:integer:element:code:1
   :direct:


constrains the integer variable ``y`` to be the element of the array ``c`` at index ``x`` (where the array starts at index ``0`` as is common in C++).

The index variable ``x`` is always an integer variable, but the array ``c`` can also be an array of integer variables, Boolean variables, or an array of integers between ``0`` and ``1``. The result variable ``y`` must be a Boolean variable or an integer between ``0`` and ``1`` if the array is an array of Boolean variables. It can be a Boolean variable if all integer values in the array are between ``0`` and ``1``.

Even if bounds propagation is requested for the ``element`` constraint, the propagators for ``element`` always perform domain reasoning on the index variable (see also GCCat: `elem <http://www.emn.fr/z-info/sdemasse/gccat/Celem.html>`__, `element <http://www.emn.fr/z-info/sdemasse/gccat/Celement.html>`__). For examples, see the case study in :ref:`chap:c:warehouses` or the examples `Steel-mill slab design problem <https://www.gecode.dev/doc/6.4.0/reference/steel-mill_8cpp.html>`__ and `Travelling salesman problem (TSP) <https://www.gecode.dev/doc/6.4.0/reference/tsp_8cpp.html>`__.

.. _tip:m:integer:sharedelement:

.. mpg-tip:: Shared integer arrays

   When checking the documentation for `Element constraints <https://www.gecode.dev/doc/6.4.0/reference/group__TaskModelIntElement.html>`__ it might come at a surprise that element constraints do not take integer argument arrays of type ``IntArgs`` but *shared integer arrays* of type ``IntSharedArray`` as argument. The reason is that the very same shared integer array can be used for several element constraints.


   Consider the following example

   .. mpg-code:: snippet:m-integer:tip:m:integer:sharedelement:code:1
      :direct:

   where ``x``, ``y``, ``a``, and ``b`` are integer variables. Then, each time an element constraint is posted, a new shared integer array is created implicitly (that is, in the example above, two arrays are created). If the integer array is large or many element constraints are posted, it is beneficial to explicitly create a shared integer array, such as in:

   .. mpg-code:: snippet:m-integer:tip:m:integer:sharedelement:code:2
      :direct:

   Here only a single shared arrays is created and is used for both propagators created for posting the element constraints.

   What is also obvious from the first example is that integer argument arrays of type ``IntArgs`` can automatically be coerced to integer shared arrays of type ``IntSharedArray``. Hence, if performance is not that important, you do not even need to know that shared integer arrays exist.

   For an example that uses shared integer arrays together with element constraints, see :ref:`chap:c:crossword` and `Crossword puzzle <https://www.gecode.dev/doc/6.4.0/reference/crossword_8cpp.html>`__.

..

.. mpg-tip:: Shared arrays also provide STL-style iterators

   Shared arrays also support STL-style (Standard Template Library) iterators, similar to other arrays provided by Gecode, see :ref:`sec:m:integer:stl`.


.. _sec:m:integer:extensional:


.. _modeling:m-integer:extensional-constraints:

Extensional constraints
~~~~~~~~~~~~~~~~~~~~~~~

`Extensional constraints <https://www.gecode.dev/doc/6.4.0/reference/group__TaskModelIntExt.html>`__ (also known as user-defined or ad-hoc constraints) provide constraints that are specified in *extension*. The extension can be either defined by a `DFA <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1DFA.html>`__ (deterministic finite automaton) or a tuple set `TupleSet <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1TupleSet.html>`__. DFAs can also be specified conveniently by regular expressions, see :ref:`sec:m:minimodel:reg`.

.. _modeling:m-integer:deterministic-finite-automata:

.. rubric:: Deterministic finite automata.

Suppose we want to plan the activities of an evening that follows the Swedish drinking protocol: you may have as many drinks as you like, but now and then you sing a song after which you have to have a drink. We want to constrain an array of activities (Boolean or integer variables) such that the activities (drinking and singing) follow the protocol.

.. figure:: /figures/fig-m-integer-dfa.svg
   :name: fig:m:integer:dfa

   A DFA for the Swedish drinking protocol

The DFA in :numref:`fig:m:integer:dfa` specifies legal sequences of activities according to the Swedish drinking protocol, where the state :math:`0` is the start state and also the final state. The symbol ``0`` corresponds to drinking, whereas ``1`` corresponds to singing. That is, the sequence of activities must be a string of ``0``\ s and ``1``\ s accepted by the DFA.

.. container:: samepage

   The `DFA <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1DFA.html>`__ ``d`` is initialized by

   .. mpg-code:: snippet:m-integer:fig:m:integer:dfa:code:1
      :direct:

The array of transitions ``t`` is initialized by triples of integers (of type `DFA::Transition <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1DFA_1_1Transition.html>`__). A triple :math:`\{a,s,b\}` defines a transition from state :math:`a` to state :math:`b` with symbol :math:`s`. States are denoted by non-negative integers and symbols are integer values (as always, restricted to integer values that can be taken on by an integer variable, see :ref:`sec:m:integer:limits`). A transition where :math:`a` is :math:`-1` marks the last transition in a transition array. The array of final states ``f`` lists all final states of the DFA, where the array is terminated by :math:`-1`. The first argument of the constructor of the DFA defines the start state.

Constraining an array of variables for four activities to the Swedish drinking protocol is done by

.. mpg-code:: snippet:m-integer:fig:m:integer:dfa:code:2
   :direct:


Note that the same DFA would also work with an array of integer variables.

The propagator for the ``extensional`` constraint is domain consistent and is based on :cite:`Pesant:CP:2004`.

Examples that use regular expressions for defining DFAs can be found in :ref:`sec:m:minimodel:reg`.

.. _modeling:m-integer:tuple-sets-tables:

.. rubric:: Tuple sets (tables).

Constraints can also be defined by a list of tuples, where each tuple defines one solution of the extensional constraint. For example, the following defines the Swedish drinking protocol for three activities by a list of tuples:

.. mpg-code:: snippet:m-integer:fig:m:integer:dfa:code:3
   :direct:


Constraining an array of variables for three activities to the Swedish drinking protocol is done by

.. mpg-code:: snippet:m-integer:fig:m:integer:dfa:code:4
   :direct:


Note that before a tuple set can be used by a post function, it must be finalized as shown above. If a not-yet finalized tuple set is used for posting a constraint, an exception of type `Int::NotYetFinalized <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1Int_1_1NotYetFinalized.html>`__ is thrown.

The above example can be written more concisely as:

.. mpg-code:: snippet:m-integer:fig:m:integer:dfa:code:5
   :direct:


A tuple set can also be used as a *negative* tuple set, expressing that the tuples in the table are *not* allowed. For example, the following expresses that three activities do not follow the Swedish drinking protocol:

.. mpg-code:: snippet:m-integer:fig:m:integer:dfa:code:6
   :direct:


Note that ``extensional(home, x, t)`` abbreviates ``extensional(home, x, true, t)``. Extensional constraints using tuple sets also support reification. For example,

.. mpg-code:: snippet:m-integer:fig:m:integer:dfa:code:7
   :direct:


constrains ``b`` to one, if and only if the drinking activities comply with the Swedish drinking protocol.

Tuple sets can also be initialized by specifying their arity and a DFA. Hence, if ``d`` refers to the DFA for the Swedish drinking protocol, the above example can also be written as:

.. mpg-code:: snippet:m-integer:fig:m:integer:dfa:code:8
   :direct:


..

.. mpg-tip:: When to use tuple sets rather than DFAs

   If a DFA is small and the arity is small, then it is typically more efficient to create a tuple set from the DFA and use it instead with an extensional constraint. However, if the arity is large or the DFA encodes many different tuples, it is typically more efficient to use the DFA directly.


The propagators for the ``extensional`` constraint are domain consistent and are based on :cite:`compact-table, negative-compact-table,IngmarSchulte:CP:2018`. (see also GCCat: `in_relation <http://www.emn.fr/z-info/sdemasse/gccat/Cin_relation.html>`__).

For several examples of extensional constraints using tuple sets, see :ref:`chap:c:kakuro`, `Black hole patience <https://www.gecode.dev/doc/6.4.0/reference/black-hole_8cpp.html>`__, and `Kakuro <https://www.gecode.dev/doc/6.4.0/reference/kakuro_8cpp.html>`__.

.. _sec:m:integer:sorted:


.. _modeling:m-integer:sorted-constraints:

Sorted constraints
~~~~~~~~~~~~~~~~~~

.. container:: samepage

   `Sorted constraints <https://www.gecode.dev/doc/6.4.0/reference/group__TaskModelIntSorted.html>`__ relate an integer variable array to an array obtained by sorting the array. For example,

   .. mpg-code:: snippet:m-integer:sec:m:integer:sorted:code:1
      :direct:

constrains ``y`` to be ``x`` (of same size) sorted in increasing order. The more general variant features an additional integer variable array (again, of same size) ``z`` as in

.. mpg-code:: snippet:m-integer:sec:m:integer:sorted:code:2
   :direct:


where ``z`` defines the sorting permutation, that is

.. math::

   \mathtt{x}_i=\mathtt{y}_{\mathtt{z}_i}
   \qquad\mbox{for }0\leq i<|\mathtt x|

The propagator for ``sorted`` is bounds consistent and is based on :cite:`MehlhornThiel:CP:2000` (see also GCCat: `sort <http://www.emn.fr/z-info/sdemasse/gccat/Csort.html>`__, `sort_permutation <http://www.emn.fr/z-info/sdemasse/gccat/Csort_permutation.html>`__).

.. _sec:m:integer:bpp:


.. _modeling:m-integer:bin-packing-constraints:

Bin-packing constraints
~~~~~~~~~~~~~~~~~~~~~~~

`Bin packing constraints <https://www.gecode.dev/doc/6.4.0/reference/group__TaskModelIntBinPacking.html>`__ constrain how items can be packed into bins.

.. _modeling:m-integer:single-dimensional-bin-packing-constraints:

.. rubric:: Single-dimensional bin-packing constraints.

The bin-packing constraint is posted as

.. mpg-code:: snippet:m-integer:sec:m:integer:bpp:code:1
   :direct:


where ``l`` is an array of integer variables (the *load* variables), ``b`` is an array of integer variables (the *bin* variables), and ``s`` is an array of non-negative integers (the item *sizes*).

The load variables ``l`` determine the load :math:`\mathtt{l}_j` of each bin :math:`j` (:math:`0\leq j<|\mathtt{l}|`) and the bin variables ``b`` determine for each item :math:`i` (:math:`0\leq i<|\mathtt{b}|`) into which bin :math:`\mathtt{b}_i` it is packed. The size of an item :math:`i` (:math:`0\leq i<|\mathtt{b}|`) is defined by its item size :math:`\mathtt{s}_i`. Naturally, the number of bin variables and item sizes must coincide (:math:`|\mathtt{b}|=|\mathtt{s}|`).

The bin-packing constraint enforces that all items are packed into bins

.. math::

   \mathtt{b}_i\in\{0,\ldots,|\mathtt{l}|-1\}
   \qquad\mbox{for }0\leq i<|\mathtt{b}|

and that the load of each bin corresponds to the items packed into it

.. math::

   \mathtt{l}_j=\sum_{\{i\in\{0,\ldots,|\mathtt{b}|-1\}\mid\mathtt{b}_j=i\}} \mathtt{s}_i
   \qquad\mbox{for }0\leq j<|\mathtt{l}|

The constraint is implemented by the propagator introduced in :cite:`Shaw:CP:2004` (see also GCCat: `bin_packing <http://www.emn.fr/z-info/sdemasse/gccat/Cbin_packing.html>`__, `bin_packing_capa <http://www.emn.fr/z-info/sdemasse/gccat/Cbin_packing_capa.html>`__). For an example using the bin-packing constraint and CDBF (complete decreasing best fit) :cite:`CDBF` as a specialized branching for bin-packing, see :ref:`chap:c:bpp` and `Bin packing <https://www.gecode.dev/doc/6.4.0/reference/examples_2bin-packing_8cpp.html>`__.

.. _modeling:m-integer:multi-dimensional-bin-packing-constraints:

.. rubric:: Multi-dimensional bin-packing constraints.

The multi-dimensional bin-packing constraint is posted as

.. mpg-code:: snippet:m-integer:sec:m:integer:bpp:code:2
   :direct:


where ``d`` is a positive integer (the *dimension*), ``l`` is an array of integer variables (the *load* variables), ``b`` is an array of integer variables (the *bin* variables), ``s`` is an array of non-negative integers (the item *sizes*), and ``c`` is an array of non-negative integers (the bin *capacities*).

In the following :math:`n` refers to the number of items and :math:`m` refers to the number of bins. The bin variables ``b`` determine for each item :math:`i` (:math:`0\leq i<n`) into which bin :math:`\mathtt{b}_i` it is packed. The load variables ``l`` determine the load :math:`\mathtt{l}_{j\cdot \mathtt{d} + k}` for each bin :math:`j` (:math:`0\leq j<m`) and dimension :math:`k` (:math:`0\leq k<\mathtt{d}`). The size of an item :math:`i` (:math:`0\leq i<n`) in dimension :math:`k` (:math:`0\leq k<\mathtt{d}`) is defined by the item size :math:`\mathtt{s}_{i\cdot\mathtt{d} + k}`. The capacity of all bins :math:`j` (:math:`0\leq j<m)` in dimension :math:`k` (:math:`0\leq k<\mathtt{d}`) is defined by :math:`\mathtt{c}_k`. Naturally, the number of bin variables, load variables, item sizes, and capacities must satisfy that :math:`|\mathtt{b}|=n`, :math:`|\mathtt{l}|=m\cdot\mathtt{d}`, :math:`|\mathtt{s}|=n\cdot\mathtt{d}`, and :math:`|\mathtt{c}|=\mathtt{d}`.

The multi-dimensional bin-packing constraint enforces that all items are packed into bins

.. math::

   \mathtt{b}_i\in\{0,\ldots,m-1\}
   \qquad\mbox{for }0\leq i<n

and that the load of each bin corresponds to the items packed into it for each dimension

.. math::

   \mathtt{l}_{j\cdot \mathtt{d} + k}
   =
   \sum_{\{i\in\{0,\ldots,n-1\}\mid\mathtt{b}_{j\cdot\mathtt{d}+k}=i\}}\mathtt{s}_{i\cdot\mathtt{d}+k}
   \qquad\mbox{for }0\leq j<m, 0\leq k<\mathtt{d}

Furthermore, the load variables must satisfy the capacity constraints

.. math::

   \mathtt{l}_{j\cdot \mathtt{d} + k} \leq \mathtt{c}_k
   \qquad\mbox{for }0\leq j<m, 0\leq k<\mathtt{d}

In addition to posting propagators, the post function

.. mpg-code:: snippet:m-integer:sec:m:integer:bpp:code:3
   :direct:


returns an integer set ``m`` of type `IntSet <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1IntSet.html>`__. The set ``m`` contains a maximal number of conflicting items that must be packed into pairwise distinct bins where the items are chosen to maximize the conflict with other items. This information can be used for symmetry breaking.

.. important::

   Posting the constraint (not propagating it) has exponential complexity in the number of items. This is due to the use of the Bron-Kerbosch algorithm :cite:`BronKerbosch:1973,CazalsKarande:2008` for finding all sets of conflicting items.

The constraint is implemented by the decomposition introduced in :cite:`GualandiLombardi:2013` using a single-dimensional bin-packing constraint for each dimension together with derived constraints capturing capacity conflicts. For an example using the multi-dimensional bin-packing constraint see `Multi-dimensional bin packing <https://www.gecode.dev/doc/6.4.0/reference/multi-bin-packing_8cpp.html>`__.

.. _sec:m:integer:geopacking:


.. _modeling:m-integer:geometrical-packing-constraints:

Geometrical packing constraints
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

`Geometrical packing constraints <https://www.gecode.dev/doc/6.4.0/reference/group__TaskModelIntGeoPacking.html>`__ constrain how rectangles can be packed such that no two rectangles from a collection of rectangles overlap.

If ``x`` and ``y`` are integer variable arrays and ``w`` and ``h`` are integer arrays (where all arrays must be of the same size), then

.. mpg-code:: snippet:m-integer:sec:m:integer:geopacking:code:1
   :direct:


propagates that the rectangles defined by coordinates :math:`\langle \mathtt x_i,\mathtt y_i\rangle`, widths :math:`\mathtt w_i`, and heights :math:`\mathtt h_i` for :math:`0\leq i<|\mathtt x|` do not overlap. That is, the following constraint is enforced (see also :ref:`sec:m:minimodel:bool` for a picture):

.. math::

   \left(\mathtt{x}_i+\mathtt{w}_i\leq \mathtt{x}_j\right) \vee
   \left(\mathtt{x}_j+\mathtt{w}_j\leq \mathtt{x}_i\right) \vee
   \left(\mathtt{y}_i+\mathtt{h}_i\leq \mathtt{y}_j\right) \vee
   \left(\mathtt{y}_j+\mathtt{h}_j\leq \mathtt{y}_i\right)

Note that the width or the height of a rectangle can be zero. In this case, the rectangle does not occupy any space. However no other rectangle is allowed to be placed where the zero-sized rectangle is placed.

Rectangles can also be modeled as optional through a Boolean variable :math:`\mathtt m_i` for each rectangle :math:`i`. If the Boolean variable :math:`\mathtt{m}_i` is ``1`` the rectangle is mandatory and considered by the packing constraint, if it is ``0``, the rectangle is ignored.

.. container:: samepage

   With an array of Boolean variables ``m`` the constraint taking optional rectangles into account is posted by

   .. mpg-code:: snippet:m-integer:sec:m:integer:geopacking:code:2
      :direct:

The arrays defining the dimensions (that is, ``w`` and ``h`` for rectangles) can also be arrays of integer variables, where its values are constrained to be non-negative. In this case, the constraint post functions expects both a start and end coordinate. That is, by posting

.. mpg-code:: snippet:m-integer:sec:m:integer:geopacking:code:3
   :direct:


it is enforced that the rectangles defined by the start coordinate :math:`\langle \mathtt{x0}_i,\mathtt{y0}_i\rangle`, the dimension :math:`\langle \mathtt{w}_i,\mathtt{h}_i\rangle`, and the end coordinate :math:`\langle \mathtt{x1}_i,\mathtt{y1}_i\rangle` do not overlap. The end coordinates are *not* constrained to be the sum of the start coordinates and dimensions. That is, one has to explicitly post the linear constraints such that

.. math::

   \left(\mathtt{x0}_i+\mathtt{w}_i=\mathtt{x1}_i\right)\wedge
   \left(\mathtt{y0}_i+\mathtt{h}_i=\mathtt{y1}_i\right)

The constraints are implemented by a naive propagator (considering pairwise no-overlap between rectangles including constructive disjunction, see also GCCat: `diffn <http://www.emn.fr/z-info/sdemasse/gccat/Cdiffn.html>`__), this will change in the future. For an example using the no-overlap constraint, see `Packing squares into a rectangle <https://www.gecode.dev/doc/6.4.0/reference/perfect-square_8cpp.html>`__.

.. _sec:m:integer:circuit:


.. _modeling:m-integer:circuit-and-hamiltonian-path-constraints:

Circuit and Hamiltonian path constraints
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. _fig:m:integer:circuit:before:

.. _fig:m:integer:circuit:after:

.. figure:: /figures/fig-m-integer-circuit.svg
   :name: fig:m:integer:circuit

   Representing edges and propagating ``circuit``

The ``circuit`` and ``path`` constraints (see `Graph constraints <https://www.gecode.dev/doc/6.4.0/reference/group__TaskModelIntGraph.html>`__) use values of variables in an integer variable array ``x`` as edges: if :math:`j\in\mathtt{x}_i`, the corresponding graph contains the edge :math:`i\to j` for :math:`0\leq i,j<|\mathtt{x}|`. Obviously, the graph has the nodes :math:`0` to :math:`|\mathtt{x}|-1`.

.. _modeling:m-integer:circuit-constraints:

.. rubric:: Circuit constraints.

Assume that ``x`` is an integer variable array (``circuit`` does not support Boolean variables). Then,

.. mpg-code:: snippet:m-integer:fig:m:integer:circuit:code:1
   :direct:


constrains the values of ``x`` such that their corresponding edges form a Hamiltonian circuit (see also GCCat: `circuit <http://www.emn.fr/z-info/sdemasse/gccat/Ccircuit.html>`__). For an example before and after propagation of ``circuit`` see :numref:`fig:m:integer:circuit`. For an example, see :ref:`chap:c:knights` and `n-Knights tour (model using circuit) <https://www.gecode.dev/doc/6.4.0/reference/examples_2knights_8cpp.html>`__.

Common applications of ``circuit`` also require costs for the edges in the graph. Assume that the cost for an edge :math:`i\to j` from node :math:`i` to node :math:`j` is defined by the following matrix:

.. math::

   \begin{array}{|c|rrrr|}
   \hline
   i\to j&\cdot\to 0&\cdot\to 1&\cdot\to 2&\cdot\to 3\\
   \hline
   0\to\cdot & 0 & 3 & 5 & 7\\
   1\to\cdot & 4 & 0 & 9 & 6\\
   2\to\cdot & 2 & 1 & 0 & 5\\
   3\to\cdot & -7 & 8 & -2 & 0\\
   \hline
   \end{array}

.. _fig:m:integer:costcircuit:before:

.. _fig:m:integer:costcircuit:after:

.. figure:: /figures/fig-m-integer-costcircuit.svg
   :name: fig:m:integer:costcircuit

   Representing edges and propagating ``circuit`` with cost

Then, by

.. mpg-code:: snippet:m-integer:fig:m:integer:costcircuit:code:1
   :direct:


the integer variables ``x`` are constrained to the values forming the circuit as above, while the integer variables ``y`` define the cost of the edge for each node (these variables can be omitted), and the integer variable ``z`` defines the total cost of the edges in the circuit. Note that the matrix interface as described in :ref:`sec:m:minimodel:matrix` might come in handy for setting up the cost matrix.

:numref:`fig:m:integer:costcircuit` shows a simple example for propagation ``circuit`` with cost where the cost matrix from above is used. For an example, see `Travelling salesman problem (TSP) <https://www.gecode.dev/doc/6.4.0/reference/tsp_8cpp.html>`__.

.. _modeling:m-integer:hamiltonian-path-constraints:

.. rubric:: Hamiltonian path constraints.

The ``path`` constraint (see `Graph constraints <https://www.gecode.dev/doc/6.4.0/reference/group__TaskModelIntGraph.html>`__) is similar to the ``circuit`` constraint and enforces that nodes in a graph from a Hamiltonian path. Assume that ``x`` is an integer variable array (``path`` does not support Boolean variables) and ``s`` (for start) and ``e`` (for end) are integer variables. Then,

.. mpg-code:: snippet:m-integer:fig:m:integer:costcircuit:code:2
   :direct:


constrains the values of ``x``, ``s``, and ``e`` such that their corresponding edges form a Hamiltonian path that starts at node :math:`\mathtt{x}_{\mathtt{s}}` and ends at node :math:`\mathtt{x}_{\mathtt{e}}` (the value of the variable :math:`\mathtt{x}_{\mathtt{e}}` is always :math:`|\mathtt{x}|`).

As an example, assume that the integer variable array ``x`` has three elements (that is, :math:`|\mathtt{x}|=3`) with values between :math:`0` and :math:`3`. Then all solutions to

.. mpg-code:: snippet:m-integer:fig:m:integer:costcircuit:code:3
   :direct:


are as follows:

.. container:: center

   +-------------------------------------------------------+-------------------+-------------------+
   | ``x``                                                 | ``s``             | ``e``             |
   +=======================================================+===================+===================+
   | :math:`\langle\mathtt 1, \mathtt 2, \mathtt 3\rangle` | :math:`\mathtt 0` | :math:`\mathtt 2` |
   +-------------------------------------------------------+-------------------+-------------------+
   | :math:`\langle\mathtt 1, \mathtt 3, \mathtt 0\rangle` | :math:`\mathtt 2` | :math:`\mathtt 1` |
   +-------------------------------------------------------+-------------------+-------------------+
   | :math:`\langle\mathtt 2, \mathtt 0, \mathtt 3\rangle` | :math:`\mathtt 1` | :math:`\mathtt 2` |
   +-------------------------------------------------------+-------------------+-------------------+
   | :math:`\langle\mathtt 2, \mathtt 3, \mathtt 1\rangle` | :math:`\mathtt 0` | :math:`\mathtt 1` |
   +-------------------------------------------------------+-------------------+-------------------+
   | :math:`\langle\mathtt 3, \mathtt 0, \mathtt 1\rangle` | :math:`\mathtt 2` | :math:`\mathtt 0` |
   +-------------------------------------------------------+-------------------+-------------------+
   | :math:`\langle\mathtt 3, \mathtt 2, \mathtt 0\rangle` | :math:`\mathtt 1` | :math:`\mathtt 0` |
   +-------------------------------------------------------+-------------------+-------------------+

The ``path`` constraint provides, similar to ``circuit``, variants for costs for edges in a Hamiltonian path, see `Graph constraints <https://www.gecode.dev/doc/6.4.0/reference/group__TaskModelIntGraph.html>`__.

.. _sec:m:integer:scheduling:


.. _modeling:m-integer:scheduling-constraints:

Scheduling constraints
~~~~~~~~~~~~~~~~~~~~~~

This section provides an overview of scheduling constraints.

.. _sec:m:integer:unary:


.. _modeling:m-integer:unary-resource-constraints:

Unary resource constraints
^^^^^^^^^^^^^^^^^^^^^^^^^^

A unary resource constraint models that a number of tasks to be executed on a single resource do not overlap, where each task is defined by its start time (an integer variable), its duration (an integer or integer variable), and possibly its end time (if the duration is a variable). Unary resource constraints are also known as disjunctive scheduling constraints.

For example, assume that four tasks with durations ``2``, ``7``, ``4``, and ``11`` are to be executed on the same resource where the start times are specified by an array of integer variables (of course, with four variables). Then, posting

.. mpg-code:: snippet:m-integer:sec:m:integer:unary:code:1
   :direct:


constrains the start times in ``s`` such that the execution of none of the tasks overlaps in time (see `Scheduling constraints <https://www.gecode.dev/doc/6.4.0/reference/group__TaskModelIntScheduling.html>`__) (see also GCCat: `disjunctive <http://www.emn.fr/z-info/sdemasse/gccat/Cdisjunctive.html>`__).

.. mpg-tip:: Tasks with duration zero

   Tasks with duration zero are still useful for modeling: even though they do not take any time to be executed on the resource, they prevent that any other task can run at the same time.


.. _modeling:m-integer:selecting-the-propagation-level-1:

.. rubric:: Selecting the propagation level.

All propagators implementing ``unary`` perform overload-checking. The propagators can be posted offering basic or advanced propagation, where basic propagation only is the default. Basic propagation is selected if the constraint is posted with an additional integer propagation level argument (see :ref:`sec:m:integer:ipl`) as

.. mpg-code:: snippet:m-integer:sec:m:integer:unary:code:2
   :direct:


Basic propagation performs time-tabling, see for example :cite:`CBS`, in addition to overload checking.

Advanced propagation is selected by

.. mpg-code:: snippet:m-integer:sec:m:integer:unary:code:3
   :direct:


and performs overload-checking, detectable precedences, not-first-not-last, and edge-finding, following :cite:`Vilim:2007`.

Basic and advanced propagation can be combined by

.. mpg-code:: snippet:m-integer:sec:m:integer:unary:code:4
   :direct:


which is more convenient than the equivalent

.. mpg-code:: snippet:m-integer:sec:m:integer:unary:code:5
   :direct:


It performs time-tabling in addition to the advanced algorithms.

All algorithms require :math:`O(n \log n)` runtime for :math:`n` tasks, however basic propagation is more efficient than advanced propagation.

.. _modeling:m-integer:optional-tasks:

.. rubric:: Optional tasks.

A common variant for unary resource constraints is where tasks can be optional: each task :math:`t` has a Boolean variable :math:`b` attached to it. If :math:`b=1` then the task is *mandatory* and is scheduled on the resource. If :math:`b=0` then the task is *excluded* and is not scheduled. Otherwise, the task is said to be *optional*. Assume that ``b`` refers to an array of Boolean variables also of size ``4``, then

.. mpg-code:: snippet:m-integer:sec:m:integer:unary:code:6
   :direct:


posts a propagator that constrains the start times ``s`` (of course, only if a task is mandatory) as well the Boolean variables in ``b`` (if a task becomes excluded as otherwise no feasible schedule would exist).

.. _modeling:m-integer:tasks-with-flexible-duration:

.. rubric:: Tasks with flexible duration.

The duration of a task can also be given as an integer variable instead of a constant integer. In this case, we say that the tasks are *flexible*. In addition to the flexible duration, the ``unary`` constraint also requires variables for the end time of each task.

Given variable arrays ``s``, ``d``, and ``e`` for the start times, durations, and end times, a unary resource constraint is posted as

.. mpg-code:: snippet:m-integer:sec:m:integer:unary:code:7
   :direct:


However, the additional constraint for each task :math:`i` that :math:`\texttt{s}[i]+\texttt{d}[i]=\texttt{e}[i]` is not enforced automatically. Therefore, a model typically must contain additional constraints like

.. mpg-code:: snippet:m-integer:sec:m:integer:unary:code:8
   :direct:


The ``unary`` post function also exists in a variant with flexible, optional tasks.

.. _sec:m:integer:cumulatives:


.. _modeling:m-integer:cumulative-scheduling-constraints:

Cumulative scheduling constraints
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Gecode provides two generalizations of the unary resource scheduling constraint. The first one, called ``cumulative``, models a resource where tasks can overlap. The resource has a limited *capacity*, and each task requires a certain *resource usage*. At each point in time, the sum of the resource usages of all tasks running at that point must not exceed the capacity. The second generalization, called ``cumulatives``, deals with several cumulative resources at once.

.. _modeling:m-integer:cumulative-single-resource-constraint:

.. rubric:: Cumulative single-resource constraint.

The single-resource constraint ``cumulative`` has nearly the same interface as ``unary``. The only difference is a parameter ``c`` specifying the resource capacity, and an additional integer array ``u`` for the resource usage of each task. Assuming that ``s`` and ``d`` give the start times and durations as before, the following models a resource where two tasks can overlap, and the first three tasks require one unit of the resource, while the last task requires two:

.. mpg-code:: snippet:m-integer:sec:m:integer:cumulatives:code:1
   :direct:


The capacity can be an integer variable or a nonnegative integer. The resource usage must be strictly positive. As for unary, there exist versions with optional, flexible, and flexible and optional tasks.

The propagators implementing the ``cumulative`` constraint always perform overload checking :cite:`Vilim:CPAIOR:2009`. Basic propagation performs time-tabling, see for example :cite:`CBS`, and can be selected by giving ``IPL_BASIC`` as additional integer propagation level argument. The cost of basic propagation is :math:`O(n\log n)` for :math:`n` tasks. Advanced propagation (selected by ``IPL_ADVANCED``) performs edge-finding :cite:`Vilim:CP:2009` (see also GCCat: `cumulative <http://www.emn.fr/z-info/sdemasse/gccat/Ccumulative.html>`__). The cost of advanced propagation is :math:`O(kn\log n)` for :math:`n` tasks where :math:`k` is the number of different resource usage values. Basic and advanced propagation can be combined as described in :ref:`sec:m:integer:unary`.

.. _modeling:m-integer:cumulative-multi-resource-constraint:

.. rubric:: Cumulative multi-resource constraint.

Given a *set* of resources that have some specified usage limit and a set of tasks that must be placed on these resources according to start-times, durations, resource usage, and resource compatibility, the ``cumulatives`` constraint (see `Scheduling constraints <https://www.gecode.dev/doc/6.4.0/reference/group__TaskModelIntScheduling.html>`__) can be used for the placement of these tasks. The limit for the resources can be either a maximum or a minimum, and the resource usage of a task can be positive, negative, or zero. The limit is only valid over the intervals where there is at least one task assigned on that particular resource.

Consider the following code.

.. mpg-code:: snippet:m-integer:sec:m:integer:cumulatives:code:2
   :direct:


This code posts a constraint over a set of tasks :math:`T`, where each task :math:`T_i` is defined by :math:`\langle \mathtt{resource}_i, \mathtt{start}_i, \mathtt{duration}_i, \mathtt{end}_i, \mathtt{height}_i \rangle`. The ``resource`` component indicates the potential resources that the task can use; ``start``, ``duration``, and ``end`` indicate when the task can occur; and finally the ``height`` component indicates the amount of resource the task uses (or “provides” in the case of a negative value). The resource :math:`R_i` is defined by the limit :math:`\mathtt{limit}_i` and the parameter ``atmost``. The latter is common for all resources, and indicates whether the limits are maximum limits (``atmost`` is true) or minimum limits (``atmost`` is false).

As for flexible tasks in :ref:`sec:m:integer:unary`, the ``cumulatives`` constraint does not enforce that :math:`\mathtt{start}_i+\mathtt{duration}_i=\mathtt{end}_i`. This additional constraint must be posted manually.

The parameters ``start`` and ``end`` are always integer variable arrays; ``resource``, ``duration``, and ``height`` can be either integer variable arrays or integer arrays; and ``limit`` is always an array of integers.

For an example using ``cumulatives`` see `Packing squares into a rectangle <https://www.gecode.dev/doc/6.4.0/reference/perfect-square_8cpp.html>`__, where the ``cumulatives`` constraints is used to model packing a set of squares. For an insightful discussion of how to use ``cumulatives`` for modeling, see :cite:`DBLP:conf/cp/BeldiceanuC02` (the propagator for ``cumulative`` is implemented following this paper, see also GCCat: `cumulatives <http://www.emn.fr/z-info/sdemasse/gccat/Ccumulatives.html>`__).

.. _sec:m:integer:precede:


.. _modeling:m-integer:value-precedence-constraints:

Value precedence constraints
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

`Value precedence constraints over integer variables <https://www.gecode.dev/doc/6.4.0/reference/group__TaskModelIntPrecede.html>`__ enforce that a value precedes another value in an array of integer variables. By

.. mpg-code:: snippet:m-integer:sec:m:integer:precede:code:1
   :direct:


where ``x`` is an array of integer variables and both ``s`` and ``t`` are integers, the following is enforced: if there exists :math:`j` (:math:`0\leq j<|\mathtt{x}|`) such that :math:`\mathtt{x}_j=\mathtt{t}`, then there must exist :math:`i` with :math:`i<j` such that :math:`\mathtt{x}_i=\mathtt{s}`. This is equivalent to:

#. :math:`\mathtt{x}_0 \neq \mathtt t`, and

#. if :math:`\mathtt{x}_j=\mathtt t` then :math:`\bigvee_{i=0}^{j-1} \mathtt{x}_i=\mathtt s` for :math:`1\leq j<|\mathtt x|`.

A generalization is available for precedences between several integer values. By

.. mpg-code:: snippet:m-integer:sec:m:integer:precede:code:2
   :direct:


where ``x`` is an array of integer variables and ``c`` is an array of integers, it is enforced that :math:`\mathtt{c}_i` precedes :math:`\mathtt{c}_{i+1}` in ``x`` for :math:`0\leq i<|\mathtt c|-1`. That is

#. :math:`\mathtt{x}_0 \neq \mathtt{c}_{k+1}` for :math:`0\leq k<|\mathtt{c}|-1`, and

#. if :math:`\mathtt{x}_j=\mathtt{c}_{k+1}` then :math:`\bigvee_{i=0}^{j-1} \mathtt{x}_i=\mathtt{c}_k` for :math:`1\leq j<|\mathtt x|` and :math:`0\leq k<|\mathtt{c}|-1`.

The constraint is implemented by the domain consistent propagator introduced in :cite:`Precede` (see also GCCat: `int_value_precede <http://www.emn.fr/z-info/sdemasse/gccat/Cint_value_precede.html>`__, `int_value_precede_chain <http://www.emn.fr/z-info/sdemasse/gccat/Cint_value_precede_chain.html>`__), the paper also explains how to use the ``precede`` constraint for breaking value symmetries. For an example, see `Schur’s lemma <https://www.gecode.dev/doc/6.4.0/reference/schurs-lemma_8cpp.html>`__.

.. _sec:m:integer:exec:


.. _modeling:m-integer:synchronized-execution:

Synchronized execution
----------------------

Gecode offers support in `Synchronized execution <https://www.gecode.dev/doc/6.4.0/reference/group__TaskModelIntExec.html>`__ for executing a function (any function that is compatible with the type ``std::function``) when integer or Boolean variables become assigned.

.. container:: samepage

   The following code

   .. mpg-code:: snippet:m-integer:sec:m:integer:exec:code:1
      :direct:

   posts a propagator that waits until the integer or Boolean variable ``x`` (or, if ``x`` is an array of variables: all variables in ``x``) is assigned. If ``x`` becomes assigned, the function passed as argument is executed with the current home space passed as argument. The type of the function must be

   .. mpg-code:: snippet:m-integer:sec:m:integer:exec:code:2
      :direct:

..

.. mpg-tip:: Failing a space

   If you want to fail a space ``home`` (for example when executing a continuation function as discussed above), you can do that by


   .. mpg-code:: snippet:m-integer:sec:m:integer:exec:code:3
      :direct:

The following code

.. mpg-code:: snippet:m-integer:sec:m:integer:exec:code:4
   :direct:


creates a propagator that will be run exactly once when the Boolean variable ``x`` becomes assigned. If ``x`` becomes assigned to ``1``, the first function is executed. If ``x`` becomes assigned to ``0``, the second function is executed. Both functions get the current home space of the propagator passed as argument and must be of type

.. mpg-code:: snippet:m-integer:sec:m:integer:exec:code:5
   :direct:


The else-function is optional and can be omitted.

.. [1]
   Actually, if an argument array has few fields it uses some space that is part of the object implementing the array rather than allocating memory from the heap. Hence, small argument arrays reside entirely on the stack.

.. mpg-covered: tip:docs/src/chapters/modeling/m-integer.tex.in:77:unlabeled-tip@docs/src/chapters/modeling/m-integer.tex.in:77
.. mpg-covered: tip:docs/src/chapters/modeling/m-integer.tex.in:500:unlabeled-tip@docs/src/chapters/modeling/m-integer.tex.in:500
.. mpg-covered: tip:docs/src/chapters/modeling/m-integer.tex.in:555:unlabeled-tip@docs/src/chapters/modeling/m-integer.tex.in:555
.. mpg-covered: literal-projection:docs/src/chapters/modeling/m-integer.tex.in:562:dynamic script
.. mpg-covered: literal-projection:docs/src/chapters/modeling/m-integer.tex.in:567:dynamic script:read data
.. mpg-covered: literal-projection:docs/src/chapters/modeling/m-integer.tex.in:570:dynamic script:initialize variable array
.. mpg-covered: tip:docs/src/chapters/modeling/m-integer.tex.in:813:unlabeled-tip@docs/src/chapters/modeling/m-integer.tex.in:813
.. mpg-covered: tip:docs/src/chapters/modeling/m-integer.tex.in:864:unlabeled-tip@docs/src/chapters/modeling/m-integer.tex.in:864
.. mpg-covered: caption:docs/src/chapters/modeling/m-integer.tex.in:974:fig:m:integer:irt
.. mpg-covered: table:docs/src/chapters/modeling/m-integer.tex.in:976:tabular@docs/src/chapters/modeling/m-integer.tex.in:976
.. mpg-covered: caption:docs/src/chapters/modeling/m-integer.tex.in:1098:fig:m:integer:bot
.. mpg-covered: table:docs/src/chapters/modeling/m-integer.tex.in:1100:tabular@docs/src/chapters/modeling/m-integer.tex.in:1100
.. mpg-covered: tip:docs/src/chapters/modeling/m-integer.tex.in:1142:unlabeled-tip@docs/src/chapters/modeling/m-integer.tex.in:1142
.. mpg-covered: caption:docs/src/chapters/modeling/m-integer.tex.in:1215:fig:m:integer:arithmetic
.. mpg-covered: table:docs/src/chapters/modeling/m-integer.tex.in:1217:tabular@docs/src/chapters/modeling/m-integer.tex.in:1217
.. mpg-covered: tip:docs/src/chapters/modeling/m-integer.tex.in:1800:unlabeled-tip@docs/src/chapters/modeling/m-integer.tex.in:1800
.. mpg-covered: caption:docs/src/chapters/modeling/m-integer.tex.in:1825:fig:m:integer:dfa
.. mpg-covered: table:docs/src/chapters/modeling/m-integer.tex.in:1832:tabular@docs/src/chapters/modeling/m-integer.tex.in:1832
.. mpg-covered: tip:docs/src/chapters/modeling/m-integer.tex.in:1951:unlabeled-tip@docs/src/chapters/modeling/m-integer.tex.in:1951
.. mpg-covered: caption:docs/src/chapters/modeling/m-integer.tex.in:2200:fig:m:integer:circuit:before
.. mpg-covered: table:docs/src/chapters/modeling/m-integer.tex.in:2205:tabular@docs/src/chapters/modeling/m-integer.tex.in:2205
.. mpg-covered: table:docs/src/chapters/modeling/m-integer.tex.in:2206:tabular@docs/src/chapters/modeling/m-integer.tex.in:2206
.. mpg-covered: table:docs/src/chapters/modeling/m-integer.tex.in:2236:tabular@docs/src/chapters/modeling/m-integer.tex.in:2236
.. mpg-covered: table:docs/src/chapters/modeling/m-integer.tex.in:2237:tabular@docs/src/chapters/modeling/m-integer.tex.in:2237
.. mpg-covered: caption:docs/src/chapters/modeling/m-integer.tex.in:2308:fig:m:integer:costcircuit:before
.. mpg-covered: table:docs/src/chapters/modeling/m-integer.tex.in:2313:tabular@docs/src/chapters/modeling/m-integer.tex.in:2313
.. mpg-covered: table:docs/src/chapters/modeling/m-integer.tex.in:2314:tabular@docs/src/chapters/modeling/m-integer.tex.in:2314
.. mpg-covered: table:docs/src/chapters/modeling/m-integer.tex.in:2353:tabular@docs/src/chapters/modeling/m-integer.tex.in:2353
.. mpg-covered: table:docs/src/chapters/modeling/m-integer.tex.in:2354:tabular@docs/src/chapters/modeling/m-integer.tex.in:2354
.. mpg-covered: table:docs/src/chapters/modeling/m-integer.tex.in:2444:tabular@docs/src/chapters/modeling/m-integer.tex.in:2444
.. mpg-covered: tip:docs/src/chapters/modeling/m-integer.tex.in:2498:unlabeled-tip@docs/src/chapters/modeling/m-integer.tex.in:2498
.. mpg-covered: tip:docs/src/chapters/modeling/m-integer.tex.in:2748:unlabeled-tip@docs/src/chapters/modeling/m-integer.tex.in:2748
