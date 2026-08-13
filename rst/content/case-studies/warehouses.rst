.. _chap:c:warehouses:

Locating warehouses
===================


This chapter demonstrates the warehouse location problem. It shows how to use ``element``, global counting (``count``), and ``linear`` constraints.

.. _sec:c:warehouses:problem:

Problem
-------


The problem is taken from  (Chapter 10; :cite:p:`OPL:1999`) , see also `CSPLib problem 34 <https://www.csplib.org/Problems/prob034/>`__ . A company needs to construct warehouses to supply stores with goods. Each candidate warehouse has a certain capacity defining how many stores it can supply. Each store shall be supplied by exactly one warehouse. Maintaining a warehouse incurs a fixed cost. Costs for transportation from warehouses to stores depend on the locations of warehouses and stores.

We want to determine which warehouses should be opened (that is, supply to at least one store) and which warehouse should supply which store such that the overall cost (transportation costs plus fixed maintenance costs) is smallest.

In the following problem instance, the fixed maintenance cost ``c_fixed`` for a warehouse is :math:`30`. There are five candidate warehouses :math:`w_0, \ldots, w_4` and ten stores :math:`s_0, \ldots,
s_{9}`. The candidate warehouses have the following ``capacity``:

.. container:: center

   =========== =========== =========== =========== ===========
   :math:`w_0` :math:`w_1` :math:`w_2` :math:`w_3` :math:`w_4`
   =========== =========== =========== =========== ===========
   1           4           2           1           3
   =========== =========== =========== =========== ===========

The costs to supply a store by a candidate warehouse are defined by a matrix :math:`\mathtt{c_supply}_{i,j}` (:math:`0\leq i<10`, :math:`0\leq j < 5`) as follows:

.. container:: center

   =========== =========== =========== =========== =========== ===========
   \           :math:`w_0` :math:`w_1` :math:`w_2` :math:`w_3` :math:`w_4`
   =========== =========== =========== =========== =========== ===========
   :math:`s_0` 20          24          11          25          30
   :math:`s_1` 28          27          82          83          74
   :math:`s_2` 74          97          71          96          70
   :math:`s_3` 2           55          73          69          61
   :math:`s_4` 46          96          59          83          4
   :math:`s_5` 42          22          29          67          59
   :math:`s_6` 1           5           73          59          56
   :math:`s_7` 10          73          13          43          96
   :math:`s_8` 93          35          63          85          46
   :math:`s_9` 47          65          55          71          95
   =========== =========== =========== =========== =========== ===========

.. _sec:c:warehouses:model:

Model
-----


.. _fig:c:warehouses:script:

.. mpg-code:: warehouses
   :caption: A script for locating warehouses
   :download:


The outline for the script implementing our model is shown in :ref:`fig:c:warehouses:script` . The data definitions are as described in the previous section.

As we need to minimize the total cost which is an integer variable, the script inherits from the class ``IntMinimizeScript`` which is a driver-defined subclass (similar to ``Script`` and ``Space``) of ``IntMinimizeSpace`` (see :ref:`sec:m:minimodel:optimize` ), see :ref:`sec:m:driver:script` . This in particular means that the class must define a virtual ``cost()`` function returning an integer variable, see below.

.. _case-studies:warehouses:variables:

Variables.
''''''''''

The script declares the following variables:


.. mpg-code:: warehouses:variables
   :direct:


where:

- for each store :math:`s`, there is a variable :math:`\mathtt{supplier}_s` such that :math:`\mathtt{supplier}_s=w` if warehouse :math:`w` supplies store :math:`s`;

- for each warehouse :math:`w`, there is a Boolean variable :math:`\mathtt{open}_w` which equals one, if the warehouse :math:`w` supplies at least one store;

- for each store :math:`s`, there is a variable :math:`\mathtt{c_store}_s` which defines the cost for :math:`s` to be supplied by warehouse :math:`\mathtt{supplier}_s`;

- a variable ``c_total`` which defines the total cost.


.. _tip:c:warehouses:varchoice:

.. mpg-tip:: Choose variables to avoid constraints

   Just by the choice of ``supplier`` variables where :math:`\mathtt{supplier}_s=w` if warehouse :math:`w` supplies store :math:`s`, the problem constraint that each store shall be supplied by exactly one warehouse is enforced. Hence, no explicit constraints must be posted in our model. After all, no ``supplier`` variable can take on two different values!

   This is good modeling practice: choosing variables such that some of the problem constraints are automatically enforced.


The variables are initialized as follows:


.. mpg-code:: warehouses:variable initialization
   :direct:


We only declare but do not initialize the cost variables ``c_store`` and ``c_total``, as we will assign them by results obtained by posting expressions, see :ref:`sec:m:minimodel:exprrel` . The difference between declaring variables and initializing them such that new variables are created is explained in detail in :ref:`sec:m:integer:create` .

.. _case-studies:warehouses:constraints:

Constraints.
''''''''''''

For a given warehouse :math:`w` the following must hold: the number of stores :math:`s` supplied by :math:`w` is not allowed to exceed the capacity of :math:`w`. This can be expressed by a counting constraint ``count`` (see :ref:`sec:m:integer:count` ) as follows:


.. mpg-code:: warehouses:do not exceed capacity
   :direct:


Here, the array of integer sets ``c`` defines how many stores can be supplied by a warehouse, where :math:`\mathtt{c}_w` contains every legal number of occurrences of :math:`w` in ``supplier``. To achieve strong propagation for the ``count`` constraint, we choose domain propagation by providing the additional argument ``IPL_DOM`` (see :ref:`sec:m:integer:ipl` ).

For a given warehouse :math:`w` the following must hold: if the number of stores :math:`s` supplied by :math:`w` is at least one, then :math:`\mathtt{open}_w` equals one. That is, :math:`\mathtt{open}_{\mathtt{supplier}_s}` must be ``1`` for all stores :math:`s`. This is expressed by using ``element`` constraints (see :ref:`sec:m:integer:element` ) as follows:


.. mpg-code:: warehouses:open warehouses
   :direct:


.. _case-studies:warehouses:cost-computation:

Cost computation.
'''''''''''''''''

