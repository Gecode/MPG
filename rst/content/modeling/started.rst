.. only:: latex

   .. mpg-part:: Modeling
      :letter: M
      :name: pdf-part:m
      :authors: Christian Schulte, Guido Tack, Mikael Z. Lagerkvist

      .. include:: ../parts/modeling.rst
         :start-after: .. mpg-part-blurb-start
         :end-before: .. mpg-part-blurb-end

.. _chap:m:started:


.. _modeling:m-started:getting-started:

Getting started
===============

This chapter provides a basic overview of how to program, compile, link, and execute a constraint model in Gecode. The chapter restricts itself to the fundamental concepts available in Gecode, the following chapter presents functionality that makes programming models more comfortable.

.. _modeling:m-started:overview:

.. mpg-paragraph:: Overview.

:ref:`sec:m:started:first` explains the basics of how a model is programmed in Gecode. This is followed in :ref:`sec:m:started:search` by a discussion of how search is used to find solutions of a model. How a model is compiled, linked, and executed is explained for several different operating systems in :ref:`sec:m:started:run`. :ref:`sec:m:started:gist` shows how Gist as a graphical and interactive search tool can be used for developing constraint models. Search for a best solution of a model is explained in :ref:`sec:m:started:search-best`.

The chapter also includes an explanation of how to obtain and build the Gecode source release in :ref:`sec:m:started:obtain`. That section is worth reading before compiling the examples by hand, as it gives the version and build layout assumed here.

.. _sec:m:started:first:


.. _modeling:m-started:a-first-gecode-model:

A first Gecode model
--------------------

Models in Gecode are implemented using *spaces*. A space is *home* to the *variables*, *propagators* (implementations of constraints), *branchers* (implementations of branchings, describing the search tree’s shape, also known as labelings), and – possibly – an *order* determining a best solution during search.

Not surprisingly in an object-oriented language such as C++, an elegant approach to programming a model is by inheritance: a model inherits from the class `Space <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1Space.html>`__ (implementing spaces) and the subclass constructor implements the model. In addition to the constructor, a model must implement a copy constructor and a copy function such that search for that model works (to be discussed later).

.. _modeling:m-started:send-more-money:

.. mpg-paragraph:: Send More Money.

The model we choose as an example is Send More Money: find distinct digits for the letters :math:`S`, :math:`E`, :math:`N`, :math:`D`, :math:`M`, :math:`O`, :math:`R`, and :math:`Y` such that the well-formed equation (no leading zeros) :math:`SEND+MORE=MONEY` holds.

.. mpg-code:: send more money
   :name: fig:m:started:smm
   :caption: A Gecode model for Send More Money


The program (with some parts yet to be presented) is shown in :numref:`fig:m:started:smm`. Note that clicking a blue line starting with :math:`\blacktriangleright` jumps to the corresponding code. Clicking **[download]** in the upper right corner of the program provides access to the complete program text.

The program starts by including the relevant Gecode headers. To use integer variables and constraints, it includes ``<gecode/int.hh>`` and to access search engines it includes ``<gecode/search.hh>``. All Gecode functionality is in the scope of the namespace `Gecode <https://www.gecode.dev/doc/6.4.0/reference/namespaceGecode.html>`__, for convenience the program makes all functionality of the Gecode namespace visible by ``using namespace Gecode``.

As discussed, the model is implemented as the class ``SendMoreMoney`` inheriting from the class `Space <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1Space.html>`__. It declares an array ``l`` of integer variables and initializes this array to have ``8`` newly created integer variables as elements, where each variable in the array can take values from ``0`` to ``9``. Note that the constructor for the variable array ``l`` takes the current space (that is, ``*this``) as first argument. This is very common: any function that depends on a space takes the current space as argument (called *home space*) Examples are constructors for variables and variable arrays, functions that post constraints, and functions that post branchings.

To simplify the posting of constraints, the constructor defines a variable of type `IntVar <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1IntVar.html>`__ for each letter. Note the difference between creating a new integer variable (as done with creating the array of integer variables together with creating a new integer variable for each array element) and referring to the same integer variable through different C++ variables of type `IntVar <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1IntVar.html>`__. This difference is discussed in more detail in :ref:`sec:m:integer:var`.

.. _modeling:m-started:posting-constraints:

.. mpg-paragraph:: Posting constraints.

For each constraint there is a *constraint post function* that creates *propagators* implementing the constraint (in the home space that is passed as argument).

.. _tip:m:started:home:

.. mpg-tip:: Space& versus Home

   Actually, when you check the reference documentation, you will see that these functions do not take an argument of type ``Space&`` but of type ``Home`` instead. An object of type ``Home`` actually stores a reference to a space of type ``Space&`` (and a reference of type ``Space&`` is automatically coerced to an object of type ``Home``). Additionally, a ``Home`` object might store other information that is useful for posting propagators and branchers. However, this is nothing you need to be concerned with when modeling with Gecode. Just think that ``Home`` reads as ``Space&``. Using ``Home`` is important when programming propagators and branchers, see :ref:`par:p:started:home`.


The first constraints to be posted enforce that the equation is well formed in that it has no leading zeros:

.. mpg-code:: send more money:no leading zeros


