.. _chap:m:comfy:


.. _modeling:m-comfy:getting-comfortable:

Getting comfortable
===================

This chapter provides an overview of some functionality in Gecode that makes modeling and execution of models more convenient.

.. _modeling:m-comfy:overview:

.. mpg-paragraph:: Overview.

Expressions constructed from standard arithmetic operators for posting linear constraints are discussed in :ref:`sec:m:comfy:expr`, cost functions for best solution search are discussed in :ref:`sec:m:comfy:cost`, and a script commandline driver that supports the most common options for running models from the commandline is discussed in :ref:`sec:m:comfy:driver`.

.. _sec:m:comfy:expr:


.. _modeling:m-comfy:posting-linear-constraints-de-mystified:

Posting linear constraints de-mystified
---------------------------------------

.. mpg-code:: send more money de-mystified
   :name: fig:m:comfy:smm-mm
   :caption: A Gecode model for Send More Money using modeling support


As mentioned in the previous chapter, Gecode comes with simple modeling support for posting constraints defined by linear expressions and relations. The parts of the program for Send More Money from :numref:`fig:m:started:smm` that change are shown in :numref:`fig:m:comfy:smm-mm`. In order to use the modeling support, we have to include the MiniModel header.

The MiniModel module also supports Boolean expressions and relations, and much more, see :ref:`chap:m:minimodel` for more information. The module in itself does not implement any constraints. The function ``rel`` takes the description of the linear constraint, analyzes it, and posts a linear constraint by using the same ``linear`` function we have been using in :ref:`sec:m:started:first`.

.. _sec:m:comfy:cost:


.. _modeling:m-comfy:using-a-cost-function:

Using a cost function
---------------------

.. mpg-code:: send most money with cost
   :name: fig:m:comfy:smm-best:minimodel
   :caption: A Gecode model for Send Most Money using a cost function


:numref:`fig:m:comfy:smm-best:minimodel` uses the class `IntMaximizeSpace <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1IntMaximizeSpace.html>`__ for cost-based optimization for Send Most Money. The class is also included in Gecode’s MiniModel module (see :ref:`sec:m:minimodel:optimize` and `Support for cost-based optimization <https://www.gecode.dev/doc/6.4.0/reference/group__TaskModelMiniModelOptimize.html>`__).

.. container:: samepage

   The `IntMaximizeSpace <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1IntMaximizeSpace.html>`__ class is a sub-class of `Space <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1Space.html>`__ that defines a ``constrain()`` member function based on the cost of a space. Our model must implement a virtual ``cost()`` function that returns an integer variable defining the cost (the function must be ``const``). In our example, we extend the model to maintain the cost (the amount of money) in a dedicated variable ``money`` (note that this variable must also be updated during cloning).

   The cost function then just returns the amount of money as follows:

   .. mpg-code:: send most money with cost:cost function

.. _sec:m:comfy:driver:


.. _modeling:m-comfy:using-the-script-commandline-driver:

Using the script commandline driver
-----------------------------------

In order to experiment from the commandline with different model variants, different search engines, and so on, it is convenient to have support for passing different option values on the commandline that then can be used by a model. Gecode comes with a simple commandline driver that defines ``Script`` as a subclass of ``Space`` for modeling and support for commandline options.

.. _modeling:m-comfy:defining-a-script-class:

.. mpg-paragraph:: Defining a script class.

Suppose that we want to experiment with two different variants of Send Most Money with a cost function: the first variant uses the model from :ref:`sec:m:comfy:cost` and the second variant models the equation :math:`SEND+MOST=MONEY` by using carry variables.

.. container:: samepage

   Using carry variables with several linear equations instead of a single linear equation is straightforward. A carry variable is an integer variable with value ``0`` or ``1`` and each column in the equation :math:`SEND+MOST=MONEY` is modeled by a linear equation involving the appropriate carry variable as follows:

   .. mpg-code:: send most money with driver:using carries

.. mpg-code:: send most money with driver
   :name: fig:m:comfy:driver
   :caption: A Gecode model for Send Most Money using the script commandline driver


