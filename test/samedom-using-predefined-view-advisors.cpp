/* -*- mode: C++; c-basic-offset: 2; indent-tabs-mode: nil -*- */

#include "test/int.hh"

#include <gecode/minimodel.hh>

namespace Test { namespace Int {

  class SameDomTest : public Test {
  public:
    IntSet is;
    /// Create and register test
    SameDomTest(const std::string& s, IntSet is0)
      : Test("SameDom::"+s,4,-3,3,false), is(is0) {
    }
    /// Test whether \a x is solution
    virtual bool solution(const Assignment& x) const {
      for (int i=0; i<x.size()-1; i++)
        if (is.in(x[i]) != is.in(x[i+1]))
          return false;
      return true;
    }
    /// Post constraint on \a x
    virtual void post(Gecode::Space& home, Gecode::IntVarArray& x) {
      using namespace Gecode;
      samedom(home,x,is);
    }
  };

  const int va[3] = {
    -1,0,1
  };
  const int vb[5] = {
    -4,-2,0,2,4
  };
  
  Gecode::IntSet a(va,3);
  Gecode::IntSet b(vb,5);
  Gecode::IntSet c(-2,2);
  

  SameDomTest ta("A",a);
  SameDomTest tb("B",b);
  SameDomTest tc("C",c);

}}


 
