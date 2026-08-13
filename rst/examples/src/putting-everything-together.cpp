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

#include "int.hh"

#include <gecode/search.hh>

using namespace MPG;

/*
 * Propagator definitions
 *
 */

// Propagator for less than or equal
template<class V0, class V1>
class LeEq : public Gecode::Propagator {
protected:
  V0 x0; V1 x1;
public:
  LeEq(Gecode::Home home, V0 y0, V1 y1) 
    : Gecode::Propagator(home), x0(y0), x1(y1) {
    x0.subscribe(home,*this,Int::PC_INT_MIN);
    x1.subscribe(home,*this,Int::PC_INT_MAX);
  }
  static Gecode::ExecStatus post(Gecode::Home home, 
                                 V0 x0, V1 x1) {
    if (x0 == x1)
      return Gecode::ES_FAILED;
    GECODE_ME_CHECK(x0.lq(home,x1.max()));
    GECODE_ME_CHECK(x1.gq(home,x0.min()));
    if (x0.max() > x1.min())
      (void) new (home) LeEq(home,x0,x1);
    return Gecode::ES_OK;
  }
  virtual size_t dispose(Gecode::Space& home) {
    x0.cancel(home,*this,Int::PC_INT_MIN);
    x1.cancel(home,*this,Int::PC_INT_MAX);
    (void) Propagator::dispose(home);
    return sizeof(*this);
  }
  LeEq(Gecode::Space& home, LeEq& p) 
    : Gecode::Propagator(home,p) {
    x0.update(home,p.x0);
    x1.update(home,p.x1);
  }
  virtual Gecode::Propagator* copy(Gecode::Space& home) {
    return new (home) LeEq(home,*this);
  }
  virtual Gecode::PropCost cost(const Gecode::Space&, 
                                const Gecode::ModEventDelta&) const {
    return Gecode::PropCost::binary(Gecode::PropCost::LO);
  }
  virtual void reschedule(Space& home) {
    x0.reschedule(home,*this,Int::PC_INT_MIN);
    x1.reschedule(home,*this,Int::PC_INT_MAX);
  }
  virtual Gecode::ExecStatus propagate(Gecode::Space& home, 
                                       const Gecode::ModEventDelta&)  {
    GECODE_ME_CHECK(x0.lq(home,x1.max()));
    GECODE_ME_CHECK(x1.gq(home,x0.min()));
    if (x0.max() <= x1.min())
      return home.ES_SUBSUMED(*this);
    else 
      return Gecode::ES_FIX;
  }
};

// Propagator for disequality
class Disequal : public Gecode::Propagator {
protected:
  Int::IntView x0, x1;
public:
  Disequal(Gecode::Home home, Int::IntView y0, Int::IntView y1) 
    : Gecode::Propagator(home), x0(y0), x1(y1) {
    x0.subscribe(home,*this,Int::PC_INT_BND);
    x1.subscribe(home,*this,Int::PC_INT_BND);
  }
  static Gecode::ExecStatus post(Gecode::Home home, 
                                 Int::IntView x0, Int::IntView x1) {
    if (x0 == x1)
      return Gecode::ES_FAILED;
    (void) new (home) Disequal(home,x0,x1);
    return Gecode::ES_OK;
  }
  virtual size_t dispose(Gecode::Space& home) {
    x0.cancel(home,*this,Int::PC_INT_BND);
    x1.cancel(home,*this,Int::PC_INT_BND);
    (void) Propagator::dispose(home);
    return sizeof(*this);
  }
  Disequal(Gecode::Space& home, Disequal& p) 
    : Gecode::Propagator(home,p) {
    x0.update(home,p.x0);
    x1.update(home,p.x1);
  }
  virtual Gecode::Propagator* copy(Gecode::Space& home) {
    return new (home) Disequal(home,*this);
  }
  virtual Gecode::PropCost cost(const Gecode::Space&, 
                                const Gecode::ModEventDelta&) const {
    return Gecode::PropCost::binary(Gecode::PropCost::LO);
  }
  virtual void reschedule(Space& home) {
    x0.reschedule(home,*this,Int::PC_INT_BND);
    x1.reschedule(home,*this,Int::PC_INT_BND);
  }
  virtual Gecode::ExecStatus propagate(Gecode::Space& home, 
                                       const Gecode::ModEventDelta&)  {
    if ((x0.max() < x1.min()) || (x0.min() > x1.max()))
      return home.ES_SUBSUMED(*this);
    if (x0.assigned()) {
      if (x0.min() == x1.min()) {
        GECODE_ME_CHECK(x1.gq(home,x0.min()+1));
        return home.ES_SUBSUMED(*this);
      } else if (x0.min() == x1.max()) {
        GECODE_ME_CHECK(x1.lq(home,x0.min()-1));
        return home.ES_SUBSUMED(*this);
      }
    } else if (x1.assigned()) {
      if (x1.min() == x0.min()) {
        GECODE_ME_CHECK(x0.gq(home,x1.min()+1));
        return home.ES_SUBSUMED(*this);
      } else if (x1.min() == x0.max()) {
        GECODE_ME_CHECK(x0.lq(home,x1.min()-1));
        return home.ES_SUBSUMED(*this);
      }
    }
    return Gecode::ES_FIX;
  }
};

