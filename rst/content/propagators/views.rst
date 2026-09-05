.. _chap:p:views:

Views
=====

This chapter should come as a welcome diversion from the previous chapters in this part. Instead of introducing more concepts and techniques for programming propagators, it shows how to straightforwardly and efficiently reuse propagators for implementing several different constraints. In a way, the chapter tells you how to cache in on all the effort that goes into developing a propagator.

The idea is to make a propagator generic with respect to the views the propagator computes with. As we are talking C++, generic propagators will be nothing but templates where the template arguments happen to be view types. Then, by instantiating the template propagator, one can obtain implementations for several constraints from a single propagator. More on views (a concept introduced by Gecode) can be found in :cite:p:`SchulteTack:Constraints:2013` and :cite:p:`SchulteTack:Advances:2006`.

As it comes to importance, this chapter should be the second in this part. However, the chapter comes rather late to be able to draw on the example propagators presented in the previous chapters.

.. _propagators:views:overview:

.. mpg-paragraph:: Overview.

Integer variable views are discussed in :ref:`sec:p:views:int` and Boolean variable views are discussed in :ref:`sec:p:views:bool`. How integer propagators can be reused for Boolean views is presented in :ref:`sec:p:views:inttobool`.

.. _sec:p:views:int:

Integer views
-------------

Assume that we need an implementation for the ``min`` constraint. Of course, we could implement a ``Min`` propagator analogous to the ``Max`` propagator from :ref:`sec:p:reified:max`. But let us assume that we need to be lazy in that we do not have the time to implement ``Min`` (after all, there are more interesting constraints out there that we want to implement).

What we could do to implement :math:`\min(\mathtt{x},\mathtt{y})=\mathtt{z}` is to introduce three new variables :math:`\mathtt{x}'`, :math:`\mathtt{y}'`, and :math:`\mathtt{z}'`, post three constraints such that :math:`\mathtt{x}=-\mathtt{x}'`, :math:`\mathtt{y}=-\mathtt{y}'`, and :math:`\mathtt{z}=-\mathtt{z}'`, and finally post a ``max`` constraint instead: :math:`\max(\mathtt{x}',\mathtt{y}')=\mathtt{z}'`. While the strength of propagation is uncompromised, efficiency is poor: three additional variables and three additional propagators are needed.

.. _sec:p:views:int:minus:

Minus views
~~~~~~~~~~~

Minus views can do exactly what we discussed above but without creating additional variables or propagators. Assume that we have an integer view :math:`\mathtt{x}` that serves as an interface to a variable implementation :math:`v`. Then, a *minus integer view* :math:`\mathtt{m}` for :math:`v` is also an interface to :math:`v`, however the interface implements operations such that :math:`\mathtt{m}` is an interface to :math:`-v`.

For example, assume that the domain of :math:`\mathtt{x}` is :math:`\{-1,1,3,4,6\}` (which also means that :math:`v\in\{-1,1,3,4,6\}`). Then, the domain for ``m`` is :math:`\{-6,-4,-3,-1,1\}`. For example, ``m.min()`` returns :math:`-6` (which, of course, is nothing but ``-x.max()``) and the modification operation ``m.gq(home,-3)`` results in domains :math:`\mathtt{m}\in\{-3,-1,1\}` and :math:`\mathtt{x}\in\{-1,1,3\}` (which, of course, is the same as ``x.lq(home,-(-3))`` and hence as ``x.lq(home,3)``).

The very point of this exercise is: a minus view is just a different interface to an *existing* variable implementation and does not require a *new* variable implementation. Moreover, the operations performed by the minus view interface are optimized away at compile time.




.. mpg-code:: min and max
   :caption: Minimum and maximum constraints implemented by a ``Max`` propagator
   :name: fig:p:views:minmax
   :download:

:numref:`fig:p:views:minmax` shows how to obtain both ``min`` and ``max`` constraints from the very same ``Max`` propagator using :api:`Int::IntView` and :api:`Int::MinusView` views. The only change needed compared to the ``Max`` propagator from :ref:`sec:p:reified:max` is that the propagator does not hardwire its view type. Instead, the propagator is generic by being implemented as a template over the view type ``View`` it uses. The constraint post functions then just instantiate the ``Max`` propagator with the appropriate view types.

.. mpg-tip:: Using ``using`` clauses
   :name: tip:p:views:using

   Note the ``using`` clauses in :numref:`fig:p:views:minmax`. They make ``x0``, ``x1``, and ``x2`` visible for the ``Max`` propagator. This is necessary in C++ as ``Max`` inherits from a base class that itself depends on the template argument ``View`` of ``Max``. There are other possibilities to refer to members such as ``x0`` that also work, for example by writing ``this->x0`` instead of just ``x0``. We choose the variant with ``using`` clauses to keep the code of the propagator uncluttered.

