.. _chap:m:string:

String variables and constraints
================================

This chapter introduces bounded-length string variables and constraints in
Dashed, the String extension of Gecode. Like :ref:`chap:m:int`,
:ref:`chap:m:set`, and :ref:`chap:m:float`, it explains how to create variables,
understand their domains, and post constraints. A string variable ranges over
finite sequences of Unicode scalar values. Its domain is represented by a
compact dashed-string abstraction, not an ordinary string or a byte array.

.. _sec:m:string:overview:

.. mpg-paragraph:: Overview.

:ref:`sec:m:string:values` explains symbols, concrete values, and Unicode
boundaries. :ref:`sec:m:string:variables` introduces string variables and
their dashed domains. :ref:`sec:m:string:constraints` summarizes the available
constraints, :ref:`sec:m:string:regular` explains regular-language membership,
and :ref:`sec:m:string:branching` covers search.
:ref:`chap:c:shortest-matching-superstring` develops a complete C++
optimization model.

.. important::

   Programs using string variables must include ``<gecode/string.hh>`` and
   link against the Gecode String library, in addition to the usual Kernel,
   Support, and Int libraries. Search also requires the Search library.

   .. mpg-code:: string modeling:include
      :direct:

.. _sec:m:string:values:

Symbols and concrete values
---------------------------

The type ``String::StringSymbol`` represents a solver symbol. A
``String::StringVal`` stores a concrete, encoding-neutral sequence of Unicode
scalar values. Its size and positions count scalar values rather than bytes,
UTF-16 code units, or user-perceived characters.

``StringVal::from_symbols`` constructs a value directly from scalar values.
``decode_utf8`` and ``decode_utf16`` decode strict UTF-8 and UTF-16,
respectively; malformed sequences, surrogate values, and values above
``U+10FFFF`` are rejected. ``to_utf8`` and ``to_utf16`` perform the inverse
encoding operations.

Gecode does not normalize text, segment grapheme clusters, perform
locale-sensitive collation, or apply Unicode case folding. The value
``U+FEFF`` is an ordinary scalar value: the UTF-16 interface receives code
units rather than a byte stream and therefore has no implicit byte-order or
BOM policy.

For example, ``StringVal::from_symbols({0x61, 0x1F600})`` contains two symbols:
an ASCII letter followed by an emoji. Encoding it as UTF-8 takes five bytes,
but a length constraint still observes length two. Scalar values range from
``U+0000`` to ``U+10FFFF``, excluding ``U+D800..U+DFFF`` (the surrogate range).

.. _sec:m:string:bytes:

.. mpg-paragraph:: Legacy byte values.

Interfaces accepting a concrete ``std::string`` retain the historical
one-byte-per-symbol interpretation. ``StringVal::from_bytes`` and
``StringVal::to_bytes`` make this compatibility boundary explicit; the latter
rejects symbols outside ``0..255`` instead of truncating them. Regular
expression text is the exception: it is decoded as strict UTF-8.

.. _sec:m:string:variables:

String variables
----------------

A ``StringVar`` has a lower and upper length bound and an active alphabet.
The default alphabet is the legacy byte range ``U+0000..U+00FF``. An explicit
``String::StringAlphabet`` can describe ASCII, Latin-1, all Unicode scalar
values, selected scalar values, or closed scalar-value ranges.

.. mpg-paragraph:: Creating a string variable.

.. mpg-code:: string modeling:values and variables
   :direct:

A fixed variable can be initialized from ``StringVal``. For a non-fixed
variable, the constructor takes minimum and maximum lengths and optionally an
alphabet. Choose non-negative, ordered length bounds within the supported
maximum (65535 with the default configuration). Do not rely on constructors
to diagnose every invalid combination of bounds.

As for other Gecode variables, ``StringVar x;`` does not create a variable
implementation. In contrast, ``StringVar x(home);`` creates a variable with
default length bounds and the legacy byte alphabet. Copying a handle, as in
``StringVar y(x);``, shares the variable implementation; it does not create an
independent string constrained to equal ``x``.

