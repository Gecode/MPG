add_executable(send-more-money send-more-money.cpp)
target_compile_features(send-more-money PRIVATE cxx_std_17)

if(GECODE_SOURCE_DIR AND GECODE_BUILD_DIR)
  target_include_directories(send-more-money PRIVATE "${GECODE_BUILD_DIR}" "${GECODE_SOURCE_DIR}")
  foreach(component search int kernel support)
    find_library(GECODE_${component}_LIBRARY NAMES "gecode${component}"
      PATHS "${GECODE_BUILD_DIR}" NO_DEFAULT_PATH REQUIRED)
    target_link_libraries(send-more-money PRIVATE "${GECODE_${component}_LIBRARY}")
  endforeach()
else()
  find_package(Gecode 6.4 CONFIG REQUIRED)
  target_link_libraries(send-more-money PRIVATE Gecode::gecode)
endif()

add_test(NAME send-more-money-runs COMMAND send-more-money)
set_tests_properties(send-more-money-runs PROPERTIES PASS_REGULAR_EXPRESSION "\\{9, 5, 6, 7, 1, 0, 8, 2\\}")
