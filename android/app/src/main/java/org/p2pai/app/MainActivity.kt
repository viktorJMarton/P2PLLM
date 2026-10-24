package org.p2pai.app

import android.os.Bundle
import android.content.Intent
import android.net.Uri
import android.provider.Settings
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.material3.MaterialTheme
import android.os.Handler
import android.os.Looper
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import java.util.concurrent.Executors
import java.io.File
import java.util.UUID
import uniffi.p2p_android_bridge.DiagnosticRecord
import uniffi.p2p_android_bridge.DiagnosticException
import uniffi.p2p_android_bridge.LocalDiagnostics
import uniffi.p2p_android_bridge.openLocalDiagnostics
import uniffi.p2p_android_bridge.nodeStatus

class MainActivity : ComponentActivity() {
    private val statusExecutor = Executors.newSingleThreadExecutor()
    private val mainHandler = Handler(Looper.getMainLooper())
    private var statusState by mutableStateOf<NodeStatusState>(NodeStatusState.Loading)
    private var requestInFlight = false
    private var diagnosticsState by mutableStateOf(LocalDiagnosticsState())
    private var diagnosticInFlight = false
    private var pendingDiagnosticId: String? = null
    private var localRuntime: LocalDiagnostics? = null
    @Volatile private var destroyed = false

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        pendingDiagnosticId = savedInstanceState?.getString("pending_local_diagnostic")
        setContent {
            MaterialTheme {
                OperatorShell(
                    statusState,
                    onRefresh = ::refreshStatus,
                    diagnostics = diagnosticsState,
                    onRunDiagnostic = ::runDiagnostic,
                    onRefreshDiagnostics = { refreshDiagnostics(0u) },
                    onNextDiagnostics = {
                        diagnosticsState.nextOffset?.let(::refreshDiagnostics)
                    },
                    onOpenAppSettings = {
                        startActivity(Intent(Settings.ACTION_APPLICATION_DETAILS_SETTINGS,
                            Uri.parse("package:$packageName")))
                    },
                    inference = LocalInferenceController.state,
                    onEditPrompt = LocalInferenceController::editPrompt,
                    onGenerate = { LocalInferenceController.generate(applicationContext) },
                    onStopInference = LocalInferenceController::cancel,
                )
            }
        }
        refreshStatus()
        refreshDiagnostics(0u)
    }

    private fun refreshStatus() {
        if (destroyed || requestInFlight) return
        requestInFlight = true
        statusState = NodeStatusState.Loading
        statusExecutor.execute {
            if (destroyed) return@execute
            // Native loading and inspection must run outside composition and the UI thread.
            val result = readStatus()
            mainHandler.post {
                if (!destroyed) {
                    requestInFlight = false
                    statusState = result
                }
            }
        }
    }

    // Accessed only by this Activity's executor. Rust retains process ownership
    // across Activity lifetimes; opening another wrapper never recovers live work.
    private fun diagnosticsRuntime(): LocalDiagnostics = localRuntime
        ?: openLocalDiagnostics(File(filesDir, "local-diagnostics.sqlite3").absolutePath)
            .also { localRuntime = it }

    private fun refreshDiagnostics(offset: UInt) {
        if (destroyed || diagnosticInFlight) return
        diagnosticInFlight = true
        diagnosticsState = diagnosticsState.copy(loading = true, error = null)
        statusExecutor.execute {
            if (destroyed) return@execute
            try {
                val page = diagnosticsRuntime().list(50u, offset)
                require(page.schemaVersion == 1u)
                val items = page.records.map(::diagnosticItem)
                mainHandler.post {
                    if (!destroyed) {
                        diagnosticInFlight = false
                        val restoredResult = items.firstOrNull {
                            it.requestId == pendingDiagnosticId && it.state !in listOf("queued", "running")
                        }
                        if (restoredResult != null) pendingDiagnosticId = null
                        diagnosticsState = diagnosticsState.copy(
                            loading = false, available = true, error = null,
                            records = items, offset = page.offset, nextOffset = page.nextOffset,
                            lastResult = restoredResult ?: diagnosticsState.lastResult,
                            requiresRestart = diagnosticsState.requiresRestart && restoredResult == null,
                        )
                    }
                }
            } catch (_: LinkageError) {
                diagnosticFailed("A helyi ellenőrzés nem tölthető be ezen a készüléken.")
            } catch (error: DiagnosticException) {
                diagnosticFailed(error)
            } catch (_: RuntimeException) {
                diagnosticFailed("Az előzményeket most nem sikerült betölteni. Próbáld újra.")
            } catch (_: Exception) {
                diagnosticFailed("Az előzmények nem érhetők el. Próbáld újra a frissítést.")
            }
        }
    }

    private fun runDiagnostic() {
        if (destroyed || diagnosticInFlight || diagnosticsState.requiresRestart) return
        val requestId = pendingDiagnosticId
            ?: "${System.currentTimeMillis()}-${UUID.randomUUID()}".also {
                pendingDiagnosticId = it
            }
        diagnosticInFlight = true
        diagnosticsState = diagnosticsState.copy(running = true, error = null, lastResult = null)
        statusExecutor.execute {
            if (destroyed) return@execute
            try {
                val runtime = diagnosticsRuntime()
                val result = diagnosticItem(runtime.run(requestId))
                // A successful result is shown even if the following history read
                // fails: do not rerun completed work to repair a display refresh.
                mainHandler.post {
                    if (!destroyed) {
                        pendingDiagnosticId = null
                        diagnosticsState = diagnosticsState.copy(lastResult = result)
                    }
                }
                val page = runtime.list(50u, 0u)
                require(page.schemaVersion == 1u)
                val items = page.records.map(::diagnosticItem)
                mainHandler.post {
                    if (!destroyed) {
                        diagnosticInFlight = false
                        diagnosticsState = diagnosticsState.copy(
                            running = false, available = true, records = items,
                            offset = page.offset, nextOffset = page.nextOffset,
                        )
                    }
                }
            } catch (_: LinkageError) {
                diagnosticFailed("A helyi ellenőrzés nem tölthető be ezen a készüléken.")
            } catch (error: DiagnosticException) {
                diagnosticFailed(error)
            } catch (_: Exception) {
                diagnosticFailed(
                    "Az ellenőrzést vagy az előzmények frissítését nem sikerült befejezni. " +
                        "Frissítsd az előzményeket, vagy próbáld újra.",
                )
            }
        }
    }

    private fun diagnosticItem(record: DiagnosticRecord): LocalDiagnosticItem {
        require(record.schemaVersion == 1u)
        return LocalDiagnosticItem(
            requestId = record.requestId,
            state = record.state.toString().lowercase(),
            version = record.version.toString(),
        )
    }

    private fun diagnosticFailed(error: DiagnosticException) {
        val restart = error is DiagnosticException.RecoveryRequired
        val message = when (error) {
            is DiagnosticException.Busy -> "Egy helyi ellenőrzés még dolgozik. Frissítsd az előzményeket később."
            is DiagnosticException.RecoveryRequired ->
                "A helyi ellenőrzés félbeszakadt. Állítsd le teljesen az alkalmazást az Android " +
                    "alkalmazásbeállításaiban, majd indítsd újra. A képernyő újranyitása önmagában nem elég."
            is DiagnosticException.StorageUnavailable -> "A helyi tároló most nem érhető el. Frissítsd az előzményeket, vagy próbáld újra később."
            is DiagnosticException.InvalidRequest -> "Az ellenőrzési kérés nem fogadható el. Frissítsd az előzményeket."
            is DiagnosticException.Internal -> "Helyi ellenőrzési hiba történt. Próbáld újra később."
        }
        mainHandler.post {
            if (!destroyed) {
                diagnosticInFlight = false
                diagnosticsState = diagnosticsState.copy(
                    loading = false, running = false, error = message,
                    requiresRestart = diagnosticsState.requiresRestart || restart,
                )
            }
        }
    }

    private fun diagnosticFailed(message: String) {
        mainHandler.post {
            if (!destroyed) {
                diagnosticInFlight = false
                diagnosticsState = diagnosticsState.copy(
                    loading = false, running = false, error = message,
                )
            }
        }
    }

    override fun onSaveInstanceState(outState: Bundle) {
        pendingDiagnosticId?.let { outState.putString("pending_local_diagnostic", it) }
        super.onSaveInstanceState(outState)
    }

    private fun readStatus(): NodeStatusState = try {
        val status = nodeStatus()
        NodeStatusState.Ready(
            schemaVersion = status.schemaVersion.toString(),
            networkEnabled = status.networkEnabled,
            privateComputeAvailable = status.privateComputeAvailable,
            privateLearningAvailable = status.privateLearningAvailable,
        )
    } catch (_: LinkageError) {
        NodeStatusState.Unavailable
    } catch (_: RuntimeException) {
        // Native diagnostics can contain implementation details; never display or log them.
        NodeStatusState.Failed
    }

    override fun onDestroy() {
        destroyed = true
        mainHandler.removeCallbacksAndMessages(null)
        // Finish any native transaction, then release only this wrapper. The
        // native process owner stays alive; screen teardown is not cancellation.
        statusExecutor.execute {
            localRuntime?.destroy()
            localRuntime = null
        }
        statusExecutor.shutdown()
        super.onDestroy()
    }

    override fun onStop() {
        if (!isChangingConfigurations) LocalInferenceController.cancel()
        super.onStop()
    }
}
