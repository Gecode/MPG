.. _chap:p:floats:

Propagators for float constraints
=================================

This chapter shows how to implement propagators for constraints over float variables. We assume that you have worked through the chapters on implementing integer propagators, as most of the techniques readily carry over and are not explained again here.

.. _propagators:floats:overview:

.. mpg-paragraph:: Overview.

:ref:`sec:p:floats:example` demonstrates a propagator that implements a ternary linear constraint. Float views and their related concepts are summarized in :ref:`sec:p:floats:propagation`.

.. _sec:p:floats:example:

A simple example
----------------

.. mpg-covered: caption:docs/src/chapters/programming/p-floats.tex.in:22:fig:p:floats:linear

.. mpg-covered: figure:docs/src/chapters/programming/p-floats.tex.in:22:fig:p:floats:linear

.. mpg-covered: literal-projection:docs/src/chapters/programming/p-floats.tex.in:23:linear

.. mpg-code:: linear
   :caption: A constraint and propagator for ternary linear
   :name: fig:p:floats:linear
   :download:

:numref:`fig:p:floats:linear` shows a propagator for the ternary linear constraint :math:`\mathtt{x}_0+\mathtt{x}_1+\mathtt{x}_2=0` for three float variables :math:`\mathtt{x}_0`, :math:`\mathtt{x}_1`, and :math:`\mathtt{x}_2`.

As you can see, propagators for float constraints follow exactly the same structure as propagators for integer or Boolean constraints. The same propagator patterns can be used (see :ref:`sec:p:started:patterns`). The appropriate views and propagation conditions are defined in the namespace ``Gecode::Float``.

.. _propagators:floats:operations-on-float-views:

.. mpg-paragraph:: Operations on float views.

.. mpg-covered: caption:docs/src/chapters/programming/p-floats.tex.in:42:fig:p:float:view

.. mpg-covered: figure:docs/src/chapters/programming/p-floats.tex.in:42:fig:p:float:view

.. mpg-covered: table:docs/src/chapters/programming/p-floats.tex.in:44:tabular@docs/src/chapters/programming/p-floats.tex.in:44

.. mpg-figure:: Most important float view operations
   :name: fig:p:float:view

   .. container:: center

      +-----------------------------+---------------------------------------------------+
      | **access operations**       |                                                   |
      +-----------------------------+---------------------------------------------------+
      | ``min()``                   | return lower bound (a float number)               |
      +-----------------------------+---------------------------------------------------+
      | ``max()``                   | return upper bound (a float number)               |
      +-----------------------------+---------------------------------------------------+
      | ``size()``                  | return width of domain (a float number)           |
      +-----------------------------+---------------------------------------------------+
      | ``assigned()``              | whether view is assigned                          |
      +-----------------------------+---------------------------------------------------+
      | ``in(n)``                   | whether float number ``n`` is contained in domain |
      +-----------------------------+---------------------------------------------------+
      | ``in(n)``                   | whether float value ``n`` is contained in domain  |
      +-----------------------------+---------------------------------------------------+
      |                             |                                                   |
      +-----------------------------+---------------------------------------------------+
      | **modification operations** |                                                   |
      +-----------------------------+---------------------------------------------------+
      | ``eq(home,n)``              | restrict values to be equal to ``n``              |
      +-----------------------------+---------------------------------------------------+
      | ``lq(home,n)``              | restrict values to be less or equal than ``n``    |
      +-----------------------------+---------------------------------------------------+
      | ``gq(home,n)``              | restrict values to be greater or equal than ``n`` |
      +-----------------------------+---------------------------------------------------+

The most important operations on float views for programming propagators are summarized in :numref:`fig:p:float:view`, the full information can be found in ``Float::FloatView``. The lack of operations such as ``gr()`` (for greater), ``le()`` (for less), and ``nq()`` (for disequality) is due to the fact that domains are closed intervals, see :ref:`sec:m:float:val` and :numref:`tip:m:float:weak`.

