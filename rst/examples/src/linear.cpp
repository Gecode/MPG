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

#include <gecode/float.hh>
using namespace Gecode;
  
class Linear
  : public TernaryPropagator<Float::FloatView,Float::PC_FLOAT_BND> {
public:
  Linear(Home home, Float::FloatView x0, Float::FloatView x1,
                    Float::FloatView x2)
    : TernaryPropagator<Float::FloatView,Float::PC_FLOAT_BND>
        (home,x0,x1,x2) {}
  static ExecStatus post(Home home, Float::FloatView x0, Float::FloatView x1,
                         Float::FloatView x2) {
    (void) new (home) Linear(home,x0,x1,x2);
    return ES_OK;
  }
  Linear(Space& home, Linear& p)
    : TernaryPropagator<Float::FloatView,Float::PC_FLOAT_BND>(home,p) {}
  virtual Propagator* copy(Space& home) {
    return new (home) Linear(home,*this);
  }
  virtual ExecStatus propagate(Space& home, const ModEventDelta&)  {
    using namespace Float;
    // create rounding object
    Rounding r;
    // prune upper bounds
    GECODE_ME_CHECK(x0.lq(home,-r.add_down(x1.min(),x2.min())));
    GECODE_ME_CHECK(x1.lq(home,-r.add_down(x0.min(),x2.min())));
    GECODE_ME_CHECK(x2.lq(home,-r.add_down(x0.min(),x1.min())));
    // prune lower bounds
    GECODE_ME_CHECK(x0.gq(home,-r.add_up(x1.max(),x2.max())));
    GECODE_ME_CHECK(x1.gq(home,-r.add_up(x0.max(),x2.max())));
    GECODE_ME_CHECK(x2.gq(home,-r.add_up(x0.max(),x1.max())));
    return (x0.assigned() && x1.assigned()) ?
      home.ES_SUBSUMED(*this) : ES_NOFIX;
  }
};

void linear(Home home, FloatVar x0, FloatVar x1, FloatVar x2) {
  GECODE_POST;
  GECODE_ES_FAIL(Linear::post(home,x0,x1,x2));
}
