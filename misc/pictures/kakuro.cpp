/*
 *  Authors:
 *    Christian Schulte <schulte@gecode.org>
 *
 *  Copyright:
 *    Christian Schulte, 2008-2010
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

const int board[] = {
  // Dimension w x h
  12, 10,
  // Vertical hints
   3, 0, 3, 7,     4, 0, 6,21,     7, 0, 4,29,     8, 0, 2,17,
  10, 0, 4,29,    11, 0, 3,23,     2, 1, 3, 6,     6, 1, 2,16,
   9, 1, 4,14,     1, 2, 2, 4,     5, 2, 2, 3,     8, 3, 6,22,
   3, 4, 4,10,     2, 5, 4,11,     5, 5, 4,10,     7, 5, 2,10,
  10, 5, 3,24,    11, 5, 2,16,     1, 6, 3, 7,     6, 6, 2, 9,
   9, 6, 3,23,     4, 7, 2, 4,    
  -1,
  // Horizontal hints
   2, 1, 2, 4,     6, 1, 2,17,     9, 1, 2,16,     1, 2, 3, 6,
   5, 2, 6,39,     0, 3, 7,28,     8, 3, 3,24,     0, 4, 2, 3,
   3, 4, 2, 3,     6, 4, 4,20,     2, 5, 2, 9,     7, 5, 2, 4,
   1, 6, 4,10,     6, 6, 2, 3,     9, 6, 2,16,     0, 7, 3, 6,
   4, 7, 7,42,     0, 8, 6,21,     7, 8, 3,21,     0, 9, 2, 4,
   3, 9, 2, 3,     7, 9, 2,16,    
  -1
};

class DistinctLinear : public Space {
protected:
  IntVarArray x;
public:
  DistinctLinear(int n, int s) : x(*this,n,1,9) {
    distinct(*this, x);
    linear(*this, x, IRT_EQ, s);
    branch(*this, x, INT_VAR_NONE, INT_VAL_SPLIT_MIN);
  }
  IntArgs solution(void) const {
    IntArgs s(x.size());
    for (int i=0; i<x.size(); i++)
      s[i]=x[i].val();
    return s;
  }
  DistinctLinear(bool share, DistinctLinear& s) : Space(share,s) {
    x.update(*this, share, s.x);
  }
  virtual Space* copy(bool share) {
    return new DistinctLinear(share,*this);
  }
};

void distinctlinear(Home home, const IntVarArgs& x, int c) {
  DistinctLinear* e = new DistinctLinear(x.size(),c);
  DFS<DistinctLinear> d(e);
  delete e;
  TupleSet ts;
  while (DistinctLinear* s = d.next()) {
    ts.add(s->solution()); delete s;
  }
  ts.finalize();
  extensional(home, x, ts);
}

class Kakuro : public Script {
protected:
  const int w, h;
  IntVarArray f;
public:
  IntVar init(IntVar& x) {
    if (x.min() == 0)
      x.init(*this,1,9);
    return x;
  }
  void hint(const IntVarArgs& x, int s) {
    if (x.size() < 8)
      linear(*this, x, IRT_EQ, s, ICL_DOM);
    else if (x.size() == 8)
      rel(*this, x, IRT_NQ, 9*(9+1)/2 - s);
    distinct(*this, x, ICL_DOM);
  }
  Kakuro(const Options& opt)
    : w(board[0]),  h(board[1]), f(*this,w*h) {
    IntVar black(*this,0,0);
    for (int i=0; i<w*h; i++)
      f[i] = black;
    Matrix<IntVarArray> b(f,w,h);
    const int* k = &board[2];
    while (*k >= 0) {
      int x=*k++; int y=*k++; int n=*k++; int s=*k++;
      IntVarArgs col(n);
      for (int i=0; i<n; i++)
        col[i]=init(b(x,y+i+1));
      hint(col,s);
    }
    k++;
    while (*k >= 0) {
      int x=*k++; int y=*k++; int n=*k++; int s=*k++;
      IntVarArgs row(n);
      for (int i=0; i<n; i++)
        row[i]=init(b(x+i+1,y));
      hint(row,s);
    }
/*
    for (int x=0; x<w; x++)
      for (int y=0; y<h; y++)
        if (b(x,y).min() == 0)
          std::cout << "\\hint{" << x << "}{" << (h-y-1) << "}";
*/

  }
  // Constructor for cloning s
  Kakuro(bool share, Kakuro& s) : Script(share,s), w(s.w), h(s.h) {
    f.update(*this, share, s.f);
  }
  // Perform copying during cloning
  virtual Space* copy(bool share) {
    return new Kakuro(share,*this);
  }
  // Print solution
  virtual void print(std::ostream& os) const {
    Matrix<IntVarArray> b(f,w,h);
    for (int y=0; y<h; y++) {

      for (int x=0; x<w; x++) 
        for (IntVarValues i(b(x,y)); i(); ++i)
          switch (i.val()) {
          case 1:
            os << "\\pone{" << x << "}{" << (h-y-1) << "}"; break;
          case 2:
            os << "\\ptwo{" << x << "}{" << (h-y-1) << "}"; break;
          case 3:
            os << "\\pthree{" << x << "}{" << (h-y-1) << "}"; break;
          case 4:
            os << "\\pfour{" << x << "}{" << (h-y-1) << "}"; break;
          case 5:
            os << "\\pfive{" << x << "}{" << (h-y-1) << "}"; break;
          case 6:
            os << "\\psix{" << x << "}{" << (h-y-1) << "}"; break;
          case 7:
            os << "\\pseven{" << x << "}{" << (h-y-1) << "}"; break;
          case 8:
            os << "\\peight{" << x << "}{" << (h-y-1) << "}"; break;
          case 9:
            os << "\\pnine{" << x << "}{" << (h-y-1) << "}"; break;
          }

    }
  }
};
int main(int argc, char* argv[]) {
  Options opt("Kakuro");
  opt.parse(argc,argv);
  Script::run<Kakuro,DFS,Options>(opt);
  return 0;
}
