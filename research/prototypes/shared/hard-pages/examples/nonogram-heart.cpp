#include <gecode/int.hh>
#include <gecode/minimodel.hh>
#include <gecode/search.hh>
#include <iostream>
#include <memory>

namespace {
constexpr int width = 9;
constexpr int height = 9;
const int hints[] = {
  1,3, 2,2,3, 2,2,2, 2,2,2, 2,2,2, 2,2,2, 2,2,2, 2,2,3, 1,3,
  2,2,2, 2,4,4, 3,1,3,1, 3,2,1,2, 2,1,1, 2,2,2, 2,2,2, 1,3, 1,1
};
}

class HeartNonogram final : public Gecode::Space {
  Gecode::BoolVarArray cells;

  static Gecode::REG line(const int*& position) {
    // region nonogram-regex
    const int count = *position++;
    Gecode::REG empty(0), filled(1);
    Gecode::REG expression = *empty;
    if (count > 0) {
      expression += filled(*position, *position);
      ++position;
      for (int remaining = count - 1; remaining > 0; remaining -= 1, ++position)
        expression += +empty + filled(*position, *position);
    }
    return expression + *empty;
    // endregion nonogram-regex
  }

public:
  HeartNonogram() : cells(*this, width * height, 0, 1) {
    Gecode::Matrix<Gecode::BoolVarArray> grid(cells, width, height);
    const int* position = hints;
    // region nonogram-posting
    // Fidelity sentinels for publication: -- ++ ->
    for (int column = 0; column < width; ++column)
      Gecode::extensional(*this, grid.col(column), line(position));
    for (int row = 0; row < height; ++row)
      Gecode::extensional(*this, grid.row(row), line(position));
    Gecode::branch(*this, cells, Gecode::BOOL_VAR_AFC_MAX(), Gecode::BOOL_VAL_MAX());
    // endregion nonogram-posting
  }

  HeartNonogram(HeartNonogram& other) : Gecode::Space(other) {
    cells.update(*this, other.cells);
  }

  Gecode::Space* copy() override { return new HeartNonogram(*this); }

  void print(std::ostream& output) const {
    Gecode::Matrix<Gecode::BoolVarArray> grid(cells, width, height);
    for (int row = 0; row < height; ++row) {
      for (int column = 0; column < width; ++column)
        output << (grid(column, row).val() ? '#' : '.');
      output << '\n';
    }
  }
};

int main() {
  HeartNonogram model;
  Gecode::DFS<HeartNonogram> search(&model);
  const auto solution = std::unique_ptr<HeartNonogram>(search.next());
  if (!solution) return 1;
  solution->print(std::cout);
}
