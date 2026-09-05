.. _chap:m:float:


.. _modeling:m-float:float-variables-and-constraints:

Float variables and constraints
===============================

This chapter gives an overview over float variables and float constraints in Gecode. Just like :ref:`chap:m:int` does for integer and Boolean variables, this chapter serves as a starting point for using float variables. For the reference documentation, please consult :api:`Using float variables and constraints <TaskModelFloat>`.

.. _modeling:m-float:overview:

.. mpg-paragraph:: Overview.

:ref:`sec:m:float:val` explains float values whereas :ref:`sec:m:float:var` explains float variables. The sections :ref:`sec:m:float:post` and :ref:`sec:m:float:exec` provide an overview of the constraints that are available for float variables in Gecode.

.. important::

   Do not forget to add

   .. mpg-code:: snippet:m-float:chap:m:float:code:1
      :direct:

   to your program when you want to use float variables. Note that the same conventions hold as in :ref:`chap:m:int`.

..

.. _m:float:mpfr:

.. mpg-tip:: Transcendental and trigonometric functions and constraints

   When compiling Gecode, by default transcendental and trigonometric functions and constraints are disabled. In order to enable them, you have to install additional third-party libraries and provide additional options to the configuration of Gecode, see :ref:`par:m:started:mpfr`.


   To find out whether the functions and constraints are enabled, consult :ref:`tip:m:comfy:conf`.

.. _sec:m:float:val:


.. _modeling:m-float:float-values-and-numbers:

Float values and numbers
------------------------

A *floating point value* (short, *float value*, see :api:`FloatVal`) is represented as a closed interval of two *floating point numbers* (short, *float number*, see :api:`Float variables <TaskModelFloatVars>`). That is, a float value is a closed interval :math:`\left[a..b\right]` which includes all real numbers :math:`n\in\RR` such that :math:`a\leq n` and :math:`n\leq b`. The float number type ``FloatNum`` is defined as ``double``.

The reason why a float value is not represented by a single floating point number is that real numbers cannot be represented exactly and that operations on floating point numbers perform rounding. All operations (see below) on float values try to be as *accurate* as possible (so the interval :math:`\left[a..b\right]` for a float value is as small as possible) while being *correct* (no possible real number is ever excluded due to rounding). The classical reference on interval arithmetic is :cite:`Moore:1966`, for more information see also the Wikipedia article on `interval arithmetic <http://en.wikipedia.org/wiki/Interval_arithmetic>`__.

A float value ``x`` represented by the interval :math:`\left[a..b\right]` provides many member functions such as ``min()`` (returning :math:`a`) and ``max()`` (returning :math:`b`), see :api:`FloatVal`. The float value ``x`` is called *tight* if :math:`a` equals :math:`b` or if :math:`b` is the smallest representable float number larger than :math:`a`. If ``x`` is tight, ``x.tight()`` returns ``true``.

A float value can be initialized from a single float number such as in

.. mpg-code:: snippet:m-float:sec:m:float:val:code:1
   :direct:


or from two float numbers such as in

.. mpg-code:: snippet:m-float:sec:m:float:val:code:2
   :direct:


Float numbers (and other numbers) are automatically cast to float values if needed, for example in

.. mpg-code:: snippet:m-float:sec:m:float:val:code:3
   :direct:


or

.. mpg-code:: snippet:m-float:sec:m:float:val:code:4
   :direct:


.. _modeling:m-float:predefined-float-values:

.. mpg-paragraph:: Predefined float values.

The static member functions ``pi_half()``, ``pi()``, and ``pi_twice()`` of :api:`FloatVal` return float values for :math:`\frac{\pi}{2}`, :math:`\pi`, and :math:`2\pi` respectively.

.. _modeling:m-float:arithmetic-operators:

.. mpg-paragraph:: Arithmetic operators.

For float values, the standard arithmetic operators ``+``, ``-``, ``*``, and ``/`` and their assignment variants ``+=``, ``-=``, ``*=``, and ``/=`` are defined with the obvious meaning.

.. _modeling:m-float:comparison-operators:

.. mpg-paragraph:: Comparison operators.

The usual float value comparisons ``==``, ``!=``, ``<=``, ``<``, ``>``, and ``>=`` are provided with *entailment* semantics (or subsumption semantics).

For example, the comparison

.. mpg-code:: snippet:m-float:sec:m:float:val:code:5
   :direct:


