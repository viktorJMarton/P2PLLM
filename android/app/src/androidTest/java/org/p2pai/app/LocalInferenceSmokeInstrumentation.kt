package org.p2pai.app

import android.app.Activity
import android.app.Instrumentation
import android.content.Intent
import android.os.Bundle
import android.os.SystemClock
import android.view.accessibility.AccessibilityNodeInfo
import android.view.inputmethod.InputMethodManager
import java.security.MessageDigest

/** Public synthetic fixtures only. Results never include prompts, answers or exception details. */
class LocalInferenceSmokeInstrumentation : Instrumentation() {
    private var restartMode = false
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
        start()
    }

    override fun onStart() {
        try {
            phase = "LAUNCH"
            var activity = launch()
            if (restartMode) {
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
        private const val QUESTION = "Write only the integer answer: 1+1."
        private const val LONG_QUESTION = "Count from 1 to 1000, writing every integer in order."
    }
}
