#ifndef GECODE_ALLOCATOR

namespace Gecode { namespace Support {

  class Allocator {
  public:
    // Default constructor
    Allocator(void);
    // Allocate memory block of size n
    void* alloc(size_t n);
    // Return address of reallocated memory block p of size n 
    void* realloc(void* p, size_t n);
    // Free memory block p
    void free(void* p);
    // Copy n bytes from s to d and return d
    void* memcpy(void *d, const void *s, size_t n);
  };

}}

#endif
