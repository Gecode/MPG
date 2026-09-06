:tocdepth: 0

.. _changelog:changelog:

Changelog
=========

.. _changelog:2026-09-06:

2026-09-06
----------

Documented the public Gecode test library, test tags, and a complete test for
the ``less`` propagator (see :ref:`chap:p:testing`).

.. _changelog:2026-05-25:

2026-05-25
----------

Updated MPG for Gecode 6.4.0: the build instructions now use the source release, and validation can target a selected Gecode branch, tag, or commit.

.. _changelog:2020-11-04:

2020-11-04
----------

Fixed description of weakly monotonic propagators in :ref:`sec:s:re:wmp`.

*Thanks to Pierre Flener.*

.. _changelog:2020-09-29:

2020-09-29
----------

Added tip about not using the copy constructor directly (see :ref:`tip:m:started:donotusecopyconstructor`).

.. _changelog:2019-08-22:

2019-08-22
----------

Fixed symmetry breaking when using CDBF :ref:`chap:c:bpp`.

*Thanks to Florian Fontan.*

.. _changelog:2019-05-28:

2019-05-28
----------

Fixed opaque colors

.. _changelog:2019-04-12:

2019-04-12
----------

Released for Gecode 6.2.0

.. _changelog:2019-04-10:

2019-04-10
----------

Fixed description of LNS in :ref:`sec:m:search:restart:lns`.

*Thanks to Marco Correia.*

.. _changelog:2019-02-13:

2019-02-13
----------

Released for Gecode 6.1.1

.. _changelog:2018-10-17:

2018-10-17
----------

Released for Gecode 6.1.0

.. _changelog:2018-10-15:

2018-10-15
----------

Added tip about memory alignment (see :ref:`tip:p:memory:align`).

.. _changelog:2018-05-22:

2018-05-22
----------

Released for Gecode 6.0.1

.. _changelog:2018-02-05:

2018-02-05
----------

Released for Gecode 6.0.0

.. _changelog:2017-11-06:

2017-11-06
----------

Explained how to use CPProfiler (see :ref:`sec:m:search:cpprofiler`).

.. _changelog:2017-11-06-2:

2017-11-06
----------

Documented commandline options for CPProfiler (see :ref:`sec:m:driver:options`).

.. _changelog:2017-05-10:

2017-05-10
----------

Updated explanation of regions for memory management (see :ref:`par:p:memory:region`).

.. _changelog:2017-05-10-2:

2017-05-10
----------

Updated explanation of shared handles and objects management (see :ref:`sec:p:memory:shared`).

.. _changelog:2017-04-18:

2017-04-18
----------

Released for Gecode 5.1.0

.. _changelog:2017-03-20:

2017-03-20
----------

Explained general tracing (see :ref:`sec:m:group:trace` and :ref:`sec:m:group:tracers`).

.. _changelog:2017-02-28:

2017-02-28
----------

Explained CHB for branching (see :ref:`sec:m:branch:chb`).

.. _changelog:2017-02-21:

2017-02-21
----------

Changed all functions for branching to functions based on ``std::function`` (see :ref:`chap:m:branch`).

.. _changelog:2017-02-21-2:

2017-02-21
----------

Explained new variable and value selection for Boolean variables (see :ref:`sec:m:branch:int`).

.. _changelog:2017-02-21-3:

2017-02-21
----------

Explained that function for ``wait()`` and ``when()`` can be of a type derived from ``std::function`` (see :ref:`sec:m:integer:exec`, :ref:`sec:m:set:exec`, and :ref:`sec:m:float:exec`).

.. _changelog:2016-10-25:

2016-10-25
----------

Released for Gecode 5.0.0

.. _changelog:2016-10-23:

2016-10-23
----------

Added a description of how to relax variables (see :ref:`par:m:search:relax`).

.. _changelog:2016-05-27:

2016-05-27
----------

Added a discussion of how propagators using advisors are re-scheduled (see :ref:`chap:p:advisors`).

.. _changelog:2016-05-27-2:

2016-05-27
----------

Added a discussion of: how propagators are disabled and enabled; the now required ``schedule()`` function of a propagator; and the ``GECODE_POST`` post macro (see :ref:`chap:p:started`).

.. _changelog:2016-05-23:

2016-05-23
----------

Added new chapter on propagator and brancher groups and tracing (see :ref:`chap:m:group`).

.. _changelog:2016-04-25:

2016-04-25
----------

