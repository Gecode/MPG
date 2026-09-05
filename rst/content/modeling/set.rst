.. _chap:m:set:


.. _modeling:m-set:set-variables-and-constraints:

Set variables and constraints
=============================

This chapter gives an overview over set variables and set constraints in Gecode and serves as a starting point for using set variables. For the reference documentation, see :api:`Using integer set variables and constraints <TaskModelSet>`.

.. _modeling:m-set:overview:

.. mpg-paragraph:: Overview.

:ref:`sec:m:set:var` details how set variables can be used for modeling. The sections :ref:`sec:m:set:post` and :ref:`sec:m:set:exec` provide an overview of the constraints that are available for set variables in Gecode.

.. important::

   Do not forget to add

   .. mpg-code:: snippet:m-set:chap:m:set:code:1
      :direct:

   to your program when you want to use set variables. Note that the same conventions hold as in :ref:`chap:m:int`.

.. _sec:m:set:var:


.. _modeling:m-set:set-variables:

Set variables
-------------

Set variables in Gecode model sets of integers and are instances of the class :api:`SetVar`.

.. mpg-tip:: Still do not use views for modeling

   Just as for integer variables, you should not feel tempted to use views of set variables (such as ``SetView``) for modeling. Views can only be used for implementing propagators and branchers, see :ref:`part:p` and :ref:`part:b`.


.. _modeling:m-set:representing-set-domains-as-intervals:

.. mpg-paragraph:: Representing set domains as intervals.

The domain of a set variable is a set of sets of integers (in contrast to a simple set of integers for an integer variable). For example, assume that the domain of the set variable :math:`x` is the set of subsets of :math:`\{1,2,3\}`:

.. math:: \big\{\;\{\},\{1\},\{2\},\{3\},\{1,2\},\{1,3\},\{2,3\},\{1,2,3\}\;\big\}

Set variable domains can become very large – the set of subsets of :math:`\{1,\dots,n\}` has :math:`2^n` elements. Gecode (like most constraint solvers) therefore approximates set variable domains by a set interval :math:`\left[l..u\right]` of a lower bound :math:`l` and an upper bound :math:`u`. The interval :math:`\left[l..u\right]` denotes the set of sets :math:`\{s\mid l\subseteq s\subseteq u\}`. The lower bound :math:`l` (commonly referred to as greatest lower bound or *glb*) contains all elements that are *known* to be included in the set, whereas the upper bound :math:`u` (commonly referred to as least upper bound or *lub*) contains the elements that *may be* included in the set. As only the two interval bounds are stored, this representation is space-efficient. The domain of :math:`x` from the above example can be represented as :math:`\left[\{\}..\{1,2,3\}\right]`.

Set intervals can only approximate set variable domains. For example, the domain

.. math:: \big\{\;\{1\},\{2\},\{3\},\{1,2\},\{1,3\},\{2,3\}\;\big\}

cannot be captured exactly by an interval. The closest interval would be :math:`\left[\{\}..\{1,2,3\}\right]`. In order to get a closer approximation of set variable domains, Gecode additionally stores cardinality bounds. We write :math:`\#\left[i..j\right]` to express that the cardinality is at least :math:`i` and at most :math:`j`. The set interval bounds :math:`\left[\{\}..\{1,2,3\}\right]` together with cardinality bounds :math:`\#\left[1..2\right]` represent the above example domain exactly.

.. _modeling:m-set:creating-a-set-variable:

.. mpg-paragraph:: Creating a set variable.

New set variables are created using a constructor. A new set variable ``x`` is created by

.. mpg-code:: snippet:m-set:sec:m:set:var:code:1
   :direct:


This declares a variable ``x`` of type ``SetVar`` in the space ``home``, creates a new set variable implementation with domain :math:`\left[\{\}..\{1,2,3\}\right],\#\left[1..2\right]`, and makes ``x`` refer to the newly created set variable implementation.

There are several overloaded versions of the constructor, you can for example omit the cardinality bounds if you do not want to restrict the cardinality. You find the full interface in the reference documentation of the class :api:`SetVar`. An attempt to create a set variable with an empty domain throws an exception of type :api:`Set::VariableEmptyDomain`.

As for integer and Boolean variables, the default and copy constructors do not create new variable implementations. Instead, the variable does not refer to any variable implementation (default constructor) or to the same variable implementation (copy constructor). For example in

.. mpg-code:: snippet:m-set:sec:m:set:var:code:2
   :direct:


the variables ``x``, ``y``, and ``z`` all refer to the same set variable implementation.