.. mpg-tip:: Small domains are still beautiful

   Give the shortest useful maximum length and the smallest useful alphabet.
   A variable with alphabet :math:`A` and length bounds :math:`l,u` can
   initially represent :math:`\sum_{n=l}^{u}|A|^n` strings. Using all Unicode
   scalar values for a model that needs only letters ``a`` and ``b`` is
   unnecessary even though the alphabet is stored compactly.

.. _sec:m:string:dashed:

.. mpg-paragraph:: Dashed domains.

Internally, a domain is an ordered sequence of blocks. A block consists of a
set of symbols and lower and upper bounds on how many consecutive positions it
contributes. For example, the two blocks ``{a,b}`` repeated once or twice,
followed by ``{0,1}`` repeated once or twice, describe strings such as
``a0``, ``bb1``, and ``ab00``. The domain also maintains global minimum and
maximum string lengths; these bounds further restrict the strings described
by its blocks.

Write :math:`A^{[l,u]}` for the words over alphabet :math:`A` whose lengths
are between :math:`l` and :math:`u`. A dashed domain with blocks
:math:`(A_1,l_1,u_1),\ldots,(A_k,l_k,u_k)` and global bounds :math:`L,U`
denotes

.. math::

   \{w_1\cdots w_k \mid w_i\in A_i^{[l_i,u_i]},
                       \ L\leq \sum_i |w_i|\leq U\}.

Different positions contributed by one block choose their symbols
independently: a block ``{a,b}`` with bounds ``[2,2]`` permits ``aa``, ``ab``,
``ba``, and ``bb``, not just repetitions of one chosen symbol. A block with
lower bound zero is optional; it can contribute no symbols.

This *dashed string* representation is compact, but cannot express
arbitrary correlations between positions: for example, a single dashed domain
cannot represent exactly the language ``{aa, bb}`` without also allowing
additional combinations. Propagation therefore refines an approximation of
the strings still possible, while the posted constraints define the model's
actual solutions.

The public ``String::NSBlock`` and ``String::NSBlocks`` types can be used to
construct such domains explicitly. A block is created from a symbol set and
its repetition bounds; the blocks are supplied in string order and combined
with global length bounds when constructing a ``StringVar``.

.. mpg-code:: string modeling:dashed domain
   :direct:

This constructs the two-block domain described above, but fixes the total
length to three. Thus ``a0`` and ``ab00`` are excluded, while ``a01`` and
``ab0`` remain. In contrast to a fixed-size character array, block boundaries
need not have a fixed position: here the second block can start at position
two or three.

.. mpg-paragraph:: Variable access functions.

Modeling code normally uses the public observations ``min_length()``,
``max_length()``, ``must_chars()``, and ``may_chars()``. An assigned variable
can be read without an encoding decision through ``val_symbols()``.
The legacy ``val()`` accessor is available only when every assigned symbol fits
in one byte.

``assigned()`` tests whether the domain describes one concrete string.
``may_chars()`` collects the symbols allowed by the blocks; ``must_chars()``
collects symbols from non-optional singleton blocks. These summaries do not
preserve positions or occurrence counts. In particular, ``must_chars()`` is
not an exhaustive inference of all character requirements imposed by posted
constraints. The separate constraint ``must_chars(home, x, s)`` requires the
symbols in ``s`` to occur; it is not an accessor.

Inspecting a handle does not run propagation. For example, after posting
``match``, call ``status()`` on the space before observing its result, or read
it from a solution returned by search. Do not read ``val()`` or
``val_symbols()`` from an unassigned variable.

.. mpg-paragraph:: Cloning and variable arrays.

In the cloning constructor of a model, update each stored string handle with
``text.update(*this, other.text)`` after invoking ``Space(other)``. An integer
handle or a variable array is updated in the same way. This connects handles
to variable implementations in the cloned space, not in the original space.

``StringVarArgs`` passes a collection of variables to a constraint or
brancher; ``StringVarArray`` stores a collection in a space. For example:

.. mpg-code:: string modeling:arrays
   :direct:

Here each element receives its own bounded ASCII variable. Although the
``StringVarArray(home, n)`` constructor currently initializes its elements
with default string variables, explicitly replace these defaults when the
model needs tighter length or alphabet bounds. Prefer these public handles
to internal views and space-owned dashed-domain objects when modeling.

.. _sec:m:string:constraints:

String constraints
------------------

As for the other variable types, a posting function adds a constraint to a
space. It does not compute and return a C++ string: its arguments are related
in both directions. For example, constraining the result of concatenation
can prune either input. In the signatures below ``home`` is omitted,
``x``, ``y``, and ``z`` are string variables, and integer results are
``IntVar`` objects.

.. mpg-paragraph:: Equality and ordering.

``rel(home, x, r, y)`` accepts ``STRT_EQ``, ``STRT_NQ``, ``STRT_LEXLT``, and
``STRT_LEXLQ``. Lexicographic order compares numeric scalar values; it is not
locale-sensitive dictionary order. The same four relations have an overload
taking ``Reify`` (see :ref:`sec:m:string:reification`).

Do not infer supported overloads from an enum name alone. In this
implementation, the unary call ``rel(home, x, STRT_INCLQ)`` requires
non-decreasing symbols, and ``STRT_INCLT`` requires strictly increasing
symbols. The unary ``STRT_DECLQ`` and ``STRT_DECLT`` variants impose the
corresponding decreasing orders. They are not binary prefix/suffix posters;
use ``startswith`` and ``endswith`` for those relations.

.. mpg-paragraph:: Length, concatenation, and transformations.

.. list-table:: Basic string operations
   :header-rows: 1
   :widths: 45 55

   * - Call (without ``home``)
     - Constraint
   * - ``length(x, n)``
     - :math:`n=|x|`.
   * - ``rel(x, y, STRT_CAT, z)``
     - ``z`` is ``x`` followed by ``y``.
   * - ``gconcat(xs, z)``
     - ``z`` concatenates all entries of ``StringVarArgs xs`` in order.
   * - ``rel(x, STRT_REV, y)``
     - ``y`` is the scalar sequence of ``x`` in reverse order.
   * - ``pow(x, n, y)``
     - ``y`` consists of ``n`` repetitions of ``x``.
   * - ``rel(x, STRT_LCASE, y)``
     - Convert ASCII upper-case letters in ``x`` to lower case.
   * - ``rel(x, STRT_UCASE, y)``
     - Convert ASCII lower-case letters in ``x`` to upper case.

Reversal operates on scalar values, not on UTF-8 bytes or grapheme clusters.
Case conversion is ASCII-only, not general Unicode case folding.

.. mpg-paragraph:: Substrings and sequence predicates.

``substr(home, x, i, j, y)`` uses one-based, inclusive endpoints, not a
start-and-length pair. It selects positions from ``max(1,i)`` through
``min(length(x),j)``; an empty intersection gives the empty string.

.. mpg-code:: string modeling:substring
   :direct:

Here ``slice`` becomes ``bcd``. Using the same integer variable for ``i`` and
``j`` selects one symbol, or the empty string if the index lies outside
``1..length(x)``.

``startswith(home, x, y)``, ``endswith(home, x, y)``, and
``contains(home, x, y)`` require ``y`` to be a prefix, suffix, or substring of
``x``, respectively. Each also has an overload with a final ``BoolVar b``
equivalent to the predicate. Notice the argument order:
``contains(home, haystack, pattern)``, but
``find(home, pattern, haystack, index)``.

.. mpg-paragraph:: Searching and replacing.

``find`` and ``rfind`` constrain an integer to the one-based position of a
string-valued pattern's first or last occurrence in a haystack; zero denotes
no occurrence. ``match`` instead uses regular-expression text as its pattern.
Its semantics and the difference from whole-string membership are detailed
in :ref:`sec:m:string:regular`.