The family of ``rel`` post functions (functions with name ``rel`` overloaded with different argument types) implements simple relation constraints such as equality, inequalities, and disequality (see :ref:`sec:m:integer:rel:int` and `Simple relation constraints over integer variables <https://www.gecode.dev/doc/6.4.0/reference/group__TaskModelIntRelInt.html>`__). The constant ``IRT_NQ`` requests a disequality constraint.

All letters are constrained to take pairwise distinct values by posting a ``distinct`` constraint (also known as ``alldifferent`` constraint):

.. mpg-code:: send more money:all letters distinct


See :ref:`sec:m:integer:distinct` and `Distinct constraints <https://www.gecode.dev/doc/6.4.0/reference/group__TaskModelIntDistinct.html>`__ for more information on the ``distinct`` constraint.

The constraint that :math:`SEND+MORE=MONEY` is posted as a linear equation where the individual letters are scaled to their appropriate decimal positions:

.. mpg-code:: send more money:linear equation


The ``linear`` constraint (which, again, exists in many overloaded variants) posts the linear equation (as instructed by ``IRT_EQ``)

.. math:: \sum_{i=0}^{|\mathtt{c}|-1} \mathtt{c}_i\cdot\mathtt{x}_i = 0

with coefficients ``c``, integer variables ``x``, and right-hand side constant :math:`0` (see :ref:`sec:m:integer:linear` and `Linear constraints over integer variables <https://www.gecode.dev/doc/6.4.0/reference/group__TaskModelIntLI.html>`__). Here, :math:`|\mathtt c|` denotes the size (the number of elements) of the array ``c`` (which can be computed by ``c.size()``). Post functions are designed to be as general as possible, hence the variant of ``linear`` that takes an array of coefficients and an array of integer variables as arguments. Other variants of ``linear`` exist that do not take coefficients (all coefficients are one) or accept an integer variable as the right-hand side instead of an integer constant.

Note that the linear equation could have been expressed simpler by using standard initializer lists as in:

.. mpg-code:: snippet:m-started:tip:m:started:home:code:1
   :direct:


:ref:`sec:m:comfy:expr` demonstrates additional support for posting linear expressions constructed from the usual arithmetic operators such as ``+``, ``-``, and ``*``.

.. _modeling:m-started:posting-branchings:

.. mpg-paragraph:: Posting branchings.

Branchings determine the shape of the search tree. Common branchings take a variable array of the variables to be assigned values during search, a variable selection strategy, and a value selection strategy.

Here, we select the variable with a smallest domain size first (``INT_VAR_SIZE_MIN()``) and assign the smallest value of the selected variable first (``INT_VAL_MIN()``):

.. mpg-code:: send more money:post branching


A *branching* is implemented by a *brancher* (like a constraint is implemented by a propagator). A brancher creates a number of *choices* where each choice is defined by a number of *alternatives*. For example, the brancher posted above will create as many choices as needed to assign all variables in the integer variable array ``l``. Each of the choices is based on the variable selected by the brancher, say :math:`x`, and the value selected by the brancher, say :math:`n`. Then the alternatives of a choice are :math:`x=n` and :math:`x\neq n` and are tried by search in that order.

A space can have several branchers, where the brancher that is posted first is also used first for search. More information on branchings can be found in :ref:`chap:m:branch`.

.. _modeling:m-started:search-support:

.. mpg-paragraph:: Search support.

As mentioned before, a space must implement an additional ``copy()`` function that is capable of returning a fresh copy during search. Search in Gecode is based on a hybrid of *recomputation* and *cloning* (see :ref:`chap:m:search`). Cloning during search relies on the capability of a space to create a copy of itself.

To avoid confusion, by *cloning* we refer to the entire process of creating a clone of a space. By *copying*, we refer to the creation of a copy of a particular object during cloning, for example, a variable or a space.

.. mpg-code:: send more money:search support


The actual ``copy()`` function is straightforward and uses an additional copy constructor. The ``copy()`` function is virtual such that cloning (used on behalf of a search engine) can create a copy of a space even though the space’s exact subclass is not known to cloning.

The obligation of the copy constructor is to invoke the copy constructor of the parent class, and to copy all data structures that contain variables. For ``SendMoreMoney`` this amounts to invoking ``Space(s)`` and updating the variable array. An exception of type `SpaceNotCloned <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1SpaceNotCloned.html>`__ is thrown if the copy constructor of the ``Space`` class is not invoked. Please keep in mind that the copy constructor is run on the copy being created and is passed the space that needs to be copied as argument. Hence, updating the variable array ``l`` in the copy copies the array ``s.l`` from the space ``s`` being cloned (including all variables contained in the array). More on updating variables and variable arrays can be found in :ref:`sec:m:integer:update`.

.. _tip:m:started:cloneallowed:

.. mpg-tip:: What is allowed during cloning

   In the copy constructor used during cloning the only thing that is allowed, is to update variables and other data structures. No new variables can be created and also no new constraints or branchers can be posted.


..

.. _tip:m:started:donotusecopyconstructor:

.. mpg-tip:: Do not use the copy constructor directly

   The copy constructor for a Space is not enough to create a fully initialized clone, and therefore you should not call it directly. The same goes for the copy member function. If you do need to create a clone, the clone member of `Space <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1Space.html>`__ should be used.


