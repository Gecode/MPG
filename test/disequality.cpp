/* -*- mode: C++; c-basic-offset: 2; indent-tabs-mode: nil -*- */

#include "test/int.hh"

#include <gecode/minimodel.hh>

namespace Test { namespace Int {

  class DisequalityTest : public Test {
  public:
    /// Create and register test
    DisequalityTest(void)
      : Test("Disequality",2,-5,5,false) {
    }
    /// Test whether \a x is solution
    virtual bool solution(const Assignment& x) const {
      return x[0] != x[1];
    }
    /// Post constraint on \a x
    virtual void post(Gecode::Space& home, Gecode::IntVarArray& x) {
      using namespace Gecode;
      disequal(home,x[0],x[1]);
    }
  };

  DisequalityTest t;

}}


 
