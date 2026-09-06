/*
 *  Authors:
 *    Mikael Z. Lagerkvist <lagerkvist@gecode.dev>
 *
 *  Copyright:
 *    Mikael Z. Lagerkvist, 2026
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

#include "int.hh"
#include <test/test.hh>
#include <memory>

namespace {

class IntTestSpace : public Gecode::Space {
public:
  MPG::IntVar x;

  IntTestSpace(void) : x(*this,-3,3) {}
  IntTestSpace(IntTestSpace& s) : Gecode::Space(s) {
    x.update(*this,s.x);
  }
  Gecode::Space* copy(void) override {
    return new IntTestSpace(*this);
  }
};

class IntTest : public Test::Base {
public:
  IntTest(void) : Test::Base("MPG::Int::Bounds") {}

  bool run(void) override {
    using namespace MPG::Int;
    IntTestSpace s;
    IntView x(s.x);

    if (Test::opt.log) Test::olog << "Updating bounds\n";
    if (x.lq(s,3) != ME_INT_NONE ||
        x.min() != -3 || x.max() != 3)
      return false;
    if (x.gq(s,-1) != ME_INT_MIN ||
        x.min() != -1 || x.max() != 3)
      return false;
    if (x.lq(s,1) != ME_INT_MAX ||
        x.min() != -1 || x.max() != 1 || x.assigned())
      return false;

    if (Test::opt.log) Test::olog << "Cloning and assigning\n";
    if (s.status() == Gecode::SS_FAILED)
      return false;
    std::unique_ptr<IntTestSpace> c(
      static_cast<IntTestSpace*>(s.clone()));
    IntView y(c->x);
    if (y.min() != -1 || y.max() != 1 || y.assigned())
      return false;
    if (y.gq(*c,1) != ME_INT_VAL ||
        !y.assigned() || y.min() != 1 || y.max() != 1)
      return false;
    if (x.min() != -1 || x.max() != 1 || x.assigned())
      return false;

    if (Test::opt.log) Test::olog << "Rejecting an empty domain\n";
    if (y.lq(*c,0) != ME_INT_FAILED)
      return false;
    c->fail();
    return c->status() == Gecode::SS_FAILED &&
      s.status() != Gecode::SS_FAILED &&
      x.min() == -1 && x.max() == 1;
  }
} int_test;

}

int
main(int argc, char* argv[]) {
  return Test::run_registered_tests(argc,argv);
}
