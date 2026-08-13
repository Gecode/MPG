.. only:: latex

   .. mpg-part:: Case studies
      :letter: C
      :name: pdf-part:c
      :authors: Christian Schulte, Guido Tack, Mikael Z. Lagerkvist

      .. include:: ../parts/case-studies.rst
         :start-after: .. mpg-part-blurb-start
         :end-before: .. mpg-part-blurb-end

.. _chap:c:golomb:

Golomb rulers
=============


This chapter studies a simple problem that is commonly used as an example for constraint programming. The model uses nothing but a single ``distinct`` constraint, a few ``rel`` constraints, and posts linear expressions. As the problem is so well known, it might serve as an initial case study of how to model with Gecode.

.. _sec:c:golomb:problem:

Problem
-------


The problem is to find an optimal *Golomb ruler* (see `CSPLib problem 6 <https://www.csplib.org/Problems/prob006/>`__ ) of size :math:`n`. A Golomb ruler has :math:`n` marks :math:`0=\mathtt{m}_0<\mathtt{m}_1<\cdots<\mathtt{m}_{n-1}` such that the distances :math:`\mathtt{d}_{i,j}=\mathtt{m}_j-\mathtt{m}_i` for :math:`0\leq i<j<n` are pairwise distinct. An optimal Golomb ruler is of minimal length (that is, :math:`\mathtt{m}_{n-1}` is minimal). :numref:`fig:c:golomb:example` shows an optimal Golomb ruler with :math:`6` marks.


.. mpg-figure:: An optimal Golomb ruler with :math:`6` marks
   :name: fig:c:golomb:example

   .. only:: html

      .. image:: /figures/fig-c-golomb-example.svg
         :alt: An optimal Golomb ruler with 6 marks

   .. only:: latex

      .. image:: /figures/pdf/fig-c-golomb-example.pdf
         :alt: An optimal Golomb ruler with 6 marks


In the model for Golomb rulers, we are going to use the following construction for a Golomb ruler (a non-optimal ruler, though) as it provides upper bounds on the values for the marks of a ruler. The upper bounds improve the efficiency of our model, see below for more details.

Assume that the distance between marks :math:`i` and :math:`i+1` is :math:`m_{i+1}-m_i=2^{i+1}` (that is, for example, :math:`m_1-m_0=1`, :math:`m_2-m_1=2`, :math:`m_3-m_2=4`, and so on). Then the marks are

.. math:: m_i=\sum_{k=1}^i 2^{k-1}=2^{i}-1.

:numref:`fig:c:golomb:constructed` shows a Golomb ruler with :math:`6` marks following this construction.


.. mpg-figure:: A constructed Golomb ruler with :math:`6` marks
   :name: fig:c:golomb:constructed

   .. only:: html

      .. image:: /figures/fig-c-golomb-constructed.svg
         :alt: A constructed Golomb ruler with 6 marks

   .. only:: latex

      .. image:: /figures/pdf/fig-c-golomb-constructed.pdf
         :alt: A constructed Golomb ruler with 6 marks


Now consider the bit representation of :math:`m_i`: exactly the least :math:`i` bits are one. For the distances

.. math:: d_{i,j}=m_j-m_i=\sum_{k=1}^j 2^{k-1}-\sum_{k=1}^i 2^{k-1}

we can easily see that in their bit representation the least :math:`i` bits are zero, followed by :math:`j-i` ones. That means for :math:`0\leq
i<j<n` the bit representations of the :math:`d_{i,j}` are pairwise distinct. In other words, we can always construct a Golomb ruler with :math:`n` marks of length :math:`m_{n-1}=2^{n-1}-1`.

.. _sec:c:golomb:model:

Model
-----


.. _fig:c:golomb:script:

.. mpg-code:: golomb
   :caption: A script for computing Golomb rulers
   :download:


:ref:`fig:c:golomb:script` shows the script for implementing the Golomb ruler model. The script stores a variable array ``m`` for the marks. The largest possible value of a mark is set to :math:`2^{n-1}-1` according to the construction of a Golomb ruler in the previous section, provided that this value does not exceed the possible size limit of an integer (integers in Gecode are at least 32 bits, this is checked when Gecode is configured for compilation). If :math:`n\geq 31` we just choose the largest possible integer value for an integer variable (see :api:`Int::Limits` ).


