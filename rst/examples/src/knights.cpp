/*
 *  Authors:
 *    Mikael Lagerkvist <lagerkvist@gecode.dev>
 *    Christian Schulte <schulte@gecode.dev>
 *
 *  Copyright:
 *    Mikael Lagerkvist, 2008-2026
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

#include <climits>
#include <gecode/driver.hh>

using namespace Gecode;

// brancher
class Warnsdorff : public Brancher {
protected:
  ViewArray<Int::IntView> x;
  mutable int start;
  class PosVal : public Choice {
  public:
    int pos; int val;
    PosVal(const Warnsdorff& b, int p, int v)
      : Choice(b,2), pos(p), val(v) {}
    virtual void archive(Archive& e) const {
      Choice::archive(e);
      e << pos << val;
    }
  };
public:
  Warnsdorff(Home home, ViewArray<Int::IntView>& x0) 
    : Brancher(home), x(x0), start(0) {}
  static void post(Home home, ViewArray<Int::IntView>& x) {
    (void) new (home) Warnsdorff(home,x);
  }
  virtual size_t dispose(Space&) {
    return sizeof(*this);
  }
  Warnsdorff(Space& home, Warnsdorff& b) 
    : Brancher(home,b), start(b.start) {
    x.update(home,b.x);
  }
  virtual Brancher* copy(Space& home) {
    return new (home) Warnsdorff(home, *this);
  }
  // status function
  virtual bool status(const Space&) const {
    for (int n=0; n<x.size(); n++) {
      if (!x[start].assigned()) 
        return true;
      start = x[start].val();
    }
    return false;
  }
  // choice function
  virtual Choice* choice(Space&) {
    int n=-1; unsigned int size=UINT_MAX;
    for (Int::ViewValues<Int::IntView> i(x[start]); i(); ++i)
      if (x[i.val()].size() < size) {
        n=i.val(); size=x[n].size();
      }
    return new PosVal(*this,start,n);
  }
  virtual Choice* choice(const Space&, Archive& e) {
    int pos, val;
    e >> pos >> val;
    return new PosVal(*this, pos, val);
  }
  virtual ExecStatus commit(Space& home, const Gecode::Choice& c, 
                            unsigned int a) {
    const PosVal& pv = static_cast<const PosVal&>(c);
    if (a == 0)
      return me_failed(x[pv.pos].eq(home,pv.val)) ? ES_FAILED : ES_OK;
    else 
      return me_failed(x[pv.pos].nq(home,pv.val)) ? ES_FAILED : ES_OK;
  }
  /// Print explanation
  virtual void print(const Space&, const Gecode::Choice& c, 
                     unsigned int a,
                     std::ostream& o) const {
    const PosVal& pv = static_cast<const PosVal&>(c);
    o << "x[" << pv.pos << "] "
      << ((a == 0) ? "=" : "!=")
      << " " << pv.val;
  }
};

void warnsdorff(Home home, const IntVarArgs& x) {
  ViewArray<Int::IntView> y(home,x);
  Warnsdorff::post(home,y);
}
class Knights : public Script {
protected:
  const int n;
  IntVarArray succ;
public:
  int f(int x, int y) const { return x + y*n; }
  int x(int f) const { return f%n; }
  int y(int f) const { return f/n; }
  IntSet neighbors(int i) {
    static const int moves[8][2] = {
      {-2,-1}, {-2,1}, {-1,-2}, {-1,2}, {1,-2}, {1,2}, {2,-1}, {2,1}
    };
    int nbs[8]; int n_nbs = 0;
    for (int m=0; m<8; m++) {
      int nx = x(i) + moves[m][0], ny = y(i) + moves[m][1];
      if ((nx >= 0) && (nx < n) && (ny >= 0) && (ny < n))
        nbs[n_nbs++] = f(nx,ny);
    }
    return IntSet(nbs,n_nbs);
  }
  Knights(const SizeOptions& opt)
    : Script(opt), n(opt.size()), succ(*this,n*n,0,n*n-1) {
   // knight's moves
    for (int i=0; i<n*n; i++)
      dom(*this, succ[i], neighbors(i));
    // fix first move
    rel(*this, succ[0], IRT_EQ, f(1,2));
    // Hamiltonian circuit
    circuit(*this, succ, IPL_DOM);
    warnsdorff(*this, succ);
  }
  Knights(Knights& s) : Script(s), n(s.n) {
    succ.update(*this, s.succ);
  }
  virtual Space* copy(void) {
    return new Knights(*this);
  }
  virtual void
  print(std::ostream& os) const {
    int* jump = new int[n*n];
    {
      int j=0;
      for (int i=0; i<n*n; i++) {
        jump[j]=i; j=succ[j].min();
      }
    }
    os << "\t";
    for (int i = 0; i < n; i++) {
      for (int j = 0; j < n; j++) {
        os.width(3);
        os << jump[f(i,j)] << " ";
        }
        os << std::endl << "\t";
    }
    os << std::endl;
    delete [] jump;
  }
};

int main(int argc, char* argv[]) {
  SizeOptions opt("Knights");
  opt.size(6);
  opt.c_d(100); opt.a_d(100);
  opt.parse(argc,argv);
  Script::run<Knights,DFS,SizeOptions>(opt);
  return 0;
}
