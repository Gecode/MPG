/* -*- mode: C++; c-basic-offset: 2; indent-tabs-mode: nil -*- */

#include "test/float.hh"

using namespace Test; 
using namespace Test::Float;

namespace Test { namespace Float {

  class LinearTest : public Test {
  public:
    /// Create and register test
    LinearTest(void)
      : Test("Linear",3,Gecode::FloatVal(-3,3),0.7,CPLT_ASSIGNMENT,false) {
      testfix = false;
    }
    /// %Test whether \a x is solution
    virtual MaybeType solution(const Assignment& x) const {
      Gecode::FloatVal e = 0.0;
      for (int i=x.size(); i--; )
        e += x[i];
      switch (cmp(e, Gecode::FRT_EQ, Gecode::FloatVal(0.0))) {
      case MT_FALSE: {
        Gecode::FloatVal eError = e;
        for (int i=x.size(); i--; )
          eError -= x[i];
        if (cmp(e+eError, Gecode::FRT_EQ, Gecode::FloatVal(0.0)) == MT_FALSE)
          return MT_FALSE;
        else
          return MT_MAYBE;
      }
      case MT_TRUE:
        return MT_TRUE;
      case MT_MAYBE:
        return MT_MAYBE;
      }
      GECODE_NEVER;
      return MT_FALSE;
    }
    /// Post constraint on \a x
    virtual void post(Gecode::Space& home, Gecode::FloatVarArray& x) {
      linear(home, x[0], x[1], x[2]);
    }
  };

  LinearTest lineartest;

}}
 
