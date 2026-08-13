/*
 *  Authors:
 *    Guido Tack <tack@gecode.dev>
 *
 *  Copyright:
 *    Guido Tack, 2008-2026
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

class LatinSquare : public Script {
protected:
  const int n;
  IntVarArray x;
public:
  /// Branching variants
  enum {
    SYMMETRY_NONE,      ///< No symmetry breaking
    SYMMETRY_LDSB       ///< Use LDSB for symmetry breaking
  };

  LatinSquare(const SizeOptions& opt)
    : Script(opt), n(opt.size()), x(*this,n*n,0,n-1) {
    Matrix<IntVarArgs> m(x, n, n);
    for (int i=0; i<n; i++)
      distinct(*this, m.row(i));
    for (int i=0; i<n; i++)
      distinct(*this, m.col(i));
    if (opt.symmetry() == SYMMETRY_NONE) {
      branch(*this, x, INT_VAR_NONE(), INT_VAL_MIN());
    } else {
    // symmetry breaking
      Symmetries syms;
      syms << ValueSymmetry(IntArgs::create(n,0));
      // row/column symmetry
      IntVarArgs rows;
      for (int r = 0; r < m.height(); r++)
        rows << m.row(r);
      syms << VariableSequenceSymmetry(rows, m.width());
      IntVarArgs cols;
      for (int c = 0; c < m.width(); c++)
        cols << m.col(c);
      syms << VariableSequenceSymmetry(cols, m.height());
      branch(*this, x, INT_VAR_NONE(), INT_VAL_MIN(), syms);
    }
  }
  LatinSquare(LatinSquare& s)
    : Script(s), n(s.n) {
    x.update(*this, s.x);
  }
  virtual Space* copy(void) {
    return new LatinSquare(*this);
  }
  virtual void print(std::ostream& os) const {
    os << x << std::endl;
  }
};
int main(int argc, char* argv[]) {
  SizeOptions opt("Latin Square");
  opt.size(8);
  opt.solutions(1);
  opt.symmetry(LatinSquare::SYMMETRY_LDSB);
  opt.symmetry(LatinSquare::SYMMETRY_NONE,"none");
  opt.symmetry(LatinSquare::SYMMETRY_LDSB,"ldsb");
  opt.parse(argc,argv);
  Script::run<LatinSquare,DFS,SizeOptions>(opt);
  return 0;
}
