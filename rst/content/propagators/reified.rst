.. _chap:p:reified:

Reification and rewriting
=========================

This chapter discusses how to implement propagators for reified constraints and how to optimize constraint propagation by propagator rewriting. Gecode does not offer any special support for reification but uses propagator rewriting as a more general technique.

.. _propagators:reified:overview:

.. rubric:: Overview.

Reified constraints and how they can be propagated is reviewed in :ref:`sec:p:reified:overview`. The following section (:ref:`sec:p:reified:leeq`) presents a reified less or equal propagator as an example. How to implement both half and full reification is discussed in the following section. General propagator rewriting during constraint propagation is discussed in :ref:`sec:p:reified:max`, whereas :ref:`sec:p:reified:or` presents how to rewrite propagators during cloning.

.. _sec:p:reified:overview:

Reification
-----------

Before reading this section, please read about reification in :ref:`sec:m:integer:reify` and about half reification in :ref:`sec:m:integer:halfreify`.

A propagator for the reified constraint :math:`\mathtt{b}=\mathtt{1}\Leftrightarrow c` for a Boolean *control variable* :math:`\mathtt{b}` propagates as follows:

#. If ``b`` is ``1``, propagate :math:`c` (reification modes: ``RM_EQV`` :math:`\Leftrightarrow`, ``RM_IMP`` :math:`\Rightarrow`).

#. If ``b`` is ``0``, propagate :math:`\neg c` (reification modes: ``RM_EQV`` :math:`\Leftrightarrow`, ``RM_PMI`` :math:`\Leftarrow`). Not that it is not always easy to propagate the negation of a constraint :math:`c` effectively and efficiently.

#. If :math:`c` is subsumed, propagate that ``b`` is ``1`` (reification modes: ``RM_EQV`` :math:`\Leftrightarrow`, ``RM_PMI`` :math:`\Leftarrow`).

#. If :math:`\neg c` is subsumed, propagate that ``b`` is ``0`` (reification modes: ``RM_EQV`` :math:`\Leftrightarrow`, ``RM_IMP`` :math:`\Rightarrow`).

The idea how to implement reification in Gecode is quite simple: if the first (or second) case is true, the reified propagator implementing the reified constraint rewrites itself into a propagator for :math:`c` (or :math:`\neg c`). The remaining two cases are nothing but testing criteria for subsumption.

The advantage of rewriting a reified propagator for :math:`\mathtt{b}=\mathtt{1}\Leftrightarrow c` into a non-reified propagator for :math:`c` or :math:`\neg c` is that the propagators created by rewriting are typically available anyway, and that after rewriting no more overhead for reification is incurred.

.. _sec:p:reified:leeq:

A fully reified less or equal propagator
----------------------------------------

We will discuss a fully reified less or equal propagator :math:`\mathtt b=\mathtt{1}\Leftrightarrow \mathtt x \leq \mathtt y` for integer variables ``x`` and ``y`` using full reification (that is, reification mode ``RM_EQV`` :math:`\Leftrightarrow`) as an example. Taking the above propagation rules for a reified constraint, we obtain:

#. If ``b`` is ``1``, propagate :math:`\mathtt x \leq \mathtt y`.

#. If ``b`` is ``0``, propagate :math:`\mathtt x > \mathtt y` (actually, we choose to propagate :math:`\mathtt y < \mathtt x` instead).

#. If :math:`\mathtt x \leq \mathtt y` is subsumed, propagate that ``b`` is ``1``.

#. If :math:`\mathtt x > \mathtt y` is subsumed, propagate that ``b`` is ``0``.

#. If none of the above rules apply, the propagator is at fixpoint.

.. mpg-covered: caption:docs/src/chapters/programming/p-reified.tex.in:80:fig:p:reified:leeq

.. mpg-covered: figure:docs/src/chapters/programming/p-reified.tex.in:80:fig:p:reified:leeq

.. mpg-covered: literal-projection:docs/src/chapters/programming/p-reified.tex.in:81:less or equal reified full

.. mpg-code:: less or equal reified full
   :caption: A constraint and propagator for fully reified less or equal
   :name: fig:p:reified:leeq
   :download:

The propagator ``ReLeEq`` for reified less or equal relies on propagators ``Less`` for less and ``LeEq`` for less or equal (the propagators are not shown, see :ref:`sec:p:started:patterns` instead). The ``propagate()`` function as shown in :numref:`fig:p:reified:leeq` follows the propagation rules sketched above.

.. _propagators:reified:propagator-rewriting:

.. rubric:: Propagator rewriting.

