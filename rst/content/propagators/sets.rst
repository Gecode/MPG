.. _chap:p:sets:

Propagators for set constraints
===============================

This chapter shows how to implement propagators for constraints over set variables. We assume that you have worked through the chapters on implementing integer propagators, as most of the techniques readily carry over and are not explained again here.

We also assume a basic knowledge of propagation for set constraints. To read more about this topic, please refer to :cite:p:`Gervet:1995:0:Finite,Tack:PhD:2009`.

.. _propagators:sets:overview:

.. mpg-paragraph:: Overview.

:ref:`sec:p:sets:simple_example` demonstrates a propagator that implements set interesection. Set views and their related concepts are summarized in :ref:`sec:p:sets:propagation_conditions_etc`.

.. _sec:p:sets:simple_example:

A simple example
----------------

.. mpg-covered: caption:docs/src/chapters/programming/p-sets.tex.in:26:fig:p:sets:intersection

.. mpg-covered: figure:docs/src/chapters/programming/p-sets.tex.in:26:fig:p:sets:intersection

.. mpg-covered: literal-projection:docs/src/chapters/programming/p-sets.tex.in:27:intersection

.. mpg-code:: intersection
   :caption: A constraint and propagator for set intersection
   :name: fig:p:sets:intersection
   :download:

:numref:`fig:p:sets:intersection` shows a propagator for the ternary intersection constraint :math:`\mathtt{x}_0\cap\mathtt{x}_1=\mathtt{x}_2` for three set variables :math:`\mathtt{x}_0`, :math:`\mathtt{x}_1`, and :math:`\mathtt{x}_2`.

As you can see, propagators for set constraints follow exactly the same structure as propagators for integer or Boolean constraints. The same propagator patterns can be used (see :ref:`sec:p:started:patterns`). The appropriate views and propagation conditions are defined in the namespace ``Gecode::Set``.

In order to understand the ``propagate()`` function, we have to look at how set variable domains are represented.

.. _propagators:sets:the-set-bounds-approximation:

.. mpg-paragraph:: The set bounds approximation.

We already saw in :ref:`chap:m:set` that set variable domains are represented as intervals in order to avoid an exponential representation. For example, recall that

.. math:: \big\{\;\{1\},\{2\},\{3\},\{1,2\},\{1,3\},\{2,3\}\;\big\}

\ cannot be captured exactly by an interval, but is instead approximated by the smallest enclosing interval :math:`\left[\{\}\;..\;\{1,2,3\}\right]`.

Set propagators therefore access and modify the interval bounds. Naturally, set-valued domain operations similar to the ones for integer variables (see :ref:`chap:p:domain`) play an important role for set propagators.

For each set view, ``Set::GlbRanges``\ provides a range iterator for its lower bound, and ``Set::LubRanges``\ iterates the upper bound. The main iterator-based modification operations on set views are ``includeI`` (adding a set to the lower bound), ``excludeI`` (removing a set from the upper bound), and ``intersectI`` (intersecting the upper bound with a set).

.. _propagators:sets:filtering-rules:

.. mpg-paragraph:: Filtering rules.

Coming back to the example propagator for ternary intersection, we have to devise filtering rules that express the constraint in terms of the interval bounds. In the following, we write :math:`\underline{x}` and :math:`\overline{x}` for the lower bound resp. upper bound of a view :math:`x`. Then, ternary intersection can be propagated with the following rules and implemented with set domain operations:

#. :math:`\underline{\mathtt{x}_0}\cap\underline{\mathtt{x}_1}\subseteq\mathtt{x}_2`

.. mpg-covered: literal-projection:docs/src/chapters/programming/p-sets.tex.in:81:intersection:rule 1

.. mpg-code:: intersection:rule 1
      :small:

#. :math:`\overline{\mathtt{x}_0}\cap\overline{\mathtt{x}_1}\supseteq\mathtt{x}_2`

.. mpg-covered: literal-projection:docs/src/chapters/programming/p-sets.tex.in:83:intersection:rule 2

.. mpg-code:: intersection:rule 2
      :small:

#. :math:`\underline{\mathtt{x}_2}\subseteq\mathtt{x}_0`

.. mpg-covered: literal-projection:docs/src/chapters/programming/p-sets.tex.in:85:intersection:rule 3

.. mpg-code:: intersection:rule 3
      :small:

#. :math:`\underline{\mathtt{x}_2}\subseteq\mathtt{x}_1`

.. mpg-covered: literal-projection:docs/src/chapters/programming/p-sets.tex.in:87:intersection:rule 4

.. mpg-code:: intersection:rule 4
      :small:

#. :math:`\underline{\mathtt{x}_0}\setminus\overline{\mathtt{x}_2}\not\subseteq\mathtt{x}_1`

.. mpg-covered: literal-projection:docs/src/chapters/programming/p-sets.tex.in:89:intersection:rule 5

.. mpg-code:: intersection:rule 5
      :small:

#. :math:`\underline{\mathtt{x}_1}\setminus\overline{\mathtt{x}_2}\not\subseteq\mathtt{x}_0`

.. mpg-covered: literal-projection:docs/src/chapters/programming/p-sets.tex.in:91:intersection:rule 6

