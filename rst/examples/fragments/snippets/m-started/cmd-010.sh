cmake -S . -B build -G "Visual Studio 17 2022" -A x64 \
  -DGecode_ROOT=C:\gecode
cmake --build build --config Release
