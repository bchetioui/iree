# Copyright 2021 The IREE Authors
#
# Licensed under the Apache License v2.0 with LLVM Exceptions.
# See https://llvm.org/LICENSE.txt for license information.
# SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception

include(FetchContent)

FetchContent_Declare(
  spirv-tools
  GIT_REPOSITORY https://github.com/KhronosGroup/SPIRV-Tools.git
  GIT_TAG 00018e58af055a74fd88718af8cca8de34c25106 # 2022-11-25
)

set(SKIP_SPIRV_TOOLS_INSTALL OFF CACHE BOOL "" FORCE)
set(SPIRV_SKIP_EXECUTABLES ON CACHE BOOL "" FORCE)
set(SPIRV_SKIP_TESTS ON CACHE BOOL "" FORCE)

FetchContent_MakeAvailable(spirv-tools)
FetchContent_GetProperties(spirv-tools SOURCE_DIR SPIRV_TOOLS_SOURCE)