.. _modeling:m-started:printing-solutions:

.. mpg-paragraph:: Printing solutions.

Finally, the following prints the variable array ``l``:

.. mpg-code:: send more money:print solution


In a real application, one would use the solution in some other parts of the program. The point is that the space acts as a *closure* for the solution variables: the space maps member names to objects. The space for an actual solution is typically different from the space created initially. This is due to the fact that search for a solution returns a space that has been obtained by constraint propagation and cloning. The space members that refer to the solution variables (the member ``l`` in our example) provide the means to access a solution independent of a particular space.

.. _sec:m:started:search:


.. _modeling:m-started:searching-for-solutions:

Searching for solutions
-----------------------

Let us assume that we want to search for all solutions and that search is controlled by the main function of our program. Search consists of two parts:

- create a model and a search engine for that model; and

- use the search engine to find all solutions.

Hence, our main function looks as follows:

.. mpg-code:: send more money:main function


Creating a model is almost obvious: create an object of the subclass of `Space <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1Space.html>`__ that implements the model. Then, create a search engine (we will be using a search engine `DFS <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1DFS.html>`__ for depth-first search) and initialize it with a model. Search engines are generic with respect to the type of model, implemented as a template in C++. Hence, we use a search engine of type ``DFS<SendMoreMoney>`` for the model ``SendMoreMoney``.

When the engine is initialized, it takes a clone of the model passed to it (``m`` in our example). As the engine takes a clone, several engines can be used without recreating the model. As we are interested in a single engine, we immediately delete the model ``m`` after the search engine has been initialized.

.. mpg-code:: send more money:create model and search engine


..

.. _tip:m:started:status:

.. mpg-tip:: Propagation is explicit



   .. container:: samepage

      A common misconception is that constraint propagation is performed as soon as a space is created or as soon as a constraint is posted. Executing the following code

      .. mpg-code:: snippet:m-started:tip:m:started:status:code:1
         :direct:

   .. container:: samepage

      prints

      .. mpg-code:: snippet:m-started:tip:m:started:status:cmd:1
         :direct:

   That is, only very simple and cheap propagation (nothing but modifying the domain of some variables) has been performed.

   Constraint propagation is *explicit* and must be requested by the ``status()`` member function of a space (the function also returns information about the result of propagation but this is of no concern here). Requesting propagation by

   .. mpg-code:: snippet:m-started:tip:m:started:status:code:2
      :direct:

   prints

   .. mpg-code:: snippet:m-started:tip:m:started:status:cmd:2
      :direct:

A search engine first performs constraint propagation as only spaces that have been propagated can be cloned (so as to not duplicate propagation for the original and for the clone).

The ``DFS<SendMoreMoney>`` search engine has a simple interface: the engine features a ``next()`` function that returns the next solution or ``NULL`` if no more solutions exist. As we are interested in all solutions, a while loop iterates over all solutions that are found by the search engine:

.. mpg-code:: send more money:search and print all solutions


As you can see, a solution is nothing but a model again. A search engine ensures that constraint propagation is performed and that all variables are assigned as described by the branching(s) of the model passed to the search engine. When a search engine returns a model, the responsibility to delete the solution model is with the client of the search engine.

It is straightforward to see how one would search for a single solution instead: replace ``while`` by ``if``. `DFS <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1DFS.html>`__ is but one search engine and the behavior of a search engine can be configured (for example: how cloning or recomputation is used; how search can be interrupted) and it can be queried for statistical information. Search engines are discussed in more detail in :ref:`chap:m:search`.

.. mpg-tip:: Catching Gecode exceptions

   Posting constraints, posting branchings, creating variables, and so on with Gecode might throw exceptions (for example, potential numerical overflow, illegal use of arguments). It is good practice to construct your programs right from the start to catch all these exceptions.


   That is, you should wrap the entire body of the main function but the ``return`` statement into a ``try`` statement as follows:

   .. mpg-code:: snippet:m-started:tip:m:started:status:code:3
      :direct:

   Even though this is good practice, the example programs in this document do not follow this advice, so as to keep the programs more readable.

.. _sec:m:started:run:


.. _modeling:m-started:compiling-linking-and-executing:

Compiling, linking, and executing
---------------------------------

This section assumes that you have built or installed the Gecode version used by this document, namely Gecode 6.4.0. It is a source release, so the usual path is to build Gecode locally and either use it directly from its build tree or install it into a prefix. If you have not done that yet, read :ref:`sec:m:started:obtain` first.

The most convenient way to use an installed Gecode from a new project is through CMake. A minimal ``CMakeLists.txt`` for the ``send-more-money.cpp`` example is:

.. mpg-code:: snippet:m-started:sec:m:started:run:cmd:1
   :direct:


If Gecode has been installed in a non-standard prefix, point CMake to that prefix:

.. mpg-code:: snippet:m-started:sec:m:started:run:cmd:2
   :direct:


The remaining sections show the underlying compiler and linker settings. They are useful when a small example is compiled by hand or when an existing project does not use CMake.

.. _sec:m:started:windows:


.. _modeling:m-started:microsoft-visual-studio:

Microsoft Visual Studio
~~~~~~~~~~~~~~~~~~~~~~~