:numref:`fig:m:comfy:driver` shows a model for Send Most Money that uses the ``IntMaximizeScript`` class as base class (see `Script classes <https://www.gecode.dev/doc/6.4.0/reference/group__TaskDriverScript.html>`__) rather than ``IntMaximizeSpace`` (likewise, the driver module also offers a ``Script`` class to be used instead of ``Space``). There are three main differences between ``IntMaximizeScript`` and ``IntMaximizeSpace`` (``Script`` and ``Space``):

#. The constructor must accept a constant argument of type ``Options`` (actually, it must accept a constant argument of the type that is specified for the ``run`` member function to be explained below) that is used to pass values computed from options passed on the commandline.

#. The constructor of a subclass of ``IntMaximizeScript`` or any other script class must call the constructor ``IntMaximizeScript`` with an argument of type ``Options``.

#. A subclass of ``IntMaximizeScript`` must define a virtual print function that accepts a standard output stream as argument.

Note that one has to include ``<gecode/driver.hh>`` for a model that uses the script commandline driver. However, neither ``<gecode/search.hh>`` nor ``<gecode/gist.hh>`` need to be included as search is handled by the commandline driver.

.. _tip:m:comfy:link-driver:

.. mpg-tip:: Linking against the driver

   As discussed in :ref:`sec:m:started:run`, when you use the commandline driver on a platform (Linux and relatives) that requires to state all libraries to link against, you also have to link against the library for the commandline driver (that is, for Linux and relatives by adding ``-lgecodedriver`` to the compiler options on the commandline).


The class ``SendMostMoney`` defines an enumeration type with values ``MODEL_SINGLE`` (for a model where a single linear equation is posted for :math:`SEND+MOST=MONEY`) and ``MODEL_CARRY`` (for a model where several linear equations using carry variables are posted for :math:`SEND+MOST=MONEY`). The options object ``opt`` provides a member function ``model`` that returns an enumeration value and posts the constraints accordingly.

.. _modeling:m-comfy:defining-commandline-options:

.. mpg-paragraph:: Defining commandline options.

The mapping between strings passed on the commandline and the values ``MODEL_SINGLE`` and ``MODEL_CARRY`` is established by configuring an object of class `Options <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1Options.html>`__ accordingly as follows:

.. mpg-code:: send most money with driver:commandline options


This code creates a new ``Option`` object ``opt`` where the string ``"SEND + MOST = MONEY"`` serves as identification (such as when requesting to print help about the available commandline options).

The first call to ``opt.model()`` defines that ``single`` is a legal value for the option switch ``-model``, that the string ``use single linear equation`` is the help text for the option value, and that the corresponding value (that is, the value returned by ``opt.model()``) is ``SendMostMoney::MODEL_SINGLE``. The last call to ``opt.model`` defines the default value.

As we are performing best solution search, we want to compute all possible solutions. This is done by setting ``opt.solutions`` to ``0`` (the default value is ``1`` for searching for the first solution). Note that this default value can be changed on the commandline by passing an integer as value for the ``-solutions`` commandline option. Parsing the commandline by ``parse`` now takes the configured values for the commandline options ``-model`` and ``-solutions`` into account.

The `Options <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1Options.html>`__ class supports most options that are useful for propagation, search, and so on similar to the ``model`` option. The full details are explained in :ref:`chap:m:driver`.

The last piece of our model is calling the static ``run`` method of the script class by passing as template arguments our script class type ``SendMostMoney``, ``BAB`` as the search engine we would like to use, and the type of options ``Options`` (as mentioned before, the constructor of the script must accept a single argument of this type).

.. mpg-code:: send most money with driver:run script


.. _modeling:m-comfy:running-the-script-from-the-commandline:

.. mpg-paragraph:: Running the script from the commandline.

Suppose that we have compiled our script example as the file ``send-most-money-with-driver.exe`` (for some platforms, just drop ``.exe``). Then

.. mpg-code:: snippet:m-comfy:tip:m:comfy:link-driver:cmd:1
   :direct:


prints something along the lines

