/* -*- mode: C++; c-basic-offset: 2; indent-tabs-mode: nil -*- */

#include "test/set.hh"

#include <gecode/minimodel.hh>

using namespace Test; 
using namespace Test::Set;


namespace Test { namespace Set {

    IntSet d_22(-2,2);

    class IntersectionTest : public SetTest {
    public:
      /// Create and register test
      IntersectionTest(void)
        : SetTest("Intersection",3,d_22,false) {}
      /// Test whether \a x is solution
      virtual bool solution(const SetAssignment& x) const {
        CountableSetRanges xr0(x.lub, x[0]);
        CountableSetRanges xr1(x.lub, x[1]);
        CountableSetRanges xr2(x.lub, x[2]);
        Iter::Ranges::Inter<CountableSetRanges, CountableSetRanges>
          u(xr0,xr1);
        return Iter::Ranges::equal(u,xr2);
      }
      /// Post constraint on \a x
      virtual void post(Gecode::Space& home, Gecode::SetVarArray& x, IntVarArray&) {
        using namespace Gecode;
        intersection(home,x[0],x[1],x[2]);
      }
    };
    
    IntersectionTest intersectiontest;

}}
 
