cmake_minimum_required(VERSION 3.24)
project(mpg_document_first_prototype LANGUAGES CXX)

enable_testing()
find_package(Gecode CONFIG REQUIRED COMPONENTS driver minimodel int search)

add_executable(magic-sequence _build/extracted/magic-sequence.cpp)
target_compile_features(magic-sequence PRIVATE cxx_std_17)
target_link_libraries(magic-sequence PRIVATE ${Gecode_LIBRARIES})

add_test(NAME magic-sequence-smoke COMMAND magic-sequence -solutions 1 8)
set_tests_properties(magic-sequence-smoke PROPERTIES
  PASS_REGULAR_EXPRESSION "\\{4, 2, 1, 0, 1, 0, 0, 0\\}")
