#include <gecode/int.hh>
#include <gecode/search.hh>
#include <iostream>

using namespace Gecode;

class SendMoreMoney : public Space {
protected:
  IntVarArray letters;

public:
  SendMoreMoney() : letters(*this, 8, 0, 9) {
    IntVar s(letters[0]), e(letters[1]), n(letters[2]), d(letters[3]);
    IntVar m(letters[4]), o(letters[5]), r(letters[6]), y(letters[7]);
    rel(*this, s, IRT_NQ, 0);
    rel(*this, m, IRT_NQ, 0);
    distinct(*this, letters);

    // region posting
    IntArgs coefficients({1000, 100, 10, 1, 1000, 100, 10, 1,
                          -10000, -1000, -100, -10, -1});
    IntVarArgs variables({s, e, n, d, m, o, r, e, m, o, n, e, y});
    linear(*this, coefficients, variables, IRT_EQ, 0);
    // endregion posting

    branch(*this, letters, INT_VAR_SIZE_MIN(), INT_VAL_MIN());
  }

  SendMoreMoney(SendMoreMoney& other) : Space(other) {
    letters.update(*this, other.letters);
  }
  Space* copy() override { return new SendMoreMoney(*this); }
  void print() const { std::cout << letters << '\n'; }
};

int main() {
  auto* model = new SendMoreMoney;
  DFS<SendMoreMoney> search(model);
  delete model;
  if (auto* solution = search.next()) {
    solution->print();
    delete solution;
    return 0;
  }
  return 1;
}
