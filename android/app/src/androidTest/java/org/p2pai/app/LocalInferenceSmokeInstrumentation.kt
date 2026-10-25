package org.p2pai.app

import android.app.Activity
import android.app.Instrumentation
import android.content.Intent
import android.os.Bundle
import android.os.SystemClock
import android.util.JsonReader
import android.util.JsonToken
import android.view.accessibility.AccessibilityNodeInfo
import android.view.inputmethod.InputMethodManager
import java.security.MessageDigest
import java.util.Locale
import java.io.StringReader
import java.math.BigDecimal
import java.nio.ByteBuffer
import java.nio.charset.CodingErrorAction
import org.json.JSONArray
import org.json.JSONObject

/** Public synthetic fixtures only. Results never include prompts, answers or exception details. */
class LocalInferenceSmokeInstrumentation : Instrumentation() {
    private var restartMode = false
    private var greetingMode = false
    private var pilotMode = false
    private var phaseDeadline = SystemClock.elapsedRealtime() + TIMEOUT_MS
    private var phase = "START"
        set(value) {
            field = value
            phaseDeadline = SystemClock.elapsedRealtime() + TIMEOUT_MS
        }
    private var completedChecks = 0
    private val results = Bundle()

    override fun onCreate(arguments: Bundle?) {
        super.onCreate(arguments)
        restartMode = arguments?.getString("mode") == "restart"
        greetingMode = arguments?.getString("mode") == "g01"
        pilotMode = arguments?.getString("mode") == "pilot"
        start()
    }

    override fun onStart() {
        try {
            phase = "LAUNCH"
            var activity = launch()
            if (pilotMode) {
                runPilot()
            } else if (greetingMode) {
                phase = "G01_PUBLIC_GREETING"
                requireSmoke(!snapshot().busy, "G01_ALREADY_BUSY")
                ask(GREETING)
                val terminal = await { !it.busy }
                requireSmoke(terminal.prompt == GREETING, "G01_INPUT_MISMATCH")
                requireSmoke(terminal.phase == InferencePhase.COMPLETED, "G01_NOT_COMPLETED")
                recordGreetingObservation(terminal.answer)
                passed("g01_observation_completed")
            } else if (restartMode) {
                phase = "RESTART_EMPTY"
                val initial = snapshot()
                requireSmoke(initial.phase == InferencePhase.IDLE && initial.prompt.isEmpty() &&
                    initial.answer.isEmpty(), "RESTART_NOT_EMPTY")
                passed("restart_empty")
                phase = "RESTART_ANSWER"
                ask()
                requireAnswer()
                passed("restart_answer")
            } else {
                phase = "VISIBLE_AI_QUESTION_ANSWER"
                clickAccessibleText("AI")
                setAccessibleQuestion()
                onMain {
                    val keyboard = targetContext.getSystemService(InputMethodManager::class.java)
                    keyboard.hideSoftInputFromWindow(activity.window.decorView.windowToken, 0)
                }
                clickAccessibleText("Válasz kérése")
                requireAnswer()
                requireVisibleAnswer()
                passed("visible_ai_question_answer")

                phase = "PREPARING_CANCEL"
                onMain {
                    LocalInferenceController.editPrompt(QUESTION)
                    LocalInferenceController.generate(targetContext)
                    LocalInferenceController.cancel()
                    val stopping = LocalInferenceController.state
                    LocalInferenceController.generate(targetContext)
                    stopping === LocalInferenceController.state
                }.also { requireSmoke(it, "STOPPING_RETRY_ACCEPTED") }
                requireCancelled()
                passed("preparing_cancel_and_retry_blocked")

                phase = "PREPARING_RECREATION"
                val preparingMonitor = addMonitor(MainActivity::class.java.name, null, false)
                try {
                    val duplicateRejected = onMain {
                        LocalInferenceController.editPrompt(QUESTION)
                        LocalInferenceController.generate(targetContext)
                        val first = LocalInferenceController.state
                        LocalInferenceController.generate(targetContext)
                        val same = first === LocalInferenceController.state
                        activity.recreate()
                        same
                    }
                    requireSmoke(duplicateRejected, "DUPLICATE_ACCEPTED")
                    activity = recreated(preparingMonitor)
                    requireRetained(QUESTION)
                    requireAnswer()
                    passed("preparing_recreation_answer_and_duplicate_rejected")
                } finally { removeMonitor(preparingMonitor) }

                phase = "RUNNING_RECREATION_CANCEL"
                ask(LONG_QUESTION)
                await { it.phase == InferencePhase.RUNNING }
                val runningMonitor = addMonitor(MainActivity::class.java.name, null, false)
                try {
                    onMain { activity.recreate() }
                    activity = recreated(runningMonitor)
                    requireRetained(LONG_QUESTION)
                    requireSmoke(snapshot().busy, "COMPLETED_BEFORE_RUNNING_CANCEL")
                    onMain { LocalInferenceController.cancel() }
                    requireCancelled()
                    passed("running_recreation_and_cancel")
                } finally { removeMonitor(runningMonitor) }

                phase = "BACKGROUND_CANCEL"
                ask(LONG_QUESTION)
                await { it.phase == InferencePhase.RUNNING }
                val moved = onMain { activity.moveTaskToBack(true) }
                requireSmoke(moved, "BACKGROUND_MOVE_FAILED")
                requireCancelled()
                passed("background_cancel")

                phase = "FOREGROUND_RETRY"
                activity = launch()
                ask()
                requireAnswer()
                passed("foreground_retry_answer")
            }
            phase = "FINISH"
            onMain { activity.finish() }
            results.putBoolean("passed", true)
            results.putInt("completed_checks", completedChecks)
            finish(Activity.RESULT_OK, results)
        } catch (failure: SmokeFailure) {
            failed(failure.code)
        } catch (_: Throwable) {
            failed("UNEXPECTED_FAILURE")
        }
    }

