# Answer-quality team review, 2026-10-24

Status: team assessment and G01 CLI reproduction completed; full pilot not run.
WORK-0002 / run quality-review-001. Coordinator: primary, Accountable delivery
coordinator. Baseline: a07cae8e7e9a65cbe7e5d5d8aa6a0f4ed12bbcb8.
Trigger: owner tried Android question entry and found answer quality unacceptable.
The owner supplied the public greeting "Hogy vagy?" and described nonsensical
repetition with a partial /No fragment. No personal chat was harvested.

## Actual participants and evidence

Android owner inference_android, runtime owner inference_native and independent
reviewer delivery_review exchanged questions and actual answers with primary.
Their separate journals contain their readings, questions and answers:
[Android](../agent-journals/inference-android.md),
[native](../agent-journals/inference-native.md),
[review](../agent-journals/delivery-review.md),
[primary](../agent-journals/primary.md).

The installed 0.3.0 app really runs the pinned Qwen3-0.6B 8da4w model offline.
Eight operational smoke checks passed, including UI/lifecycle/cancellation and
restart; repeated exact arithmetic answer checks are not eight quality tasks.
[Observed results](../WORK-0015-android-local-inference/device-observations.json).
No accepted Hungarian quality corpus, float-reference/export parity or backend
placement evidence exists. Do not equate operational acceptance with useful AI.

Android source passes the complete accepted question String to JNI and the full
returned answer to Text, with no answer substring/ellipsis/maxLines restriction.
The 1024-byte UTF-8 input rule rejects an oversized edit entirely, leaving the
previous text; this is a known UX risk, not a proven cause of the owner's issue.
Native generation uses temperature0 and at most128 new tokens. EOS and reaching
the token budget both appear as COMPLETED; the API exposes no stop reason.
Each question is single-turn: no previous messages or system-language instruction.

Model capacity, quantization/export loss, framing and output truncation are
separate hypotheses. None is established as the cause of the reported answer.
The measured /no_think arithmetic improvement is not Hungarian quality evidence.

## Agreed next bounded experiment

G01 is a mandatory separate blocking regression: the public question "Hogy vagy?"
must yield a coherent short Hungarian greeting, without pathological repetition
or exposed directive fragments. A10/12 aggregate cannot hide this failure.

Actual unchanged A72 CLI baseline was run after the meeting: recipe artifact
hashes verified, temperature0/max128/4threads/current template. In10.079s the
answer had258 UTF-8 bytes and its most repeated word trigram occurred38times.
The repetition flag was true; the directive-fragment flag was false and no EOS
marker was observed. This reproduces repetition outside the app, not necessarily
the owner's identical output. No human coherence score, token-ID parity, app
comparison or reference result is claimed. No raw answer saved. See the portable
[G01 receipt](greeting-observation.json); local script and receipt remain under
.artifacts/device/WORK-0002/greeting-001/. This does not yet distinguish model,
quantization, export or framing. Absence of an EOS marker alone does not establish
the precise stop reason or token count.

WORK-0002 retains priority. Freeze this pilot before observing answers. Compare
the same pinned revision/tokenizer and rendered template on three paths:
float reference, device CLI, and installed JNI/app. Preserve temperature0,
max128, EOS handling and /no_think for the first comparison. Check input bytes
and token IDs before attributing differences to weights/runtime. Matching hashes
do not themselves prove numerical parity. Mark unavailable paths blocked.

Public synthetic fixtures only; no personal chat copied from the device. Each
question is self-contained and deliberately short enough for the existing cap.
Public fixtures below are evaluation inputs, not captured user conversations.

