cmake -S gecode-6.5.0 -B build \
  -DCMAKE_C_COMPILER=gcc -DCMAKE_CXX_COMPILER=g++ \
  -DCMAKE_BUILD_TYPE=Release
cmake --build build
cmake --install build --prefix /opt/gecode
