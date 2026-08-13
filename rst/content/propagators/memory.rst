.. _chap:p:memory:

Managing memory
===============

This chapter provides an overview of memory management for propagators. In fact, the memory management aspects discussed here are also valid for branchers (:ref:`part:b`) and to some extent even for variables (:ref:`part:v`).

.. _propagators:memory:overview:

.. rubric:: Overview.

:ref:`sec:p:memory:areas` describes the different memory areas available in Gecode together with their allocation policies. The following section (:ref:`sec:p:memory:state`) discusses how a propagator can efficiently manage its own state. :ref:`sec:p:memory:shared` discusses an abstraction for sharing data structures globally, whereas :ref:`sec:p:memory:local` discusses an abstraction for sharing data structures among several propagators (or branchers) that belong to the same space.

.. _sec:p:memory:areas:

Memory areas
------------

Gecode manages several different memory areas with different allocation policies: *spaces* provide access to space-allocated memory, *regions* provide access to temporary memory with implicit deallocation, and *space-allocated freelists* provide efficient access to small chunks of memory which require frequent allocation and deallocation.

All memory areas but freelists provide operations ``alloc()``, ``realloc()``, and ``free()`` for allocation, reallocation, and deallocation of memory from the respective area. To provide a uniform interface, Gecode also defines a ``heap`` object (see ``FuncMemHeap``) implementing the very same allocation functions. All memory-management related operations are documented in ``FuncMem``.

.. _propagators:memory:memory-management-functions:

.. rubric:: Memory management functions.

Let us consider allocation from the ``heap`` as an example. By

.. mpg-code:: snippet:p-memory:sec:p:memory:areas:code:1
   :direct:

a memory chunk for ``n`` integers is allocated. Likewise, by

.. mpg-code:: snippet:p-memory:sec:p:memory:areas:code:2
   :direct:

the memory is freed (for ``heap``, the memory is returned to the operating system). By

.. mpg-code:: snippet:p-memory:sec:p:memory:areas:code:3
   :direct:

a memory chunk is allocated for ``m`` integers. If possible, ``j`` will refer to the same memory chunk as ``i`` (but there is no guarantee, of course).

The memory management functions implement C++ semantics: ``alloc()`` calls the default constructor for each element allocated; ``realloc()`` calls the destructor, default constructor, or copy constructor (depending on whether the memory area must shrink or grow); ``free()`` calls the destructor for each element freed.

.. _propagators:memory:space:

.. rubric:: Space.

Space-allocated memory (see ``FuncMemSpace``) is managed per each individual space. All space-allocated memory is returned to the operating system if a space is deleted. Freeing memory (via the ``free()`` operation) enables the memory to be reused by later ``alloc()`` operations.

Spaces manage several blocks of memory allocated from the operating system, the block sizes are automatically chosen based on the recent memory allocations of a space (and, if a space has been created by cloning, the memory allocation history of the original space). The exact policies can be configured, see the namespace ``Kernel::MemoryConfig``.

Memory chunks allocated from the operating system for spaces are cached among all spaces for a single thread. This cache for the current thread can be flushed by invoking the ``flush()`` member function of ``Space``.

Variable implementations, propagators, branchers, view arrays, for example, are allocated from their ``home`` space. An important characteristic is that all these data structures have fixed size throughout their lifetimes or even shrink. As space-allocated memory is managed for later reusal if it is freed, frequent allocation/reallocation/deallocation leads to highly fragmented memory with little chance of reusal. Hence, space-allocated memory is *absolutely unsuited* for data structures that require frequent allocation/deallocation and/or resizing. For these data structures it is better to use the heap or freelists, if possible. See :ref:`sec:p:memory:state` for more information.

Note that space-allocated memory is available with allocators compatible with the C++ STL, see ``FuncMemAllocator``.

.. _par:p:memory:region:

.. rubric:: Region.

A region is a chunk of memory for temporary data structures with very efficient allocation and deallocation (again, its exact size is defined in the namespace ``Kernel::MemoryConfig``). The code fragment

.. mpg-code:: snippet:p-memory:par:p:memory:region:code:1
   :direct:

creates a new region ``r`` for memory management (see ``FuncMemRegion``). A region does not impose any size limit on the memory blocks allocated from it. If necessary, a region transparently falls back to heap-allocated memory.

.. container:: samepage

   Several regions can exist simultaneously. For example,

   .. mpg-code:: snippet:p-memory:par:p:memory:region:code:2
      :direct:

The speciality of a region is that it does not require ``free()`` operations. If a region is destructed, all memory allocated from it is freed. Even though a region does not require ``free()`` operations, it can profit from it: if the memory allocated last is freed first, the freed memory becomes immediately available for future allocation.

.. mpg-covered: tip:docs/src/chapters/programming/p-memory.tex.in:138:unlabeled-tip@docs/src/chapters/programming/p-memory.tex.in:138

