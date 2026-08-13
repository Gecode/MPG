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

Space* dfs(Space* s) {
  switch (s->status()) {
  case SS_FAILED:
    delete s; return NULL;
  case SS_SOLVED:
    (void) s->choice(); return s;
  case SS_BRANCH:
    {
      const Choice* ch = s->choice();
      unsigned int n = ch->alternatives();
      // single alternative
      if (n == 1) {
        s->commit(*ch,0);
        delete ch;
        return dfs(s);
      }
      // several alternatives
      Space* c = s->clone();
      for (unsigned int a=0; a<n; a++) {
        // space to explore
        Space* e;
        if (a == 0)
          e = s;
        else if (a == n-1)
          e = c;
        else
          e = c->clone();
        // recursive search
        e->commit(*ch,a);
        if (Space* t = dfs(e)) {
          if (a != n-1) delete c;
          delete ch;
          return t;
        }
      }
      delete ch;
      return NULL;
    }
    break;
  }
}
