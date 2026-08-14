.. _chap:c:crossword:

Crossword puzzle
================


This chapter studies solving crossword puzzles and presents a simple model using nothing but ``distinct`` and ``element`` constraints.

The simple model for this classical problem is shown to work quite well compared to a constraint-based approach to solving crossword puzzles using a dedicated problem-specific constraint solver  :cite:p:`DBLP:conf/cp/AnbulaganB08` . This underlines that an efficient general-purpose constraint programming system actually can go a long way.

.. _sec:c:crossword:problem:

Problem
-------


.. mpg-figure:: A crossword puzzle grid
   :name: fig:c:crossword:grid
   :class: mpg-figure-compact

   .. only:: html

      .. image:: /figures/fig-c-crossword-grid.svg
         :alt: A crossword puzzle grid

   .. only:: latex

      .. image:: /figures/pdf/fig-c-crossword-grid.pdf
         :alt: A crossword puzzle grid


To solve a crossword puzzle problem, a crossword grid (see :numref:`fig:c:crossword:grid` for an example) must be filled with words (from a predefined dictionary) extending both in horizontal and vertical directions such that:

- If words cross at a field of the grid, the words’ letters at the crossing field are the same.

- No word is used twice.

Words use lowercase letters only and extend as far as they can. That is, the beginning (and the end) of a word must either be adjacent to a black field on the grid or must be a field on the grid’s border.


.. mpg-figure:: Solution for crossword puzzle grid from :numref:`fig:c:crossword:grid`
   :name: fig:c:crossword:solution
   :class: mpg-figure-compact

   .. only:: html

      .. image:: /figures/fig-c-crossword-solution.svg
         :alt: Solution for the example crossword puzzle grid

   .. only:: latex

      .. image:: /figures/pdf/fig-c-crossword-solution.pdf
         :alt: Solution for the example crossword puzzle grid


An example solution for the grid from :numref:`fig:c:crossword:grid` is shown in :numref:`fig:c:crossword:solution` .

.. _sec:c:crossword:model:

Model
-----


The model uses two sets of variables:

- The model uses for each word on the grid a *word variable*. A value for a word variable is a *dictionary index* defining the index of the word chosen from the dictionary of all words.

  The script for the model uses the word variables only as temporary variables for posting constraints. To simplify posting constraints, words are processed in groups of words of the same length. In particular, dictionary indices are also defined with respect to words of the same length in the dictionary.

- For each field on the grid, the model uses a *letter variable*. The values for a letter variable are either ``0`` (for a black field on the grid) or a character code between ``’a’`` and ``’z’`` for lowercase letters.

Given the sets of variables, the constraints for the model are straightforward:

- All word variables for words of the same length must be ``distinct``. Only word variables for words of the same length need to be constrained to be distinct, as words of different length are distinct by definition.

- Assume that :math:`w` is a word variable for a word of length :math:`n` on the grid and :math:`x_0,\ldots, x_{n-1}` are the letter variables that correspond to the word on the grid. Assume further that :math:`0\leq p<n` and that an array :math:`\mathtt{w2l}` (for ``w``\ ord to ``l``\ etter) maps the dictionary indices of all words of length :math:`n` to their :math:`p`-th letter. Then, the letter variable :math:`x_p` can be linked to the word variable :math:`w` by posting the constraint that :math:`\mathtt{w2l}_w=x_p` (this is an ``element`` constraint).


.. _fig:c:crossword:script:

.. mpg-code:: crossword
   :caption: Crossword script
   :download:


An outline for the script implementing the crossword puzzle is shown in :ref:`fig:c:crossword:script` . The script stores the width ``w`` and the height ``h`` of the grid and an integer variable array ``letters`` for the letter variables (including the black fields). The values for ``letters`` range from ``’a’`` to ``’z’`` (black fields are discussed below).

.. _fig:c:crossword:spec:

Grid and words specification.
'''''''''''''''''''''''''''''

.. mpg-code:: crossword:grid specification
   :caption: Grid and words specification

.. mpg-code:: crossword:words specification
   :direct:


The specification for the ``grid`` used in this case study (see :ref:`sec:c:crossword:info` for more information) and the word dictionary are shown in :ref:`fig:c:crossword:spec` . The grid specification contains information about the dimension of the grid (as used in :ref:`fig:c:crossword:script` ), the number and coordinates of black fields on the grid, and the start coordinates of words and their direction on the grid for each word length permitted by the grid.

For each word length :math:`l`, the array :math:`\mathtt{n_words}_l` defines how many words of length :math:`l` exist in the dictionary of words. That is, for a word length :math:`l`, the set of dictionary indices is :math:`\{0,\ldots,\mathtt{n_words}_l-1\}`. The array ``words`` provides access to the letters of a word of some given length with a given dictionary index. That is, for a given word length :math:`l` and for a position in the word :math:`p` with :math:`0\leq p<l`, :math:`\mathtt{words}_{l,i,p}` (or :math:`\mathtt{words}[l][i][p]` in C++) is the :math:`p`-th letter of the word with dictionary index :math:`i` among all words of length :math:`l` (where :math:`0\leq
i<\mathtt{n_words}_l`) in the dictionary. The dictionary of words just contains words of length at most eight as this is sufficient for the example grid used in this case study.

The word list is based on SCOWL-55 (Spell Checking Oriented Word Lists) truncated to words of length at most eight, see `wordlist.sourceforge.net <http://wordlist.sourceforge.net/>`__ . Please check the source file available from :ref:`fig:c:crossword:script` for copyright information.

.. _case-studies:crossword:grid-initialization:

Grid initialization.
''''''''''''''''''''

The grid specification is accessed by the pointer ``g`` (with the width and height part already skipped). The matrix ``ml`` (see :ref:`sec:m:minimodel:matrix` ) supports access to the ``letters`` as a matrix:


.. mpg-code:: crossword:set up
   :direct:


The black fields of the grid are initialized by storing a variable ``black`` at the respective coordinates:


.. mpg-code:: crossword:initialize black fields
   :direct:


At first sight, the treatment of black fields in the grid appears to be inefficient. First, each element in the integer variable array ``letters`` is initialized (in the initialization list of the constructor ``Crossword()``) to a new integer variable with values ranging from ``’a’`` to ``’z’``. Then, some variables become redundant as their fields are overwritten by ``black``. However, this only matters initially when a space of class ``Crossword`` is created. As soon as a clone of that space is created, the redundant variables are not copied and hence do not matter any longer. Moreover, all black fields on the grid share a single variable ``black`` which saves memory compared to a variable for each black field on the grid.

.. _case-studies:crossword:processing-words-by-length:

Processing words by length.
'''''''''''''''''''''''''''

