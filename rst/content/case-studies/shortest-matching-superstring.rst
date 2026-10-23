.. _chap:c:shortest-matching-superstring:

Shortest matching superstring
=============================

This chapter combines string constraints and optimization in a complete C++
model. Given regular-expression patterns :math:`\rho_1,\ldots,\rho_n`, find
a shortest string :math:`x` containing a match of every pattern:

.. math::

   \min |x| \quad\text{subject to}\quad
   \operatorname{match}(x,\rho_i)>0
   \quad (i=1,\ldots,n).

Each pattern must match a non-empty substring somewhere in :math:`x`.
The occurrences may overlap and need not appear in the order the patterns
are listed. This is not the intersection of the patterns' whole-string
languages. See :ref:`chap:m:string` for the string modeling interface.

.. _sec:c:shortest-matching-superstring:problem:

Problem
-------

Consider three patterns over the alphabet ``{a,b,c,d,e,f}``:

.. math::

   \rho_1=\mathtt{ab(c|d)},\qquad
   \rho_2=\mathtt{(c|d)ef},\qquad
   \rho_3=\mathtt{efab}.

For example, ``cefabc`` contains ``abc`` at position four, ``cef`` at
position one, and ``efab`` at position two. Its length is six.
Simply concatenating one word from each pattern, such as
``abc`` + ``def`` + ``efab``, also satisfies the constraints, but gives
length ten. The solver should exploit overlaps rather than assume that
these occurrences occupy disjoint parts of the string.

.. _sec:c:shortest-matching-superstring:model:

Model
-----

The complete program uses ``IntMinimizeSpace`` and the branch-and-bound
engine ``BAB``, just as integer optimization models do. It needs no
MiniZinc compiler or custom search engine.

.. mpg-code:: shortest matching superstring
   :caption: A shortest string containing a match of every pattern
   :name: program:c:shortest-matching-superstring
   :download:

.. mpg-paragraph:: Initial domain and a safe length bound.

``text`` initially ranges over words of length zero through ten, with an
explicit six-symbol alphabet. The upper bound is not an arbitrary cutoff:
concatenating ``abc``, ``def``, and ``efab`` supplies a feasible length-ten
witness. Therefore no optimal solution for this instance is excluded.

More generally, a concatenation of one non-empty witness for each pattern
gives a safe upper bound, provided those witnesses use the chosen alphabet.
Changing the patterns requires reconsidering this bound; failure within
an insufficient bound would not prove that the unbounded problem has no
solution. Patterns accepting the empty string violate the precondition of
``match`` and must not be used here.

.. mpg-paragraph:: Requiring each pattern to occur.

For every pattern, the model creates an integer ``first`` with domain
``1..10`` and posts ``match(*this, text, pattern, first)``. Excluding zero
expresses exactly that the pattern must occur. Its first position is not
fixed: the model lets the solver choose the text and hence the position.
Several patterns may use overlapping substrings.

The ``first`` handles are local because their values are not needed in the
output. Their variable implementations remain connected to the posted
propagators. Once ``text`` is assigned, its first-match positions are
determined, so these integers need no independent branching.

.. mpg-paragraph:: Objective and branching.

``length(*this, text, size)`` equates the integer ``size`` to the string's
length. Returning ``size`` from ``cost()`` tells ``IntMinimizeSpace`` what
to minimize. ``BAB`` searches for improving solutions and rules out a
shorter solution before it terminates.

The first brancher tries smaller lengths. The second branches on the string
with the supported ``STRING_VAR_NONE()`` / ``STRING_VAL_LLLL()`` pair.
The model does not precompute the required overlaps or constrain the answer
to length six: that value is found by search.

.. mpg-paragraph:: Cloning and extracting the optimum.

The cloning constructor updates both stored handles, and ``copy()`` creates
a cloned model. The search engine clones its input by default, so the
initial model can be deleted after constructing ``BAB``.

Each call to ``next()`` returns a new improving solution. The program keeps
the most recent one, replacing the previous ``unique_ptr``. Only after search
is exhausted does it print the optimal string and length. If no solution
exists within the bound, it reports failure explicitly.

.. _sec:c:shortest-matching-superstring:result:

Result and optimality
---------------------

One optimal output is ``cefabc length=6``. Other optimal strings are
``cefabd``, ``defabc``, and ``defabd``; the program returns one optimum, not
all optimal solutions.

An optimality argument is short enough to check by hand. Every solution must
contain ``efab``. A word of length at most five containing ``efab`` has at
most one additional symbol, either before or after that occurrence.
Neither ``ab(c|d)`` nor ``(c|d)ef`` occurs inside ``efab``: the first
requires an extra symbol after its final ``ab``, while the second requires
one before its initial ``ef``. One extra symbol cannot supply both.
Thus no solution has length below six. Adding ``c`` or ``d`` at each end
gives exactly the four length-six solutions above.

The automated example validation independently enumerates all words over
``abcdef`` up to length six, searches for each of the three patterns, and
checks that the reported result is one of the shortest witnesses. It
verifies feasibility and optimality, not merely a successful exit code.

To compile this example from the MPG repository against the neighboring
Dashed build on Linux:

.. code-block:: console

   c++ -std=c++11 -I../gecode rst/examples/src/shortest-matching-superstring.cpp \
       -L../gecode -Wl,-rpath,"$PWD/../gecode" \
       -lgecodestring -lgecodesearch -lgecodeminimodel -lgecodeint \
       -lgecodekernel -lgecodesupport -o /tmp/shortest-matching-superstring
   /tmp/shortest-matching-superstring

The example is also registered with MPG's normal example build and
validation commands.
