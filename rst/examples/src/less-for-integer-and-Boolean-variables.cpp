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
class Less : public BinaryPropagator<View,Int::PC_INT_BND> {
protected:
    using BinaryPropagator<View,Int::PC_INT_BND>::x0;
    using BinaryPropagator<View,Int::PC_INT_BND>::x1;
public:
  Less(Home home, View x0, View x1) 
    : BinaryPropagator<View,Int::PC_INT_BND>(home,x0,x1) {}
  static ExecStatus post(Home home, View x0, View x1) {
    if (x0 == x1)
      return ES_FAILED;
    GECODE_ME_CHECK(x0.le(home,x1.max()));
    GECODE_ME_CHECK(x1.gr(home,x0.min()));
    if (x0.max() >= x1.min())
      (void) new (home) Less<View>(home,x0,x1);
    return ES_OK;
  }
  Less(Space& home, Less<View>& p) 
    : BinaryPropagator<View,Int::PC_INT_BND>(home,p) {}
  virtual Propagator* copy(Space& home) {
    return new (home) Less<View>(home,*this);
  }
  virtual ExecStatus propagate(Space& home, const ModEventDelta&)  {
    GECODE_ME_CHECK(x0.le(home,x1.max()));
    GECODE_ME_CHECK(x1.gr(home,x0.min()));
    if (x0.max() < x1.min())
      return home.ES_SUBSUMED(*this);
    else 
      return ES_FIX;
  }
};

void less(Home home, IntVar x0, IntVar x1) {
  GECODE_POST;
  GECODE_ES_FAIL(Less<Int::IntView>::post(home,x0,x1));
}
void less(Home home, BoolVar x0, BoolVar x1) {
  GECODE_POST;
  GECODE_ES_FAIL(Less<Int::BoolView>::post(home,x0,x1));
}