Documented how Boolean expressions and relations can be extended by new reified constraints (see :ref:`sec:m:minimodel:boolmisc`).

.. _changelog:2016-04-19:

2016-04-19
----------

Documented how to use a different memory allocator (see :ref:`par:p:memory:allocator`).

.. _changelog:2015-10-14:

2015-10-14
----------

Documented portfolio search (see :ref:`sec:m:search:portfolio`).

.. _changelog:2015-09-17:

2015-09-17
----------

Explained when ``=SCHEDULE`` modification events are needed (see :ref:`sec:v:varimp:spec`).

*Thanks to Joseph Scott.*

.. _changelog:2015-09-17-2:

2015-09-17
----------

Documented new integer propagation levels (see :ref:`sec:m:integer:ipl`).

.. _changelog:2015-03-31:

2015-03-31
----------

Fixed typo in example of :ref:`part:v`.

*Thanks to Joseph Scott.*

.. _changelog:2015-03-20:

2015-03-20
----------

Released for Gecode 4.4.0

.. _changelog:2015-03-18:

2015-03-18
----------

Improved and update documentation of optimization spaces and scripts (see :ref:`sec:m:minimodel:optimize` and :ref:`sec:m:driver:script`).

.. _changelog:2015-02-26:

2015-02-26
----------

Improved explanation of activity.

*Thanks to Roberto Castañeda Lozano.*

.. _changelog:2015-01-20:

2015-01-20
----------

Released for Gecode 4.3.3

.. _changelog:2015-01-19:

2015-01-19
----------

Documented the argument of minimum and maximum constraints (see :ref:`sec:m:integer:arithmetic`)

.. _changelog:2014-11-06:

2014-11-06
----------

Released for Gecode 4.3.2

.. _changelog:2014-10-22:

2014-10-22
----------

Released for Gecode 4.3.1

.. _changelog:2014-10-20:

2014-10-20
----------

Documented changed restart-based search in :ref:`sec:m:search:restart` and added information on how to use it for LNS (see :ref:`sec:m:search:restart:lns`)

.. _changelog:2014-09-01:

2014-09-01
----------

Released for Gecode 4.3.0

.. _changelog:2014-07-27:

2014-07-27
----------

Documented multi-dimensional bin-packing constraints (see :ref:`sec:m:integer:bpp`)

.. _changelog:2014-06-30:

2014-06-30
----------

Added missing edges in :ref:`fig:m:integer:circuit` and :ref:`fig:m:integer:costcircuit`

*Thanks to Léonard Benedetti.*

.. _changelog:2013-11-05:

2013-11-05
----------

Released for Gecode 4.2.1

.. _changelog:2013-07-19:

2013-07-19
----------

Released for Gecode 4.2.0

.. _changelog:2013-07-10:

2013-07-10
----------

Explained support for no-goods for variable-value branchers (see :ref:`sec:v:branch:valcommit`)

.. _changelog:2013-07-10-2:

2013-07-10
----------

Explained how to add support for no-goods to branchers (see :ref:`sec:b:advanced:nogoods`)

.. _changelog:2013-07-10-3:

2013-07-10
----------

Explained how to use no-goods from restarts (see :ref:`sec:m:search:nogoods`)

.. _changelog:2013-06-13:

2013-06-13
----------

Released for Gecode 4.1.0

.. _changelog:2013-05-13:

2013-05-13
----------

Documented display of branching information in Gist (see :ref:`sec:m:gist:print`)

.. _changelog:2013-05-03:

2013-05-03
----------

Documented variable-value print functions for branching (see :ref:`sec:m:branch:print`)

.. _changelog:2013-03-14:

2013-03-14
----------

Released for Gecode 4.0.0

.. _changelog:2013-04-12:

2013-04-12
----------

Fixed documentation of user-defined variable selection (the ``_MERIT_`` part was missing) (see :ref:`sec:m:branch:uservar`)

*Thanks to Roberto Castañeda Lozano.*

.. _changelog:2013-03-08:

2013-03-08
----------

Documented LDSB (see :ref:`sec:m:branch:sym`)

.. _changelog:2013-02-22:

2013-02-22
----------

Documented restart-based search (see :ref:`sec:m:search:restart`), added example (see :ref:`sec:c:crossword:info`)

.. _changelog:2013-02-22-2:

2013-02-22
----------

Complete rewrite of how to branch (you should read it again), see :ref:`chap:m:branch`