As suggested by the grid specification, words are processed in groups of the same length. The loop that processes all words of the same length ``l`` has the following structure:


.. mpg-code:: crossword:process words by length
   :direct:


Here, ``n`` is initialized to the number of words with length ``l`` in the grid.

To enforce that all ``n`` words of the same length ``l`` are distinct, an integer argument array ``wosl`` (for ``w``\ ords ``o``\ f ``s``\ ame ``l``\ ength) is created (see :ref:`sec:m:integer:intvararray` ), where each variable takes the possible dictionary indices for words of length ``l`` as values. The word variables in ``wosl`` are constrained to be distinct as follows:


.. mpg-code:: crossword:initialize array of words
   :direct:


.. _case-studies:crossword:constraining-letters-by-words:

Constraining letters by words.
''''''''''''''''''''''''''''''

The remaining constraints link a word variable to the variables for its letters. All words of length ``l`` are processed as follows:


.. mpg-code:: crossword:process word on grid
   :direct:


The integer argument array ``w2l`` is used to map the dictionary indices of all words of length ``l`` in the dictionary to their letters. The ``x``-coordinate and the ``y``-coordinate and whether the word extends horizontally (``h`` is ``true``) or vertically (``h`` is ``false``) is retrieved from the grid specification.

Linking a word variable to a single letter is done for all ``l`` letters in a word, where the integer ``p`` refers to the position of a letter in a word:


.. mpg-code:: crossword:process each letter position
   :direct:


The integer argument array ``w2l`` is used to map all words in the dictionary of length ``l`` to their ``p``-th letters. Then, for each letter position an ``element`` constraint (see :ref:`sec:m:integer:element` ) is posted that links the word variables to the respective letter variable:


.. mpg-code:: crossword:constrain letters
   :direct:


.. _case-studies:crossword:branching:

Branching.
''''''''''

We choose a simple branching that selects a variable where the quotient of AFC and domain size is largest (see :ref:`sec:m:branch:int` ). The first value for the selected variable to be tried is the smallest:


.. mpg-code:: crossword:branching
   :direct:


Additionally we pass a variable value print function (see :ref:`sec:m:branch:print` ) so that additional information about the branching is printed when, for example, using Gist:


.. mpg-code:: crossword:print function
   :direct:


.. _sec:c:crossword:optimized:

An optimized model
------------------


The model in the previous section wastes some memory: for all word variables for words of length ``l``, the array ``w2l`` is the same for a given position ``p``. However, the very same array is computed ``n`` times: for each word variable for words of length ``l``.


.. _fig:c:crossword:optimized:

.. mpg-code:: crossword optimized
   :caption: An optimized crossword script
   :download:


The first optimization is to swap the loops that iterate over the dictionary index ``i`` and the letter position ``p``, as shown in :ref:`fig:c:crossword:optimized` . However, one can go even further. By default, each time an ``element`` constraint is posted, a new shared array for the integer argument array is created (it will be still shared among all spaces). To just have a single copy of the array, we can create a shared integer array of type ``IntSharedArray`` instead. Then, for each word length ``l`` and each position ``p`` there will be a single shared array only. See :ref:`tip:m:integer:sharedelement` for more on shared arrays.

The shared integer array is initialized as follows:


.. mpg-code:: crossword optimized:initialize word to letter array
   :direct:


The very same shared integer array is used for all words of the same length from the dictionary as follows:


.. mpg-code:: crossword optimized:constrain letters
   :direct:


In summary, the optimization does not offer a better model but a more memory-efficient implementation of the same model.

.. _sec:c:crossword:info:

More information
----------------


The script that is shown in this case study is also available as a Gecode example called :api:`crossword` . The example features a number of different crossword grids and supports branching on the word variables or on the letter variables. In addition, arbitrary dictionaries can be used provided they are available as a list of words in a file.

.. _case-studies:crossword:related-work:

Related work.
'''''''''''''

Solving crossword puzzles is a classic example for search methods (see for example :cite:p:`DBLP:conf/aaai/GinsbergFHT90` ) and also for constraint programming (see for example :cite:p:`DBLP:conf/ai/BeachamCSB01` and :cite:p:`DBLP:conf/cp/AnbulaganB08` ).

Anbulagan and Botea introduce Combus in :cite:p:`DBLP:conf/cp/AnbulaganB08` . Combus is a constraint-based solver specialized at solving crossword puzzles. Its distinctive feature is that it uses nogood-learning to speed up search.

In the following, we are going to compare Combus to the model presented in this chapter. The purpose of the comparison is to shed light on the respective advantages of a problem-specific solver such as Combus and a simple model using a modern off-the-shelf constraint programming system such as Gecode.

.. _case-studies:crossword:used-hardware-and-software-platform:

Used hardware and software platform.
''''''''''''''''''''''''''''''''''''

All experiments have been run on a desktop with two Intel Xeon CPU (2.8 GHz, 4 cores), 8 GB of main memory, running Windows 7 x64 and using Gecode 4.4.0. The model has been run with a single thread only. The runtimes are measured as wall-time and are the average of five runs. The coefficient of deviation is less than 3% and typically less than 1%.

The hardware platform used in :cite:p:`DBLP:conf/cp/AnbulaganB08` is an Intel Core Duo 2.4 GHz.

.. _case-studies:crossword:comparison-with-combus:

Comparison with Combus.
'''''''''''''''''''''''