For Visual Studio, the recommended route is to configure Gecode and the application with CMake. Visual Studio is a multi-configuration generator, so the configuration name is supplied when building:

.. mpg-code:: snippet:m-started:sec:m:started:windows:cmd:1
   :direct:


For an application using the installed tree:

.. mpg-code:: snippet:m-started:sec:m:started:windows:cmd:2
   :direct:


.. _modeling:m-started:commandline:

.. mpg-paragraph:: Commandline.

In the following we assume that you use the Visual Studio Command Prompt. When compiling and linking with ``cl``, you have to take the following into account:

- As Gecode uses exceptions, you have to add ``/EHsc`` as option on the commandline.

- You have to link dynamically against multithreaded libraries. That is, you have to add to the commandline either ``/MD`` (release build) or ``/MDd`` (debug build).

- If you want a release build, you need to switch off assertions by defining ``/DNDEBUG``.

- You should instruct the compiler ``cl`` to search for the Gecode header files by adding ``/I"<dir>\include"`` as an option.

- When using ``cl`` for linking, you should add at the very end of the commandline: ``/link /LIBPATH:"<dir>\lib"``.

- By default, ``cl`` warns if ``this`` is used in an initializer list (Gecode uses this for the initialization of variables and variable arrays). You can suppress the warning by passing ``/wd4355``.

The full command for compiling ``send-more-money.cpp`` as a release build (including optimization with ``/Ox``) is

.. mpg-code:: snippet:m-started:sec:m:started:windows:cmd:3
   :direct:


where the :math:`\backslash` at the end of a line means that the line actually continues on the next line. The following command links the program:

.. mpg-code:: snippet:m-started:sec:m:started:windows:cmd:4
   :direct:


.. _modeling:m-started:integrated-development-environment:

.. mpg-paragraph:: Integrated development environment.

When your Microsoft Visual Studio solution uses Gecode, all necessary settings can be configured in the properties dialog of your solution. We assume that Gecode is installed in ``"<dir>"``.

- You must use dynamic linking against a multithreaded library. That is, either ``/MD`` (release build) or ``/MDd`` (debug build). Depending on whether ``/MD`` or ``/MDd`` is used, release or debug libraries and DLLs will be used automatically.

- As Gecode uses exceptions, you have to enable ``/EHsc`` as option (this is true by default).

- If you want a release build, you have to switch off assertions by defining ``/DNDEBUG`` (this is true by default).

- Configuration Properties, C++, General: set the "Additional Include Directories" to include ``"<dir>\include"`` as the directory containing the Gecode header files.

- Configuration Properties, Linker, General: set the "Additional Library Directories" to ``"<dir>\lib"`` as the path containing the libraries.

..

.. _tip:m:started:cygwin:

.. mpg-tip:: Visual Studio command prompts

   If you compile by hand, start the appropriate Visual Studio developer prompt first, for example *x64 Native Tools Command Prompt for VS 2022*. This sets up ``cl``, ``link``, and the Windows SDK paths. CMake uses the same compiler environment when it is launched from that prompt.


.. _modeling:m-started:apple-mac-os:

Apple Mac OS
~~~~~~~~~~~~

On Mac OS, build Gecode from the source release with CMake and install it into a prefix such as ``/opt/gecode`` or ``/usr/local``. Xcode or the Xcode command line tools provide the compiler.

.. _commandline.-1:

.. _modeling:m-started:commandline-1:

.. mpg-paragraph:: Commandline.

When compiling your code using the ``gcc`` compiler (invoking it as ``g++``), add the include and library directories for the prefix where Gecode has been installed.

The following command compiles and links ``send-more-money.cpp`` as a release build (including optimization):

.. mpg-code:: snippet:m-started:tip:m:started:cygwin:cmd:1
   :direct:


.. _modeling:m-started:xcode:

.. mpg-paragraph:: Xcode.

Xcode projects should normally be generated or configured through CMake. If you manage an Xcode project by hand, add ``<dir>/include`` to the header search paths, ``<dir>/lib`` to the library search paths, and link the Gecode libraries used by the program.

.. _sec:m:started:linux:


.. _modeling:m-started:linux-and-relatives:

Linux and relatives
~~~~~~~~~~~~~~~~~~~

On Linux and similar operating systems, Gecode is installed as a set of libraries and headers. The default installation prefix is ``"/usr/local"``, but a source build can be installed anywhere. For now, assume that Gecode is installed in ``"<dir>"``.

.. _commandline.-2:

.. _modeling:m-started:commandline-2:

.. mpg-paragraph:: Commandline.

To compile your code using the ``gcc`` compiler, you have to add the option ``-I<dir>/include`` so that ``gcc`` can find the header files.

For linking, the path has to be given as ``-L<dir>/lib``, and in addition the individual Gecode libraries must be linked. You always have to link against the support and kernel libraries, using ``-lgecodesupport -lgecodekernel``. For the remaining libraries, the rule of thumb is that if you include a header file ``<gecode/FOO.hh>``, then ``-lgecodeFOO`` must be given as a linker option. For instance, if you use integer variables and include ``gecode/int.hh``, you have to link using ``-lgecodeint``.

