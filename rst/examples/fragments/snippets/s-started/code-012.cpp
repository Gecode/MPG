StatusStatistics stat;
{
  StatusStatistics a, b;
  s1->status(a); stat += a;
  s2->status(b); stat += b;
}
