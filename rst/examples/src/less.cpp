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

class Less : public Propagator {
protected:
  Int::IntView x0, x1;
public:
  // posting
  Less(Space& home, Int::IntView y0, Int::IntView y1) 
    : Propagator(home), x0(y0), x1(y1) {
    x0.subscribe(home,*this,Int::PC_INT_DOM);
    x1.subscribe(home,*this,Int::PC_INT_DOM);
  }
  static ExecStatus post(Space& home, 
                         Int::IntView x0, Int::IntView x1) {
    (void) new (home) Less(home,x0,x1);
    return ES_OK;
  }
  // disposal
  virtual size_t dispose(Space& home) {
    x0.cancel(home,*this,Int::PC_INT_DOM);
    x1.cancel(home,*this,Int::PC_INT_DOM);
    (void) Propagator::dispose(home);
    return sizeof(*this);
  }
  // copying
  Less(Space& home, Less& p) 
    : Propagator(home,p) {
    x0.update(home,p.x0);
    x1.update(home,p.x1);
  }
  virtual Propagator* copy(Space& home) {
    return new (home) Less(home,*this);
  }
  // cost computation
  virtual PropCost cost(const Space&, const ModEventDelta&) const {
    return PropCost::binary(PropCost::LO);
  }
  // re-scheduling
  virtual void reschedule(Space& home) {
    x0.reschedule(home,*this,Int::PC_INT_DOM);
    x1.reschedule(home,*this,Int::PC_INT_DOM);
  }
  // propagation
  virtual ExecStatus propagate(Space& home, const ModEventDelta&)  {
    if (x0.le(home,x1.max()) == Int::ME_INT_FAILED)
      return ES_FAILED;
    if (x1.gr(home,x0.min()) == Int::ME_INT_FAILED)
      return ES_FAILED;
    if (x0.assigned() && x1.assigned())
      return home.ES_SUBSUMED(*this);
    else 
      return ES_NOFIX;
  }
};

void less(Space& home, IntVar x0, IntVar x1) {
  // constraint post function
  Int::IntView y0(x0), y1(x1);
  if (Less::post(home,y0,y1) != ES_OK)
    home.fail();
}
