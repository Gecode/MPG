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
const unsigned int a_d = 2;

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
  void clone(Space* s) {
    c = s->clone();
  }
  Space* recompute(unsigned int n, unsigned int& d) {
    if (c != NULL) {
      d = (n >= a_d) ? n/2 : n;
      return commit(c->clone());
    } else {
      Space* s = p->recompute(n+1,d);
      if ((d == n) && (s->status() != SS_FAILED))
        clone(s);
      return commit(s);
    }
  }
  Space* recompute(unsigned int& d) {
    return recompute(1,d);
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
      Edge e(s,p);
      if (d >= c_d) {
        e.clone(s); d=0;
      }
      if (Space* t = dfs(e.commit(s),&e,d+1))
        return t;
      e.next();
      return dfs(e.recompute(d),&e,d+1);
    }
  }
}

Space* dfs(Space* s) {
  return dfs(s,NULL,c_d);
}
