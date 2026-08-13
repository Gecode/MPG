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

class BoolDomExpr : public BoolExpr::Misc {
protected:
  IntVar x; int l, u;
public:
  BoolDomExpr(IntVar x0, int l0, int u0)
    : x(x0), l(l0), u(u0) {}
  // post member function
  virtual void post(Home home, BoolVar b, bool neg,
                    const IntPropLevels& ipls) {
    (void) ipls;
    if (neg) {
      const int nlu[2][2] = { { Int::Limits::min, l-1 },
                              { u+1, Int::Limits::max } };
      dom(home, x, IntSet(nlu,2), b);
    } else {
      dom(home, x, l, u, b);
    }
  }
  virtual ~BoolDomExpr(void) {}
};
// create Boolean domain expression
BoolExpr dom(IntVar x, int l, int u) {
  return BoolExpr(new BoolDomExpr(x,l,u));
}
