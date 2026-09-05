.. _chap:b:advanced:

Advanced topics
===============

This chapters presents advanced topics for programming branchers as implementations of branchings.

.. _branchers:advanced:overview:

.. mpg-paragraph:: Overview.

:ref:`sec:b:advanced:assign` presents a specialized brancher for assigning views rather than branching on them. How branchers support no-goods is discussed in :ref:`sec:b:advanced:nogoods`. Variable views for branchers are discussed in :ref:`sec:b:advanced:views`.

.. _sec:b:advanced:assign:

Assignment branchers
--------------------

This section presents an example for a brancher that assigns all of its views rather than branches on its views. The branching

.. mpg-code:: snippet:b-advanced:sec:b:advanced:assign:code:1
   :direct:

assigns all variables in ``x`` to their smallest possible value. That is, ``assignmin`` is equivalent to the predefined branching (see :ref:`sec:m:branch:assign`) used as

.. mpg-code:: snippet:b-advanced:sec:b:advanced:assign:code:2
   :direct:




.. mpg-code:: assign min
   :caption: A brancher for ``assignmin``
   :name: fig:b:advanced:assignmin
   :download:

:numref:`fig:b:advanced:assignmin` shows the relevant parts of the brancher ``AssignMin``. Unsurprisingly, both the ``status()`` and ``choice()`` function are identical to those shown in :numref:`fig:b:started:improved` (and hence are omitted).

The changes concern the created choice of type ``PosVal``: the constructor now initializes a choice with a single alternative only (the second argument to the call of the constructor ``Choice``). The ``commit()`` function is a specialized version of the ``commit()`` function defined in :numref:`fig:b:started:improved`. It only needs to be capable of handling a single alternative. The same holds true for the ``print()`` function.

.. _sec:b:advanced:nogoods:

Supporting no-goods
-------------------

Supporting no-goods by a brancher is straightforward: every brancher has a virtual member function ``ngl()`` (for no-good literal) that takes the same arguments as the ``commit()`` member function: a space, a choice, and the number of the alternative and returns a pointer to a no-good literal of class :api:`NGL`. The ``ngl()`` function is called during no-good generation (see :ref:`sec:m:search:nogoods`) and the returned no-good literal is then used by a no-good propagator that propagates the no-goods (if you are curious, the propagator is implemented by :api:`Search::NoGoodsProp`).




.. mpg-code:: none min with no-good support
   :caption: Branching for ``nonemin`` with no-good support
   :name: fig:b:advanced:nogoods
   :download:

By default, the ``ngl()`` function of a brancher returns ``NULL``, which means that the brancher does not support no-goods. In order to support no-goods, a brancher must redefine the ``ngl()`` function and must define a class (or several classes) for the no-good literals to be returned. The class ``EqNGL`` implementing a no-good literal for equality and the ``ngl()`` function is shown in :numref:`fig:b:advanced:nogoods`. Otherwise, the brancher is the same as the ``nonemin`` brancher shown in :numref:`fig:b:started:improved`.

.. _branchers:advanced:returning-no-good-literals:

Returning no-good literals
~~~~~~~~~~~~~~~~~~~~~~~~~~

The ``ngl()`` function of a brancher has the following options:

- As mentioned above, it can always return ``NULL`` and hence the brancher does not support no-goods.

- It returns for each alternative of a choice a no-good literal. For our ``NoneMin`` brancher this would entail that when ``ngl(home,c,0)`` is called, it returns a no-good literal implementing equality between a view and an integer that corresponds to the first alternative (for a given space ``home`` and a choice ``c``).

  For the second alternative ``ngl(home,c,1)`` a no-good literal implementing disequality should be returned. This would work, but the brancher can do better than that as is explained below.

- When ``ngl(home,c,a)`` is called for an alternative where :math:`\mathtt{a}>0` with a space ``home`` and a choice ``c`` and ``a`` is the last alternative (for ``NoneMin``, :math:`\mathtt{a}=\mathtt{1}`) and the last alternative is the logical negation of all other alternatives, then the ``ngl()`` function can return ``NULL`` as an optimization.

  Assume that the alternatives of a choice are

  .. math:: \mathtt{l}_0\vee\ldots\vee\mathtt{l}_{\mathtt{n}-1}

  where ``n`` is the arity of the choice and it holds that

  .. math::

     (\mathtt{l}_0\vee\ldots\vee\mathtt{l}_{\mathtt{n}-2})
       \Leftrightarrow \neg\mathtt{l}_{\mathtt{n}-1}

  is true, then the ``ngl()`` function can return ``NULL`` for the last alternative (that is, for the alternative :math:`\mathtt{n}-1`).

  Note that this optimization implements the very same idea as discussed at the beginning of :ref:`sec:m:search:nogoods`. Note also that this property is typically only true for branchers with binary choices such as in our example.