.. _changelog:2013-02-14:

2013-02-14
----------

Added missing copy constructors and assignment operators in :ref:`sec:p:memory:shared` and :ref:`sec:p:memory:local`

*Thanks to David Rijsman.*

.. _changelog:2013-02-04:

2013-02-04
----------

Documented how to implement variable-value branchings (see :ref:`chap:v:branch`)

.. _changelog:2013-02-04-2:

2013-02-04
----------

Documented how to implement constraints over float variables (see :ref:`chap:p:floats`)

.. _changelog:2013-01-29:

2013-01-29
----------

Documented modeling with floats (see :ref:`chap:m:float`, :ref:`sec:m:minimodel:float`, :ref:`sec:m:branch:float`, and :ref:`par:m:started:mpfr`)

.. _changelog:2013-01-25:

2013-01-25
----------

Explain new search options for Gist in :ref:`sec:m:gist:preferences`

.. _changelog:2012-12-17:

2012-12-17
----------

Fixed typo in :ref:`sec:p:domain:iterators`

*Thanks to Benjamin Negrevergne.*

.. _changelog:2012-10-19:

2012-10-19
----------

Explained how to use half reification (see :ref:`sec:m:integer:halfreify`) and how to implement it (see :ref:`sec:p:reified:half`)

.. _changelog:2012-09-07:

2012-09-07
----------

Properly explained regions (see :ref:`par:p:memory:region`)

.. _changelog:2012-08-29:

2012-08-29
----------

Documented hardware-based random seed generation for random branchers (see :ref:`sec:m:branch:rnd`)

.. _changelog:2012-08-27:

2012-08-27
----------

Documented ``pow`` and ``nroot`` constraints (see :ref:`sec:m:integer:arithmetic` and :ref:`sec:m:minimodel:exprrel:int`)

.. _changelog:2012-08-21:

2012-08-21
----------

Fixed explanation of advisor deltas (see :ref:`par:p:advisors:delta`)

*Thanks to Max Ostrowski.*

.. _changelog:2012-03-06:

2012-03-06
----------

Explained activity-based search and shared variable selection criteria (see :ref:`chap:m:branch`)

.. _changelog:2012-03-20:

2012-03-20
----------

Released for Gecode 3.7.3

.. _changelog:2012-02-22:

2012-02-22
----------

Released for Gecode 3.7.2

.. _changelog:2011-11-10:

2011-11-10
----------

Added tip that compilers for Qt and Gecode must match (see :ref:`tip:m:started:samecompiler`)

*Thanks to Pavel Bochman.*

.. _changelog:2011-10-10:

2011-10-10
----------

Released for Gecode 3.7.1

.. _changelog:2011-10-06:

2011-10-06
----------

Explained semantics of :math:`n`-ary implication (see :ref:`sec:m:integer:rel:bool`)

.. _changelog:2011-08-31:

2011-08-31
----------

Released for Gecode 3.7.0

.. _changelog:2011-08-22:

2011-08-22
----------

Added links to the Global Constraint Catalog (Global Constraint Catalog, :cite:p:`GlobalConstraintCatalog`)

.. _changelog:2011-08-22-2:

2011-08-22
----------

Documented membership constraints (see :ref:`sec:m:integer:member`)

.. _changelog:2011-08-17:

2011-08-17
----------

Documented number of values constraints (see :ref:`sec:m:integer:nvalues`)

.. _changelog:2011-08-17-2:

2011-08-17
----------

Fixed error in explanation of value precedence constraint for multiple values (see :ref:`sec:m:integer:precede`)

*Thanks to Chris Mears.*

.. _changelog:2011-08-15:

2011-08-15
----------

Added missing information on creating a variable implementation disposer (see :ref:`par:v:varimp:dispose`)

*Thanks to Gustavo Gutierrez.*

.. _changelog:2011-07-25:

2011-07-25
----------

Fixed some typos

*Thanks to Pierre Flener.*

.. _changelog:2011-07-15:

2011-07-15
----------

Released for Gecode 3.6.0

.. _changelog:2011-07-13:

2011-07-13
----------

Documented ``precede`` constraint (see :ref:`sec:m:set:precede`)

.. _changelog:2011-07-08:

2011-07-08
----------

Explained that constraint post functions are clever in that they select a good propagator (see :ref:`sec:m:integer:generic`)

*Thanks to Kish Shen.*

.. _changelog:2011-06-30:

2011-06-30
----------

