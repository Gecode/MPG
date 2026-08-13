:orphan:

.. _part:v:

.. _part-v:

Programming variables
=====================

.. mpg-part:: Programming variables
   :letter: V
   :authors: Christian Schulte

   .. mpg-part-blurb-start

   This part explains how new variable types can be programmed with Gecode.

   In order to be able to program variables, all chapters in this part should
   be read. The chapters capture the following:

   * :ref:`chap:v:started` outlines how a new variable type can be programmed
     for Gecode.
   * :ref:`chap:v:varimp` shows how the kernel-specific and variable
     domain-specific aspects of a variable implementation are specified and
     programmed.
   * :ref:`chap:v:var` shows how variables and variable arrays for modeling
     are programmed for a given variable implementation.
   * :ref:`chap:v:view` shows how views for programming propagators and
     branchers are programmed for a given variable implementation.
   * :ref:`chap:v:branch` explains how variable-value branchings can be
     implemented from functionality provided by Gecode.
   * :ref:`chap:v:all` finally explains how a new variable type can be used
     with Gecode.

   .. important::

      Programming variables requires to configure and recompile Gecode from
      its source code. Using an already installed package is not sufficient.
      More details can be found in :ref:`chap:v:all`.

   .. mpg-part-blurb-end
