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

class NoneMin : public Brancher {
protected:
  ViewArray<Int::IntView> x;
  // choice definition
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
    : Brancher(home), x(x0) {}
  static void post(Home home, ViewArray<Int::IntView>& x) {
    (void) new (home) NoneMin(home,x);
  }
  virtual size_t dispose(Space& home) {
    (void) Brancher::dispose(home);
    return sizeof(*this);
  }
  NoneMin(Space& home, NoneMin& b)
    : Brancher(home,b) {
    x.update(home,b.x);
  }
  virtual Brancher* copy(Space& home) {
    return new (home) NoneMin(home,*this);
  }
  // status
  virtual bool status(const Space& home) const {
    for (int i=0; i<x.size(); i++)
      if (!x[i].assigned())
        return true;
    return false;
  }
  // choice
  virtual Choice* choice(Space& home) {
    for (int i=0; true; i++)
      if (!x[i].assigned())
        return new PosVal(*this,i,x[i].min());
    GECODE_NEVER;
    return NULL;
  }
  virtual Choice* choice(const Space&, Archive& e) {
    int pos, val;
    e >> pos >> val;
    return new PosVal(*this, pos, val);
  }
  // commit
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
  // print
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
};
void nonemin(Home home, const IntVarArgs& x) {
  if (home.failed()) return;
  ViewArray<Int::IntView> y(home,x);
  NoneMin::post(home,y);
}
