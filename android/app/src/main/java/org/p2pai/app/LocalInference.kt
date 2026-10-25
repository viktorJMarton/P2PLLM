package org.p2pai.app

import android.content.Context
import android.os.Handler
import android.os.Looper
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import java.io.File
import java.io.IOException
import java.security.MessageDigest
import java.util.concurrent.Executors
import java.util.concurrent.atomic.AtomicBoolean

internal object LocalInferenceNative {
    init { System.loadLibrary("p2p_inference") }
    external fun generate(modelPath: String, tokenizerPath: String, prompt: String, requestId: Long): String
    external fun cancel(requestId: Long)
}

internal enum class InferencePhase { IDLE, PREPARING, RUNNING, COMPLETED, CANCELLED, ERROR }

internal data class InferenceState(
    val prompt: String = "",
    val answer: String = "",
    val phase: InferencePhase = InferencePhase.IDLE,
    val progress: Int = 0,
    val error: String? = null,
    val stopping: Boolean = false,
) {
    val busy: Boolean get() = phase == InferencePhase.PREPARING || phase == InferencePhase.RUNNING
}

// Process ownership prevents Activity recreation from opening or recovering live work.
// State contains chat only in memory; no SavedStateHandle, file or diagnostic logging.
internal object LocalInferenceController {
    private val worker = Executors.newSingleThreadExecutor()
    private val cancellationWorker = Executors.newSingleThreadExecutor()
    private val main = Handler(Looper.getMainLooper())
    private val cancelled = AtomicBoolean(false)
    @Volatile private var active = false
    private var requestId = 0L
    var state by mutableStateOf(InferenceState())
        private set

    fun editPrompt(value: String) {
        if (!active && value.length <= 1024 && value.toByteArray(Charsets.UTF_8).size <= 1024) {
            state = state.copy(prompt = value, error = null)
        }
    }

    fun generate(context: Context) {
        if (active) return
        val prompt = state.prompt
        if (prompt.isBlank() || prompt.indexOf('\u0000') >= 0 || prompt.contains("<|") ||
            prompt.contains("|>") || prompt.contains("<think>") || prompt.contains("</think>") ||
            prompt.toByteArray(Charsets.UTF_8).size > 1024
        ) {
            state = state.copy(phase = InferencePhase.ERROR,
                error = "Adj meg legfeljebb 1024 UTF-8 bájtnyi kérdést, vezérlőjelölők nélkül.")
            return
        }
        active = true
        requestId += 1
        val generationId = requestId
        cancelled.set(false)
        state = state.copy(answer = "", phase = InferencePhase.PREPARING, progress = 0,
            error = null, stopping = false)
        val app = context.applicationContext
        worker.execute {
            var result: String? = null
            var error: String? = null
            try {
                val directory = File(app.noBackupFilesDir, "local-inference")
                if (!directory.isDirectory && !directory.mkdirs()) throw IOException()
                val model = prepare(app, directory, "model.pte", BuildConfig.LOCAL_MODEL_BYTES,
                    BuildConfig.LOCAL_MODEL_SHA256, 0, 97)
                val tokenizer = prepare(app, directory, "tokenizer.json", BuildConfig.LOCAL_TOKENIZER_BYTES,
                    BuildConfig.LOCAL_TOKENIZER_SHA256, 97, 3)
                checkCancelled()
                publish { it.copy(phase = InferencePhase.RUNNING, progress = 100) }
                checkCancelled()
                result = LocalInferenceNative.generate(model.absolutePath, tokenizer.absolutePath, prompt, generationId)
                if (result.toByteArray(Charsets.UTF_8).size > 16384 || result.isBlank()) {
                    result = null
                    error = "A helyi modell nem adott megjeleníthető választ. Próbáld újra."
                }
            } catch (_: InterruptedException) {
                cancelled.set(true)
            } catch (_: LinkageError) {
                error = "A helyi AI ezen a készüléken nem tölthető be."
            } catch (_: Exception) {
                // Native exception details may carry implementation data. Never render or log them.
                error = "A helyi AI indítása vagy futtatása nem sikerült. Próbáld újra."
            } finally {
                val answer = result.orEmpty()
                val failure = error
                // Drain cancellation before allowing another call: a late cancel must never
                // cancel the next request. This worker remains the sole generation owner.
                cancellationWorker.execute {
                    main.post {
                        active = false
                        state = state.copy(
                            phase = when {
                                cancelled.get() -> InferencePhase.CANCELLED
                                failure != null -> InferencePhase.ERROR
                                else -> InferencePhase.COMPLETED
                            },
                            answer = if (cancelled.get()) "" else answer,
                            error = if (cancelled.get()) null else failure,
                            stopping = false,
                        )
                    }
                }
            }
        }
    }

    fun cancel() {
        if (!active || cancelled.getAndSet(true)) return
        state = state.copy(stopping = true)
        val generationId = requestId
        cancellationWorker.execute {
            try { LocalInferenceNative.cancel(generationId) } catch (_: LinkageError) {
                // A missing adapter is reported by the generation worker.
            } catch (_: Exception) {
                // Terminal state is published only once the generation worker finishes.
            }
        }
    }

    private fun checkCancelled() {
        if (cancelled.get()) throw InterruptedException()
    }

    private fun publish(update: (InferenceState) -> InferenceState) {
        main.post { if (active) state = update(state) }
    }

    private fun prepare(context: Context, directory: File, name: String, size: Long,
        sha256: String, base: Int, weight: Int): File {
        checkCancelled()
        val destination = File(directory, name)
        val partial = File(directory, "$name.partial")
        if (partial.exists() && !partial.delete()) throw IOException()
        if (destination.isFile && destination.length() == size &&
            digest(destination, size, base, weight) == sha256) return destination
        if (destination.exists() && !destination.delete()) throw IOException()
        try {
            context.assets.open("local-model/$name").use { input ->
                partial.outputStream().use { output ->
                    val buffer = ByteArray(1024 * 1024)
                    var copied = 0L
                    while (true) {
                        checkCancelled()
                        val count = input.read(buffer)
                        if (count < 0) break
                        copied += count
                        if (copied > size) throw IOException()
                        output.write(buffer, 0, count)
                        val progress = base + (copied * weight / size).toInt()
                        publish { it.copy(progress = progress) }
                    }
                    if (copied != size) throw IOException()
                    output.fd.sync()
                }
            }
            if (digest(partial, size, base, weight) != sha256) throw IOException()
            checkCancelled()
            if (!partial.renameTo(destination)) throw IOException()
            return destination
        } finally {
            if (partial.exists()) partial.delete()
        }
    }

    private fun digest(file: File, size: Long, base: Int, weight: Int): String {
        val hash = MessageDigest.getInstance("SHA-256")
        file.inputStream().use { input ->
            val buffer = ByteArray(1024 * 1024)
            var read = 0L
            while (true) {
                checkCancelled()
                val count = input.read(buffer)
                if (count < 0) break
                read += count
                if (read > size) throw IOException()
                hash.update(buffer, 0, count)
                val progress = base + (read * weight / size).toInt()
                publish { it.copy(progress = progress) }
            }
            if (read != size) throw IOException()
        }
        return hash.digest().joinToString("") { "%02x".format(it) }
    }
}
