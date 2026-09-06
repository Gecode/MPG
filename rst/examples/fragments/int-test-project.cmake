cmake_minimum_required(VERSION 3.21)
project(int_test LANGUAGES CXX)

find_package(Gecode CONFIG REQUIRED COMPONENTS test)

add_executable(int-test int-test.cpp)
target_compile_features(int-test PRIVATE cxx_std_17)
target_link_libraries(int-test PRIVATE Gecode::gecodetest)
