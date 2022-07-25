cmake_minimum_required(VERSION 3.18.2)
cmake_policy(SET CMP0076 NEW) # Ensure target_sources converts relative paths

if (NOT CMAKE_BUILD_TYPE)
  set(CMAKE_BUILD_TYPE "Debug" CACHE STRING "Choose build type" FORCE)
endif()

# scikit-build claims to support FindPython, but doesn't fully?
# https://github.com/scikit-build/scikit-build/issues/506#issuecomment-706791791
if(SKBUILD)
  message(STATUS "SciKit-Build PYTHON_EXECUTABLE ${PYTHON_EXECUTABLE}")
  message(STATUS "SciKit-Build PYTHON_INCLUDE_DIR ${PYTHON_INCLUDE_DIR}")
  message(STATUS "SciKit-Build PYTHON_LIBRARY ${PYTHON_LIBRARY}")
  set(Python_EXECUTABLE "${PYTHON_EXECUTABLE}")
  set(Python_INCLUDE_DIR "${PYTHON_INCLUDE_DIR}")
  set(Python_LIBRARY "${PYTHON_LIBRARY}")
else()
  if (PYTHON_EXECUTABLE)
    # Ensure the provided Python interpreter is used
    set(Python3_EXECUTABLE ${PYTHON_EXECUTABLE})
  endif()
endif()

# Attempt to find full development Python3
find_package(Python3 COMPONENTS Interpreter Development QUIET)
if (NOT DEFINED Python3_Development_FOUND OR NOT ${Python3_Development_FOUND})
  # Fall-back to Development.Module which is present for SciKit-Build under manylinux, but not Windows?
  find_package(Python3 REQUIRED COMPONENTS Interpreter Development.Module)
endif()

if (NOT DEFINED PYTHON_EXECUTABLE)
  set(PYTHON_EXECUTABLE ${Python3_EXECUTABLE})
endif()

include(checkgit.cmake)
checkGitSetup("MODULE")
message(STATUS "Build module v${MODULE_VERSION} with type ${CMAKE_BUILD_TYPE}")

project(module VERSION ${MODULE_SAFE_VERSION} LANGUAGES CXX)
set(PROJECT_PYTHON_MODULE _module)
set(PROJECT_PYTHON_DESTINATION module)
set(TESTING_TARGET tester)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS ON)
set(CMAKE_POSITION_INDEPENDENT_CODE ON)

if (SKBUILD)
  set(PROJECT_BUILD_TESTING OFF)
  set(PROJECT_BUILD_PYTHON_TESTING ON)
  set(PROJECT_LOGLEVEL "INFO")
endif()
if (NOT DEFINED PROJECT_BUILD_TESTING)
  option(PROJECT_BUILD_TESTING "Build C++ tests for module" OFF)
endif()
if (NOT DEFINED PROJECT_BUILD_PYTHON_TESTING)
  option(PROJECT_BUILD_PYTHON_TESTING "Build python tests for module" ON)
endif()
if (NOT DEFINED PROJECT_LOGLEVEL)
  set(PROJECT_LOGLEVEL "INFO" CACHE STRING "Emit log messages to standard out (DEBUG|VERBOSE)")
endif()
# Special option for profiling runs
option(PROJECT_PROFILING "Emit profiling output to standard out" OFF)

# Use conan to fetch/configure/build pybind11, catch2 and hdf5
if(NOT EXISTS "${CMAKE_CURRENT_BINARY_DIR}/conan.cmake")
  message(STATUS "Downloading conan.cmake from https://github.com/conan-io/cmake-conan")
  file(DOWNLOAD "https://raw.githubusercontent.com/conan-io/cmake-conan/0.18.1/conan.cmake"
          "${CMAKE_CURRENT_BINARY_DIR}/conan.cmake"
          EXPECTED_HASH SHA256=5cdb3042632da3efff558924eecefd580a0e786863a857ca097c3d1d43df5dcd
          TLS_VERIFY ON)
endif()
include(${CMAKE_BINARY_DIR}/conan.cmake)
list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_BINARY_DIR})
list(APPEND CMAKE_PREFIX_PATH ${CMAKE_CURRENT_BINARY_DIR})

conan_cmake_configure(
        REQUIRES
        pybind11/2.6.2
        catch2/2.13.9
        GENERATORS
        cmake_find_package
        OPTIONS
)

conan_cmake_autodetect(conan_settings)

conan_cmake_install(PATH_OR_REFERENCE ${CMAKE_CURRENT_BINARY_DIR}
        BUILD outdated
        REMOTE conancenter
        SETTINGS ${conan_settings}
        OUTPUT_QUIET)

find_package(Catch2 REQUIRED)
find_package(pybind11 REQUIRED)


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

foreach(CXX_TARGET IN LISTS CXX_TARGETS)
  addGitVersion(${CXX_TARGET})
  #target_link_libraries(${CXX_TARGET} PUBLIC git_version)
endforeach()

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

#if (SKBUILD)
#  message(STATUS "PYTHON_NumPy_INCLUDE_DIRS ${PYTHON_NumPy_INCLUDE_DIRS}")
#  message(STATUS "Python3_NumPy_INCLUDE_DIRS ${Python3_NumPy_INCLUDE_DIRS}")
#  message(STATUS "Python_EXECUTABLE ${Python_EXECUTABLE}")
#  message(STATUS "Python_INCLUDE_DIR ${Python_INCLUDE_DIR}")
#  message(STATUS "Python_LIBRARY ${Python_LIBRARY}")
#  message(STATUS "Python_NumPy_INCLUDE_DIRS ${Python_NumPy_INCLUDE_DIRS}")
#endif()


install(TARGETS ${PROJECT_PYTHON_MODULE} LIBRARY DESTINATION ${PROJECT_PYTHON_DESTINATION})