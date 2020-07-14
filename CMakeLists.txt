project(workflows)
cmake_minimum_required(VERSION 2.8)

add_executable(test_tests test_tests.c)

enable_testing()
add_test(usage_test_tests test)
set_tests_properties(usage_test_tests PROPERTIES WILL_FAIL TRUE)

add_test(success_test_tests test_tests 0)
set_tests_properties(success_test_tests PROPERTIES PASS_REGULAR_EXPRESSION "SUCCESS")

add_test(fail_test_tests test_tests 1)
set_tests_properties(fail_test_tests PROPERTIES WILL_FAIL TRUE)

add_test(fail_test_output test_tests 1)
set_tests_properties(fail_test_output PROPERTIES PASS_REGULAR_EXPRESSION "FAIL")

