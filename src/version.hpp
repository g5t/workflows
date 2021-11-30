#ifndef PROJECT_VERSION_HPP_
#define PROJECT_VERSION_HPP_
//! \file
namespace project::version{
    //! `project` git repository revision information at build time
    auto constexpr git_revision = u8"e1db50ca82e8819ab8f5808661d31b832fec7613";
    //! `project` git repository branch at build time
    auto constexpr git_branch = u8"master";
    //! build date and time in YYYY-MM-DDThh:mm format
    auto constexpr build_datetime = u8"2021-11-30T05:56";
    //! `project` version
    auto constexpr version_number = u8"0.0.3";
    //! hostname of the build machine
    auto constexpr build_hostname = u8"yolin";
}
#endif
