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
#include <gecode/set.hh>
#include <gecode/minimodel.hh>

using namespace Gecode;
class GolfOptions : public Options {
protected:
  Driver::IntOption _w; // Number of weeks
  Driver::IntOption _g; // Number of groups
  Driver::IntOption _s; // Number of players per group
public:
  /// Constructor
  GolfOptions(void)
    : Options("Golf"),
      _w("-w","number of weeks",9),
      _g("-g","number of groups",8),
      _s("-s","number of players per group",4) {
    add(_w); add(_g); add(_s);
  }
  int w(void) const { return _w.value(); }
  int g(void) const { return _g.value(); }
  int s(void) const { return _s.value(); }
};

class Golf : public Script {
  int g, s, w;
  SetVarArray groups;
public:
  Golf(const GolfOptions& opt)
  : Script(opt), g(opt.g()), s(opt.s()), w(opt.w()),
    groups(*this,g*w,IntSet::empty,0,g*s-1,
           static_cast<unsigned int>(s),
           static_cast<unsigned int>(s)) {
    Matrix<SetVarArray> schedule(groups,g,w);
    // groups in a week
    SetVar allPlayers(*this, 0,g*s-1, 0,g*s-1);
    for (int i=0; i<w; i++)
      rel(*this, setdunion(schedule.row(i)) == allPlayers);
    // overlap between groups
    for (int i=0; i<groups.size()-1; i++)
      for (int j=i+1; j<groups.size(); j++)
        rel(*this, cardinality(groups[i] & groups[j]) <= 1);
    // break group symmetry
    for (int j=0; j<w; j++) {
      IntVarArgs m(g);
      for (int i=0; i<g; i++)
        m[i] = expr(*this, min(schedule(i,j)));
      rel(*this, m, IRT_LE);
    }
    // break week symmetry
    IntVarArgs m(w);
    for (int j=0; j<w; j++)
      m[j] = expr(*this, min(schedule(0,j)-IntSet(0,0)));
    rel(*this, m, IRT_LE);
    // break player symmetry
    precede(*this, groups, IntArgs::create(groups.size(),0));
    branch(*this, groups, SET_VAR_MIN_MIN(), SET_VAL_MIN_INC());
  }
  virtual void
  print(std::ostream& os) const {
    os << "Tournament plan" << std::endl;
    Matrix<SetVarArray> schedule(groups,g,w);
    for (int j=0; j<w; j++) {
      os << "Week " << j << ": " << std::endl << "    ";
      os << schedule.row(j) << std::endl;
    }
  }

  /// Constructor for copying \a s
  Golf(Golf& s) : Script(s), g(s.g), s(s.s), w(s.w) {
    groups.update(*this, s.groups);
  }
  /// Copy during cloning
  virtual Space*
  copy(void) {
    return new Golf(*this);
  }
};

int
main(int argc, char* argv[]) {
  GolfOptions opt;
  opt.parse(argc,argv);
  Script::run<Golf,DFS,GolfOptions>(opt);
  return 0;
}
