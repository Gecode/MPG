.. _chap:m:minimodel:


.. _modeling:m-minimodel:modeling-convenience-minimodel:

Modeling convenience: MiniModel
===============================

This chapter provides an overview of modeling convenience implemented by MiniModel. MiniModel (see `Direct modeling support <https://www.gecode.dev/doc/6.4.0/reference/group__TaskModelMiniModel.html>`__) provides some little helpers to the constraint modeler. However, it does not offer any new constraints or branchers.

.. _modeling:m-minimodel:overview:

.. mpg-paragraph:: Overview.

:ref:`sec:m:minimodel:exprrel` surveys how constraints represented by integer, Boolean, set, and float expressions and relations can be posted. How matrix interfaces for arrays can be defined and used is discussed in :ref:`sec:m:minimodel:matrix`. Support for defining cost functions for cost-based optimization is presented in :ref:`sec:m:minimodel:optimize`. Regular expressions for expressing extensional constraints are discussed in :ref:`sec:m:minimodel:reg`. :ref:`sec:m:minimodel:channel` surveys channeling functions, whereas :ref:`sec:m:minimodel:intalias` and :ref:`sec:m:minimodel:setalias` discuss aliases for some commonly used constraints.

.. important::

   Do not forget to add

   .. mpg-code:: snippet:m-minimodel:chap:m:minimodel:code:1
      :direct:

   to your program when you want to use MiniModel. Note that the same conventions hold as in :ref:`chap:m:int`.

.. _sec:m:minimodel:exprrel:


.. _modeling:m-minimodel:expressions-and-relations:

Expressions and relations
-------------------------

The main part of MiniModel consists of overloaded operators and functions that provide a more natural syntax for posting constraints. These operators can be used in two slightly different ways. You can post a relation, or create a new variable from an expression.

For example, the following code creates a fresh integer variable ``z`` that is constrained to be equal to the given *expression* ``3*x-4*y+2``, where both ``x`` and ``y`` are integer variables:

.. mpg-code:: snippet:m-minimodel:sec:m:minimodel:exprrel:code:1
   :direct:


An important aspect of posting an expression is that the returned variable is initialized with a reasonably small variable domain, see :ref:`tip:m:integer:beautifuldomains`.

A *relation* can be posted using the ``rel`` function, which posts the corresponding constraints and consequently returns ``void``. Assume that ``z`` is an integer variable, then

.. mpg-code:: snippet:m-minimodel:sec:m:minimodel:exprrel:code:2
   :direct:


posts the same constraint as in the previous example.

MiniModel provides syntax for expressions and relations over integer, Boolean, set, and float variables, which can be freely mixed. For example, the following code snippet returns a Boolean variable that is true if and only if :math:`\{\mathtt x\}\subseteq \mathtt s` and :math:`|\mathtt s|=\mathtt y`, where :math:`\mathtt x` and :math:`\mathtt y` are integer variables, and :math:`\mathtt s` is a set variable:

.. mpg-code:: snippet:m-minimodel:sec:m:minimodel:exprrel:code:3
   :direct:


The rest of this section presents the different ways to construct expressions and relations, grouped by the type of the expressions.

.. _sec:m:minimodel:exprrel:int:


.. _modeling:m-minimodel:integer-expressions-and-relations:

Integer expressions and relations
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. mpg-figure:: Integer expressions
   :name: fig:m:minimodel:integer:expr

   .. container:: center

      +----------------------------------------+-------------+------------------------------------------------------------------------------------------------------------------------------------+-------------------------------------+
      | :math:`\langle\mathit{IntExpr}\rangle` | :math:`::=` | :math:`\langle n\rangle`                                                                                                           | integer value                       |
      +----------------------------------------+-------------+------------------------------------------------------------------------------------------------------------------------------------+-------------------------------------+
      |                                        | :math:`|`   | :math:`\langle x\rangle`                                                                                                           | integer or Boolean variable         |
      +----------------------------------------+-------------+------------------------------------------------------------------------------------------------------------------------------------+-------------------------------------+
      |                                        | :math:`|`   | :math:`\operatorname{\texttt{-}}\langle\mathit{IntExpr}\rangle`                                                                    | unary minus                         |
      +----------------------------------------+-------------+------------------------------------------------------------------------------------------------------------------------------------+-------------------------------------+
      |                                        | :math:`|`   | :math:`\langle\mathit{IntExpr}\rangle\mathbin{\texttt{+}} \langle\mathit{IntExpr}\rangle`                                          | addition                            |
      +----------------------------------------+-------------+------------------------------------------------------------------------------------------------------------------------------------+-------------------------------------+
      |                                        | :math:`|`   | :math:`\langle\mathit{IntExpr}\rangle\mathbin{\texttt{-}} \langle\mathit{IntExpr}\rangle`                                          | subtraction                         |
      +----------------------------------------+-------------+------------------------------------------------------------------------------------------------------------------------------------+-------------------------------------+
      |                                        | :math:`|`   | :math:`\langle\mathit{IntExpr}\rangle\mathbin{\texttt{*}} \langle\mathit{IntExpr}\rangle`                                          | multiplication                      |
      +----------------------------------------+-------------+------------------------------------------------------------------------------------------------------------------------------------+-------------------------------------+
      |                                        | :math:`|`   | :math:`\langle\mathit{IntExpr}\rangle\mathbin{\texttt{/}} \langle\mathit{IntExpr}\rangle`                                          | integer division                    |
      +----------------------------------------+-------------+------------------------------------------------------------------------------------------------------------------------------------+-------------------------------------+
      |                                        | :math:`|`   | :math:`\langle\mathit{IntExpr}\rangle\mathbin{\texttt{\%}} \langle\mathit{IntExpr}\rangle`                                         | modulo                              |
      +----------------------------------------+-------------+------------------------------------------------------------------------------------------------------------------------------------+-------------------------------------+
      |                                        | :math:`|`   | :math:`\texttt{sum(}\langle\overline x\rangle\texttt{)}`                                                                           | sum of integer or Boolean variables |
      +----------------------------------------+-------------+------------------------------------------------------------------------------------------------------------------------------------+-------------------------------------+
      |                                        | :math:`|`   | :math:`\texttt{sum(}\langle\overline n\rangle\texttt{,}\langle\overline x\rangle\texttt{)}`                                        | sum of integer or Boolean variables |
      +----------------------------------------+-------------+------------------------------------------------------------------------------------------------------------------------------------+-------------------------------------+
      |                                        |             |                                                                                                                                    | with integer coefficients           |
      +----------------------------------------+-------------+------------------------------------------------------------------------------------------------------------------------------------+-------------------------------------+
      |                                        | :math:`|`   | :math:`\operatorname{\texttt{min}}(\langle\mathit{IntExpr}\rangle,\langle\mathit{IntExpr}\rangle)`                                 | minimum                             |
      +----------------------------------------+-------------+------------------------------------------------------------------------------------------------------------------------------------+-------------------------------------+
      |                                        | :math:`|`   | :math:`\operatorname{\texttt{min}}(\langle\overline x\rangle)`                                                                     | minimum of integer variables        |
      +----------------------------------------+-------------+------------------------------------------------------------------------------------------------------------------------------------+-------------------------------------+
      |                                        | :math:`|`   | :math:`\operatorname{\texttt{max}}(\langle\mathit{IntExpr}\rangle,\langle\mathit{IntExpr}\rangle)`                                 | maximum                             |
      +----------------------------------------+-------------+------------------------------------------------------------------------------------------------------------------------------------+-------------------------------------+
      |                                        | :math:`|`   | :math:`\operatorname{\texttt{max}}(\langle\overline x\rangle)`                                                                     | maximum of integer variables        |
      +----------------------------------------+-------------+------------------------------------------------------------------------------------------------------------------------------------+-------------------------------------+
      |                                        | :math:`|`   | :math:`\operatorname{\texttt{abs}}(\langle\mathit{IntExpr}\rangle)`                                                                | absolute value                      |
      +----------------------------------------+-------------+------------------------------------------------------------------------------------------------------------------------------------+-------------------------------------+
      |                                        | :math:`|`   | :math:`\operatorname{\texttt{sqr}}(\langle\mathit{IntExpr}\rangle)`                                                                | square                              |
      +----------------------------------------+-------------+------------------------------------------------------------------------------------------------------------------------------------+-------------------------------------+
      |                                        | :math:`|`   | :math:`\operatorname{\texttt{sqrt}}(\langle\mathit{IntExpr}\rangle)`                                                               | square root                         |
      +----------------------------------------+-------------+------------------------------------------------------------------------------------------------------------------------------------+-------------------------------------+
      |                                        | :math:`|`   | :math:`\operatorname{\texttt{pow}}(\langle\mathit{IntExpr}\rangle,\langle n\rangle)`                                               | power                               |
      +----------------------------------------+-------------+------------------------------------------------------------------------------------------------------------------------------------+-------------------------------------+
      |                                        | :math:`|`   | :math:`\operatorname{\texttt{nroot}}(\langle\mathit{IntExpr}\rangle,\langle n\rangle)`                                             | :math:`n`-th root                   |
      +----------------------------------------+-------------+------------------------------------------------------------------------------------------------------------------------------------+-------------------------------------+
      |                                        | :math:`|`   | :math:`\operatorname{\texttt{element}}(\langle\overline x\rangle,\langle\mathit{IntExpr}\rangle)`                                  | array element of integer variables  |
      +----------------------------------------+-------------+------------------------------------------------------------------------------------------------------------------------------------+-------------------------------------+
      |                                        | :math:`|`   | :math:`\operatorname{\texttt{element}}(\langle\overline n\rangle,\langle\mathit{IntExpr}\rangle)`                                  | array element of integers           |
      +----------------------------------------+-------------+------------------------------------------------------------------------------------------------------------------------------------+-------------------------------------+
      |                                        | :math:`|`   | :math:`\operatorname{\texttt{ite}}(\langle\mathit{BoolExpr}\rangle,\langle\mathit{IntExpr}\rangle,\langle\mathit{IntExpr}\rangle)` | if-then-else                        |
      +----------------------------------------+-------------+------------------------------------------------------------------------------------------------------------------------------------+-------------------------------------+
      |                                        | :math:`|`   | :math:`\operatorname{\texttt{min}}(\langle\mathit{SetExpr}\rangle)`                                                                | minimum of a set expression         |
      +----------------------------------------+-------------+------------------------------------------------------------------------------------------------------------------------------------+-------------------------------------+
      |                                        | :math:`|`   | :math:`\operatorname{\texttt{max}}(\langle\mathit{SetExpr}\rangle)`                                                                | maximum of a set expression         |
      +----------------------------------------+-------------+------------------------------------------------------------------------------------------------------------------------------------+-------------------------------------+
      |                                        | :math:`|`   | :math:`\operatorname{\texttt{cardinality}}(\langle\mathit{SetExpr}\rangle)`                                                        | cardinality of a set expression     |
      +----------------------------------------+-------------+------------------------------------------------------------------------------------------------------------------------------------+-------------------------------------+
      |                                        |             |                                                                                                                                    |                                     |
      +----------------------------------------+-------------+------------------------------------------------------------------------------------------------------------------------------------+-------------------------------------+
      | :math:`\langle\overline x\rangle`      | :math:`::=` | array of integer or Boolean variables                                                                                              |                                     |
      +----------------------------------------+-------------+------------------------------------------------------------------------------------------------------------------------------------+-------------------------------------+
      | :math:`\langle\overline n\rangle`      | :math:`::=` | array of integers                                                                                                                  |                                     |
      +----------------------------------------+-------------+------------------------------------------------------------------------------------------------------------------------------------+-------------------------------------+

