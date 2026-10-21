{
  Space::NoGPI local(home);
  rel(home, x, IRT_LE, y);
  {
    Space::UseGPI global(home);
    rel(home, y, IRT_LE, z);
  }
  rel(home, x, IRT_LE, z);
}
