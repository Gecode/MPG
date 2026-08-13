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

class Edge {
protected:
  Edge* p;
  const Choice* ch;
  unsigned int a;
public:
  Edge(Space* s, Edge* e)
    : p(e), ch(s->choice()), a(0) {}
  void next(void) {
    a++;
  }
  Space* commit(Space* s) const {
    s->commit(*ch,a); return s;
  }
  Space* recompute(Space* r) const {
    return commit((p == NULL) ? r->clone() : p->recompute(r));
  }
  ~Edge(void) {
    delete ch;
  }
};

void bab(Space* s, Space*& r, Space*& b, Edge* p) {
  switch (s->status()) {
  case SS_FAILED:
    delete s; break;
  case SS_SOLVED:
    // solved
    delete b; 
    (void) s->choice(); b = s->clone(); delete s;
    r->constrain(*b);
    if (r->status() == SS_FAILED) {
      delete r; r = NULL;
    } else {
      Space* c = r->clone(); delete r; r = c;
    }
    break;
  case SS_BRANCH:
    {
      Edge e(s,p);
      bab(e.commit(s),r,b,&e);
      e.next();
      // explore second alternative
      if (r != NULL)
        bab(e.recompute(r),r,b,&e);
    }
  }
}

Space* bab(Space* s) {
  if (s->status() == SS_FAILED) {
    delete s; return NULL;
  }
  Space* r = s->clone();
  Space* b = NULL;
  bab(s,r,b,NULL);
  (void) b->choice();
  delete r;
  return b;
}
