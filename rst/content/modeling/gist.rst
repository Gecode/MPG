.. _chap:m:gist:


.. _modeling:m-gist:gist:

Gist
====

The Graphical Interactive Search Tool, Gist, provides user-controlled search, search tree visualization, and inspection of arbitrary nodes in the search tree. Gist can be helpful when experimenting with different branching strategies, with different models for the same problem (for instance adding redundant constraints), or with propagation strength (for instance bounds versus domain propagation). It gives you direct feedback how the search tree looks like, if your branching heuristic works, or where propagation is weaker than you expected.

.. _modeling:m-gist:overview:

.. mpg-paragraph:: Overview.

How the search tree of a problem is used as the central metaphor in Gist is sketched in :ref:`sec:m:gist:tree`. :ref:`sec:m:gist:invoke` explains how to invoke Gist, whereas :ref:`sec:m:gist:use` explains how to use Gist.

.. important::

   Do not forget to add

   .. mpg-code:: snippet:m-gist:chap:m:gist:code:1
      :direct:

   to your program when you want to use Gist.

.. _sec:m:gist:tree:


.. _modeling:m-gist:the-search-tree:

The search tree
---------------

.. figure:: /figures/fig-m-gist-smm_full_tree_clean.svg
   :name: fig:m:gist:smm_full_tree_clean
   :figclass: mpg-figure-narrow

   A search tree

The central metaphor in Gist is the *search tree*. Each node in the tree represents a fixpoint of propagation (that is, an invocation of ``status()``, see :ref:`tip:m:started:status`). Inner nodes stand for *choices* (fixpoints with a subsequent brancher), while leaf nodes correspond to *failure* (dead ends in the search) or *solutions* of the problem. :numref:`fig:m:gist:smm_full_tree_clean` shows a search tree as drawn by Gist. The inner nodes (blue circles) are choices, the red square leaf nodes are failures, and the green diamond leaf node is a solution.

Conceptually, every node in the tree contains a corresponding space, which the user can access in order to inspect the node. Internally, Gist does not store all these spaces, but recomputes them on demand. That way, Gist can handle very large search trees (with millions of nodes) efficiently.

.. _sec:m:gist:invoke:


.. _modeling:m-gist:invoking-gist:

Invoking Gist
-------------

Gist is implemented using the `Qt <http://www.qtsoftware.com/>`__ application framework. It can be invoked either as a standalone component, or as part of a bigger Qt-based application.

The screenshots in this chapter show Gist running on Mac OS X, but the functionality, the menus and the keyboard shortcuts are the same on all platforms (with small exceptions that will be mentioned later).

.. _modeling:m-gist:standalone-use:

Standalone use
~~~~~~~~~~~~~~

.. figure:: /figures/fig-m-gist-gist_smm.svg
   :name: fig:m:gist:gist_smm
   :figclass: mpg-figure-wide

   Gist, solving the Send More Money problem

When used as a standalone component, invoking Gist merely amounts to calling

.. mpg-code:: snippet:m-gist:fig:m:gist:gist_smm:code:1
   :direct:


where ``m`` is a pointer to the space that contains the model to be solved. This call opens a new instance of Gist, with the root node initialized with ``m``. :numref:`fig:m:gist:gist_smm` (left) shows Gist initialized with the Send More Money puzzle from :ref:`chap:m:started`.

If you want to solve an optimization problem using branch-and-bound search, you can invoke Gist with optimization turned on:

.. mpg-code:: snippet:m-gist:fig:m:gist:gist_smm:code:2
   :direct:


.. _modeling:m-gist:use-as-a-qt-widget:

Use as a Qt widget
~~~~~~~~~~~~~~~~~~

If you are developing an application with a graphical user interface using the Qt toolkit, you can embed Gist as a widget. Either use :api:`Gist::GistMainWindow`, which gives you an independent widget that inherits from ``QMainWindow``, or directly embed the :api:`Gist::Gist` widget into your own widgets. You have to include the files ``gecode/gist/mainwindow.hh`` for the independent widget, or ``gecode/gist/qtgist.hh`` for the widget you can embed.

Apart from the integration into your own application, the advantage over the standalone approach is that you get access to Gist’s *signals* and *slots*. For example, you can use more than one inspector, or you can control the search programatically instead of by user input. The details of this are beyond the scope of this document, please refer to the reference documentation of the corresponding classes for more information, and have a look at the directory ``gecode/gist/standalone-example`` in the Gecode source distribution.

.. _sec:m:gist:use:


.. _modeling:m-gist:using-gist:

Using Gist
----------

