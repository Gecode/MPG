SEBs sebs(m);
for (int i=0; i<m; i++) {
  Search::Options o;
  o.assets = n / m;
  sebs[i] = pbs<Script,DFS>(o);
}
Search::Options o;
o.threads = m;
PBS<Script> e(master, sebs, o);
