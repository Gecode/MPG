/* -*- mode: C++; c-basic-offset: 2; indent-tabs-mode: nil -*- */
/*
 *  Main author:
 *     Mikael Zayenz Lagerkvist <lagerkvist@gecode.dev>
 *
 *  Copyright:
 *     Mikael Zayenz Lagerkvist, 2026
 *
 *  This file is part of Gecode, the generic constraint
 *  development environment:
 *     http://www.gecode.dev
 *
 *  Permission is hereby granted, free of charge, to any person obtaining
 *  a copy of this software and associated documentation files (the
 *  "Software"), to deal in the Software without restriction, including
 *  without limitation the rights to use, copy, modify, merge, publish,
 *  distribute, sublicense, and/or sell copies of the Software, and to
 *  permit persons to whom the Software is furnished to do so, subject to
 *  the following conditions:
 *
 *  The above copyright notice and this permission notice shall be
 *  included in all copies or substantial portions of the Software.
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

#include <gecode/driver.hh>
#include <gecode/int.hh>
#include <gecode/minimodel.hh>

using namespace Gecode;

namespace {
  /// The actions; a move has the same code as its destination
  enum { ToShelf, ToWorkbench, ToCharger, PickUp, Deliver, Charge };
  /// The locations, connected in a line
  enum { Shelf, Workbench, Charger };
  /// Where the packet is
  enum { OnShelf, Carried, Delivered };
  /// Battery capacity
  const int capacity = 5;
  /// Maximal number of actions
  const int limit = 12;
  /// Action names for printing
  const char* name[] = {
    "to-shelf", "to-workbench", "to-charger", "pick-up", "deliver", "charge"
  };

  /// Steps (a,at0,ch0,pk0,at1,ch1,pk1): action a from state 0 to 1
  TupleSet
  robot_steps(void) {
    TupleSet t(7);
    // A move to a neighbouring location uses one unit of charge
    for (int pk=OnShelf; pk<=Carried; pk++)
      for (int ch=1; ch<=capacity; ch++)
        for (int at=Shelf; at<Charger; at++) {
          t.add({at+1,at,ch,pk,at+1,ch-1,pk});
          t.add({at,at+1,ch,pk,at,ch-1,pk});
        }
    // Charging adds one unit, up to the capacity
    for (int pk=OnShelf; pk<=Carried; pk++)
      for (int ch=0; ch<capacity; ch++)
        t.add({Charge,Charger,ch,pk,Charger,ch+1,pk});
    // Pick up at the shelf and deliver at the workbench
    for (int ch=0; ch<=capacity; ch++) {
      t.add({PickUp,Shelf,ch,OnShelf,Shelf,ch,Carried});
      t.add({Deliver,Workbench,ch,Carried,Workbench,ch,Delivered});
    }
    t.finalize();
    return t;
  }
}

/**
 * \brief %Example: a delivery plan of unknown length
 *
 * A robot at the workbench must fetch a packet from the shelf and deliver
 * it to the workbench. The shelf, workbench, and charger are connected in
 * a line. A move uses one unit of charge, and charging adds one unit, up
 * to five. The size option gives the initial charge (default 1).
 *
 * \ingroup Example
 */
class OpenDelivery : public IntMinimizeScript {
protected:
  /// Actions in plan order
  OpenIntVarList actions;
  /// Location, charge, and packet status in each state
  OpenIntVarList at, charge, packet;
public:
  /// Construct the model
  OpenDelivery(const SizeOptions& opt)
    : IntMinimizeScript(opt),
      actions(*this,IntSet(ToShelf,Charge),
              [](Space& home, OpenIntVarList, int i) {
                static_cast<OpenDelivery&>(home).step(i);
              },limit),
      at(*this,IntSet(Shelf,Charger),limit+1),
      charge(*this,IntSet(0,capacity),limit+1),
      packet(*this,IntSet(OnShelf,Delivered),limit+1) {
    rel(*this,at.length() == actions.length()+1);
    rel(*this,charge.length() == actions.length()+1);
    rel(*this,packet.length() == actions.length()+1);
    rel(*this,at.get(*this,0),IRT_EQ,Workbench);
    rel(*this,charge.get(*this,0),IRT_EQ,static_cast<int>(opt.size()));
    rel(*this,packet.get(*this,0),IRT_EQ,OnShelf);
    if (failed())
      return;
    goal(0);
    branch(*this,actions,INT_VAR_NONE(),INT_VAL_MIN());
  }

  /// Post the step for the new action \a i and the state after it
  void step(int i) {
    at.materialize(*this,i+2);
    charge.materialize(*this,i+2);
    packet.materialize(*this,i+2);
    if (failed())
      return;
    static const TupleSet steps = robot_steps();
    extensional(*this,
                IntVarArgs({actions[i],
                            at[i],charge[i],packet[i],
                            at[i+1],charge[i+1],packet[i+1]}),
                steps);
    goal(i+1);
  }

  /// End the plan in state \a i exactly when the packet is delivered
  void goal(int i) {
    BoolVar done = expr(*this,packet[i] == Delivered);
    rel(*this,(actions.length() == i) >> done);
    rel(*this,done >> (actions.length() <= i));
  }

  /// Return the number of actions as cost
  virtual IntVar cost(void) const {
    return actions.length();
  }

  /// Constructor for cloning \a s
  OpenDelivery(OpenDelivery& s) : IntMinimizeScript(s) {
    actions.update(*this,s.actions);
    at.update(*this,s.at);
    charge.update(*this,s.charge);
    packet.update(*this,s.packet);
  }

  /// Perform copying during cloning
  virtual Space*
  copy(void) {
    return new OpenDelivery(*this);
  }

  /// Print the plan
  virtual void
  print(std::ostream& os) const {
    os << "\t" << actions.length() << " actions:";
    for (int i=0; i<actions.known_length(); i++)
      os << " " << name[actions[i].val()];
    os << std::endl;
  }
};

/** \brief Main-function
 *  \relates OpenDelivery
 */
int
main(int argc, char* argv[]) {
  SizeOptions opt("OpenDelivery");
  opt.size(1);
  opt.solutions(0);
  opt.parse(argc,argv);
  Script::run<OpenDelivery,BAB,SizeOptions>(opt);
  return 0;
}

// STATISTICS: example-any
