#pragma once
#include <atomic>
#include <cstdint>
#include <mutex>
#include <stdexcept>
#include <string>
#include <string_view>

namespace p2p {
// Strict conversions: JNI modified UTF-8 would corrupt supplementary characters.
inline std::string utf8(std::u16string_view input, size_t limit) {
  std::string out;
  for (size_t i = 0; i < input.size(); ++i) {
    uint32_t cp = input[i];
    if (cp >= 0xd800 && cp <= 0xdbff) {
      if (++i == input.size() || input[i] < 0xdc00 || input[i] > 0xdfff)
        throw std::runtime_error("INPUT_INVALID");
      cp = 0x10000 + ((cp - 0xd800) << 10) + input[i] - 0xdc00;
    } else if (cp >= 0xdc00 && cp <= 0xdfff) {
      throw std::runtime_error("INPUT_INVALID");
    }
    if (cp == 0) throw std::runtime_error("INPUT_INVALID");
    if (cp < 0x80) out += char(cp);
    else if (cp < 0x800) { out += char(0xc0 | cp >> 6); out += char(0x80 | (cp & 63)); }
    else if (cp < 0x10000) { out += char(0xe0 | cp >> 12); out += char(0x80 | ((cp >> 6) & 63)); out += char(0x80 | (cp & 63)); }
    else { out += char(0xf0 | cp >> 18); out += char(0x80 | ((cp >> 12) & 63)); out += char(0x80 | ((cp >> 6) & 63)); out += char(0x80 | (cp & 63)); }
    if (out.size() > limit) throw std::runtime_error("INPUT_INVALID");
  }
  return out;
}

inline std::u16string utf16(std::string_view input) {
  std::u16string out;
  for (size_t i = 0; i < input.size();) {
    uint32_t cp = static_cast<unsigned char>(input[i++]);
    int count = 0;
    uint32_t minimum = 0;
    if (cp >= 0xc2 && cp <= 0xdf) { cp &= 31; count = 1; minimum = 0x80; }
    else if (cp >= 0xe0 && cp <= 0xef) { cp &= 15; count = 2; minimum = 0x800; }
    else if (cp >= 0xf0 && cp <= 0xf4) { cp &= 7; count = 3; minimum = 0x10000; }
    else if (cp >= 0x80) throw std::runtime_error("GENERATION_FAILED");
    while (count-- > 0) {
      if (i == input.size()) throw std::runtime_error("GENERATION_FAILED");
      unsigned char c = input[i++];
      if ((c & 0xc0) != 0x80) throw std::runtime_error("GENERATION_FAILED");
      cp = (cp << 6) | (c & 63);
    }
    if (cp < minimum || cp > 0x10ffff || (cp >= 0xd800 && cp <= 0xdfff))
      throw std::runtime_error("GENERATION_FAILED");
    if (cp <= 0xffff) out += char16_t(cp);
    else { cp -= 0x10000; out += char16_t(0xd800 + (cp >> 10)); out += char16_t(0xdc00 + (cp & 1023)); }
  }
  return out;
}

inline std::string chat_prompt(std::u16string_view raw) {
  auto text = utf8(raw, 1024);
  if (text.empty() || text.find("<|") != std::string::npos || text.find("|>") != std::string::npos ||
      text.find("<think>") != std::string::npos || text.find("</think>") != std::string::npos)
    throw std::runtime_error("INPUT_INVALID");
  return "<|im_start|>user\n" + text + " /no_think" +
      "<|im_end|>\n<|im_start|>assistant\n<think>\n\n</think>\n\n";
}

class AnswerBuffer {
 public:
  // Keep a bounded tail so an EOS marker split over callbacks is consumed whole.
  void append(std::string_view piece) {
    for (char c : piece) {
      if (stopped_ || failed_) return;
      if (text_.size() == 16384 + 14) { failed_ = true; return; }
      text_ += c;
      if (c != '>') continue;
      for (std::string_view marker : {"<|im_end|>", "<|endoftext|>"}) {
        if (text_.size() >= marker.size() &&
            text_.compare(text_.size() - marker.size(), marker.size(), marker) == 0) {
          text_.resize(text_.size() - marker.size());
          stopped_ = true;
          return;
        }
      }
    }
  }
  bool stop_requested() const { return stopped_ || failed_; }
  const std::string& finish() const {
    if (failed_ || text_.size() > 16384 || text_.find("<|") != std::string::npos ||
        text_.find("|>") != std::string::npos)
      throw std::runtime_error("GENERATION_FAILED");
    return text_;
  }
 private:
  std::string text_;
  bool stopped_ = false;
  bool failed_ = false;
};

class RequestGate {
 public:
  std::mutex active;
  void cancel(int64_t id) noexcept {
    if (id <= 0) return;
    auto seen = cancelled_.load();
    while (seen < id && !cancelled_.compare_exchange_weak(seen, id)) {}
  }
  bool cancelled(int64_t id) const noexcept { return id <= cancelled_.load(); }
 private:
  std::atomic<int64_t> cancelled_{0};
};
} // namespace p2p
