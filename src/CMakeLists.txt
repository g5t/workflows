# Directory specific compilation flags
if (MSVC)
    # warning level 4 -- add /WX for all warnings as errors
    # /Zc__cplusplus ensures the preprocessor macro __cplusplus is set
    add_compile_options(/W4 /Zc__cplusplus)
else()
    # lots of warnings -- add -Werror for  all warnings as errors
    add_compile_options(-Wall -Wextra -pedantic -Wmissing-braces)
endif()

message(STATUS "Using interpreter: ${Python3_EXECUTABLE}")


#list(APPEND CXX_SOURCES )
foreach(CXX_TARGET IN LISTS CXX_TARGETS)
#  target_sources(${CXX_TARGET} PRIVATE ${CXX_SOURCES})
  target_include_directories(${CXX_TARGET} PUBLIC ${CMAKE_CURRENT_LIST_DIR})
endforeach()

if(PROJECT_BUILD_TESTING)
  add_subdirectory(tests)
endif()
