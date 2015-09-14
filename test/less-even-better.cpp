/* -*- mode: C++; c-basic-offset: 2; indent-tabs-mode: nil -*- */

#include "test/int.hh"

#include <gecode/minimodel.hh>

using namespace Test; 
using namespace Test::Int;



namespace Test { namespace Int {

    class LessTest : public Test {
    public:
      /// Create and register test
      LessTest(void)
        : Test("Less::EvenBetter",2,-3,3,false) {}
      /// Test whether \a x is solution
      virtual bool solution(const Assignment& x) const {
        return x[0] < x[1];
      }
      /// Post constraint on \a x
      virtual void post(Gecode::Space& home, Gecode::IntVarArray& x) {
        using namespace Gecode;
        less(home,x[0],x[1]);
      }
    };

    LessTest lesstest;

}}
 
