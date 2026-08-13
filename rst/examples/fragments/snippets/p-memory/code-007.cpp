Region r;
{
  int* i = r.alloc<int>(n);
  ...
  r.free();
}
{ 
  int* i = r.alloc<int>(n);
  ...
  r.free();
}