    private fun launch(): MainActivity {
        val intent = Intent(targetContext, MainActivity::class.java)
            .addFlags(Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TOP)
        val activity = startActivitySync(intent) as? MainActivity
            ?: throw SmokeFailure("LAUNCH_FAILED")
        waitForIdleSync()
        return activity
    }

    private fun recreated(monitor: ActivityMonitor): MainActivity {
        val remaining = (phaseDeadline - SystemClock.elapsedRealtime()).coerceAtLeast(1L)
        val activity = monitor.waitForActivityWithTimeout(remaining) as? MainActivity
            ?: throw SmokeFailure("RECREATE_TIMEOUT")
        waitForIdleSync()
        return activity
    }

    private fun ask(prompt: String = QUESTION) {
        onMain {
            LocalInferenceController.editPrompt(prompt)
            LocalInferenceController.generate(targetContext)
        }
    }

    private fun requireRetained(prompt: String) {
        val current = snapshot()
        requireSmoke(current.prompt == prompt && current.phase != InferencePhase.CANCELLED &&
            current.phase != InferencePhase.ERROR && current.phase != InferencePhase.IDLE,
            "RECREATION_STATE_LOST")
    }

    private fun requireAnswer() {
        val terminal = await { !it.busy }
        val answer = terminal.answer
        val exactExpected = answer.trim() == "2"
        val containsProtocol = answer.contains("<|") || answer.contains("|>")
        val containsThought = answer.contains("<think>") || answer.contains("</think>")
        if (terminal.phase != InferencePhase.COMPLETED || !exactExpected || containsProtocol || containsThought) {
            // Only the fixed public QUESTION reaches this helper. Emit bounded
            // diagnostics for that synthetic fixture, never answer text or errors.
            val bytes = answer.toByteArray(Charsets.UTF_8)
            results.putInt("answer_bytes", bytes.size)
            results.putString("answer_digest", MessageDigest.getInstance("SHA-256")
                .digest(bytes).joinToString("") { "%02x".format(it) })
            results.putBoolean("contains_expected_digit", Regex("\\b2\\b").containsMatchIn(answer))
            results.putBoolean("contains_protocol", containsProtocol)
            results.putBoolean("contains_thought", containsThought)
            results.putBoolean("exact_expected", exactExpected)
            results.putString("terminal_phase", terminal.phase.name)
        }
        requireSmoke(terminal.phase == InferencePhase.COMPLETED, "ANSWER_NOT_COMPLETED")
        requireSmoke(exactExpected && !containsProtocol && !containsThought, "ANSWER_CHECK_FAILED")
    }

    private fun requireCancelled() {
        val terminal = await { !it.busy }
        requireSmoke(terminal.phase == InferencePhase.CANCELLED && terminal.answer.isEmpty() &&
            !terminal.stopping, "CANCEL_NOT_TERMINAL")
    }

    private fun recordGreetingObservation(answer: String) {
        val observation = answerObservation(answer)
        observation.keys().forEach { key ->
            when (val value = observation.get(key)) {
                is Int -> results.putInt(key, value)
                is String -> results.putString(key, value)
                is Boolean -> results.putBoolean(key, value)
                else -> throw SmokeFailure("OBSERVATION_TYPE_INVALID")
            }
        }
    }

