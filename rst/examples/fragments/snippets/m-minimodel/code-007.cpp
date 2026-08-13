IntVar tmp0 = expr(home, c+d);
IntVar tmp1 = expr(home, b*tmp0);
rel(home, a+tmp1 == 0);
