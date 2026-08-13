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

class EqNGL : public NGL {
protected:
  Int::IntView x; int n;
public:
  EqNGL(Space& home, Int::IntView x0, int n0)
    : NGL(home), x(x0), n(n0) {}
  EqNGL(Space& home, EqNGL& ngl)
    : NGL(home, ngl), n(ngl.n) {
    x.update(home, ngl.x);
  }
  // status
  virtual NGL::Status status(const Space& home) const {
    if (x.assigned())
      return (x.val() == n) ? NGL::SUBSUMED : NGL::FAILED;
    else 
      return x.in(n) ? NGL::NONE : NGL::FAILED;
  }
  // prune
  virtual ExecStatus prune(Space& home) {
    return me_failed(x.nq(home,n)) ? ES_FAILED : ES_OK;
  }
  // subscribe and cancel
  virtual void subscribe(Space& home, Propagator& p) {
    x.subscribe(home, p, Int::PC_INT_VAL);
  }
  virtual void cancel(Space& home, Propagator& p) {
    x.cancel(home, p, Int::PC_INT_VAL);
  }
  // re-scheduling
  virtual void reschedule(Space& home, Propagator& p) {
    x.reschedule(home, p, Int::PC_INT_VAL);
  }
  virtual NGL* copy(Space& home) {
    return new (home) EqNGL(home,*this);
  }
  virtual size_t dispose(Space& home) {
    (void) NGL::dispose(home);
    return sizeof(*this);
  }
};

class NoneMin : public Brancher {
protected:
  ViewArray<Int::IntView> x;
  mutable int start;
  class PosVal : public Choice {
  public:
    int pos; int val;
    PosVal(const NoneMin& b, int p, int v)
      : Choice(b,2), pos(p), val(v) {}
    virtual void archive(Archive& e) const {
      Choice::archive(e);
      e << pos << val;
    }
  };
public:
  NoneMin(Home home, ViewArray<Int::IntView>& x0)
    : Brancher(home), x(x0), start(0) {}
  static void post(Home home, ViewArray<Int::IntView>& x) {
    (void) new (home) NoneMin(home,x);
  }
  virtual size_t dispose(Space& home) {
    (void) Brancher::dispose(home);
    return sizeof(*this);
  }
  NoneMin(Space& home, NoneMin& b)
    : Brancher(home,b), start(b.start) {
    x.update(home,b.x);
  }
  virtual Brancher* copy(Space& home) {
    return new (home) NoneMin(home,*this);
  }
  virtual bool status(const Space& home) const {
    for (int i=start; i<x.size(); i++)
      if (!x[i].assigned()) {
        start = i; return true;
      }
    return false;
  }
  virtual Choice* choice(Space& home) {
    return new PosVal(*this,start,x[start].min());
  }
  virtual Choice* choice(const Space&, Archive& e) {
    int pos, val;
    e >> pos >> val;
    return new PosVal(*this, pos, val);
  }
  virtual ExecStatus commit(Space& home, 
                            const Choice& c,
                            unsigned int a) {
    const PosVal& pv = static_cast<const PosVal&>(c);
    int pos=pv.pos, val=pv.val;
    if (a == 0)
      return me_failed(x[pos].eq(home,val)) ? ES_FAILED : ES_OK;
    else
      return me_failed(x[pos].nq(home,val)) ? ES_FAILED : ES_OK;
  }
  virtual void print(const Space& home, const Choice& c,
                     unsigned int a,
                     std::ostream& o) const {
    const PosVal& pv = static_cast<const PosVal&>(c);
    int pos=pv.pos, val=pv.val;
    if (a == 0)
      o << "x[" << pos << "] = " << val;
    else
      o << "x[" << pos << "] != " << val;
  }
  // no-good literal creation
  virtual NGL* ngl(Space& home, const Choice& c,
                   unsigned int a) const {
    const PosVal& pv = static_cast<const PosVal&>(c);
    int pos=pv.pos, val=pv.val;
    if (a == 0)
      return new (home) EqNGL(home, x[pos], val);
    else
      return NULL;
  }
};
void nonemin(Home home, const IntVarArgs& x) {
  if (home.failed()) return;
  ViewArray<Int::IntView> y(home,x);
  NoneMin::post(home,y);
}