The ``GECODE_REWRITE`` macro takes the propagator (here, ``*this``) to be rewritten and an expression that posts the new propagator as arguments. It relies on the fact that the identifier ``home`` refers to the current home space (like the fail macros in :ref:`sec:p:started:better`). The macro expands to something along the following lines:

.. mpg-code:: snippet:p-reified:fig:p:reified:leeq:code:1
   :direct:

That is, the ``ReLeEq`` propagator is disposed, the new ``LeEq`` propagator is posted, and subsumption is reported. The order is essential for performance: by first disposing ``ReLeEq``, the data structures that store the subscriptions for ``x0`` and ``x1`` will have at least one free slot for the subscriptions that are created by posting ``LeEq`` and hence avoid (rather inefficient and memory consuming) resizing. Note that it is important to understand that the old propagator is disposed before the new propagator is posted. In case that some data structures that are deleted during disposal are needed for posting, one either has to make sure that the data structures outlive the call to ``dispose()`` or that one does not use the ``GECODE_REWRITE`` macro but first posts the new propagator and only then reports subsumption.

Another essential part is that after calling ``ES_SUBSUMED()``, a propagator is not allowed to do anything that can schedule propagators (such as performing modification operations or creating subscriptions). That is the reason that first ``dispose()`` is called and later the special variant ``ES_SUBSUMED_DISPOSED()`` is used for actually reporting subsumption. Do not use ``ES_SUBSUMED_DISPOSED()`` unless you really, really have to!

.. _propagators:reified:adding-information-to-home:

.. rubric:: Adding information to ``Home``.

As has been discussed in :numref:`tip:m:started:home` and :ref:`sec:p:started:better`, posting uses a value of class ``Home``\ instead of a reference to a ``Space``. In the expansion of ``GECODE_REWRITE`` as shown above, the call operator ``()`` as in

.. mpg-code:: snippet:p-reified:fig:p:reified:leeq:code:2
   :direct:

returns a new value of type ``Home`` with the additional information added that the propagator to be posted is in fact a rewrite of the propagator ``*this``. This information is important, for example, for inheriting the AFC (accumulated failure count, see :ref:`sec:m:branch:afc`): the newly created propagator will inherit the number of accumulated failures from the propagator being rewritten. There will be other applications of ``Home`` in future versions of Gecode.

.. _propagators:reified:testing-relations-between-views:

.. rubric:: Testing relations between views.

Rather than testing whether :math:`\mathtt{x0}\leq\mathtt{x1}` or :math:`\mathtt{x0}>\mathtt{x1}` hold individually, we use the function ``Int::rtest_lq()`` that tests whether two views are less or equal and returns whether the relation holds (``Int::RT_TRUE``), does not hold (``Int::RT_FALSE``), or might hold or not (``Int::RT_MAYBE``).

Relation tests are available for two views (integer or Boolean) or for a view (again, integer or Boolean) and an integer. Relation tests exist for all inequality relations: ``Int::rtest_le()`` (for :math:`<`), ``Int::rtest_lq()`` (for :math:`\leq`), ``Int::rtest_gr()`` (for :math:`>`), and ``Int::rtest_gq()`` (for :math:`\geq`). For equality, a bounds test (``Int::rtest_eq_bnd()``) as well as a domain test exists (``Int::rtest_eq_dom()``).

While ``Int::rtest_eq_bnd()`` only uses the bounds for testing the relation (with constant time complexity), ``Int::rtest_eq_dom()`` uses the full set of values in the domain of the views to determine the relation (having linear time complexity in the length of the range representation of the views’ domains, see :ref:`sec:p:domain:iter` for more information on range representations of view domains). The same holds true for disequality: ``Int::rtest_nq_bnd()`` performs the bounds-only test, whereas ``Int::rtest_nq_dom()`` performs the full domain test. For example, ``Int::rtest_eq_bnd(x,y)`` for :math:`\mathtt x\in\{0,2\}` and :math:`\mathtt y\in\{1,3\}` returns ``Int::RT_MAYBE``, whereas ``Int::rtest_eq_dom()`` returns ``Int::RT_FALSE``.

.. _propagators:reified:reified-propagator-patterns:

.. rubric:: Reified propagator patterns.

The integer module (as these patterns require Boolean views they are part of the integer module) provides reified propagator patterns for unary propagators (``Int::ReUnaryPropagator``) and binary propagators (``Int::ReBinaryPropagator``\ and ``Int::ReMixBinaryPropagator``). In addition to views ``x0`` (and ``x1`` for the binary variants), they define a Boolean control variable ``b``. Please note that in :numref:`fig:p:reified:leeq` a reified propagator pattern requires an additional template argument for the Boolean control view used (the mystery why this is useful is lifted in :ref:`chap:p:views`).

