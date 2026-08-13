void next(const Model& b) {
  relax(*this, x, b.x, r, 0.7);    
}
