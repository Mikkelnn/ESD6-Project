//
// Copyright 2010-2016 Ettus Research LLC
// Copyright 2018 Ettus Research, a National Instruments Company
//
// SPDX-License-Identifier: GPL-3.0-or-later
//

#pragma once

/*!
 * The ABI version string that the client application builds against.
 * Call get_abi_string() to check this against the library build.
 * The format is oldest API compatible release - ABI compat number.
 * The compatibility number allows pre-release ABI to be versioned.
 */
#define UHD_VERSION_ABI_STRING "4.6.0"

// clang-format off
/*!
 * A macro to check UHD version at compile-time.
 * The value of this macro is MAJOR * 1000000 + API * 10000 + ABI * 100 + PATCH
 * (e.g., for UHD 3.10.0.1 this is 3100001).
 */
#define UHD_VERSION 4060000

#ifdef __cplusplus
#include <uhd/config.hpp>
#include <string>

// clang-format on

namespace uhd {

//! Get the version string (dotted version number + build info)
UHD_API std::string get_version_string(void);

//! Get the ABI compatibility string for this build of the library
UHD_API std::string get_abi_string(void);

//! Get the component string
UHD_API std::string get_component(void);

} // namespace uhd
#endif
