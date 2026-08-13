Matrix<IntVarArray> m(x, 9, 9);

for (int i=0; i<9; i++)
  distinct(home, m.row(i));
for (int i=0; i<9; i++)
  distinct(home, m.col(i));
for (int i=0; i<9; i+=3)
  for (int j=0; j<9; j+=3)
    distinct(home, m.slice(i, i+3, j, j+3));
