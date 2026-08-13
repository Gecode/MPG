class Model : public Space {
protected:
  IntVarArray x;
  Rnd r;
public:
  Model(void) : ... {
    // Initialize master
  }
  void first(void) {
    // Initialize slave for first solution
  }
  void next(const Model& b) {
    // Initialize slave for next solution
  }
  virtual bool slave(const MetaInfo& mi) {
    if (mi.type() == MetaInfo::RESTART) {
      if (mi.last() == nullptr) {
        first();
        return true;
      } else {
        next(static_cast<const Model&>(*mi.last()));
        return false;
      }
    } else {
      ...
    }
  }
  virtual bool master(const MetaInfo& mi) {
    ...
  }
};
