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

const char* names[] = 
  {"Betty","Chris","Donald","Fred","Gary",
   "Mary","Paul","Peter","Susan"};
enum {
  Betty, Chris, Donald, Fred, Gary,
  Mary, Paul, Peter, Susan
};
const int n = 9;
const int n_prefs = 17;
int spec[n_prefs][2] = {
  {Betty,Donald}, {Betty,Gary}, {Betty,Peter},
  {Chris,Gary}, {Chris,Susan},
  {Donald,Fred}, {Donald,Gary},
  {Fred,Betty}, {Fred,Gary},
  {Gary,Mary}, {Gary,Betty},
  {Mary,Betty}, {Mary,Susan},
  {Paul,Donald}, {Paul,Peter},
  {Peter,Susan}, {Peter,Paul}
};

class Photo : public IntMinimizeScript {
  IntVarArray pos;
  IntVar      violations;
public:
  Photo(const Options& opt)
    : IntMinimizeScript(opt),
      pos(*this,n,0,n-1), violations(*this,0,n_prefs) {
    distinct(*this, pos, IPL_BND);
    BoolVarArgs viol(*this,n_prefs,0,1);
    for (int i=0; i<n_prefs; i++) {
      IntVar distance(*this,0,n), diff(*this,-n,n);
      linear(*this, {1,-1},
                    IntVarArgs({pos[spec[i][0]],pos[spec[i][1]]}),
             IRT_EQ, diff);
      abs(*this, diff, distance);
      rel(*this, distance, IRT_GR, 1, viol[i]);
    }
    linear(*this, viol, IRT_EQ, violations);
    rel(*this, pos[Betty] < pos[Chris]);
    branch(*this, pos, INT_VAR_NONE(), INT_VAL_MIN());
  }
  virtual IntVar cost(void) const {
    return violations;
  }  
  Photo(Photo& p) : IntMinimizeScript(p) {
    pos.update(*this, p.pos);
    violations.update(*this, p.violations);
  }
  virtual Space* copy(void) {
    return new Photo(*this);
  }
  virtual void print(std::ostream& os) const {
    if (pos.assigned()) {
      os << "\tOrder: ";
      int order[n];
      for (int i=0; i<n; i++)
        order[pos[i].val()] = i;
      for (int i=0; i<n; i++)
        os << names[order[i]] << " ";
    } else {
      os << "\tPositions: " << pos;
    }
    os << std::endl << "\tViolations: " << violations << std::endl;
  }
};
int main(int argc, char* argv[]) {
  Options opt("Photo");
  opt.solutions(0);
  opt.parse(argc,argv);
  IntMinimizeScript::run<Photo,BAB,Options>(opt);
  return 0;
}