.. mpg-code:: intersection:rule 6
      :small:

.. mpg-covered: caption:docs/src/chapters/programming/p-sets.tex.in:94:fig:p:sets:view_operations

.. mpg-covered: figure:docs/src/chapters/programming/p-sets.tex.in:94:fig:p:sets:view_operations

.. mpg-covered: table:docs/src/chapters/programming/p-sets.tex.in:96:tabular@docs/src/chapters/programming/p-sets.tex.in:96

.. mpg-figure:: Set view operations
   :name: fig:p:sets:view_operations

   .. container:: center

      +--------------------------------------+-----------------------------------------------------------+
      | **integer-valued bounds operations** |                                                           |
      +--------------------------------------+-----------------------------------------------------------+
      | ``glbMin()`` / ``glbMax()``          | return minimum/maximum of lower bound                     |
      +--------------------------------------+-----------------------------------------------------------+
      | ``lubMin()`` / ``lubMax()``          | return minimum/maximum of upper bound                     |
      +--------------------------------------+-----------------------------------------------------------+
      | ``glbSize()`` / ``lubSize()``        | return size of lower/upper bound                          |
      +--------------------------------------+-----------------------------------------------------------+
      | ``unknownSize()``                    | return number of elements in upper but not in lower bound |
      +--------------------------------------+-----------------------------------------------------------+
      | ``contains()``                       | test whether lower bound contains element                 |
      +--------------------------------------+-----------------------------------------------------------+
      | ``notContains()``                    | test whether upper bound does not contain element         |
      +--------------------------------------+-----------------------------------------------------------+
      | ``include()``                        | add element (or range) to lower bound                     |
      +--------------------------------------+-----------------------------------------------------------+
      | ``exclude()``                        | remove element (or range) from upper bound                |
      +--------------------------------------+-----------------------------------------------------------+
      | ``intersect()``                      | intersect upper bound with element or range               |
      +--------------------------------------+-----------------------------------------------------------+
      |                                      |                                                           |
      +--------------------------------------+-----------------------------------------------------------+
      | **set-valued bounds modifications**  |                                                           |
      +--------------------------------------+-----------------------------------------------------------+
      | ``includeI()``                       | add elements to lower bound                               |
      +--------------------------------------+-----------------------------------------------------------+
      | ``excludeI()``                       | remove elements from upper bound                          |
      +--------------------------------------+-----------------------------------------------------------+
      | ``intersectI()``                     | intersect upper bound with given set                      |
      +--------------------------------------+-----------------------------------------------------------+
      |                                      |                                                           |
      +--------------------------------------+-----------------------------------------------------------+
      | **cardinality operations**           |                                                           |
      +--------------------------------------+-----------------------------------------------------------+
      | ``cardMin()``                        | return/modify minimum cardinality                         |
      +--------------------------------------+-----------------------------------------------------------+
      | ``cardMax()``                        | return/modify maximum cardinality                         |
      +--------------------------------------+-----------------------------------------------------------+

The first four rules should be self-explanatory. The last two rules state that anything that is in :math:`\mathtt{x}_0` but not in :math:`\mathtt{x}_2` cannot be in :math:`\mathtt{x}_1` (and the same for :math:`\mathtt{x}_0` and :math:`\mathtt{x}_1` swapped). The full list of operations on set views appears in :numref:`fig:p:sets:view_operations`.

.. _propagators:sets:fixpoint:

.. mpg-paragraph:: Fixpoint.

Note how the propagator determines which execution status to return. Before applying any of the filtering rules, it checks whether all of the variables are already assigned. If they are, then propagation will compute a fixpoint and the propagator can return that it is subsumed after applying the filtering rules. Otherwise, it has not necessarily computed a fixpoint (e.g. rule 6 may modify the upper bound of :math:`\mathtt{x}_0`, making it necessary to apply rule 2 again).

.. _propagators:sets:cardinality:

.. mpg-paragraph:: Cardinality.

In addition to the interval bounds, set variables store *cardinality bounds*, that is, the minimum and maximum cardinality of the set variable. These bounds are stored and modified independently of the interval bounds, but of course modifications to these different bounds affect each other.

For example, consider a set variable with a domain represented by the interval :math:`\left[\{\}\;..\;\{1,2\}\right]` and the cardinality :math:`\#\left[1\;..\;2\right]`. Adding :math:`1` to the lower bound would result in the cardinality lower bound being increased to :math:`1`. Removing :math:`1` from the upper bound would result in :math:`2` being added to the lower bound to satisfy the minimum cardinality of :math:`1`.

Using cardinality information, propagation for some set constraints can be strengthened. For the ternary intersection example, we can for instance add the following filtering rules:

.. mpg-covered: literal-projection:docs/src/chapters/programming/p-sets.tex.in:159:intersection:cardinality

.. mpg-code:: intersection:cardinality

When dealing with cardinality, it is important to handle overflow or signedness issues. In the above example, we have to check whether ``x0.cardMin()+x1.cardMin()>s``, because otherwise the expression ``x0.cardMin()+x1.cardMin()-s`` may underflow (as we are dealing with unsigned integers here). This is not the case for the second cardinality rule. Here, we can be sure that the size of the union of the lower bounds is always greater than the sum of the maximum cardinalities.