.. _modeling:m-set:limits-for-set-elements:

.. mpg-paragraph:: Limits for set elements.

All set variable bounds are subsets of the *universe*, defined as

.. math:: \left[\mathtt{Set::Limits::min}..\mathtt{Set::Limits::max}\right]

The universe is symmetric: :math:`-\mbox{\texttt{Set::Limits::min}}=\mbox{\texttt{Set::Limits::max}}`. Furthermore, the cardinality of a set is limited to the unsigned integer interval

.. math:: \#\left[0..\mathtt{Set::Limits::card}\right]

The limits have been chosen such that an integer variable can hold the cardinality. This means that the maximal element of a set variable is :math:`\mathtt{Int::Limits::max} / 2 - 1`. The limits are defined in the namespace :api:`Set::Limits`.

Any attempt to create a set variable with values outside the defined limits throws an exception of type :api:`Set::OutOfLimits`.

.. mpg-tip:: Small variable domains are still beautiful

   Just like integer variables (see :ref:`tip:m:integer:beautifuldomains`), set variables do not have a constructor that creates a variable with the largest possible domain. And again, one has to worry and the omission is deliberate to make you worry. So think about the initial domains carefully when modeling.


.. _modeling:m-set:variable-access-functions:

.. mpg-paragraph:: Variable access functions.

You can access the current domain of a set variable ``x`` using member functions such as ``x.cardMax()``, returning the upper bound of the cardinality, or ``x.glbMin()``, returning the smallest element of the lower bound. Furthermore, you can print a set variable’s domain using the standard output operator ``<<``.

.. _modeling:m-set:iterating-variable-domain-interval-bounds:

.. mpg-paragraph:: Iterating variable domain interval bounds.

For access to the interval bounds of a set variable, Gecode provides three value iterators and corresponding range iterators. For example, the following loop

.. mpg-code:: snippet:m-set:sec:m:set:var:code:3
   :direct:


uses the value iterator ``i`` to print all values of the greatest lower bound of the domain of ``x`` in increasing order. If ``x`` is assigned, this of course corresponds to the value of ``x``. Similarly, the following loop

.. mpg-code:: snippet:m-set:sec:m:set:var:code:4
   :direct:


uses the range iterator ``i`` to print all ranges of the least upper bound of the domain of ``x``. The third kind of iterator, :api:`SetVarUnknownValues` or :api:`SetVarUnknownRanges`, iterate the values resp. ranges that are still unknown to be part or not part of the set, that is :math:`u\setminus l` for the domain :math:`\left[l..u\right]`.

.. _modeling:m-set:when-to-inspect-a-variable:

.. mpg-paragraph:: When to inspect a variable.

The same restrictions hold as for integer variables (see :ref:`sec:m:integer:inspect`). The important restriction is that one must not change the domain of a variable (for example, by posting a constraint on that variable) while an iterator for that variable is being used.

.. _modeling:m-set:updating-variables:

.. mpg-paragraph:: Updating variables.

Set variables behave exactly like integer variables during cloning of a space. A set variable is updated by

.. mpg-code:: snippet:m-set:sec:m:set:var:code:5
   :direct:


where ``y`` is the variable from which ``x`` is to be updated. While ``home`` is the space ``x`` belongs to, ``y`` belongs to the space which is being cloned.

.. _modeling:m-set:variable-and-argument-arrays:

.. mpg-paragraph:: Variable and argument arrays.

Set variable arrays can be allocated using the class :api:`SetVarArray`. The constructors of this class take the same arguments as the set variable constructors, preceded by the size of the array. For example,

.. mpg-code:: snippet:m-set:sec:m:set:var:code:6
   :direct:


creates an array of four set variables, each with domain :math:`\left[\{\}..\{1,2,3\}\right]`.

To pass temporary data structures as arguments, you can use the ``SetVarArgs`` class (see :api:`Argument arrays <TaskModelSetArgs>`). Some set constraints are defined in terms of arrays of sets of integers. These can be passed using ``IntSetArgs`` (see :api:`Argument arrays <TaskModelSetArgs>`). Set variable argument arrays support the same operations introduced in :ref:`sec:m:integer:args`.

.. _sec:m:set:post:


.. _modeling:m-set:constraint-overview:

Constraint overview
-------------------

This section introduces the different groups of constraints over set variables available in Gecode. The section serves only as an overview. For the details and the full list of available post functions, the section refers to the relevant reference documentation.

.. _modeling:m-set:reified-constraints:

