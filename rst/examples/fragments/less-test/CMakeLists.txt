cmake_minimum_required(VERSION 3.21)
project(less_test LANGUAGES CXX)

find_package(Gecode CONFIG REQUIRED COMPONENTS test)

add_executable(less-test less-test.cpp)
target_compile_features(less-test PRIVATE cxx_std_17)
target_link_libraries(less-test PRIVATE Gecode::gecodetestint)