.. _propagators:floats:creating-a-rounding-object:

.. mpg-paragraph:: Creating a rounding object.

.. mpg-covered: caption:docs/src/chapters/programming/p-floats.tex.in:74:fig:p:floats:rounding

.. mpg-covered: figure:docs/src/chapters/programming/p-floats.tex.in:74:fig:p:floats:rounding

.. mpg-covered: table:docs/src/chapters/programming/p-floats.tex.in:76:tabular@docs/src/chapters/programming/p-floats.tex.in:76

.. mpg-figure:: Rounding operations on float numbers (``x`` and ``y`` are float numbers)
   :name: fig:p:floats:rounding
   :short-caption: Rounding operations on float numbers

   .. container:: center

      +------------------------------------+---------------------------------------------------------+---------+
      | function                           | meaning                                                 | default |
      +====================================+=========================================================+=========+
      | ``add_down(x,y)``, ``add_up(x,y)`` | l/u bound of :math:`\mathtt{x}+\mathtt{y}`              | yes     |
      +------------------------------------+---------------------------------------------------------+---------+
      | ``sub_down(x,y)``, ``sub_up(x,y)`` | l/u bound of :math:`\mathtt{x} - \mathtt{y}`            | yes     |
      +------------------------------------+---------------------------------------------------------+---------+
      | ``mul_down(x,y)``, ``mul_up(x,y)`` | l/u bound of :math:`\mathtt{x} \times \mathtt{y}`       | yes     |
      +------------------------------------+---------------------------------------------------------+---------+
      | ``div_down(x,y)``, ``div_up(x,y)`` | l/u bound of :math:`\mathtt{x} / \mathtt{y}`            | yes     |
      +------------------------------------+---------------------------------------------------------+---------+
      | ``sqrt_down(x)``, ``sqrt_up(x)``   | l/u bound of :math:`\sqrt{\mathtt{x}}`                  | yes     |
      +------------------------------------+---------------------------------------------------------+---------+
      | ``int``\ ``_down(x)``              | next downward-rounded integer of :math:`\mathtt{x}`     | yes     |
      +------------------------------------+---------------------------------------------------------+---------+
      | ``int``\ ``_up(x)``                | next upward-rounded integer of :math:`\mathtt{x}`       | yes     |
      +------------------------------------+---------------------------------------------------------+---------+
      | ``exp_down(x)``, ``exp_up(x)``     | l/u bound of :math:`\exp(\mathtt{x})`                   |         |
      +------------------------------------+---------------------------------------------------------+---------+
      | ``log_down(x)``, ``log_up(x)``     | l/u bound of :math:`\log(\mathtt{x})`                   |         |
      +------------------------------------+---------------------------------------------------------+---------+
      | ``sin_down(x)``, ``sin_up(x)``     | l/u bound of :math:`\sin(\mathtt{x})`                   |         |
      +------------------------------------+---------------------------------------------------------+---------+
      | ``cos_down(x)``, ``cos_up(x)``     | l/u bound of :math:`\cos(\mathtt{x})`                   |         |
      +------------------------------------+---------------------------------------------------------+---------+
      | ``tan_down(x)``, ``tan_up(x)``     | l/u bound of :math:`\tan(\mathtt{x})`                   |         |
      +------------------------------------+---------------------------------------------------------+---------+
      | ``asin_down(x)``, ``asin_up(x)``   | l/u bound of :math:`\arcsin(\mathtt{x})`                |         |
      +------------------------------------+---------------------------------------------------------+---------+
      | ``acos_down(x)``, ``acos_up(x)``   | l/u bound of :math:`\arccos(\mathtt{x})`                |         |
      +------------------------------------+---------------------------------------------------------+---------+
      | ``atan_down(x)``, ``atan_up(x)``   | l/u bound of :math:`\arctan(\mathtt{x})`                |         |
      +------------------------------------+---------------------------------------------------------+---------+
      | ``sinh_down(x)``, ``sinh_up(x)``   | l/u bound of :math:`\sinh(\mathtt{x})`                  |         |
      +------------------------------------+---------------------------------------------------------+---------+
      | ``cosh_down(x)``, ``cosh_up(x)``   | l/u bound of :math:`\cosh(\mathtt{x})`                  |         |
      +------------------------------------+---------------------------------------------------------+---------+
      | ``tanh_down(x)``, ``tanh_up(x)``   | l/u bound of :math:`\tanh(\mathtt{x})`                  |         |
      +------------------------------------+---------------------------------------------------------+---------+
      | ``asinh_down(x)``, ``asinh_up(x)`` | l/u bound of :math:`\operatorname{arcsinh}(\mathtt{x})` |         |
      +------------------------------------+---------------------------------------------------------+---------+
      | ``acosh_down(x)``, ``acosh_up(x)`` | l/u bound of :math:`\operatorname{arccosh}(\mathtt{x})` |         |
      +------------------------------------+---------------------------------------------------------+---------+
      | ``atanh_down(x)``, ``atanh_up(x)`` | l/u bound of :math:`\operatorname{arctanh}(\mathtt{x})` |         |
      +------------------------------------+---------------------------------------------------------+---------+

