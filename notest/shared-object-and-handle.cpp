int
main(int argc, char* argv[]) {
  SI si(4);
  std::cout << si.get() << std::endl;
  si.set(5);
  std::cout << si.get() << std::endl;
  return 0;
}

