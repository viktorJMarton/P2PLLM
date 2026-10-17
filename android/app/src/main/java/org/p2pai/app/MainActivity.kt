package org.p2pai.app

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import uniffi.p2p_android_bridge.nodeStatus

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            MaterialTheme {
                val status = try {
                    nodeStatus()
                } catch (error: UnsatisfiedLinkError) {
                    null
                }
                Column(Modifier.padding(24.dp)) {
                    Text("P2P AI – helyi állapot")
                    if (status == null) {
                        Text("A Rust híd nem érhető el ezen a builden.")
                    } else {
                        Text("Séma: ${status.schemaVersion}")
                        Text("Hálózat: ${if (status.networkEnabled) "bekapcsolva" else "kikapcsolva"}")
                        Text("Privát számítás: ${if (status.privateComputeAvailable) "elérhető" else "nem elérhető"}")
                        Text("Privát tanulás: ${if (status.privateLearningAvailable) "elérhető" else "nem elérhető"}")
                    }
                }
            }
        }
    }
}
