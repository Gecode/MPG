.. _chap:m:driver:


.. _modeling:m-driver:script-commandline-driver:

Script commandline driver
=========================

The commandline driver (see `Script commandline driver <https://www.gecode.dev/doc/6.4.0/reference/group__TaskDriver.html>`__) provides support for passing common commandline options to programs and a sub-class for spaces called ``Script`` that can take advantage of the options.

.. _modeling:m-driver:overview:

.. mpg-paragraph:: Overview.

:ref:`sec:m:driver:options` summarizes the commandline options supported by the commandline driver. The base classes for scripts that work together with the commandline driver are sketched in :ref:`sec:m:driver:script`.

.. important::

   Do not forget to add

   .. mpg-code:: snippet:m-driver:chap:m:driver:code:1
      :direct:

   to your program when you want to use the script commandline driver.

.. _sec:m:driver:options:


.. _modeling:m-driver:commandline-options:

Commandline options
-------------------

.. mpg-figure:: Predefined commandline options
   :name: fig:m:driver:options:a

   .. container:: center

      +--------------------------------------------+--------------------------------------------------------------------------------+----------------------------------------+
      | option                                     | type                                                                           | explanation                            |
      +============================================+================================================================================+========================================+
      | propagation options                        |                                                                                |                                        |
      +--------------------------------------------+--------------------------------------------------------------------------------+----------------------------------------+
      | ``-ipl``                                   | :math:`\{\mathtt{def},\mathtt{val},\mathtt{bnd},\mathtt{dom}\}`                | integer propagation level              |
      +--------------------------------------------+--------------------------------------------------------------------------------+----------------------------------------+
      | branching options                          |                                                                                |                                        |
      +--------------------------------------------+--------------------------------------------------------------------------------+----------------------------------------+
      | ``-decay``                                 | ``double``                                                                     | decay-factor                           |
      +--------------------------------------------+--------------------------------------------------------------------------------+----------------------------------------+
      | ``-seed``                                  | ``unsigned int``                                                               | seed for random numbers                |
      +--------------------------------------------+--------------------------------------------------------------------------------+----------------------------------------+
      | search options                             |                                                                                |                                        |
      +--------------------------------------------+--------------------------------------------------------------------------------+----------------------------------------+
      | ``-solutions``                             | ``unsigned int``                                                               | how many solutions (:math:`0` for all) |
      +--------------------------------------------+--------------------------------------------------------------------------------+----------------------------------------+
      | ``-threads``                               | ``double``                                                                     | how many threads                       |
      +--------------------------------------------+--------------------------------------------------------------------------------+----------------------------------------+
      | ``-c-d``                                   | ``unsigned int``                                                               | commit recomputation distance          |
      +--------------------------------------------+--------------------------------------------------------------------------------+----------------------------------------+
      | ``-a-d``                                   | ``unsigned int``                                                               | adaptive recomputation distance        |
      +--------------------------------------------+--------------------------------------------------------------------------------+----------------------------------------+
      | ``-d-l``                                   | ``unsigned int``                                                               | discrepancy limit for ``LDS``          |
      +--------------------------------------------+--------------------------------------------------------------------------------+----------------------------------------+
      | ``-node``                                  | ``unsigned long long int``                                                     | cutoff for number of nodes             |
      +--------------------------------------------+--------------------------------------------------------------------------------+----------------------------------------+
      | ``-fail``                                  | ``unsigned long long int``                                                     | cutoff for number of failures          |
      +--------------------------------------------+--------------------------------------------------------------------------------+----------------------------------------+
      | ``-time``                                  | ``double``                                                                     | cutoff for time in milliseconds        |
      +--------------------------------------------+--------------------------------------------------------------------------------+----------------------------------------+
      | ``-step``                                  | ``double``                                                                     | improvement step for floats            |
      +--------------------------------------------+--------------------------------------------------------------------------------+----------------------------------------+
      | restart-based and portfolio search options |                                                                                |                                        |
      +--------------------------------------------+--------------------------------------------------------------------------------+----------------------------------------+
      | ``-restart``                               | :math:`\{\mathtt{none},\mathtt{constant},\mathtt{linear},`                     | enable restarts, define cutoff         |
      +--------------------------------------------+--------------------------------------------------------------------------------+----------------------------------------+
      |                                            | :math:`\;\mathtt{geometric},\mathtt{luby}\}`                                   |                                        |
      +--------------------------------------------+--------------------------------------------------------------------------------+----------------------------------------+
      | ``-restart-scale``                         | ``unsigned int``                                                               | scale-factor for cutoff values         |
      +--------------------------------------------+--------------------------------------------------------------------------------+----------------------------------------+
      | ``-restart-base``                          | ``double``                                                                     | base for geometric cutoff values       |
      +--------------------------------------------+--------------------------------------------------------------------------------+----------------------------------------+
      | ``-nogoods``                               | :math:`\{\mathtt{false},\mathtt{true},\mathtt{0},\mathtt{1}\}`                 | whether to post no-goods               |
      +--------------------------------------------+--------------------------------------------------------------------------------+----------------------------------------+
      | ``-nogoods-limit``                         | ``unsigned int``                                                               | depth limit for no-good recording      |
      +--------------------------------------------+--------------------------------------------------------------------------------+----------------------------------------+
      | ``-assets``                                | ``unsigned int``                                                               | number of assets in a portfolio        |
      +--------------------------------------------+--------------------------------------------------------------------------------+----------------------------------------+