This section gives an overview of the functionality available in Gist. Most of Gist is intuitive to use, and the easiest way of learning how to use it is to start one of the examples that come with Gecode using the ``-mode gist`` commandline option, and then play around.

.. _modeling:m-gist:automatic-search:

Automatic search
~~~~~~~~~~~~~~~~

When you invoke Gist, it initializes the root node of the search tree, as seen in :numref:`fig:m:gist:gist_smm`. Any node that has not yet been explored by the search is drawn as a white circle, indicating that it is not yet known whether this node is in fact a choice, failure, or solution. White nodes are called *open*.

Obviously, the first thing a user will then want to do is to search for a solution of the given problem. Gist provides an automatic first-solution and all-solution depth-first search engine. It can be activated from the *Search* menu:

|image|

If you click *All solutions* (or alternatively press the *A* key), Gist will explore the entire tree. The result appears in :numref:`fig:m:gist:gist_smm` (right). Depending on the preferences, Gist may collapse subtrees that contain only failed nodes (such as the rightmost subtree in the figure) into big red triangles.

The search engines always only explore the subtree under the *currently selected node*, which is marked by a shadow. For example, the root node is selected after initialization, and the rightmost choice node is selected in :numref:`fig:m:gist:gist_smm` (right). A single click selects a node, and there is always exactly one selected node.

.. _modeling:m-gist:stopping-search-after-exhausting-a-branching:

.. mpg-paragraph:: Stopping search after exhausting a branching.

If you want to learn more about how your branchings affect the shape of the search tree, you can add *stop branchings* to your problem using the ``Gist::stopBranch()`` function. This will install a brancher that does not modify the search tree (in fact, it simply inserts a single unary choice), but Gist will recognize the brancher and halt exploration. A special node (shaped like a stop-sign) marks the position in the tree where the stop brancher was active. You can toggle whether Gist continues exploration beyond the brancher using the options in the *Node* menu. Obviously, this is most useful if the call to ``stopBranch`` is placed *between* calls to other branchings.

.. _modeling:m-gist:interactive-search:

Interactive search
~~~~~~~~~~~~~~~~~~

As an alternative to automatic search, you can also explore the search tree interactively. Just select an arbitrary open (white) node and choose *Inspect* from the *Node-Inspect* menu (or press the *Return* key).

You can navigate in the tree using the arrow keys (or the corresponding options from the *Node* menu). Automatic and interactive search can be freely mixed. In order to focus on interesting parts of the search tree, you can hide subtrees using the *Hide/unhide* option, or hide all subtrees below the selected node that are completely failed. The option *Unhide all* expands all hidden subtrees below the current node again. The red triangle in :numref:`fig:m:gist:hidden` is a hidden subtree.

If you want to start over, the *Search* menu provides an option to reset Gist.

.. figure:: /figures/fig-m-gist-hidden.svg
   :name: fig:m:gist:hidden
   :figclass: mpg-figure-compact

   A hidden subtree in Gist

.. _modeling:m-gist:bookmarks:

.. mpg-paragraph:: Bookmarks.

The *Node* menu has a submenu *Bookmarks*, where you can collect nodes for quick access. You can set a bookmark for the currently selected node by chosing *Add/remove bookmark* from the submenue, or by pressing *Shift+B*. You can then enter a name for the bookmark (or leave it empty, then the bookmark will get a number). Chosing *Add/remove bookmark* for an already bookmarked node removes the bookmark. Bookmarked nodes are drawn with a small black circle. Selecting a bookmark moves you directly to the corresponding node.

.. _modeling:m-gist:branch-and-bound-search:

Branch-and-bound search
~~~~~~~~~~~~~~~~~~~~~~~

If Gist has been invoked in branch-and-bound mode, it prunes the search tree with each new solution that is found. Branch-and-bound works with any order of exploration, so you can for instance explore interactively, or start automatic search for just a subtree.

The last solution that was found, which in branch-and-bound is always the best solution known so far, is displayed in orange instead of green.

.. _sec:m:gist:inspecting_nodes:

.. _sec:m:gist:print:


.. _modeling:m-gist:inspecting-and-comparing-nodes:

Inspecting and comparing nodes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. figure:: /figures/fig-m-gist-node_menu.svg
   :name: fig:m:gist:node_menu
   :figclass: mpg-figure-medium

   The *Node* menu

Of course just looking at the shape of the tree is most of the time not very enlightening by itself. We want to see the content of the nodes. For this, you can display information about the *alternatives* in the tree (provided by print functions, see :ref:`sec:m:branch:print`), and add *inspectors* and *comparators* to Gist. Inspectors and comparators can be called on solution, choice, or failure nodes (but obviously not on open nodes).

.. _modeling:m-gist:displaying-branching-information:

.. mpg-paragraph:: Displaying branching information.

The *Node* menu (:numref:`fig:m:gist:node_menu`) has two options for displaying information about branches in the tree. Choosing *Label/clear branches* will add information on all branches in the subtree below the currently selected node (or clear that information if it is already present). *Label/clear path* adds that information on the path from the current node to the root. :numref:`fig:m:gist:branches` shows branching information for the Send More Money problem.

.. figure:: /figures/fig-m-gist-branches.svg
   :name: fig:m:gist:branches
   :figclass: mpg-figure-compact

   Branch information in Gist

Gist uses print functions provided by the branchers of a space. For variable-value branchers as described in :ref:`chap:m:branch`, the information displayed for the branches can be supplied by the user, see :ref:`sec:m:branch:print` for details. Also other branchers can define which information is printed for a branch, see :ref:`par:b:started:print`.

.. _modeling:m-gist:invoking-inspectors-and-comparators:

.. mpg-paragraph:: Invoking inspectors and comparators.

The *Node* menu (:numref:`fig:m:gist:node_menu`) provides several options for inspecting and comparing nodes. If you choose *Inspect* from the *Inspect* submenu (or simply press *Return*), all double-click inspectors that are active in the *Tools* menu (see below) will be invoked for the currently selected node. You can also invoke a particular inspector by choosing it from th *Inspect* menu or typing its shortcut (the first nine inspectors get the shortcuts 0–9).

If you choose an inspector from the *Inspect before fixpoint* menu instead, the state of the node after branching but before fixpoint propagation is shown.

When choosing the *Compare* option, the mouse cursor turns into a crosshair, and clicking on another node will invoke the comparators that have been activated in the *Tools* menu. Again, *Compare before fixpoint* considers the state of the second node after branching but before fixpoint propagation. This is especially useful to find out what the branching does at a particular node: Select a node, choose *Compare before fixpoint*, and click on the child node you are interested in. The comparison will show you exactly how the branching has changed the variable domains.

.. _modeling:m-gist:choosing-the-active-inspectors-and-comparators:

.. mpg-paragraph:: Choosing the active inspectors and comparators.

Gist distinguishes between three groups of inspectors, and the group of comparators, which can be chosen from the *Tools* menu (:numref:`fig:m:gist:tools_menu`):

- *Move inspectors* are called whenever the user moves to a different node.

- *Solution inspectors* are called for each new solution that is found.

- *Double-click inspectors* are called when the user explicitly inspects a node, for instance by choosing *Inspect* from the *Node* menu or by double-clicking.

- *Comparators* are called when the user chooses *Compare* or *Compare before fixpoint*, and then clicks on another node to compare the currently selected one to.

.. figure:: /figures/fig-m-gist-tools_menu.svg
   :name: fig:m:gist:tools_menu
   :figclass: mpg-figure-wide

   The *Tools* menu

.. _modeling:m-gist:the-printing-inspector:

.. mpg-paragraph:: The printing inspector.

.. figure:: /figures/fig-m-gist-inspect.svg
   :name: fig:m:gist:inspect
   :figclass: mpg-figure-medium

   Inspecting a solution in Gist

The simplest way to add an inspector to your model is to use the :api:`Gist::Print` inspector, as demonstrated in :ref:`sec:m:started:gist`. :numref:`fig:m:gist:inspect` shows the :api:`Gist::Print` inspector after double-clicking the solution of the Send More Money problem.

.. _modeling:m-gist:implementing-inspectors:

.. mpg-paragraph:: Implementing inspectors.

An inspector is an object that inherits from the abstract base class :api:`Gist::Inspector`. The abstract base class declares a virtual member function, ``inspect(const Space& s)``, which is called when one of the events described above happens. The space that is passed as an argument corresponds to the inspected node in the tree. The inspector is free to perform any ``const`` operation on the space.

.. _modeling:m-gist:the-variable-comparator:

.. mpg-paragraph:: The variable comparator.

Similar to the printing inspector, there is a predefined comparator :api:`Gist::VarComparator` that can be easily added to scripts. It requires the script to implement a member function ``compare()`` in which it outputs the result of comparing itself to another space. :numref:`fig:m:gist:gist-compare` shows how to add comparison to the example from :ref:`sec:m:started:gist`. It uses a convenience member function from the class :api:`Gist::Comparator` that produces a string representation of the differences between two variable arrays.

.. mpg-code:: send more money with gist comparison
   :name: fig:m:gist:gist-compare
   :caption: Using Gist for Send More Money with node comparison


.. _modeling:m-gist:implementing-comparators:

.. mpg-paragraph:: Implementing comparators.