.. container:: samepage

   In our example, the second alternative is indeed the negation of the first alternative. Hence the following ``ngl()`` function implements no-good literal creation and only requires a single class ``EqNGL`` for no-good literals implementing equality:


.. mpg-code:: none min with no-good support:no-good literal creation

.. _branchers:advanced:implementing-no-good-literals:

Implementing no-good literals
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

No-good literals implement constraints that correspond to alternatives of choices. But instead of implementing these constraints by a propagator, they have a specialized implementation that is used by a no-good propagator. All concepts needed to implement a no-good literal are concepts that are familiar from implementing a propagator.

A no-good literal inherits from the class :api:`NGL` and must implement the following constructors and functions:

- Unsurprisingly, a no-good literal must implement constructors for creation and cloning and member functions ``copy()`` for copying and ``dispose()`` for disposal. They are straightforward and are shown in :numref:`fig:b:advanced:nogoods`.

- It must implement a ``status()`` function that checks whether the no-good literal is subsumed (the function returns ``NGL::SUBSUMED``), failed (the function returns ``NGL::FAILED``), or neither (the function returns ``NGL::NONE``). The return type is ``NGL::Status`` as defined in the :api:`NGL` class.

  It is important to understand that the no-good propagator using no-good literals can only perform propagation if some of its no-good literals become subsumed. Hence, the test for subsumption used in ``status()`` should try to detect subsumption as early as possible.

  Testing subsumption for our ``EqNGL`` no-good literal is straightforward:


.. mpg-code:: none min with no-good support:status

     :small:

- The ``prune()`` function propagates the negation of the constraint that the no-good literal implements.

  Again, the ``prune()`` function for ``NoneMin`` is straightforward:


.. mpg-code:: none min with no-good support:prune

     :small:

- A no-good literal must implement a ``subscribe()`` and a ``cancel()`` function that subscribe and cancel the no-good propagator to the no-good literal’s views.

  As mentioned above, the earlier the ``status()`` function detects subsumption, the more constraint propagation can be expected from the no-good propagator. Hence, it is important to choose the propagation condition for subscriptions such that whenever there is a modification to the view that could result in subsumption the no-good propagator is executed.

  For the ``EqNGL`` no-good literal, we choose the propagation condition for subscriptions to be ``Int::PC_INT_VAL`` (see :ref:`sec:p:started:propcond` for a discussion of propagation conditions). This choice reflects the fact that subsumption can only be decided after the view ``x`` has been assigned:


.. mpg-code:: none min with no-good support:subscribe and cancel

     :small:

- A no-good literal must also implement a ``reschedule()`` function that re-schedules the no-goods propagator when it is re-enabled. The ``reschedule()`` function is straightforward, following the patterns of the ``subscribe()`` and ``cancel()`` functions:


.. mpg-code:: none min with no-good support:re-scheduling

     :small:

In case a no-good literal uses members that must be deallocated when the home-space is deleted, the no-good literal’s class must redefine the virtual member functions ``notice()`` and ``dispose()``, for example by:

.. mpg-code:: snippet:b-advanced:fig:b:advanced:nogoods:code:1
   :direct:

If ``notice()`` returns ``true``, the no-good propagator ensures that the no-good literal’s ``dispose()`` function is called whenever the propagator’s home-space is deleted.

.. _sec:b:advanced:views:

Using variable views
--------------------

Variable views can also be used for reusing branchers to obtain several branchings, similar to reusing propagators for several constraints, see :ref:`chap:p:views`.

While in principle all different variable views introduced in :ref:`chap:p:views` can be used for branchers, the only meaningful variable view for branchers is the minus integer view (see :ref:`sec:p:views:int:minus`).




.. mpg-code:: none min and none max
   :caption: Branchings for ``nonemin`` and ``nonemax``
   :name: fig:b:advanced:views
   :download:

As an example consider the branchings ``nonemin`` (see :ref:`sec:b:started:nonemin`) and ``nonemax`` where the latter tries to assign the maximal value of a view first. The corresponding program fragment is shown in :numref:`fig:b:advanced:views`. The class ``NoneMin`` is made generic with respect to the type of view it uses. Then, both ``nonemin`` and ``nonemax`` can be obtained by instantiating ``NoneMin`` with integer views or integer minus views.
