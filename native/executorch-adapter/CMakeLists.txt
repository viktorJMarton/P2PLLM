cmake_minimum_required(VERSION 3.24)
project(p2p_inference LANGUAGES CXX)
set(CMAKE_CXX_STANDARD 17)
if(NOT ANDROID)
  add_executable(boundary_test boundary_test.cpp)
  if(MSVC)
    target_compile_options(boundary_test PRIVATE /utf-8)
  endif()
  enable_testing()
  add_test(NAME boundary COMMAND boundary_test)
  return()
endif()
if(NOT EXECUTORCH_SOURCE OR NOT EXECUTORCH_INSTALL)
  message(FATAL_ERROR "Pinned ExecuTorch source and existing install required")
endif()
# The official example supplies the exact static registration/backend link list.
list(APPEND CMAKE_FIND_ROOT_PATH "${EXECUTORCH_INSTALL}")
find_package(gflags REQUIRED)
find_package(executorch CONFIG REQUIRED FIND_ROOT_PATH_BOTH)
# Place its binary dir under the existing install so upstream package discovery
# resolves its already-built targets. Do not modify any upstream sources.
add_subdirectory("${EXECUTORCH_SOURCE}/examples/models/llama"
                 "${EXECUTORCH_INSTALL}/examples/models/p2p-llama" EXCLUDE_FROM_ALL)
get_target_property(runner_links llama_main LINK_LIBRARIES)
add_library(p2p_inference SHARED inference.cpp)
target_link_libraries(p2p_inference PRIVATE ${runner_links})
target_include_directories(p2p_inference PRIVATE "${EXECUTORCH_SOURCE}/..")
target_link_options(p2p_inference PRIVATE -Wl,--wrap=printf -Wl,--wrap=fprintf
                    -Wl,--wrap=puts -Wl,--wrap=putchar -Wl,--exclude-libs,ALL -Wl,-Bsymbolic -Wl,-s)
