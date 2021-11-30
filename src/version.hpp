#ifndef PROJECT_VERSION_HPP_
#define PROJECT_VERSION_HPP_
//! \file
namespace project::version{
    //! `project` git repository revision information at build time
    auto constexpr git_revision = u8"da4cb11141a74c5b6bbc3004158c90a5f613cd18";
    //! `project` git repository branch at build time
    auto constexpr git_branch = u8"master";
    //! build date and time in YYYY-MM-DDThh:mm format
    auto constexpr build_datetime = u8"2021-11-30T14:09";
    //! `project` version
    auto constexpr version_number = u8"0.0.3";
    //! hostname of the build machine
    auto constexpr build_hostname = u8"t.dram.esss.dk";
}
#endif
