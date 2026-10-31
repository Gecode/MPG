  const char* dimacs = R"(format dimacs-cnf
  comment "c"
  line "p cnf {vars:int} {clauses:int}"
  repeat clauses { list clause: int until 0 }
  )";

  class Sat : public Script {
    BoolVarArray x;
  public:
    Sat(const InstanceOptions& opt) : Script(opt) {
      Instance::Data d = opt.data();
      int n = static_cast<int>(d.integer("vars"));
      x = BoolVarArray(*this, n, 0, 1);
      for (int c=0; c<d.size("clause"); c++) {
        IntArgs literals = d.ints("clause", {c});
        ...
      }
      ...
    }
    ...
  };

  int main(int argc, char* argv[]) {
    InstanceOptions opt("SAT", dimacs);
    opt.parse(argc,argv);
    try {
      (void) opt.data();
    } catch (const Instance::Error& e) {
      std::cerr << e.what() << std::endl;
      return 1;
    }
    Script::run<Sat,DFS,InstanceOptions>(opt);
    return 0;
  }
