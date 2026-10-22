package org.p2pai.app

import androidx.compose.foundation.horizontalScroll
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.heightIn
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.safeDrawingPadding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.semantics.Role
import androidx.compose.ui.semantics.heading
import androidx.compose.ui.semantics.role
import androidx.compose.ui.semantics.selected
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.unit.dp

internal sealed interface NodeStatusState {
    data object Loading : NodeStatusState
    data object Unavailable : NodeStatusState
    data object Failed : NodeStatusState
    data class Ready(
        val schemaVersion: String,
        val networkEnabled: Boolean,
        val privateComputeAvailable: Boolean,
        val privateLearningAvailable: Boolean,
    ) : NodeStatusState
}

private enum class Destination(val label: String, val title: String) {
    OVERVIEW("Áttekintés", "Helyi csomópont"),
    SESSION("AI", "AI-munkamenet"),
    JOBS("Feladatok", "Hálózati feladatok"),
    MODELS("Modellek", "Modellek és tanulás"),
    RESOURCES("Erőforrások", "Erőforrások és adatvédelem"),
}

@Composable
internal fun OperatorShell(state: NodeStatusState, onRefresh: () -> Unit) {
    var selection by rememberSaveable { mutableStateOf(Destination.OVERVIEW.name) }
    val destination = Destination.entries.firstOrNull { it.name == selection }
        ?: Destination.OVERVIEW
    Surface(Modifier.fillMaxSize(), color = MaterialTheme.colorScheme.background) {
        Column(Modifier.safeDrawingPadding()) {
            Text(
                "P2P AI",
                style = MaterialTheme.typography.headlineMedium,
                modifier = Modifier.padding(horizontal = 20.dp, vertical = 12.dp),
            )
            Row(Modifier.fillMaxWidth().horizontalScroll(rememberScrollState())) {
                Destination.entries.forEach { item ->
                    TextButton(
                        onClick = { selection = item.name },
                        modifier = Modifier.heightIn(min = 48.dp).semantics {
                            selected = item == destination
                            role = Role.Tab
                        },
                    ) {
                        Text(
                            item.label,
                            style = if (item == destination) MaterialTheme.typography.titleSmall
                            else MaterialTheme.typography.bodyMedium,
                        )
                    }
                }
            }
            Column(
                Modifier.weight(1f).fillMaxWidth().verticalScroll(rememberScrollState())
                    .padding(20.dp),
                verticalArrangement = Arrangement.spacedBy(16.dp),
            ) {
                Text(
                    destination.title,
                    style = MaterialTheme.typography.headlineSmall,
                    modifier = Modifier.semantics { heading() },
                )
                StatusPanel(state, onRefresh)
                when (destination) {
                    Destination.OVERVIEW -> Overview(state)
                    Destination.SESSION -> UnavailableFeature(
                        "Helyi AI", "A modellbetöltés és a szöveggenerálás még nincs bekötve. " +
                            "Ez a felület jelenleg a csomópont állapotát tudja lekérni.",
                        "Munkamenet indítása",
                    )
                    Destination.JOBS -> UnavailableFeature(
                        "Hálózati munkavégzés", "Feladatlista és hitelesített peer-kapcsolat még " +
                            "nem érhető el ezen a felületen. A hálózat indítása és leállítása " +
                            "még nincs bekötve.", "Hálózat kezelése",
                    )
                    Destination.MODELS -> UnavailableFeature(
                        "Modellek és frissítések", "Nincs bekötött modellnyilvántartás. " +
                            "Modellbetöltés, közös tanulás, frissítésaktiválás és visszaállítás " +
                            "jelenleg nem indítható.", "Modell betöltése",
                    )
                    Destination.RESOURCES -> Resources(state)
                }
            }
        }
    }
}

@Composable
private fun StatusPanel(state: NodeStatusState, onRefresh: () -> Unit) {
    InfoCard("Állapotkapcsolat") {
        when (state) {
            NodeStatusState.Loading -> {
                CircularProgressIndicator()
                Text("Helyi állapot lekérése…")
            }
            NodeStatusState.Unavailable -> Text(
                "A natív állapothíd nem tölthető be ebben a környezetben. " +
                    "A csomópont állapota ismeretlen.",
            )
            NodeStatusState.Failed -> Text(
                "Az állapot lekérése nem sikerült. A csomópont állapota ismeretlen. " +
                    "Próbáld újra a frissítést.",
            )
            is NodeStatusState.Ready -> Text(
                "A helyi mag válaszolt. Sémaverzió: ${state.schemaVersion}. " +
                    "A híd jelenleg az alapállapotot adja vissza; ez nem futó feladatok mérése.",
            )
        }
        Button(
            onClick = onRefresh,
            enabled = state != NodeStatusState.Loading,
            modifier = Modifier.heightIn(min = 48.dp),
        ) { Text("Állapot frissítése") }
    }
}

@Composable
private fun Overview(state: NodeStatusState) {
    if (state is NodeStatusState.Ready) {
        InfoCard("A mag által jelzett állapot") {
            Text("Hálózat: ${if (state.networkEnabled) "bekapcsolva" else "kikapcsolva"}")
            Text("Privát számítás: ${availability(state.privateComputeAvailable)}")
            Text("Privát tanulás: ${availability(state.privateLearningAvailable)}")
        }
    }
    InfoCard("Fejlesztési állapot") {
        Text("A navigáció és az állapotfrissítés használható. Az AI-, hálózati és " +
            "tanulási műveletekhez további mag- és platformintegráció szükséges.")
    }
}

@Composable
private fun Resources(state: NodeStatusState) {
    InfoCard("Adatvédelmi képességek") {
        if (state is NodeStatusState.Ready) {
            Text("Privát számítás: ${availability(state.privateComputeAvailable)}")
            Text("Privát tanulás: ${availability(state.privateLearningAvailable)}")
        } else {
            Text("Az adatvédelmi képességek állapota a mag válaszáig ismeretlen.")
        }
        Text("A képességjelzés önmagában nem adatvédelmi bizonyíték. " +
            "A titkosított kapcsolat önmagában nem védi az adatot a számítást végző peertől.")
    }
    UnavailableFeature(
        "Erőforrás-korlátok",
        "Memória-, akkumulátor- és hőmérsékletmérés, valamint erőforráspolitika " +
            "módosítása még nincs bekötve. Nincs megjeleníthető mért érték.",
        "Korlátok beállítása",
    )
}

private fun availability(available: Boolean): String =
    if (available) "a mag elérhetőnek jelzi" else "nem elérhető"

@Composable
private fun UnavailableFeature(title: String, explanation: String, action: String) {
    InfoCard(title) {
        Text(explanation)
        Button(onClick = {}, enabled = false, modifier = Modifier.heightIn(min = 48.dp)) {
            Text(action)
        }
    }
}

@Composable
private fun InfoCard(title: String, content: @Composable () -> Unit) {
    Card(Modifier.fillMaxWidth()) {
        Column(
            Modifier.padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp),
        ) {
            Text(title, style = MaterialTheme.typography.titleMedium)
            content()
        }
    }
}