Some linkers require the list of libraries to be sorted such that libraries appear before all libraries they depend on. In this case, use the following order (and omit libraries you don’t use):

#. ``-lgecodeflatzinc``

#. ``-lgecodedriver``

#. ``-lgecodegist``

#. ``-lgecodesearch``,

#. ``-lgecodeminimodel``

#. ``-lgecodeset``

#. ``-lgecodefloat``

#. ``-lgecodeint``

#. ``-lgecodekernel``

#. ``-lgecodesupport``

A complete example for compiling and linking the file ``send-more-money.cpp`` is as follows.

.. mpg-code:: snippet:m-started:sec:m:started:linux:cmd:1
   :direct:


The :math:`\backslash` at the end of a line means that the line actually continues on the next line.

In order to run programs that are linked against Gecode, the Gecode libraries must be found on the library path. They either have to be installed in one of the default locations (such as ``/usr/lib``), or the environment variable ``LD_LIBRARY_PATH`` has to be set to include ``<dir>/lib``.

.. _modeling:m-started:eclipse-development-environment:

.. mpg-paragraph:: Eclipse development environment.

If you use the `Eclipse IDE <http://www.eclipse.org/>`__ with the `CDT <http://www.eclipse.org/cdt/>`__ (C/C++ development tools), you have to configure the paths to the Gecode header files and libraries.

In the *Project* menu, select the *Properties* dialog. Under *GCC C++ Compiler*, add ``<dir>/include`` to the *Directories*. Under *GCC C++ Linker*, add ``<dir>/lib`` to the *Library search path*, and the Gecode libraries you have to link against to the *Libraries* field.

In order to run programs that link against Gecode from within the Eclipse CDT, select *Open Run Dialog* from the *Run* menu. Either add a new launch configuration, or modify your existing launch configuration. In the *Environment* tab, add the environment variable ``LD_LIBRARY_PATH=<dir>/lib``.

.. mpg-tip:: Eclipse on Windows and Mac OS

   If you use Eclipse on Windows or Mac OS, the procedure should be similar, except that you do not have to add the environment variable to the launch configuration, and on Windows you do not need to specify the libraries to link against.


.. _sec:m:started:gist:


.. _modeling:m-started:using-gist:

Using Gist
----------

.. mpg-code:: send more money with gist
   :name: fig:m:started:gist
   :caption: Using Gist for Send More Money


When developing a constraint model, the usual outcome of a first modeling attempt is that the model has no solutions or searching for a solution takes too much time to be feasible. What one really needs in these situations is additional insight as to: why does the model have no solutions, why is propagation not sufficient, or why is the branching not appropriate for the problem?

Gecode offers Gist as a graphical and interactive search tool with which you can explore any part of the search tree of a model step by step or automatically and inspect the nodes of the search tree.

Using Gist is absolutely straightforward. :numref:`fig:m:started:gist` shows how Gist is used for the Send More Money problem. As before, a space ``m`` for the model is created. This space is passed to Gist, where Gist is instructed to work in ``dfs`` (depth-first search) mode. The call to ``Gecode::dfs`` terminates only after Gist’s window is closed.

.. figure:: /figures/fig-m-started-gist-shot.svg
   :name: fig:m:started:gist:shot
   :figclass: mpg-figure-wide

   Gist screen shots

:numref:`fig:m:started:gist:shot` shows two screenshots of Gist. The left-hand side shows how Gist starts (with no node of the tree yet explored). The right-hand side shows the fully explored search tree of Send More Money.

Gist is so intuitive that our recommendation is to just play a little with it. If you want to know more about Gist, consult :ref:`chap:m:gist`.

.. mpg-code:: send more money with gist inspection
   :name: fig:m:started:gist-inspect
   :caption: Using Gist for Send More Money with node inspection


One additional feature of Gist that comes in handy when developing constraint models is to inspect nodes of the search tree by double-clicking them. :numref:`fig:m:started:gist-inspect` shows a modified program that instructs Gist to use the ``print()`` function of ``SendMoreMoney`` whenever a node is double-clicked. Note that the print function has been changed to take a standard out-stream to print on as argument.

.. mpg-tip:: Gist scales

   Do not be afraid to use Gist even on large problems. You can expect that per Gigabyte of main memory, Gist can maintain around eight to ten million nodes. And the runtime overhead is low (in our experiments, around 15% compared to the commandline search engine using one thread). Just be sure to increase the display refresh rate for larger trees (see :ref:`sec:m:gist:preferences`).


:ref:`sec:m:comfy:driver` explains how to use a commandline driver that supports to execute the same constraint model with different search engines (for example, ``DFS`` or ``Gist``) by passing options on the commandline.

.. _tip:m:started:link-gist:

.. mpg-tip:: Linking against Gist

   As discussed in :ref:`sec:m:started:run`, when you use Gist on a platform (Linux and relatives) that requires to state all libraries to link against, you also have to link against the library for Gist (that is, for Linux and relatives by adding ``-lgecodegist`` to the compiler options on the commandline).


.. _sec:m:started:search-best:


.. _modeling:m-started:best-solution-search:

Best solution search
--------------------

