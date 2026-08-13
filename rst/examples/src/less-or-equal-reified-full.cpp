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

class Less 
  : public BinaryPropagator<Int::IntView,Int::PC_INT_BND> {
public:
  Less(Home home, Int::IntView x0, Int::IntView x1) 
    : BinaryPropagator<Int::IntView,Int::PC_INT_BND>(home,x0,x1) {}
  static ExecStatus post(Home home, 
                         Int::IntView x0, Int::IntView x1) {
    if (x0 == x1)
      return ES_FAILED;
    GECODE_ME_CHECK(x0.le(home,x1.max()));
    GECODE_ME_CHECK(x1.gr(home,x0.min()));
    if (x0.max() >= x1.min())
      (void) new (home) Less(home,x0,x1);
    return ES_OK;
  }
  Less(Space& home, Less& p) 
    : BinaryPropagator<Int::IntView,Int::PC_INT_BND>(home,p) {}
  virtual Propagator* copy(Space& home) {
    return new (home) Less(home,*this);
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
class LeEq
  : public BinaryPropagator<Int::IntView,Int::PC_INT_BND> {
public:
  LeEq(Home home, Int::IntView x0, Int::IntView x1) 
    : BinaryPropagator<Int::IntView,Int::PC_INT_BND>(home,x0,x1) {}
  static ExecStatus post(Home home, 
                         Int::IntView x0, Int::IntView x1) {
    if (x0 == x1)
      return ES_OK;
    GECODE_ME_CHECK(x0.lq(home,x1.max()));
    GECODE_ME_CHECK(x1.gq(home,x0.min()));
    if (x0.max() > x1.min())
      (void) new (home) LeEq(home,x0,x1);
    return ES_OK;
  }
  LeEq(Space& home, LeEq& p) 
    : BinaryPropagator<Int::IntView,Int::PC_INT_BND>(home,p) {}
  virtual Propagator* copy(Space& home) {
    return new (home) LeEq(home,*this);
  }
  virtual ExecStatus propagate(Space& home, const ModEventDelta&)  {
    GECODE_ME_CHECK(x0.lq(home,x1.max()));
    GECODE_ME_CHECK(x1.gq(home,x0.min()));
    if (x0.max() <= x1.min())
      return home.ES_SUBSUMED(*this);
    else 
      return ES_FIX;
  }
};

class ReLeEq
  : public Int::ReBinaryPropagator<Int::IntView,Int::PC_INT_BND,
                                   Int::BoolView> {
public:
  ReLeEq(Home home, Int::IntView x0, Int::IntView x1,
         Int::BoolView b) 
    : Int::ReBinaryPropagator<Int::IntView,Int::PC_INT_BND,Int::BoolView>(home,x0,x1,b) {}
  static ExecStatus post(Home home, 
                         Int::IntView x0, Int::IntView x1,
                         Int::BoolView b) {
    if (b.zero())
      return Less::post(home,x1,x0);
    if (b.one())
      return LeEq::post(home,x0,x1);
    if (x0 == x1) {
      GECODE_ME_CHECK(b.one(home));
    } else {
      switch (Int::rtest_lq(x0,x1)) {
      case Int::RT_TRUE:
        GECODE_ME_CHECK(b.one(home)); break;
      case Int::RT_FALSE:
        GECODE_ME_CHECK(b.zero(home)); break;
      case Int::RT_MAYBE:
        (void) new (home) ReLeEq(home,x0,x1,b); break;
      }
    }
    return ES_OK;
  }
  ReLeEq(Space& home, ReLeEq& p) 
    : Int::ReBinaryPropagator<Int::IntView,Int::PC_INT_BND,Int::BoolView>(home,p) {}
  virtual Propagator* copy(Space& home) {
    return new (home) ReLeEq(home,*this);
  }
  virtual ExecStatus propagate(Space& home, const ModEventDelta&)  {
    if (b.one())
      GECODE_REWRITE(*this,LeEq::post(home(*this),x0,x1));
    if (b.zero())
      GECODE_REWRITE(*this,Less::post(home(*this),x1,x0));
    switch (Int::rtest_lq(x0,x1)) {
    case Int::RT_TRUE:
      GECODE_ME_CHECK(b.one(home)); break;
    case Int::RT_FALSE:
      GECODE_ME_CHECK(b.zero(home)); break;
    case Int::RT_MAYBE:
       return ES_FIX;
    }
    return home.ES_SUBSUMED(*this);
  }
};

void leeq(Home home, IntVar x0, IntVar x1, BoolVar b) {
  GECODE_POST;
  GECODE_ES_FAIL(ReLeEq::post(home,x0,x1,b));
}