.. mpg-paragraph:: Reified constraints.

Several set constraints also exist as a reified variant. Whether a reified version exists for a given constraint can be found in the reference documentation. If a reified version does exist, the reification information combining the Boolean control variable and an optional reification mode is passed as the last non-optional argument, see :ref:`sec:m:integer:halfreify`.

.. _tip:m:set:rbd:

.. mpg-tip:: Reification by decomposition

   If your model requires reification of a constraint for which no reified version exists in the library, you can often *decompose* the reification. For example, to reify the constraint :math:`\mbox{\texttt{x}}\cup\mbox{\texttt{y}}=\mbox{\texttt{z}}` to a control variable ``b``, you can introduce an auxiliary variable :math:`\mbox{\texttt{z0}}` and post the two constraints


   .. mpg-code:: snippet:m-set:tip:m:set:rbd:code:1
      :direct:

.. _modeling:m-set:domain-constraints:

Domain constraints
~~~~~~~~~~~~~~~~~~

.. mpg-figure:: Set relation types
   :name: fig:m:set:srt

   .. container:: center

      +--------------+----------------------------------+--------------+-------------------------------------------+
      | ``SRT_EQ``   | equality (:math:`=`)             | ``SRT_NQ``   | disequality (:math:`\neq`)                |
      +--------------+----------------------------------+--------------+-------------------------------------------+
      | ``SRT_LQ``   | lex. less than or equal          | ``SRT_LE``   | lex. less than                            |
      +--------------+----------------------------------+--------------+-------------------------------------------+
      | ``SRT_GQ``   | lex. greater than or equal       | ``SRT_GR``   | lex. greater than                         |
      +--------------+----------------------------------+--------------+-------------------------------------------+
      | ``SRT_SUB``  | subset (:math:`\subseteq`)       | ``SRT_SUP``  | superset (:math:`\supseteq`)              |
      +--------------+----------------------------------+--------------+-------------------------------------------+
      | ``SRT_DISJ`` | disjointness (:math:`\parallel`) | ``SRT_CMPL`` | complement (:math:`\;\overline{\cdot}\;`) |
      +--------------+----------------------------------+--------------+-------------------------------------------+

:api:`Domain constraints <TaskModelSetDom>` restrict the domain of a set variable using a set constant (given as a single integer, an interval of two integers or an ``IntSet``), depending on set relation types of type ``SetRelType`` (see :api:`Using integer set variables and constraints <TaskModelSet>`). :numref:`fig:m:set:srt` lists the available set relation types and their meaning. The relations ``SRT_LQ``, ``SRT_LE``, ``SRT_GQ``, and ``SRT_GR`` establish a total order based on the lexicographic order of the characteristic functions of the two sets.

.. container:: samepage

   For example, the constraints

   .. mpg-code:: snippet:m-set:fig:m:set:srt:code:1
      :direct:

   result in the set variable ``x`` being a subset of :math:`\{1,\dots,10\}` and a superset of :math:`\{1,2,3\}`, while :math:`4`, :math:`5`, and :math:`6` are not elements of the set :math:`\mathtt{y}`. The domain constraints for set variables support reification. Both ``x`` and ``y`` can also be arrays of set variables where each array element is constrained accordingly (but no reification is supported).

In addition to the above constraints,

.. mpg-code:: snippet:m-set:fig:m:set:srt:code:2
   :direct:


restricts the cardinality of the set variable ``x`` to be between :math:`3` and :math:`5`. ``x`` can also be an array of set variables.

The domain of a set variable ``x`` can be constrained according to the domain of another variable set ``d`` by

.. mpg-code:: snippet:m-set:fig:m:set:srt:code:3
   :direct:


Here, ``x`` and ``d`` can also be arrays of set variables.

For examples using domain constraints, see :api:`Airline crew allocation <crew.cpp>`, as well as the redundant constraints in :api:`Golf tournament <golf.cpp>`.

.. _modeling:m-set:relation-constraints:

Relation constraints
~~~~~~~~~~~~~~~~~~~~

:api:`Relation constraints <TaskModelSetRel>` enforce relations between set variables and between set and integer variables, depending on the set relation types introduced above.

For set variables ``x`` and ``y``, the following constrains ``x`` to be a subset of ``y``:

.. mpg-code:: snippet:m-set:fig:m:set:srt:code:4
   :direct:


If ``x`` is a set variable and ``y`` is an integer variable, then

.. mpg-code:: snippet:m-set:fig:m:set:srt:code:5
   :direct:


