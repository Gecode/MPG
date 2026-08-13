IntVarArgs x;
x << IntVar(home,0,10);
IntVarArgs y;
y << IntVar(home,10,20);
y << x;
linear(home, IntVarArgs()<<x[0]<<x[1], IRT_EQ, 0);