    // Used only for the fixed G01 or the embedded frozen public pilot corpus.
    private fun answerObservation(answer: String): JSONObject {
        fun digest(bytes: ByteArray) = MessageDigest.getInstance("SHA-256")
            .digest(bytes).joinToString("") { "%02x".format(it) }
        val raw = answer.toByteArray(Charsets.UTF_8)
        val trimmed = answer.trim()
        val trimmedBytes = trimmed.toByteArray(Charsets.UTF_8)
        val words = Regex("[\\p{L}\\p{N}_]+")
            .findAll(trimmed.lowercase(Locale.ROOT)).map { it.value }.toList()
        val maxRepeated = words.windowed(3).groupingBy { it }.eachCount().values.maxOrNull() ?: 0
        return JSONObject()
            .put("answer_bytes", raw.size)
            .put("answer_digest", digest(raw))
            .put("answer_trimmed_bytes", trimmedBytes.size)
            .put("answer_trimmed_digest", digest(trimmedBytes))
            .put("max_repeated_word_trigram", maxRepeated)
            .put("pathological_repetition_flag", maxRepeated >= 3)
            .put("directive_fragment_flag", Regex("/no(?:_think)?\\b", RegexOption.IGNORE_CASE)
                .containsMatchIn(answer))
            .put("contains_protocol", answer.contains("<|") || answer.contains("|>"))
            .put("contains_thought", answer.contains("<think>") || answer.contains("</think>"))
            .put("coherence_scored", false)
    }

    private fun runPilot() {
        phase = "PILOT_CORPUS"
        val cases = loadPilotCases()
        val observations = JSONArray()
        results.putString("pilot_results_json", observations.toString())
        for (index in 0 until cases.length()) {
            val case = cases.getJSONObject(index)
            val id = case.getString("id")
            phase = "PILOT_$id"
            phaseDeadline = SystemClock.elapsedRealtime() + PILOT_TIMEOUT_MS
            try {
                requireSmoke(!snapshot().busy, "PILOT_ALREADY_BUSY")
                val prompt = case.getString("prompt")
                ask(prompt)
                val terminal = await { !it.busy }
                requireSmoke(terminal.prompt == prompt, "PILOT_INPUT_MISMATCH")
                requireSmoke(terminal.phase == InferencePhase.COMPLETED, "PILOT_NOT_COMPLETED")
                val observation = answerObservation(terminal.answer)
                    .put("id", id).put("status", "observed")
                    .put("terminal_phase", terminal.phase.name)
                    .put("expected_kind", case.getString("expected_kind"))
                when (case.getString("expected_kind")) {
                    "exact" -> {
                        val matches = terminal.answer.trim() == case.getString("expected")
                        observation.put("deterministic_match", matches)
                    }
                    "json" -> {
                        val matches = matchesPilotJson(terminal.answer)
                        observation.put("deterministic_match", matches)
                    }
                    "review" -> observation.put("deterministic_match", JSONObject.NULL)
                }
                observation.put("correctness", "not_human_rated")
                observations.put(observation)
                completedChecks += 1
                results.putString("pilot_results_json", observations.toString())
            } catch (failure: SmokeFailure) {
                observations.put(JSONObject().put("id", id).put("status", "error")
                    .put("error_code", failure.code))
                results.putString("pilot_results_json", observations.toString())
                throw failure
            } catch (_: Throwable) {
                observations.put(JSONObject().put("id", id).put("status", "error")
                    .put("error_code", "PILOT_CASE_FAILED"))
                results.putString("pilot_results_json", observations.toString())
                throw SmokeFailure("PILOT_CASE_FAILED")
            }
        }
        results.putBoolean("pilot_observations_completed", true)
        results.putBoolean("human_review_complete", false)
    }

