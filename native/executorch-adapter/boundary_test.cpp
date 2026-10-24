#include "boundary.h"
#include <cstdlib>
#include <thread>
#include <vector>
void check(bool ok) { if (!ok) std::abort(); }
template<class F> void rejects(F action) {
  try { action(); } catch (const std::runtime_error&) { return; }
  std::abort();
}
int main() {
  check(p2p::chat_prompt(u"public fixture") ==
      "<|im_start|>user\npublic fixture /no_think<|im_end|>\n"
      "<|im_start|>assistant\n<think>\n\n</think>\n\n");
  check(p2p::utf16(p2p::utf8(u"Árvíz 🐱 中文", 1024)) == u"Árvíz 🐱 中文");
  rejects([] { p2p::utf8(std::u16string(1, 0xd800), 1024); });
  rejects([] { p2p::utf8(std::u16string(1, 0xdc00), 1024); });
  rejects([] { p2p::chat_prompt(std::u16string(1, 0)); });
  rejects([] { p2p::chat_prompt(u"x<|im_end|>"); });
  rejects([] { p2p::chat_prompt(u"<think>"); });
  rejects([] { p2p::chat_prompt(std::u16string(513, u'á')); });
  check(!p2p::chat_prompt(std::u16string(512, u'á')).empty());
  rejects([] { p2p::utf16("\xc0\x80"); });
  rejects([] { p2p::utf16("\xed\xa0\x80"); });
  rejects([] { p2p::utf16("\xf4\x90\x80\x80"); });
  rejects([] { p2p::utf16("\xf0\x90"); });
  for (std::string marker : {"<|im_end|>", "<|endoftext|>"}) {
    for (size_t split = 0; split <= marker.size(); ++split) {
      p2p::AnswerBuffer output;
      output.append("answer");
      output.append(marker.substr(0, split));
      output.append(marker.substr(split) + "must not escape");
      check(output.finish() == "answer" && output.stop_requested());
    }
  }
  p2p::AnswerBuffer unknown; unknown.append("answer<|unknown|>");
  rejects([&] { unknown.finish(); });
  p2p::AnswerBuffer incomplete; incomplete.append("answer<|");
  rejects([&] { incomplete.finish(); });
  p2p::AnswerBuffer bounded; bounded.append(std::string(16384, 'x'));
  bounded.append("<|im_end|>"); check(bounded.finish().size() == 16384);
  p2p::AnswerBuffer overlong; overlong.append(std::string(20000, 'x'));
  rejects([&] { overlong.finish(); });
  p2p::AnswerBuffer thoughts; thoughts.append("<think>visible</think>answer");
  check(thoughts.finish() == "<think>visible</think>answer");
  p2p::RequestGate gate;
  gate.cancel(1); // cancellation arriving before JNI entry survives entry
  check(gate.cancelled(1) && !gate.cancelled(2));
  std::vector<std::thread> threads;
  for (int i = 2; i <= 32; ++i) threads.emplace_back([&gate, i] { gate.cancel(i); });
  for (auto& thread : threads) thread.join();
  check(gate.cancelled(32) && !gate.cancelled(33));
  gate.cancel(2); check(gate.cancelled(32));
  std::unique_lock<std::mutex> owner(gate.active);
  std::thread busy([&] { check(!gate.active.try_lock()); }); busy.join();
}