// Propagator for ternary plus
template<class V0, class V1, class V2>
class Plus : public Gecode::Propagator {
protected:
  V0 x0; V1 x1; V2 x2;
public:
  Plus(Gecode::Home home, V0 y0, V1 y1, V2 y2) 
    : Gecode::Propagator(home), x0(y0), x1(y1), x2(y2) {
    x0.subscribe(home,*this,Int::PC_INT_BND);
    x1.subscribe(home,*this,Int::PC_INT_BND);
    x2.subscribe(home,*this,Int::PC_INT_BND);
  }
  static Gecode::ExecStatus post(Gecode::Home home, 
                                 V0 x0, V1 x1, V2 x2) {
    (void) new (home) Plus(home,x0,x1,x2);
    return Gecode::ES_OK;
  }
  virtual size_t dispose(Gecode::Space& home) {
    x0.cancel(home,*this,Int::PC_INT_BND);
    x1.cancel(home,*this,Int::PC_INT_BND);
    x2.cancel(home,*this,Int::PC_INT_BND);
    (void) Propagator::dispose(home);
    return sizeof(*this);
  }
  Plus(Gecode::Space& home, Plus& p) 
    : Gecode::Propagator(home,p) {
    x0.update(home,p.x0);
    x1.update(home,p.x1);
    x2.update(home,p.x2);
  }
  virtual Gecode::Propagator* copy(Gecode::Space& home) {
    return new (home) Plus(home,*this);
  }
  virtual Gecode::PropCost cost(const Gecode::Space&, 
                                const Gecode::ModEventDelta&) const {
    return Gecode::PropCost::ternary(Gecode::PropCost::LO);
  }
  virtual void reschedule(Space& home) {
    x0.reschedule(home,*this,Int::PC_INT_BND);
    x1.reschedule(home,*this,Int::PC_INT_BND);
    x2.reschedule(home,*this,Int::PC_INT_BND);
  }
  virtual Gecode::ExecStatus propagate(Gecode::Space& home, 
                                       const Gecode::ModEventDelta&)  {
    GECODE_ME_CHECK(x0.lq(home,x2.max()-x1.min()));
    GECODE_ME_CHECK(x0.gq(home,x2.min()-x1.max()));
    GECODE_ME_CHECK(x1.lq(home,x2.max()-x0.min()));
    GECODE_ME_CHECK(x1.gq(home,x2.min()-x0.max()));
    GECODE_ME_CHECK(x2.lq(home,x0.max()+x1.max()));
    GECODE_ME_CHECK(x2.gq(home,x0.min()+x1.min()));
    if (x0.assigned() && x1.assigned() && x2.assigned())
      return home.ES_SUBSUMED(*this);
    else 
      return Gecode::ES_NOFIX;
  }
};



/*
 * Constraint post functions
 *
 */

// Constrain x to be equal to n
void equal(Gecode::Space& home, IntVar x, int n) {
  Int::IntView y(x);
  GECODE_ME_FAIL(y.gq(home,n));
  GECODE_ME_FAIL(y.lq(home,n));
}

// Constrain x to be less than n
void less(Gecode::Space& home, IntVar x, int n) {
  Int::IntView y(x);
  GECODE_ME_FAIL(y.lq(home,n-1));
}