.. _tip:c:golomb:beautifuldomains:

.. mpg-tip:: Small variable domains are still beautiful

   As mentioned in :ref:`tip:m:integer:beautifuldomains` , initializing variable domains to be small makes sense. For example, if we always chose ``Int::Limits::max`` rather than the smaller upper bounds for Golomb rulers with :math:`n< 31`, the propagators for ``linear`` constraining the distances would have to resort to extended precision as the internal computations during propagation exceed the integer precision. That would mean that scripts for :math:`n< 31` would run approximately 15% slower!


The script does not store a variable array for the distances (unlike the array for the marks), they are stored in an integer variable argument array. As the distances are only needed for posting constraints but not for printing the solution, it is more efficient to store them in an variable argument array but not in a variable array. More details on argument arrays and their relation to variable arrays can be found in :ref:`sec:m:integer:proper` .

The ``cost()`` function as required by the class ``MinimizeScript`` (see :ref:`sec:m:driver:script` ) just returns the largest mark on the ruler.

.. _case-studies:golomb:marks:

Marks.
''''''

Assigning the first mark to zero and ordering the marks in increasing order is done by posting ``rel`` constraints (see :ref:`sec:m:integer:rel:int` ):


.. mpg-code:: golomb:constraining marks
   :direct:


.. _case-studies:golomb:distances:

Distances.
''''''''''

The number of marks ``n`` and number of distances ``n_d`` are initialized so that they can be used for posting constraints:


.. mpg-code:: golomb:number of marks and distances
   :direct:


As mentioned, the distances are stored in an integer variable argument array ``d``. The fields of the array ``d`` are initialized by the variable returned by the ``expr()`` function for linear expressions (see :ref:`sec:m:minimodel:exprrel` ):


.. mpg-code:: golomb:posting distance constraints
   :direct:


One might be tempted to optimize the posting of distance constraints for :math:`\mathtt{d}_{0,j}` for :math:`0<j<n` as :math:`\mathtt{m}_0=0` and hence :math:`\mathtt{d}_{0,j}=\mathtt{m}_j` for :math:`0<j<n`. Optimizing avoids to create new variables (that is, the variables :math:`\mathtt{m}_j` are stored as :math:`\mathtt{d}_{0,j}` for :math:`0<j<n`) and posting propagators to implement the equality constraints :math:`\mathtt{d}_{0,j}=\mathtt{m}_j` for :math:`0<j<n`.

However, the ``expr()`` function does this automatically. As :math:`\mathtt{m}_0` is already assigned by posting a ``rel`` constraint, the ``expr()`` function simplifies the posted expressions accordingly.

Finally, all distances must be pairwise distinct (see :ref:`sec:m:integer:distinct` ) where bounds propagation is requested (see :ref:`sec:m:integer:ipl` ):


.. mpg-code:: golomb:distances must be distinct
   :direct:


Intuitively, bounds propagation is sufficient as also the propagation for the distances is using bounds propagation.

.. _case-studies:golomb:implied-constraints:

Implied constraints.
''''''''''''''''''''

The following implied constraints are due to :cite:p:`Golomb` . A distance :math:`\mathtt{d}_{i,j}` for :math:`0\leq i<j<n` satisfies the property that it is equal to the sum of all distances between marks :math:`\mathtt{m}_i` and :math:`\mathtt{m}_j`. That is

.. math::

   \mathtt{d}_{i,j} =
   \mathtt{d}_{i,i+1} +
   \mathtt{d}_{i+1,i+2} + \cdots +
   \mathtt{d}_{j-1,j}

This can be verified as follows:

.. math::

   \begin{aligned}
   \mathtt{d}_{i,j}
   &=&\mathtt{m}_j-\mathtt{m}_i\\
   &=&(\mathtt{m}_{j} - \mathtt{m}_{j-1})
    + (\mathtt{m}_{j-1} - \mathtt{m}_{j-2})
    + \cdots
    + (\mathtt{m}_{i+1} - \mathtt{m}_{i})\\
   &=&
   \mathtt{d}_{j-1,j} + \mathtt{d}_{j-2,j-1} + \cdots +
   \mathtt{d}_{i,i+1}\\
   &=&
   \mathtt{d}_{i,i+1} +
   \mathtt{d}_{i+1,i+2} + \cdots +
   \mathtt{d}_{j-1,j}
   \end{aligned}

As all distances :math:`\mathtt{d}_{i,j}` for :math:`0\leq i<j<n` must be pairwise distinct, also the :math:`j-i` distances

.. math::

   \mathtt{d}_{i,i+1},
   \mathtt{d}_{i+1,i+2}, \ldots,
   \mathtt{d}_{j-1,j}

must be pairwise distinct and hence must be :math:`j-i` distinct integers. That means that

.. math::

   \mathtt{d}_{i,j} =
   \mathtt{d}_{i,i+1} +
   \mathtt{d}_{i+1,i+2} + \cdots +
   \mathtt{d}_{j-1,j}

must be at least the sum of the first :math:`j-i` integers:

.. math:: \mathtt{d}_{i,j} \geq \sum_{l=1}^{j-i} l=(j-i)(j-i+1)/2

The implied constraints can be posted as a lower bound with a ``rel`` constraint (see :ref:`sec:m:integer:rel:int` ) for the distances as follows:


.. mpg-code:: golomb:implied constraints
   :direct:


Note that one could also combine the posting of the distance constraints with constraining the lower bounds of the distances for efficiency. However, we separate both for clarity. Anyway, the time spent on posting constraints is insignificant to the time spent on solving the model!

.. _case-studies:golomb:symmetry-breaking:

Symmetry breaking.
''''''''''''''''''

Provided that the ruler has a sufficient number of marks (that is, :math:`\mathtt{n}>2`) we can break (a few) symmetries by constraining the distance :math:`\mathtt{d}_{0,1}` (stored at the first position in the array ``d``) between the first and second mark to be smaller than the distance :math:`\mathtt{d}_{\mathtt n-2,\mathtt n-1}` (stored at the last position in the array ``d``) between the next to last and last mark as follows:


.. mpg-code:: golomb:symmetry breaking
   :direct:


.. _case-studies:golomb:branching:

Branching.
''''''''''

