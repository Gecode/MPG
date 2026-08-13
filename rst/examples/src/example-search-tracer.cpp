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

#include <gecode/search.hh>

using namespace Gecode;
class SimpleSearchTracer : public SearchTracer {
protected:
  static const char* t2s(EngineType et)  {
    switch (et) {
    case EngineType::DFS: return "DFS";
    case EngineType::BAB: return "BAB";
    case EngineType::LDS: return "LDS";
    case EngineType::RBS: return "RBS";
    case EngineType::PBS: return "PBS";
    case EngineType::AOE: return "AOE";
    }
  }
public:
  SimpleSearchTracer(void) {}
  // init
  virtual void init(void) {
    std::cout << "trace<Search>::init()" << std::endl;
    for (unsigned int e=0U; e<engines(); e++) {
      std::cout << "\t" << e << ": " 
                << t2s(engine(e).type());
      if (engine(e).meta()) {
        // init for meta engines
        std::cout << ", engines: {";
        for (unsigned int i=engine(e).efst(); i<engine(e).elst(); i++) {
          std::cout << i; if (i+1 < engine(e).elst()) std::cout << ",";
        }
      } else {
        // init for engines
        std::cout << ", workers: {";
        for (unsigned int i=engine(e).wfst(); i<engine(e).wlst(); i++) {
          std::cout << i; if (i+1 < engine(e).wlst()) std::cout << ",";
        }
      }
      std::cout << "}" << std::endl;
    }
  }
  // node
  virtual void node(const EdgeInfo& ei, const NodeInfo& ni) {
    std::cout << "trace<Search>::node(";
    switch (ni.type()) {
    case NodeType::FAILED:
      std::cout << "FAILED";
      break;
    case NodeType::SOLVED:
      std::cout << "SOLVED";
      break;
    case NodeType::BRANCH:
      std::cout << "BRANCH(" << ni.choice().alternatives() << ")";
      break;
    }
    std::cout << ',' << "w:" << ni.wid() << ','
              << "n:" << ni.nid() << ')';
    if (ei) {
      if (ei.wid() != ni.wid())
        std::cout << " [stolen from w:" << ei.wid() << "]";
      std::cout << std::endl << '\t' << ei.string()
                << std::endl;
    } else {
      std::cout << std::endl;
    }
  }
  // round
  virtual void round(unsigned int eid) {
    std::cout << "trace<Search>::round(e:" << eid << ")" << std::endl;
  }
  // skip
  virtual void skip(const EdgeInfo& ei) {
    std::cout << "trace<Search>Search::skip(w:" << ei.wid()
              << ",n:" << ei.nid()
              << ",a:" << ei.alternative() << ")" << std::endl;
  }
  // done
  virtual void done(void) {
    std::cout << "trace<Search>::done()" << std::endl;
  }
  virtual ~SimpleSearchTracer(void) {}
};