.. mpg-figure:: Integer relations
   :name: fig:m:minimodel:integer:rel

   .. container:: center

      +---------------------------------------+-------------+---------------------------------------------------------------------------------------------------------------+-------------------------+
      | :math:`\langle\mathit{IntRel}\rangle` | :math:`::=` | :math:`\langle\mathit{IntExpr}\rangle\mathrel{\langle r\rangle} \langle\mathit{IntExpr}\rangle`               | integer relation        |
      +---------------------------------------+-------------+---------------------------------------------------------------------------------------------------------------+-------------------------+
      |                                       | :math:`|`   | :math:`\operatorname{\texttt{dom}}(\langle x\rangle,\langle n\rangle)`                                        | domain relation         |
      +---------------------------------------+-------------+---------------------------------------------------------------------------------------------------------------+-------------------------+
      |                                       | :math:`|`   | :math:`\operatorname{\texttt{dom}}(\langle x\rangle,\langle n\rangle,\langle n\rangle)`                       | domain relation         |
      +---------------------------------------+-------------+---------------------------------------------------------------------------------------------------------------+-------------------------+
      |                                       | :math:`|`   | :math:`\operatorname{\texttt{dom}}(\langle x\rangle,\langle s\rangle)`                                        | domain relation         |
      +---------------------------------------+-------------+---------------------------------------------------------------------------------------------------------------+-------------------------+
      |                                       |             |                                                                                                               |                         |
      +---------------------------------------+-------------+---------------------------------------------------------------------------------------------------------------+-------------------------+
      | :math:`\langle n\rangle`              | :math:`::=` | integer value                                                                                                 |                         |
      +---------------------------------------+-------------+---------------------------------------------------------------------------------------------------------------+-------------------------+
      | :math:`\langle s\rangle`              | :math:`::=` | set constant (``IntSet``)                                                                                     |                         |
      +---------------------------------------+-------------+---------------------------------------------------------------------------------------------------------------+-------------------------+
      | :math:`\langle x\rangle`              | :math:`::=` | integer or Boolean variable                                                                                   |                         |
      +---------------------------------------+-------------+---------------------------------------------------------------------------------------------------------------+-------------------------+
      | :math:`\langle r\rangle`              | :math:`::=` | ``==`` :math:`\;|\;` ``!=`` :math:`\;|\;` ``<`` :math:`\;|\;` ``<=`` :math:`\;|\;` ``>`` :math:`\;|\;` ``>=`` | integer relation symbol |
      +---------------------------------------+-------------+---------------------------------------------------------------------------------------------------------------+-------------------------+

Integer expressions (that is, expressions that evaluate to an integer) are constructed according to the structure sketched in :numref:`fig:m:minimodel:integer:expr`, whereas integer relations are constructed according to the structure sketched in :numref:`fig:m:minimodel:integer:rel`. We use the standard C++ operators (for an example, see :ref:`sec:m:comfy:expr`), as well as several functions with intuitive names such as ``min`` or ``max``. Integer expressions and relations can be constructed over integer, Boolean, and set variables. In Gecode, integer expressions are of type `LinIntExpr <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1LinIntExpr.html>`__, which are constructed using `Linear expressions and relations <https://www.gecode.dev/doc/6.4.0/reference/group__TaskModelMiniModelLin.html>`__, `Arithmetic functions <https://www.gecode.dev/doc/6.4.0/reference/group__TaskModelMiniModelArith.html>`__, and some `Set expressions and relations <https://www.gecode.dev/doc/6.4.0/reference/group__TaskModelMiniModelSet.html>`__.

Even arrays of variables (possibly with integer argument arrays as coefficients) can be used for posting some expressions and relations. For example, if ``x`` and ``y`` are integer variables and ``z`` is an array of integer variables, then

.. mpg-code:: snippet:m-minimodel:fig:m:minimodel:integer:rel:code:1
   :direct:


posts a single linear constraint that involves all variables from the array ``z``.

As long as an expression is *linear* (i.e., it can be represented as :math:`\sum a_i\cdot x_i` where the :math:`a_i` are integers and :math:`x_i` are integer or Boolean variables), the constraint posted for the expression will be as few ``linear`` constraints as possible (see :ref:`sec:m:integer:linear`) to ensure maximal constraint propagation. [1]_

*Non-linear* expressions, such as a multiplication of two variables, are handled by MiniModel using *decomposition*. For example, posting the constraint

.. mpg-code:: snippet:m-minimodel:fig:m:minimodel:integer:rel:code:2
   :direct:


for integer variables ``a``, ``b``, ``c``, and ``d`` is equivalent to the decomposition

.. mpg-code:: snippet:m-minimodel:fig:m:minimodel:integer:rel:code:3
   :direct:


Like the post functions for integer and Boolean constraints presented in :ref:`sec:m:integer:post`, posting integer expressions and relations supports an optional argument of type ``IntPropLevel`` to select the propagation level. For more information, see `Posting of expressions and relations <https://www.gecode.dev/doc/6.4.0/reference/group__TaskModelMiniModelPost.html>`__ and :ref:`sec:m:integer:generic`.

Using the ``expr()`` function, you can enforce a particular decomposition, and you can specify the propagation level for each subexpression. For example,

.. mpg-code:: snippet:m-minimodel:fig:m:minimodel:integer:rel:code:4
   :direct:


will perform domain propagation for the multiplication, but bounds propagation (the default) for the sum.

An ``element`` expression such as ``element(x,e)``, where ``x`` is an array of integers or integer variables, and ``e`` is an integer expression, corresponds to an array access ``x[e]``, implemented using an ``element`` constraint (see :ref:`sec:m:integer:element`).

MiniModel provides three integer expressions whose arguments are set expressions: the minimum of a set, the maximum of a set, and a set’s cardinality. We will see later how set expressions are constructed.

For examples of integer expressions, see `Alpha puzzle <https://www.gecode.dev/doc/6.4.0/reference/examples_2alpha_8cpp.html>`__, `SEND+MORE=MONEY puzzle <https://www.gecode.dev/doc/6.4.0/reference/money_8cpp.html>`__, `Grocery puzzle <https://www.gecode.dev/doc/6.4.0/reference/grocery_8cpp.html>`__, :ref:`chap:c:golomb`, :ref:`chap:c:warehouses`, and :ref:`sec:m:comfy:expr`.

.. _modeling:m-minimodel:integer-propagation-levels:

.. mpg-paragraph:: Integer propagation levels.

When posting integer expressions and relations it can be controlled which integer propagation level is used for each constraint. The integer propagation levels for all relevant constraints are specified by an object of class `IntPropLevels <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1IntPropLevels.html>`__. The ``expr()`` and ``rel()`` functions for posting expressions take an object of this class as last argument.

