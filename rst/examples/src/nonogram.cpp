/*
 *  Authors:
 *    Mikael Lagerkvist <lagerkvist@gecode.dev>
 *
 *  Copyright:
 *    Mikael Lagerkvist, 2008-2026
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
#include <gecode/minimodel.hh>

using namespace Gecode;
// puzzle
const int spec[] =
  { 9, 9,
    // Column hints
    1, 3,
    2, 2, 3,
    2, 2, 2,
    2, 2, 2,
    2, 2, 2,
    2, 2, 2,
    2, 2, 2,
    2, 2, 3,
    1, 3,
    // Row hints
    2, 2, 2,
    2, 4, 4,
    3, 1, 3, 1,
    3, 2, 1, 2,
    2, 1, 1,
    2, 2, 2,
    2, 2, 2,
    1, 3,
    1, 1
  };
class Nonogram : public Script {
  int width, height;
  BoolVarArray b;

  DFA line(const int*& p) {
    // line function
    int nhints = *p++;
    REG r0(0), r1(1);
    REG border = *r0;
    REG separator = +r0;
    REG result = border;
    if (nhints > 0) {
      result += r1(*p,*p);
      p++;
      for (int i=nhints-1; i--; p++)
        result += separator + r1(*p,*p);
    }
    return result + border;
  }
public:
  Nonogram(const Options& opt)
    : Script(opt), width(spec[0]), height(spec[1]),
      b(*this,width*height,0,1) {
    Matrix<BoolVarArray> m(b, width, height);
    // intialize hint pointer
    const int* p = spec+2;
    // column constraints
    for (int w=0; w<width; w++)
      extensional(*this, m.col(w), line(p));
    // row constraints
    for (int h=0; h<height; h++)
      extensional(*this, m.row(h), line(p));
    // branching
    branch(*this, b, BOOL_VAR_AFC_MAX(), BOOL_VAL_MAX());
  }
  Nonogram(Nonogram& s) 
    : Script(s), width(s.width), height(s.height) {
    b.update(*this, s.b);
  }
  virtual Space* copy(void) {
    return new Nonogram(*this);
  }
  virtual void
  print(std::ostream& os) const {
    Matrix<BoolVarArray> m(b, width, height);
    for (int h = 0; h < height; ++h) {
      os << "\t";
      for (int w = 0; w < width; ++w)
        if (m(w,h).assigned())
          os << ((m(w,h).val() == 1) ? '#' : ' ');
        else
          os << "?";
      os << std::endl;
    }
    os << std::endl;
  }
};

int main(int argc, char* argv[]) {
  Options opt("Nonogram");
  opt.solutions(0);
  opt.parse(argc,argv);
  Script::run<Nonogram,DFS,Options>(opt);
  return 0;
}
