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

void bab(Space* s, unsigned int& n, Space*& b) {
  switch (s->status()) {
  case SS_FAILED:
    delete s;
    break;
  case SS_SOLVED:
    // solved
    n++;
    delete b; 
    (void) s->choice(); b = s->clone(); delete s;
    break;
  case SS_BRANCH:
    {
      const Choice* ch = s->choice();
      Space* c = s->clone();
      // remember number of solutions
      unsigned int m=n;
      // explore first alternative
      s->commit(*ch,0);
      bab(s,n,b);
      // constrain clone
      if (n > m)
        c->constrain(*b);
      // explore second alternative
      c->commit(*ch,1);
      bab(c,n,b);
      delete ch;
    }
    break;
  }
}

Space* bab(Space* s) {
  unsigned int n = 0; Space* b = NULL;
  bab(s,n,b);
  return b;
}
