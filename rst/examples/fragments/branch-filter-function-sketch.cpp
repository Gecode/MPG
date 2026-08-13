class Model : public Space {
protected:
  IntVarArray x;
public:
  Model(void) : ... {
    branch(home, x, ..., ..., &filter);
  }
  static bool filter(const Space& home, IntVar y, int i) {
    return y.size() >= 4;
  }
};