.. mpg-code:: snippet:m-comfy:tip:m:comfy:link-driver:cmd:2
   :direct:


.. container:: samepage

   If we want to try the model with carry variables we can do that by running

   .. mpg-code:: snippet:m-comfy:tip:m:comfy:link-driver:cmd:3
      :direct:

.. container:: samepage

   We can also use Gist by giving a different mode of execution:

   .. mpg-code:: snippet:m-comfy:tip:m:comfy:link-driver:cmd:4
      :direct:

As we call ``run`` with ``BAB`` as type of search, Gist will automatically start in branch-and-bound mode. Other supported modes are ``solution`` (the default mode shown above), ``time`` for printing average runtimes, and ``stat`` for just printing an execution statistics but no solutions.

Another important commandline option is ``-help`` which prints the options supported by the script together with some configuration information. The full details are explained in :ref:`chap:m:driver`.

.. mpg-tip:: Aborting execution

   In the ``solution`` and ``stat`` modes, the driver aborts the search gracefully if you send it a ``SIGINT`` signal, for example by pressing Ctrl-C on the command line. So if your model runs a long time without returning solutions, you can press Ctrl-C and still see the statistics that tell you how deep the search tree was up to that point, or how many nodes the search has explored.


   When you press Ctrl-C twice, the process is interrupted immediately. This can be useful when debugging programs, e.g. if the process is stuck in an infinite loop. Alternatively, you can make the driver ignore Ctrl-C altogether, so that it immediately interrupts your program, using the commandline option ``-interrupt false``.

..

.. _tip:m:comfy:conf:

.. mpg-tip:: How Gecode has been configured

   Depending on the hardware and software platform on which Gecode has been compiled, some features (such as Gist, thread support for parallel search, trigonometric and transcendental constraints for floats) might not be available. For example, if Gist is not supported, the request for ``-mode gist`` will be silently ignored and the normal mode (``-mode solution``) is used instead.


   To find out which features are available, just invoke a program using the commandline driver with the ``-help`` option. At the beginning of the printed text, you will find a short configuration summary.

   The source release can be configured with all optional features, provided that the corresponding dependencies are available when Gecode is built.

.. _tip:m:comfy:version:

.. mpg-tip:: Which version of Gecode are we using?

   Some programs might have to deal with incompatible changes between different versions of Gecode. The Gecode-defined macro ``GECODE_VERSION_NUMBER`` can be used to find out which version of Gecode is used during compilation. The macro’s value is defined as :math:`100000\times x + 100\times y +z` for Gecode version :math:`x.y.z`.

.. mpg-covered: caption:docs/src/chapters/modeling/m-comfy.tex.in:22:fig:m:comfy:smm-mm
.. mpg-covered: literal-projection:docs/src/chapters/modeling/m-comfy.tex.in:23:send more money de-mystified
.. mpg-covered: caption:docs/src/chapters/modeling/m-comfy.tex.in:48:fig:m:comfy:smm-best:minimodel
.. mpg-covered: literal-projection:docs/src/chapters/modeling/m-comfy.tex.in:49:send most money with cost
.. mpg-covered: literal-projection:docs/src/chapters/modeling/m-comfy.tex.in:73:send most money with cost:cost function
.. mpg-covered: literal-projection:docs/src/chapters/modeling/m-comfy.tex.in:101:send most money with driver:using carries
.. mpg-covered: caption:docs/src/chapters/modeling/m-comfy.tex.in:105:fig:m:comfy:driver
.. mpg-covered: literal-projection:docs/src/chapters/modeling/m-comfy.tex.in:106:send most money with driver
.. mpg-covered: literal-projection:docs/src/chapters/modeling/m-comfy.tex.in:164:send most money with driver:commandline options
.. mpg-covered: literal-projection:docs/src/chapters/modeling/m-comfy.tex.in:200:send most money with driver:run script
.. mpg-covered: tip:docs/src/chapters/modeling/m-comfy.tex.in:265:unlabeled-tip@docs/src/chapters/modeling/m-comfy.tex.in:265
