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
#include <gecode/search.hh>

using namespace Gecode;

class SendMostMoney : public Space {
protected:
  IntVarArray l;
public:
  SendMostMoney(void) : l(*this, 8, 0, 9) {
    IntVar s(l[0]), e(l[1]), n(l[2]), d(l[3]), m(l[4]), 
           o(l[5]), t(l[6]), y(l[7]);
    rel(*this, s, IRT_NQ, 0);
    rel(*this, m, IRT_NQ, 0);
    distinct(*this, l);
    IntArgs c(4+4+5); IntVarArgs x(4+4+5);
    c[0]=1000; c[1]=100; c[2]=10; c[3]=1;
    x[0]=s;    x[1]=e;   x[2]=n;  x[3]=d;
    c[4]=1000; c[5]=100; c[6]=10; c[7]=1;
    x[4]=m;    x[5]=o;   x[6]=s;  x[7]=t;
    c[8]=-10000; c[9]=-1000; c[10]=-100; c[11]=-10; c[12]=-1;
    x[8]=m;      x[9]=o;     x[10]=n;    x[11]=e;   x[12]=y;
    linear(*this, c, x, IRT_EQ, 0);
    branch(*this, l, INT_VAR_SIZE_MIN(), INT_VAL_MIN());
  }
  SendMostMoney(SendMostMoney& s) : Space(s) {
    l.update(*this, s.l);
  }
  virtual Space* copy(void) {
    return new SendMostMoney(*this);
  }
  void print(void) const {
    std::cout << l << std::endl;
  }
  // constrain function
  virtual void constrain(const Space& _b) {
    const SendMostMoney& b = static_cast<const SendMostMoney&>(_b);
    IntVar e(l[1]), n(l[2]), m(l[4]), o(l[5]), y(l[7]);
    IntVar b_e(b.l[1]), b_n(b.l[2]), b_m(b.l[4]), 
           b_o(b.l[5]), b_y(b.l[7]);
    int money = (10000*b_m.val()+1000*b_o.val()+100*b_n.val()+
                 10*b_e.val()+b_y.val());
    IntArgs c(5); IntVarArgs x(5);
    c[0]=10000; c[1]=1000; c[2]=100; c[3]=10; c[4]=1;
    x[0]=m;     x[1]=o;    x[2]=n;   x[3]=e;  x[4]=y;
    linear(*this, c, x, IRT_GR, money);
  }
};

// main function
int main(int argc, char* argv[]) {
  SendMostMoney* m = new SendMostMoney;
  BAB<SendMostMoney> e(m);
  delete m;
  while (SendMostMoney* s = e.next()) {
    s->print(); delete s;
  }
  return 0;
}
