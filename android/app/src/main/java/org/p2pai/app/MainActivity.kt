package org.p2pai.app

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.material3.MaterialTheme
import android.os.Handler
import android.os.Looper
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import java.util.concurrent.Executors
import uniffi.p2p_android_bridge.nodeStatus

class MainActivity : ComponentActivity() {
    private val statusExecutor = Executors.newSingleThreadExecutor()
    private val mainHandler = Handler(Looper.getMainLooper())
    private var statusState by mutableStateOf<NodeStatusState>(NodeStatusState.Loading)
    private var requestInFlight = false
    private var destroyed = false

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            MaterialTheme {
                OperatorShell(statusState, onRefresh = ::refreshStatus)
            }
        }
        refreshStatus()
    }

    private fun refreshStatus() {
        if (destroyed || requestInFlight) return
        requestInFlight = true
        statusState = NodeStatusState.Loading
        statusExecutor.execute {
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
        statusExecutor.shutdownNow()
        super.onDestroy()
    }
}