.. _sec:p:views:int:offset:

Offset views
~~~~~~~~~~~~




.. mpg-code:: domain equal with and without offset
   :caption: Domain equality with and without offset
   :name: fig:p:views:equal
   :download:

An *offset view* ``o`` with offset ``c`` (an integer value) for a variable implementation :math:`v` provides operations such that ``o`` behaves as :math:`v+\mathtt c`.

:numref:`fig:p:views:equal` shows how a domain equality constraint (see :ref:`sec:p:domain:iter`) and a domain equality constraint with offset (see :ref:`sec:p:domain:iterators`) can be obtained from the same domain equality propagator ``Equal``. ``Equal`` has two template arguments ``View0`` and ``View1`` for its views ``x0`` and ``x1`` respectively. With two view template arguments, the propagator can be instantiated with different view types for ``x0`` and ``x1``. Therefore, the propagator uses :api:`MixBinaryPropagator` as base class as it supports different view types as well.

.. _par:p:views:sameshared:

.. mpg-paragraph:: ``shared`` versus ``==``.

The domain modification operations ``inter_r`` and ``narrow_r`` used in the ``Equal`` propagator from :ref:`sec:p:domain:iter` are used such that the operations perform a more efficient in-place update of the view domain (with an additional Boolean value ``false`` as last and optional argument). This is only legal because the range iterator passed as argument to the modification operations does not depend on the view being modified. The post function of ``Equal`` ensures this by only posting the propagator if the two views ``x0`` and ``x1`` are not referring to the very same variable implementation (that is, ``x0==x1`` is false).

With arbitrary views, the situation becomes a little bit more involved. Assume that ``x0`` is an integer view referring to the variable implementation :math:`v` and that ``x1`` is an offset integer view for the same variable implementation :math:`v` and an integer value :math:`c\neq 0`. In this case, the views ``x0`` and ``x1`` share the same variable implementation :math:`v` but are *not* the same.

The function ``shared()`` tests whether two views share the same variable implementation. Hence, the use of domain modification operations in ``Equal`` have to be modified as follows:


.. mpg-code:: domain equal with and without offset:domain propagation

Now, the more efficient in-place operations are used only if ``x0`` and ``x1`` do not share the same variable implementation.

.. _sec:p:views:int:constantscale:

Constant and scale views
~~~~~~~~~~~~~~~~~~~~~~~~

In addition to minus and offset views, Gecode offers *scale views* and *constant views* for integer variable implementations.

A scale view for a variable implementation :math:`v` with an integer scale factor :math:`a` where :math:`a>0` implements operations for :math:`a\cdot v`. Scale views exist in two variants differing in the precision of multiplication: ``IntScaleView`` performs multiplication over integers, whereas ``LLongScaleView`` performs multiplication over long long integers (see :api:`Integer views <TaskActorIntView>` and :api:`Int::ScaleView`).

An integer constant view :api:`Int::ConstIntView` provides an integer view interface to an integer constant ``c``. With other words, an integer constant view for the integer ``c`` behaves as an integer view assigned to the value ``c``.

.. _sec:p:views:bool:

Boolean views
-------------




.. mpg-code:: or and and from or
   :caption: Disjunction and conjunction from same propagator
   :name: fig:p:views:orand
   :download:

For Boolean views, the view resembling a minus view over integers is a view for negation. For example, with Boolean negation views :api:`Int::NegBoolView` both disjunction and conjunction constraints can be obtained from a propagator for disjunction (see :numref:`fig:p:views:orand`).

.. _sec:p:views:inttobool:

Integer propagators on Boolean views
------------------------------------

As has been discussed in :ref:`sec:p:avoid:ortrue`, Boolean views feature all operations available on integer views (such as ``lq()`` or ``gr()``) in addition to the dedicated Boolean operations (such as ``one()`` or ``zero()``). Due to the availability of integer operations on Boolean views, integer propagators can be used to implement Boolean constraints.




.. mpg-code:: less for integer and Boolean variables
   :caption: Less constraints for both integer and Boolean variables
   :name: fig:p:views:intbool
   :download:

:numref:`fig:p:views:intbool` shows how the propagator ``Less`` can be used to implement the ``less`` constraint for both integer and Boolean variables.


.. mpg-tip:: Boolean variables are not integer variables

   The above example uses a template to obtain an implementation of a constraint on both integer and Boolean variables. This is necessary as Boolean variables are not integer variables (in the sense that ``BoolVar`` is not a subclass of ``IntVar``). The same holds true for their views and variable implementations.

   This is by design: Boolean variables are not integer variables as they have a specially optimized implementation (taking advantage of the limited possible variable domains and that only ``PC_BOOL_VAL`` as propagation condition is needed).