The purpose of the comparison is to understand better the relative merits of the two different approaches. An exact comparison of runtimes is therefore not really meaningful, in particular as different hardware platforms are used.

The comparison makes only approximate statements for runtime and number of nodes explored during search. If the runtime for the Gecode model and Combus differ by at most a factor of two in either direction, the two approaches are roughly the same, denoted by :math:`\approx`. If the runtime for the Gecode model is two to ten times faster, we use :math:`+`; if it is ten to 100 times faster, we use :math:`++`; if it is more than 100 times faster, we use :math:`+++`. Analogously, we use :math:`-`, :math:`--`, and :math:`---` if the Gecode model is slower than Combus. We also use the same symbols for comparing the number of nodes explored during search, where fewer nodes are of course better.


.. list-table:: ``words`` dictionary, :math:`15\times 15`
   :name: table:c:crossword:baseline:words:15x15
   :header-rows: 1
   :widths: 12 20 18 28 18
   :class: mpg-results

   * - instance
     - time
     - comparison
     - nodes
     - comparison
   * - ``01``
     - :math:`1.7`
     - ++
     - :math:`{897}`
     - --
   * - ``02``
     - :math:`5.3`
     - +
     - :math:`{4\,509}`
     - --
   * - ``03``
     - :math:`0.4`
     - +++
     - :math:`{143}`
     - -
   * - ``04``
     - :math:`78.9`
     - -
     - :math:`{53\,648}`
     - ---
   * - ``05``
     - :math:`1.1`
     - ++
     - :math:`{382}`
     - -
   * - ``06``
     - :math:`49.1`
     - ≈
     - :math:`{14\,895}`
     - -
   * - ``07``
     - :math:`40.4`
     - +
     - :math:`{8\,570}`
     - --
   * - ``08``
     - :math:`0.3`
     - +++
     - :math:`{130}`
     - ≈
   * - ``09``
     - :math:`0.3`
     - ++
     - :math:`{112}`
     - ≈
   * - ``10``
     - --
     - ---
     - --
     -

.. list-table:: ``words`` dictionary, :math:`19\times 19`
   :name: table:c:crossword:baseline:words:19x19
   :header-rows: 1
   :widths: 12 20 18 28 18
   :class: mpg-results

   * - instance
     - time
     - comparison
     - nodes
     - comparison
   * - ``01``
     - :math:`0.5`
     - +++
     - :math:`{145}`
     - ≈
   * - ``02``
     - :math:`3.2`
     - +
     - :math:`{1\,916}`
     - --
   * - ``03``
     - :math:`9.8`
     - +
     - :math:`{3\,267}`
     - --
   * - ``04``
     - :math:`0.7`
     - +++
     - :math:`{458}`
     - -
   * - ``05``
     - :math:`0.3`
     - ++
     - :math:`{138}`
     - ≈
   * - ``06``
     - :math:`0.4`
     - +++
     - :math:`{238}`
     - ≈
   * - ``07``
     - :math:`0.7`
     - ++
     - :math:`{203}`
     - ≈
   * - ``08``
     - :math:`0.6`
     - +++
     - :math:`{221}`
     - ≈
   * - ``09``
     - :math:`0.7`
     - ++
     - :math:`{300}`
     - -
   * - ``10``
     - :math:`0.3`
     - ++
     - :math:`{138}`
     - ≈

.. list-table:: ``words`` dictionary, :math:`21\times 21`
   :name: table:c:crossword:baseline:words:21x21
   :header-rows: 1
   :widths: 12 20 18 28 18
   :class: mpg-results

   * - instance
     - time
     - comparison
     - nodes
     - comparison
   * - ``01``
     - :math:`103.7`
     - ≈
     - :math:`{17\,605}`
     - --
   * - ``02``
     - :math:`2.4`
     - ++
     - :math:`{595}`
     - -
   * - ``03``
     - :math:`1.3`
     - ++
     - :math:`{378}`
     - -
   * - ``04``
     - :math:`36.9`
     - ++
     - :math:`{9\,974}`
     - ≈
   * - ``05``
     - :math:`7.3`
     - +
     - :math:`{3\,695}`
     - --
   * - ``06``
     - :math:`1.7`
     - ++
     - :math:`{305}`
     - -
   * - ``07``
     - :math:`2.3`
     - ++
     - :math:`{671}`
     - -
   * - ``08``
     - :math:`1.2`
     - ++
     - :math:`{173}`
     - ≈
   * - ``09``
     - :math:`1.6`
     - ++
     - :math:`{185}`
     - ≈
   * - ``10``
     - --
     - ≈
     - --
     -

