/*
 *  Authors:
 *    Guido Tack <tack@gecode.dev>
 *
 *  Copyright:
 *    Guido Tack, 2008-2026
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

class LI : public LocalHandle {
protected:
  class LIO : public LocalObject {
  public:
    int* data;
    int n;
    LIO(Space& home, int n0)
     : LocalObject(home), data(heap.alloc<int>(n0)), n(n0) {
      home.notice(*this,AP_DISPOSE);
    }
    LIO(Space& home, LIO& l)
      : LocalObject(home,l), data(l.data) {}
    virtual LocalObject* copy(Space& home) {
      return new (home) LIO(home,*this);
    }
    virtual size_t dispose(Space& home) {
      home.ignore(*this,AP_DISPOSE);
      heap.free<int>(data,n);
      return sizeof(*this);
    }
  };
public:
  LI(Space& home, int n) 
    : LocalHandle(new (home) LIO(home,n)) {}
  LI(const LI& li)
    : LocalHandle(li) {}
  LI& operator =(const LI& li) {
    return static_cast<LI&>(LocalHandle::operator =(li));
  }
  int operator [](int i) const {
    return static_cast<const LIO*>(object())->data[i];
  }
  int& operator [](int i) {
    return static_cast<LIO*>(object())->data[i];
  }
};
