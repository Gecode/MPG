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
class MagicSequence : public Script {
  IntVarArray x;
public:
  MagicSequence(const SizeOptions& opt)
    : Script(opt), x(*this,opt.size(),0,opt.size()-1) {
    // counting constraints
    for (int i=0; i<x.size(); i++)
      count(*this, x, i, IRT_EQ, x[i]);
    // implied constraints
    linear(*this, x, IRT_EQ, x.size());
    linear(*this, IntArgs::create(x.size(),-1,1), x, IRT_EQ, 0);
    // branching
    branch(*this, x, INT_VAR_NONE(), INT_VAL_MAX());
  }
  MagicSequence(MagicSequence& e) : Script(e) {
    x.update(*this, e.x);
  }
  virtual Space* copy(void) {
    return new MagicSequence(*this);
  }
  virtual void print(std::ostream& os) const {
    os << "\t";
    for (int i=0; i<x.size(); i++) {
      os << x[i] << ", ";
      if ((i+1) % 20 == 0)
        os << std::endl << "\t";
    }
    os << std::endl;
  }
};
int main(int argc, char* argv[]) {
  SizeOptions opt("MagicSequence");
  opt.solutions(0);
  opt.size(500);
  opt.parse(argc,argv);
  Script::run<MagicSequence,DFS,SizeOptions>(opt);
  return 0;
}
