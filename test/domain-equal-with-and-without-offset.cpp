/* -*- mode: C++; c-basic-offset: 2; indent-tabs-mode: nil -*- */

#include "test/int.hh"

#include <gecode/minimodel.hh>

namespace Test { namespace Int {

  class EqualTest : public Test {
  public:
    int i;
    /// Create and register test
    EqualTest(int i0)
      : Test("DomainEqual::Offset::"+str(i0),2,-5,5,false), i(i0) {
    }
    /// Test whether \a x is solution
    virtual bool solution(const Assignment& x) const {
      return x[0] == x[1]+i;
    }
    /// Post constraint on \a x
    virtual void post(Gecode::Space& home, Gecode::IntVarArray& x) {
      using namespace Gecode;
      equal(home,x[0],x[1],i);
    }
  };

  EqualTest t0(0);
  EqualTest t1(1);

}}


 