.. mpg-figure:: Predefined commandline options, continued
   :name: fig:m:driver:options:b

   .. container:: center

      +-------------------+----------------------------------------------------------------------------------+-------------------------------------------+
      | option            | type                                                                             | explanation                               |
      +===================+==================================================================================+===========================================+
      | execution options |                                                                                  |                                           |
      +-------------------+----------------------------------------------------------------------------------+-------------------------------------------+
      | ``-mode``         | :math:`\{\mathtt{solution},\mathtt{time},\mathtt{stat},`                         | script mode to run                        |
      +-------------------+----------------------------------------------------------------------------------+-------------------------------------------+
      |                   | :math:`\;\mathtt{gist}\}`                                                        |                                           |
      +-------------------+----------------------------------------------------------------------------------+-------------------------------------------+
      | ``-samples``      | ``unsigned int``                                                                 | how many samples                          |
      +-------------------+----------------------------------------------------------------------------------+-------------------------------------------+
      | ``-iterations``   | ``unsigned int``                                                                 | how many iterations per sample            |
      +-------------------+----------------------------------------------------------------------------------+-------------------------------------------+
      | ``-print-last``   | :math:`\{\mathtt{false},\mathtt{true},\mathtt{0},\mathtt{1}\}`                   | whether to only print last solution       |
      +-------------------+----------------------------------------------------------------------------------+-------------------------------------------+
      | ``-file-sol``     | :math:`\{\mathtt{stdout},\mathtt{stdlog},\mathtt{stderr}\}`                      | where to print solutions                  |
      +-------------------+----------------------------------------------------------------------------------+-------------------------------------------+
      | ``-file-stat``    | :math:`\{\mathtt{stdout},\mathtt{stdlog},\mathtt{stderr}\}`                      | where to print statistics                 |
      +-------------------+----------------------------------------------------------------------------------+-------------------------------------------+
      | ``-interrupt``    | :math:`\{\mathtt{false},\mathtt{true},\mathtt{0},\mathtt{1}\}`                   | whether driver catches Ctrl-C             |
      +-------------------+----------------------------------------------------------------------------------+-------------------------------------------+
      | ``-trace``        | :math:`\{\mathtt{init},\mathtt{prune},\mathtt{fix},\mathtt{fail},\mathtt{done},` | which events to trace                     |
      +-------------------+----------------------------------------------------------------------------------+-------------------------------------------+
      |                   | :math:`\;\mathtt{propagate},\mathtt{commit},\mathtt{none},\mathtt{all}\}`        |                                           |
      +-------------------+----------------------------------------------------------------------------------+-------------------------------------------+
      | ``-cp-profiler``  | ``int,int``                                                                      | Comma separated pair of execution id      |
      +-------------------+----------------------------------------------------------------------------------+-------------------------------------------+
      |                   |                                                                                  | and port number to connect to CPProfiler. |
      +-------------------+----------------------------------------------------------------------------------+-------------------------------------------+

