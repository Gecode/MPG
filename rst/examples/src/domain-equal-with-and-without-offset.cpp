/*
 *  Authors:
 *    Christian Schulte <schulte@gecode.dev>
 *
 *  Copyright:
 *    Christian Schulte, 2008-2026
 *
 *  Permission is hereby granted, free of charge, to any person obtaining
 *  a copy of this software, to deal in the software without restriction,
 *  including without limitation the rights to use, copy, modify, merge,
 *  publish, distribute, sublicense, and/or sell copies of the software,
 *  and to permit persons to whom the software is furnished to do so, subject
 *  to the following conditions:
 *
 *  The above copyright notice and this permission notice shall be
 *  included in all copies or substantial portions of the software.
 *
 *  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
 *  EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
 *  MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
 *  NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
 *  LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
 *  OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
 *  WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
 *
 */

#include <gecode/int.hh>

using namespace Gecode;

template<class View0, class View1>
class Equal 
  : public MixBinaryPropagator<View0,Int::PC_INT_DOM,
                               View1,Int::PC_INT_DOM> {
protected:
    using MixBinaryPropagator<View0,Int::PC_INT_DOM,
                              View1,Int::PC_INT_DOM>::x0;
    using MixBinaryPropagator<View0,Int::PC_INT_DOM,
                              View1,Int::PC_INT_DOM>::x1;
public:
  Equal(Home home, View0 x0, View1 x1) 
    : MixBinaryPropagator<View0,Int::PC_INT_DOM,
                          View1,Int::PC_INT_DOM>(home,x0,x1) {}
  static ExecStatus post(Home home, View0 x0, View1 x1) {
    (void) new (home) Equal(home,x0,x1);
    return ES_OK;
  }
  Equal(Space& home, Equal<View0,View1>& p) 
    : MixBinaryPropagator<View0,Int::PC_INT_DOM,
                          View1,Int::PC_INT_DOM>(home,p) {}
  virtual Propagator* copy(Space& home) {
    return new (home) Equal<View0,View1>(home,*this);
  }
  virtual PropCost cost(const Space&, 
                        const ModEventDelta& med) const {
    if (Int::IntView::me(med) != Int::ME_INT_DOM)
      return PropCost::binary(PropCost::LO);
    else
      return PropCost::binary(PropCost::HI);
  }
  virtual ExecStatus propagate(Space& home, 
                               const ModEventDelta& med) {
    if (Int::IntView::me(med) != Int::ME_INT_DOM) {
      do { 
        GECODE_ME_CHECK(x0.gq(home,x1.min()));
        GECODE_ME_CHECK(x1.gq(home,x0.min()));
      } while (x0.min() != x1.min());
      do {
        GECODE_ME_CHECK(x0.lq(home,x1.max()));
        GECODE_ME_CHECK(x1.lq(home,x0.max()));
      } while (x0.max() != x1.max());
      if (x0.assigned() && x1.assigned())
        return home.ES_SUBSUMED(*this);
      if (x0.range() && x1.range())
        return ES_FIX;
      return home.ES_FIX_PARTIAL
        (*this,Int::IntView::med(Int::ME_INT_DOM));
    }
    // domain propagation
    Int::ViewRanges<View0> r0(x0);
    GECODE_ME_CHECK(x1.inter_r(home,r0,shared(x0,x1)));
    Int::ViewRanges<View1> r1(x1);
    GECODE_ME_CHECK(x0.narrow_r(home,r1,shared(x0,x1)));
    if (x0.assigned() && x1.assigned())
      return home.ES_SUBSUMED(*this);
    else
      return ES_FIX;
  }
};

void equal(Home home, IntVar x0, IntVar x1) {
  GECODE_POST;
  GECODE_ES_FAIL((Equal<Int::IntView,Int::IntView>
                  ::post(home,x0,x1)));
}
void equal(Home home, IntVar x0, IntVar x1, int c) {
  GECODE_POST;
  GECODE_ES_FAIL((Equal<Int::IntView,Int::OffsetView>
                  ::post(home,x0,Int::OffsetView(x1,c))));
}