returns ``true`` if and only if ``x.max()<y.min()`` returns ``true``. That means, ``x<y`` returns ``false`` if either ``x`` is larger or equal than ``y`` or it cannot yet be decided: both ``x`` and ``y`` still represent values which are both smaller and greater or equal.

.. _modeling:m-float:functions-on-float-values:

.. mpg-paragraph:: Functions on float values.

.. mpg-figure:: Functions on float values (``x`` and ``y`` are float values; ``n`` is a non-negative integer)
   :name: fig:m:float:val:fun
   :short-caption: Functions on float values

   .. container:: center

      +----------------+-------------------------------------------------------------+---------+
      | function       | meaning                                                     | default |
      +================+=============================================================+=========+
      | ``max(x,y)``   | maximum :math:`\max(\mathtt{x},\mathtt{y})`                 | yes     |
      +----------------+-------------------------------------------------------------+---------+
      | ``min(x,y)``   | minimum :math:`\max(\mathtt{x},\mathtt{y})`                 | yes     |
      +----------------+-------------------------------------------------------------+---------+
      | ``abs(x)``     | absolute value :math:`|\mathtt{x}|`                         | yes     |
      +----------------+-------------------------------------------------------------+---------+
      | ``sqrt(x)``    | square root :math:`\sqrt{x}`                                | yes     |
      +----------------+-------------------------------------------------------------+---------+
      | ``sqr(x)``     | square :math:`\mathtt{x}^2`                                 | yes     |
      +----------------+-------------------------------------------------------------+---------+
      | ``pow(x,n)``   | :math:`\mathtt{n}`-th power :math:`\mathtt{x}^{\mathtt{n}}` | yes     |
      +----------------+-------------------------------------------------------------+---------+
      | ``nroot(x,n)`` | :math:`\mathtt{n}`-th root :math:`\sqrt[n]{x}`              | yes     |
      +----------------+-------------------------------------------------------------+---------+
      | ``fmod(x,y)``  | remainder of :math:`\mathtt{x}/\mathtt{y}`                  |         |
      +----------------+-------------------------------------------------------------+---------+
      | ``exp(x)``     | exponential :math:`\exp(\mathtt{x})`                        |         |
      +----------------+-------------------------------------------------------------+---------+
      | ``log(x)``     | natural logarithm :math:`\log(\mathtt{x})`                  |         |
      +----------------+-------------------------------------------------------------+---------+
      | ``sin(x)``     | sine :math:`\sin(\mathtt{x})`                               |         |
      +----------------+-------------------------------------------------------------+---------+
      | ``cos(x)``     | cosine :math:`\cos(\mathtt{x})`                             |         |
      +----------------+-------------------------------------------------------------+---------+
      | ``tan(x)``     | tangent :math:`\tan(\mathtt{x})`                            |         |
      +----------------+-------------------------------------------------------------+---------+
      | ``asin(x)``    | arcsine :math:`\arcsin(\mathtt{x})`                         |         |
      +----------------+-------------------------------------------------------------+---------+
      | ``acos(x)``    | arccosine :math:`\arccos(\mathtt{x})`                       |         |
      +----------------+-------------------------------------------------------------+---------+
      | ``atan(x)``    | arctangent :math:`\arctan(\mathtt{x})`                      |         |
      +----------------+-------------------------------------------------------------+---------+
      | ``sinh(x)``    | hyperbolic sine :math:`\sinh(\mathtt{x})`                   |         |
      +----------------+-------------------------------------------------------------+---------+
      | ``cosh(x)``    | hyperbolic cosine :math:`\cosh(\mathtt{x})`                 |         |
      +----------------+-------------------------------------------------------------+---------+
      | ``tanh(x)``    | hyperbolic tangent :math:`\tanh(\mathtt{x})`                |         |
      +----------------+-------------------------------------------------------------+---------+
      | ``asinh(x)``   | hyperbolic arcsine :math:`\arcsinh(\mathtt{x})`             |         |
      +----------------+-------------------------------------------------------------+---------+
      | ``acosh(x)``   | hyperbolic arccosine :math:`\arccosh(\mathtt{x})`           |         |
      +----------------+-------------------------------------------------------------+---------+
      | ``atanh(x)``   | hyperbolic arctangent :math:`\arctanh(\mathtt{x})`          |         |
      +----------------+-------------------------------------------------------------+---------+

