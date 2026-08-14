.. _core:intro:introduction:

Introduction
============

This document provides an introduction to modeling and programming with Gecode, an open, free, portable, accessible, and efficient environment for developing constraint-based systems and applications.

The hands-on, tutorial-style approach will get you started very quickly. The focus is on giving an overview of the key concepts and ideas required to model and program with Gecode. Each concept is introduced using concrete C++ code examples that are developed and explained step by step. This document is complemented by the complete `Gecode reference documentation <https://www.gecode.dev/doc/6.4.0/reference/index.html>`__, as well as pointers to introductory and more advanced material throughout the text.

The first part of this document (:ref:`part:m`) is about *modeling* with Gecode. It explains modeling and solving constraint problems, and how to program, compile, link, and execute these models. This is complemented by a collection of interesting case studies of how to model with Gecode (:ref:`part:c`). The remaining, more advanced parts are about *programming* with Gecode: they explain how to use Gecode for implementing constraints (:ref:`part:p`), branchings (:ref:`part:b`), new variable types (:ref:`part:v`), and search engines (:ref:`part:s`).

.. _core:intro:what-is-gecode:

What is Gecode?
---------------

Gecode is an open, free, portable, accessible, and efficient environment for developing constraint-based systems and applications. Gecode is:

open
   Gecode is radically open for programming: it can be easily interfaced to other systems. It supports the programming of new propagators (as implementation of constraints), branching strategies, and search engines. New variables can be programmed at the same level of efficiency as integer, set, and float variables that ship with Gecode.

free
   Gecode is distributed under the `MIT license <https://www.gecode.dev/license.html>`__ and is `listed as free software <http://directory.fsf.org/project/gecode/>`__ by the FSF. All of its parts — including reference documentation, implementations of global constraints, and examples — are available as source code for download.

portable
   Gecode is implemented in C++ that rigidly follows the C++ standard. It can be compiled with modern C++ compilers and runs on a wide range of platforms.

accessible
   Gecode comes with complete tutorial and reference documentation that allows users to focus on different programming tasks with Gecode.

efficient
   Gecode offers excellent performance with respect to runtime, memory usage, and scalability. For example, Gecode won all gold medals in the MiniZinc Challenge in `2012 <http://www.g12.cs.mu.oz.au/minizinc/challenge2010/results2012.html>`__, `2011 <http://www.g12.cs.mu.oz.au/minizinc/challenge2010/results2011.html>`__, `2010 <http://www.g12.cs.mu.oz.au/minizinc/challenge2010/results2010.html>`__, `2009 <http://www.g12.cs.mu.oz.au/minizinc/challenge2009/results2009.html>`__, and `2008 <http://www.g12.csse.unimelb.edu.au/minizinc/results.html>`__.

parallel
   Gecode complies with reality in that it exploits the multiple cores of today’s commodity hardware for parallel search, giving an already efficient base system an additional edge.

alive
   Gecode has a sizeable user community and is being actively developed and maintained. In order to give you an idea: there has been a release every two to three month since the first release in December 2005.

.. _core:intro:what-is-this-document:

What is this document?
----------------------

We do not want to disappoint our readers, so let us get this out of the way as early as possible – here is *what this document is not*. This document is very definitely neither

- an introduction to constraint programming or modeling techniques, nor

- a collection of interesting implementations of constraints, nor

- an introduction to the architecture of constraint solvers, nor

- a reference documentation of the Gecode API.

The reader is therefore expected to have some background knowledge in constraint programming.

Furthermore, the document describes the C++ interface to Gecode, it is not about modeling with any of the available `interfaces to Gecode <https://www.gecode.dev/interfaces.html>`__.

.. _core:intro:keeping-it-simple:

.. mpg-paragraph:: Keeping it simple.

Throughout this document, we will use simple examples to explain the concepts you have to understand in order to model and program with Gecode. However, these simple examples demonstrate the *complete array of techniques* that are sufficient to implement complex models, constraints, branchings, variables, and search engines. In fact, Gecode itself is based on the very same techniques – you will learn how to develop code that is just as good as (or maybe better than?) what Gecode itself provides.

.. _core:intro:gecode-architecture:

.. mpg-paragraph:: Gecode architecture.

