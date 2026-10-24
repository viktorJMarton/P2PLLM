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
import androidx.compose.material3.OutlinedTextField
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
import java.text.DateFormat
import java.util.Date

internal data class LocalDiagnosticItem(
    val requestId: String,
    val state: String,
    val version: String,
)

internal data class LocalDiagnosticsState(
    val loading: Boolean = true,
    val running: Boolean = false,
    val available: Boolean = false,
    val records: List<LocalDiagnosticItem> = emptyList(),
    val offset: UInt = 0u,
    val nextOffset: UInt? = null,
    val lastResult: LocalDiagnosticItem? = null,
    val error: String? = null,
    val requiresRestart: Boolean = false,
)

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
    JOBS("Feladatok", "Helyi ellenőrzések"),
    MODELS("Modellek", "Modellek és tanulás"),
    RESOURCES("Erőforrások", "Erőforrások és adatvédelem"),
}

@Composable
internal fun OperatorShell(
    state: NodeStatusState,
    onRefresh: () -> Unit,
    diagnostics: LocalDiagnosticsState,
    onRunDiagnostic: () -> Unit,
    onRefreshDiagnostics: () -> Unit,
    onNextDiagnostics: () -> Unit,
    onOpenAppSettings: () -> Unit,
    inference: InferenceState,
    onEditPrompt: (String) -> Unit,
    onGenerate: () -> Unit,
    onStopInference: () -> Unit,
) {
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
                if (destination == Destination.OVERVIEW || destination == Destination.JOBS) {
                    LocalDiagnosticPanel(
                        diagnostics, onRunDiagnostic, onRefreshDiagnostics, onNextDiagnostics,
                        onOpenAppSettings,
                        showHistory = destination == Destination.JOBS,
                    )
                }
                StatusPanel(state, onRefresh)
                when (destination) {
                    Destination.OVERVIEW -> Overview(state)
                    Destination.SESSION -> LocalInferencePanel(
                        inference, onEditPrompt, onGenerate, onStopInference,
                    )
                    Destination.JOBS -> Text(
                        "Ezek a telefonon végzett helyi ellenőrzések. " +
                            "Hálózati feladat még nem indítható. A helyi AI az AI lapon érhető el.",
                    )
                    Destination.MODELS -> UnavailableFeature(
                        "Modellek és frissítések", "Nincs bekötött modellnyilvántartás. " +
                            "Az AI lap a beépített Qwen3-0.6B modellt futtatja. Közös tanulás, " +
                            "modellfrissítés és visszaállítás jelenleg nem indítható.", "Modell frissítése",
                    )
                    Destination.RESOURCES -> Resources(state)
                }
            }
        }
    }
}

@Composable
private fun LocalInferencePanel(
    state: InferenceState,
    onEditPrompt: (String) -> Unit,
    onGenerate: () -> Unit,
    onStop: () -> Unit,
) {
    InfoCard("Kérdezz a helyi AI-tól") {
        Text("Qwen3-0.6B · offline CPU bemutató. A kérdés és válasz csak az alkalmazás " +
            "memóriájában marad; a folyamat leállításakor elvész. Az első indítás a " +
            "beépített modell előkészítése miatt tovább tarthat.")
        OutlinedTextField(
            value = state.prompt,
            onValueChange = onEditPrompt,
            enabled = !state.busy,
            label = { Text("Kérdés") },
            supportingText = { Text("${state.prompt.toByteArray(Charsets.UTF_8).size} / 1024 UTF-8 bájt") },
            minLines = 3,
            maxLines = 6,
            modifier = Modifier.fillMaxWidth(),
        )
        Button(onClick = onGenerate, enabled = !state.busy && state.prompt.isNotBlank(),
            modifier = Modifier.fillMaxWidth().heightIn(min = 48.dp)) {
            Text("Válasz kérése")
        }
        if (state.busy) {
            CircularProgressIndicator()
            Text(when {
                state.stopping -> "Leállítás folyamatban… A modell betöltésének befejezése eltarthat."
                state.phase == InferencePhase.PREPARING -> "Modell előkészítése és ellenőrzése: ${state.progress}%"
                else -> "Válasz készül a telefonon…"
            })
            Button(onClick = onStop, enabled = !state.stopping,
                modifier = Modifier.heightIn(min = 48.dp)) { Text("Leállítás") }
        }
        when (state.phase) {
            InferencePhase.COMPLETED -> Text("A válasz elkészült.")
            InferencePhase.CANCELLED -> Text("Megszakítva. Újra kérdezhetsz.")
            else -> Unit
        }
        state.error?.let { Text(it, color = MaterialTheme.colorScheme.error) }
        if (state.answer.isNotEmpty()) {
            Text("Válasz", style = MaterialTheme.typography.titleMedium,
                modifier = Modifier.semantics { heading() })
            Text(state.answer)
        }
        Text("A generálás leáll, ha az alkalmazás háttérbe kerül. A képernyő elforgatása " +
            "nem indít új feladatot. A modell tévedhet; a válasz hossza korlátozott.")
    }
}