| ID | Category | Fixed question | Expected requirement |
| --- | --- | --- | --- |
| HU01 | Arithmetic | Mennyi 17 + 25? Csak a számot írd le. | Exact 42 after surrounding whitespace removal |
| HU02 | Arithmetic | Három dobozban dobozonként 4 ceruza van. Mennyi összesen? Csak a számot írd le. | Exact 12 |
| HU03 | Supplied comprehension | A könyvtár hétfőn zárva, kedden 9 órakor nyit. Mikor nyit kedden? | 9 órakor; no invented schedule |
| HU04 | Supplied comprehension | Anna a piros, Béla a kék táskát viszi. Ki viszi a kék táskát? Csak a nevet írd le. | Exact Béla |
| HU05 | Extraction | Alma: 120 Ft; körte: 180 Ft. Csak a körte árát írd le. | Exact 180 Ft |
| HU06 | Structured extraction | Név: Éva, kor: 31. Add vissza JSON-ként a nev és kor kulcsokkal, más szöveg nélkül. | JSON object exactly nev=Éva and numeric kor=31 |
| HU07 | Translation | Fordítsd magyarra: The train leaves at six. | A vonat hatkor indul; equivalent Hungarian wording allowed |
| HU08 | Translation | Fordítsd angolra: A kulcs az asztalon van. | The key is on the table; equivalent wording allowed |
| HU09 | Instruction | Írd le ezt a két szót fordított sorrendben, vesszővel: alma, körte. Más szöveget ne írj. | Exact körte, alma |
| HU10 | Instruction | Adj pontosan két magyar gyümölcsnevet, soronként egyet, magyarázat nélkül. | Two distinct valid Hungarian fruit names; exactly two lines |
| HU11 | Unknown | Az itt megadott adatok: a doboz piros. Hány kilogramm a doboz? Ha nem derül ki, ezt írd: Nincs elég adat. | Exact Nincs elég adat. |
| HU12 | False premise | A történet szerint Zoli kutyája fekete. Miért fehér Zoli kutyája? | Identify inconsistent premise; do not invent reason for whiteness |

Score correctness, language and instruction compliance separately, each0/1/2:
0 wrong/unusable;1 partial or material omission;2 fully satisfies that dimension.
For HU08 the required answer language is English, not Hungarian. Exact predicates
apply only where stated; other items require explicit reviewer rubric judgment,
never keyword-presence alone. Publish per-case scores and failures, not just mean.

Candidate comparison gate agreed by delivery_review: at least10/12 correctness2,
zero critical failures and zero unexplained device/app losses on deterministic
items versus reference. This is a small diagnostic pilot, not general Hungarian
or product/release acceptance. Stop reason/truncation is a separate observation,
never inferred from COMPLETED. Unknown data stays unknown. A crash, payload leak
or unexplained deterministic divergence stops promotion and requires diagnosis.

## Decisions and ownership

1. Primary owns frozen cases/rubric and evidence coordination. No retuning the
   questions, expected answers or thresholds after observing results.
2. Native owns reference/export/CLI comparison and provenance; Android owns
   byte-preserving UI/JNI comparison and future versioned stop-reason proposal.
3. If reference succeeds and device fails, investigate export/quantization/runtime
   before changing model. If CLI succeeds and app fails, investigate app boundary.
4. If reference also fails, evaluate model fit. Qwen3-1.7B remains an already
   approved WORK-0002 evaluation candidate: pin revision/license/export, measure
   A72 memory/load/TTFT/throughput before any shipping decision. No silent upgrade.
5. Change one variable per follow-up comparison. Conversation memory is a separate
   feature; current quality evaluation must supply all needed context explicitly.

Not yet done: reference/app G01 comparison, this12-case experiment, a quality fix, new APK or demonstrated
quality improvement. Runtime/thermal/privacy/release gates remain open. Device
availability and reference/backend readiness must be checked before execution.
Next action is G01 reference/tokenizer/config parity and a same-weight quantized
reference if needed; then a single-variable suffix comparison, preserving other
parameters. Budget128->256 is a separate experiment only after measured budget
stopping. Do not strip fragments or repetition to disguise a generation failure.
