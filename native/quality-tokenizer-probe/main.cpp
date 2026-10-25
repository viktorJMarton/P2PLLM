#include <pytorch/tokenizers/hf_tokenizer.h>
#include "../executorch-adapter/boundary.h"
#include <array>
#include <cerrno>
#include <cstdarg>
#include <cstdio>
#include <cwchar>
#include <fstream>
#include <string>
#include <unistd.h>

extern "C" int __wrap_printf(const char*, ...) { return 0; }
extern "C" int __wrap_vprintf(const char*, va_list) { return 0; }
extern "C" int __wrap_fprintf(FILE*, const char*, ...) { return 0; }
extern "C" int __wrap_vfprintf(FILE*, const char*, va_list) { return 0; }
extern "C" int __wrap_puts(const char*) { return 0; }
extern "C" int __wrap_putchar(int value) { return value; }
extern "C" int __wrap_fputs(const char*, FILE*) { return 0; }
extern "C" size_t __wrap_fwrite(const void*, size_t, size_t count, FILE*) { return count; }
extern "C" int __wrap_fputc(int value, FILE*) { return value; }
extern "C" wint_t __wrap_fputwc(wchar_t value, FILE*) { return value; }
extern "C" int __wrap___android_log_write(int, const char*, const char*) { return 0; }
extern "C" void __wrap_syslog(int, const char*, ...) {}

namespace {
bool write_all(int descriptor, const std::string& value) {
  size_t position = 0;
  while (position < value.size()) {
    const auto count = write(descriptor, value.data() + position, value.size() - position);
    if (count < 0 && errno == EINTR) continue;
    if (count <= 0) return false;
    position += static_cast<size_t>(count);
  }
  return true;
}
int fail(const char* code) {
  write_all(STDERR_FILENO, std::string(code) + "\n");
  return 2;
}
}

// Fixed public-fixture diagnostic only. Root verifies/stages the pinned tokenizer
// bytes and fixture before invocation and consumes IDs in memory, not a file.
int main(int argc, char** argv) {
  try {
    if (argc != 3) return fail("ARGUMENT_INVALID");
    const std::string tokenizer_path(argv[1]);
    const auto separator = tokenizer_path.find_last_of("/\\");
    if (tokenizer_path.substr(separator == std::string::npos ? 0 : separator + 1) != "tokenizer.json")
      return fail("TOKENIZER_PATH_INVALID");
    std::ifstream tokenizer_file(tokenizer_path, std::ios::binary | std::ios::ate);
    if (!tokenizer_file || tokenizer_file.tellg() != std::streampos(11422654))
      return fail("TOKENIZER_FILE_INVALID");
    tokenizer_file.close();
    std::ifstream input(argv[2], std::ios::binary);
    if (!input) return fail("INPUT_FILE_INVALID");
    std::array<char, 4097> bytes{};
    input.read(bytes.data(), bytes.size());
    const auto size = input.gcount();
    if (input.bad() || size <= 0 || size > 4096) return fail("INPUT_SIZE_INVALID");
    const std::string text(bytes.data(), static_cast<size_t>(size));
    if (text.find('\0') != std::string::npos) return fail("INPUT_INVALID");
    try { (void)p2p::utf16(text); } catch (...) { return fail("INPUT_INVALID"); }
    tokenizers::HFTokenizer tokenizer;
    if (tokenizer.load(tokenizer_path) != tokenizers::Error::Ok) return fail("TOKENIZER_LOAD_FAILED");
    auto encoded = tokenizer.encode(text, 0, 0);
    if (!encoded.ok()) return fail("TOKENIZER_ENCODE_FAILED");
    const auto& ids = encoded.get();
    if (ids.empty() || ids.size() > 1024) return fail("TOKEN_COUNT_INVALID");
    std::string output("[");
    for (size_t index = 0; index < ids.size(); ++index) {
      if (index != 0) output += ',';
      output += std::to_string(ids[index]);
    }
    output += ']';
    return write_all(STDOUT_FILENO, output) ? 0 : fail("OUTPUT_FAILED");
  } catch (...) { return fail("PROBE_FAILED"); }
}