The branching chooses the marks from left to right on the ruler and assigns the smallest possible value for a mark first:


.. mpg-code:: golomb:branching
   :direct:


.. _sec:c:golomb:info:

More information
----------------


This case study is also available as an example, see :api:`golomb-ruler` . For a detailed discussion of how to model the Golomb ruler problem, see  :cite:p:`Golomb` .

..
   Migration traceability for the migrated semantic constructs above.

.. mpg-covered: caption:docs/src/chapters/case-studies/c-golomb.tex.in:27:fig:c:golomb:example
.. mpg-covered: caption:docs/src/chapters/case-studies/c-golomb.tex.in:57:fig:c:golomb:constructed
.. mpg-covered: caption:docs/src/chapters/case-studies/c-golomb.tex.in:86:fig:c:golomb:script
.. mpg-covered: literal-projection:docs/src/chapters/case-studies/c-golomb.tex.in:87:golomb
.. mpg-covered: literal-projection:docs/src/chapters/case-studies/c-golomb.tex.in:133:golomb:constraining marks
.. mpg-covered: literal-projection:docs/src/chapters/case-studies/c-golomb.tex.in:139:golomb:number of marks and distances
.. mpg-covered: literal-projection:docs/src/chapters/case-studies/c-golomb.tex.in:145:golomb:posting distance constraints
.. mpg-covered: literal-projection:docs/src/chapters/case-studies/c-golomb.tex.in:163:golomb:distances must be distinct
.. mpg-covered: literal-projection:docs/src/chapters/case-studies/c-golomb.tex.in:221:golomb:implied constraints
.. mpg-covered: literal-projection:docs/src/chapters/case-studies/c-golomb.tex.in:238:golomb:symmetry breaking
.. mpg-covered: literal-projection:docs/src/chapters/case-studies/c-golomb.tex.in:244:golomb:branching
