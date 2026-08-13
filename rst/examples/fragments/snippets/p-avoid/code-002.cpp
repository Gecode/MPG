while (nafp) {
  nafp = false;
  GECODE_ME_CHECK_MODIFIED(nafp,x0.gq(home,x1.min()));
  GECODE_ME_CHECK_MODIFIED(nafp,x1.gq(home,x0.min()));
  GECODE_ME_CHECK_MODIFIED(nafp,x0.lq(home,x1.max()));
  GECODE_ME_CHECK_MODIFIED(nafp,x1.lq(home,x0.max()));
}