.. list-table:: ``words`` dictionary, :math:`23\times 23`
   :name: table:c:crossword:baseline:words:23x23
   :header-rows: 1
   :widths: 12 20 18 28 18
   :class: mpg-results

   * - instance
     - time
     - comparison
     - nodes
     - comparison
   * - ``01``
     - :math:`0.0`
     - +++
     - :math:`{0}`
     - ≈
   * - ``02``
     - :math:`3.8`
     - ++
     - :math:`{1\,376}`
     - -
   * - ``03``
     - :math:`38.0`
     - ++
     - :math:`{7\,869}`
     - ≈
   * - ``04``
     - :math:`18.9`
     - +
     - :math:`{4\,230}`
     - -
   * - ``05``
     - :math:`2.5`
     - ++
     - :math:`{1\,258}`
     - -
   * - ``06``
     - --
     - ≈
     - --
     -
   * - ``07``
     - :math:`3.0`
     - ++
     - :math:`{1\,104}`
     - -
   * - ``08``
     - --
     - ---
     - --
     -
   * - ``09``
     - :math:`382.9`
     - ≈
     - :math:`{143\,715}`
     - -
   * - ``10``
     - --
     - ≈
     - --
     -

.. list-table:: ``uk`` dictionary, :math:`15\times 15`
   :name: table:c:crossword:baseline:uk:15x15
   :header-rows: 1
   :widths: 12 20 18 28 18
   :class: mpg-results

   * - instance
     - time
     - comparison
     - nodes
     - comparison
   * - ``01``
     - :math:`0.7`
     - +++
     - :math:`{108}`
     - ≈
   * - ``02``
     - :math:`0.7`
     - +++
     - :math:`{96}`
     - ≈
   * - ``03``
     - :math:`0.7`
     - +++
     - :math:`{104}`
     - ≈
   * - ``04``
     - :math:`0.5`
     - +++
     - :math:`{95}`
     - ≈
   * - ``05``
     - :math:`0.4`
     - +++
     - :math:`{85}`
     - ≈
   * - ``06``
     - :math:`2.2`
     - +++
     - :math:`{110}`
     - ≈
   * - ``07``
     - :math:`1.3`
     - +++
     - :math:`{114}`
     - ≈
   * - ``08``
     - :math:`0.5`
     - +++
     - :math:`{122}`
     - ≈
   * - ``09``
     - :math:`0.6`
     - +++
     - :math:`{117}`
     - ≈
   * - ``10``
     - :math:`0.8`
     - +++
     - :math:`{97}`
     - ≈

.. list-table:: ``uk`` dictionary, :math:`19\times 19`
   :name: table:c:crossword:baseline:uk:19x19
   :header-rows: 1
   :widths: 12 20 18 28 18
   :class: mpg-results

   * - instance
     - time
     - comparison
     - nodes
     - comparison
   * - ``01``
     - :math:`1.6`
     - +++
     - :math:`{200}`
     - ≈
   * - ``02``
     - :math:`1.5`
     - +++
     - :math:`{356}`
     - -
   * - ``03``
     - :math:`1.9`
     - +++
     - :math:`{378}`
     - -
   * - ``04``
     - :math:`0.8`
     - +++
     - :math:`{183}`
     - ≈
   * - ``05``
     - :math:`0.7`
     - +++
     - :math:`{145}`
     - ≈
   * - ``06``
     - :math:`0.8`
     - +++
     - :math:`{171}`
     - ≈
   * - ``07``
     - :math:`0.8`
     - +++
     - :math:`{166}`
     - ≈
   * - ``08``
     - :math:`1.0`
     - +++
     - :math:`{154}`
     - ≈
   * - ``09``
     - --
     - ---
     - --
     -
   * - ``10``
     - :math:`0.9`
     - +++
     - :math:`{173}`
     - ≈

.. list-table:: ``uk`` dictionary, :math:`21\times 21`
   :name: table:c:crossword:baseline:uk:21x21
   :header-rows: 1
   :widths: 12 20 18 28 18
   :class: mpg-results

   * - instance
     - time
     - comparison
     - nodes
     - comparison
   * - ``01``
     - :math:`3.1`
     - +++
     - :math:`{163}`
     - ≈
   * - ``02``
     - :math:`2.5`
     - +++
     - :math:`{196}`
     - ≈
   * - ``03``
     - :math:`2.6`
     - +++
     - :math:`{194}`
     - ≈
   * - ``04``
     - :math:`6.1`
     - ++
     - :math:`{282}`
     - -
   * - ``05``
     - :math:`3.9`
     - ++
     - :math:`{304}`
     - -
   * - ``06``
     - :math:`1.9`
     - +++
     - :math:`{168}`
     - ≈
   * - ``07``
     - :math:`2.1`
     - +++
     - :math:`{183}`
     - ≈
   * - ``08``
     - :math:`1.7`
     - +++
     - :math:`{188}`
     - ≈
   * - ``09``
     - :math:`2.5`
     - +++
     - :math:`{193}`
     - ≈
   * - ``10``
     - :math:`8.1`
     - +++
     - :math:`{323}`
     - -

