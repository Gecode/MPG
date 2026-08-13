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

template<class View>
class Equal : public BinaryPropagator<View,Int::PC_INT_BND> {
protected:
    using BinaryPropagator<View,Int::PC_INT_BND>::x0;
    using BinaryPropagator<View,Int::PC_INT_BND>::x1;
public:
  Equal(Home home, View x0, View x1) 
    : BinaryPropagator<View,Int::PC_INT_BND>(home,x0,x1) {}
  static ExecStatus post(Home home, 
                         View x0, View x1) {
    (void) new (home) Equal<View>(home,x0,x1);
    return ES_OK;
  }
  Equal(Space& home, Equal<View>& p) 
    : BinaryPropagator<View,Int::PC_INT_BND>(home,p) {}
  virtual Propagator* copy(Space& home) {
    return new (home) Equal<View>(home,*this);
  }
  virtual ExecStatus propagate(Space& home, const ModEventDelta&) {
    GECODE_ME_CHECK(x0.gq(home,x1.min()));
    GECODE_ME_CHECK(x1.gq(home,x0.min()));
    GECODE_ME_CHECK(x0.lq(home,x1.max()));
    GECODE_ME_CHECK(x1.lq(home,x0.max()));
    if (x0.assigned() && x1.assigned())
      return home.ES_SUBSUMED(*this);
    else 
      return ES_NOFIX;
  }
};
template<class View>
class Max : public TernaryPropagator<View,Int::PC_INT_BND> {
protected:
    using TernaryPropagator<View,Int::PC_INT_BND>::x0;
    using TernaryPropagator<View,Int::PC_INT_BND>::x1;
    using TernaryPropagator<View,Int::PC_INT_BND>::x2;
public:
  Max(Home home, View x0, View x1, View x2) 
    : TernaryPropagator<View,Int::PC_INT_BND>(home,x0,x1,x2) {}
  static ExecStatus post(Home home, 
                         View x0, View x1, View x2) {
    (void) new (home) Max<View>(home,x0,x1,x2);
    return ES_OK;
  }
  Max(Space& home, Max<View>& p) 
    : TernaryPropagator<View,Int::PC_INT_BND>(home,p) {}
  virtual Propagator* copy(Space& home) {
    return new (home) Max<View>(home,*this);
  }
  virtual ExecStatus propagate(Space& home, const ModEventDelta&) {
    GECODE_ME_CHECK(x2.lq(home,std::max(x0.max(),x1.max())));
    GECODE_ME_CHECK(x2.gq(home,std::max(x0.min(),x1.min())));
    GECODE_ME_CHECK(x0.lq(home,x2.max()));
    GECODE_ME_CHECK(x1.lq(home,x2.max()));
    if ((x1.max() <= x0.min()) || (x1.max() < x2.min()))
      GECODE_REWRITE(*this,Equal<View>::post(home(*this),x0,x2));
    if ((x0.max() <= x1.min()) || (x0.max() < x2.min()))
      GECODE_REWRITE(*this,Equal<View>::post(home(*this),x1,x2));
    if (x0.assigned() && x1.assigned() && x2.assigned())
      return home.ES_SUBSUMED(*this);
    else 
      return ES_NOFIX;
  }
};

void min(Home home, IntVar x0, IntVar x1, IntVar x2) {
  GECODE_POST;
  Int::MinusView y0(x0), y1(x1), y2(x2);
  GECODE_ES_FAIL(Max<Int::MinusView>::post(home,y0,y1,y2));
}
void max(Home home, IntVar x0, IntVar x1, IntVar x2) {
  GECODE_POST;
  GECODE_ES_FAIL(Max<Int::IntView>::post(home,x0,x1,x2));
}
