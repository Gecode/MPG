#include <gecode/int.hh>
#include <gecode/minimodel.hh>
#include <gecode/search.hh>
#include <array>
#include <iostream>
#include <memory>
#include <string_view>

namespace {
constexpr int size = 5;
constexpr std::array<std::string_view, 5> across = {
  "balsa", "avail", "tided", "halve", "sneer"
};
constexpr std::array<std::string_view, 5> down = {
  "baths", "avian", "ladle", "sieve", "alder"
};

Gecode::TupleSet dictionary(const std::array<std::string_view, 5>& words) {
  Gecode::TupleSet tuples(size);
  for (const auto word : words) {
    Gecode::IntArgs letters(size);
    for (int i = 0; i < size; ++i) letters[i] = word[i];
    tuples.add(letters);
  }
  tuples.finalize();
  return tuples;
}
}

class MiniCrossword final : public Gecode::Space {
  Gecode::IntVarArray letters;

public:
  MiniCrossword() : letters(*this, size * size, 'a', 'z') {
    Gecode::Matrix<Gecode::IntVarArray> grid(letters, size, size);
    const Gecode::TupleSet acrossWords = dictionary(across);
    const Gecode::TupleSet downWords = dictionary(down);
    // region crossword-posting
    for (int row = 0; row < size; ++row)
      Gecode::extensional(*this, grid.row(row), acrossWords);
    for (int column = 0; column < size; ++column)
      Gecode::extensional(*this, grid.col(column), downWords);
    Gecode::branch(*this, letters, Gecode::INT_VAR_SIZE_MIN(), Gecode::INT_VAL_MIN());
    // endregion crossword-posting
  }

  MiniCrossword(MiniCrossword& other) : Gecode::Space(other) {
    letters.update(*this, other.letters);
  }

  Gecode::Space* copy() override { return new MiniCrossword(*this); }

  void print(std::ostream& output) const {
    Gecode::Matrix<Gecode::IntVarArray> grid(letters, size, size);
    for (int row = 0; row < size; ++row) {
      for (int column = 0; column < size; ++column)
        output << static_cast<char>(grid(column, row).val());
      output << '\n';
    }
  }
};

int main() {
  MiniCrossword model;
  Gecode::DFS<MiniCrossword> search(&model);
  const auto solution = std::unique_ptr<MiniCrossword>(search.next());
  if (!solution) return 1;
  solution->print(std::cout);
}