    private fun loadPilotCases(): JSONArray {
        val bytes = ByteArray(16385)
        var size = 0
        context.assets.open("local-inference-quality.json").use { input ->
            while (true) {
                val count = input.read(bytes, size, bytes.size - size)
                if (count < 0) break
                requireSmoke(count > 0, "PILOT_CORPUS_READ_FAILED")
                size += count
                requireSmoke(size <= 16384, "PILOT_CORPUS_SIZE_INVALID")
            }
        }
        requireSmoke(size > 0, "PILOT_CORPUS_SIZE_INVALID")
        val text = Charsets.UTF_8.newDecoder().onMalformedInput(CodingErrorAction.REPORT)
            .onUnmappableCharacter(CodingErrorAction.REPORT).decode(ByteBuffer.wrap(bytes, 0, size)).toString()
        val corpus = JSONObject(text)
        requireSmoke(corpus.keys().asSequence().toSet() == setOf("schema_version", "scope", "cases") &&
            corpus.get("schema_version") == 1 && corpus.get("scope") is String, "PILOT_SCHEMA_INVALID")
        val cases = corpus.getJSONArray("cases")
        val expectedIds = listOf("G01") + (1..12).map { "HU%02d".format(Locale.ROOT, it) }
        val exactIds = setOf("HU01", "HU02", "HU04", "HU05", "HU09", "HU11")
        requireSmoke(cases.length() == expectedIds.size, "PILOT_CASES_INVALID")
        for (index in expectedIds.indices) {
            val case = cases.getJSONObject(index)
            val id = expectedIds[index]
            requireSmoke(case.get("id") == id && case.get("prompt") is String, "PILOT_CASE_INVALID")
            val prompt = case.getString("prompt")
            requireSmoke(prompt.isNotBlank() && prompt.toByteArray(Charsets.UTF_8).size <= 1024 &&
                !prompt.contains('\u0000') && !prompt.contains("<|") && !prompt.contains("|>") &&
                !prompt.contains("<think>") && !prompt.contains("</think>"), "PILOT_INPUT_INVALID")
            val expectedKind = when { id in exactIds -> "exact"; id == "HU06" -> "json"; else -> "review" }
            val fields = when {
                id == "G01" -> setOf("id", "prompt", "expected_kind", "blocking")
                expectedKind != "review" -> setOf("id", "prompt", "expected_kind", "expected")
                else -> setOf("id", "prompt", "expected_kind")
            }
            requireSmoke(case.keys().asSequence().toSet() == fields &&
                case.get("expected_kind") == expectedKind, "PILOT_EXPECTATION_INVALID")
            if (id == "G01") requireSmoke(prompt == GREETING && case.get("blocking") == true, "PILOT_G01_INVALID")
            if (expectedKind == "exact") requireSmoke(case.get("expected") is String, "PILOT_EXACT_INVALID")
            if (expectedKind == "json") {
                val expected = case.getJSONObject("expected")
                requireSmoke(expected.keys().asSequence().toSet() == setOf("nev", "kor") &&
                    expected.get("nev") == "Éva" && expected.get("kor") is Number &&
                    BigDecimal(expected.get("kor").toString()).compareTo(BigDecimal(31)) == 0,
                    "PILOT_JSON_INVALID")
            }
        }
        return cases
    }

    private fun matchesPilotJson(answer: String): Boolean {
        return try {
            JsonReader(StringReader(answer)).use { reader ->
                reader.isLenient = false
                reader.beginObject()
                val seen = mutableSetOf<String>()
                var matches = true
                while (reader.hasNext()) {
                    val key = reader.nextName()
                    if (!seen.add(key)) return false
                    when (key) {
                        "nev" -> {
                            if (reader.peek() != JsonToken.STRING) return false
                            matches = reader.nextString() == "Éva" && matches
                        }
                        "kor" -> {
                            if (reader.peek() != JsonToken.NUMBER) return false
                            matches = BigDecimal(reader.nextString()).compareTo(BigDecimal(31)) == 0 && matches
                        }
                        else -> return false
                    }
                }
                reader.endObject()
                matches && seen == setOf("nev", "kor") && reader.peek() == JsonToken.END_DOCUMENT
            }
        } catch (_: Exception) { false }
    }

    private fun await(predicate: (InferenceState) -> Boolean): InferenceState {
        while (SystemClock.elapsedRealtime() < phaseDeadline) {
            val current = snapshot()
            if (predicate(current)) return current
            if (current.phase == InferencePhase.ERROR) throw SmokeFailure("CONTROLLER_ERROR")
            SystemClock.sleep(20)
        }
        throw SmokeFailure("STATE_TIMEOUT")
    }

    private fun snapshot(): InferenceState = onMain { LocalInferenceController.state }

    private fun clickAccessibleText(text: String) {
        while (SystemClock.elapsedRealtime() < phaseDeadline) {
            val node = findAppNode { it.text?.toString() == text }
            if (node != null && clickClosestParent(node)) return
            SystemClock.sleep(50)
        }
        throw SmokeFailure("UI_CLICK_TIMEOUT")
    }

