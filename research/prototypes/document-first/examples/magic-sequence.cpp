#include <gecode/driver.hh>
#include <gecode/int.hh>
#include <gecode/minimodel.hh>

using namespace Gecode;

class MagicSequence : public Script {
private:
  IntVarArray x;

public:
  explicit MagicSequence(const SizeOptions& options)
      : Script(options),
        x(*this, options.size(), 0, options.size() - 1) {
    for (int value = 0; value < x.size(); ++value)
      count(*this, x, value, IRT_EQ, x[value]);

    linear(*this, x, IRT_EQ, x.size());
    linear(*this, IntArgs::create(x.size(), -1, 1), x, IRT_EQ, 0);
    branch(*this, x, INT_VAR_NONE(), INT_VAL_MAX());
  }

  MagicSequence(MagicSequence& other) : Script(other) {
    x.update(*this, other.x);
  }

  Space* copy() override {
    return new MagicSequence(*this);
  }

  void print(std::ostream& output) const override {
    output << "\t" << x << std::endl;
  }
};

int main(int argc, char* argv[]) {
  SizeOptions options("MagicSequence");
  options.size(8);
  options.solutions(1);
  options.parse(argc, argv);
  Script::run<MagicSequence, DFS, SizeOptions>(options);
  return 0;
}
