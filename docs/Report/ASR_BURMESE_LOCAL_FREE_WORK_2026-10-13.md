# Burmese ASR — Local-Free Work Log

**Date:** 2026-10-13  
**Branch:** `fix/burmese-asr-script-guard`  
**Pull request:** [#73](https://github.com/dragonknighttw-cmd/Narrativ-Forge/pull/73)  
**Latest verified code head before this documentation refresh:** `4c8e7835f2f17a270ebb1ebbc07368a0ce9dc284`

## Completed without local execution

- Reviewed the production processing path in `web-platform/backend/app/services/real_processing.py`.
- Added a defensive check before transcript assets are persisted. If neither the transcript's main text nor its segments contain any Myanmar-script characters, processing fails with `ASR_LANGUAGE_MISMATCH` rather than treating likely Chinese/other-script ASR output as a Burmese transcript.
- Added unit tests for Chinese-only output, Myanmar text in segments, and empty transcript payloads.
- The first version of the guard incorrectly rejected the generated tone/silence media used by Real Worker Evidence because Whisper returned an empty transcript. Updated the guard to reject only **non-empty** output without Myanmar-script characters, while allowing empty output for silence/tone fixtures.
- Verified the exact code head `4c8e7835f2f17a270ebb1ebbc07368a0ce9dc284`: GitHub Actions runs for CI, Repository Gate, Real Worker Evidence, Local Runtime Evidence, Windows Local Runtime Evidence, CodeQL, Security, and Windows Portable Package Evidence all completed successfully. The Real Worker Evidence `real-worker-e2e` job and its real-media smoke step passed.

## Important limitations

- The script check is a guardrail, not a speech-recognition fix. It does not validate the accuracy or meaning of Burmese text.
- It can still accept incorrect text that happens to contain one or more Myanmar-script characters.
- Local tests and real Burmese-audio inference have not been run because local execution is currently unavailable.
- No Cloudflare inference was run; no quota was consumed by this work.
- No production deployment was triggered. Render auto-deploy remains disabled.

## Work still pending

1. After this documentation-only commit, confirm GitHub Actions completes successfully on the new PR head too.
2. When local execution is available, run the backend test suite and the focused Whisper tests.
3. Test the same Burmese audio with auto-detection and forced Burmese language; compare model outputs and saved language metadata.
4. Confirm transcript retrieval, subtitle timing, output playback, and unchanged source media.
5. Reassess whether a stronger language/quality gate is appropriate after observing real samples. Do not add a heuristic that silently rewrites ASR output.
6. Obtain explicit approval before any quota-consuming remote inference or production deployment.
7. Keep PR #73 in draft and do not merge until real Burmese-audio acceptance checks are complete.