.. _sec:p:sets:propagation_conditions_etc:

Modification events, propagation conditions, views, and advisors
----------------------------------------------------------------

This section summarizes how these concepts are specialized for set variables and propagators.

.. _propagators:sets:modification-events-and-propagation-conditions:

.. mpg-paragraph:: Modification events and propagation conditions.

.. mpg-covered: caption:docs/src/chapters/programming/p-sets.tex.in:180:fig:p:sets:propagation_conditions

.. mpg-covered: figure:docs/src/chapters/programming/p-sets.tex.in:180:fig:p:sets:propagation_conditions

.. mpg-covered: table:docs/src/chapters/programming/p-sets.tex.in:182:tabular@docs/src/chapters/programming/p-sets.tex.in:182

.. mpg-figure:: Set modification events and propagation conditions
   :name: fig:p:sets:propagation_conditions

   [p]

   .. container:: center

      +--------------------------------+----------------------------------------------------------+
      | **set modification events**    |                                                          |
      +--------------------------------+----------------------------------------------------------+
      | ``Set::ME_SET_NONE``           | the view has not been changed                            |
      +--------------------------------+----------------------------------------------------------+
      | ``Set::ME_SET_FAILED``         | the domain has become empty                              |
      +--------------------------------+----------------------------------------------------------+
      | ``Set::ME_SET_VAL``            | the view has been assigned to a single set               |
      +--------------------------------+----------------------------------------------------------+
      | ``Set::ME_SET_CARD``           | the view has been assigned to a single set               |
      +--------------------------------+----------------------------------------------------------+
      | ``Set::ME_SET_LUB``            | the upper bound has been changed                         |
      +--------------------------------+----------------------------------------------------------+
      | ``Set::ME_SET_GLB``            | the lower bound has been changed                         |
      +--------------------------------+----------------------------------------------------------+
      | ``Set::ME_SET_BB``             | both bounds have been changed                            |
      +--------------------------------+----------------------------------------------------------+
      | ``Set::ME_SET_CLUB``           | cardinality and upper bound have changed                 |
      +--------------------------------+----------------------------------------------------------+
      | ``Set::ME_SET_CGLB``           | cardinality and lower bound have changed                 |
      +--------------------------------+----------------------------------------------------------+
      | ``Set::ME_SET_CBB``            | cardinality and both bounds have changed                 |
      +--------------------------------+----------------------------------------------------------+
      |                                |                                                          |
      +--------------------------------+----------------------------------------------------------+
      | **set propagation conditions** |                                                          |
      +--------------------------------+----------------------------------------------------------+
      | ``Set::PC_SET_VAL``            | schedule when the view is assigned                       |
      +--------------------------------+----------------------------------------------------------+
      | ``Set::PC_SET_CARD``           | schedule when the cardinality changes                    |
      +--------------------------------+----------------------------------------------------------+
      | ``Set::PC_SET_CLUB``           | schedule when the cardinality or the upper bound changes |
      +--------------------------------+----------------------------------------------------------+
      | ``Set::PC_SET_CGLB``           | schedule when the cardinality or the lower bound changes |
      +--------------------------------+----------------------------------------------------------+
      | ``Set::PC_SET_ANY``            | schedule at any change                                   |
      +--------------------------------+----------------------------------------------------------+
      | ``Set::PC_SET_NONE``           | do not schedule                                          |
      +--------------------------------+----------------------------------------------------------+

The modification events and propagation conditions for set propagators (see :numref:`fig:p:sets:propagation_conditions`) capture the parts of a set variable domain that can change.

One could imagine a richer set, for example distinguishing between lower and upper bound changes of the cardinality, or separating the cardinality changes from the interval bound changes. However, the number of propagation conditions has a direct influence on the size of a variable, see :ref:`par:v:varimp:design:cost`. Just like for integer views, this set of modification events and propagation conditions has been chosen as a compromise between expressiveness on the one hand, and keeping the set small on the other.

.. _propagators:sets:set-variable-views:

.. mpg-paragraph:: Set variable views.

In addition to the basic ``Set::SetView``\ class, there are five other set views: ``Set::ConstSetView``, ``Set::EmptyView``, ``Set::UniverseView``, ``Set::SingletonView``, and ``Set::ComplementView``.

The first three are constant views. A ``SingletonView`` wraps an integer view :math:`x` in the interface of a set view, so that it acts like the singleton set :math:`\{x\}`. A ``ComplementView`` is like Boolean negation, it provides the set complement with respect to the global Gecode universe for set variables (defined as :math:`\left[\mathtt{Set::Limits::min}\;..\;\mathtt{Set::Limits::max}\right]`, see ``Set::Limits``).

.. _propagators:sets:advisors-for-set-propagators:

.. mpg-paragraph:: Advisors for set propagators.

Advisors for set constraints get informed about the domain modifications using a ``Set::SetDelta``. The set delta provides only information about the minimum and maximum values that were added to the lower bound and/or removed from the upper bound.