:numref:`fig:m:float:val:fun` lists the available functions on float values. The functions marked as default are always supported, the others only if Gecode has been built accordingly, see :ref:`m:float:mpfr`.

.. _sec:m:float:var:


.. _modeling:m-float:float-variables:

Float variables
---------------

Float variables in Gecode model sets of real numbers and are instances of the class :api:`FloatVar`.

.. mpg-tip:: Still do not use views for modeling

   Just as for integer variables, you should not feel tempted to use views of float variables (such as ``FloatView``) for modeling. Views can only be used for implementing propagators and branchers, see :ref:`part:p` and :ref:`part:b`.


.. _modeling:m-float:representing-float-domains-as-intervals:

.. mpg-paragraph:: Representing float domains as intervals.

The domain of a float variable is represented exactly as a float value: a closed interval :math:`\left[a..b\right]` which represents all real numbers :math:`n\in\RR` such that :math:`a\leq n` and :math:`n\leq b`. A float variable is *assigned* if the interval :math:`\left[a..b\right]` is tight (see :ref:`sec:m:float:val`). [1]_

.. _modeling:m-float:creating-a-float-variable:

.. mpg-paragraph:: Creating a float variable.

New float variables are created using a constructor. A new float variable ``x`` is created by

.. mpg-code:: snippet:m-float:sec:m:float:var:code:1
   :direct:


This declares a variable ``x`` of type :api:`FloatVar` in the space ``home``, creates a new float variable implementation with domain :math:`\left[-1.0..1.0\right]`, and makes ``x`` refer to the newly created float variable implementation.

You find the full interface in the reference documentation of the class :api:`FloatVar`. An attempt to create a float variable with an empty domain throws an exception of type :api:`Float::VariableEmptyDomain`.

As for integer variables, the default and copy constructors do not create new variable implementations. Instead, the variable does not refer to any variable implementation (default constructor) or to the same variable implementation (copy constructor). For example in

.. mpg-code:: snippet:m-float:sec:m:float:var:code:2
   :direct:


the variables ``x``, ``y``, and ``z`` all refer to the same float variable implementation.

.. _modeling:m-float:limits:

.. mpg-paragraph:: Limits.

Float numbers range from :math:`\mathtt{Float::Limits::min}` to :math:`\mathtt{Float::Limits::max}` which also define the numbers that can represent float values and float variables. The limits are defined in the namespace :api:`Float::Limits`.

.. mpg-tip:: Small variable domains are still beautiful

   Just like integer variables (see :ref:`tip:m:integer:beautifuldomains`), float variables do not have a constructor that creates a variable with the largest possible domain. And again, one has to worry and the omission is deliberate to make you worry. So think about the initial domains carefully when modeling.


.. _modeling:m-float:variable-access-functions:

.. mpg-paragraph:: Variable access functions.

You can access the current domain of a float variable ``x`` using member functions such as ``x.min()`` and ``x.max()``. Furthermore, you can print a float variable’s domain using the standard output operator ``<<``.

.. _modeling:m-float:updating-variables:

.. mpg-paragraph:: Updating variables.

Float variables behave exactly like integer variables during cloning of a space. A float variable is updated by

.. mpg-code:: snippet:m-float:sec:m:float:var:code:3
   :direct:


where ``y`` is the variable from which ``x`` is to be updated. While ``home`` is the space ``x`` belongs to, ``y`` belongs to the space which is being cloned.

.. _modeling:m-float:variable-and-argument-arrays:

.. mpg-paragraph:: Variable and argument arrays.

Float variable arrays can be allocated using the class :api:`FloatVarArray`. The constructors of this class take the same arguments as the float variable constructors, preceded by the size of the array. For example,

.. mpg-code:: snippet:m-float:sec:m:float:var:code:4
   :direct:


creates an array of four float variables, each with domain :math:`\left[-1.0..1.2\right]`.

To pass temporary data structures as arguments, you can use the :api:`FloatVarArgs` class. Some float constraints are defined in terms of arrays of float values. These can be passed using the :api:`FloatValArgs` class. Float variable and value argument arrays support the same operations introduced in :ref:`sec:m:integer:args` but :api:`FloatValArgs` do not support the initialization with a variable number of float values.

.. _sec:m:float:post:


.. _modeling:m-float:constraint-overview:

