StatusStatistics stat;
{
  StatusStatistics a, b;
  s1->status(a);
  s2->status(b);
  stat = a + b;
}