.. list-table:: ``uk`` dictionary, :math:`23\times 23`
   :name: table:c:crossword:baseline:uk:23x23
   :header-rows: 1
   :widths: 12 20 18 28 18
   :class: mpg-results

   * - instance
     - time
     - comparison
     - nodes
     - comparison
   * - ``01``
     - :math:`3.1`
     - ++
     - :math:`{241}`
     - ≈
   * - ``02``
     - :math:`3.8`
     - +++
     - :math:`{420}`
     - -
   * - ``03``
     - :math:`6.1`
     - +++
     - :math:`{886}`
     - -
   * - ``04``
     - :math:`29.0`
     - ++
     - :math:`{2\,395}`
     - --
   * - ``05``
     - :math:`3.4`
     - +++
     - :math:`{255}`
     - ≈
   * - ``06``
     - :math:`28.0`
     - ++
     - :math:`{3\,696}`
     - --
   * - ``07``
     - :math:`3.5`
     - +++
     - :math:`{218}`
     - ≈
   * - ``08``
     - :math:`5.8`
     - +++
     - :math:`{379}`
     - -
   * - ``09``
     - :math:`3.8`
     - ++
     - :math:`{212}`
     - ≈
   * - ``10``
     - :math:`35.2`
     - ++
     - :math:`{2\,788}`
     - --

.. mpg-figure:: Comparison of Gecode model with Combus
   :name: fig:c:crossword:compare

:ref:`fig:c:crossword:compare` shows the results for the Gecode model and their comparison to Combus for the dictionaries ``words`` (containing :math:`45\,371` words) and ``uk`` (containing :math:`225\,349` words), where both dictionaries are the same as in :cite:p:`DBLP:conf/cp/AnbulaganB08` . For each grid size :math:`\mathtt{15}\times\mathtt{15}`, :math:`\mathtt{19}\times\mathtt{19}`, :math:`\mathtt{21}\times\mathtt{21}`, and :math:`\mathtt{23}\times\mathtt{23}` ten different grids ``01`` to ``10`` are used. The runtime is in seconds.

For the Gecode model a timeout of 10 minutes is used, whereas a timeout of 20 minutes has been used for Combus. Giving the Gecode model only half the time is to cater for the difference in the hardware platform used. Orange fields are instances where neither the Gecode model nor Combus finds a solution (or proves that there is none) before their respective timeouts. Red fields are instances where Combus finds a solution but the Gecode model fails to find a solution.

Just by judging how many instances can be solved by either approach (74 for the Gecode model, 77 for Combus), it becomes clear that Combus is, as to be expected, the more robust approach. Likewise, considering the number of nodes explored during search, Combus shows the clear advantage of the approach taken.

On the other hand, in most cases the Gecode model can explore more than two orders of magnitude more nodes and always at least one order of magnitude more nodes per second than Combus. This difference in efficiency explains why the simple Gecode model can solve that many instances at all.

Moreover, one needs to consider the modeling and programming effort. The Gecode model is straightforward, does have considerably less than 100 lines of code (excluding grid specifications and dictionary support), and can be programmed in a few hours. One can expect that designing and programming a powerful problem-specific solver such as Combus requires considerably more time and expertise.


.. list-table:: ``words`` dictionary, :math:`15\times 15`
   :name: table:c:crossword:restart:words:15x15
   :header-rows: 1
   :widths: 12 20 18 28 18
   :class: mpg-results

   * - instance
     - time
     - comparison
     - nodes
     - comparison
   * - ``01``
     - :math:`1.6`
     - ++
     - :math:`{741}^{1}`
     - -
   * - ``02``
     - :math:`5.9`
     - ≈
     - :math:`{1\,679}^{2}`
     - --
   * - ``03``
     - :math:`0.4`
     - +++
     - :math:`{139}`
     - ≈
   * - ``04``
     - :math:`12.8`
     - ≈
     - :math:`{5\,126}^{4}`
     - --
   * - ``05``
     - :math:`0.6`
     - ++
     - :math:`{186}`
     - -
   * - ``06``
     - :math:`95.6`
     - ≈
     - :math:`{19\,437}^{7}`
     - --
   * - ``07``
     - :math:`3.5`
     - ++
     - :math:`{836}^{1}`
     - -
   * - ``08``
     - :math:`0.3`
     - +++
     - :math:`{130}`
     - ≈
   * - ``09``
     - :math:`0.3`
     - ++
     - :math:`{115}`
     - ≈
   * - ``10``
     - :math:`61.3`
     - ≈
     - :math:`{18\,218}^{7}`
     - --

.. list-table:: ``words`` dictionary, :math:`19\times 19`
   :name: table:c:crossword:restart:words:19x19
   :header-rows: 1
   :widths: 12 20 18 28 18
   :class: mpg-results

   * - instance
     - time
     - comparison
     - nodes
     - comparison
   * - ``01``
     - :math:`0.6`
     - ++
     - :math:`{145}`
     - ≈
   * - ``02``
     - :math:`2.7`
     - +
     - :math:`{778}^{1}`
     - -
   * - ``03``
     - :math:`45.8`
     - ≈
     - :math:`{12\,967}^{6}`
     - --
   * - ``04``
     - :math:`0.7`
     - +++
     - :math:`{401}`
     - -
   * - ``05``
     - :math:`0.3`
     - ++
     - :math:`{138}`
     - ≈
   * - ``06``
     - :math:`0.4`
     - +++
     - :math:`{249}`
     - ≈
   * - ``07``
     - :math:`0.7`
     - ++
     - :math:`{242}`
     - -
   * - ``08``
     - :math:`0.7`
     - ++
     - :math:`{153}`
     - ≈
   * - ``09``
     - :math:`1.2`
     - ++
     - :math:`{766}^{1}`
     - -
   * - ``10``
     - :math:`0.3`
     - ++
     - :math:`{138}`
     - ≈