``replace(home, x, q, replacement, y)`` replaces the first occurrence of ``q``
in ``x``; ``replace_last`` replaces the last and ``replace_all`` replaces
all non-overlapping occurrences. An absent pattern leaves the string
unchanged. For example, in ``ababa``, replacing ``ba`` by ``X`` produces
``aXba``, ``abaX``, or ``aXX``, respectively. The corresponding ternary
``rel`` operations use ``STRT_REP``, ``STRT_REPLST``, and ``STRT_REPALL``.
``STRT_SUB`` is not supported by the ``rel`` posters; use ``substr`` or
``contains`` instead.

.. mpg-paragraph:: Counting, selection, and numeric channels.

``gcc(home, x, cover, counts)`` connects each integer variable ``counts[i]``
to the number of occurrences of scalar ``cover[i]`` in ``x``. Supply equally
sized arrays and distinct cover values. Symbols not in ``cover`` are not
counted, and need not be forbidden. ``must_chars(home, x, s)`` requires every
symbol in ``s`` to occur at least once.

``element(home, xs, i, x)`` selects ``x = xs[i]``, with a zero-based array
index, unlike the one-based positions inside strings.

``nat2str(home, n, x)`` and ``str2nat(home, x, n)`` connect a non-negative
integer to an ASCII decimal representation; they are not general-purpose
Unicode number parsers. ``char2code(home, x, n)`` requires ``x`` to contain
one scalar value and equates its numeric value to ``n``.

.. mpg-code:: string modeling:constraints
   :direct:

These constraints can be combined without decomposing a string into integer
variables. In the excerpt above, ``size`` is its length, whole-string regex
membership restricts ``word``, and disequality excludes one concrete value.

.. _sec:m:string:reification:

.. mpg-paragraph:: Reification.

For ``rel(home, x, r, y, Reify(b, mode))``, ``RM_EQV`` means
:math:`b\Leftrightarrow(x\mathrel{r}y)`, ``RM_IMP`` means
:math:`b\Rightarrow(x\mathrel{r}y)`, and ``RM_PMI`` means
:math:`(x\mathrel{r}y)\Rightarrow b`. The default mode of ``Reify(b)`` is
``RM_EQV``. Regex membership instead takes ``b`` and the mode as separate
arguments:

.. mpg-code:: string modeling:reification
   :direct:

This relates ``member`` to membership; it does not require membership unless
``member`` is fixed to one. The Boolean predicate overloads of
``startswith``, ``endswith``, and ``contains`` express equivalence and do not
take a ``ReifyMode`` argument.

.. _sec:m:string:regular:

Regular languages and first-match search
--------------------------------------------------

``extensional(home, x, expr)`` constrains the *whole string* ``x`` to the
language of ``expr``. For example, ``(ab)*`` permits the empty string, ``ab``,
and ``abab``, but not ``aab``. This is different from finding ``ab``
somewhere inside a longer string.

.. mpg-paragraph:: Pattern syntax and encoding.

Text passed to the regular-expression overloads is strict UTF-8. Literal
scalars and character-class ranges are represented symbolically; wildcard and
negated classes range over the active alphabet of the constrained variable,
rather than enumerating the entire Unicode space. The escapes ``\uHHHH`` and
``\u{H...}`` denote Unicode scalar values, while ``\xHH`` denotes one legacy
byte symbol. A backslash in a normal C++ string literal must be doubled;
for example ``"\\u{1F600}"`` passes a Unicode escape to the regex parser.

The parser supports literal concatenation, alternation ``(a|b)``,
intersection ``(a&b)``, Kleene repetition ``*``, wildcard ``.``, and
character classes such as ``[a-z]`` and ``[^a]``. Parentheses group
expressions. In particular, ``+`` and ``?`` are not repetition operators in
this dialect: use ``aa*`` for one or more ``a`` symbols, and ``(a|)`` for an
optional ``a``. Do not assume compatibility with ``std::regex`` or a
particular text editor's regex dialect.

The finite-language overload taking ``std::vector<StringVal>`` is
encoding-neutral. The overload taking ``std::vector<std::string>`` preserves
the one-byte-per-symbol compatibility interpretation.

Other ``extensional`` overloads accept a ``DFA`` or a ``StringVarArgs`` of
candidate strings. Use the finite-language overload for a fixed dictionary,
not a regular expression built by concatenating unescaped dictionary text.
An exact language constraint can retain correlations that are not visible
in the variable's dashed-domain approximation.

