class Script : public Space {
  ...
  virtual bool master(const MetaInfo& mi) {
    // Configure the master
    ...
    // Whether to restart or not
    return true;
  }
  virtual bool slave(const MetaInfo& mi) {
    // Configure the slave
    ...
    // Search is complete
    return true;
  }
};
