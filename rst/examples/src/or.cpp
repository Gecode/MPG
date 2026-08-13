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

class OrTrue : 
  public NaryPropagator<Int::BoolView,Int::PC_BOOL_VAL> {
public:
  OrTrue(Home home, ViewArray<Int::BoolView>& x) 
    : NaryPropagator<Int::BoolView,Int::PC_BOOL_VAL>(home,x) {}
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
  OrTrue(Space& home, OrTrue& p) 
    : NaryPropagator<Int::BoolView,Int::PC_BOOL_VAL>(home,p) {}
  virtual Propagator* copy(Space& home) {
    return new (home) OrTrue(home,*this);
  }
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
typedef MixNaryOnePropagator<Int::BoolView,Int::PC_BOOL_NONE,
                             Int::BoolView,Int::PC_BOOL_VAL>
        OrBase;
class Or : public OrBase {
protected:
  int n_zero;
  Council<Advisor> c;
public:
  Or(Home home, ViewArray<Int::BoolView>& x, Int::BoolView y)
    : OrBase(home,x,y), n_zero(0), c(home) {
    x.subscribe(home,*new (home) Advisor(home,*this,c));
  }
  static ExecStatus post(Home home, ViewArray<Int::BoolView>& x, Int::BoolView y) {
    x.unique();
    if (y.one())
      return OrTrue::post(home,x);
    if (y.zero()) {
      for (int i=x.size(); i--; )
        GECODE_ME_CHECK(x[i].zero(home));
      return ES_OK;
    }
    for (int i=x.size(); i--; )
      if (x[i].one()) {
        GECODE_ME_CHECK(y.one(home));
        return ES_OK;
      } else if (x[i].zero()) {
        x.move_lst(i);
      }
    if (x.size() == 0) {
      GECODE_ME_CHECK(y.zero(home));
    } else {
      (void) new (home) Or(home,x,y);
    }
    return ES_OK;
  }
  virtual size_t dispose(Space& home) {
    x.cancel(home,Advisors<Advisor>(c).advisor());
    c.dispose(home);
    (void) OrBase::dispose(home);
    return sizeof(*this);
  }
  Or(Space& home, Or& p)
    : OrBase(home,p), n_zero(p.n_zero) {
    c.update(home,p.c);
  }
  virtual Propagator* copy(Space& home) {
    return new (home) Or(home,*this);
  }
  virtual PropCost cost(const Space&, const ModEventDelta&) const {
    return PropCost::unary(PropCost::LO);
  }
  // advise
  virtual ExecStatus advise(Space&, Advisor&, const Delta& d) {
    if (Int::BoolView::zero(d) && (++n_zero < x.size()))
      return ES_FIX;
    else
      return ES_NOFIX;
  }
  // re-scheduling
  virtual void reschedule(Space& home) {
    if (y.assigned() || (n_zero == x.size()))
      Int::BoolView::schedule(home, *this, Int::ME_BOOL_VAL);
    for (int i=x.size(); i--; )
      if (x[i].one()) {
        Int::BoolView::schedule(home, *this, Int::ME_BOOL_VAL);
        return;
      }
  }
  // propagation
  virtual ExecStatus propagate(Space& home, const ModEventDelta&) {
    if (y.one())
      GECODE_REWRITE(*this,OrTrue::post(home(*this),x));
    if (y.zero()) {
      for (int i = x.size(); i--; )
        GECODE_ME_CHECK(x[i].zero(home));
    } else if (n_zero == x.size()) {
      GECODE_ME_CHECK(y.zero(home));
    } else {
      GECODE_ME_CHECK(y.one(home));
    }
    return home.ES_SUBSUMED(*this);
  }
};

void dis(Home home, const BoolVarArgs& x, BoolVar y) {
  GECODE_POST;
  ViewArray<Int::BoolView> vx(home,x);
  GECODE_ES_FAIL(Or::post(home,vx,y));
}