.. mpg-paragraph:: The position of the first match.

``match(home, x, expr, i)`` relates ``i`` to the smallest one-based position
at which a non-empty substring of ``x`` belongs to the regex language. It
sets ``i`` to zero when no substring matches. The index counts Unicode
scalar values, not encoded bytes. It returns neither the matched text nor
its length, and it does not choose a later occurrence merely because ``i``
has been constrained to that later position.

.. mpg-code:: string modeling:match
   :direct:

After propagation, ``first_match`` is three, where ``cat`` begins; ``dog``
begins at thirteen, but it is not the first match. No integer equality is
needed to tell the solver that the answer is three. Constraining the index
to thirteen would instead fail.

The pattern must not accept the empty string. For example, ``a*`` violates
the precondition: the current poster fails the space rather than interpreting
it as a match at every boundary. Use a non-empty pattern such as ``aa*``.
This differs from ``extensional``, where languages containing the empty
string are allowed. For a complete model that constructs a shortest string
containing matches of several patterns, see
:ref:`chap:c:shortest-matching-superstring`.

.. _sec:m:string:branching:

Branching
---------

As for integer and set variables, constraints alone do not specify the search
order. String branching is posted with ``branch`` and separate variable and
value selection objects. Variable selection can use the estimated domain
size, length bounds, or dashed-block structure. Value selection controls
splits on length, block repetition counts, and symbols; it does not generally
assign a complete string in one step.

.. mpg-code:: string modeling:branching
   :direct:

Not every pair of selectors is implemented. The supported combinations are:

.. list-table:: Supported string branching combinations
   :header-rows: 1
   :widths: 35 40 25

   * - Variable selector
     - Preference
     - Value selector
   * - ``STRING_VAR_NONE()``
     - First unassigned
     - ``STRING_VAL_LLLL()``
   * - ``STRING_VAR_SIZEMIN()``
     - Smallest estimated domain
     - ``STRING_VAL_LLUL()``
   * - ``STRING_VAR_LENMIN()``
     - Smallest minimum length
     - ``STRING_VAL_LLLL()``
   * - ``STRING_VAR_LENMAX()``
     - Largest maximum length
     - ``STRING_VAL_LLLL()``
   * - ``STRING_VAR_BLOCKMIN()``
     - Fewest dashed blocks
     - ``STRING_VAL_LLLL()`` or ``STRING_VAL_LLLM()``
   * - ``STRING_VAR_LENBLOCKMIN()``
     - Smallest minimum length, then fewest blocks
     - ``STRING_VAL_LLLM()``

``LLLL`` prefers lower lengths, lower repetition counts, and lower symbols;
``LLUL`` prefers upper repetition counts instead; ``LLLM`` prefers mandatory
symbols after lower length and repetition alternatives. Unsupported pairs
throw ``String::UnknownBranching``. In particular, do not combine
``STRING_VAR_SIZEMIN()`` with ``STRING_VAL_LLLL()``.

Branch on every independent decision variable: integer or Boolean variables
that remain undetermined need their own branchers. String branchers support
cloning and archived choice replay. Read assigned strings from solutions
using ``val_symbols()`` and choose the output encoding explicitly.

.. _sec:m:string:frontend:

MiniZinc and FlatZinc
---------------------
MiniZinc string models require Dashed's bundled ``mzn2fzn-str`` compiler,
based on MiniZinc 2.0.97 with string-variable support. The official MiniZinc
release does not currently support this extension. The bundled compiler
supports Linux x86-64.

The Dashed frontend adds bounded-length string variables and the String
propagators to FlatZinc. Raw model text is UTF-8. String literals and Unicode
escapes are decoded at the parser boundary, while the solver operates only on
scalar values. The active alphabet starts with the legacy byte range and is
extended by the literals, character sets, and regular-expression ranges
observed in the model.

This frontend is optional. The modeling interface and the complete example
in :ref:`chap:c:shortest-matching-superstring` are C++ and do not require MiniZinc or
the bundled compiler.
