#include "boundary.h"
#include <jni.h>
#include <executorch/examples/models/llama/runner/runner.h>
#include <executorch/extension/threadpool/threadpool.h>
#include <executorch/runtime/platform/platform.h>
#include <executorch/runtime/platform/runtime.h>

namespace {
p2p::RequestGate gate;
struct Failure { const char* code; };
std::u16string java_text(JNIEnv* env, jstring value, size_t limit) {
  if (!value) throw Failure{"INPUT_INVALID"};
  const auto length = env->GetStringLength(value);
  if (size_t(length) > limit) throw Failure{"INPUT_INVALID"};
  std::u16string text(length, u'\0');
  env->GetStringRegion(value, 0, length, reinterpret_cast<jchar*>(text.data()));
  if (env->ExceptionCheck()) throw Failure{"GENERATION_FAILED"};
  return text;
}
void check_cancel(jlong id) { if (gate.cancelled(id)) throw Failure{"CANCELLED"}; }
void fail(JNIEnv* env, const char* code) {
  if (!env->ExceptionCheck()) {
    auto cls = env->FindClass("java/lang/IllegalStateException");
    if (cls) env->ThrowNew(cls, code);
  }
}
}

// Strong PAL override: upstream error paths can otherwise emit input text.
extern "C" void et_pal_emit_log_message(et_timestamp_t, et_pal_log_level_t,
    const char*, const char*, size_t, const char*, size_t) {}
// Applied only to this library's linked code; never redirect process descriptors.
extern "C" int __wrap_printf(const char*, ...) { return 0; }
extern "C" int __wrap_fprintf(void*, const char*, ...) { return 0; }
extern "C" int __wrap_puts(const char*) { return 0; }
extern "C" int __wrap_putchar(int c) { return c; }

extern "C" JNIEXPORT void JNICALL
Java_org_p2pai_app_LocalInferenceNative_cancel(JNIEnv*, jobject, jlong request_id) {
  gate.cancel(request_id);
}

extern "C" JNIEXPORT jstring JNICALL
Java_org_p2pai_app_LocalInferenceNative_generate(JNIEnv* env, jobject,
    jstring model, jstring tokenizer, jstring input, jlong request_id) {
  const char* phase_error = "INPUT_INVALID";
  try {
    if (request_id <= 0) throw Failure{"INPUT_INVALID"};
    std::unique_lock<std::mutex> lock(gate.active, std::try_to_lock);
    if (!lock.owns_lock()) throw Failure{"BUSY"};
    check_cancel(request_id);
    auto prompt = p2p::chat_prompt(java_text(env, input, 1024));
    auto model_path = p2p::utf8(java_text(env, model, 4096), 4096);
    auto tokenizer_path = p2p::utf8(java_text(env, tokenizer, 4096), 4096);
    phase_error = "MODEL_LOAD_FAILED";
    executorch::runtime::runtime_init();
    executorch::extension::threadpool::get_threadpool()->_unsafe_reset_threadpool(4);
    check_cancel(request_id);
    auto runner = example::create_llama_runner(model_path, tokenizer_path,
        std::vector<std::string>{}, 0.0f);
    check_cancel(request_id);
    if (!runner || runner->load() != executorch::runtime::Error::Ok)
      throw Failure{"MODEL_LOAD_FAILED"};
    check_cancel(request_id);
    phase_error = "GENERATION_FAILED";
    executorch::extension::llm::GenerationConfig config;
    config.echo = false;
    config.warming = true; // upstream suppresses unconditional token/report stdout
    config.temperature = 0;
    config.max_new_tokens = 128;
    p2p::AnswerBuffer output;
    auto status = runner->generate(prompt, config, [&](const std::string& piece) {
      if (gate.cancelled(request_id) || output.stop_requested()) { runner->stop(); return; }
      output.append(piece);
      if (output.stop_requested()) runner->stop();
    });
    check_cancel(request_id);
    if (status != executorch::runtime::Error::Ok)
      throw Failure{"GENERATION_FAILED"};
    auto result = p2p::utf16(output.finish());
    return env->NewString(reinterpret_cast<const jchar*>(result.data()), result.size());
  } catch (const Failure& failure) { fail(env, failure.code); }
    catch (...) { fail(env, phase_error); }
  return nullptr;
}