Documented ``precede`` constraint (see :ref:`sec:m:integer:precede`)

.. _changelog:2011-06-07:

2011-06-07
----------

Documented ``nooverlap`` constraint (see :ref:`sec:m:integer:geopacking`)

.. _changelog:2011-06-07-2:

2011-06-07
----------

Documented ``path`` constraint for Hamiltonian paths (see :ref:`sec:m:integer:circuit`)

.. _changelog:2011-05-26:

2011-05-26
----------

Moved graph and scheduling constraints to integer module (see :ref:`sec:m:integer:circuit` and :ref:`sec:m:integer:scheduling`)

.. _changelog:2011-05-03:

2011-05-03
----------

Fixed example for ``count`` constraint

*Thanks to Kish Shen.*

.. _changelog:2011-03-28:

2011-03-28
----------

Added :ref:`tip:m:started:install:ld` about the library path to the compilation instructions

*Thanks to Gabriel Hjort Blindell, Flutra Osmani.*

.. _changelog:2011-03-24:

2011-03-24
----------

Added pointers to MiniModel reference documentation

.. _changelog:2011-03-14:

2011-03-14
----------

Added archiving for choices and branchers

.. _changelog:2011-02-22:

2011-02-22
----------

Adapted to new names for set channeling constraints

.. _changelog:2011-02-13:

2011-02-13
----------

Added that Gecode on Windows requires Microsoft Visual C++ 2008 or better

.. _changelog:2011-02-11:

2011-02-11
----------

Added missing ``int.hh`` file

*Thanks to Gustavo Gutierrez.*

.. _changelog:2011-02-01:

2011-02-01
----------

Released for Gecode 3.5.0

.. _changelog:2011-01-28:

2011-01-28
----------

Added bin packing case study (:ref:`chap:c:bpp`)

.. _changelog:2011-01-25:

2011-01-25
----------

Documented STL-style array iterators (:ref:`sec:m:integer:stl`)

*Thanks to Gregory Crosswhite.*

.. _changelog:2010-10-09:

2010-10-09
----------

Released for Gecode 3.4.2

.. _changelog:2010-10-09-2:

2010-10-09
----------

Removed discussion of limited discrepancy search

.. _changelog:2010-10-06:

2010-10-06
----------

Released for Gecode 3.4.1

.. _changelog:2010-10-06-2:

2010-10-06
----------

Documented the ``binpacking`` constraint (:ref:`sec:m:integer:bpp`)

.. _changelog:2010-10-05:

2010-10-05
----------

Added explanation how to initially schedule a propagator using advisors (see :ref:`tip:p:advisors:started`)

*Thanks to Chris Mears.*

.. _changelog:2010-10-05-2:

2010-10-05
----------

Added installation and compilation instructions (moved and eexpanded from the reference documentation) (:ref:`sec:m:started:obtain`)

.. _changelog:2010-09-02:

2010-09-02
----------

Explain that variables are re-selected during branching (:ref:`tip:m:branch:reselected`)

*Thanks to Kish Shen.*

.. _changelog:2010-08-31:

2010-08-31
----------

Documented that variable implementation views are parametric with respect to variables (:ref:`sec:v:view:varview`)

.. _changelog:2010-08-31-2:

2010-08-31
----------

Documented that the variable base class is ``VarImpVar`` (:ref:`sec:v:var:var`)

.. _changelog:2010-07-30:

2010-07-30
----------

Many small fixes everywhere (language, presentation, references)

.. _changelog:2010-07-26:

2010-07-26
----------

Released for Gecode 3.4.0 (first complete version)

.. _changelog:2010-07-21:

2010-07-21
----------

Added a how to read section (:ref:`sec:intro:how`) and overview material to each chapter and part

.. _changelog:2010-07-20:

2010-07-20
----------

Added the part on programming search engines (:ref:`part:s`)

.. _changelog:2010-07-02:

2010-07-02
----------

Added the part on programming variables (:ref:`part:v`)

.. _changelog:2010-06-17:

2010-06-17
----------

Explain that the compiler environment is set up on Windows (:ref:`tip:m:started:cygwin`)

*Thanks to Dan Scott.*

.. _changelog:2010-06-04:

2010-06-04
----------

Explained that variables do not have ``init()`` functions as they are not needed.

.. _changelog:2010-05-10:

2010-05-10
----------

Fixed typo in :ref:`sec:m:search:recomp`

*Thanks to Andreas Karlsson.*

