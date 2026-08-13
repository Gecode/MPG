cmake_minimum_required(VERSION 3.20)
project(mpg_examples LANGUAGES CXX)

add_executable(send-more-money send-more-money.cpp)
target_compile_features(send-more-money PRIVATE cxx_std_17)

if(GECODE_SOURCE_DIR AND GECODE_BUILD_DIR)
  # Generated configuration headers live in the build tree; public headers
  # remain in the source tree.
  target_include_directories(send-more-money PRIVATE
    "${GECODE_BUILD_DIR}"
    "${GECODE_SOURCE_DIR}")
  foreach(component search int kernel support)
    find_library(GECODE_${component}_LIBRARY
      NAMES "gecode${component}"
      PATHS "${GECODE_BUILD_DIR}"
      NO_DEFAULT_PATH
      REQUIRED)
    target_link_libraries(send-more-money PRIVATE "${GECODE_${component}_LIBRARY}")
  endforeach()
else()
  find_package(Gecode 6.4 CONFIG REQUIRED)
  target_link_libraries(send-more-money PRIVATE Gecode::gecode)
endif()
