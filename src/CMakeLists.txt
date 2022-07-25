# Directory specific compilation flags
if (MSVC)
    # warning level 4 -- add /WX for all warnings as errors
    # /Zc__cplusplus ensures the preprocessor macro __cplusplus is set
    add_compile_options(/W4 /Zc__cplusplus)
    # suppress MSVC warning C4996 about 'localtime' vs 'localtime_s'
    add_definitions(-D_CRT_SECURE_NO_WARNINGS)
else()
    # lots of warnings -- add -Werror for  all warnings as errors
    add_compile_options(-Wall -Wextra -pedantic -Wmissing-braces)
endif()
set(CMAKE_MACOSX_RPATH OFF)

foreach(CXX_TARGET IN LISTS CXX_TARGETS)
#  target_sources(${CXX_TARGET} PRIVATE ${CXX_SOURCES})
  target_include_directories(${CXX_TARGET} PUBLIC ${CMAKE_CURRENT_LIST_DIR})
endforeach()

if(PROJECT_BUILD_CXX_TESTING)
  add_subdirectory(tests)
endif()