.. mpg-figure:: User-definable commandline options
   :name: fig:m:driver:options:user

   .. container:: center

      ================ ====== =========================
      option           type   explanation
      ================ ====== =========================
      ``-branching``   string branching options
      ``-model``       string general model options
      ``-propagation`` string propagation options
      ``-symmetry``    string symmetry breaking options
      ``-search``      string search options
      ================ ====== =========================

The commandline driver provides classes `Options <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1Options.html>`__, `SizeOptions <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1SizeOptions.html>`__, and `InstanceOptions <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1InstanceOptions.html>`__ that support parsing commandline options. All classes support the options as summarized in :numref:`fig:m:driver:options:a`, :numref:`fig:m:driver:options:b`, and :numref:`fig:m:driver:options:user`. Here, for a commandline option with name ``-name``, the option classes provide two functions with name ``name()``: one that takes no argument and returns the current value of the option, and one that takes an argument of the listed type and sets the option to that value. If the commandline options contains a hyphen ``-``, then the member function contain an underscore ``_`` instead. For example, for the options ``-c-d``, ``-a-d``, and ``-d-l`` the member functions are named ``c_d()``, ``a_d()``, ``d_l()``.

The values for ``-threads`` are interpreted as described in :ref:`sec:m:search:options`.

Note that all commanline options can also be used with a starting double hyphen ``--`` instead of a single hyphen.

.. _modeling:m-driver:invoking-help:

.. mpg-paragraph:: Invoking help.

The only option for which no value exists is ``-help``: it prints some configuration information and a help text for the options and stops program execution.

.. _modeling:m-driver:size-and-instance-options:

.. mpg-paragraph:: Size and instance options.

The class `SizeOptions <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1SizeOptions.html>`__ accepts an unsigned integer as the last value on the commandline (of course, without an option). The value can be retrieved or set by member functions ``size()``.

The class `InstanceOptions <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1InstanceOptions.html>`__ accepts a string as the last value on the commandline (of course, without an option). The value can be retrieved or set by member functions ``instance()``.

.. _modeling:m-driver:integer-propagation-level-options:

.. mpg-paragraph:: Integer propagation level options.

The command line option ``-ipl`` accepts a comma separated list of the basic integer propagation levels: ``def`` for the default level, ``val`` for value propagation, ``bnd`` for bounds propagation, and ``dom`` for domain propagation. In addition it accepts the modifiers ``speed``, ``memory``, ``basic``, and ``advanced`` that are used by some constraints and can be given in addition to a basic integer propagation level.

.. _modeling:m-driver:mode-options:

.. mpg-paragraph:: Mode options.

The different modes passed as argument for the option ``-mode`` have the following meaning:

- ``solution`` prints solutions together with some runtime statistics.

- ``time`` can be used for benchmarking: average runtime and coefficient of deviation is printed, where the example is run ``-samples`` times. For examples with short runtime, ``-iterations`` can be used to repeat the example several times before measuring runtime. Note that the runtime includes also setup time (the creation of the space for the model).

- ``stat`` prints short execution statistics.

- ``gist`` runs Gist rather than search engines that print information. Gist is put into depth-first mode, when a non best solution search engine is used (that is, ``DFS``), and into branch-and-bound mode otherwise (that is, ``BAB``).

  If Gecode has not been compiled with support for Gist (see :ref:`tip:m:comfy:conf` for how to find out about Gecode’s configuration), the mode ``gist`` will be ignored and the mode ``solution`` is used instead.

.. _modeling:m-driver:trace-options:

.. mpg-paragraph:: Trace options.

Which events to trace (see also :ref:`chap:m:group`) can be specified by the ``-trace`` commandline option. It accepts a comma-separated list of the event types to trace, that is ``init``, ``prune``, ``fix`` for fixpoint, ``fail`` for failure, and ``done`` as well as ``none`` to trace no events and ``all`` to trace events of all types.