.. mpg-tip:: Freeing memory explicitly

   In order to make best use of the memory provided by a region you can explicitly deallocate it. It is good practice to tie the expelicit deallocation to scoping units. For example, suppose that in the following example

   .. mpg-code:: snippet:p-memory:par:p:memory:region:code:3
      :direct:

   the memory allocated for ``i`` is not used outside the two blocks. Then it is in fact better to rewrite the code to:

   .. mpg-code:: snippet:p-memory:par:p:memory:region:code:4
      :direct:

   Then both blocks will have access to the full memory of the region.

.. _propagators:memory:heap:

.. rubric:: Heap.

The ``heap`` (a global variable, see ``FuncMemHeap``) is nothing but a C++-wrapper around memory allocation functions typically provided by the underlying operating system. In case memory is exhausted, an exception of type ``MemoryExhausted``\ is thrown. The default memory allocator can be replaced by a user-defined memory allocator as discussed below.

.. mpg-tip:: Memory alignment
   :name: tip:p:memory:align

   Memory allocated from the heap or a region is aligned as defined by the maximum ``std::max_align_t`` and the macro ``GECODE_MEMORY_ALIGNMENT``. This is not true for memory allocated from a space, which is aligned by ``GECODE_MEMORY_ALIGNMENT``. If differently aligned memory is needed for storing data structures for a space, it is recommended to manage that memory explicitly by allocating it from the heap instead.

   However, the macro ``GECODE_MEMORY_ALIGNMENT`` can be defined when Gecode is compiled.

.. _par:p:memory:allocator:

.. rubric:: Using a different memory allocator.

The ``heap`` object uses an object ``allocator`` of class ``Support::Allocator``. The class provides the basic operations for allocation, re-allocation, de-allocation, and copying of memory areas. By default, the ``allocator`` object uses functions such as ``malloc()`` and ``free()`` from the underlying operating system.

.. mpg-covered: caption:docs/src/chapters/programming/p-memory.tex.in:208:fig:p:memory:allocator

.. mpg-covered: figure:docs/src/chapters/programming/p-memory.tex.in:208:fig:p:memory:allocator

.. mpg-figure:: Declaration of an ``Allocator`` class
   :name: fig:p:memory:allocator

   .. mpg-code:: snippet:p-memory:par:p:memory:allocator:code:1
      :direct:

If a different allocator is needed, Gecode can be configured to not enable the default allocator (see :ref:`par:s:started:allocator`). If Gecode has been configured without the default allocator the macro ``GECODE_ALLOCATOR`` is undefined. Then an ``Allocator`` class must be defined in the namespace ``Gecode::Support`` that implements the interface shown in :numref:`fig:p:memory:allocator`. The declaration must occur before any Gecode header file is included.

.. _propagators:memory:space-allocated-freelists:

.. rubric:: Space-allocated freelists.

Freelists are allocated from space memory. Any object to be managed by a freelist must inherit from the class ``FreeList``\ which already defines a pointer to a next freelist element. The sizes for freelist objects are quite constrained, check the values ``fl_size_min`` and ``fl_size_max`` as defined in the namespace ``Kernel::MemoryConfig``.

Allocation and deallocation is available through the member functions ``fl_alloc()`` and ``fl_dispose()`` of the class ``Space``.

.. _sec:p:memory:state:

Managing propagator state
-------------------------

Many propagators require sophisticated data structures to perform propagation. The data structures are typically kept between successive executions of a propagator. There are two main issues for these data structures: *where* to allocate them and *when* to allocate them.

.. _propagators:memory:where-to-allocate:

.. rubric:: Where to allocate.

Typically, the data structures used by a propagator are of dynamic size and hence cannot be stored in a simple member of the propagator. This means that the propagator is free to allocate the memory from either its own space or from the heap. Allocation from the heap could also mean to use other operations to allocate and free memory, such as ``malloc()`` and ``free()`` provided by the operating system or ``new`` and ``delete`` provided by C++.

In case the data structure does not change its size often, it is best to allocate from a space: allocation is more efficient and deallocation is automatic when the space is deleted.

In case the data structure requires frequent reallocation operations, it is better to allocate from the heap. Then, the memory will not be automatically freed when a space is deleted. The memory must be freed by the propagator’s ``dispose()`` function. Furthermore, the Gecode kernel must be informed that the ``dispose()`` function must be called when the propagator’s home space is deleted, see :ref:`sec:p:started:waive`.

.. _propagators:memory:when-to-allocate:

.. rubric:: When to allocate.

An important fact on which search engines in Gecode rely (see :ref:`part:s`) is that they always store a space created by cloning for backtracking and never a space that has already been used for propagation. The reason is that in order to perform propagation, the propagators, variables, and branchers might require some additional memory. Hence, a space that has performed propagation is likely to require more memory than a pristine clone. As the spaces stored by a search engine define the total amount of memory allocated for solving a problem with Gecode, it pays to save memory by storing pristine clones.