.. list-table:: ``words`` dictionary, :math:`21\times 21`
   :name: table:c:crossword:restart:words:21x21
   :header-rows: 1
   :widths: 12 20 18 28 18
   :class: mpg-results

   * - instance
     - time
     - comparison
     - nodes
     - comparison
   * - ``01``
     - :math:`58.1`
     - ≈
     - :math:`{8\,785}^{5}`
     - --
   * - ``02``
     - :math:`1.5`
     - ++
     - :math:`{314}`
     - -
   * - ``03``
     - :math:`1.3`
     - ++
     - :math:`{391}`
     - -
   * - ``04``
     - :math:`23.7`
     - ++
     - :math:`{4\,931}^{4}`
     - +
   * - ``05``
     - :math:`20.4`
     - +
     - :math:`{6\,257}^{4}`
     - --
   * - ``06``
     - :math:`1.2`
     - ++
     - :math:`{375}`
     - -
   * - ``07``
     - :math:`3.6`
     - ++
     - :math:`{901}^{1}`
     - -
   * - ``08``
     - :math:`1.3`
     - ++
     - :math:`{173}`
     - ≈
   * - ``09``
     - :math:`1.6`
     - ++
     - :math:`{188}`
     - ≈
   * - ``10``
     - --
     - ≈
     - --
     -

.. list-table:: ``words`` dictionary, :math:`23\times 23`
   :name: table:c:crossword:restart:words:23x23
   :header-rows: 1
   :widths: 12 20 18 28 18
   :class: mpg-results

   * - instance
     - time
     - comparison
     - nodes
     - comparison
   * - ``01``
     - :math:`0.0`
     - +++
     - :math:`{0}`
     - ≈
   * - ``02``
     - :math:`2.9`
     - ++
     - :math:`{467}`
     - -
   * - ``03``
     - :math:`138.5`
     - +
     - :math:`{37\,388}^{8}`
     - -
   * - ``04``
     - :math:`174.9`
     - ≈
     - :math:`{30\,388}^{8}`
     - --
   * - ``05``
     - :math:`2.3`
     - ++
     - :math:`{337}`
     - ≈
   * - ``06``
     - --
     - ≈
     - --
     -
   * - ``07``
     - :math:`3.1`
     - ++
     - :math:`{936}^{1}`
     - -
   * - ``08``
     - :math:`84.6`
     - +
     - :math:`{16\,469}^{6}`
     - -
   * - ``09``
     - :math:`79.7`
     - +
     - :math:`{15\,325}^{6}`
     - ≈
   * - ``10``
     - --
     - ≈
     - --
     -

.. list-table:: ``uk`` dictionary, :math:`15\times 15`
   :name: table:c:crossword:restart:uk:15x15
   :header-rows: 1
   :widths: 12 20 18 28 18
   :class: mpg-results

   * - instance
     - time
     - comparison
     - nodes
     - comparison
   * - ``01``
     - :math:`0.8`
     - +++
     - :math:`{103}`
     - ≈
   * - ``02``
     - :math:`0.7`
     - +++
     - :math:`{96}`
     - ≈
   * - ``03``
     - :math:`0.8`
     - +++
     - :math:`{104}`
     - ≈
   * - ``04``
     - :math:`0.6`
     - +++
     - :math:`{91}`
     - ≈
   * - ``05``
     - :math:`0.5`
     - +++
     - :math:`{85}`
     - ≈
   * - ``06``
     - :math:`2.3`
     - +++
     - :math:`{116}`
     - ≈
   * - ``07``
     - :math:`1.4`
     - +++
     - :math:`{115}`
     - ≈
   * - ``08``
     - :math:`0.6`
     - +++
     - :math:`{108}`
     - ≈
   * - ``09``
     - :math:`0.7`
     - +++
     - :math:`{116}`
     - ≈
   * - ``10``
     - :math:`0.9`
     - +++
     - :math:`{94}`
     - ≈

.. list-table:: ``uk`` dictionary, :math:`19\times 19`
   :name: table:c:crossword:restart:uk:19x19
   :header-rows: 1
   :widths: 12 20 18 28 18
   :class: mpg-results

   * - instance
     - time
     - comparison
     - nodes
     - comparison
   * - ``01``
     - :math:`1.7`
     - +++
     - :math:`{198}`
     - ≈
   * - ``02``
     - :math:`1.7`
     - +++
     - :math:`{290}`
     - -
   * - ``03``
     - :math:`2.2`
     - +++
     - :math:`{366}`
     - -
   * - ``04``
     - :math:`0.9`
     - +++
     - :math:`{181}`
     - ≈
   * - ``05``
     - :math:`0.8`
     - +++
     - :math:`{145}`
     - ≈
   * - ``06``
     - :math:`1.0`
     - +++
     - :math:`{171}`
     - ≈
   * - ``07``
     - :math:`0.9`
     - +++
     - :math:`{166}`
     - ≈
   * - ``08``
     - :math:`1.1`
     - +++
     - :math:`{154}`
     - ≈
   * - ``09``
     - :math:`20.8`
     - ++
     - :math:`{292\,873}^{14}`
     - ---
   * - ``10``
     - :math:`1.0`
     - +++
     - :math:`{173}`
     - ≈

