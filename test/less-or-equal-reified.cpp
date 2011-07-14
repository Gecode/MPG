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
        : Test("LessOrEqual",2,-3,3,true) {}
      /// Test whether \a x is solution
      virtual bool solution(const Assignment& x) const {
        return x[0] <= x[1];
      }
      /// Post constraint on \a x
      virtual void post(Gecode::Space& home, Gecode::IntVarArray& x) {
        using namespace Gecode;
        rel(home,x[0],IRT_LQ,x[1]);
      }
      /// Post reified constraint on \a x
      virtual void post(Gecode::Space& home, Gecode::IntVarArray& x,
                        Gecode::BoolVar b) {
        using namespace Gecode;
        leeq(home,x[0],x[1],b);
      }
    };
    
    LessTest lesstest;

}}
 
