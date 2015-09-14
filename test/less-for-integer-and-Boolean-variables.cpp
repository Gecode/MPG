/* -*- mode: C++; c-basic-offset: 2; indent-tabs-mode: nil -*- */

#include "test/int.hh"

#include <gecode/minimodel.hh>

namespace Test { namespace Int {

class LessInt : public Test {
public:
  /// Create and register test
  LessInt(void)
    : Test("Less::Int",2,-3,3,false) {}
  /// Test whether \a x is solution
  virtual bool solution(const Assignment& x) const {
    return x[0] < x[1];
  }
  /// Post constraint on \a x
  virtual void post(Gecode::Space& home, Gecode::IntVarArray& x) {
    using namespace Gecode;
    less(home,x[0],x[1]);
  }
};

class LessBool : public Test {
public:
  /// Create and register test
  LessBool(void)
    : Test("Less::Bool",2,0,1,false) {}
  /// Test whether \a x is solution
  virtual bool solution(const Assignment& x) const {
    return x[0] < x[1];
  }
  /// Post constraint on \a x
  virtual void post(Gecode::Space& home, Gecode::IntVarArray& x) {
    using namespace Gecode;
    less(home,channel(home,x[0]),channel(home,x[1]));
  }
};

LessInt li;
LessBool lb;

}}
 
