# Folytatás számítógépen

Ez a repó forrásokat és zárolt Rust-függőségeket tartalmaz. Modell-súlyokat,
SDK-t, titkokat és a Drive-átadási ZIP-et nem tartalmazza.

## Klónozás után

1. Telepítsd a Git, Python 3.11+, rustup és just eszközöket.
2. A projekt gyökerében a `rust-toolchain.toml` szerinti Rust 1.88.0
   toolchaint használd. Futtasd: `rustup toolchain install 1.88.0
   --profile minimal --component rustfmt --component clippy`.
3. Futtasd: `just check`, `just test`, `just build-desktop`, majd
   `./target/debug/p2p-node status`.
4. A `config/node.example.toml` példát másold helyi konfigurációként,
   de privát hálózati műveletet ne engedélyezz: nincs jóváhagyott backend.

## Android

A Kotlin/UniFFI projekt az `android/` mappában van. Az Android buildhez
asztali Linux/macOS/Windows gépen JDK, Android SDK 35, NDK és az Android
Gradle wrapper szükséges. Az első APK-buildet x86_64 Linuxon vagy más,
az Android SDK által támogatott asztali gépen végezd: az itt vizsgált
Linux 35.0.0 build tools `aapt2` állománya x86-64, a jelenlegi proot
pedig aarch64. Az Android arm64 Rust cél külön telepítendő
(`rustup target add aarch64-linux-android`), a cargo-ndk rögzített
verziója `cargo install cargo-ndk --version 3.5.4 --locked`.
A pontos parancs és ellenőrizetlen pontok:
`android/README.md` és `tools/build-android.sh`. Android-buildet vagy
eszközös futtatást a proot környezetben nem igazoltunk.

## Munkaállapot

A kiinduló specifikáció történeti állapotát az első Git-commit tartja
meg. A `MANIFEST.json` az aktuális forrásfájlokat ellenőrzi; szándékos
módosítás után `python3 tools/update_manifest.py`, majd
`python3 tools/validate_package.py` futtatandó. A munkanapló és a
következő lépés a `work/WORK-0001-project-bootstrap/` alatt van.
Git remote nincs beállítva; a későbbi push célját a tulajdonos adja meg.
