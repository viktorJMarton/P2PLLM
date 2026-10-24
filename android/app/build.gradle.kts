import java.security.MessageDigest

plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
    id("org.jetbrains.kotlin.plugin.compose")
}

android {
    namespace = "org.p2pai.app"
    compileSdk = 35

    defaultConfig {
        applicationId = "org.p2pai.app"
        minSdk = 26
        targetSdk = 35
        versionCode = 3
        versionName = "0.3.0"
        testInstrumentationRunner = "org.p2pai.app.LocalInferenceSmokeInstrumentation"
        ndk {
            abiFilters += "arm64-v8a"
        }
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }
    kotlinOptions {
        jvmTarget = "17"
    }
    buildFeatures {
        compose = true
    }
    sourceSets.getByName("main").assets.srcDir(layout.buildDirectory.dir("generated/localModelAssets"))
    androidResources {
        noCompress += listOf("pte", "json")
    }
}

dependencies {
    implementation(platform("androidx.compose:compose-bom:2024.12.01"))
    implementation("androidx.activity:activity-compose:1.9.3")
    implementation("androidx.compose.material3:material3")
    implementation("net.java.dev.jna:jna:5.13.0@aar")
}

dependencyLocking {
    lockAllConfigurations()
}

// Packaging must fail closed if preparation was skipped; pure Kotlin compilation
// remains usable without staging the large public model payload.
val verifyLocalInferencePayload by tasks.registering {
    group = "verification"
    description = "Verify the pinned offline model and arm64 inference libraries before packaging."
    doLast {
        val assetDirectory = layout.buildDirectory.dir("generated/localModelAssets/local-model").get().asFile
        fun verifyAsset(name: String, expectedSize: Long, expectedHash: String) {
            val asset = assetDirectory.resolve(name)
            check(asset.isFile && asset.length() == expectedSize) {
                "Missing or invalid bundled $name; run tools/prepare_android_inference.py before packaging."
            }
            val digest = MessageDigest.getInstance("SHA-256")
            asset.inputStream().buffered().use { input ->
                val buffer = ByteArray(1024 * 1024)
                var count = input.read(buffer)
                while (count >= 0) {
                    digest.update(buffer, 0, count)
                    count = input.read(buffer)
                }
            }
            val actualHash = digest.digest().joinToString("") { "%02x".format(it) }
            check(actualHash == expectedHash) { "Bundled $name hash mismatch; repeat verified preparation." }
        }
        verifyAsset("model.pte", 468633472L,
            "07786b553d9661d36431426d06c268f385d453314f6722ca79f66c7e79653b48")
        verifyAsset("tokenizer.json", 11422654L,
            "aeb13307a71acd8fe81861d94ad54ab689df773318809eed3cbe794b4492dae4")
        verifyAsset("LICENSE", 11343L,
            "832dd9e00a68dd83b3c3fb9f5588dad7dcf337a0db50f7d9483f310cd292e92e")
        listOf("runtime-notices/inventory.json", "runtime-notices/executorch/LICENSE").forEach { name ->
            val notice = assetDirectory.resolve(name)
            check(notice.isFile && notice.length() > 0) { "Missing bundled runtime notice $name." }
        }
        listOf("libp2p_inference.so", "libc++_shared.so").forEach { name ->
            val library = project.file("src/main/jniLibs/arm64-v8a/$name")
            check(library.isFile && library.length() >= 64) { "Missing bundled arm64 library $name." }
            val header = library.inputStream().use { it.readNBytes(64) }
            fun byteAt(index: Int) = header[index].toInt() and 0xff
            check(header.size == 64 && byteAt(0) == 0x7f && byteAt(1) == 0x45 &&
                byteAt(2) == 0x4c && byteAt(3) == 0x46 && byteAt(4) == 2 &&
                byteAt(5) == 1 && byteAt(6) == 1 && byteAt(16) == 3 &&
                byteAt(17) == 0 && byteAt(18) == 183 && byteAt(19) == 0 &&
                byteAt(20) == 1 && byteAt(21) == 0 && byteAt(22) == 0 && byteAt(23) == 0) {
                "Bundled $name must be an ELF64 little-endian AArch64 shared library."
            }
        }
    }
}

tasks.matching {
    it.name in setOf("packageDebug", "packageRelease", "assembleDebug", "assembleRelease", "bundleDebug", "bundleRelease")
}.configureEach {
    dependsOn(verifyLocalInferencePayload)
}
