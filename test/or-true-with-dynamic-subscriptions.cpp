/* -*- mode: C++; c-basic-offset: 2; indent-tabs-mode: nil -*- */

#include "test/int.hh"

#include <gecode/minimodel.hh>

namespace Test { namespace Int {

  class OrTrueTest : public Test {
  public:
    int i;
    /// Create and register test
    OrTrueTest(int i0)
      : Test("OrTrue::Dynamic::"+str(i0),8,0,1,false), i(i0) {
    }
    /// Test whether \a x is solution
    virtual bool solution(const Assignment& x) const {
      if (i == 0) {
        for (int j=x.size(); j--; )
          if (x[j] == 1)
            return false;
        return true;
      } else {
        for (int j=x.size(); j--; )
          if (x[j] == 1)
            return true;
        return false;
      }
    }
    /// Post constraint on \a x
    virtual void post(Gecode::Space& home, Gecode::IntVarArray& x) {
      using namespace Gecode;
      BoolVarArgs b(x.size());
      for (int j=x.size(); j--; )
        b[j]=channel(home,x[j]);
      dis(home,b,i);
    }
  };

  OrTrueTest ta(0);
  OrTrueTest tb(1);

}}


 