// Constrain x0 to be less than or equal to x1
void leeq(Gecode::Home home, IntVar x0, IntVar x1) {
  GECODE_POST;
  GECODE_ES_FAIL((LeEq<Int::IntView,Int::IntView>::post(home,x0,x1)));
}

// Constrain x1 to be less than x1
void less(Gecode::Home home, IntVar x0, IntVar x1) {
  GECODE_POST;
  Int::OffsetView y0(x0,1);
  GECODE_ES_FAIL((LeEq<Int::OffsetView,Int::IntView>::post(home,y0,x1)));
}

// Constrain x0 to be different from x1
void disequal(Gecode::Home home, IntVar x0, IntVar x1) {
  GECODE_POST;
  GECODE_ES_FAIL(Disequal::post(home,x0,x1));
}

// Constrain x2 to x0 + x1
void plus(Gecode::Home home, IntVar x0, IntVar x1, IntVar x2) {
  GECODE_POST;
  if (x0.assigned()) {
    Int::ConstIntView y0(x0.min());
    GECODE_ES_FAIL((Plus<Int::ConstIntView,Int::IntView,Int::IntView>
                    ::post(home,y0,x1,x2)));
  } else if (x1.assigned()) {
    Int::ConstIntView y1(x1.min());
    GECODE_ES_FAIL((Plus<Int::IntView,Int::ConstIntView,Int::IntView>
                    ::post(home,x0,y1,x2)));
  } else {
    GECODE_ES_FAIL((Plus<Int::IntView,Int::IntView,Int::IntView>
                    ::post(home,x0,x1,x2)));
  }
}

// Constrain x2 to x0 - x1
void minus(Gecode::Home home, IntVar x0, IntVar x1, IntVar x2) {
  GECODE_POST;
  if (x0.assigned()) {
    Int::ConstIntView y0(x0.min());
    Int::MinusView y1(x1);
    GECODE_ES_FAIL((Plus<Int::ConstIntView,Int::MinusView,Int::IntView>
                    ::post(home,y0,y1,x2)));
  } else if (x1.assigned()) {
    Int::ConstIntView y1(-x1.min());
    GECODE_ES_FAIL((Plus<Int::IntView,Int::ConstIntView,Int::IntView>
                    ::post(home,x0,y1,x2)));
  } else {
    Int::MinusView y1(x1);
    GECODE_ES_FAIL((Plus<Int::IntView,Int::MinusView,Int::IntView>
                    ::post(home,x0,y1,x2)));
  }
}

/*
 * The Golomb ruler script
 *
 */

class GolombRuler : public Gecode::Space {
protected:
  static const int n = 8;
  IntVarArray m;
public:
  GolombRuler(void)
    : m(*this,n,0,Int::Limits::max) {

    // Assume first mark to be zero
    equal(*this, m[0], 0);

    // Order marks
    for (int i=1; i<n; i++)
      less(*this, m[i-1], m[i]);

    // Number of differences
    const int n_d = (n*n-n)/2;

    // Array of differences
    IntVarArgs d(*this, n_d, 0, Int::Limits::max);

    // Setup difference constraints
    for (int k=0, i=0; i<n-1; i++)
      for (int j=i+1; j<n; j++, k++)
        minus(*this, m[j], m[i], d[k]);

    // All differences must be pairwise different
    for (int i=0; i<n_d; i++)
      for (int j=i+1; j<n_d; j++)
        disequal(*this, d[i], d[j]);

    // Symmetry breaking
    if (n > 2)
      less(*this, d[0], d[n_d-1]);
 
    // Tracing
    trace(*this, m);

    branch(*this, m, INT_VAR_NONE(), INT_VAL_MIN());
  }
  virtual void constrain(const Gecode::Space& b) {
    less(*this, m[n-1], static_cast<const GolombRuler&>(b).m[n-1].min());
  }
  void print(void) const {
    std::cout << "\tm[" << m.size() << "] = " << m << std::endl;
  }
  GolombRuler(GolombRuler& s)
    : Gecode::Space(s) {
    m.update(*this, s.m);
  }
  virtual Space* copy(void) {
    return new GolombRuler(*this);
  }
};

int main(int argc, char* argv[]) {
  GolombRuler* g = new GolombRuler();
  Gecode::BAB<GolombRuler> e(g);
  delete g;
  
  while (Gecode::Space* s = e.next()) {
    static_cast<GolombRuler*>(s)->print();
    delete s;
  }
  return 0;
}
