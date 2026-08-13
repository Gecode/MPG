auto c = [](Space& home, unsigned int a,
            IntVar x, int i, int n) {
  if (a == 0U) {
    rel(home, x, IRT_EQ, n);
  } else {
    rel(home, x, IRT_NQ, n);
  }
}
