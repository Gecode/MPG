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

// offset map
class OffsetMap {
protected:
  int o;
public:
  OffsetMap(int o0) : o(o0) {}
  int min(int m) const { 
    return m+o; 
  }
  int max(int m) const { 
    return m+o; 
  }
};
class EqualOffset : 
  public BinaryPropagator<Int::IntView,Int::PC_INT_DOM> {
protected:
  int c;
public:
  EqualOffset(Home home, Int::IntView x0, Int::IntView x1, int c0) 
    : BinaryPropagator<Int::IntView,Int::PC_INT_DOM>(home,x0,x1),
      c(c0) {}
  static ExecStatus post(Home home, 
                         Int::IntView x0, Int::IntView x1, int c) {
    if (x0 == x1)
      return (c == 0) ? ES_OK : ES_FAILED;
    (void) new (home) EqualOffset(home,x0,x1,c);
    return ES_OK;
  }
  virtual size_t dispose(Space& home) {
    (void) BinaryPropagator<Int::IntView,Int::PC_INT_DOM>::dispose(home);
    return sizeof(*this);
  }
  EqualOffset(Space& home, EqualOffset& p) 
    : BinaryPropagator<Int::IntView,Int::PC_INT_DOM>(home,p),
      c(p.c) {}
  virtual Propagator* copy(Space& home) {
    return new (home) EqualOffset(home,*this);
  }
  virtual PropCost cost(const Space&, const ModEventDelta&) const {
    return PropCost::binary(PropCost::HI);
  }
  virtual ExecStatus propagate(Space& home, const ModEventDelta&) {
    Int::ViewRanges<Int::IntView> r0(x0);
    OffsetMap om0(-c);
    Iter::Ranges::Map<Int::ViewRanges<Int::IntView>,OffsetMap> 
      mr0(r0,om0);
    GECODE_ME_CHECK(x1.inter_r(home,mr0,false));
    Int::ViewRanges<Int::IntView> r1(x1);
    OffsetMap om1(c);
    Iter::Ranges::Map<Int::ViewRanges<Int::IntView>,OffsetMap>
      mr1(r1,om1);
    GECODE_ME_CHECK(x0.narrow_r(home,mr1,false));
    if (x0.assigned() && x1.assigned())
      return home.ES_SUBSUMED(*this);
    else
      return ES_FIX;
  }
};

void equal(Home home, IntVar x0, IntVar x1, int c) {
  GECODE_POST;
  GECODE_ES_FAIL(EqualOffset::post(home,x0,x1,c));
}
