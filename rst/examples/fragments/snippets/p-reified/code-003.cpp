GECODE_ME_CHECK(x2.lq(home,std::max(x0.max(),x1.max())));
GECODE_ME_CHECK(x2.gq(home,std::max(x0.min(),x1.min())));
GECODE_ME_CHECK(x0.lq(home,x2.max()));
GECODE_ME_CHECK(x1.lq(home,x2.max()));
if ((x1.max() <= x0.min()) || 
    (x1.max() < x2.min()))
  GECODE_ME_CHECK(x0.gq(home,x2.min()));
if ((x0.max() <= x1.min()) || 
    (x0.max() < x2.min()))
  GECODE_ME_CHECK(x1.gq(home,x2.min()));