The propagation rules of the ``Linear`` propagator will require that it can be controlled whether to round downwards or upwards in a floating point operation on a float number. Access to operations with explicit rounding control is provided by an object of class ``Float::Rounding``. The creation of an object of this class initializes the underlying floating point unit such that it performs exact rounding in the required direction. Note, that explicit rounding is only required if rounding provided by operations on float values is not sufficient.

:numref:`fig:p:floats:rounding` lists the supported operations with explicit rounding, where the ``_down()`` variants round downwards and the ``_up()`` variants round upwards. The functions marked as default are always supported, the others are only supported if Gecode has been built accordingly, see :ref:`m:float:mpfr`.

Hence, the first thing that the ``propagate()`` function of the ``Linear`` propagator does is to create a rounding object ``r`` as follows:

.. mpg-covered: literal-projection:docs/src/chapters/programming/p-floats.tex.in:172:linear:create rounding object

.. mpg-code:: linear:create rounding object

.. _propagators:floats:pruning-lower-and-upper-bounds:

.. mpg-paragraph:: Pruning lower and upper bounds.

The propagation rules for ``Linear`` are quite straightforward. As :math:`\mathtt{x}_0+\mathtt{x}_1+\mathtt{x}_2=0` we can isolate :math:`\mathtt{x}_0` (:math:`\mathtt{x}_1` and :math:`\mathtt{x}_2` are of course analogous):

.. math:: \mathtt{x}_0=-\mathtt{x}_1-\mathtt{x}_2

The upper bound of :math:`\mathtt{x}_0` can be constrained following:

.. math::

   \begin{aligned}
   \mathtt{x}_0&\leq&\max\left(-\mathtt{x}_1-\mathtt{x}_2\right)\\
               &=&-\min\left(\mathtt{x}_1+\mathtt{x}_2\right)\\
               &=&-\min\left(\min(\mathtt{x}_1)+\min(\mathtt{x}_2)\right)
   \end{aligned}

and, accordingly, the lower bound of :math:`\mathtt{x}_0` can be constrained following:

.. math::

   \begin{aligned}
   \mathtt{x}_0&\geq&\min\left(-\mathtt{x}_1-\mathtt{x}_2\right)\\
               &=&-\max\left(\mathtt{x}_1+\mathtt{x}_2\right)\\
               &=&-\max\left(\max(\mathtt{x}_1)+\max(\mathtt{x}_2\right))
   \end{aligned}

The equations can be translated directly into update operations, where :math:`\min` corresponds to rounding downwards:

.. mpg-covered: literal-projection:docs/src/chapters/programming/p-floats.tex.in:200:linear:prune upper bounds

