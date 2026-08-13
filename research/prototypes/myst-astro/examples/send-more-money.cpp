#include <gecode/int.hh>
#include <gecode/minimodel.hh>
#include <gecode/search.hh>
#include <iostream>
#include <memory>

class SendMoreMoney final : public Gecode::Space {
public:
  Gecode::IntVarArray letter;

  SendMoreMoney() : letter(*this, 8, 0, 9) {
    const auto s = letter[0], e = letter[1], n = letter[2], d = letter[3];
    const auto m = letter[4], o = letter[5], r = letter[6], y = letter[7];
    Gecode::distinct(*this, letter);
    Gecode::rel(*this, s != 0);
    Gecode::rel(*this, m != 0);
    Gecode::rel(*this,
      1000*s + 100*e + 10*n + d + 1000*m + 100*o + 10*r + e
      == 10000*m + 1000*o + 100*n + 10*e + y);
    Gecode::branch(*this, letter, Gecode::INT_VAR_SIZE_MIN(), Gecode::INT_VAL_MIN());
  }

  SendMoreMoney(SendMoreMoney& other) : Gecode::Space(other) {
    letter.update(*this, other.letter);
  }

  Gecode::Space* copy() override { return new SendMoreMoney(*this); }
};

int main() {
  // region search-loop
  SendMoreMoney model;
  Gecode::DFS<SendMoreMoney> search(&model);
  const auto solution = std::unique_ptr<SendMoreMoney>(search.next());
  if (!solution) {
    std::cerr << "no solution\n";
    return 1;
  }
  for (int i = 0; i < solution->letter.size(); ++i)
    std::cout << solution->letter[i].val() << (i + 1 == solution->letter.size() ? '\n' : ' ');
  // endregion search-loop
}
