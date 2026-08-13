virtual bool slave(const MetaInfo& mi) {
  if (mi.type() == MetaInfo::PORTFOLIO) {
    switch (mi.asset() & 3) {
    case 0: branch(...); break;
    case 1: branch(...); break;
    case 2: branch(...); break;
    case 3: branch(...); break;
  }
  return true;
}
