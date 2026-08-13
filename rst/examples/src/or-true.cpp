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

class OrTrue : public Propagator {
protected:
  ViewArray<Int::BoolView> x;
public:
  OrTrue(Home home, ViewArray<Int::BoolView>& y) 
    : Propagator(home), x(y) {
    x.subscribe(home,*this,Int::PC_BOOL_VAL);
  }
  static ExecStatus post(Home home, ViewArray<Int::BoolView>& x) {
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
      (void) new (home) OrTrue(home,x);
    }
    return ES_OK;
  }
  virtual size_t dispose(Space& home) {
    x.cancel(home,*this,Int::PC_BOOL_VAL);
    (void) Propagator::dispose(home);
    return sizeof(*this);
  }
  OrTrue(Space& home, OrTrue& p) 
    : Propagator(home,p) {
    x.update(home,p.x);
  }
  virtual Propagator* copy(Space& home) {
    return new (home) OrTrue(home,*this);
  }
  virtual PropCost cost(const Space&, const ModEventDelta&) const {
    return PropCost::linear(PropCost::LO,x.size());
  }
  virtual void reschedule(Space& home) {
    x.reschedule(home,*this,Int::PC_BOOL_VAL);
  }
  // propagation
  virtual ExecStatus propagate(Space& home, const ModEventDelta&) {
    for (int i=x.size(); i--; )
      if (x[i].one())
        return home.ES_SUBSUMED(*this);
      else if (x[i].zero())
        x.move_lst(i);
    if (x.size() == 0)
      return ES_FAILED;
    if (x.size() == 1) {
      GECODE_ME_CHECK(x[0].one(home));
      return home.ES_SUBSUMED(*this);
    }
    return ES_FIX;
  }
};

void dis(Home home, const BoolVarArgs& x, int n) {
  if ((n != 0) && (n != 1))
    throw Int::NotZeroOne("dis");
  GECODE_POST;
  if (n == 0) {
    for (int i=x.size(); i--; )
      GECODE_ME_FAIL(Int::BoolView(x[i]).zero(home));
  } else {
    ViewArray<Int::BoolView> y(home,x);
    GECODE_ES_FAIL(OrTrue::post(home,y));
  }
}
