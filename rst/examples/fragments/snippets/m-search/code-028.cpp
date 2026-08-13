Search::Options s0, s1, s2;
s0.threads = 2;
s1.threads = 1;
s2.threads = 1;
s2.cutoff  = Search::Cutoff::luby(10);
Search::Options s;
s.threads = 3;
PBS<Script> e(master,
              SEBs({dfs<Script>(s0),
                    dfs<Script>(s1),
                    rbs<Script,DFS>(s2)}),
             s);