Declaring an object of class `IntPropLevels <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1IntPropLevels.html>`__ by default initializes all propagation levels to the default integer propagation level ``IPL_DEF``. All integer propagation levels can be initialized to, for example, ``IPL_DOM`` by

.. mpg-code:: snippet:m-minimodel:fig:m:minimodel:integer:rel:code:5
   :direct:


and then used as last argument of ``rel()`` and ``expr()`` for posting relations and expressions.

However, this also uses domain propagation for linear constraints as well as minimum and maximum with an arbitrary number of variables where domain propagation can be very slow. To use default propagation for these constraints, ``ipls`` can be modified by

.. mpg-code:: snippet:m-minimodel:fig:m:minimodel:integer:rel:code:6
   :direct:


The list of constraints for which the propagation level can be specified can be seen from the class definition `IntPropLevels <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1IntPropLevels.html>`__.

.. _sec:m:minimodel:bool:


.. _modeling:m-minimodel:boolean-expressions-and-relations:

Boolean expressions and relations
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. mpg-figure:: Boolean expressions
   :name: fig:m:minimodel:bool

   .. container:: center

      +-----------------------------------------+-------------+---------------------------------------------------------------------------------------------------+------------------------------------+
      | :math:`\langle\mathit{BoolExpr}\rangle` | :math:`::=` | :math:`\langle x\rangle`                                                                          | Boolean variable                   |
      +-----------------------------------------+-------------+---------------------------------------------------------------------------------------------------+------------------------------------+
      |                                         | :math:`|`   | :math:`\operatorname{\texttt{!}}\langle\mathit{BoolExpr}\rangle`                                  | negation                           |
      +-----------------------------------------+-------------+---------------------------------------------------------------------------------------------------+------------------------------------+
      |                                         | :math:`|`   | :math:`\langle\mathit{BoolExpr}\rangle\mathbin{\texttt{\&\&}} \langle\mathit{BoolExpr}\rangle`    | conjunction                        |
      +-----------------------------------------+-------------+---------------------------------------------------------------------------------------------------+------------------------------------+
      |                                         | :math:`|`   | :math:`\langle\mathit{BoolExpr}\rangle\mathbin{\texttt{||}} \langle\mathit{BoolExpr}\rangle`      | disjunction                        |
      +-----------------------------------------+-------------+---------------------------------------------------------------------------------------------------+------------------------------------+
      |                                         | :math:`|`   | :math:`\langle\mathit{BoolExpr}\rangle\mathbin{\texttt{==}} \langle\mathit{BoolExpr}\rangle`      | equivalence                        |
      +-----------------------------------------+-------------+---------------------------------------------------------------------------------------------------+------------------------------------+
      |                                         | :math:`|`   | :math:`\langle\mathit{BoolExpr}\rangle\mathbin{\texttt{!=}} \langle\mathit{BoolExpr}\rangle`      | non-equivalence                    |
      +-----------------------------------------+-------------+---------------------------------------------------------------------------------------------------+------------------------------------+
      |                                         | :math:`|`   | :math:`\langle\mathit{BoolExpr}\rangle\mathbin{\texttt{>{}>{}}} \langle\mathit{BoolExpr}\rangle`  | implication                        |
      +-----------------------------------------+-------------+---------------------------------------------------------------------------------------------------+------------------------------------+
      |                                         | :math:`|`   | :math:`\langle\mathit{BoolExpr}\rangle\mathbin{\texttt{<{}<{}}} \langle\mathit{BoolExpr}\rangle`  | reverse implication                |
      +-----------------------------------------+-------------+---------------------------------------------------------------------------------------------------+------------------------------------+
      |                                         | :math:`|`   | :math:`\langle\mathit{BoolExpr}\rangle\mathbin{\texttt{\^{}}} \langle\mathit{BoolExpr}\rangle`    | exclusive or                       |
      +-----------------------------------------+-------------+---------------------------------------------------------------------------------------------------+------------------------------------+
      |                                         | :math:`|`   | :math:`\operatorname{\texttt{element}}(\langle\overline x\rangle,\langle\mathit{IntExpr}\rangle)` | array element of Boolean variables |
      +-----------------------------------------+-------------+---------------------------------------------------------------------------------------------------+------------------------------------+
      |                                         | :math:`|`   | :math:`\langle\mathit{IntRel}\rangle`                                                             | reified integer relation           |
      +-----------------------------------------+-------------+---------------------------------------------------------------------------------------------------+------------------------------------+
      |                                         | :math:`|`   | :math:`\langle\mathit{SetRel}\rangle`                                                             | reified set relation               |
      +-----------------------------------------+-------------+---------------------------------------------------------------------------------------------------+------------------------------------+
      |                                         | :math:`|`   | :math:`\langle\mathit{FloatRel}\rangle`                                                           | reified float relation             |
      +-----------------------------------------+-------------+---------------------------------------------------------------------------------------------------+------------------------------------+

`Boolean expressions <https://www.gecode.dev/doc/6.4.0/reference/group__TaskModelMiniModelBool.html>`__ are constructed using standard C++ operators according to the structure sketched in :numref:`fig:m:minimodel:bool`.

Again, the purpose of a Boolean expression or relation is to post a corresponding constraint for it (see `Posting of expressions and relations <https://www.gecode.dev/doc/6.4.0/reference/group__TaskModelMiniModelPost.html>`__). Posting a Boolean expression returns a new Boolean variable that is constrained to the value of the expression. Several constraints might be posted for a single expression, however as few constraints as possible are posted. For example, all negation constraints are eliminated by rewriting the Boolean expression into NNF (negation normal form) and conjunction and disjunction constraints are combined whenever possible.

For example, the Boolean expression ``x && (y >> z)`` (to be read as :math:`\mathtt{x}\wedge(\mathtt{y}\to\mathtt{z})`) for Boolean variables ``x``, ``y``, and ``z`` is posted by

.. mpg-code:: snippet:m-minimodel:fig:m:minimodel:bool:code:1
   :direct:


..

.. mpg-tip:: Boolean precedences

   Note that the precedences of the Boolean connectives are different from the usual mathematical notation. In C++, operator precedence cannot be changed, so the precedences are as follows (high to low): ``!``, ``<<``, ``>>``, ``==``, ``!=``, ``^``, ``&&``, ``||``. For instance, this means that the expression :math:`b_0  \mathbin{\texttt{==}} b_1 \mathbin{\texttt{>{}>{}}}b_2` will be interpreted as :math:`(b_0\leftrightarrow b_1) \rightarrow b_2` instead of the more canonical :math:`b_0 \leftrightarrow (b_1\rightarrow b_2)`. If in doubt, use parentheses!

Any Boolean expression :math:`e` corresponds to the Boolean relation stating that :math:`e` is true. Posting a Boolean relation posts the corresponding Boolean constraint. Using the Boolean expression from above,

.. mpg-code:: snippet:m-minimodel:fig:m:minimodel:bool:code:2
   :direct:


posts that :math:`\mathtt{x}\wedge(\mathtt{y}\to\mathtt{z})` must be true, whereas

.. mpg-code:: snippet:m-minimodel:fig:m:minimodel:bool:code:3
   :direct:


posts that :math:`\mathtt{x}\wedge(\mathtt{y}\to\mathtt{z})` must be false.

A Boolean ``element`` expression such as ``element(x,e)``, where ``x`` is an array of Boolean variables, and ``e`` is an integer expression, corresponds to an array access ``x[e]``, implemented using an ``element`` constraint (see :ref:`sec:m:integer:element`).

Boolean expressions include reified integer relations. As an example consider the placement of two squares :math:`s_1` and :math:`s_2` such that the squares do not overlap. A well known model for this constraint is

.. math::

   \begin{array}{ccccc}
     \mathtt{x}_1+\mathtt{d}_1\leq \mathtt{x}_2 & \vee &
     \mathtt{x}_2+\mathtt{d}_2\leq \mathtt{x}_1 & \vee \\
     \mathtt{y}_1+\mathtt{d}_1\leq \mathtt{y}_2 & \vee &
     \mathtt{y}_2+\mathtt{d}_2\leq \mathtt{y}_1\\
   \end{array}

.. container:: window

   The meaning of the integer variables :math:`\mathtt{x}_i` and :math:`\mathtt{y}_i`, and the integer values :math:`\mathtt{d}_i` is sketched to the right. The squares do not overlap, if the relative position of :math:`s_1` with respect to :math:`s_2` is either left, right, above, or below. As soon as one of the relationships is established, the squares do not overlap. Please also consult :ref:`sec:m:integer:geopacking` for geometrical packing constraints.

   With Boolean relations using reified integer relations, the constraint that the squares :math:`s_1` and :math:`s_2` do not overlap can be posted as follows:

.. mpg-code:: snippet:m-minimodel:fig:m:minimodel:bool:code:4
   :direct:


Like the post functions for integer and Boolean variables presented above, posting Boolean expressions and relations supports an optional argument of type ``IntPropLevel`` to select the propagation level. For more information, see :ref:`sec:m:integer:generic`.

Boolean expressions also include reified set relations, which will be covered below.

