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

#include "less.cpp"
#include <test/int.hh>

namespace {

class LessTest final : public ::Test::Int::Test {
public:
  LessTest(void)
    : ::Test::Int::Test(
        ::Test::TestTags(::Test::TestTag::check, ::Test::TestTag::normal),
        "Less", 2, -3, 3, false, Gecode::IPL_DOM) {}

  bool solution(const ::Test::Int::Assignment& x) const override {
    return x[0] < x[1];
  }

  void post(Gecode::Space& home, Gecode::IntVarArray& x) override {
    less(home, x[0], x[1]);
  }
} less_test;

}

int
main(int argc, char* argv[]) {
  return Test::run_registered_tests(argc, argv);
}