constrains ``x`` to be a superset of the singleton set :math:`\{\mathtt{y}\}`, which means that ``y`` must be an element of ``x``.

.. container:: samepage

   The last form of set relation constraint uses an integer relation type (see :numref:`fig:m:integer:irt`) instead of a set relation type. This constraint restricts *all* elements of a set variable to be in the given relation to the value of an integer variable. For example,

   .. mpg-code:: snippet:m-set:fig:m:set:srt:code:6
      :direct:

constrains all elements of the set variable ``x`` to be strictly greater than the value of the integer variable ``y`` (see also GCCat: `eq_set <http://www.emn.fr/z-info/sdemasse/gccat/Ceq_set.html>`__, `in <http://www.emn.fr/z-info/sdemasse/gccat/Cin.html>`__, `in_set <http://www.emn.fr/z-info/sdemasse/gccat/Cin_set.html>`__, `not_in <http://www.emn.fr/z-info/sdemasse/gccat/Cnot_in.html>`__).

Gecode provides reified versions of all set relation constraints. For an example, see :api:`Golf tournament <golf.cpp>` and :ref:`chap:c:golf`.

.. _modeling:m-set:if-then-else-constraint:

.. mpg-paragraph:: If-then-else constraint.

An if-then-else constraint can be posted by

.. mpg-code:: snippet:m-set:fig:m:set:srt:code:7
   :direct:


where ``b`` is a Boolean variable and ``x``, ``y``, and ``z`` are set variables. In case ``b`` is one, then :math:`\mathtt{x}=\mathtt{z}` must hold, otherwise :math:`\mathtt{y}=\mathtt{z}` must hold.

.. _m:set:set_operations:


.. _modeling:m-set:set-operations:

Set operations
~~~~~~~~~~~~~~

.. mpg-figure:: Set operation types
   :name: fig:m:set:sot

   .. container:: center

      +----------------+---------------------------------+---------------+-------------------------------+
      | ``SOT_UNION``  | union (:math:`\cup`)            | ``SOT_INTER`` | intersection (:math:`\cap`)   |
      +----------------+---------------------------------+---------------+-------------------------------+
      | ``SOT_DUNION`` | disjoint union (:math:`\uplus`) | ``SOT_MINUS`` | set minus (:math:`\setminus`) |
      +----------------+---------------------------------+---------------+-------------------------------+

:api:`Set operation/relation constraints <TaskModelSetRelOp>` perform set operations according to the type shown in :numref:`fig:m:set:sot` and relate the result to a set variable. For example,

.. mpg-code:: snippet:m-set:fig:m:set:sot:code:1
   :direct:


enforces the relation :math:`\mathtt{x}\cup \mathtt{y}=\mathtt{z}` for set variables ``x``, ``y``, and ``z``. For an array of set variables ``x``,

.. mpg-code:: snippet:m-set:fig:m:set:sot:code:2
   :direct:


enforces the relation

.. math:: \bigcup_{i=0}^{|\mathtt{x}|-1}\mathtt{x}_i=\mathtt{y}

Instead of set variables, the relation constraints also accept ``IntSet`` arguments as set constants. There are no reified versions of the set operation constraints (you can decompose using reified relation constraints on the result, see :ref:`tip:m:set:rbd`).

Set operation constraints are used in most examples that contain set variables, such as :api:`Airline crew allocation <crew.cpp>` or :api:`Generating Hamming codes <hamming.cpp>`.

.. _m:set:element:


.. _modeling:m-set:element-constraints:

Element constraints
~~~~~~~~~~~~~~~~~~~

:reference:`Element constraints (element()) <namespaceGecode.html#a844feb95b37b987163a550d214d976d7>` generalize array access to set variables. The simplest version of ``element`` for set variables is stated as

.. mpg-code:: snippet:m-set:m:set:element:code:1
   :direct:


for an array of set variables or constants ``x``, an integer variable ``y``, and a set variable ``z``. It constrains ``z`` to be the element of array ``x`` at index ``y`` (where the index starts at ``0``).

A further generalization uses a *set variable* as the index, thus selecting several sets at once. The result variable is constrained to be the union, disjoint union, or intersection of the selected set variables, depending on the set operation type argument. For example,

.. mpg-code:: snippet:m-set:m:set:element:code:2
   :direct:


for set variables ``y`` and ``z`` and an array of set variables ``x`` enforces the following relation:

.. math:: \mathtt{z}=\bigcup_{i\in\mathtt{y}}\mathtt{x}_i

