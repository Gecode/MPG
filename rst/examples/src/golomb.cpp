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

class GolombRuler : public IntMinimizeScript {
protected:
  IntVarArray m;
public:
  GolombRuler(const SizeOptions& opt)
    : IntMinimizeScript(opt),
      m(*this,opt.size(),0,
        (opt.size() < 31) 
          ? (1 << (opt.size()-1)) - 1 
          : Int::Limits::max) {
    // constraining marks
    rel(*this, m[0], IRT_EQ, 0);
    rel(*this, m, IRT_LE);
    // number of marks and distances
    const int n = m.size();
    const int n_d = (n*n-n)/2;
    // posting distance constraints
    IntVarArgs d(n_d);
    for (int k=0, i=0; i<n-1; i++)
      for (int j=i+1; j<n; j++, k++)
        d[k] = expr(*this, m[j] - m[i]);
    // implied constraints
    for (int k=0, i=0; i<n-1; i++)
      for (int j=i+1; j<n; j++, k++)
        rel(*this, d[k], IRT_GQ, (j-i)*(j-i+1)/2);
    // distances must be distinct
    distinct(*this, d, IPL_BND);
    // symmetry breaking
    if (n > 2)
      rel(*this, d[0], IRT_LE, d[n_d-1]);
    // branching
    branch(*this, m, INT_VAR_NONE(), INT_VAL_MIN());
  }
  virtual IntVar cost(void) const {
    return m[m.size()-1];
  }
  /// Print solution
  virtual void print(std::ostream& os) const {
    os << m << std::endl;
  }
  // Constructor for cloning \a s
  GolombRuler(GolombRuler& s)
    : IntMinimizeScript(s) {
    m.update(*this, s.m);
  }
  // Copy during cloning
  virtual Space* copy(void) {
    return new GolombRuler(*this);
  }
};

int main(int argc, char* argv[]) {
  SizeOptions opt("GolombRuler");
  opt.solutions(0);
  opt.size(10);
  opt.parse(argc,argv);
  IntMinimizeScript::run<GolombRuler,BAB,SizeOptions>(opt);
  return 0;
}
