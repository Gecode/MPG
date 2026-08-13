class Model : public Space {
public:
  Model(void) : ... {
    branch(home, x, INT_VAR_NONE(), INT_VAL_MIN());
    branch(home, &Model::post);
  }
  void more(void) {
    ...
  }
  static void post(Space& home) {
    static_cast<Model&>(home).more();
  }
};
