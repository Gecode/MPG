IntArgs distances{
  0, 2, 5, 7,
  2, 0, 3, 5,
  5, 3, 0, 2,
  7, 5, 2, 0
};
IntDistance d(4, distances);
IntVarArray x(home, 2, 0, 3);
IntVar z(home, 3, 7);
minimum_distance(home, x, z, d);
