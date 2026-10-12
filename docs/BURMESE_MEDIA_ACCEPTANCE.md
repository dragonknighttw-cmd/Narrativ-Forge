# Burmese Media Acceptance Checklist

Status: **PENDING — owner-approved speech sample required.**
Scope: human-reviewed Burmese transcription, subtitle timing, rendering, and output acceptance. This checklist does not claim a live provider or production worker is verified.

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
