size_t s = this->dispose(home);
GECODE_ES_CHECK(LeEq::post(home(*this),x0,x1));
return home.ES_SUBSUMED_DISPOSED(*this,s);
