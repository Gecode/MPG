class S : public Space {
public:
  S(void) {}
  S(S& s) : Space(s) {}
  virtual Space* copy(void) { return new S(*this); }
};

int
main(int argc, char* argv[]) {
  S s;
  LI li(s,4);
  std::cout << li[2] << std::endl;
  li[2] = 5;
  std::cout << li[2] << std::endl;
  return 0;
}

