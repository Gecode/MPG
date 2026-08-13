virtual ExecStatus propagate(Space& home, const ModEventDelta&) {
  bool modified = false;

  ModEvent me = x0.gq(home,x1.min());
  if (me_failed(me)) 
    return ES_FAILED;
  else if (me_modified(me)) 
    modified = true;
  ...
  if (x0.assigned() && x1.assigned())
    return home.ES_SUBSUMED(*this);
  else
    return modified ? ES_NOFIX : ES_FIX;
}