.. mpg-tip:: Reification of non-functional constraints

   Reification of integer or set relations is mostly implemented through *decomposition*. For example, given integer variables ``x``, ``y``, and ``z``, the reified division constraint


   .. mpg-code:: snippet:m-minimodel:fig:m:minimodel:bool:code:5
      :direct:

   is actually equivalent to

   .. mpg-code:: snippet:m-minimodel:fig:m:minimodel:bool:code:6
      :direct:

   Some constraints, such as division above, are not simple functions but impose side constraints. In the case of the division above, the side constraint is that ``y`` is not zero. It is important to understand the subtle semantics of decomposed reification here: If ``y`` happens to be zero, we get failure instead of ``b`` being constrained to false!

   There are several expressions that have non-functional semantics: division, modulo, element, and disjoint set union (introduced below).

For more examples using Boolean expressions and Boolean relations including reification, see :ref:`chap:c:photo`.

.. _modeling:m-minimodel:set-expressions-and-relations:

Set expressions and relations
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. mpg-figure:: Set expressions and relations
   :name: fig:m:minimodel:set

   .. container:: center

      +----------------------------------------+-------------+---------------------------------------------------------------------------------------------------------------+----------------------------------------+
      | :math:`\langle\mathit{SetExpr}\rangle` | :math:`::=` | :math:`\langle y\rangle`                                                                                      | set variable                           |
      +----------------------------------------+-------------+---------------------------------------------------------------------------------------------------------------+----------------------------------------+
      |                                        | :math:`|`   | :math:`\langle s\rangle`                                                                                      | set constant (``IntSet``)              |
      +----------------------------------------+-------------+---------------------------------------------------------------------------------------------------------------+----------------------------------------+
      |                                        | :math:`|`   | :math:`\operatorname{\texttt{-}}\langle\mathit{SetExpr}\rangle`                                               | complement                             |
      +----------------------------------------+-------------+---------------------------------------------------------------------------------------------------------------+----------------------------------------+
      |                                        | :math:`|`   | :math:`\langle\mathit{SetExpr}\rangle\mathbin{\texttt{\&}} \langle\mathit{SetExpr}\rangle`                    | intersection                           |
      +----------------------------------------+-------------+---------------------------------------------------------------------------------------------------------------+----------------------------------------+
      |                                        | :math:`|`   | :math:`\langle\mathit{SetExpr}\rangle\mathbin{\texttt{|}} \langle\mathit{SetExpr}\rangle`                     | union                                  |
      +----------------------------------------+-------------+---------------------------------------------------------------------------------------------------------------+----------------------------------------+
      |                                        | :math:`|`   | :math:`\langle\mathit{SetExpr}\rangle\mathbin{\texttt{+}} \langle\mathit{SetExpr}\rangle`                     | disjoint union                         |
      +----------------------------------------+-------------+---------------------------------------------------------------------------------------------------------------+----------------------------------------+
      |                                        | :math:`|`   | :math:`\langle\mathit{SetExpr}\rangle\mathbin{\texttt{-}} \langle\mathit{SetExpr}\rangle`                     | set difference                         |
      +----------------------------------------+-------------+---------------------------------------------------------------------------------------------------------------+----------------------------------------+
      |                                        | :math:`|`   | :math:`\operatorname{\texttt{inter}}(\langle\overline y\rangle)`                                              | intersection of variables              |
      +----------------------------------------+-------------+---------------------------------------------------------------------------------------------------------------+----------------------------------------+
      |                                        | :math:`|`   | :math:`\operatorname{\texttt{setunion}}(\langle\overline y\rangle)`                                           | union of variables                     |
      +----------------------------------------+-------------+---------------------------------------------------------------------------------------------------------------+----------------------------------------+
      |                                        | :math:`|`   | :math:`\operatorname{\texttt{setdunion}}(\langle\overline y\rangle)`                                          | disjoint union of variables            |
      +----------------------------------------+-------------+---------------------------------------------------------------------------------------------------------------+----------------------------------------+
      |                                        | :math:`|`   | :math:`\operatorname{\texttt{singleton}}(\langle\mathit{IntExpr}\rangle)`                                     | singleton given by integer expression  |
      +----------------------------------------+-------------+---------------------------------------------------------------------------------------------------------------+----------------------------------------+
      |                                        |             |                                                                                                               |                                        |
      +----------------------------------------+-------------+---------------------------------------------------------------------------------------------------------------+----------------------------------------+
      | :math:`\langle\mathit{SetRel}\rangle`  | :math:`::=` | :math:`\langle\mathit{SetExpr}\rangle\mathbin{\texttt{==}} \langle\mathit{SetExpr}\rangle`                    | expressions are equal                  |
      +----------------------------------------+-------------+---------------------------------------------------------------------------------------------------------------+----------------------------------------+
      |                                        | :math:`|`   | :math:`\langle\mathit{SetExpr}\rangle\mathbin{\texttt{!=}} \langle\mathit{SetExpr}\rangle`                    | expressions are not equal              |
      +----------------------------------------+-------------+---------------------------------------------------------------------------------------------------------------+----------------------------------------+
      |                                        | :math:`|`   | :math:`\langle\mathit{SetExpr}\rangle\mathbin{\texttt{<=}} \langle\mathit{SetExpr}\rangle`                    | first is subset of second expression   |
      +----------------------------------------+-------------+---------------------------------------------------------------------------------------------------------------+----------------------------------------+
      |                                        | :math:`|`   | :math:`\langle\mathit{SetExpr}\rangle\mathbin{\texttt{>=}} \langle\mathit{SetExpr}\rangle`                    | first is superset of second expression |
      +----------------------------------------+-------------+---------------------------------------------------------------------------------------------------------------+----------------------------------------+
      |                                        | :math:`|`   | :math:`\langle\mathit{SetExpr}\rangle\mathbin{\texttt{||}} \langle\mathit{SetExpr}\rangle`                    | expressions are disjoint               |
      +----------------------------------------+-------------+---------------------------------------------------------------------------------------------------------------+----------------------------------------+
      |                                        | :math:`|`   | :math:`\langle\mathit{SetExpr}\rangle\mathrel{\langle r\rangle} \langle\mathit{IntExpr}\rangle`               | set-integer relation                   |
      +----------------------------------------+-------------+---------------------------------------------------------------------------------------------------------------+----------------------------------------+
      |                                        | :math:`|`   | :math:`\langle\mathit{IntExpr}\rangle\mathrel{\langle r\rangle} \langle\mathit{SetExpr}\rangle`               | integer-set relation                   |
      +----------------------------------------+-------------+---------------------------------------------------------------------------------------------------------------+----------------------------------------+
      |                                        | :math:`|`   | :math:`\operatorname{\texttt{dom}}(\langle y\rangle,\langle r_s\rangle,\langle n\rangle)`                     | domain relation                        |
      +----------------------------------------+-------------+---------------------------------------------------------------------------------------------------------------+----------------------------------------+
      |                                        | :math:`|`   | :math:`\operatorname{\texttt{dom}}(\langle y\rangle,\langle r_s\rangle,\langle n\rangle,\langle n\rangle)`    | domain relation                        |
      +----------------------------------------+-------------+---------------------------------------------------------------------------------------------------------------+----------------------------------------+
      |                                        | :math:`|`   | :math:`\operatorname{\texttt{dom}}(\langle y\rangle,\langle r_s\rangle,\langle s\rangle)`                     | domain relation                        |
      +----------------------------------------+-------------+---------------------------------------------------------------------------------------------------------------+----------------------------------------+
      |                                        |             |                                                                                                               |                                        |
      +----------------------------------------+-------------+---------------------------------------------------------------------------------------------------------------+----------------------------------------+
      | :math:`\langle n\rangle`               | :math:`::=` | integer value                                                                                                 |                                        |
      +----------------------------------------+-------------+---------------------------------------------------------------------------------------------------------------+----------------------------------------+
      | :math:`\langle\overline y\rangle`      | :math:`::=` | array of set variables                                                                                        |                                        |
      +----------------------------------------+-------------+---------------------------------------------------------------------------------------------------------------+----------------------------------------+
      | :math:`\langle r\rangle`               | :math:`::=` | ``==`` :math:`\;|\;` ``!=`` :math:`\;|\;` ``<`` :math:`\;|\;` ``<=`` :math:`\;|\;` ``>`` :math:`\;|\;` ``>=`` | integer relation symbol                |
      +----------------------------------------+-------------+---------------------------------------------------------------------------------------------------------------+----------------------------------------+
      | :math:`\langle r_s\rangle`             | :math:`::=` | ``==`` :math:`\;|\;` ``!=`` :math:`\;|\;` ``<=`` :math:`\;|\;` ``>=`` :math:`\;|\;` ``||``                    | set relation symbol                    |
      +----------------------------------------+-------------+---------------------------------------------------------------------------------------------------------------+----------------------------------------+

`Set expressions and relations <https://www.gecode.dev/doc/6.4.0/reference/group__TaskModelMiniModelSet.html>`__ are constructed using the standard C++ operators and the functions listed in :numref:`fig:m:minimodel:set`. Just like for integer and Boolean expressions, posting of a set expression returns a new set variable that is constrained to the value of the expression.

For example, the set expression ``x & (y | z)`` (to be read as :math:`\mathtt{x}\cap(\mathtt{y}\cup\mathtt{z})`) for set variables ``x``, ``y``, and ``z`` is posted by

