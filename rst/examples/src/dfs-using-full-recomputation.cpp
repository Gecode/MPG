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

// edge class
class Edge {
protected:
  Edge* p;
  const Choice* ch;
  unsigned int a;
public:
  Edge(Space* s, Edge* e)
    : p(e), ch(s->choice()), a(0) {}
  // next alternative
  void next(void) {
    a++;
  }
  // committing a space
  Space* commit(Space* s) const {
    s->commit(*ch,a); return s;
  }
  // recomputing a space
  Space* recompute(Space* r) const {
    return commit((p == NULL) ? r->clone() : p->recompute(r));
  }
  ~Edge(void) {
    delete ch;
  }
};

Space* dfs(Space* s, Space* r, Edge* p) {
  switch (s->status()) {
  case SS_FAILED:
    delete s; return NULL;
  case SS_SOLVED:
    (void) s->choice(); return s;
  case SS_BRANCH:
    { 
      // explore first alternative
      Edge e(s,p);
      if (Space* t = dfs(e.commit(s),r,&e))
        return t;
      // explore second alternative
      e.next();
      return dfs(e.recompute(r),r,&e);
    }
  }
}

Space* dfs(Space* s) {
  if (s->status() == SS_FAILED) {
    delete s; return NULL;
  }
  Space* r = s->clone();
  Space* t = dfs(s,r,NULL);
  delete r;
  return t;
}
