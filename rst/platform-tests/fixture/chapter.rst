.. _chap:m:fixture:

Getting started
===============

.. _fixture-first-model:

A first model
-------------

This fixture checks :math:`x \in \mathbb{Z}`, an internal source-label reference
to :ref:`chap:m:fixture`, a stable reference to :ref:`fixture-first-model`, and
the publication vocabulary, including the custom operators
:math:`\arcsinh(x)`, :math:`\arccosh(x)`, and :math:`\arctanh(x)`. It also
checks migrated typewriter notation with :math:`\texttt{x[0]}` and references
the arbitrary-content
:numref:`fig:m:fixture` and
the semantic :ref:`fixture-tip`.

The remaining custom notation is exercised by
:math:`\Gecode, \NN, \ZZ, \RR, \reifyeqv{x}{y}, \reifyimp{x}{y},
\reifypmi{x}{y}`, including legacy :math:`\mbox{prose}`.

.. math::

   0 < 1

.. mpg-paragraph:: Classical heading.

This paragraph verifies the classical paragraph structure in both editions.

.. mpg-figure:: Available values
   :name: fig:m:fixture
   :short-caption: Values

   +-------+---------+
   | Value | Meaning |
   +=======+=========+
   | ``0`` | false   |
   +-------+---------+
   | ``1`` | true    |
   +-------+---------+

.. _fixture-tip:

.. mpg-tip:: Name constraints after their intent

   This keeps explanations connected to the model.

.. code-block:: cpp
   :caption: A minimal model
   :name: fixture-program

   #include <gecode/int.hh>

   class Model : public Gecode::Space {};

.. mpg-part:: Modeling
   :letter: M
   :authors: The Gecode Team
   :name: fixture-part

   Modeling expresses a problem through variables and constraints.