.. mpg-code:: snippet:m-minimodel:fig:m:minimodel:set:code:1
   :direct:


Posting a set relation posts the corresponding constraint. Given an existing set variable ``s``, the previous code fragment could therefore be written as

.. mpg-code:: snippet:m-minimodel:fig:m:minimodel:set:code:2
   :direct:


As noted above, set relations can be reified, turning them into Boolean expressions. The following code posts the constraint that ``b`` is true if and only if ``x`` is the complement of ``y``:

.. mpg-code:: snippet:m-minimodel:fig:m:minimodel:set:code:3
   :direct:


.. container:: samepage

   Instead of a set variable, you can always use a constant ``IntSet``, for example for reifying the fact that ``x`` is empty:

   .. mpg-code:: snippet:m-minimodel:fig:m:minimodel:set:code:4
      :direct:

   The subset relations can also be posted two-sided, such as

   .. mpg-code:: snippet:m-minimodel:fig:m:minimodel:set:code:5
      :direct:

.. _sec:m:minimodel:float:


.. _modeling:m-minimodel:float-expressions-and-relations:

Float expressions and relations
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. mpg-figure:: Float expressions
   :name: fig:m:minimodel:float:expr

   .. container:: center

      +------------------------------------------+-------------+--------------------------------------------------------------------------------------------------------+--------------------------------+
      | :math:`\langle\mathit{FloatExpr}\rangle` | :math:`::=` | :math:`\langle z\rangle`                                                                               | float variable                 |
      +------------------------------------------+-------------+--------------------------------------------------------------------------------------------------------+--------------------------------+
      |                                          | :math:`|`   | :math:`\langle f\rangle`                                                                               | float value                    |
      +------------------------------------------+-------------+--------------------------------------------------------------------------------------------------------+--------------------------------+
      |                                          | :math:`|`   | :math:`\operatorname{\texttt{-}}\langle\mathit{FloatExpr}\rangle`                                      | unary minus                    |
      +------------------------------------------+-------------+--------------------------------------------------------------------------------------------------------+--------------------------------+
      |                                          | :math:`|`   | :math:`\langle\mathit{FloatExpr}\rangle\mathbin{\texttt{+}} \langle\mathit{FloatExpr}\rangle`          | addition                       |
      +------------------------------------------+-------------+--------------------------------------------------------------------------------------------------------+--------------------------------+
      |                                          | :math:`|`   | :math:`\langle\mathit{FloatExpr}\rangle\mathbin{\texttt{-}} \langle\mathit{FloatExpr}\rangle`          | subtraction                    |
      +------------------------------------------+-------------+--------------------------------------------------------------------------------------------------------+--------------------------------+
      |                                          | :math:`|`   | :math:`\langle\mathit{FloatExpr}\rangle\mathbin{\texttt{*}} \langle\mathit{FloatExpr}\rangle`          | multiplication                 |
      +------------------------------------------+-------------+--------------------------------------------------------------------------------------------------------+--------------------------------+
      |                                          | :math:`|`   | :math:`\langle\mathit{FloatExpr}\rangle\mathbin{\texttt{/}} \langle\mathit{FloatExpr}\rangle`          | division                       |
      +------------------------------------------+-------------+--------------------------------------------------------------------------------------------------------+--------------------------------+
      |                                          | :math:`|`   | :math:`\texttt{sum(}\langle\overline z\rangle\texttt{)}`                                               | sum of float variables         |
      +------------------------------------------+-------------+--------------------------------------------------------------------------------------------------------+--------------------------------+
      |                                          | :math:`|`   | :math:`\texttt{sum(}\langle\overline f\rangle\texttt{,}\langle\overline z\rangle\texttt{)}`            | sum of float with coefficients |
      +------------------------------------------+-------------+--------------------------------------------------------------------------------------------------------+--------------------------------+
      |                                          | :math:`|`   | :math:`\operatorname{\texttt{min}}(\langle\mathit{FloatExpr}\rangle,\langle\mathit{FloatExpr}\rangle)` | minimum                        |
      +------------------------------------------+-------------+--------------------------------------------------------------------------------------------------------+--------------------------------+
      |                                          | :math:`|`   | :math:`\operatorname{\texttt{min}}(\langle\overline z\rangle)`                                         | minimum of float variables     |
      +------------------------------------------+-------------+--------------------------------------------------------------------------------------------------------+--------------------------------+
      |                                          | :math:`|`   | :math:`\operatorname{\texttt{max}}(\langle\mathit{FloatExpr}\rangle,\langle\mathit{FloatExpr}\rangle)` | maximum                        |
      +------------------------------------------+-------------+--------------------------------------------------------------------------------------------------------+--------------------------------+
      |                                          | :math:`|`   | :math:`\operatorname{\texttt{max}}(\langle\overline z\rangle)`                                         | maximum of float variables     |
      +------------------------------------------+-------------+--------------------------------------------------------------------------------------------------------+--------------------------------+
      |                                          | :math:`|`   | :math:`\operatorname{\texttt{abs}}(\langle\mathit{FloatExpr}\rangle)`                                  | absolute value                 |
      +------------------------------------------+-------------+--------------------------------------------------------------------------------------------------------+--------------------------------+
      |                                          | :math:`|`   | :math:`\operatorname{\texttt{sqr}}(\langle\mathit{FloatExpr}\rangle)`                                  | square                         |
      +------------------------------------------+-------------+--------------------------------------------------------------------------------------------------------+--------------------------------+
      |                                          | :math:`|`   | :math:`\operatorname{\texttt{sqrt}}(\langle\mathit{FloatExpr}\rangle)`                                 | square root                    |
      +------------------------------------------+-------------+--------------------------------------------------------------------------------------------------------+--------------------------------+
      |                                          | :math:`|`   | :math:`\operatorname{\texttt{pow}}(\langle\mathit{FloatExpr}\rangle,\langle n\rangle)`                 | power                          |
      +------------------------------------------+-------------+--------------------------------------------------------------------------------------------------------+--------------------------------+
      |                                          | :math:`|`   | :math:`\operatorname{\texttt{nroot}}(\langle\mathit{FloatExpr}\rangle,\langle n\rangle)`               | :math:`n`-th root              |
      +------------------------------------------+-------------+--------------------------------------------------------------------------------------------------------+--------------------------------+
      |                                          | :math:`|`   | :math:`\operatorname{\texttt{exp}}(\langle\mathit{FloatExpr}\rangle)`                                  | exponentialMPFR                |
      +------------------------------------------+-------------+--------------------------------------------------------------------------------------------------------+--------------------------------+
      |                                          | :math:`|`   | :math:`\operatorname{\texttt{log}}(\langle\mathit{FloatExpr}\rangle)`                                  | logarithmMPFR                  |
      +------------------------------------------+-------------+--------------------------------------------------------------------------------------------------------+--------------------------------+
      |                                          | :math:`|`   | :math:`\operatorname{\texttt{sin}}(\langle\mathit{FloatExpr}\rangle)`                                  | sineMPFR                       |
      +------------------------------------------+-------------+--------------------------------------------------------------------------------------------------------+--------------------------------+
      |                                          | :math:`|`   | :math:`\operatorname{\texttt{cos}}(\langle\mathit{FloatExpr}\rangle)`                                  | cosineMPFR                     |
      +------------------------------------------+-------------+--------------------------------------------------------------------------------------------------------+--------------------------------+
      |                                          | :math:`|`   | :math:`\operatorname{\texttt{tan}}(\langle\mathit{FloatExpr}\rangle)`                                  | tangentMPFR                    |
      +------------------------------------------+-------------+--------------------------------------------------------------------------------------------------------+--------------------------------+
      |                                          | :math:`|`   | :math:`\operatorname{\texttt{asin}}(\langle\mathit{FloatExpr}\rangle)`                                 | arcsineMPFR                    |
      +------------------------------------------+-------------+--------------------------------------------------------------------------------------------------------+--------------------------------+
      |                                          | :math:`|`   | :math:`\operatorname{\texttt{acos}}(\langle\mathit{FloatExpr}\rangle)`                                 | arccosineMPFR                  |
      +------------------------------------------+-------------+--------------------------------------------------------------------------------------------------------+--------------------------------+
      |                                          | :math:`|`   | :math:`\operatorname{\texttt{atan}}(\langle\mathit{FloatExpr}\rangle)`                                 | arctangentMPFR                 |
      +------------------------------------------+-------------+--------------------------------------------------------------------------------------------------------+--------------------------------+
      |                                          |             |                                                                                                        |                                |
      +------------------------------------------+-------------+--------------------------------------------------------------------------------------------------------+--------------------------------+
      | :math:`\langle\overline z\rangle`        | :math:`::=` | array of float variables                                                                               |                                |
      +------------------------------------------+-------------+--------------------------------------------------------------------------------------------------------+--------------------------------+
      | :math:`\langle\overline f\rangle`        | :math:`::=` | array of float values                                                                                  |                                |
      +------------------------------------------+-------------+--------------------------------------------------------------------------------------------------------+--------------------------------+

