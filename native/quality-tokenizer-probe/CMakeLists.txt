cmake_minimum_required(VERSION 3.24)
project(quality_tokenizer_probe LANGUAGES CXX)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
if(NOT ANDROID OR NOT ANDROID_ABI STREQUAL "arm64-v8a")
  message(FATAL_ERROR "This diagnostic requires the pinned Android arm64 toolchain")
endif()
if(NOT EXECUTORCH_INSTALL)
  message(FATAL_ERROR "Existing pinned ExecuTorch static install required")
endif()
list(APPEND CMAKE_FIND_ROOT_PATH "${EXECUTORCH_INSTALL}")
find_package(tokenizers CONFIG REQUIRED PATHS
  "${EXECUTORCH_INSTALL}/lib/cmake/tokenizers" NO_DEFAULT_PATH)
add_executable(quality_tokenizer_probe main.cpp)
target_include_directories(quality_tokenizer_probe PRIVATE "${EXECUTORCH_INSTALL}/include")
target_link_libraries(quality_tokenizer_probe PRIVATE tokenizers::tokenizers)
# Suppress known third-party formatted logging; the probe emits its bounded
# result/static error codes only through write(2), never formatted payload logs.
target_link_options(quality_tokenizer_probe PRIVATE
  -Wl,--wrap=printf -Wl,--wrap=vprintf -Wl,--wrap=fprintf -Wl,--wrap=vfprintf
  -Wl,--wrap=puts -Wl,--wrap=putchar -Wl,--wrap=fputs -Wl,--wrap=fwrite
  -Wl,--wrap=fputc -Wl,--wrap=fputwc -Wl,--wrap=__android_log_write -Wl,--wrap=syslog)
