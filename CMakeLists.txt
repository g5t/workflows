cmake_minimum_required(VERSION 3.18.2)
cmake_policy(SET CMP0076 NEW) # Ensure target_sources converts relative paths

project(module)
set(PROJECT_PYTHON_MODULE _module)
set(TESTING_TARGET tester)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS ON)

# Make the availability of testing optional
option(PROJECT_BUILD_TESTING "Build C++ tests for module" OFF)
option(PROJECT_BUILD_PYTHON_TESTING "Build python tests for module" ON)
# Allow system pybind11 to be required
option(REQUIRE_SYSTEM_PYBIND11 "Never attempt to fetch pybind11" OFF)
mark_as_advanced(REQUIRE_SYSTEM_PYBIND11)
# Allow system catch2 to be required
option(REQUIRE_SYSTEM_CATCH2 "Never attempt to fetch catch2" OFF)
mark_as_advanced(REQUIRE_SYSTEM_CATCH2)
# Allow the log level to be set by cmake
set(PROJECT_LOGLEVEL "INFO" CACHE STRING "Emit log messages to standard out (DEBUG|VERBOSE)")
# Special option for profiling runs
option(PROJECT_PROFILING "Emit profiling output to standard out" OFF)

# Define the minimum version of libraries needed
set(MINIMUM_PYBIND11_VERSION 2.8.1)
set(FETCH_PYBIND11_REPO https://github.com/pybind/pybind11)
set(MINIMUM_CATCH2_VERSION 2.11.3)
set(FETCH_CATCH2_REPO https://github.com/catchorg/Catch2)

if (MSVC)
    # warning level 4 -- add /WX for all warnings as errors
    add_compile_options(/W4)
    # suppress MSVC warning C4996 about 'localtime' vs 'localtime_s'
    add_definitions(-D_CRT_SECURE_NO_WARNINGS)
else()
    # lots of warnings -- add -Werror for  all warnings as errors
    add_compile_options(-Wall -Wextra -pedantic)
endif()

set(CMAKE_MACOSX_RPATH 1)
if(NOT CMAKE_BUILD_TYPE)
  set(CMAKE_BUILD_TYPE Debug)
endif(NOT CMAKE_BUILD_TYPE)

if (${PROJECT_LOGLEVEL} STREQUAL "VERBOSE")
  message(STATUS "Verbose logging emitted at runtime")
  add_definitions(-DVERBOSE)
else()
  if (${PROJECT_LOGLEVEL} STREQUAL "DEBUG")
    message(STATUS "Debug logging emitted at runtime")
    add_definitions(-DDEBUG)
  else()
    message(STATUS "Informational logging emitted at runtime")
  endif()
endif()
if (PROJECT_PROFILING)
  message(STATUS "Profiling output emitted at runtime")
  add_definitions(-DPROFILING)
endif (PROJECT_PROFILING)


set(CMAKE_POSITION_INDEPENDENT_CODE ON)

if (PYTHON_EXECUTABLE)
  message(STATUS "              provided python at ${PYTHON_EXECUTABLE}")
  # Ensure the provided Python interpreter is used
  set(Python3_EXECUTABLE ${PYTHON_EXECUTABLE})
else()
  message(STATUS "              not provided with any python executable?")
endif()
# With modern CMake, this find_package forces pybind11 to use FindPython instead of its custom tools
find_package(Python3 COMPONENTS Interpreter Development)

include(fetcher.cmake)

# Attempt to find catch2 to handle C++ testing
if(PROJECT_BUILD_CXX_TESTING)
  git_fetch(catch2 ${MINIMUM_CATCH2_VERSION} ${FETCH_CATCH2_REPO} ${REQUIRE_SYSTEM_CATCH2})
  list(APPEND CMAKE_MODULE_PATH "${catch2_SOURCE_DIR}/contrib")
else()
  # Since no testing is to be built, fake that we've found Catch2.
  set(Catch2_FOUND ON)
endif()
# Attempt to find pybind11 to handle CPython bindings
git_fetch(pybind11 ${MINIMUM_PYBIND11_VERSION} ${FETCH_PYBIND11_REPO} ${REQUIRE_SYSTEM_PYBIND11})


# Read the version of module
execute_process(COMMAND ${Python3_EXECUTABLE} -c "from version_info import version_number; version_number()"
        WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
        OUTPUT_VARIABLE PROJECT_VERSION)
# So that we can print it to the console along with the specified build type
message(STATUS "Build module v${PROJECT_VERSION} with type ${CMAKE_BUILD_TYPE}")

# Create a header file with information about the last time tye python module was built
# This file will be updated even if no other source files are modified but it does not
# cause relinking the module (if it is the *only* file which changes)
add_custom_target(write_version_info
  COMMAND ${Python3_EXECUTABLE} version_info.py src/version.hpp
  WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
)



# We will always build the python module
list(APPEND CXX_TARGETS ${PROJECT_PYTHON_MODULE})

if(PROJECT_BUILD_PYTHON_TESTING OR PROJECT_BUILD_CXX_TESTING)
  enable_testing() # allows registration of Python tests in wrap/
endif()

# Target for python module
pybind11_add_module(${PROJECT_PYTHON_MODULE} MODULE)
add_subdirectory(wrap)

if(PROJECT_BUILD_CXX_TESTING)
  list(APPEND CXX_TARGETS ${TESTING_TARGET}) # Include the C++ test target
  # target for Catch2 based tests
  add_executable(${TESTING_TARGET})
endif()
# add_subdirectory(lib)

# add the dependencies and include directories for all CXX targets:
add_subdirectory(src)  # important

if (PROJECT_BUILD_CXX_TESTING OR PROJECT_BUILD_PYTHON_TESTING)
	include(CTest)
endif()

if(PROJECT_BUILD_CXX_TESTING)
  target_link_libraries(${TESTING_TARGET} PUBLIC Catch2::Catch2)
  include(Catch)
  catch_discover_tests(${TESTING_TARGET})
endif()

# first we can indicate the documentation build as an option (default OFF)
option(BUILD_DOC "Build documentation" OFF)
option(USE_DOXYGEN "Look for and use Doxygen to build documentation" OFF)
# check if Doxygen is installed
if (USE_DOXYGEN)
find_package(Doxygen QUIET)
if (DOXYGEN_FOUND)
  # set input and output files
  set(DOXYGEN_IN ${PROJECT_SOURCE_DIR}/Doxyfile.in)
  set(DOXYGEN_OUT ${CMAKE_CURRENT_BINARY_DIR}/Doxyfile)
  # request to configure the file
  configure_file(${DOXYGEN_IN} ${DOXYGEN_OUT} @ONLY)
  if(BUILD_DOC)
    add_custom_target( docs ALL
    COMMAND ${DOXYGEN_EXECUTABLE} ${DOXYGEN_OUT}
    WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}
    COMMENT "Generating documentation with Doxygen"
    VERBATIM )
  else()
    add_custom_target( docs
    COMMAND ${DOXYGEN_EXECUTABLE} ${DOXYGEN_OUT}
    WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}
    COMMENT "Generate documentation using target 'docs'"
    VERBATIM )
  endif()
else (DOXYGEN_FOUND)
  message(STATUS "Install Doxygen to build documentation")
endif (DOXYGEN_FOUND)
endif()