@Composable
private fun LocalDiagnosticPanel(
    state: LocalDiagnosticsState,
    onRun: () -> Unit,
    onRefresh: () -> Unit,
    onNext: () -> Unit,
    onOpenAppSettings: () -> Unit,
    showHistory: Boolean,
) {
    InfoCard("Próbáld ki a helyi működést") {
        Text("Ellenőrizd, hogy a helyi mag válaszol-e, és az eredmény menthető-e a telefonon.")
        Button(
            onClick = onRun,
            enabled = state.available && !state.loading && !state.running && !state.requiresRestart,
            modifier = Modifier.fillMaxWidth().heightIn(min = 48.dp),
        ) {
            Text(if (state.running) "Ellenőrzés folyamatban…" else "Helyi ellenőrzés indítása")
        }
        if (state.loading || state.running) {
            CircularProgressIndicator()
            Text(if (state.running) "Az eredmény mentése folyamatban…" else "Előzmények betöltése…")
        }
        state.lastResult?.let { result ->
            Text(diagnosticLabel(result.state), style = MaterialTheme.typography.titleMedium)
            Text("Az eredményt a telefonon tároljuk. Az előzmények újranyitás után is elérhetők.")
        }
        state.error?.let { Text(it, color = MaterialTheme.colorScheme.error) }
        if (state.requiresRestart) {
            TextButton(onClick = onOpenAppSettings) { Text("Alkalmazás beállításai") }
        }
        TextButton(onClick = onRefresh, enabled = !state.loading && !state.running) {
            Text("Előzmények frissítése")
        }
        Text("Ez helyi működésellenőrzés; nem futtat AI-modellt.")
    }
    if (showHistory) {
        InfoCard("Mentett előzmények") {
            if (state.records.isEmpty() && !state.loading) {
                Text(if (state.available) "Még nincs mentett ellenőrzés. Indítsd el az elsőt." else "Az előzmények jelenleg nem érhetők el.")
            }
            state.records.forEach { item ->
                val millis = item.requestId.substringBefore('-').toLongOrNull()
                Text(
                    (millis?.let { DateFormat.getDateTimeInstance(DateFormat.SHORT, DateFormat.MEDIUM).format(Date(it)) }
                        ?: "Helyi ellenőrzés") + " · " + diagnosticLabel(item.state),
                )
            }
            if (state.nextOffset != null) {
                TextButton(onClick = onNext, enabled = !state.loading && !state.running) {
                    Text("Következő oldal")
                }
            }
            if (state.offset > 0u) {
                TextButton(onClick = onRefresh, enabled = !state.loading && !state.running) {
                    Text("Vissza az első oldalra")
                }
            }
        }
    }
}

private fun diagnosticLabel(state: String): String = when (state) {
    "queued" -> "Indításra vár"
    "running" -> "Folyamatban"
    "succeeded" -> "Az ellenőrzés sikeres"
    "failed" -> "Az ellenőrzés hibát jelzett"
    "cancelled" -> "Megszakítva"
    "interrupted" -> "Az alkalmazás leállása miatt félbeszakadt"
    else -> "Ismeretlen állapot; frissítsd az előzményeket"
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
        Text("A helyi kérdés és válasz az AI lapon próbálható ki. Hálózati és " +
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
