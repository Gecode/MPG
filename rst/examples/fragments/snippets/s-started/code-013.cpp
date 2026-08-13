c->commit(*ch,0);
if (Space* t = dfs(c)) {
  delete ch; delete s;
  return t;
}
