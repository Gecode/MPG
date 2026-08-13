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
class OrTrue : 
  public BinaryPropagator<View,Int::PC_BOOL_VAL> {
protected:
    using BinaryPropagator<View,Int::PC_BOOL_VAL>::x0;
    using BinaryPropagator<View,Int::PC_BOOL_VAL>::x1;
protected:
  ViewArray<View> x;
public:
  OrTrue(Home home, ViewArray<View>& y) 
    : BinaryPropagator<View,Int::PC_BOOL_VAL>
      (home,y[0],y[1]), x(y) {
    x.drop_fst(2);
  }
  static ExecStatus post(Home home, ViewArray<View>& x) {
    for (int i=x.size(); i--; )
      if (x[i].one())
        return ES_OK;
      else if (x[i].zero())
        x.move_lst(i);
    if (x.size() == 0)
      return ES_FAILED;
    x.unique();
    if (x.size() == 1) {
      GECODE_ME_CHECK(x[0].one(home));
    } else {
      (void) new (home) OrTrue<View>(home,x);
    }
    return ES_OK;
  }
  virtual size_t dispose(Space& home) {
    (void) BinaryPropagator<View,Int::PC_BOOL_VAL>
      ::dispose(home);
    return sizeof(*this);
  }
  OrTrue(Space& home, OrTrue<View>& p) 
    : BinaryPropagator<View,Int::PC_BOOL_VAL>(home,p) {
    x.update(home,p.x);
  }
  virtual Propagator* copy(Space& home) {
    for (int i=x.size(); i--; )
      if (x[i].one()) {
        x[0]=x[i]; x.size(1); break;
      } else if (x[i].zero()) {
        x.move_lst(i);
      }
    return new (home) OrTrue<View>(home,*this);
  }
  ExecStatus resubscribe(Space& home, View& y, View z) {
    for (int i=x.size(); i--; )
      if (x[i].one()) {
        return home.ES_SUBSUMED(*this);
      } else if (x[i].zero()) {
        x.move_lst(i);
      } else {
        y=x[i]; x.move_lst(i);
        y.subscribe(home,*this,Int::PC_BOOL_VAL);
        return ES_FIX;
      }
    GECODE_ME_CHECK(z.one(home));
    return home.ES_SUBSUMED(*this);
  }
  virtual ExecStatus propagate(Space& home, const ModEventDelta&) {
    if (x0.one() || x1.one())
      return home.ES_SUBSUMED(*this);
    if (x0.zero())
      GECODE_ES_CHECK(resubscribe(home,x0,x1));
    if (x1.zero())
      GECODE_ES_CHECK(resubscribe(home,x1,x0));
    return ES_FIX;
  }
};

void dis(Home home, const BoolVarArgs& x, int n) {
  if ((n != 0) && (n != 1))
    throw Int::NotZeroOne("dis");
  GECODE_POST;
  if (n == 0) {
    for (int i=x.size(); i--; ) {
      Int::BoolView xi(x[i]);
      GECODE_ME_FAIL(xi.zero(home));
    }
  } else {
    ViewArray<Int::BoolView> y(home,x);
    GECODE_ES_FAIL(OrTrue<Int::BoolView>::post(home,y));
  }
}

void con(Home home, const BoolVarArgs& x, int n) {
  if ((n != 0) && (n != 1))
    throw Int::NotZeroOne("con");
  GECODE_POST;
  if (n == 1) {
    for (int i=x.size(); i--; ) {
      Int::BoolView xi(x[i]);
      GECODE_ME_FAIL(xi.one(home));
    }
  } else {
    ViewArray<Int::NegBoolView> y(home,x.size());
    for (int i=x.size(); i--; )
      y[i]=Int::NegBoolView(x[i]);
    GECODE_ES_FAIL(OrTrue<Int::NegBoolView>::post(home,y));
  }
}