The last aspect to be discussed in this chapter is how to search for a best solution. We are using a model for Send Most Money as an example: find distinct digits for the letters :math:`S`, :math:`E`, :math:`N`, :math:`D`, :math:`M`, :math:`O`, :math:`T`, and :math:`Y` such that the well-formed equation (no leading zeros) :math:`SEND+MOST=MONEY` holds and that :math:`MONEY` is maximal.

.. mpg-code:: send most money
   :name: fig:m:started:smm-best
   :caption: A Gecode model for Send Most Money finding a best solution


Searching for a best solution requires a best solution search engine and a function that constrains a space to yield a better solution. A Gecode model for Send Most Money is shown in :numref:`fig:m:started:smm-best`. The model differs from Send More Money only by using a different linear equation and the additional ``constrain()`` function.

Assume a new solution, say ``b``, is found during best solution search: on the current search node ``s`` (a space) the member function ``constrain()`` is called and the so-far best solution ``b`` is passed as argument (that is, ``s.constrain(b)`` is executed). The ``constrain()`` member function must add a constraint to ``s`` such that ``s`` can only yield a better solution than ``b`` during search. For Send Most Money, the ``constrain()`` member function is as follows:

.. mpg-code:: send most money:constrain function


First, the integer value of ``money`` in the so-far best solution is computed from the values of the variables. Note that the search engine does not know what model it searches a solution for. The search engine passes a space ``_b`` that the ``constrain`` member function must cast into a ``SendMostMoney`` space. Then the constraint is added that a better solution must yield more money.

.. _modeling:m-started:using-a-best-solution-search-engine:

.. mpg-paragraph:: Using a best solution search engine.

The main function now uses a branch-and-bound search engine rather than a plain depth-first engine:

.. mpg-code:: send most money:main function


The loop that iterates over all solutions found by the branch-and-bound search engine is exactly the same as before. That means that solutions are found and printed with an increasing value of :math:`MONEY`. The best solution is printed last.

The branch-and-bound engine `BAB <https://www.gecode.dev/doc/6.4.0/reference/classGecode_1_1BAB.html>`__ (see also :ref:`sec:m:search:simple`) calls the ``constrain()`` member function defined by the model. Note that every space defines a default ``constrain()`` member function (to keep the design of models simple). If a model does not re-define the ``constrain()`` member function (either directly or indirectly bu inheriting a ``constrain()`` function), the default function will do nothing.

Using Gist for best solution search is straightforward. Instead of using ``Gist::dfs``, one uses ``Gist::bab`` to put Gist into branch-and-bound mode.

In :ref:`sec:m:comfy:cost` it is discussed how a simple ``cost()`` function can be used for best solution search instead of a more general ``constrain()`` function.

.. _sec:m:started:obtain:


.. _modeling:m-started:obtaining-gecode:

Obtaining Gecode
----------------

This section explains how to obtain Gecode. Gecode 6.4.0 is distributed as a source release. Some operating systems also provide Gecode packages, but those packages are maintained by the corresponding distribution and may not match the version used by this document. To get the version described here, download the source release and build it locally.

.. _sec:m:started:install:


.. _modeling:m-started:installing-gecode:

Installing Gecode
~~~~~~~~~~~~~~~~~

The source archive is available from the `Gecode GitHub releases <https://github.com/Gecode/gecode/releases>`__. Download the archive for Gecode 6.4.0 and unpack it into a working directory. The commands in the next section assume that the source directory is called ``gecode-6.4.0``.

.. _sec:m:started:install:windows:


.. _modeling:m-started:installing-gecode-on-windows:

Installing Gecode on Windows
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Install Visual Studio 2022 with the C++ toolchain and CMake. If you need MPFR support, using the source release with CMake and vcpkg is the most direct path.

.. _sec:m:started:install:macos:


.. _modeling:m-started:installing-gecode-on-apple-mac-os:

Installing Gecode on Apple Mac OS
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Install Xcode or the Xcode command line tools. CMake can then use the Apple compiler directly. Optional components require their own dependencies; Gist, for example, requires Qt.

.. _modeling:m-started:installing-gecode-on-linux-and-relatives:

Installing Gecode on Linux and relatives
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The Debian and Ubuntu Linux distributions come with pre-compiled packages for Gecode. These packages (and all the packages they depend on) can be installed with the usual package management tools. These packages can be useful for quick experiments. They are not the Gecode 6.4.0 release, and they should not be used when exact version matching matters.

.. _sec:m:started:compile:


.. _modeling:m-started:compiling-gecode:

Compiling Gecode
~~~~~~~~~~~~~~~~

Gecode can be built on recent versions of Windows, Linux, and Mac OS. The source code is available from the `Gecode GitHub releases <https://github.com/Gecode/gecode/releases>`__.

.. _modeling:m-started:prerequisites:

.. mpg-paragraph:: Prerequisites.

In order to compile Gecode with the CMake build, you need CMake 3.21 or newer, a C++17-capable compiler, and ``uv`` on the search path. Optional modules have optional dependencies: MPFR for trigonometric and transcendental float constraints, and Qt5 or Qt6 for Gist.

We currently support:

- Microsoft Visual C++ compilers for Windows. Microsoft Visual Studio Community is available free of charge from `Microsoft <https://visualstudio.microsoft.com/free-developer-offers/>`__.

