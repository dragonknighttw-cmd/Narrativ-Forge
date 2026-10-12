# Burmese Sample — Technical Preflight Report

**Date:** 2026-10-12  
**Status:** TECHNICAL PREFLIGHT PASSED; SPEECH ACCEPTANCE PENDING  
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

## What this does not establish

- No speech-to-text model was available in this analysis runtime, so no transcript was generated or reviewed here.
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