.. _changelog:2010-05-07:

2010-05-07
----------

Documented new MiniModel for set constraints (:ref:`sec:m:minimodel:exprrel`) and adapted to other MiniModel changes

.. _changelog:2010-05-06:

2010-05-06
----------

Added more case studies

.. _changelog:2010-05-06-2:

2010-05-06
----------

Documented new operations on argument arrays (:ref:`sec:m:integer:args`)

.. _changelog:2010-04-11:

2010-04-11
----------

Only use absolute URLs as not all PDF viewers honor the base URL

.. _changelog:2010-04-09:

2010-04-09
----------

Released for Gecode 3.3.1 (first release of “Modeling and Programming with Gecode”)

.. _changelog:2010-04-01:

2010-04-01
----------

Fixed typo in :ref:`fig:m:started:smm-best`

*Thanks to Seyed Hosein Attarzadeh Niaki.*

.. _changelog:2010-03-13:

2010-03-13
----------

Released for Gecode 3.3.0

.. _changelog:2010-02-01:

2010-02-01
----------

Described that linear expressions can freely mix integer and Boolean variables and that also sum expressions are supported (:ref:`sec:m:minimodel:exprrel`)

.. _changelog:2010-01-18:

2010-01-18
----------

Fixed typo in example (:ref:`sec:m:search:recomp`)

*Thanks to Vincent Barichard.*

.. _changelog:2010-01-18-2:

2010-01-18
----------

Added tips for linking libraries (:ref:`tip:m:started:link-gist` and :ref:`tip:m:comfy:link-driver`)

.. _changelog:2009-11-30:

2009-11-30
----------

Released for Gecode 3.2.2

.. _changelog:2009-11-24:

2009-11-24
----------

Documented ``sequence`` constraints (:ref:`sec:m:integer:sequence`)

.. _changelog:2009-11-04:

2009-11-04
----------

Released for Gecode 3.2.1

.. _changelog:2009-11-01:

2009-11-01
----------

Explained integer shared arrays for ``element`` (:ref:`tip:m:integer:sharedelement`)

.. _changelog:2009-10-16:

2009-10-16
----------

Explained ``Home`` (:ref:`tip:m:started:home`)

.. _changelog:2009-10-13:

2009-10-13
----------

Documented AFC-based variable selection for branching (:ref:`sec:m:branch:int`)

.. _changelog:2009-10-08:

2009-10-08
----------

Fixed link for reporting bugs

.. _changelog:2009-10-05:

2009-10-05
----------

Released for Gecode 3.2.0

.. _changelog:2009-06-15:

2009-06-15
----------

Fixed some broken links

*Thanks to Sverker Janson.*

.. _changelog:2009-06-08:

2009-06-08
----------

Documented branching on single variables (:ref:`sec:m:branch:basics`)

.. _changelog:2009-06-08-2:

2009-06-08
----------

Documented element constraint for matrix interface (:ref:`par:m:minimodel:matrix:element`)

.. _changelog:2009-05-20:

2009-05-20
----------

Released for Gecode 3.1.0

.. _changelog:2009-05-12:

2009-05-12
----------

Documented parallel search (:ref:`sec:m:search:parallel`)

.. _changelog:2009-05-08:

2009-05-08
----------

Clarified the use of ``"<GECODEDIR>"``. (:ref:`sec:m:started:windows`)

*Thanks to Markus Böhm.*

.. _changelog:2009-04-20:

2009-04-20
----------

Documented script commandline driver (:ref:`sec:m:comfy:driver`, :ref:`chap:m:driver`)

.. _changelog:2009-04-09:

2009-04-09
----------

Documented ``wait`` post functions (:ref:`sec:m:integer:exec`, :ref:`sec:m:set:exec`)

.. _changelog:2009-03-26:

2009-03-26
----------

Released for Gecode 3.0.2

.. _changelog:2009-03-26-2:

2009-03-26
----------

Fix for gcc compilation instructions in :ref:`sec:m:started:linux`

*Thanks to Roberto Castañeda Lozano.*

.. _changelog:2009-03-24:

2009-03-24
----------

Released for Gecode 3.0.1

.. _changelog:2009-03-23:

2009-03-23
----------

Generate shorter inter-document references to avoid problems with some PDF viewers

*Thanks to Håkan Kjellerstrand.*

.. _changelog:2009-03-13:

2009-03-13
----------

Initial release for Gecode 3.0.0
