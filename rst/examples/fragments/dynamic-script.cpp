  class Script : public Space {
    IntVarArray x;
  public:
    Script(void) {
      IntVarArgs _x;
      while (...) {
        ...
        _x << IntVar(*this,...);
      }
      ...
      x = IntVarArray(*this,_x);
    }
    ...
  }