Note that generalized element constraints follow the usual semantics of set operations if the index variable is the empty set: an empty union is the empty set, whereas an empty intersection is the full universe. Because of this semantics, the ``element`` constraint has an optional set constant argument so that you can specify the universe (i.e., usually the full set of elements your problem deals with) explicitly. For an example of a set element constraint, see :api:`Golf tournament <golf.cpp>` and :ref:`chap:c:golf`.

.. _m:set:set_int:


.. _modeling:m-set:constraints-connecting-set-and-integer-variables:

Constraints connecting set and integer variables
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Most models that involve set variables also involve integer variables. In addition to the set relation constraints that accept integer variables (interpreting them as singleton sets), :reference:`Cardinality constraints (cardinality()) <group__TaskModelSetConnect.html#ga2275ba756168623853b2682347e36cc2>` and the operations below provide the necessary interface for models that use both set variables and integer or Boolean variables.

The most obvious constraint connecting integer and set variables is the cardinality constraint:

.. mpg-code:: snippet:m-set:m:set:set_int:code:1
   :direct:


It states that the integer variable ``y`` is equal to the cardinality of the set variable ``x``.

Gecode provides constraints for the minimal and maximal elements of a set. The following code

.. mpg-code:: snippet:m-set:m:set:set_int:code:2
   :direct:


constrains the integer variable ``y`` to be the minimum of the set ``x``.

For an example of constraints connecting integer and set variables, see :api:`Steiner triples <steiner.cpp>`.

.. _modeling:m-set:weighted-sets:

.. mpg-paragraph:: Weighted sets.

The ``weights`` constraint assigns a weight to each possible element of a set variable ``x``, and then constrains an integer variable ``y`` to be the sum of the weights of the elements of ``x``. The mapping is given using two integer arrays, ``e`` and ``w``. For example,

.. mpg-code:: snippet:m-set:m:set:set_int:code:3
   :direct:


enforces that ``x`` is a subset of :math:`\{1,3,4,5,7,9\}` (the set of elements), and that ``y`` is the sum of the weights of the elements in ``x``, where the weight of the element ``1`` would be ``-1``, the weight of ``3`` would be ``4`` and so on. Assigning ``x`` to the set :math:`\{3,7,9\}` would therefore result in ``y`` being assigned to :math:`4+3+3=10` (see also GCCat: `sum_set <http://www.emn.fr/z-info/sdemasse/gccat/Csum_set.html>`__).

.. _m:set:set_channel:


.. _modeling:m-set:set-channeling-constraints:

Set channeling constraints
~~~~~~~~~~~~~~~~~~~~~~~~~~

:reference:`Channel constraints (channel()) <namespaceGecode.html#a9a722c5a14e6503556315d4257061c1a>` link arrays of set variables, as well as set variables with integer and Boolean variables.

For an two arrays of set variables ``x`` and ``y``,

.. mpg-code:: snippet:m-set:m:set:set_channel:code:1
   :direct:


posts the constraint

.. math::

   j\in\mathtt{x}_i \Leftrightarrow i\in \mathtt{y}_j
   \qquad\mbox{for }0\leq i<|\mathtt{x}|
   \qquad\mbox{and }0\leq j<|\mathtt{y}|

For an array of integer variables ``x`` and an array of set variables ``y``,

.. mpg-code:: snippet:m-set:m:set:set_channel:code:2
   :direct:


posts the constraint

.. math::

   \mathtt{x}_i=j \Leftrightarrow i\in \mathtt{y}_j
   \qquad\mbox{for }0\leq i,j<|\mathtt{x}|

The channel between a set variable ``y`` and an array of Boolean variables ``x``,

.. mpg-code:: snippet:m-set:m:set:set_channel:code:3
   :direct:


enforces the constraint

.. math::

   \mathtt{x}_i=1 \Leftrightarrow i\in \mathtt{y}
   \qquad\mbox{for }0\leq i<|\mathtt{x}|

An array of integer variables ``x`` can be channeled to a set variable ``y`` using

.. mpg-code:: snippet:m-set:m:set:set_channel:code:4
   :direct:


which constrains ``y`` to be the set :math:`\{\mathtt{x}_0,\dots,\mathtt{x}_{|\mathtt{x}|-1}\}`. An alias for this constraint is defined in the modeling convenience library, see :ref:`sec:m:minimodel:channel` and :ref:`sec:m:minimodel:setalias`.

A specialized version of the previous constraint is

.. mpg-code:: snippet:m-set:m:set:set_channel:code:5
   :direct:


