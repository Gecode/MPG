virtual bool Space::master(const MetaInfo& mi) {
  switch (mi.type()) {
  case MetaInfo::RESTART:
    if (mi.last() != NULL)
      constrain(*mi.last());
    mi.nogoods().post(*this);
    return true;
  case MetaInfo::PORTFOLIO:
    BrancherGroup::all.kill(*this);
    break;
  default:
    break;
  }
  return true;
}
virtual bool Space::slave(const MetaInfo& mi) {
  return true;
}
