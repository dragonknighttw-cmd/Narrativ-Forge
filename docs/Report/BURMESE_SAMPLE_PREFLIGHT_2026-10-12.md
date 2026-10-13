# Burmese Sample — Technical Preflight Report

**Date:** 2026-10-12  
**Status:** TECHNICAL PREFLIGHT PASSED; CURRENT BURMESE ASR OUTPUT FAILED; HUMAN ACCEPTANCE PENDING
**Repository HEAD when updated:** `95aa9163cc40383a8c44c3a5f445e4de899116e4` (`main`, dirty worktree; local worker run SHA not recorded)
**Scope:** Metadata and local audio-conversion checks on the chat-uploaded sample only. The media itself and any transcript are not committed to this repository.

## Input metadata

| Check | Result |
|---|---|
| Container | MP4 |
| File size | 7,113,672 bytes |
| Duration | 58.733 seconds (video); 58.722 seconds (audio) |
| Video | H.264/AVC, 576 × 1024, 30 fps, portrait 9:16 |
| Audio | AAC-LC, 44.1 kHz, stereo |
| Embedded subtitle stream | None detected |
| Audio conversion | Successfully converted to 16 kHz mono PCM WAV in the isolated analysis runtime |
| Mean audio level | -17.3 dBFS |
| Peak audio level | Approximately 0.0 dBFS; listen for audible clipping/distortion during review |
| Detected silence | Approximately 2.815 seconds at the end (threshold -45 dB, minimum duration 0.5 seconds) |

## What this establishes

- The MP4 container and both expected audio/video streams are readable by FFprobe/FFmpeg.
- The audio can be extracted and converted into a common 16 kHz mono speech-processing format.
- The clip duration is within the project's 30–90 second initial sample target.
- A terminal silent interval was detected and should not be mistaken for missing audio during transcription review.

## What the initial preflight did not establish

- The initial metadata preflight did not have a speech-to-text model, so no transcript was generated at that stage.
- No word error rate can be measured without a reference transcript.
- Burmese language recognition, names/spelling, Unicode normalization, subtitle timing, rendered output, persistence through Narrativ Forge's actual worker, and human listening review remain pending.
- This report does not prove cloud-provider behavior, production worker availability, or production readiness.

## Safe next run on the Windows local runtime

1. Keep the original sample unchanged and copy it to a dedicated test-input location outside the repository.
2. Run the existing local Windows media-worker workflow with the already configured local Whisper model and local storage. Do not switch to authenticated cloud inference or provision paid resources for this test.
3. Record the exact source commit, local runtime version, job ID, terminal status, retry/error summary, and paths for the generated transcript/subtitle/output artifacts. Keep secrets and transcript text out of logs.
4. Review the transcript against the audio manually; because no reference transcript was supplied, record this as qualitative review rather than a measured word-error rate.
5. Review Burmese Unicode/NFC, subtitle cue timing/overlap/readability, output playback, and original-file preservation.
6. If the worker reports success with an empty transcript, first listen to confirm the clip actually contains speech; an empty transcript from a no-speech fixture is not speech-quality evidence.
7. Update the acceptance checklist only with evidence actually observed. Keep speech acceptance and production release status pending until their separate gates pass.

## Privacy and cost boundary

The sample media is not stored in Git. No authenticated cloud inference, paid resource provisioning, production-data mutation, or destructive recovery was performed for this preflight.

## Local worker verification update (2026-10-12)

The supplied MP4 was preserved unchanged and then processed locally under the repository's canonical Celery worker with the loopback-only Memurai instance on port 6380, `WHISPER_REMOTE_ENABLED=false`, `WHISPER_MODEL=tiny`, and `SUBTITLE_NORMALIZATION_MODE=unicode_nfc_only`.

Observed evidence:
- Worker result: `SAMPLE_WORKER_OK`
- Job status: `completed`, `progress=100`
- Output artifact exists: `True`
- Transcript artifact exists: `True`
- Original file SHA-256 preserved: `C6862BAA65F9876F9B9422FCC8FFBE7A5D3EA99A90760E6628983217CAEE1518`
- Processed output path recorded on the local storage root, with transcript stored under the same episode asset tree

What this proves:
- The local Windows runtime can execute the canonical processing task end-to-end on the supplied sample without modifying the original source file.
- The subprocess output path and transcript generation work in the repository's local storage profile.

What it does not prove:
- Burmese speech recognition quality, human approval, or production readiness. This remains a technical local-scope confirmation only.

## Burmese ASR quality follow-up (2026-10-12)

The persisted transcript from the local Whisper `tiny` run is **not acceptable as Burmese output**:

- Its JSON metadata says `language: my`, but the historical local worker command explicitly invoked Whisper with `--language my`; that value was not independent language detection.
- The transcript text contains 252 CJK ideographs and zero Myanmar-script characters.
- A separate `tiny` run with automatic language detection identified the sample as Chinese.
- A later local `small`-model automatic-detection run printed `Detected language: Myanmar`, but it did not produce a completed, reviewable transcript artifact during this check. Language detection alone is not evidence of transcription quality.
- A separate local `small` run forced to `my` did produce a private candidate outside the repository, but it contained only 6 text characters across 4 segments and zero Myanmar-script characters. This is an effectively empty/unusable result, not an accepted transcript.
- A direct local `small` run using automatic detection completed with `language: my` and 5 segments/152 text characters, but the text contained zero Myanmar-script characters. This candidate is also unusable as Burmese. Candidate data remains outside Git and its text is intentionally omitted.
- The first `large-v3-turbo` download was interrupted and Whisper rejected the partial file. The transfer was resumed from the official model URL; the completed 1,617,941,637-byte model then passed the expected SHA-256 check (`aff26ae408abcba5fbf8813c21e62b0941638c5f6eebfb145be0c9839262a19a`). Local CPU inference completed on the sample and detected `zh` (Chinese): 3 segments, 41 non-whitespace characters, 0 Myanmar-script characters, and 24 CJK ideographs. NFC check passed. Candidate JSON remains outside the repository; its transcript text is intentionally omitted. This model output also fails Burmese-script acceptance and does not prove the sample's actual spoken language.

## Worker language metadata correction

The current uncommitted backend change removes the hard-coded `--language my` option from local Whisper fallback and stops overriding provider language metadata with `my`. This allows Whisper/provider output to report its detected language instead of falsely labeling output as Burmese. It does not improve the model itself or validate transcript accuracy. Focused Whisper fallback tests passed (see [test results](01_TEST_RESULTS.md)).

Therefore the completed worker job and existing transcript artifact prove pipeline execution only, not Burmese speech recognition. Do not approve or publish these transcripts as Burmese subtitles. The mismatch may be caused by an incorrect/non-Burmese source sample or by recognition failure; this cannot be resolved from language metadata or a language-detector result alone. Confirm that the spoken audio is Burmese and review a usable completed candidate against an owner-provided reference or by a Burmese-speaking reviewer before accepting it. Burmese speech-quality acceptance remains **PENDING**.
