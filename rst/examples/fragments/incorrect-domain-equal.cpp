#include <gecode/int.hh>

using namespace Gecode;

class Equal : public BinaryPropagator<Int::IntView,Int::PC_INT_DOM> {
public:
  Equal(Home home, Int::IntView x0, Int::IntView x1) 
    : BinaryPropagator<Int::IntView,Int::PC_INT_DOM>(home,x0,x1) {}
  static ExecStatus post(Home home, 
                         Int::IntView x0, Int::IntView x1) {
    (void) new (home) Equal(home,x0,x1);
    return ES_OK;
  }
  Equal(Space& home, Equal& p) 
    : BinaryPropagator<Int::IntView,Int::PC_INT_DOM>(home,p) {}
  virtual Propagator* copy(Space& home) {
    return new (home) Equal(home,*this);
  }
  virtual ExecStatus propagate(Space& home, const ModEventDelta&) {
    Int::ViewValues<Int::IntView> i(x0), j(x1);
    while (i() && j())
      if (i.val() < j.val()) {
        GECODE_ME_CHECK(x1.nq(home,i.val())); ++i;
      } else if (j.val() < i.val()) {
        GECODE_ME_CHECK(x0.nq(home,j.val())); ++j;
      } else {
        ++i; ++j;
      }
    while (i()) {
      GECODE_ME_CHECK(x1.nq(home,i.val())); ++i;
    }
    while (j()) {
      GECODE_ME_CHECK(x0.nq(home,j.val())); ++j;
    }
    if (x0.assigned() && x1.assigned())
      return home.ES_SUBSUMED(*this);
    else
      return ES_FIX;
  }
};

void equal(Home home, IntVar x0, IntVar x1) {
  GECODE_POST;
  GECODE_ES_FAIL(Equal::post(home,x0,x1));
}