Constraint overview
-------------------

This section introduces the different groups of constraints over float variables available in Gecode. The section serves only as an overview. For the details and the full list of available post functions, the section refers to the relevant reference documentation.

.. _modeling:m-float:reified-constraints:

.. mpg-paragraph:: Reified constraints.

Some float constraints (relation constraints, see :ref:`sec:m:float:rel`, and linear constraints, see :ref:`sec:m:float:linear`) also exist as a reified variant. If a reified version does exist, the reification information combining the Boolean control variable and an optional reification mode is passed as the last non-optional argument, see :ref:`sec:m:integer:halfreify`.

.. _sec:m:float:dom:


.. _modeling:m-float:domain-constraints:

Domain constraints
~~~~~~~~~~~~~~~~~~

:api:`Domain constraints <TaskModelFloatDomain>` constrain float variables and variable arrays to values from a given domain. For example, by

.. mpg-code:: snippet:m-float:sec:m:float:dom:code:1
   :direct:


the values of the variable ``x`` (or of all variables in a variable array ``x``) are constrained to be between the float numbers :math:`-2.0` and :math:`12.0`. Domain constraints also take float values as argument.

The domain of a float variable ``x`` can be constrained according to the domain of another float variable ``d`` by

.. mpg-code:: snippet:m-float:sec:m:float:dom:code:2
   :direct:


Here, ``x`` and ``d`` can also be arrays of float variables.

Domain constraints for a single variable also support reification.

.. _sec:m:float:rel:


.. _modeling:m-float:simple-relation-constraints:

Simple relation constraints
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. mpg-figure:: Float relation types
   :name: fig:m:float:frt

   .. container:: center

      +------------+-----------------------------------------+------------+--------------------------------------------+
      | ``FRT_EQ`` | equality (:math:`=`)                    | ``FRT_NQ`` | disequality (:math:`\neq`)                 |
      +------------+-----------------------------------------+------------+--------------------------------------------+
      | ``FRT_LE`` | strictly less inequality (:math:`<`)    | ``FRT_LQ`` | less or equal inequality (:math:`\leq`)    |
      +------------+-----------------------------------------+------------+--------------------------------------------+
      | ``FRT_GR`` | strictly greater inequality (:math:`>`) | ``FRT_GQ`` | greater or equal inequality (:math:`\geq`) |
      +------------+-----------------------------------------+------------+--------------------------------------------+

:api:`Simple relation constraints over float variables <TaskModelFloatRelFloat>` enforce relations between float variables and between float variables and float values. The relation depends on a float relation type ``FloatRelType`` (see :api:`Simple relation constraints over float variables <TaskModelFloatRelFloat>`). :numref:`fig:m:float:frt` lists the available float relation types and their meaning.

.. _modeling:m-float:binary-relation-constraints:

.. mpg-paragraph:: Binary relation constraints.

Assume that ``x`` and ``y`` are float variables. Then

.. mpg-code:: snippet:m-float:fig:m:float:frt:code:1
   :direct:


constrains ``x`` to be strictly less than ``y``. Similarly, by

.. mpg-code:: snippet:m-float:fig:m:float:frt:code:2
   :direct:


``x`` is constrained to be less than ``4.0``. Both variants of ``rel`` also support reification.

.. _tip:m:float:weak:

.. mpg-tip:: Weak propagation for strict inequalities (<, >) and disequality (≠)

   Unfortunately, the propagation for strict inequality (:math:`<`, :math:`>`) and disequality (:math:`\neq`) relations is rather weak.


   Consider the constraint ``x<y`` for float variables ``x`` and ``y`` with domains :math:`\left[a..b\right]` and :math:`\left[c..d\right]` respectively, where :math:`b>d` and :math:`c<a`. Then one would like to propagate that ``x`` must be less than :math:`d` and ``y`` must be larger than :math:`a`. However, this would require that the domains of ``x`` and ``y`` after propagation are the *open* intervals :math:`\left[a..d\right)` and :math:`\left(a..d\right]`. But only closed intervals can be represented by float variables!

   Hence, the best propagation one could get is that the new domains are represented by the closed intervals :math:`\left[a..d\right]` and :math:`\left[a..d\right]` (the same propagation one would get for the constraint :math:`\mathtt x\leq \mathtt y` in this case).