Examples with tracing include `SEND+MORE=MONEY puzzle <https://www.gecode.dev/doc/6.4.0/reference/money_8cpp.html>`__, `Generating Hamming codes <https://www.gecode.dev/doc/6.4.0/reference/hamming_8cpp.html>`__, and `Folium of Descartes <https://www.gecode.dev/doc/6.4.0/reference/descartes-folium_8cpp.html>`__.

.. _modeling:m-driver:cpprofiler-options:

.. mpg-paragraph:: CPProfiler options.

For more details on the CPProfiler, please consult :ref:`sec:m:search:cpprofiler` as the commandline arguments are used exactly as described there.

.. _modeling:m-driver:examples:

.. mpg-paragraph:: Examples.

For an example, in particular, how to use the user-defined options, see :ref:`sec:m:comfy:driver`. As all examples that come with Gecode use the script commandline driver, a plethora of examples is available (see `Example scripts (models) <https://www.gecode.dev/doc/6.4.0/reference/group__Example.html>`__). Also adding additional options is straightforward, for an example see `Golf tournament <https://www.gecode.dev/doc/6.4.0/reference/golf_8cpp.html>`__.

.. _modeling:m-driver:gist-inspectors-and-comparators:

.. mpg-paragraph:: Gist inspectors and comparators.

The driver options can pass inspectors and comparators (see :ref:`sec:m:gist:inspecting_nodes`) to Gist. To register an inspector ``i``, use the ``inspect.click(&i)``, ``inspect.solution(&i)``, or ``inspect.move(&i)`` methods of the option object, for a comparator ``c``, use ``inspect.compare(&c)``.

.. _sec:m:driver:script:


.. _modeling:m-driver:scripts:

Scripts
-------

Scripts (see `Script classes <https://www.gecode.dev/doc/6.4.0/reference/group__TaskDriverScript.html>`__) are subclasses of ``Space`` that are designed to work together with option objects of class `Options <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1Options.html>`__ and `SizeOptions <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1SizeOptions.html>`__.

In particular, the driver module defines scripts ``IntMinimizeScript``, ``IntMaximizeScript``, ``IntLexMinimizeScript``, ``IntLexMaximizeScript``, ``FloatMinimizeScript``, and ``FloatMaximizeScript`` that can be used for finding best solutions based on a virtual ``cost()`` function, see also :ref:`sec:m:comfy:cost` and :ref:`sec:m:minimodel:optimize`.

Subclasses of ``FloatMinimizeScript`` and ``FloatMaximizeScript`` use the value passed on the command line option ``-step`` as value for the improvement step (see :ref:`sec:m:minimodel:optimize:float`). For an example, see `Golden spiral <https://www.gecode.dev/doc/6.4.0/reference/golden-spiral_8cpp.html>`__.

As scripts are absolutely straightforward, all can be understood by following some examples. For an example see :ref:`sec:m:comfy:driver` or all examples that come with Gecode, see `Example scripts (models) <https://www.gecode.dev/doc/6.4.0/reference/group__Example.html>`__.

.. mpg-covered: caption:docs/src/chapters/modeling/m-driver.tex.in:29:fig:m:driver:options:a
.. mpg-covered: table:docs/src/chapters/modeling/m-driver.tex.in:31:tabular@docs/src/chapters/modeling/m-driver.tex.in:31
.. mpg-covered: caption:docs/src/chapters/modeling/m-driver.tex.in:86:fig:m:driver:options:b
.. mpg-covered: table:docs/src/chapters/modeling/m-driver.tex.in:89:tabular@docs/src/chapters/modeling/m-driver.tex.in:89
.. mpg-covered: caption:docs/src/chapters/modeling/m-driver.tex.in:122:fig:m:driver:options:user
.. mpg-covered: table:docs/src/chapters/modeling/m-driver.tex.in:124:tabular@docs/src/chapters/modeling/m-driver.tex.in:124
