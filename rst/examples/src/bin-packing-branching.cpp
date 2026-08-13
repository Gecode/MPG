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
  // initialize free capacity
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

// CDBF
class CDBF : public Brancher {
protected:
  ViewArray<Int::IntView> load;
  ViewArray<Int::IntView> bin;
  IntSharedArray size;
  mutable int item;
  // CDBF choice
  class Choice : public Gecode::Choice {
  public:
    int  item;
    int* same;
    int  n_same;
    Choice(const Brancher& b, unsigned int a, int i, int* s, int n_s)
      : Gecode::Choice(b,a), item(i), 
        same(heap.alloc<int>(n_s)), n_same(n_s) {
      for (int k=0; k<n_same; k++)
        same[k] = s[k];
    }
    virtual ~Choice(void) {
      heap.free<int>(same,n_same);
    }
    virtual void archive(Archive& e) const {
      Gecode::Choice::archive(e);
      e << alternatives() << item << n_same;
      for (int i=n_same; i--;) e << same[i];
    }
  };
public:
  CDBF(Home home, ViewArray<Int::IntView>& l, 
                  ViewArray<Int::IntView>& b,
                  IntSharedArray& s) 
    : Brancher(home), load(l), bin(b), size(s), item(0) {
    home.notice(*this,AP_DISPOSE);
  }
  static void post(Home home, ViewArray<Int::IntView>& l, 
                              ViewArray<Int::IntView>& b,
                              IntSharedArray& s) {
    (void) new (home) CDBF(home, l, b, s);
  }
  // status function
  virtual bool status(const Space&) const {
    for (int i = item; i < bin.size(); i++)
      if (!bin[i].assigned()) {
        item = i; return true;
      }
    return false;
  }
  // choice function
  virtual Gecode::Choice* choice(Space& home) {
    int n = bin.size(), m = load.size();
    Region region;
    // initialize free space in bins
    int* free = region.alloc<int>(m);
    for (int j=0; j<m; j++)
      free[j] = load[j].max();
    for (int i=0; i<n; i++)
      if (bin[i].assigned())
        free[bin[i].val()] -= size[i];
    // initialize bins with same slack
    int slack = INT_MAX;
    unsigned int n_possible = 0;
    unsigned int n_same = 0;
    int* same = region.alloc<int>(m+1);
    same[n_same++] = -1;
    // find best fit
    for (Int::ViewValues<Int::IntView> j(bin[item]); j(); ++j) 
      if (size[item] <= free[j.val()]) {
        n_possible++;
        if (free[j.val()] - size[item] < slack) {
          slack = free[j.val()] - size[item];
          n_same = 0;
          same[n_same++] = j.val(); 
        } else if (free[j.val()] - size[item] == slack) {
          same[n_same++] = j.val();
        }
      }
    // create choice
    if ((slack == 0) || 
        (n_same == n_possible) || 
        (n_possible == 0))
      return new Choice(*this, 1, item, same, 1);
    else
      return new Choice(*this, 2, item, same, n_same);
  }
  // commit function
  virtual ExecStatus commit(Space& home, const Gecode::Choice& _c, 
                            unsigned int a) {
    const Choice& c = static_cast<const Choice&>(_c);
    if (a == 0) {
      // commit to first alternative
      GECODE_ME_CHECK(bin[c.item].eq(home, c.same[0]));
    } else {
      // commit to second alternative
      int i = c.item;
      do {
        Iter::Values::Array same(c.same, c.n_same);
        GECODE_ME_CHECK(bin[i++].minus_v(home, same));
      } while ((i < bin.size()) && 
               (size[i] == size[c.item]));
    }
    return ES_OK;
  }
  // Print information for brancher
  virtual void print(const Space&, const Gecode::Choice& _c, 
                     unsigned int a,
                     std::ostream& o) const {
    const Choice& c = static_cast<const Choice&>(_c);
    if (a == 0) {
      o << "bin[" << c.item << "] = " << c.same[0];
    } else {
      o << "bin[" << c.item;
      for (int i = c.item+1; (i<bin.size()) && 
                             (size[i] == size[c.item]); i++)
        o << "," << i;
      o << "] != ";
      for (int i = 0; i<c.n_same-1; i++)
        o << c.same[i] << ",";
      o << c.same[c.n_same-1];
    }
  }
  // Initialize brancher
  CDBF(Space& home, CDBF& cdbf) 
    : Brancher(home, cdbf), size(cdbf.size), item(cdbf.item) {
    load.update(home, cdbf.load);
    bin.update(home, cdbf.bin);
  }
  // Copy brancher
  virtual Actor* copy(Space& home) {
    return new (home) CDBF(home, *this);
  }
  // Create choice from archive
  virtual const Gecode::Choice*
  choice(const Space& home, Archive& e) {
    int alt, item, n_same;
    e >> alt >> item >> n_same;
    Region region;
    int* same = region.alloc<int>(n_same);
    for (int i=n_same; i--;) 
      e >> same[i];
    return new Choice(*this, alt, item, same, n_same);
  }
  // Delete brancher and return its size
  virtual size_t dispose(Space& home) {
    home.ignore(*this,AP_DISPOSE);
    size.~IntSharedArray();
    (void) Brancher::dispose(home);
    return sizeof(*this);
  }
};

void cdbf(Home home, const IntVarArgs& l, const IntVarArgs& b,
                     const IntArgs& s) {
  if (b.size() != s.size())
    throw Int::ArgumentSizeMismatch("cdbf");      
  ViewArray<Int::IntView> load(home, l);
  ViewArray<Int::IntView> bin(home, b);
  IntSharedArray size(s);
  CDBF::post(home, load, bin, size);
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
    IntArgs sizes(n, size);
    binpacking(*this, load, bin, sizes);
    // pack items that require a bin
    for (int i=0; (i < n) && (i < u) && (size[i] * 2 > c); i++)
      rel(*this, bin[i] == i);
    // branching
    branch(*this, bins, INT_VAL_MIN());
    cdbf(*this, load, bin, sizes);
  }
  // Cost function
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
