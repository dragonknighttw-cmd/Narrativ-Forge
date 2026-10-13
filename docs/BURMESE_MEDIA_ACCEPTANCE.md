# Burmese Media Acceptance Checklist

Status: **PENDING — technical pipeline completed, but the current Whisper transcript failed the Burmese-script check; speech acceptance is not granted.**
Scope: human-reviewed Burmese transcription, subtitle timing, rendering, and output acceptance. This checklist does not claim a live provider or production worker is verified.

Latest sample intake: a 58.7-second MP4 was supplied in chat. Container/stream inspection and conversion to 16 kHz mono PCM succeeded; a roughly 2.8-second silent tail was detected and the audio peak is near 0 dBFS, so listen for possible distortion. The sample itself is not committed to Git. The local worker completed, but its historical `tiny` Whisper transcript contains CJK ideographs and no Myanmar-script characters; its `language: my` metadata was forced by the old worker command and is not proof of recognition. Automatic detection with `tiny` identified Chinese. A `small` auto-detection run detected `my` but produced 152 text characters with no Myanmar-script characters; a forced-`my` `small` run produced only 6 non-Myanmar characters across 4 segments. Checksum-verified `large-v3-turbo` automatic CPU inference completed, detected Chinese, and produced 41 characters with zero Myanmar-script characters. All current candidates fail Burmese-script acceptance; detection results alone do not prove the spoken language. Do not accept or publish these outputs as Burmese. The current backend working tree now preserves detected language instead of forcing `my`, but this does not establish transcription quality. Privately confirm the spoken language and obtain Burmese-speaker/reference review before acceptance. See [technical preflight report](Report/BURMESE_SAMPLE_PREFLIGHT_2026-10-12.md).

## 1. What the owner needs to provide

Provide one short sample that you own or have permission to use:

- Prefer **30–90 seconds** of clear spoken Burmese; a longer sample can follow after the first pass.
- Use an audio or video file such as WAV, MP3, M4A, or MP4.
- Choose ordinary speech with a few complete sentences. Avoid private conversations, personal data, or confidential client material.
- If possible, include a plain-text reference transcript of what was said. If you do not have one, the reviewer can still assess obvious errors, but word-level accuracy cannot be scored reliably.
- Tell the reviewer whether the clip contains one speaker or multiple speakers, and identify any difficult names/technical terms if they matter.

Do not paste API keys, passwords, cookies, or provider secrets into chat or put them in the media file.

## 2. Safe first-pass procedure

1. Confirm the sample is approved for this test and decide whether it may be processed locally or sent to the configured provider. **Default to local processing** until external-provider use is explicitly approved.
2. Record the sample filename, duration, language/dialect if known, speaker count, and a checksum. Keep the original immutable.
3. Run the existing canonical media path: input asset → processing job/queue → worker → FFmpeg/Whisper → transcript/subtitle persistence → rendered output.
4. Capture the job ID, worker/provider mode, timestamps, status, error/retry information, and generated artifact locations. Redact secrets and private transcript text from logs.
5. Compare the transcript with the reference transcript if available. Review Unicode Burmese spelling, punctuation, omitted/repeated words, names, and hallucinated text.
6. Review subtitle segmentation, readability, timing, overlap, clipping, and synchronization against the spoken audio.
7. Watch/listen to the rendered output from beginning to end. Confirm the original is preserved and the generated output and subtitle assets can be retrieved.
8. Record pass/fail with evidence. Do not mark production acceptance VERIFIED based on a single local sample or synthetic CI fixture.

## 3. Acceptance record

Complete one record per sample:

| Field | Result |
|---|---|
| Sample ID (avoid personal filename) | PENDING |
| Owner permission confirmed | PENDING |
| Processing mode (local/provider) | PENDING |
| Job ID and commit/version | PENDING |
| Input asset persisted | PENDING |
| Processing reached terminal success | PENDING |
| Transcript persisted and reviewed | PENDING |
| Unicode Burmese / NFC checked | PENDING |
| Subtitle timing and segmentation reviewed | PENDING |
| Rendered output plays correctly | PENDING |
| Original preserved | PENDING |
| Errors/retries investigated | PENDING |
| Human reviewer decision and notes | PENDING |

## 4. Pass/fail rules

**Pass for this sample** only when the processing job completes, expected artifacts persist and are retrievable, Burmese transcript quality is manually reviewed against available ground truth, subtitles are synchronized/readable, the rendered output plays, and the original remains unchanged.

**Fail / investigate** if the job silently reports success with missing artifacts, the transcript contains substantial omissions or invented speech, subtitles are badly timed/unreadable, output cannot play, or the original is changed. Preserve redacted logs and job identifiers for diagnosis.

A single passing sample is a limited acceptance result, not a broad quality guarantee. Test more than one speaker/accent and noisy/real-world audio before making wider claims.

## 5. Boundaries and remaining gates

- Existing synthetic tone fixtures contain no speech; an empty transcript from those fixtures is expected and is not Burmese speech-quality evidence.
- Deterministic Unicode transcript fixtures prove normalization/export behavior only, not speech recognition accuracy.
- Do not run quota-consuming authenticated inference, provision paid resources, modify production data, or perform destructive recovery without explicit owner approval.
- Keep production provider flags disabled unless the owner separately approves production configuration changes.
- Production release still requires persistent worker/recovery evidence, live storage/provider acceptance, backup/restore, auth/tenant E2E, operational monitoring, accessibility, legal/privacy review, and external security acceptance.