.. list-table:: ``uk`` dictionary, :math:`21\times 21`
   :name: table:c:crossword:restart:uk:21x21
   :header-rows: 1
   :widths: 12 20 18 28 18
   :class: mpg-results

   * - instance
     - time
     - comparison
     - nodes
     - comparison
   * - ``01``
     - :math:`3.2`
     - +++
     - :math:`{162}`
     - ≈
   * - ``02``
     - :math:`2.7`
     - +++
     - :math:`{195}`
     - ≈
   * - ``03``
     - :math:`2.8`
     - +++
     - :math:`{194}`
     - ≈
   * - ``04``
     - :math:`4.9`
     - +++
     - :math:`{519}`
     - -
   * - ``05``
     - :math:`4.1`
     - ++
     - :math:`{395}`
     - -
   * - ``06``
     - :math:`2.1`
     - +++
     - :math:`{168}`
     - ≈
   * - ``07``
     - :math:`2.3`
     - +++
     - :math:`{176}`
     - ≈
   * - ``08``
     - :math:`1.9`
     - +++
     - :math:`{188}`
     - ≈
   * - ``09``
     - :math:`2.8`
     - +++
     - :math:`{193}`
     - ≈
   * - ``10``
     - :math:`8.1`
     - +++
     - :math:`{328}`
     - -

.. list-table:: ``uk`` dictionary, :math:`23\times 23`
   :name: table:c:crossword:restart:uk:23x23
   :header-rows: 1
   :widths: 12 20 18 28 18
   :class: mpg-results

   * - instance
     - time
     - comparison
     - nodes
     - comparison
   * - ``01``
     - :math:`3.0`
     - ++
     - :math:`{233}`
     - ≈
   * - ``02``
     - :math:`3.5`
     - +++
     - :math:`{366}`
     - -
   * - ``03``
     - :math:`3.4`
     - +++
     - :math:`{261}`
     - ≈
   * - ``04``
     - :math:`13.5`
     - ++
     - :math:`{848}^{1}`
     - -
   * - ``05``
     - :math:`3.7`
     - +++
     - :math:`{258}`
     - ≈
   * - ``06``
     - :math:`117.4`
     - +
     - :math:`{6\,710}^{4}`
     - --
   * - ``07``
     - :math:`3.7`
     - +++
     - :math:`{228}`
     - ≈
   * - ``08``
     - :math:`6.0`
     - +++
     - :math:`{383}`
     - -
   * - ``09``
     - :math:`3.7`
     - ++
     - :math:`{210}`
     - ≈
   * - ``10``
     - :math:`50.1`
     - ++
     - :math:`{2\,061}^{2}`
     - --

.. mpg-figure:: Comparison of Gecode model using restarts with Combus
   :name: fig:c:crossword:restart


.. _case-studies:crossword:using-restarts-and-no-goods:

Using restarts and no-goods.
''''''''''''''''''''''''''''

To improve the robustness of search, one can use restart-based search and no-goods from restarts with Gecode, see :ref:`sec:m:search:restart` and :ref:`sec:m:search:nogoods` . The instances are run using a geometric cutoff sequence with base :math:`1.5` and a scale-factor :math:`250`, a decay-factor of :math:`0.995` for AFC (see :ref:`sec:m:branch:afc` ), and no-goods depth limit of :math:`256`. The results are shown in :ref:`fig:c:crossword:restart` . The number raised to the number of nodes shows how many restarts have been carried out during search. Note that the choice of parameters is standard and in no way optimized for the problem at hand. The reason for using decay for AFC is to gradually change the AFC information for restarts.

Now Gecode can solve exactly the same instances as Combus and for all but one with at least the same efficiency. None of the instances that neither Combus nor Gecode could solve were helped by restart-based search though, even when the timeout was increased to one hour.

.. _case-studies:crossword:solve-the-rest:

Solve the rest.
'''''''''''''''


+--------------------------------------------------------+----------------------+----------------------+------------+
| instance                                               | time                 | nodes                | restarts   |
+========================================================+======================+======================+============+
| ``words-nogoods-21`` :math:`\mathtt{\times}` ``21-10`` | :math:`8:04:14.879`  | :math:`5\,057\,102`  | :math:`21` |
+--------------------------------------------------------+----------------------+----------------------+------------+
| ``words-nogoods-23`` :math:`\mathtt{\times}` ``23-06`` | :math:`10:15:46.767` | :math:`4\,253\,481`  | :math:`20` |
+--------------------------------------------------------+----------------------+----------------------+------------+
| ``words-nogoods-23`` :math:`\mathtt{\times}` ``23-10`` | :math:`54:37:13.617` | :math:`19\,125\,068` | :math:`24` |
+--------------------------------------------------------+----------------------+----------------------+------------+


.. mpg-figure:: Results for some hard words dictionary instances
   :name: fig:c:crossword:hard


Even the remaining three ``word`` instances can be solved within one day of runtime, the results are shown in :ref:`fig:c:crossword:hard` . The runtime is in the format hours:minutes:seconds (measured only by a single run).