.. _modeling:m-float:constraints-between-variable-arrays-and-a-single-variable:

.. mpg-paragraph:: Constraints between variable arrays and a single variable.

If ``x`` is a float variable array and ``y`` is an float variable, then

.. mpg-code:: snippet:m-float:tip:m:float:weak:code:1
   :direct:


constrains all variables in ``x`` to be less than or equal to ``y``. Likewise,

.. mpg-code:: snippet:m-float:tip:m:float:weak:code:2
   :direct:


constrains all variables in ``x`` to be larger than ``7.0``.

.. _modeling:m-float:if-then-else-constraint:

.. mpg-paragraph:: If-then-else constraint.

An if-then-else constraint can be posted by

.. mpg-code:: snippet:m-float:tip:m:float:weak:code:3
   :direct:


where ``b`` is a Boolean variable and ``x``, ``y``, and ``z`` are float variables. In case ``b`` is one, then :math:`\mathtt{x}=\mathtt{z}` must hold, otherwise :math:`\mathtt{y}=\mathtt{z}` must hold.

.. _sec:m:float:arithmetic:


.. _modeling:m-float:arithmetic-constraints:

Arithmetic constraints
~~~~~~~~~~~~~~~~~~~~~~

.. mpg-figure:: Arithmetic constraints (``x``, ``y``, and ``z`` are float variables; ``n`` is a non-negative integer; ``b`` is a float number)
   :name: fig:m:float:arithmetic
   :short-caption: Arithmetic constraints

   .. container:: center

      +---------------------------+-------------------------------------------------+---------+
      | post function             | constraint posted                               | default |
      +===========================+=================================================+=========+
      | ``min(home, x, y, z);``   | :math:`\min(\mathtt x, \mathtt y)=\mathtt z`    | yes     |
      +---------------------------+-------------------------------------------------+---------+
      | ``max(home, x, y, z);``   | :math:`\max(\mathtt x, \mathtt y)=\mathtt z`    | yes     |
      +---------------------------+-------------------------------------------------+---------+
      | ``abs(home, x, y);``      | :math:`|\mathtt x|=\mathtt y`                   | yes     |
      +---------------------------+-------------------------------------------------+---------+
      | ``mult(home, x, y, z);``  | :math:`\mathtt x \cdot \mathtt y=\mathtt z`     | yes     |
      +---------------------------+-------------------------------------------------+---------+
      | ``div(home, x, y, z);``   | :math:`\mathtt{x} / \mathtt{y}=\mathtt{z}`      | yes     |
      +---------------------------+-------------------------------------------------+---------+
      | ``sqr(home, x, y);``      | :math:`{\mathtt x}^2=\mathtt y`                 | yes     |
      +---------------------------+-------------------------------------------------+---------+
      | ``sqrt(home, x, y);``     | :math:`\sqrt{\mathtt x}=\mathtt y`              | yes     |
      +---------------------------+-------------------------------------------------+---------+
      | ``pow(home, x, n, y);``   | :math:`{\mathtt x}^{\mathtt n}=\mathtt y`       | yes     |
      +---------------------------+-------------------------------------------------+---------+
      | ``nroot(home, x, n, y);`` | :math:`\sqrt[{\mathtt n}]{\mathtt x}=\mathtt y` | yes     |
      +---------------------------+-------------------------------------------------+---------+
      | ``exp(home, x, y)``       | :math:`\exp(\mathtt{x})=\mathtt y`              |         |
      +---------------------------+-------------------------------------------------+---------+
      | ``pow(home, b, x, y)``    | :math:`\mathtt{b}^\mathtt{x}=\mathtt y`         |         |
      +---------------------------+-------------------------------------------------+---------+
      | ``log(home, x, y)``       | :math:`\log(\mathtt{x})=\mathtt y`              |         |
      +---------------------------+-------------------------------------------------+---------+
      | ``log(home, b, x, y)``    | :math:`\log_{\mathtt{b}}(\mathtt{x})=\mathtt y` |         |
      +---------------------------+-------------------------------------------------+---------+
      | ``sin(home, x, y)``       | :math:`\sin(\mathtt{x})=\mathtt y`              |         |
      +---------------------------+-------------------------------------------------+---------+
      | ``cos(home, x, y)``       | :math:`\cos(\mathtt{x})=\mathtt y`              |         |
      +---------------------------+-------------------------------------------------+---------+
      | ``tan(home, x, y)``       | :math:`\tan(\mathtt{x})=\mathtt y`              |         |
      +---------------------------+-------------------------------------------------+---------+
      | ``asin(home, x, y)``      | :math:`\arcsin(\mathtt{x})=\mathtt y`           |         |
      +---------------------------+-------------------------------------------------+---------+
      | ``acos(home, x, y)``      | :math:`\arccos(\mathtt{x})=\mathtt y`           |         |
      +---------------------------+-------------------------------------------------+---------+
      | ``atan(home, x, y)``      | :math:`\arctan(\mathtt{x})=\mathtt y`           |         |
      +---------------------------+-------------------------------------------------+---------+

