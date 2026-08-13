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

#include <gecode/int.hh>
#include <iomanip>

using namespace Gecode;

class StdCoutIntTracer : public IntTracer {
protected:
  // print propagator information
  static void ids(const Propagator& p) {
    std::cout << "(id:" << p.id();
    if (p.group().in())
      std::cout << ",g:" << p.group().id();
    std::cout << ')';
  }
  static void ids(const Brancher& b) {
    std::cout << "(id:" << b.id();
    if (b.group().in())
      std::cout << ",g:" << b.group().id();
    std::cout << ')';
  }
  // print view trace information
  static void info(const ViewTraceInfo& vti) {
    switch (vti.what()) {
    case ViewTraceInfo::PROPAGATOR:
      std::cout << "propagator"; ids(vti.propagator());
      break;
    case ViewTraceInfo::BRANCHER:
      std::cout << "brancher"; ids(vti.brancher());
      break;
    case ViewTraceInfo::POST:
      std::cout << "post(";
      if (vti.post().in())
        std::cout << "g:" << vti.post().id();
      std::cout << ')';
      break;
    case ViewTraceInfo::OTHER:
      std::cout << '-';
      break;
    }
  }
public:
  virtual void init(const Space& home, const IntTraceRecorder& t) {
    std::cout << "trace::init"; ids(t);
    std::cout << " slack: 100.00% (" << t.slack().initial() << " values)"
              << std::endl;
  }
  // prune event
  virtual void prune(const Space& home, const IntTraceRecorder& t,
                     const ViewTraceInfo& vti, int i, IntTraceDelta& d) {
    std::cout << "trace::prune"; ids(t);
    std::cout << ": [" << i << "] = " << t[i] << " - {";
    std::cout << d.min();
    if (d.width() > 1)
      std::cout << ".." << d.max();
    ++d;
    while (d()) {
      std::cout << ',' << d.min();
      if (d.width() > 1)
        std::cout << ".." << d.max();
      ++d;
    }
    std::cout << "} by "; info(vti);
    std::cout << std::endl;
  }
  // fixpoint event
  virtual void fix(const Space& home, const IntTraceRecorder& t) {
    std::cout << "trace::fix"; ids(t);
    double sl_i = static_cast<double>(t.slack().initial());
    double sl_p = static_cast<double>(t.slack().previous());
    double sl_c = static_cast<double>(t.slack().current());
    double p_c = 100.0 * (sl_c / sl_i);
    double p_d = 100.0 * (sl_p / sl_i) - p_c;
    std::cout << " slack: "
              << std::showpoint << std::setprecision(4)
              << p_c << "% - "
              << std::showpoint << std::setprecision(4)
              << p_d << '%'
              << std::endl;
  }
  virtual void fail(const Space& home, const IntTraceRecorder& t) {
    std::cout << "trace::fail"; ids(t);
    double sl_i = static_cast<double>(t.slack().initial());
    double sl_p = static_cast<double>(t.slack().previous());
    double sl_c = static_cast<double>(t.slack().current());
    double p_c = 100.0 * (sl_c / sl_i);
    double p_d = 100.0 * (sl_p / sl_i) - p_c;
    std::cout << " slack: "
              << std::showpoint << std::setprecision(4)
              << p_c << "% - "
              << std::showpoint << std::setprecision(4)
              << p_d << '%'
              << std::endl;
  }
  virtual void done(const Space& home, const IntTraceRecorder& t) {
    std::cout << "trace::done"; ids(t);
    if (t.group().in())
      std::cout << ",g:" << t.group().id();
    std::cout << ") slack: 0%" << std::endl;
  }
};