.. mpg-figure:: Solution for instance ``words-21`` :math:`\mathtt{\times}` ``21-10``
   :name: fig:c:crossword:sol:21:10
   :class: mpg-figure-compact

   .. only:: html

      .. image:: /figures/fig-c-crossword-sol-21-10.svg
         :alt: Solution for instance words-21 by 21-10

   .. only:: latex

      .. image:: /figures/pdf/fig-c-crossword-sol-21-10.pdf
         :alt: Solution for instance words-21 by 21-10


.. mpg-figure:: Solution for instance ``words-23`` :math:`\mathtt{\times}` ``23-06``
   :name: fig:c:crossword:sol:23:06
   :class: mpg-figure-compact

   .. only:: html

      .. image:: /figures/fig-c-crossword-sol-23-06.svg
         :alt: Solution for instance words-23 by 23-06

   .. only:: latex

      .. image:: /figures/pdf/fig-c-crossword-sol-23-06.pdf
         :alt: Solution for instance words-23 by 23-06


A solution for ``words-21`` :math:`\mathtt{\times}` ``21-10`` is shown in :numref:`fig:c:crossword:sol:21:10` . A solution for ``words-23`` :math:`\mathtt{\times}` ``23-06`` is shown in :numref:`fig:c:crossword:sol:23:06` . Note that ``words-23`` :math:`\mathtt{\times}` ``23-10`` does in fact not have a solution.

.. _case-studies:crossword:acknowledgments:

Acknowledgments.
''''''''''''''''

We are grateful to Peter Van Beek for access to example grids and to Adi Botea for providing us with the dictionaries ``words`` and ``uk`` from :cite:p:`DBLP:conf/cp/AnbulaganB08` .

..
   Migration traceability for the migrated semantic constructs above.

.. mpg-covered: caption:docs/src/chapters/case-studies/c-crossword.tex.in:22:fig:c:crossword:grid
.. mpg-covered: caption:docs/src/chapters/case-studies/c-crossword.tex.in:56:fig:c:crossword:solution
.. mpg-covered: caption:docs/src/chapters/case-studies/c-crossword.tex.in:123:fig:c:crossword:script
.. mpg-covered: literal-projection:docs/src/chapters/case-studies/c-crossword.tex.in:124:crossword
.. mpg-covered: caption:docs/src/chapters/case-studies/c-crossword.tex.in:138:fig:c:crossword:spec
.. mpg-covered: literal-projection:docs/src/chapters/case-studies/c-crossword.tex.in:139:crossword:grid specification
.. mpg-covered: literal-projection:docs/src/chapters/case-studies/c-crossword.tex.in:141:crossword:words specification
.. mpg-covered: literal-projection:docs/src/chapters/case-studies/c-crossword.tex.in:182:crossword:set up
.. mpg-covered: literal-projection:docs/src/chapters/case-studies/c-crossword.tex.in:186:crossword:initialize black fields
.. mpg-covered: literal-projection:docs/src/chapters/case-studies/c-crossword.tex.in:207:crossword:process words by length
.. mpg-covered: literal-projection:docs/src/chapters/case-studies/c-crossword.tex.in:217:crossword:initialize array of words
.. mpg-covered: literal-projection:docs/src/chapters/case-studies/c-crossword.tex.in:224:crossword:process word on grid
.. mpg-covered: literal-projection:docs/src/chapters/case-studies/c-crossword.tex.in:235:crossword:process each letter position
.. mpg-covered: literal-projection:docs/src/chapters/case-studies/c-crossword.tex.in:242:crossword:constrain letters
.. mpg-covered: literal-projection:docs/src/chapters/case-studies/c-crossword.tex.in:251:crossword:branching
.. mpg-covered: literal-projection:docs/src/chapters/case-studies/c-crossword.tex.in:256:crossword:print function
.. mpg-covered: caption:docs/src/chapters/case-studies/c-crossword.tex.in:268:fig:c:crossword:optimized
.. mpg-covered: literal-projection:docs/src/chapters/case-studies/c-crossword.tex.in:269:crossword optimized
.. mpg-covered: literal-projection:docs/src/chapters/case-studies/c-crossword.tex.in:285:crossword optimized:initialize word to letter array
.. mpg-covered: literal-projection:docs/src/chapters/case-studies/c-crossword.tex.in:289:crossword optimized:constrain letters
.. mpg-covered: caption:docs/src/chapters/case-studies/c-crossword.tex.in:373:fig:c:crossword:compare
.. mpg-covered: table:docs/src/chapters/case-studies/c-crossword.tex.in:377:tabular@docs/src/chapters/case-studies/c-crossword.tex.in:377
.. mpg-covered: caption:docs/src/chapters/case-studies/c-crossword.tex.in:457:fig:c:crossword:restart
.. mpg-covered: table:docs/src/chapters/case-studies/c-crossword.tex.in:461:tabular@docs/src/chapters/case-studies/c-crossword.tex.in:461
.. mpg-covered: caption:docs/src/chapters/case-studies/c-crossword.tex.in:524:fig:c:crossword:hard
.. mpg-covered: table:docs/src/chapters/case-studies/c-crossword.tex.in:528:tabular@docs/src/chapters/case-studies/c-crossword.tex.in:528
.. mpg-covered: caption:docs/src/chapters/case-studies/c-crossword.tex.in:545:fig:c:crossword:sol:21:10
.. mpg-covered: caption:docs/src/chapters/case-studies/c-crossword.tex.in:608:fig:c:crossword:sol:23:06
