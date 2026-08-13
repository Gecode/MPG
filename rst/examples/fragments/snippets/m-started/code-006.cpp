try {
  ...
} catch (Exception e) {
  std::cerr << "Gecode exception: " << e.what() << std::endl;
  return 1;
}
return 0;
