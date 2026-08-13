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

#include <gecode/kernel.hh>
#include <iomanip>

using namespace Gecode;

class StdCoutTracer : public Tracer {
public:
  virtual void post(const Space& home,
                    const PostTraceInfo& pti) {
    std::cout << "trace::" << pti << std::endl;
  }
  virtual void propagate(const Space& home,
                         const PropagateTraceInfo& pti) {
    std::cout << "trace::" << pti << std::endl;
  }
  virtual void commit(const Space& home,
                      const CommitTraceInfo& cti) {
    std::cout << "trace::" << cti << std::endl
              << '\t';
    cti.brancher().print(home, cti.choice(), cti.alternative(),
                         std::cout);
    std::cout << std::endl;
  }
};