`Linear float expressions and relations <https://www.gecode.dev/doc/6.4.0/reference/group__TaskModelMiniModelFloat.html>`__ are constructed using the standard C++ operators and the functions listed in :numref:`fig:m:minimodel:float:expr` and :numref:`fig:m:minimodel:float:rel` (see also `Arithmetic functions <https://www.gecode.dev/doc/6.4.0/reference/group__TaskModelMiniModelArith.html>`__, `Transcendental functions <https://www.gecode.dev/doc/6.4.0/reference/group__TaskModelMiniModelTrans.html>`__, and `Trigonometric functions <https://www.gecode.dev/doc/6.4.0/reference/group__TaskModelMiniModelTrigo.html>`__). Posting a float expression returns a new float variable that is constrained to the value of the expression.

.. mpg-figure:: Float relations
   :name: fig:m:minimodel:float:rel

   .. container:: center

      +-----------------------------------------+-------------+---------------------------------------------------------------------------------------------------------------+-----------------------+
      | :math:`\langle\mathit{FloatRel}\rangle` | :math:`::=` | :math:`\langle\mathit{FloatExpr}\rangle\mathrel{\langle r\rangle} \langle\mathit{FloatExpr}\rangle`           | float relation        |
      +-----------------------------------------+-------------+---------------------------------------------------------------------------------------------------------------+-----------------------+
      |                                         | :math:`|`   | :math:`\operatorname{\texttt{dom}}(\langle z\rangle,\langle f\rangle)`                                        | domain relation       |
      +-----------------------------------------+-------------+---------------------------------------------------------------------------------------------------------------+-----------------------+
      |                                         | :math:`|`   | :math:`\operatorname{\texttt{dom}}(\langle z\rangle,\langle m\rangle,\langle m\rangle)`                       | domain relation       |
      +-----------------------------------------+-------------+---------------------------------------------------------------------------------------------------------------+-----------------------+
      |                                         |             |                                                                                                               |                       |
      +-----------------------------------------+-------------+---------------------------------------------------------------------------------------------------------------+-----------------------+
      | :math:`\langle r\rangle`                | :math:`::=` | ``==`` :math:`\;|\;` ``!=`` :math:`\;|\;` ``<`` :math:`\;|\;` ``<=`` :math:`\;|\;` ``>`` :math:`\;|\;` ``>=`` | float relation symbol |
      +-----------------------------------------+-------------+---------------------------------------------------------------------------------------------------------------+-----------------------+
      | :math:`\langle f\rangle`                | :math:`::=` | float value                                                                                                   |                       |
      +-----------------------------------------+-------------+---------------------------------------------------------------------------------------------------------------+-----------------------+
      | :math:`\langle m\rangle`                | :math:`::=` | float number                                                                                                  |                       |
      +-----------------------------------------+-------------+---------------------------------------------------------------------------------------------------------------+-----------------------+
      | :math:`\langle z\rangle`                | :math:`::=` | float variable                                                                                                |                       |
      +-----------------------------------------+-------------+---------------------------------------------------------------------------------------------------------------+-----------------------+

Instead of a float variable, you can always use a constant of type `FloatVal <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1FloatVal.html>`__.

.. _sec:m:minimodel:boolmisc:


.. _modeling:m-minimodel:extending-boolean-expressions-and-relations:

Extending Boolean expressions and relations
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Boolean expressions and relations can easily be extended. A typical case for extension is when a new variable type is added (see also :ref:`part:v`) and that there are also reified constraints using the new variable type that should be included in Boolean expressions and relations.

As an example, we assume that we would like to extend Boolean expressions and relations by a domain expression ``dom()`` (as a more convenient form of domain constraints as described in :ref:`sec:m:integer:dom`), so for example

.. mpg-code:: snippet:m-minimodel:sec:m:minimodel:boolmisc:code:1
   :direct:


constrains the domain of ``x`` to :math:`\{1,2,3,4,5\}` whereas

.. mpg-code:: snippet:m-minimodel:sec:m:minimodel:boolmisc:code:2
   :direct:


constrains the domain of ``x`` to :math:`\{-10,-9,\ldots,0,6,7,\ldots,10\}`. The domain expression can be used together with other Boolean expressions. For example, if both ``x`` and ``y`` are integer variables, then the following is possible:

.. mpg-code:: snippet:m-minimodel:sec:m:minimodel:boolmisc:code:3
   :direct:


.. mpg-code:: Boolean domain expression
   :name: fig:m:minimodel:domexpr
   :caption: The class ``BoolDomExpr`` and the ``dom()`` function


In order to extend Boolean expressions one must implement the following:

- A function ``dom(IntVar x, int l, int u)`` that creates a Boolean expression where ``x`` is the variable and ``l`` and ``u`` are the lower and upper bound for the domain.

- A class ``BoolDomExpr`` that inherits from the class `BoolExpr::Misc <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1BoolExpr_1_1Misc.html>`__. An object of the class is created by our ``dom()`` function and the modeling layer uses a virtual member function ``post()`` to post a constraint when the ``rel()`` or ``expr()`` functions require this.

.. _modeling:m-minimodel:the-dom-function:

.. mpg-paragraph:: The ``dom()`` function.

The definition of the ``dom()`` function is straightforward and as follows:

.. mpg-code:: Boolean domain expression:create Boolean domain expression


It returns a new Boolean expression that contains an object of class ``BoolDomExpr`` that can be used by the ``rel()`` and ``expr()`` functions.

.. _modeling:m-minimodel:the-boolean-domain-expression-class:

.. mpg-paragraph:: The Boolean domain expression class.

The class is shown in :numref:`fig:m:minimodel:domexpr`. An object of class ``BoolDomExpr`` stores the information needed for the actual post function: the variable ``x`` and lower and upper bounds ``l`` and ``u``. Note that our class does not need a destructor, it is only shown as a reminder for classes that actually need a destructor!

The ``post()`` member function is defined as follows:

.. mpg-code:: Boolean domain expression:post member function


where the posted expression must constrain the Boolean variable ``b`` with integer propagation level ``ipl``. If ``neg`` is ``true``, a negated constraint must be posted.

.. _sec:m:minimodel:matrix:


.. _modeling:m-minimodel:matrix-interface-for-arrays:

Matrix interface for arrays
---------------------------

MiniModel provides a `Matrix <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1Matrix.html>`__ support class for accessing an array as a two dimensional matrix. The following

.. mpg-code:: snippet:m-minimodel:sec:m:minimodel:matrix:code:1
   :direct:


declares an array of integer variables ``x`` and superimposes a matrix interface to ``x`` called ``mat`` with width ``n`` and height ``m``. Note that the first argument specifies the number of columns, and the second argument specifies the number of rows.

.. container:: samepage

   The elements of the array can now be accessed at positions :math:`\langle i,j\rangle` in the matrix ``mat`` (that is, the element in column :math:`i` and row :math:`j`) using

   .. mpg-code:: snippet:m-minimodel:sec:m:minimodel:matrix:code:2
      :direct:

Furthermore, the rows and columns of the matrix can be accessed using ``mat.row(i)`` and ``mat.col(j)``. If a rectangular slice is required, the ``slice()`` member function can be used.

A matrix interface can be declared for any standard array or argument array used in Gecode, such as ``IntVarArray`` or ``IntSetArgs``.

As an example of how the ``Matrix`` class can be used, consider the Sudoku problem (see `Solving Sudoku puzzles using integer constraints <https://www.gecode.dev/doc/6.4.0/reference/examples_2sudoku_8cpp.html>`__). Given that there is a member ``IntVarArray x`` that contains :math:`9\cdot 9` integer variables with domain :math:`\{1,\ldots,9\}`, the following code posts constraints that implement the basic rules for a Sudoku.

.. mpg-code:: snippet:m-minimodel:sec:m:minimodel:matrix:code:3
   :direct:


For more examples that use the ``Matrix`` class, see :ref:`chap:c:crossword`, :ref:`chap:c:golf`, :ref:`chap:c:kakuro`, :ref:`chap:c:nonogram`, `Magic squares <https://www.gecode.dev/doc/6.4.0/reference/magic-square_8cpp.html>`__, and `Nonogram <https://www.gecode.dev/doc/6.4.0/reference/nonogram_8cpp.html>`__.

.. _par:m:minimodel:matrix:element:


.. _modeling:m-minimodel:element-constraints:

.. mpg-paragraph:: Element constraints.

A matrix can also be used with an element constraint that propagates information about the row and column of matrix entries.

.. container:: samepage

   For example, the following code assumes that ``x`` is an integer array of type ``IntArgs`` with ``12`` elements.

   .. mpg-code:: snippet:m-minimodel:par:m:minimodel:matrix:element:code:1
      :direct:

   constrains the variable ``v`` to the value at position :math:`\langle \mathtt{r},\mathtt{c}\rangle` of the matrix ``m`` (see also GCCat: `element_matrix <http://www.emn.fr/z-info/sdemasse/gccat/Celement_matrix.html>`__).

..