A comparator inherits from :api:`Gist::Comparator` and implements at least its ``compare(const Space& s0, const Space& s1)`` member function. This function is called when the currently selected node with space ``s0`` is compared to the node with space ``s1``. As for inspectors, a comparator can perform any ``const`` operation on these two spaces.

.. _modeling:m-gist:subtree-statistics:

.. mpg-paragraph:: Subtree statistics.

The *Node* menu provides an option *Node statistics*, which when clicked opens a small window that displays statistics of the subtree rooted at the currently selected node, as shown in :numref:`fig:m:gist:subtreestats`. The statistics include the depth of the current node (the upper right number in :numref:`fig:m:gist:subtreestats`), the maximum depth of the subtree (the lower right number), and how many of the different node types the subtree contains (the numbers at the small nodes). The information is automatically updated when you select a different node.

.. figure:: /figures/fig-m-gist-subtreestats.svg
   :name: fig:m:gist:subtreestats
   :figclass: mpg-figure-compact

   Node statistics

.. _modeling:m-gist:zooming-centering-exporting-printing:

Zooming, centering, exporting, printing
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Here is some functionality you may have already found during your experiments with Gist.

.. _modeling:m-gist:mouse-wheel-zoom:

.. mpg-paragraph:: Mouse wheel zoom.

You probably noticed that the slider right of the search tree lets you zoom in and out. Another way of zooming is to hold *Shift* while using the mouse wheel. It will zoom in and out keeping the area under the mouse cursor visible.

.. _modeling:m-gist:zoom-and-center:

.. mpg-paragraph:: Zoom and center.

In addition to manual zooming, Gist provides automatic options. The button with the magnifying glass icon above the zoom slider toggles the auto-zoom feature, which always zooms the tree such that as much of it as possible is visible in the window. During auto-zoom, the manual zoom is disabled. Instead of auto-zoom, you can also select *Zoom to fit* from the *Node* menu (or press *Z*) in order to adjust the zoom so that the current tree fits. When working with large trees, it is sometimes useful to scroll back to the currently selected node by choosing *Center current node* from the *Node* menu or pressing *C*.

.. _modeling:m-gist:exporting-and-printing:

.. mpg-paragraph:: Exporting and printing.

The *File* menu provides options for exporting the current search tree as a PDF file or printing it. If you want to export a single subtree, select *Export subtree PDF* from the *Node* menu. The tree is exported or printed as seen, including hidden nodes.

.. _sec:m:gist:preferences:


.. _modeling:m-gist:options-and-preferences:

Options and preferences
~~~~~~~~~~~~~~~~~~~~~~~

When invoking Gist, you can pass it an optional argument of type :api:`Gist::Options`. This options class inherits from the standard search options discussed in :ref:`sec:m:search:options`, but adds a ``class`` with two member functions, ``inspect.click()`` and ``inspect.solution()``, that you can use to pass inspectors to Gist.

The two options for recomputation, ``c_d`` and ``a_d``, as well as the ``clone`` option of :api:`Search::Options` are honored by Gist; the remaining options are ignored.

During execution, Gist can be configured using the *Preferences* dialog, available from the program menu on Mac OS or the *File* menu on Windows and Linux.

.. figure:: /figures/fig-m-gist-preferences.svg
   :name: fig:m:gist:preferences
   :figclass: mpg-figure-medium

   Gist preferences

The drawing preferences (:numref:`fig:m:gist:preferences`, left) let you specify whether failed subtrees are hidden automatically during search, and whether the auto-zoom and smooth scrolling features are enabled at start-up. Furthermore, you can set the refresh interval – this is the number of nodes that are explored before the tree is redrawn. If you set this to a large number, search will be faster, but you get less visual feedback. You can enable slow search, which will explore only around three nodes per second, useful for demonstrating how search proceeds. Finally, enabling the “Move cursor during search” option means that the move inspectors will be called for every single node during search. Again, this is great for demonstration and debugging purposes, but it slows down the search considerably. Drawing preferences (except for the slow-down and cursor moving options) are remembered between sessions and across different invocations of Gist.

The search preferences are exactly the parameters you can pass using the :api:`Gist::Options` class. In addition, you can switch on the display of where Gist actually stores spaces in the tree, as shown in :numref:`fig:m:gist:copies`. A small red circle indicates a clone used for recomputation, while a small yellow circle shows that the node has an active space used for exploration (a so-called *working clone*).

The recomputation parameters are not remembered between sessions.

.. figure:: /figures/fig-m-gist-copies.svg
   :name: fig:m:gist:copies
   :figclass: mpg-figure-compact

   Displaying where Gist stores spaces in the tree

.. |image| image:: /figures/screenshots/gist_menu_search.png