This document follows the general architecure of Gecode, containing one part for each major component. :numref:`fig:intro:gecode_architecture` gives an overview of the Gecode architecture. The kernel provides common functionality, upon which the modules for integer, set, and float constraints as well as the search engines are built. The colored boxes refer to the topics covered in this document.

.. figure:: /figures/fig-intro-gecode_architecture.svg
   :name: fig:intro:gecode_architecture
   :figclass: mpg-figure-full
   :alt: Gecode architecture: Int, Set, Float, and Search modules bridge the Gecode kernel and Modeling; propagators and branchers overlap the core modules, while variables and search engines extend the stack vertically.
   :width: 97.8%

   Gecode architecture

.. _core:intro:modeling:

.. mpg-paragraph:: Modeling.

The modeling part (:ref:`part:m`) of this document assumes some basic knowledge of modeling and solving constraint problems, as well as some basic C++ skills. The document restricts itself to simple and well known problems as examples. A constraint programming novice should have no difficulty to concentrate on the how-to-model with Gecode in particular, rather than the how-to-model with constraint programming in general.

The modeling part starts with a very simple constraint model that already touches on all the important concepts used in Gecode. There are detailed instructions how to compile and link the example code, so that you can get started right away. After that, the different variable types, the most important classes of constraints (including pointers to the `Global Constraint Catalog <http://www.emn.fr/z-info/sdemasse/gccat/>`__ :cite:`GlobalConstraintCatalog`, referred to by GCCat) , and the infrastructure provided by Gecode (such as search engines) are presented.

.. _core:intro:case-studies:

.. mpg-paragraph:: Case studies.

This document includes a collection of case studies in :ref:`part:c`. The case studies mix modeling and programming with Gecode. Some case studies are just interesting constraint models. Other case studies are constraint models that include the programming of new constraints and/or branchings.

.. _core:intro:programming:

.. mpg-paragraph:: Programming.

The programming parts of this document require the same knowledge as the modeling part, plus some additional basic knowledge of how constraint propagation is organized. :ref:`sec:p:started:back` provides pointers to recommended background reading.

The programming parts of this document cover the following topics:

programming propagators
   :ref:`part:p` describes in detail how new propagators (as implementations of constraints) can be programmed using Gecode. The part gives a fairly complete account of concepts and techniques for programming propagators.

programming branchers
   :ref:`part:b` describes how new branchers (as implementations of branchings for search) can be programmed using Gecode. This part is short and straightforward.

programming variables
   Gecode supports the addition of new variables types: the modules for integer, Boolean, set, and float variables use exactly the same programming interface as is available to any user. This interface is described in :ref:`part:v`.

programming search
   :ref:`part:s` describes how to program new search engines (Gecode comes with the most important search engines). The programming interface is simple yet very powerful as it is based on concurrency-enabled techniques such as recomputation and cloning.

.. _sec:intro:how:


.. _core:intro:how-to-read-this-document:

How to read this document?
--------------------------

.. figure:: /figures/fig-intro-dep.svg
   :name: fig:intro:dep
   :figclass: mpg-figure-wide

   Dependencies among different parts of this document

The dependencies among the different parts of this document are sketched in :numref:`fig:intro:dep`. Every part starts with a short overview section and sketches what constitutes the basic material of a part. A part only requires the basic material of the parts it depends on.

The dashed arrows from programming propagators (:ref:`part:p`) and programming branchers (:ref:`part:b`) capture that some but not all case studies require knowledge on how to program propagators and branchers. The individual case studies provide information on the required prerequisites.

.. _core:intro:downloading-example-programs:

.. mpg-paragraph:: Downloading example programs.

All example program code used in this document is available for download, just click the download link in the upper right corner of an example.

Note that the code available for download is licensed under the `same license as Gecode <https://www.gecode.dev/license.html>`__ and not under the same license as this document. By this, you can use an example program as a starting point for your own programs.

If you prefer to download all example programs at once, you can do so here:

- `example programs as gzipped tar archive <https://www.gecode.dev/doc/6.4.0/MPG.tar.gz>`__

- `example programs as 7z archive <https://www.gecode.dev/doc/6.4.0/MPG.7z>`__

.. _core:intro:do-i-need-to-be-a-c-wizard:

Do I need to be a C++ wizard?
-----------------------------

You very definitely do not have to be a C++ wizard to program Gecode models, some basic C++ knowledge will do. Modeling constraint problems typically involves little programming and tends to follow a common and simple structure that is presented in this document. It should be sufficient to have a general idea of programming and object-oriented programming.

Even programming with Gecode requires only basic C++ knowledge. The implementation of propagators, branchings, variables, and search engines follows simple and predictable recipes. However, this estimate refers to the aspects of using the concepts and techniques provided by Gecode. Of course, implementing truly advanced propagation algorithms inside a propagator will be challenging!

If you want to brush up your C++ knowledge, then brushing up your knowledge about the following topics might be most rewarding when using Gecode:

- Classes and objects, inheritance, virtual member functions: models are typically implemented by inheritance from a Gecode-provided base class.

- Overloading and operator overloading: post functions for constraints and support for posting symbolic expressions and relations rely on overloading (several functions with different argument types share the same function name).

- Exceptions: Gecode throws exceptions if post functions are used erroneously, for example, when numerical overflow could occur or when parameters are used inconsistently.

- Templates: while the modeling layer uses only few generic classes implemented as templates, programming with Gecode requires some basic knowledge about how to program with templates in C++.

Any textbook covering these topics should be well suited, for example, :cite:`LippmanLajoieMoo:2005` for a general introduction to C++, and :cite:`Weiss:2004` for an introduction to C++ for Java programmers.

.. _core:intro:can-you-help-me:

Can you help me?
----------------

Gecode has a lively and sizeable user community that can be tapped for help. You can ask questions about Gecode on the `discussion forum <https://www.gecode.dev/community.html>`__. But, please make sure to not waste your time and the time of others:

- Please check this document and the `Gecode reference documentation <https://www.gecode.dev/doc/6.4.0/reference/index.html>`__ before asking a question.

- Please check whether a similar question has been asked before.

- Please focus on questions specific to Gecode. For general questions about constraint programming more suitable forums exist.

- Please provide sufficient detail: describe your platform (operating system, compiler, Gecode version) and your problem (what does not work, what do you want to do, what is the problem you observe) as accurately as you can.

- Please do not contact the developers for general Gecode questions, we will not answer. First, we insist on the benefit to the entire user community to see questions and answers (and the contribution to the mailing list archive). Second, more importantly, our users are known to have very good answers indeed. Remember, they – in contrast to the developers – might be more familiar with your user perspective on Gecode.

- Never ask for solutions to homework. The only more offensive thing you could do is to provide a solution on the mailing list if someone has violated the no homework policy!

.. _core:intro:does-gecode-have-bugs:

Does Gecode have bugs?
----------------------

Yes, of course! But, Gecode is very thoroughly tested (tests cover almost 100%) and extensively used (several thousand users). If something does not work, we regret to inform you that this is most likely due to your program and not Gecode. Again, this does not mean that Gecode has no bugs. But it does mean that it might be worth searching for errors in *your* program first.

Likewise, all major program fragments in this document (those that can be downloaded) have been carefully tested as well.

And, yes. Please take our apologies in advance if that somewhat bold claim does turn out to be false... If you have accepted our apologies, you can submit your bug report `here <https://github.com/Gecode/gecode/issues>`__.

.. _core:intro:how-to-refer-to-this-document:

How to refer to this document?
------------------------------

We kindly ask you to refer to the individual parts of this document with their respective authors (each part has a dedicated set of authors). Bib\ TeX entries for the individual parts are `available here <https://www.gecode.dev/doc/6.4.0/MPG.bib>`__.

If you refer to concepts introduced in Gecode, we kindly ask you to refer to the relevant academic publications.

.. _core:intro:do-you-have-comments:

Do you have comments?
---------------------

If you have comments, suggestions, bug reports, wishes, or any other feedback for this document, please send a mail with your feedback to `mpg@gecode.dev <mailto:mpg@gecode.dev>`__.

.. mpg-covered: caption:docs/src/chapters/core/intro.tex.in:121:fig:intro:gecode_architecture
.. mpg-covered: caption:docs/src/chapters/core/intro.tex.in:232:fig:intro:dep