.. mpg-tip:: Element for matrix can compromise propagation



   Whenever it is possible one should use an array rather than a matrix for posting ``element`` constraints, as an ``element`` constraint for a matrix will provide rather weak propagation for the row and column variables.

   Consider the following array of integers ``x`` together with its matrix interface ``m``

   .. mpg-code:: snippet:m-minimodel:par:m:minimodel:matrix:element:code:2
      :direct:

   That is, ``m`` represents the matrix

   .. math::

      \left(
      \begin{array}{cc}0&2\\2&1\\\end{array}
      \right)

   Consider the following example using an ``element`` constraint on an integer array:

   .. mpg-code:: snippet:m-minimodel:par:m:minimodel:matrix:element:code:3
      :direct:

   After performing propagation, ``i`` will be constrained to the set :math:`\{0,3\}` (as :math:`2` is not included in the values of ``v``).

   Compare this to propagating an ``element`` constraint over the corresponding matrix as follows:

   .. mpg-code:: snippet:m-minimodel:par:m:minimodel:matrix:element:code:4
      :direct:

   Propagation of ``element`` will determine that only the fields :math:`\langle 0,0\rangle` and :math:`\langle 1,1\rangle` are still possible. But propagating this information to the row and column variables, yields the values :math:`\{0,1\}` for both ``r`` and ``c``: each value for the coordinates is still possible even though some of their combinations are not.

.. _sec:m:minimodel:optimize:


.. _modeling:m-minimodel:support-for-cost-based-optimization:

Support for cost-based optimization
-----------------------------------

`Support for cost-based optimization <https://www.gecode.dev/doc/6.4.0/reference/group__TaskModelMiniModelOptimize.html>`__ provides several subclasses of `Space <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1Space.html>`__ for cost-based optimization. `IntMinimizeSpace <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1IntMinimizeSpace.html>`__ and `IntMaximizeSpace <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1IntMaximizeSpace.html>`__ support search for a solution of minimal and maximal, respectively, integer cost. `FloatMinimizeSpace <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1FloatMinimizeSpace.html>`__ and `FloatMaximizeSpace <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1FloatMaximizeSpace.html>`__ support search for a solution of minimal and maximal, respectively, float cost, possibly with an improvement step (see below). `IntLexMinimizeSpace <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1IntLexMinimizeSpace.html>`__ and `IntLexMaximizeSpace <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1IntLexMaximizeSpace.html>`__ support search for the lexicographically smallest and largest solution where the cost is defined as an array of integer variables.

.. _modeling:m-minimodel:optimizing-integer-cost:

.. mpg-paragraph:: Optimizing integer cost.

The classes `IntMinimizeSpace <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1IntMinimizeSpace.html>`__ and `IntMaximizeSpace <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1IntMaximizeSpace.html>`__ support searching a solution of minimal and maximal, respectively, integer cost.

.. container:: samepage

   In order to use these abstract classes, a class inheriting from `IntMinimizeSpace <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1IntMinimizeSpace.html>`__ and `IntMaximizeSpace <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1IntMaximizeSpace.html>`__ must implement a virtual cost function of type

   .. mpg-code:: snippet:m-minimodel:sec:m:minimodel:optimize:code:1
      :direct:

The function must return an integer variable for the cost. For an example, see :ref:`sec:m:comfy:cost`.

.. mpg-tip:: Cost must be assigned for solutions

   In case the ``cost()`` function is called on a *solution*, the variable returned by ``cost()`` *must* be assigned. If the variable is unassigned for a solution, an exception of type `Int::ValOfUnassignedVar <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1Int_1_1ValOfUnassignedVar.html>`__ is thrown.


.. _sec:m:minimodel:optimize:float:


.. _modeling:m-minimodel:optimizing-float-cost-with-improvement-step:

.. mpg-paragraph:: Optimizing float cost with improvement step.

The classes `FloatMinimizeSpace <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1FloatMinimizeSpace.html>`__ and `FloatMaximizeSpace <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1FloatMaximizeSpace.html>`__ support searching a solution of minimal and maximal, respectively, float cost.

Note that the constructor of these classes take an optional argument of type ``FloatNum`` that defines the improvement step: a better solution is found only if it is better than the previous solution and the improvement step. For example, suppose

.. mpg-code:: snippet:m-minimodel:sec:m:minimodel:optimize:float:code:1
   :direct:


that searching for a best solution of ``WithStep`` finds a solution ``s`` with cost value ``c=s.cost().val()``. Then, the next solution must have a cost that is strictly smaller than :math:`\mathtt{c}-\mathtt{s}`. For `FloatMaximizeSpace <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1FloatMaximizeSpace.html>`__, the next solution must have a cost that is strictly larger than :math:`\mathtt{c}+\mathtt{s}`.

.. _modeling:m-minimodel:lexicographically-optimizing-for-integer-costs:

.. mpg-paragraph:: Lexicographically optimizing for integer costs.

The classes `IntLexMinimizeSpace <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1IntLexMinimizeSpace.html>`__ and `IntLexMaximizeSpace <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1IntLexMaximizeSpace.html>`__ support searching for a solution with lexicographically smallest and largest cost. The cost is defined by an array of integer variables.

In order to use these abstract classes, a class inheriting from `IntLexMinimizeSpace <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1IntLexMinimizeSpace.html>`__ and `IntLexMaximizeSpace <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1IntLexMaximizeSpace.html>`__ must implement a virtual cost function of type

.. mpg-code:: snippet:m-minimodel:sec:m:minimodel:optimize:float:code:2
   :direct:


The function must return an array of integer variable as cost. For an example, see `Locating warehouses <https://www.gecode.dev/doc/6.4.0/reference/examples_2warehouses_8cpp.html>`__.

.. _sec:m:minimodel:reg:


.. _modeling:m-minimodel:regular-expressions-for-extensional-constraints:

Regular expressions for extensional constraints
-----------------------------------------------

.. mpg-figure:: Constructing regular expressions (``r`` and ``s`` are regular expressions, ``n`` and ``m`` are unsigned integers)
   :name: fig:m:minimodel:reg
   :short-caption: Constructing regular expressions

   .. container:: center

      +-----------------------------+---------------------------------------------------------------------------------------+
      | operation                   | meaning                                                                               |
      +=============================+=======================================================================================+
      | ``REG r``                   | initialize ``r`` as :math:`\epsilon` (empty)                                          |
      +-----------------------------+---------------------------------------------------------------------------------------+
      | ``REG r(4)``                | initialize ``r`` as single integer (symbol) ``4``                                     |
      +-----------------------------+---------------------------------------------------------------------------------------+
      | ``REG r(IntArgs({0,2,4}))`` | initialize ``r`` as alternative of integers :math:`\mathtt 0 | \mathtt 2 | \mathtt 4` |
      +-----------------------------+---------------------------------------------------------------------------------------+
      | ``r + s``                   | ``r`` followed by ``s``                                                               |
      +-----------------------------+---------------------------------------------------------------------------------------+
      | ``r | s``                   | ``r`` or ``s``                                                                        |
      +-----------------------------+---------------------------------------------------------------------------------------+
      | ``r += s``                  | efficient shortcut for ``r = r + s``                                                  |
      +-----------------------------+---------------------------------------------------------------------------------------+
      | ``r |= s``                  | efficient shortcut for ``r = r | s``                                                  |
      +-----------------------------+---------------------------------------------------------------------------------------+
      | ``*r``                      | repeat ``r`` arbitrarily often (Kleene star)                                          |
      +-----------------------------+---------------------------------------------------------------------------------------+
      | ``+r``                      | repeat ``r`` at least once                                                            |
      +-----------------------------+---------------------------------------------------------------------------------------+
      | ``r(n)``                    | repeat ``r`` at least ``n`` times                                                     |
      +-----------------------------+---------------------------------------------------------------------------------------+
      | ``r(n,m)``                  | repeat ``r`` at least ``n`` times, at most ``m`` times                                |
      +-----------------------------+---------------------------------------------------------------------------------------+

Regular expressions are implemented as instances of the class `REG <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1REG.html>`__ and provide an alternative, typically more convenient, interface for the specification of extensional constraints than DFAs do. The construction of regular expressions is summarized in :numref:`fig:m:minimodel:reg`.

.. container:: samepage

   Let us reconsider the Swedish drinking protocol from :ref:`sec:m:integer:extensional`. The protocol can be described by a regular expression ``r`` constructed by

   .. mpg-code:: snippet:m-minimodel:fig:m:minimodel:reg:code:1
      :direct:

   A sequence of activities ``x`` (an integer or Boolean variable array) can be constrained by

   .. mpg-code:: snippet:m-minimodel:fig:m:minimodel:reg:code:2
      :direct:

   after a DFA for the regular expression has been computed.

..

.. mpg-tip:: Creating a DFA only once

   Please make it a habit to create a DFA explicitly from a regular expression ``r`` rather than implicitly by


   .. mpg-code:: snippet:m-minimodel:fig:m:minimodel:reg:code:3
      :direct:

   Both variants work, however the implicit variant disguises the fact that each time the code fragment is executed, a new DFA for the regular expression ``r`` is computed (think about the code fragment being executed inside a loop and your C++ compiler being not too smart about it)! [2]_

For examples on using regular expressions for extensional constraints, see the nonogram case study in :ref:`chap:c:nonogram` or the examples `Solitaire domino <https://www.gecode.dev/doc/6.4.0/reference/domino_8cpp.html>`__, `Nonogram <https://www.gecode.dev/doc/6.4.0/reference/nonogram_8cpp.html>`__, and `Pentominoes <https://www.gecode.dev/doc/6.4.0/reference/pentominoes_8cpp.html>`__. The models are based on ideas described in :cite:`LagerkvistPesant:BPPC:2008`, where regular expressions for extensional constraints nicely demonstrate their usefulness.

