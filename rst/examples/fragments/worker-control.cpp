Search::WorkerControl control(2);
Search::Options o;
o.threads = 4;
o.worker_control = control;
DFS<Script> e(s,o);
control.request(1);
