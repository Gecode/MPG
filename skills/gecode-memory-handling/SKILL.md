---
name: gecode-memory-handling
description: "Manage Gecode memory areas and actor state: space/region/heap/freelists, lazy vs eager state allocation, shared/local handles, and disposal obligations (`AP_DISPOSE`). Use when implementing memory-sensitive propagators/branchers."
---

# Gecode Memory Handling

## Core
- Memory areas: space, region, heap, space freelists.
- `alloc/realloc/free` follow C++ object lifecycle semantics.
- Space memory auto-reclaimed on space deletion; good for stable-size actor data.
- Region is temporary arena; implicit free on region destruction.
- Heap is for frequently resized/dynamic structures.
- Search memory profile favors pristine clones; allocation timing matters.
- Shared handles: cross-space/thread shared heap object with refcount.
- Local handles: per-space shared object, copied on cloning.

## Key Patterns
- Allocate fixed actor members in home space.
- Allocate resize-heavy buffers on heap; free in `dispose()`.
- Build heavy internal state lazily on first propagation when possible.
- Choose eager vs lazy vs hybrid allocation based on clone-footprint and hit rate.
- Use regions for short-lived temporary iterators/buffers.
- Explicitly `Region::free()` at clear control-flow boundaries to maximize reuse.
- Use `SharedHandle` for immutable/global lookup data.
- Use `LocalHandle` for shared per-space mutable state.
- Use `IntSharedArray`/shared arrays for read-only large data reused across clones.
- For brancher choices using heap buffers, pair allocation/free and register `AP_DISPOSE`.
- Use `Region` for per-choice scratch arrays to avoid heap churn.

## Pitfalls
- Frequent resize in space memory causing fragmentation.
- Forgetting `home.notice(..., AP_DISPOSE)` for external/heap resources.
- Forgetting matching `home.ignore(..., AP_DISPOSE)` in dispose path.
- Assuming same alignment guarantees across space vs heap/region.
- Leaking ownership assumptions across cloning boundaries.
- Allocating per-choice temporary arrays on heap in hot paths.
