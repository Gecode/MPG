/* -*- mode: C++; c-basic-offset: 2; indent-tabs-mode: nil -*- */

#include "test/int.hh"

#include <gecode/minimodel.hh>

namespace Test { namespace Int {

  class AndFalseTest : public Test {
  public:
    int i;
    /// Create and register test
    AndFalseTest(int i0)
      : Test("AndFalse::"+str(i0),8,0,1,false), i(i0) {
    }
    /// Test whether \a x is solution
    virtual bool solution(const Assignment& x) const {
      if (i == 0) {
        for (int j=x.size(); j--; )
          if (x[j] == 0)
            return true;
        return false;
      } else {
        for (int j=x.size(); j--; )
          if (x[j] == 0)
            return false;
        return true;
      }
    }
    /// Post constraint on \a x
    virtual void post(Gecode::Space& home, Gecode::IntVarArray& x) {
      using namespace Gecode;
      BoolVarArgs b(x.size());
      for (int j=x.size(); j--; )
        b[j]=channel(home,x[j]);
      con(home,b,i);
    }
  };

  AndFalseTest ta(0);
  AndFalseTest tb(1);

}}


 
