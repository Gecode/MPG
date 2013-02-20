/*
 *  Authors:
 *    Mikael Lagerkvist <lagerkvist@gecode.org>
 *    Christian Schulte <schulte@gecode.org>
 *
 *  Copyright:
 *    Mikael Lagerkvist, 2008
 *    Christian Schulte, 2008
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
#include <gecode/graph.hh>

using namespace Gecode;

class Warnsdorff : public Brancher {
protected:
  ViewArray<Int::IntView> x;
  mutable int start;
  class Choice : public Gecode::Choice {
  public:
    int pos, val;
    Choice(const Brancher& b, int p, int v)
      : Gecode::Choice(b,2), pos(p), val(v) {}
    virtual size_t size(void) const {
      return sizeof(Choice);
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
  Warnsdorff(Space& home, bool share, Warnsdorff& b) 
    : Brancher(home,share,b), start(b.start) {
    x.update(home,share,b.x);
  }
  virtual Brancher* copy(Space& home, bool share) {
    return new (home) Warnsdorff(home, share, *this);
  }
  virtual bool status(const Space&) const {
    while (true) {
      if (!x[start].assigned()) 
        return true;
      start = x[start].val();
      if (start == 0) 
        return false;
    }
  }
  virtual Gecode::Choice* choice(Space&) {
    int n=-1; unsigned int min=UINT_MAX;
    for (Int::ViewValues<Int::IntView> i(x[start]); i(); ++i)
      if (x[i.val()].size() < min) {
        n=i.val(); min=x[n].size();
      }
    return new Choice(*this,start,n);
  }
  virtual ExecStatus commit(Space& home, const Gecode::Choice& _c, 
                            unsigned int a) {
    const Choice& c = static_cast<const Choice&>(_c);
    if (a == 0)
      return me_failed(x[c.pos].eq(home,c.val)) ? ES_FAILED : ES_OK;
    else 
      return me_failed(x[c.pos].nq(home,c.val)) ? ES_FAILED : ES_OK;
  }
};

void warnsdorff(Home home, const IntVarArgs& x) {
  ViewArray<Int::IntView> y(home,x);
  (void) new (home) Warnsdorff(home,y);
}
class Knights : public Script {
protected:
  const int n;
  IntVarArray succ;
public:
  int field(int x, int y) const {
    return x+y*n;
  }
  IntSet neighbours(int f) {
    static const int moves[8][2] = {
      {-2,-1}, {-2,1}, {-1,-2}, {-1,2}, {1,-2}, {1,2}, {2,-1}, {2,1}
    };
    int nbs[8]; int n_nbs = 0;
    int x = f % n, y = f / n;
    for (int i=0; i<8; i++) {
      int nx = x + moves[i][0], ny = y + moves[i][1];
      if ((nx >= 0) && (nx < n) && (ny >= 0) && (ny < n))
        nbs[n_nbs++] = field(nx,ny);
    }
    return IntSet(nbs,n_nbs);
  }
  Knights(const SizeOptions& opt)
    : n(opt.size()), succ(*this,n*n,0,n*n-1) {
    for (int f=0; f<n*n; f++)
      dom(*this, succ[f], neighbours(f));
    circuit(*this, succ, ICL_DOM);
    rel(*this, succ[0], IRT_EQ, field(1,2));
    warnsdorff(*this, succ);
  }
  Knights(bool share, Knights& s) : Script(share,s), n(s.n) {
    succ.update(*this, share, s.succ);
  }
  virtual Space* copy(bool share) {
    return new Knights(share,*this);
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
    for (int i=0; i<n; i++) {
      for (int j=0; j<n; j++)
	os << "\\knfield{" << field(i,j) << "}{"  
           << jump[field(i,j)] << "}{"  
	   << i << "}{" << j << "}";
      os << "%\n";
    }
    for (int i=0; i<n*n; i++)
      os << "\\knmove{" << jump[i] << "}{" << i << "}{" << succ[i].min() << "}";
    os << "%\n";
/*
    os << "\t";
    for (int i = 0; i < n; i++) {
      for (int j = 0; j < n; j++) {
        os.width(3);
        os << jump[field(i,j)] << " ";
        }
        os << std::endl << "\t";
    }
    os << std::endl;
    delete [] jump;
    */
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