.. _sec:m:minimodel:channel:


.. _modeling:m-minimodel:channeling-functions:

Channeling functions
--------------------

`Channel functions <https://www.gecode.dev/doc/6.4.0/reference/group__TaskModelMiniModelChannel.html>`__ are functions to channel a Boolean variable to an integer variable and vice versa, to channel a float variable to an integer variable, and to channel between integer variables and a set variable.

For an integer variable ``x``,

.. mpg-code:: snippet:m-minimodel:sec:m:minimodel:channel:code:1
   :direct:


returns a new Boolean variable that is equal to ``x``. Likewise, for a Boolean variable ``x`` an equal integer variable is returned.

For a float variable ``x``, ``channel(home, x)`` returns an integer variable equal to ``x``.

For an array of integer variables ``x``, ``channel(home, x)`` returns a set variable equal to all the integers in ``x``.

.. _sec:m:minimodel:intalias:


.. _modeling:m-minimodel:aliases-for-integer-constraints:

Aliases for integer constraints
-------------------------------

.. mpg-figure:: Aliases for integer constraints (``x`` and ``y`` are integer variable arrays, ``u`` and ``v`` are integers or integer variables, ``r`` is an integer relation type, ``s`` is an integer set)
   :name: fig:m:minimodel:alias
   :short-caption: Aliases for integer constraints

   .. container:: center

      +-----------------------------+-----------------------------------------+-------------------------------------------------------------------------+
      | alias                       | constraint posted                       | GCCat                                                                   |
      +=============================+=========================================+=========================================================================+
      | ``atmost(home, x, u, v);``  | ``count(home, x, u, IRT_LQ, v);``       | `atmost <http://www.emn.fr/z-info/sdemasse/gccat/Catmost.html>`__       |
      +-----------------------------+-----------------------------------------+-------------------------------------------------------------------------+
      | ``atleast(home, x, u, v);`` | ``count(home, x, u, IRT_GQ, v);``       | `atleast <http://www.emn.fr/z-info/sdemasse/gccat/Catleast.html>`__     |
      +-----------------------------+-----------------------------------------+-------------------------------------------------------------------------+
      | ``exactly(home, x, u, v);`` | ``count(home, x, u, IRT_EQ, v);``       | `exactly <http://www.emn.fr/z-info/sdemasse/gccat/Cexactly.html>`__     |
      +-----------------------------+-----------------------------------------+-------------------------------------------------------------------------+
      | ``lex(home, x, r, y);``     | ``rel(home, x, r, y);``                 | `lex <http://www.emn.fr/z-info/sdemasse/gccat/Clex.html>`__             |
      +-----------------------------+-----------------------------------------+-------------------------------------------------------------------------+
      | ``values(home, x, s);``     | ``dom(home, x, s);``                    |                                                                         |
      +-----------------------------+-----------------------------------------+-------------------------------------------------------------------------+
      |                             | ``nvalues(home, x, IRT_EQ, s.size());`` |                                                                         |
      +-----------------------------+-----------------------------------------+-------------------------------------------------------------------------+

`Aliases for integer constraints <https://www.gecode.dev/doc/6.4.0/reference/group__TaskModelMiniModelIntAlias.html>`__ provide some popular aliases. :numref:`fig:m:minimodel:alias` lists the aliases and their corresponding definitions.

.. _sec:m:minimodel:setalias:


.. _modeling:m-minimodel:aliases-for-set-constraints:

Aliases for set constraints
---------------------------

`Aliases for set constraints <https://www.gecode.dev/doc/6.4.0/reference/group__TaskModelMiniModelSetAlias.html>`__ provide aliases and convenience post functions for useful set constraints.

``channel(home, x, y)`` is an alias for ``rel(home, SOT_UNION, x, y)``, posting the constraint that ``y`` is exactly the set of integers :math:`\{\mathtt{x}_0,\dots,\mathtt{x}_{|\mathtt{x}|-1}\}`. In addition to the union constraint, it posts an ``nvalues`` constraint for stronger propagation (see :ref:`sec:m:integer:nvalues`).

``range(home, x, y, z)``, where ``x`` is an array of integer variables and ``y`` and ``z`` are set variables, is an alias for ``element(home, SOT_UNION, x, y, z)``. This constraints treats ``x`` as defining a function, and constrains ``z`` to be the range of the function restricted to ``y``:

.. math:: z=\bigcup_{i\in y}\{x_i\}

Conversely, ``roots(home, x, y, z)`` constrains ``y`` to be the roots of the elements in ``z``, i.e., those indices mapping to elements in ``z``:

.. math:: y=\bigcup_{i\in z}\{j\ |\ x_j=i\}

(see also GCCat: `roots <http://www.emn.fr/z-info/sdemasse/gccat/Croots.html>`__).

.. [1]
   In case a linear expression has only integer variables or only Boolean variables, a single ``linear`` constraint is posted. If the expression contains both integer and Boolean variables, two ``linear`` constraints are posted.

.. [2]
   The integer module cannot know anything about regular expressions. Hence, it is impossible in C++ to avoid the implicit conversion. This is due to the fact that the conversion is controlled by a type operator (that must reside in the MiniModel module) and not by a constructor that could be made ``explicit``.

.. mpg-covered: caption:docs/src/chapters/modeling/m-minimodel.tex.in:77:fig:m:minimodel:integer:expr
.. mpg-covered: table:docs/src/chapters/modeling/m-minimodel.tex.in:79:tabular@docs/src/chapters/modeling/m-minimodel.tex.in:79
.. mpg-covered: caption:docs/src/chapters/modeling/m-minimodel.tex.in:116:fig:m:minimodel:integer:rel
.. mpg-covered: table:docs/src/chapters/modeling/m-minimodel.tex.in:118:tabular@docs/src/chapters/modeling/m-minimodel.tex.in:118
.. mpg-covered: caption:docs/src/chapters/modeling/m-minimodel.tex.in:250:fig:m:minimodel:bool
.. mpg-covered: table:docs/src/chapters/modeling/m-minimodel.tex.in:252:tabular@docs/src/chapters/modeling/m-minimodel.tex.in:252
.. mpg-covered: tip:docs/src/chapters/modeling/m-minimodel.tex.in:294:unlabeled-tip@docs/src/chapters/modeling/m-minimodel.tex.in:294
.. mpg-covered: tip:docs/src/chapters/modeling/m-minimodel.tex.in:374:unlabeled-tip@docs/src/chapters/modeling/m-minimodel.tex.in:374
.. mpg-covered: caption:docs/src/chapters/modeling/m-minimodel.tex.in:394:fig:m:minimodel:set
.. mpg-covered: table:docs/src/chapters/modeling/m-minimodel.tex.in:396:tabular@docs/src/chapters/modeling/m-minimodel.tex.in:396
.. mpg-covered: caption:docs/src/chapters/modeling/m-minimodel.tex.in:487:fig:m:minimodel:float:expr
.. mpg-covered: table:docs/src/chapters/modeling/m-minimodel.tex.in:490:tabular@docs/src/chapters/modeling/m-minimodel.tex.in:490
.. mpg-covered: caption:docs/src/chapters/modeling/m-minimodel.tex.in:538:fig:m:minimodel:float:rel
.. mpg-covered: table:docs/src/chapters/modeling/m-minimodel.tex.in:540:tabular@docs/src/chapters/modeling/m-minimodel.tex.in:540
.. mpg-covered: caption:docs/src/chapters/modeling/m-minimodel.tex.in:595:fig:m:minimodel:domexpr
.. mpg-covered: literal-projection:docs/src/chapters/modeling/m-minimodel.tex.in:596:Boolean domain expression
.. mpg-covered: literal-projection:docs/src/chapters/modeling/m-minimodel.tex.in:620:Boolean domain expression:create Boolean domain expression
.. mpg-covered: literal-projection:docs/src/chapters/modeling/m-minimodel.tex.in:636:Boolean domain expression:post member function
.. mpg-covered: tip:docs/src/chapters/modeling/m-minimodel.tex.in:717:unlabeled-tip@docs/src/chapters/modeling/m-minimodel.tex.in:717
.. mpg-covered: tip:docs/src/chapters/modeling/m-minimodel.tex.in:794:unlabeled-tip@docs/src/chapters/modeling/m-minimodel.tex.in:794
.. mpg-covered: caption:docs/src/chapters/modeling/m-minimodel.tex.in:848:fig:m:minimodel:reg
.. mpg-covered: table:docs/src/chapters/modeling/m-minimodel.tex.in:850:tabular@docs/src/chapters/modeling/m-minimodel.tex.in:850
.. mpg-covered: tip:docs/src/chapters/modeling/m-minimodel.tex.in:904:unlabeled-tip@docs/src/chapters/modeling/m-minimodel.tex.in:904
.. mpg-covered: caption:docs/src/chapters/modeling/m-minimodel.tex.in:955:fig:m:minimodel:alias
.. mpg-covered: table:docs/src/chapters/modeling/m-minimodel.tex.in:957:tabular@docs/src/chapters/modeling/m-minimodel.tex.in:957
