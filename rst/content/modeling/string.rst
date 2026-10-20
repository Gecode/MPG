.. _chap:m:string:

String variables and constraints
================================

This chapter gives a technical overview of bounded string variables and string
constraints in Gecode. A string variable represents a finite sequence of
integer symbols. Public concrete values restrict those symbols to Unicode
scalar values.

.. _sec:m:string:overview:

.. mpg-paragraph:: Overview.

:ref:`sec:m:string:values` explains symbols, concrete values, and Unicode
boundaries. :ref:`sec:m:string:variables` introduces string variables and
their dashed domains. :ref:`sec:m:string:constraints` summarizes the available
constraints, while :ref:`sec:m:string:branching` covers search.

.. important::

   Programs using string variables must include ``<gecode/string.hh>`` and
   link against the Gecode String library.

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

.. mpg-code:: string modeling:values and variables
   :direct:

A fixed variable can be initialized from ``StringVal``. For a non-fixed
variable, the constructor takes minimum and maximum lengths and optionally an
alphabet. Invalid length bounds or non-scalar alphabet members are rejected.

.. _sec:m:string:dashed:

.. mpg-paragraph:: Dashed domains.

Internally, a domain is a sequence of blocks. Each block describes a set of
possible symbols and lower and upper repetition bounds. This *dashed string*
representation compactly approximates many possible strings while retaining
global minimum and maximum lengths. The representation is not a lattice:
propagators refine it through the String variable implementation rather than
constructing conventional domain deltas.

Modeling code normally uses the public observations ``min_length()``,
``max_length()``, ``must_chars()``, and ``may_chars()``. An assigned variable
can be read without an encoding decision through ``val_symbols()``.
The legacy ``val()`` accessor is available only when every assigned symbol fits
in one byte.

.. _sec:m:string:constraints:

String constraints
------------------

The String module provides the following main constraint families.

* ``length`` connects a string to an integer length.
* ``rel`` provides equality, disequality, lexicographic ordering, prefix and
  suffix relations, concatenation, reversal, substring, replacement, and
  ASCII lower- and upper-case operations.
* ``substr``, ``startswith``, ``endswith``, ``contains``, ``find``, and
  ``rfind`` provide sequence constraints. Positions count scalar values.
* ``gconcat`` concatenates an argument array of strings.
* ``gcc`` constrains symbol occurrences and ``must_chars`` requires selected
  symbols to occur.
* ``element`` selects a string from a string argument array.
* ``nat2str`` and ``str2nat`` channel non-negative integers to ASCII decimal
  representations. ``char2code`` channels a one-symbol string to its scalar
  value.
* ``extensional`` accepts a DFA, an array of string variables, a finite
  language of concrete values, or regular-expression text.
* ``match`` returns the length of the match selected by a regular expression.

.. mpg-code:: string modeling:constraints
   :direct:

As with other Gecode variables, posting a constraint to a failed home is a
no-op. Invalid arguments are reported by the documented String exceptions.

.. _sec:m:string:regular:

.. mpg-paragraph:: Regular expressions.

Text passed to the regular-expression overloads is strict UTF-8. Literal
scalars and character-class ranges are represented symbolically; wildcard and
negated classes range over the active alphabet rather than enumerating the
entire Unicode space. The escapes ``\uHHHH`` and ``\u{H...}`` denote Unicode
scalar values, while ``\xHH`` denotes one legacy byte symbol.

The finite-language overload taking ``std::vector<StringVal>`` is
encoding-neutral. The overload taking ``std::vector<std::string>`` preserves
the one-byte-per-symbol compatibility interpretation.

.. _sec:m:string:branching:

Branching
---------

String branching is posted with ``branch`` and separate variable and value
selection objects. Variable selectors can prefer domain size, length bounds,
or dashed-block structure. Value selectors choose a concrete scalar sequence
from the selected domain.

.. mpg-code:: string modeling:branching
   :direct:

String branchers participate in cloning and archive their choices like native
Gecode branchers. Search terminates with assigned ``StringVar`` objects whose
encoding-neutral values can be obtained through ``val_symbols()``.

.. _sec:m:string:frontend:

MiniZinc and FlatZinc
---------------------

The Dashed frontend adds bounded string variables and the String propagators to
FlatZinc. Raw model text is UTF-8. String literals and Unicode escapes are
decoded at the parser boundary, while the solver operates only on scalar
values. The active alphabet starts with the legacy byte range and is extended
by the literals, character sets, and regular-expression ranges observed in the
model.

The :ref:`chap:c:inglenook` case study demonstrates concatenation, length,
regular-language, and optimization constraints in a complete MiniZinc model.
