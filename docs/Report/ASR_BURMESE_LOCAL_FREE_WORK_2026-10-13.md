# Burmese ASR — Local-Free Work Log

**Date:** 2026-10-13  
**Branch:** `fix/burmese-asr-script-guard`  
**Pull request:** [#73](https://github.com/dragonknighttw-cmd/Narrativ-Forge/pull/73)

## Completed without local execution

- Reviewed the production processing path in `web-platform/backend/app/services/real_processing.py`.
- Added a defensive check before transcript assets are persisted. If neither the transcript's main text nor its segments contain any Myanmar-script characters, processing now fails with `ASR_LANGUAGE_MISMATCH` rather than treating likely Chinese/other-script output as a Burmese transcript.
- Added unit tests for Chinese-only output, Myanmar text in segments, and empty transcript payloads.
- Opened draft PR #73. CI workflows have started but were queued at the time of this note.

## Important limitations

- The script check is a guardrail, not a speech-recognition fix. It does not validate the accuracy or meaning of Burmese text.
- It can still accept incorrect text that happens to contain one or more Myanmar-script characters.
- Local tests and real Burmese-audio inference have not been run because local execution is currently unavailable.
- No Cloudflare inference was run; no quota was consumed by this work.
- No production deployment was triggered. Render auto-deploy remains disabled.

## Work still pending

1. Review the CI results for the exact latest PR head and fix any failures.
2. When local execution is available, run the backend test suite and the focused Whisper tests.
3. Test the same Burmese audio with auto-detection and forced Burmese language; compare model outputs and saved language metadata.
4. Confirm transcript retrieval, subtitle timing, output playback, and unchanged source media.
5. Reassess whether a stronger language/quality gate is appropriate after observing real samples. Do not add a heuristic that silently rewrites ASR output.
6. Obtain explicit approval before any quota-consuming remote inference or production deployment.
7. Keep PR #73 in draft and do not merge until CI and the real-audio acceptance checks are complete.