.. _sec:p:reified:half:

Supporting both full and half reification
-----------------------------------------

There are two different options for implementing all different reification modes: either implement a single propagator that stores its reification mode, or implement three different propagators, one for each reification mode. Due to performance reasons we choose the latter variant here. That is, one needs one propagator for each reification mode: ``RM_EQV`` for equivalence (:math:`\Leftrightarrow`), ``RM_IMP`` for implication (:math:`\Rightarrow`), and ``RM_PMI`` for reverse implication (:math:`\Leftarrow`). Instead of three different implementations it is better to have a single implementation that is parametric with respect to the reification mode.

.. mpg-covered: caption:docs/src/chapters/programming/p-reified.tex.in:209:fig:p:reified:leeq:half

.. mpg-covered: figure:docs/src/chapters/programming/p-reified.tex.in:209:fig:p:reified:leeq:half

.. mpg-covered: literal-projection:docs/src/chapters/programming/p-reified.tex.in:210:less or equal reified half

.. mpg-code:: less or equal reified half
   :caption: A constraint and propagator for full and half reified less or equal
   :name: fig:p:reified:leeq:half
   :download:

:numref:`fig:p:reified:leeq:half` shows the constraint post function ``leeq()`` for the reified less or equal propagator supporting all three reification modes. The class ``ReLeEq`` now is parametric with respect to the reification mode the propagator implements. The constraint post function now posts the propagator that corresponds to the reification mode (available via ``r.mode()``) passed as argument ``r`` of type ``Reify``. The Boolean control variable can be returned by ``r.var()``.

.. mpg-covered: caption:docs/src/chapters/programming/p-reified.tex.in:225:fig:p:reified:leeq:half:propagate

.. mpg-covered: figure:docs/src/chapters/programming/p-reified.tex.in:225:fig:p:reified:leeq:half:propagate

.. mpg-covered: literal-projection:docs/src/chapters/programming/p-reified.tex.in:226:less or equal reified half:propagate function

.. mpg-code:: less or equal reified half:propagate function
   :caption: Propagate function for full and half reified less or equal
   :name: fig:p:reified:leeq:half:propagate

The idea for the reified propagator is straightforward, its ``propagate()`` function is shown in :numref:`fig:p:reified:leeq:half:propagate`: the four different parts of the propagator are employed depending on the reification mode ``rm``. Note that this is entirely schematic and any reified propagator can be programmed supporting all reification modes in that way.

.. _sec:p:reified:max:

Rewriting during propagation
----------------------------

Rewriting during propagation is a useful technique that is not limited to implementing reification. We consider a ``Max`` propagator that propagates :math:`\max(\mathtt{x}_0,\mathtt{x}_1)=\mathtt{x}_2`. The propagation rules (we are giving bounds propagation rules that achieve () consistency, see :cite:p:`bounds-consistency`) for ``Max`` are easy to understand when looking at an equivalent formulation of :math:`\max` :cite:p:`SchulteStuckey:TOPLAS:2005`:

.. math::

   \begin{aligned}
   \max(\mathtt{x}_0,\mathtt{x}_1)=\mathtt{x}_2
   &\iff&
   (\mathtt{x}_0\leq\mathtt{x}_2)\wedge
   (\mathtt{x}_1\leq\mathtt{x}_2)\wedge
   \left( (\mathtt{x}_0=\mathtt{x}_2)\vee(\mathtt{x}_1=\mathtt{x}_2)\right)\\
   &\iff&
   (\mathtt{x}_0\leq\mathtt{x}_2)\wedge
   (\mathtt{x}_1\leq\mathtt{x}_2)\wedge
   \left( (\mathtt{x}_0\geq\mathtt{x}_2)\vee(\mathtt{x}_1\geq\mathtt{x}_2)\right)\\
   \end{aligned}

Then, the propagation rules can be turned into the following C++-code to be executed by the ``propagate()`` member function of ``Max``:

.. mpg-code:: snippet:p-reified:sec:p:reified:max:code:1
   :direct:

.. mpg-covered: caption:docs/src/chapters/programming/p-reified.tex.in:279:fig:p:reified:max

.. mpg-covered: figure:docs/src/chapters/programming/p-reified.tex.in:279:fig:p:reified:max

.. mpg-covered: literal-projection:docs/src/chapters/programming/p-reified.tex.in:280:max using rewriting

.. mpg-code:: max using rewriting
   :caption: A maximum propagator using rewriting
   :name: fig:p:reified:max
   :download:

Please take a second look: the condition of the first ``if``-statement tests whether :math:`\mathtt{x}_1` is less or equal than :math:`\mathtt{x}_0`, or whether :math:`\mathtt{x}_1` is less than :math:`\mathtt{x}_2`. In both cases, :math:`\max(\mathtt{x}_0,\mathtt{x}_1)=\mathtt{x}_2` simplifies to :math:`\mathtt{x}_0=\mathtt{x}_2`. Exactly this simplification can be implemented by propagator rewriting, please check :numref:`fig:p:reified:max`. Note that the propagator is naive in that it does not implement the propagator to be idempotent (however, this can be done exactly as demonstrated in :ref:`sec:p:avoid:eqbnd`).

Another idea would be to perform rewriting during cloning: the ``copy()`` function could return an ``Equal`` propagator rather than a ``Max`` propagator in the cases where rewriting is possible. However, this is illegal: it would create a propagator with only two views, hence one view would not be updated even though there is a subscription for it (violating obligation “update complete” from :ref:`sec:p:started:obligations`). Also, canceling a subscription is illegal during cloning (violating obligation “cloning conservative” from :ref:`sec:p:started:obligations`). The next section shows an example with opposite properties: rewriting during propagation makes no sense (even though it would be legal) whereas rewriting during cloning is legal and useful.

.. _sec:p:reified:or:

Rewriting during cloning
------------------------

In :ref:`sec:p:avoid:dynamic`, the propagator ``OrTrue`` is simplified during copying by eliminating assigned views. Here we show that the propagator created as a copy during cloning can be optimized further by rewriting it during copying.

.. container:: samepage

   .. rubric:: Copying.
      :name: copying.

   The modified ``copy()`` function is as follows:

.. mpg-covered: literal-projection:docs/src/chapters/programming/p-reified.tex.in:323:or true using rewriting:copy

.. mpg-code:: or true using rewriting:copy

.. mpg-covered: caption:docs/src/chapters/programming/p-reified.tex.in:326:fig:p:reified:or

.. mpg-covered: figure:docs/src/chapters/programming/p-reified.tex.in:326:fig:p:reified:or

.. mpg-covered: literal-projection:docs/src/chapters/programming/p-reified.tex.in:327:or true using rewriting

.. mpg-code:: or true using rewriting
   :caption: A Boolean disjunction propagator using rewriting
   :name: fig:p:reified:or
   :download:

The ``copy()`` function takes advantage of two cases:

#. If there is a view that is assigned to ``1``, the propagator is subsumed. However, during cloning a propagator cannot be deleted by subsumption. Reporting subsumption is only possible during propagation. The ``copy()`` function does the next best thing: it creates a propagator ``SubsumedOrTrue`` that next time it is executed will in fact report subsumption.

   Note that in this situation rewriting during cloning is preferable to rewriting during propagation. An important aspect of the ``OrTrue`` propagator is that it does not inspect all of its views during finding a view for resubscribing (as implemented by the ``resubscribe()`` member function). Instead, inspection stops as soon as the first unassigned view is found. That entails that a view that is assigned to ``1`` might be missed during propagation. In other words, rewriting during cloning also optimizes subsumption detection.

#. If all views in the view array ``x`` are assigned to ``0``, the view array is actually not longer needed (it has no elements). In this case, the ``copy()`` function creates a propagator ``BinaryOrTrue`` that is a special variant of ``OrTrue`` limited to just two views. Note that the two views ``x0`` and ``x1`` are known to be not yet assigned: otherwise, the propagator would not be at fixpoint. This is impossible as only spaces that are at fixpoint (and hence all of its propagators must be at fixpoint) can be cloned (this invariant is discussed in :ref:`sec:s:started:space`).

   Rewriting during propagation would be entirely pointless in this situation: the propagator (be it ``OrTrue`` or ``BinaryOrTrue``) will be executed at most one more time and will become subsumed then (or, due to failure, it is not executed at all). As rewriting incurs the cost of creating and disposing propagators and subscriptions, rewriting in this case would actually slow down execution.

.. _propagators:reified:constructors-for-copying:

.. rubric:: Constructors for copying.

The relevant parts of the two special propagators for rewriting ``SubsumedOrTrue`` and ``BinaryOrTrue`` are shown in :numref:`fig:p:reified:or`. Their ``propagate()`` functions are exactly as sketched above. The only other non-obvious aspect are the constructors used for copying during cloning: they are now called for a propagator of class ``OrTrue``. In this example, it is sufficient to have a single constructor for copying as all the propagators ``OrTrue``, ``SubsumedOrTrue``, and ``BinaryOrTrue`` inherit from ``BinaryPropagator``. In other cases, it might be necessary to have more than a single constructor for copying defined by a propagator class ``C``: one for copying a propagator of class ``C`` and one for creating propagators as rewrites of other propagators.
