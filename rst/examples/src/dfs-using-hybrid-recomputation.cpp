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

using namespace Gecode;

const unsigned int c_d = 5;

class Edge {
protected:
  Edge* p;
  const Choice* ch;
  unsigned int a;
  Space* c;
public:
  Edge(Space* s, Edge* e)
    : p(e), ch(s->choice()), a(0), c(NULL) {}
  void next(void) {
    a++;
  }
  Space* commit(Space* s) const {
    s->commit(*ch,a); return s;
  }
  // create clone
  void clone(Space* s) {
    c = s->clone();
  }
  // perform recomputation
  Space* recompute(void) const {
    return commit((c != NULL) ? c->clone() : p->recompute());
  }
  ~Edge(void) {
    delete c; delete ch;
  }
};

Space* dfs(Space* s, Edge* p, unsigned int d) {
  switch (s->status()) {
  case SS_FAILED:
    delete s; return NULL;
  case SS_SOLVED:
    (void) s->choice(); return s;
  case SS_BRANCH:
    {
      // store clone if needed
      Edge e(s,p);
      if (d >= c_d) {
        e.clone(s); d=0;
      }
      // explore first alternative
      if (Space* t = dfs(e.commit(s),&e,d+1))
        return t;
      e.next();
      return dfs(e.recompute(),&e,d+1);
    }
  }
}

Space* dfs(Space* s) {
  return dfs(s,NULL,c_d);
}