In addition to the constraints summarized in :numref:`fig:m:float:arithmetic` (see also :api:`Arithmetic constraints <TaskModelFloatArith>`), the minimum and maximum constraints are also available for float variable arrays. That is, for a float variable array ``x`` and a float variable ``y``

.. mpg-code:: snippet:m-float:fig:m:float:arithmetic:code:1
   :direct:


constrains ``y`` to be the minimum of the variables in ``x`` (``max`` is analogous).

The constraints marked as default in :numref:`fig:m:float:arithmetic` are always supported, the others only if Gecode has been built accordingly, see :ref:`m:float:mpfr`.

.. _sec:m:float:linear:


.. _modeling:m-float:linear-constraints:

Linear constraints
~~~~~~~~~~~~~~~~~~

:api:`Linear constraints over float variables <TaskModelFloatLI>` provide constraint post functions for linear constraints over float variables. The most general variant

.. mpg-code:: snippet:m-float:sec:m:float:linear:code:1
   :direct:


posts the linear constraint

.. math::

   \sum_{i=0}^{|\mathtt x|-1} \mathtt{a}_i \cdot \mathtt{x}_i =
   \mathtt c

with float value coefficients ``a`` (of type :api:`FloatValArgs`), float variables ``x``, and a float value ``c``. Note that ``a`` and ``x`` must have the same size. Of course, all other float relation types are supported, see :numref:`fig:m:float:frt` for a table of float relation types (note that, linear constraints also show poor propagation for strict inequalities and disequality as discussed in :ref:`tip:m:float:weak`). Multiple occurrences of the same variable in ``x`` are explicitly allowed and common terms :math:`a\cdot y` and :math:`b\cdot y` for the same variable :math:`y` are rewritten to :math:`(a+b)\cdot y` to increase propagation.

.. container:: samepage

   The array of coefficients can be omitted if all coefficients are one. That is,

   .. mpg-code:: snippet:m-float:sec:m:float:linear:code:2
      :direct:

   posts the linear constraint

   .. math:: \sum_{i=0}^{|\mathtt x|-1} \mathtt{x}_i > \mathtt c

   for a variable array ``x`` and a float value ``c``.

Instead of a float value ``c`` as the right-hand side of the linear constraint, a float variable can be used as well. All variants of ``linear`` support reification.

.. _sec:m:float:channel:


.. _modeling:m-float:channel-constraints:

Channel constraints
~~~~~~~~~~~~~~~~~~~

:api:`Channel constraints <TaskModelFloatChannel>` channel float variables to integer variables. To express that a float variable ``x`` is equal to an integer variable ``y`` is by posting either

.. mpg-code:: snippet:m-float:sec:m:float:channel:code:1
   :direct:


.. container:: samepage

   or

   .. mpg-code:: snippet:m-float:sec:m:float:channel:code:2
      :direct:

.. _sec:m:float:exec:


.. _modeling:m-float:synchronized-execution:

Synchronized execution
----------------------

Gecode offers support in :api:`Synchronized execution <TaskModelFloatExec>` for executing a function when float variables become assigned.

The following code

.. mpg-code:: snippet:m-float:sec:m:float:exec:code:1
   :direct:


posts a propagator that waits until the float variable ``x`` (or, if ``x`` is an array of float variables: all variables in ``x``) is assigned. If ``x`` becomes assigned, the function passed as argument is executed with the current home space passed as argument. The type of the function must be

.. mpg-code:: snippet:m-float:sec:m:float:exec:code:2
   :direct:


.. [1]
   Note that this means that a float variable is assigned even though its domain might still denote a set with more than one element. But this cannot be avoided as real numbers cannot be represented exactly.