.. mpg-code:: linear:prune upper bounds

and :math:`\max` corresponds to rounding upwards:

.. mpg-covered: literal-projection:docs/src/chapters/programming/p-floats.tex.in:202:linear:prune lower bounds

.. mpg-code:: linear:prune lower bounds

.. _sec:p:floats:propagation:

Modification events, propagation conditions, views, and advisors
----------------------------------------------------------------

This section summarizes how these concepts are specialized for float variables and propagators.

.. _propagators:floats:modification-events-and-propagation-conditions:

.. mpg-paragraph:: Modification events and propagation conditions.

.. mpg-covered: caption:docs/src/chapters/programming/p-floats.tex.in:215:fig:p:floats:propagation_conditions

.. mpg-covered: figure:docs/src/chapters/programming/p-floats.tex.in:215:fig:p:floats:propagation_conditions

.. mpg-covered: table:docs/src/chapters/programming/p-floats.tex.in:217:tabular@docs/src/chapters/programming/p-floats.tex.in:217

.. mpg-figure:: Float modification events and propagation conditions
   :name: fig:p:floats:propagation_conditions

   .. container:: center

      +----------------------------------+--------------------------------------------------+
      | **float modification events**    |                                                  |
      +----------------------------------+--------------------------------------------------+
      | ``Float::ME_FLOAT_NONE``         | the view has not been changed                    |
      +----------------------------------+--------------------------------------------------+
      | ``Float::ME_FLOAT_FAILED``       | the domain has become empty                      |
      +----------------------------------+--------------------------------------------------+
      | ``Float::ME_FLOAT_VAL``          | the view has been assigned                       |
      +----------------------------------+--------------------------------------------------+
      | ``Float::ME_FLOAT_BND``          | the bounds have changed (the domain has changed) |
      +----------------------------------+--------------------------------------------------+
      |                                  |                                                  |
      +----------------------------------+--------------------------------------------------+
      | **float propagation conditions** |                                                  |
      +----------------------------------+--------------------------------------------------+
      | ``Float::PC_FLOAT_VAL``          | schedule when the view is assigned               |
      +----------------------------------+--------------------------------------------------+
      | ``Float::PC_FLOAT_BND``          | schedule when the domain changes                 |
      +----------------------------------+--------------------------------------------------+
      | ``Float::PC_FLOAT_NONE``         | do not schedule                                  |
      +----------------------------------+--------------------------------------------------+

The modification events and propagation conditions for float propagators (see :numref:`fig:p:floats:propagation_conditions`) capture how the variable domain of a float view can change.

.. _propagators:floats:float-variable-views:

.. mpg-paragraph:: Float variable views.

In addition to the basic ``Float::FloatView``\ class, there are two other float views: ``Float::MinusView``, and ``Float::ScaleView``. The two latter views are defined similarly to minus view for integers (see :ref:`sec:p:views:int:minus`) and scale views for integers (see :ref:`sec:p:views:int:constantscale`).

.. _propagators:floats:advisors-for-float-propagators:

.. mpg-paragraph:: Advisors for float propagators.

Advisors for float constraints get informed about the domain modifications using a float delta of class ``Float::FloatDelta``.

Float deltas are also represented by a minimum and maximum float number and hence also constitute a closed interval (like float values and float variables). That means that a float delta cannot describe exactly which values have been removed. For example, assume that ``x`` is a float view and that the domain of ``x`` is :math:`\left[-1.0\;..\;1.0\right]`. Then, executing

.. mpg-code:: snippet:p-floats:fig:p:floats:propagation_conditions:code:1
   :direct:

will generate a float delta ``d`` such that ``x.min(d)`` returns ``0.0`` and ``x.max(d)`` returns ``1.0`` even though the domain of ``x`` is now :math:`\left[-1.0\;..\;0.0\right]` and still includes :math:`0.0`.
