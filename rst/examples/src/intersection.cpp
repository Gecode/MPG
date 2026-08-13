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

#include <gecode/set.hh>
using namespace Gecode;
  
class Intersection
  : public TernaryPropagator<Set::SetView,Set::PC_SET_ANY> {
public:
  Intersection(Home home, Set::SetView x0, Set::SetView x1,
               Set::SetView x2)
    : TernaryPropagator<Set::SetView,Set::PC_SET_ANY>(home,
                                                      x0,x1,x2) {}
  static ExecStatus post(Home home, Set::SetView x0, Set::SetView x1,
                         Set::SetView x2) {
    (void) new (home) Intersection(home,x0,x1,x2);
    return ES_OK;
  }
  Intersection(Space& home, Intersection& p)
    : TernaryPropagator<Set::SetView,Set::PC_SET_ANY>(home,p) {}
  virtual Propagator* copy(Space& home) {
    return new (home) Intersection(home,*this);
  }
  virtual ExecStatus propagate(Space& home, const ModEventDelta&)  {
    using namespace Iter::Ranges; using namespace Set;
    bool assigned = x0.assigned() && x1.assigned() && x2.assigned();
    // rule 1
    { 
      GlbRanges<SetView> x0lb(x0), x1lb(x1);
      Inter<GlbRanges<SetView>, GlbRanges<SetView> > i(x0lb,x1lb);
      GECODE_ME_CHECK(x2.includeI(home,i));
    }
    // rule 2
    { 
      LubRanges<SetView> x0ub(x0), x1ub(x1);
      Inter<LubRanges<SetView>, LubRanges<SetView> > i1(x0ub,x1ub);
      GECODE_ME_CHECK(x2.intersectI(home,i1)); 
    }
    // rule 3
    { 
      GlbRanges<SetView> x2lb(x2);
      GECODE_ME_CHECK(x0.includeI(home,x2lb)); 
    }
    // rule 4
    { 
      GlbRanges<SetView> x2lb(x2);
      GECODE_ME_CHECK(x1.includeI(home,x2lb)); 
    }
    // rule 5
    { 
      GlbRanges<SetView> x0lb(x0); LubRanges<SetView> x2ub(x2);
      Diff<GlbRanges<SetView>, LubRanges<SetView> > diff(x0lb, x2ub);
      GECODE_ME_CHECK(x1.excludeI(home,diff)); 
    }
    // rule 6
    { 
      GlbRanges<SetView> x1lb(x1); LubRanges<SetView> x2ub(x2);
      Diff<GlbRanges<SetView>, LubRanges<SetView> > diff(x1lb, x2ub);
      GECODE_ME_CHECK(x0.excludeI(home,diff)); 
    }
    // cardinality
    LubRanges<SetView> x0ub(x0), x1ub(x1);
    Union<LubRanges<SetView>, LubRanges<SetView> > u_lub(x0ub,x1ub);
    unsigned int s_lub = size(u_lub);
    if (x0.cardMin() + x1.cardMin() > s_lub)
      GECODE_ME_CHECK(x2.cardMin(home, x0.cardMin()+x1.cardMin()-s_lub));
    GlbRanges<SetView> x0lb(x0), x1lb(x1);
    Union<GlbRanges<SetView>, GlbRanges<SetView> > u_glb(x0lb,x1lb);
    unsigned int s_glb = size(u_glb);
    GECODE_ME_CHECK(x2.cardMax(home,x0.cardMax()+x1.cardMax()-s_glb));
    GECODE_ME_CHECK(x0.cardMin(home,x2.cardMin()));
    GECODE_ME_CHECK(x1.cardMin(home,x2.cardMin()));
    return assigned ? home.ES_SUBSUMED(*this) : ES_NOFIX;
  }
};

void intersection(Home home, SetVar x0, SetVar x1, SetVar x2) {
  GECODE_POST;
  GECODE_ES_FAIL(Intersection::post(home,x0,x1,x2));
}