The cost :math:`\mathtt{c_store}_s` for each store :math:`s` is computed by an ``element`` constraint (see :ref:`sec:m:integer:element` ), mapping the warehouse supplying :math:`s` to the appropriate cost:


.. mpg-code:: warehouses:cost for each warehouse
   :direct:


The total cost ``c_total`` is defined by the cost of open warehouses (that is, the sum of :math:`\mathtt{open}_w` for all warehouses :math:`w` multiplied with the fixed maintenance cost for a warehouse) and the cost of stores (that is, the sum of the :math:`\mathtt{c_store}_s` for all stores :math:`s`):


.. mpg-code:: warehouses:total cost
   :direct:


Note that the linear expression posted for defining the total cost mixes integer and Boolean variables and is automatically decomposed into the appropriate ``linear`` constraints, see :ref:`sec:m:minimodel:exprrel` .


.. _tip:c:warehouses:beautifuldomains:

.. mpg-tip:: Small variable domains are still beautiful

   As mentioned in :ref:`tip:m:integer:beautifuldomains` , initializing variable domains to be small makes sense.

   Here we choose to post expressions (see :ref:`sec:m:minimodel:exprrel` ) via the ``expr()`` function that returns an integer variable. The integer variable returned by ``expr()`` has automatically computed and reasonable bounds.

   A different choice would be to initialize the variables ``c_store`` and ``c_total`` in the constructor of the script and constrain them explicitly (for example, via the ``rel()`` function where the expression for ``expr()`` is turned into an equality relation). But that would mean that we either have to compute some estimates for the bounds used for initializing the variables or resort — without real necessity — to the largest possible integer value.


.. _case-studies:warehouses:branching:

Branching.
''''''''''

The branching proceeds in two steps, implemented by two different branchings. The first branching assigns values to the variables :math:`\mathtt{c_store}_s` and follows the strategy of maximal regret: select the variable for which the difference between the smallest value and the next larger value is maximal (see :ref:`sec:m:branch:int` ). The second branching makes sure that all stores are being assigned a warehouse. This branching is necessary as supplying a store could have the same cost for several different warehouses (depending on the data used for the model). Hence, even though all variables in ``c_store`` are assigned, not all variables in ``supplier`` must be assigned and hence the total cost is also not assigned. The branchings are posted in the appropriate order as follows:


.. mpg-code:: warehouses:branching
   :direct:


.. _case-studies:warehouses:cost-function:

Cost function.
''''''''''''''

The cost function ``cost()`` to be used by the search engine is defined to return the total cost ``c_total``:


.. mpg-code:: warehouses:cost function
   :direct:


.. _sec:c:warehouses:info:

More information
----------------


This problem is also available as a Gecode example, see :api:`warehouses` . The model presented in (Chapter 10; :cite:p:`OPL:1999`) proposes a better branching than the branching shown in the previous section.

..
   Migration traceability for the migrated semantic constructs above.

.. mpg-covered: table:docs/src/chapters/case-studies/c-warehouses.tex.in:32:tabular@docs/src/chapters/case-studies/c-warehouses.tex.in:32
.. mpg-covered: table:docs/src/chapters/case-studies/c-warehouses.tex.in:42:tabular@docs/src/chapters/case-studies/c-warehouses.tex.in:42
.. mpg-covered: caption:docs/src/chapters/case-studies/c-warehouses.tex.in:62:fig:c:warehouses:script
.. mpg-covered: literal-projection:docs/src/chapters/case-studies/c-warehouses.tex.in:63:warehouses
.. mpg-covered: literal-projection:docs/src/chapters/case-studies/c-warehouses.tex.in:84:warehouses:variables
.. mpg-covered: literal-projection:docs/src/chapters/case-studies/c-warehouses.tex.in:115:warehouses:variable initialization
.. mpg-covered: literal-projection:docs/src/chapters/case-studies/c-warehouses.tex.in:132:warehouses:do not exceed capacity
.. mpg-covered: literal-projection:docs/src/chapters/case-studies/c-warehouses.tex.in:146:warehouses:open warehouses
.. mpg-covered: literal-projection:docs/src/chapters/case-studies/c-warehouses.tex.in:154:warehouses:cost for each warehouse
.. mpg-covered: literal-projection:docs/src/chapters/case-studies/c-warehouses.tex.in:161:warehouses:total cost
.. mpg-covered: literal-projection:docs/src/chapters/case-studies/c-warehouses.tex.in:201:warehouses:branching
.. mpg-covered: literal-projection:docs/src/chapters/case-studies/c-warehouses.tex.in:207:warehouses:cost function