    // Consumes the node and each acquired parent without serializing their text.
    private fun clickClosestParent(node: AccessibilityNodeInfo): Boolean {
        var current: AccessibilityNodeInfo? = node
        var depth = 0
        while (current != null && depth++ < 12) {
            val item = current
            if (item.isEnabled && item.isClickable) {
                return try {
                    item.performAction(AccessibilityNodeInfo.AccessibilityAction.ACTION_SHOW_ON_SCREEN.id)
                    SystemClock.sleep(100)
                    item.performAction(AccessibilityNodeInfo.ACTION_CLICK)
                } finally { item.recycle() }
            }
            current = item.parent
            item.recycle()
        }
        current?.recycle()
        return false
    }

    private fun setAccessibleQuestion() {
        while (SystemClock.elapsedRealtime() < phaseDeadline) {
            val field = findAppNode { it.className?.toString() == "android.widget.EditText" && it.isEnabled }
            if (field != null) {
                val accepted = try {
                    field.performAction(AccessibilityNodeInfo.AccessibilityAction.ACTION_SHOW_ON_SCREEN.id)
                    val arguments = Bundle().apply {
                        putCharSequence(AccessibilityNodeInfo.ACTION_ARGUMENT_SET_TEXT_CHARSEQUENCE, QUESTION)
                    }
                    field.performAction(AccessibilityNodeInfo.ACTION_SET_TEXT, arguments)
                } finally { field.recycle() }
                if (accepted && snapshot().prompt == QUESTION) return
            }
            SystemClock.sleep(50)
        }
        throw SmokeFailure("UI_SET_TEXT_TIMEOUT")
    }

    private fun requireVisibleAnswer() {
        while (SystemClock.elapsedRealtime() < phaseDeadline) {
            val answer = findAppNode { it.text?.toString()?.trim() == "2" }
            if (answer != null) {
                val visible = try {
                    if (!answer.isVisibleToUser) {
                        answer.performAction(AccessibilityNodeInfo.AccessibilityAction.ACTION_SHOW_ON_SCREEN.id)
                    }
                    answer.isVisibleToUser
                } finally { answer.recycle() }
                if (visible) return
            }
            SystemClock.sleep(50)
        }
        throw SmokeFailure("UI_ANSWER_NOT_VISIBLE")
    }

    private fun findAppNode(predicate: (AccessibilityNodeInfo) -> Boolean): AccessibilityNodeInfo? {
        val root = uiAutomation.rootInActiveWindow ?: return null
        if (root.packageName?.toString() != targetContext.packageName) {
            root.recycle()
            return null
        }
        var budget = 512
        fun visit(node: AccessibilityNodeInfo, depth: Int): AccessibilityNodeInfo? {
            if (--budget < 0 || depth > 32) {
                node.recycle()
                return null
            }
            if (node.packageName?.toString() == targetContext.packageName && predicate(node)) return node
            for (index in 0 until node.childCount) {
                val child = node.getChild(index) ?: continue
                val found = visit(child, depth + 1)
                if (found != null) {
                    node.recycle()
                    return found
                }
            }
            node.recycle()
            return null
        }
        return visit(root, 0)
    }

    private fun <T> onMain(action: () -> T): T {
        var result: T? = null
        var failed = false
        // Never throw a test assertion on the application main thread: that would
        // crash the target process and bypass the sanitized instrumentation bundle.
        runOnMainSync {
            try { result = action() } catch (_: Throwable) { failed = true }
        }
        if (failed) throw SmokeFailure("MAIN_ACTION_FAILED")
        @Suppress("UNCHECKED_CAST")
        return result as T
    }

    private fun requireSmoke(condition: Boolean, code: String) {
        if (!condition) throw SmokeFailure(code)
    }

    private fun passed(key: String) {
        results.putBoolean(key, true)
        completedChecks += 1
    }

    private fun failed(code: String) {
        results.putBoolean("passed", false)
        results.putInt("completed_checks", completedChecks)
        results.putString("phase", phase)
        results.putString("error_code", code)
        finish(Activity.RESULT_CANCELED, results)
    }

    private class SmokeFailure(val code: String) : Exception()

    companion object {
        private const val TIMEOUT_MS = 120000L
        private const val PILOT_TIMEOUT_MS = 300000L
        private const val QUESTION = "Write only the integer answer: 1+1."
        private const val GREETING = "Hogy vagy?"
        private const val LONG_QUESTION = "Count from 1 to 1000, writing every integer in order."
    }
}
