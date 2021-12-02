#include <pybind11/pybind11.h>
#include "version.hpp"

void wrap_version(pybind11::module & m){
  using namespace project::version;
  m.attr("__version__") = version_number;
	m.attr("__git_branch") = git_branch;
  m.attr("__git_revision") = git_revision;
  m.attr("__build_datetime") = build_datetime;
  m.attr("__build_hostname") = build_hostname;
}


#define STRINGIFY(x) #x
#define MACRO_STRINGIFY(x) STRINGIFY(x)

int add(int i, int j) {
    return i + j;
}

namespace py = pybind11;

PYBIND11_MODULE(_module, m) {
    m.doc() = R"pbdoc(
        Pybind11 example plugin
        -----------------------

        .. currentmodule:: _module

        .. autosummary::
           :toctree: _generate

           add
           subtract
    )pbdoc";

    m.def("add", &add, R"pbdoc(
        Add two numbers

        Some other explanation about the add function.
    )pbdoc");

    m.def("subtract", [](int i, int j) { return i - j; }, R"pbdoc(
        Subtract two numbers

        Some other explanation about the subtract function.
    )pbdoc");

    wrap_version(m);
}
