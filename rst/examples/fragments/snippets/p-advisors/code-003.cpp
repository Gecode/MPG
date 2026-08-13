if (todo != NOTHING)
  return home.ES_FIX_DISPOSE(c,static_cast<ViewAdvisor&>(a));
todo = dom(static_cast<ViewAdvisor&>(a).x,d);
return (todo == NOTHING) ? ES_FIX : 
  home.ES_NOFIX_DISPOSE(c,static_cast<ViewAdvisor&>(a));
