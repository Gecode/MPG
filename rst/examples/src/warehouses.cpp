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

#include <gecode/driver.hh>
#include <gecode/int.hh>
#include <gecode/minimodel.hh>

using namespace Gecode;

const int n_warehouses = 5;
const int n_stores = 10;
const int capacity[n_warehouses] = {
  1, 4, 2, 1, 3
};
const int c_fixed = 30;
const int c_supply[n_stores][n_warehouses] = {
  {20, 24, 11, 25, 30},
  {28, 27, 82, 83, 74},
  {74, 97, 71, 96, 70},
  { 2, 55, 73, 69, 61},
  {46, 96, 59, 83,  4},
  {42, 22, 29, 67, 59},
  { 1,  5, 73, 59, 56},
  {10, 73, 13, 43, 96},
  {93, 35, 63, 85, 46},
  {47, 65, 55, 71, 95}
};

class Warehouses : public IntMinimizeScript {
protected:
  // variables
  IntVarArray  supplier;
  BoolVarArray open;
  IntVarArray  c_store;
  IntVar       c_total;
public:
  Warehouses(const Options& opt)
    // variable initialization
    : IntMinimizeScript(opt),
      supplier(*this, n_stores, 0, n_warehouses-1),
      open(*this, n_warehouses, 0, 1),
      c_store(*this, n_stores)
  {
    {
      // do not exceed capacity
      IntSetArgs c(n_warehouses);
      for (int w=0; w<n_warehouses; w++)
        c[w] = IntSet(0,capacity[w]);
      count(*this, supplier, c, IPL_DOM);
    }
    // open warehouses
    for (int s=0; s<n_stores; s++)
      element(*this, open, supplier[s], 1);
    // cost for each warehouse
    for (int s=0; s<n_stores; s++) {
      IntArgs c(n_warehouses, c_supply[s]);
      c_store[s] = expr(*this, element(c, supplier[s]));
    }
    // total cost
    c_total = expr(*this, c_fixed*sum(open) + sum(c_store));
    // branching
    branch(*this, c_store, INT_VAR_REGRET_MIN_MAX(), INT_VAL_MIN());
    branch(*this, supplier, INT_VAR_NONE(), INT_VAL_MIN());
  }
  // cost function
  virtual IntVar cost(void) const {
    return c_total;
  }
  // Constructor for cloning \a s
  Warehouses(Warehouses& s) : IntMinimizeScript(s) {
    supplier.update(*this, s.supplier);
    open.update(*this, s.open);
    c_store.update(*this, s.c_store);
    c_total.update(*this, s.c_total);
  }
  // Copy during cloning
  virtual Space* copy(void) {
    return new Warehouses(*this);
  }
  // Print solution
  virtual void print(std::ostream& os) const {
    os << "\tSupplier:        " << supplier << std::endl
       << "\tOpen warehouses: " << open << std::endl
       << "\tStore cost:      " << c_store << std::endl
       << "\tTotal cost:      " << c_total << std::endl
       << std::endl;
  }
};

int main(int argc, char* argv[]) {
  Options opt("Warehouses");
  opt.solutions(0);
  opt.parse(argc,argv);
  IntMinimizeScript::run<Warehouses,BAB,Options>(opt);
  return 0;
}