which constrains ``y`` to be the set :math:`\{\mathtt{x}_0,\dots,\mathtt{x}_{|\mathtt{x}|-1}\}`, and the integer variables in ``x`` are sorted in increasing order (:math:`\mathtt{x}_i<\mathtt{x}_{i+1}` for :math:`0\leq i<|\mathtt{x}|`) (see also GCCat: `link_set_to_booleans <http://www.emn.fr/z-info/sdemasse/gccat/Clink_set_to_booleans.html>`__).

.. _modeling:m-set:convexity-constraints:

Convexity constraints
~~~~~~~~~~~~~~~~~~~~~

:api:`Convexity constraints <TaskModelSetConvex>` enforce that set variables are convex, which means that the elements form an integer interval. For example, the set :math:`\{1,2,3,4,5\}` is convex, while :math:`\{1,3,4,5\}` is not, as it contains a hole. The *convex hull* of a set :math:`s` is the smallest convex set containing :math:`s` (:math:`\{1,2,3,4,5\}` is the convex hull of :math:`\{1,3,4,5\}`).

The constraint

.. mpg-code:: snippet:m-set:m:set:set_channel:code:6
   :direct:


states that the set variable ``x`` must be convex, and

.. mpg-code:: snippet:m-set:m:set:set_channel:code:7
   :direct:


enforces that the set variable ``y`` is the convex hull of the set variable ``x``.

.. _modeling:m-set:sequence-constraints:

Sequence constraints
~~~~~~~~~~~~~~~~~~~~

:api:`Sequence constraints <TaskModelSetSequence>` enforce an order among an array of set variables ``x``. Posting the constraint

.. mpg-code:: snippet:m-set:m:set:set_channel:code:8
   :direct:


results in the sets ``x`` being pairwise disjoint, and furthermore :math:`\max(\mathtt{x}_i)<\min(\mathtt{x}_{i+1})` for all :math:`0\leq i<|\mathtt{x}|-1`. Posting

.. mpg-code:: snippet:m-set:m:set:set_channel:code:9
   :direct:


additionally constrains the set variable ``y`` to be the union of the ``x``.

For an example of sequence constraints, see :api:`Steiner triples <steiner.cpp>`.

.. _sec:m:set:precede:


.. _modeling:m-set:value-precedence-constraints:

Value precedence constraints
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:reference:`Value precedence constraints (precede()) <group__TaskModelSetPrecede.html#gacbffe24f32e7e393f27c3da7df0f5f3f>` enforce that a value precedes another value in an array of set variables. By

.. mpg-code:: snippet:m-set:sec:m:set:precede:code:1
   :direct:


where ``x`` is an array of set variables and both ``s`` and ``t`` are integers, the following is enforced: if there exists :math:`j` (:math:`0\leq j<|\mathtt{x}|`) such that :math:`s\notin\mathtt{x}_j` and :math:`t\in\mathtt{x}_j`, then there must exist :math:`i` with :math:`i<j` such that :math:`s\in\mathtt{x}_i` and :math:`t\notin\mathtt{x}_i`.

A generalization is available for precedences between several integer values. By

.. mpg-code:: snippet:m-set:sec:m:set:precede:code:2
   :direct:


where ``x`` is an array of set variables and ``c`` is an array of integers, it is enforced that :math:`\mathtt{c}_k` precedes :math:`\mathtt{c}_{k+1}` in ``x`` for :math:`0\leq k<|\mathtt c|-1`.

The constraint is implemented by the propagator introduced in :cite:`Precede` (see also GCCat: `set_value_precede <http://www.emn.fr/z-info/sdemasse/gccat/Cset_value_precede.html>`__), the paper also explains how to use the ``precede`` constraint for breaking value symmetries. For an example, see :api:`Golf tournament <golf.cpp>` and :ref:`chap:c:golf`.

.. _sec:m:set:exec:


.. _modeling:m-set:synchronized-execution:

Synchronized execution
----------------------

Gecode offers support in :reference:`Synchronized execution (wait()) <namespaceGecode.html#ad614b55b27244916514b394a3478273a>` for executing a function when set variables become assigned.

The code

.. mpg-code:: snippet:m-set:sec:m:set:exec:code:1
   :direct:


posts a propagator that waits until the set variable ``x`` (or, if ``x`` is an array of set variables: all variables in ``x``) is assigned. If ``x`` becomes assigned, the function passed as argument is executed with the current home space passed as argument. The type of the function must be

.. mpg-code:: snippet:m-set:sec:m:set:exec:code:2
   :direct:
