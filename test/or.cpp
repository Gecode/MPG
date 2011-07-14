/* -*- mode: C++; c-basic-offset: 2; indent-tabs-mode: nil -*- */

#include "test/int.hh"

#include <gecode/minimodel.hh>

namespace Test { namespace Int {

  class OrTest : public Test {
  public:
    /// Create and register test
    OrTest(void)
      : Test("Or",8+1,0,1,false) {
    }
    /// Test whether \a x is solution
    virtual bool solution(const Assignment& x) const {
      int n=x.size()-1;
      for (int j=n; j--; )
        if (x[j] == 1)
          return x[n] == 1;
      return x[n] == 0;
    }
    /// Post constraint on \a x
    virtual void post(Gecode::Space& home, Gecode::IntVarArray& x) {
      using namespace Gecode;
      BoolVarArgs b(x.size()-1);
      for (int j=x.size()-1; j--; )
        b[j]=channel(home,x[j]);
      dis(home,b,channel(home,x[x.size()-1]));
    }
  };

  OrTest t;

}}


 
