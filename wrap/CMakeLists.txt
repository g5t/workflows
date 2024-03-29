set(PROJECT_PYTHON_MODULE_SOURCES
  "${PROJECT_PYTHON_MODULE}.cpp" # this needs to be first
)
target_sources(${PROJECT_PYTHON_MODULE} PRIVATE ${PROJECT_PYTHON_MODULE_SOURCES})


if(PROJECT_BUILD_PYTHON_TESTING)
  #ensure that the python interpreter knows how to import numpy
  execute_process(
    COMMAND ${Python3_EXECUTABLE} -c "import numpy"
    RESULT_VARIABLE EXIT_CODE
    OUTPUT_QUIET
  )
  if (${EXIT_CODE} EQUAL 0)
    # python interpreter knows about numpy, so we can add all test_*.py tests
    set(test_folder "${CMAKE_CURRENT_SOURCE_DIR}/tests")
    file(GLOB python_tests_ tests/test_*.py)
    foreach(python_test ${python_tests_})
      add_test(NAME ${python_test} COMMAND ${Python3_EXECUTABLE} ${python_test} )
    endforeach()
  else()
    message(WARNING "Install working numpy for ${Python3_EXECUTABLE} to run all tests")
  endif()
endif()