The most obvious policy is to allocate *eagerly*: the data structures are allocated when the propagator is created and they are copied exactly when the propagator is copied.

However, very often it is better to *lazily* recompute the data structures as follows. The data structures are initialized and allocated the first time a propagator is executed. Likewise, the data structures are not copied and construction is again postponed until the propagator is executed again. Creating and allocating data structures lazily is often as simple as creating them eagerly. The benefit is that clones of spaces on which no propagation has been performed yet require considerably less memory.

Most propagators in Gecode that require involved data structures construct their data structures lazily (for example, the propagator for domain consistent ``distinct`` using the algorithm from :cite:p:`Regin94`, see ``Int::Distinct::Dom``). Some use a hybrid approach where some data structures are created eagerly and others lazily (for example the propagator for ``extensional`` for finite automata using the algorithm from :cite:p:`Pesant:CP:2004`, see ``Int::Extensional::LayeredGraph``).

.. _sec:p:memory:shared:

Shared objects and handles
--------------------------

A common request for managing a data structure (we will refer to data structure here just as object) is that it is used and shared by several propagators or branchers from different spaces possibly executed by parallel threads. Gecode provides *shared objects* and *shared handles* for this form of sharing.

A shared object is heap-allocated and is referred to by several shared handles. If the last shared handle is deleted, also the shared object is deleted (implemented by efficient thread-safe reference counting).

.. mpg-covered: caption:docs/src/chapters/programming/p-memory.tex.in:349:fig:p:memory:shared

.. mpg-covered: figure:docs/src/chapters/programming/p-memory.tex.in:349:fig:p:memory:shared

.. mpg-covered: literal-projection:docs/src/chapters/programming/p-memory.tex.in:350:shared object and handle

.. mpg-code:: shared object and handle
   :caption: A simple shared object and handle
   :name: fig:p:memory:shared
   :download:

:numref:`fig:p:memory:shared` shows a simple example of a shared object and the shared handle using the object. A shared object ``SIO`` (for ``S``\ hared ``I``\ nteger ``O``\ bject) stores a single integer ``data`` to be shared (normally, this will be an interesting data structure). A shared object must inherit from ``SharedHandle::Object``\ and can define a virtual destructor if needed.

The shared handle ``SI`` (for ``S``\ hared ``I``\ nteger) is the only class that has access to a shared object of type ``SIO``. A shared handle must inherit from ``SharedHandle``\ and can use the ``object()`` member function to access and update its shared object.

Shared integer arrays are an example for shared objects, see :numref:`tip:m:integer:sharedelement`.

.. _sec:p:memory:local:

Local objects and handles
-------------------------

For some applications, it is necessary to share data structures between different propagators (and/or branchers, see :ref:`part:b`) that belong to the same space. For example, several scheduling propagators might record precedences between tasks in a shared data structure. *Local objects* and *local handles* implement this form of sharing.

A local object is space-allocated and is referred to by several local handles. A local object is deleted when its ``home`` space is deleted. Local handles provide an ``update()`` function that creates a new copy of the local object when the space is cloned (while maintaining the sharing of local objects within a space).

.. mpg-covered: caption:docs/src/chapters/programming/p-memory.tex.in:388:fig:p:memory:local

.. mpg-covered: figure:docs/src/chapters/programming/p-memory.tex.in:388:fig:p:memory:local

.. mpg-covered: literal-projection:docs/src/chapters/programming/p-memory.tex.in:389:local object and handle

.. mpg-code:: local object and handle
   :caption: A simple local object and handle
   :name: fig:p:memory:local
   :download:

:numref:`fig:p:memory:local` shows a simple local object and handle. Similar to the shared integer objects from :numref:`fig:p:memory:shared`, the local integer objects here provide shared access to a single integer. However, this integer object is copied whenever the space is copied, so changes to the object are kept within the same space.

.. mpg-covered: caption:docs/src/chapters/programming/p-memory.tex.in:401:fig:p:memory:local_res

.. mpg-covered: figure:docs/src/chapters/programming/p-memory.tex.in:401:fig:p:memory:local_res

.. mpg-covered: literal-projection:docs/src/chapters/programming/p-memory.tex.in:402:local object with external resources

.. mpg-code:: local object with external resources
   :caption: A local object and handle with external resources
   :name: fig:p:memory:local_res
   :download:

If a local object additionally allocates external resources or non-space allocated memory, it must inform its ``home`` space about this fact, very much like propagators (see :ref:`sec:p:started:waive`). :numref:`fig:p:memory:local_res` shows a local object and handle that implement an array of integers. In the constructor and the ``dispose`` function, the local object registers and de-registers itself for disposal using ``AP_DISPOSE``.
