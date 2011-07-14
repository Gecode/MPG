/* -*- mode: C++; c-basic-offset: 2; indent-tabs-mode: nil -*- */

#include "test/int.hh"

#include <gecode/minimodel.hh>

namespace Test { namespace Int {

  class MaxTest : public Test {
  public:
    /// Create and register test
    MaxTest(void)
      : Test("Max",3,-4,4,false) {
    }
    /// Test whether \a x is solution
    virtual bool solution(const Assignment& x) const {
      return std::max(x[0],x[1])==x[2];
    }
    /// Post constraint on \a x
    virtual void post(Gecode::Space& home, Gecode::IntVarArray& x) {
      ::max(home,x[0],x[1],x[2]);
    }
  };

  MaxTest t;

}}


 