- GNU Compiler Collection (gcc) for Unix flavors such as Linux and Mac OS. The GNU gcc is open source software and available from `the GCC home page <http://gcc.gnu.org/>`__. It is included in many Linux distributions.

- The Apple compiler shipped with Xcode and the Xcode command line tools.

.. _modeling:m-started:configuring-the-sources:

.. mpg-paragraph:: Configuring the sources.

For a single-configuration generator such as Ninja or Unix Makefiles, configure a release build as follows:

.. mpg-code:: snippet:m-started:sec:m:started:compile:cmd:1
   :direct:


For a multi-configuration generator such as Visual Studio or Xcode, omit ``CMAKE_BUILD_TYPE`` and choose the configuration when building:

.. mpg-code:: snippet:m-started:sec:m:started:compile:cmd:2
   :direct:


.. _modeling:m-started:compiling-the-sources:

.. mpg-paragraph:: Compiling the sources.

After configuration succeeds, build Gecode with:

.. mpg-code:: snippet:m-started:sec:m:started:compile:cmd:3
   :direct:


With single-configuration generators, the ``--config Release`` argument is harmless and may also be omitted.

.. _modeling:m-started:running-the-test-suite:

.. mpg-paragraph:: Running the test suite.

The CMake build defines a ``check`` target when tests are enabled:

.. mpg-code:: snippet:m-started:sec:m:started:compile:cmd:4
   :direct:


.. _modeling:m-started:installation:

.. mpg-paragraph:: Installation.

After compilation succeeds, you can install the Gecode library and all header files necessary for compiling against it by invoking

.. mpg-code:: snippet:m-started:sec:m:started:compile:cmd:5
   :direct:


..

.. _tip:m:started:install:ld:

.. mpg-tip:: Do not forget the library path

   In order to run programs that are linked against Gecode (such as the Gecode examples), the libraries must be found on the library path. See :ref:`sec:m:started:linux` for details.


.. _modeling:m-started:running-the-examples:

.. mpg-paragraph:: Running the examples.

After compiling the examples, they can be run directly from the build tree. For instance, try the Golomb Rulers Problem:

.. mpg-code:: snippet:m-started:tip:m:started:install:ld:cmd:1
   :direct:


or, when using a multi-configuration generator on Windows:

.. mpg-code:: snippet:m-started:tip:m:started:install:ld:cmd:2
   :direct:


On some platforms, you may need to set environment variables like ``LD_LIBRARY_PATH`` (Linux) or ``DYLD_LIBRARY_PATH`` (Mac OS) to the toplevel compile directory or the installation directory (where the dynamic libraries are placed after compilation).

.. _modeling:m-started:compilation-with-gist:

.. mpg-paragraph:: Compilation with Gist.

The Gecode Interactive Search Tool (Gist) is a graphical search engine for Gecode, built on top of Qt. CMake looks for Qt5 or Qt6 when Gist is enabled. If Qt is not found, Gist is disabled automatically. To make this choice explicit, configure with:

.. mpg-code:: snippet:m-started:tip:m:started:install:ld:cmd:3
   :direct:


..

.. _tip:m:started:samecompiler:

.. mpg-tip:: Compatible compilers and installations for Gecode and Qt

   Please make sure that the compiler with which Qt has been compiled is compatible with the compiler you intend to use for Gecode (most likely, the requirement is that both packages must be compiled with the very same compiler).


   In particular, make sure that this is true when you install Qt through a package manager. On Windows, vcpkg is often the simplest way to keep Qt and the Visual Studio compiler in the same toolchain.

.. _par:m:started:mpfr:


.. _modeling:m-started:compilation-with-support-for-trigonometric-and-transcendental-float-constraints:

.. mpg-paragraph:: Compilation with support for trigonometric and transcendental float constraints.

Trigonometric and transcendental float constraints require MPFR (see also :ref:`m:float:mpfr`). CMake searches for MPFR when float support with MPFR is enabled. Use ``CMAKE_PREFIX_PATH``, ``MPFR_ROOT``, or a toolchain file to point CMake to a non-standard MPFR installation.

.. _sec:m:started:compileadvanced:


.. _modeling:m-started:advanced-configuration-and-compilation:

Advanced configuration and compilation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If the instructions from the previous section do not work for your system, the following examples show common CMake options for configuring Gecode.

.. _modeling:m-started:example-configurations:

Example configurations
^^^^^^^^^^^^^^^^^^^^^^

To compile only the Gecode library **without examples**, use

.. mpg-code:: snippet:m-started:sec:m:started:compileadvanced:cmd:1
   :direct:


To compile using a different compiler and install under ``/opt/gecode``, use

.. mpg-code:: snippet:m-started:sec:m:started:compileadvanced:cmd:2
   :direct:


To compile a **debug build**, use

.. mpg-code:: snippet:m-started:sec:m:started:compileadvanced:cmd:3
   :direct:


To disable an optional module, use the corresponding ``GECODE_ENABLE_…`` option. For example, to build without Gist:

.. mpg-code:: snippet:m-started:sec:m:started:compileadvanced:cmd:4
   :direct:


On Mac OS, universal binaries are configured through the standard CMake architecture setting:

.. mpg-code:: snippet:m-started:sec:m:started:compileadvanced:cmd:5
   :direct:


.. _par:s:started:allocator:


.. _modeling:m-started:disabling-the-default-memory-allocator:

.. mpg-paragraph:: Disabling the default memory allocator.

By default, Gecode uses a default memory allocator based on the C standard library functions ``malloc()`` and ``free()``. This default allocator can be disabled by

.. mpg-code:: snippet:m-started:par:s:started:allocator:cmd:1
   :direct:


If the default allocator is disabled, one must supply the implementation of an allocator, this is explained in :ref:`par:p:memory:allocator`.

.. _modeling:m-started:passing-options-for-compilation:

.. mpg-paragraph:: Passing options for compilation.

Additional options for compilation can be passed through the standard CMake compiler flags. For example:

.. mpg-code:: snippet:m-started:par:s:started:allocator:cmd:2
   :direct:


.. _modeling:m-started:compiling-in-a-separate-directory:

.. mpg-paragraph:: Compiling in a separate directory.

The Gecode library should normally be built in a separate build directory. Assume that the sources can be found in directory ``$GSOURCEDIR``. Configure the build directory with:

.. mpg-code:: snippet:m-started:par:s:started:allocator:cmd:3
   :direct:


This keeps generated files out of the source tree.

.. _modeling:m-started:dependency-management:

.. mpg-paragraph:: Dependency management.

CMake tracks source dependencies for normal builds. If you change the variable implementation specifications and want to regenerate the checked-in generated headers, configure with ``GECODE_REGENERATE_VARIMP=ON``. This requires ``uv`` on the search path.

.. _modeling:m-started:compiling-for-unsupported-platforms:

.. mpg-paragraph:: Compiling for unsupported platforms.

For a platform not mentioned here, start with the closest native CMake generator and toolchain file for that platform. The CMake settings should describe the compiler, target system, SDK, and architecture.

.. _modeling:m-started:useful-makefile-targets:

Useful Makefile targets
^^^^^^^^^^^^^^^^^^^^^^^

The CMake build supports the following useful targets:

- ``all`` compiles the enabled parts of the library and the examples if examples are enabled.

- ``check`` builds and runs the test suite when tests are enabled.

- ``install`` installs libraries, headers, tools, and CMake package files into the selected prefix.

- ``clean`` removes files generated by the current build configuration.

.. mpg-covered: caption:docs/src/chapters/modeling/m-started.tex.in:56:fig:m:started:smm
.. mpg-covered: literal-projection:docs/src/chapters/modeling/m-started.tex.in:57:send more money
.. mpg-covered: literal-projection:docs/src/chapters/modeling/m-started.tex.in:125:send more money:no leading zeros
.. mpg-covered: literal-projection:docs/src/chapters/modeling/m-started.tex.in:137:send more money:all letters distinct
.. mpg-covered: literal-projection:docs/src/chapters/modeling/m-started.tex.in:145:send more money:linear equation
.. mpg-covered: literal-projection:docs/src/chapters/modeling/m-started.tex.in:193:send more money:post branching
.. mpg-covered: literal-projection:docs/src/chapters/modeling/m-started.tex.in:223:send more money:search support
.. mpg-covered: literal-projection:docs/src/chapters/modeling/m-started.tex.in:268:send more money:print solution
.. mpg-covered: literal-projection:docs/src/chapters/modeling/m-started.tex.in:293:send more money:main function
.. mpg-covered: literal-projection:docs/src/chapters/modeling/m-started.tex.in:310:send more money:create model and search engine
.. mpg-covered: literal-projection:docs/src/chapters/modeling/m-started.tex.in:355:send more money:search and print all solutions
.. mpg-covered: tip:docs/src/chapters/modeling/m-started.tex.in:372:unlabeled-tip@docs/src/chapters/modeling/m-started.tex.in:372
.. mpg-covered: tip:docs/src/chapters/modeling/m-started.tex.in:621:unlabeled-tip@docs/src/chapters/modeling/m-started.tex.in:621
.. mpg-covered: caption:docs/src/chapters/modeling/m-started.tex.in:632:fig:m:started:gist
.. mpg-covered: literal-projection:docs/src/chapters/modeling/m-started.tex.in:633:send more money with gist
.. mpg-covered: caption:docs/src/chapters/modeling/m-started.tex.in:658:fig:m:started:gist:shot
.. mpg-covered: caption:docs/src/chapters/modeling/m-started.tex.in:678:fig:m:started:gist-inspect
.. mpg-covered: literal-projection:docs/src/chapters/modeling/m-started.tex.in:679:send more money with gist inspection
.. mpg-covered: tip:docs/src/chapters/modeling/m-started.tex.in:692:unlabeled-tip@docs/src/chapters/modeling/m-started.tex.in:692
.. mpg-covered: caption:docs/src/chapters/modeling/m-started.tex.in:725:fig:m:started:smm-best
.. mpg-covered: literal-projection:docs/src/chapters/modeling/m-started.tex.in:726:send most money
.. mpg-covered: literal-projection:docs/src/chapters/modeling/m-started.tex.in:746:send most money:constrain function
.. mpg-covered: literal-projection:docs/src/chapters/modeling/m-started.tex.in:759:send most money:main function
