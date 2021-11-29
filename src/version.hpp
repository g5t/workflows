#ifndef PROJECT_VERSION_HPP_
#define PROJECT_VERSION_HPP_
//! \file
namespace project::version{
    //! `project` git repository revision information at build time
    auto constexpr git_revision = u8"a318911a69478963d76718c924bd1961802a029c";
    //! `project` git repository branch at build time
    auto constexpr git_branch = u8"master";
    //! build date and time in YYYY-MM-DDThh:mm format
    auto constexpr build_datetime = u8"2021-11-29T22:01";
    //! `project` version
    auto constexpr version_number = u8"0.0.1";
    //! hostname of the build machine
    auto constexpr build_hostname = u8"yolin";
}
#endif
