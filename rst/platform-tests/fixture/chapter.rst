.. _chap:m:fixture:

Getting started
===============

.. _fixture-first-model:

A first model
-------------

This fixture checks :math:`x \in \mathbb{Z}`, an exact legacy-label reference
to :ref:`chap:m:fixture`, a stable reference to :ref:`fixture-first-model`, and
the publication vocabulary. It also references the arbitrary-content
:numref:`fig:m:fixture` and
the semantic :ref:`fixture-tip`.

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
