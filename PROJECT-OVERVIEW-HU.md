# Projektösszefoglaló

## Mit építünk?
Nyílt forrású, decentralizált P2P AI-ökoszisztémát, amelyben önálló node-ok közösen számolnak és tanulnak. A telefon saját modellje és tudástára is fejlődhet. A node kérhet és felajánlhat kapacitást. Nem egy központi AI-szolgáltatás kliensét készítjük.

## Rögzített döntések
- Android + PC az első környezet; később Android + Android.
- PyTorch + ExecuTorch a modellfejlesztés és mobilos végrehajtás iránya.
- Qwen3-0.6B gyors referencia; Qwen3-1.7B érdemi mobiljelölt, külön export- és hardverellenőrzéssel. Nem állítjuk, hogy ezek a legújabb Qwen-modellek.
- CPU mellett GPU/NPU/DSP kihasználása, ahol a művelet és driver támogatja. Az ISP nem általános LLM-processzor.
- Köztes modellállapot és tanulási frissítés cserélhető; a nyers tartalom alapértelmezésben nem.
- A privát közös számítás és tanulás az MVP része. Ha nincs igazoltan megfelelő backend, hálózati végrehajtás nem indul.
- Nyílt csoportok először, későbbi zárt csoportokhoz bővítési pont.
- Háttérmód célkövetelmény; első labor előtérben is futhat. Töltő/Wi-Fi alapérték egyelőre javaslat.
- Saját protokollüzenetek, bevált kriptográfia és transzport.
- Clean Code, DRY és helyi tranzakciós ACID kötelező. Nincs globális ACID-ígéret.

## Mi készült el ténylegesen?
Ez a specifikációs csomag: agentutasítások, döntések, munkatételek, sémavázlatok, PlantUML/BPMN források és csomagellenőrző. Termékkód és működő CI még nincs. A dokumentumokban szereplő célparancsok közül csak a csomagvalidátor futtatható most.

## Fő nyitott akadály
Nyílt, ismeretlen telefonok közötti privát LLM-művelet hatékonysága és adatvédelmi feltételei. Dokumentáció vagy Reddit-vélemény önmagában nem oldja ezt meg. Az MP-SPDZ kutatási referenciajelölt, nem kiválasztott éles mobilbackend.

## Indítás Codex CLI-ben
Nyisd meg a kicsomagolt projekt gyökerét. Kérd: „Olvasd az AGENTS.md-t, majd hajtsd végre a work/INDEX.md első végrehajtható tételét. Rögzíts minden lényeges döntést és bizonyítékot. Ne állíts nem mért eredményt.”
