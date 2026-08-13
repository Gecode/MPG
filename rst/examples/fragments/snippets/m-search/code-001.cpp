IntVarArray x(home, 3, 1, 6);
rel(home, x[0] + x[1] == x[2]);
mult(home, x[0], x[1], x[2]);
branch(home, x, INT_VAR_NONE(), INT_VAL_MIN());
