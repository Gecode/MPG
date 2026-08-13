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

#include <gecode/driver.hh>
#include <gecode/int.hh>
#include <gecode/minimodel.hh>

using namespace Gecode;

class SendMostMoney : public IntMaximizeScript {
protected:
  IntVarArray l;
  IntVar money;
public:
  enum {
    MODEL_SINGLE, MODEL_CARRY
  };
  SendMostMoney(const Options& opt)
    : IntMaximizeScript(opt),
      l(*this, 8, 0, 9), money(*this,0,100000) {
    IntVar s(l[0]), e(l[1]), n(l[2]), d(l[3]), m(l[4]), 
           o(l[5]), t(l[6]), y(l[7]);
    rel(*this, s != 0);
    rel(*this, m != 0);
    distinct(*this, l);
    switch (opt.model()) {
    case MODEL_SINGLE:
      rel(*this,             1000*s + 100*e + 10*n + d
                           + 1000*m + 100*o + 10*s + t
                == 10000*m + 1000*o + 100*n + 10*e + y);
      break;
    case MODEL_CARRY:
      // using carries
      {
        IntVar c0(*this, 0, 1), c1(*this, 0, 1), 
               c2(*this, 0, 1), c3(*this, 0, 1);
        rel(*this,      d + t == y + 10 * c0);
        rel(*this, c0 + n + s == e + 10 * c1);
        rel(*this, c1 + e + o == n + 10 * c2);
        rel(*this, c2 + s + m == o + 10 * c3);
        rel(*this, c3         == m);
      }
      break;
    }
    rel(*this, money == 10000*m + 1000*o + 100*n + 10*e + y);
    branch(*this, l, INT_VAR_SIZE_MIN(), INT_VAL_MIN());
  }
  SendMostMoney(SendMostMoney& s)
    : IntMaximizeScript(s) {
    l.update(*this, s.l);
    money.update(*this, s.money);
  }
  virtual Space* copy(void) {
    return new SendMostMoney(*this);
  }
  virtual IntVar cost(void) const {
    return money;
  }
  virtual void print(std::ostream& os) const {
    os << l << std::endl;
  }
};

int main(int argc, char* argv[]) {
  // commandline options
  Options opt("SEND + MOST = MONEY");
  opt.model(SendMostMoney::MODEL_SINGLE, 
            "single", "use single linear equation");
  opt.model(SendMostMoney::MODEL_CARRY, 
            "carry", "use carry");
  opt.model(SendMostMoney::MODEL_SINGLE);
  opt.solutions(0);
  opt.parse(argc,argv);
  // run script
  Script::run<SendMostMoney,BAB,Options>(opt);
  return 0;
}
