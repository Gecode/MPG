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

const unsigned int n_stack = 1024;

class StackOverflow : public Exception {
public:
  StackOverflow(const char* l)
    : Exception(l,"Stack overflow") {}
};

// path
class Path {
protected:
  // edge
  class Edge {
  protected:
    const Choice* ch;
    unsigned int a;
    Space* c;
  public:
    void init(Space* s, Space* c0) {
      ch = s->choice(); a = 0; c = c0;
    }
    Space* clone(void) const {
      return c;
    }
    void clone(Space* s) {
      c = s->clone();
    }
    void next(void) {
      a++;
    }
    bool la(void) const {
      return a+1 == ch->alternatives();
    }
    void commit(Space* s) {
      s->commit(*ch,a);
    }
    // perform lao
    Space* lao(void) {
      if (!la() || (c == NULL))
        return NULL;
      Space* t = c; c = NULL;
      commit(t);
      return t;
    }
    void reset(void) {
      delete ch; ch=NULL; delete c; c=NULL;
    }
  };
  Edge e[n_stack];
  unsigned int n;
public:
  Path(void) : n(0) {}
  // push edge
  void push(Space* s, Space* c) {
    if (n == n_stack)
      throw StackOverflow("Path::push");
    e[n].init(s,c); e[n].commit(s);
    n++;
  }
  // move to next alternative
  bool next(void) {
    while (n > 0)
      if (e[n-1].la()) {
        e[--n].reset();
      } else {
        e[n-1].next(); return true;
      }
    return false;
  }
  // perform recomputation
  Space* recompute(unsigned int& d) {
    // perform lao
    if (Space* t = e[n-1].lao()) {
      e[--n].reset();
      d = c_d; 
      return t;
    }
    unsigned int i = n-1;
    for (; e[i].clone() == NULL; i--) {}
    Space* s = e[i].clone()->clone();
    d = n - i;
    // perform adaptive recomputation
    if (d >= a_d) {
      unsigned int m = i + d/2;
      for (; i < m; i++)
        e[i].commit(s);
      // skip over last alternatives
      for (; (i < n) && e[i].la(); i++)
        e[i].commit(s);
      // create additional clone
      if (i < n-1) {
        // perform propagation
        if (s->status() == SS_FAILED) {
          delete s; 
          for (; i < n; n--) {
            e[n-1].reset(); d--;
          }
          return NULL;
        }
        e[i].clone(s);
        d = n-i;
      }
    }
    for (; i < n; i++)
      e[i].commit(s);
    return s;
  }
};

// search engine
class Engine {
protected:
  Path p;
  Space* s;
  unsigned int d;
public:
  Engine(Space* r) : s(r), d(c_d) {}
  Space* next(void) {
    do {
      while (s != NULL)
        // exploration
        switch (s->status()) {
        case SS_FAILED:
          delete s; s = NULL;
          break;
        case SS_SOLVED:
          {
            Space* t = s; s = NULL;
            (void) t->choice();
            return t;
          }
        case SS_BRANCH:
          if (d >= c_d) {
            p.push(s,s->clone()); d=1;
          } else {
            p.push(s,NULL); d++;
          }
        }
      while ((s == NULL) && p.next())
        s = p.recompute(d);
    } while (s != NULL);
    return NULL;
  }
  ~Engine(void) {
    delete s;
  }
};
  
