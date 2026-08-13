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

#include <algorithm>

#include <gecode/driver.hh>
#include <gecode/minimodel.hh>

using namespace Gecode;
// instance data
const int c = 100;
const int n = 50;
const int size[n] = {
  99,98,95,95,95,94,94,91,88,87,86,85,76,74,73,71,68,60,55,54,51,
  45,42,40,39,39,36,34,33,32,32,31,31,30,29,26,26,23,21,21,21,19,
  18,18,16,15,5,5,4,1
};
// compute lower bound
int lower(void) {
  int s=0;
  for (int i=0; i<n; i++)
    s += size[i];
  return (s + c - 1) / c;
}
// compute upper bound
int upper(void) {
  int* free = new int[n];
  for (int i=0; i<n; i++)
    free[i] = c;
  int u=0;
  // pack items into free bins
  for (int i=0; i<n; i++) {
    int j=0;
    // find free bin
    while (free[j] < size[i])
      j++;
    free[j] -= size[i];
    u = std::max(u,j);
  }
  delete [] free;
  return u+1;
}
class BinPacking : public IntMinimizeScript {
protected:
  const int l;
  const int u;  
  IntVarArray load;
  IntVarArray bin;
  IntVar bins;
public:
  BinPacking(const Options& opt) 
    : IntMinimizeScript(opt),
      l(lower()), u(upper()),
      load(*this, u, 0, c), 
      bin(*this, n, 0, u-1), bins(*this, l, u) {
    // excess bins
    for (int i=1; i<=u; i++)
      rel(*this, (bins < i) == (load[i-1] == 0));
    int s=0;
    for (int i=0; i<n; i++)
      s += size[i];
    IntArgs sizes(n, size);
    // loads add up to item sizes
    linear(*this, load, IRT_EQ, s);
    // loads are equal to packed items
    BoolVarArgs _x(*this, n*u, 0, 1);
    Matrix<BoolVarArgs> x(_x, n, u);
    for (int i=0; i<n; i++)
      channel(*this, x.col(i), bin[i]);
    for (int j=0; j<u; j++)
      linear(*this, sizes, x.row(j), IRT_EQ, load[j]);
    // symmetry breaking
    for (int i=1; i<n; i++)
      if (size[i-1] == size[i])
        rel(*this, bin[i-1] <= bin[i]);
    // pack items that require a bin
    for (int i=0; (i < n) && (i < u) && (size[i] * 2 > c); i++)
      rel(*this, bin[i] == i);
    // branching
    branch(*this, bins, INT_VAL_MIN());
    branch(*this, bin, INT_VAR_NONE(), INT_VAL_MIN());
  }
  virtual IntVar cost(void) const {
    return bins;
  }
  // Constructor for cloning s
  BinPacking(BinPacking& s) 
    : IntMinimizeScript(s), l(s.l), u(s.u) {
    load.update(*this, s.load);
    bin.update(*this, s.bin);
    bins.update(*this, s.bins);
  }
  // Copy during cloning
  virtual Space* copy(void) {
    return new BinPacking(*this);
  }
  // Print solution
  virtual void print(std::ostream& os) const {
    os << "Bins used: " << bins << " (from " << u << " bins)." << std::endl;
    for (int j=0; j<u; j++) {
      bool fst = true;
      os << "\t[" << j << "]={";
      for (int i=0; i<n; i++)
        if (bin[i].assigned() && (bin[i].val() == j)) {
          if (fst) {
            fst = false;
          } else {
            os << ",";
          }
          os << i;
        }
      os << "} #" << load[j] << std::endl;
    }
    if (!bin.assigned()) {
      os << std::endl 
         << "Unpacked items:" << std::endl;
      for (int i=0;i<n; i++)
        if (!bin[i].assigned())
          os << "\t[" << i << "] = " << bin[i] << std::endl;
    }
  }
};
int main(int argc, char* argv[]) {
  Options opt("BinPacking");
  opt.solutions(0);
  opt.parse(argc,argv);
  IntMinimizeScript::run<BinPacking,BAB,Options>(opt);
  return 0;
}
