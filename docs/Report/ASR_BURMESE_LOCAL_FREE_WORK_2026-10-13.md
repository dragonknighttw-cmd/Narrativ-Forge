# Burmese ASR — Local-Free Work Log

**Date:** 2026-10-13  
**Branch:** `fix/burmese-asr-script-guard`  
**Pull request:** [#73](https://github.com/dragonknighttw-cmd/Narrativ-Forge/pull/73)  
**Latest code/CI-verified head before this documentation-only refresh:** `5323c19ded5f7049babb205e292e90ac6a59bfd5`

## Completed without local execution

- Reviewed the production processing path in `web-platform/backend/app/services/real_processing.py`.
- Added a defensive check before transcript assets are persisted. If neither the transcript's main text nor its segments contain any Myanmar-script characters, processing fails with `ASR_LANGUAGE_MISMATCH` rather than treating likely Chinese/other-script ASR output as a Burmese transcript.
- Added unit tests for Chinese-only output, Myanmar text in segments, and empty transcript payloads.
- The first version of the guard incorrectly rejected the generated tone/silence media used by Real Worker Evidence because Whisper returned an empty transcript. Updated the guard to reject only **non-empty** output without Myanmar-script characters, while allowing empty output for silence/tone fixtures.
- Verified the exact code head `4c8e7835f2f17a270ebb1ebbc07368a0ce9dc284`: GitHub Actions runs for CI, Repository Gate, Real Worker Evidence, Local Runtime Evidence, Windows Local Runtime Evidence, CodeQL, Security, and Windows Portable Package Evidence all completed successfully. The Real Worker Evidence `real-worker-e2e` job and its real-media smoke step passed.
- After adding the acceptance guide, rechecked the exact PR head `5323c19ded5f7049babb205e292e90ac6a59bfd5`: all eight workflows (CI, Repository Gate, Real Worker Evidence, Local Runtime Evidence, Windows Local Runtime Evidence, Windows Portable Package Evidence, CodeQL, Security) completed successfully. This is CI/fixture evidence, not validation of real Burmese speech accuracy.


## Additional non-local review

- Added regression tests for Myanmar script in the main transcript text, whitespace-only transcript payloads, and the rule that a `language: "my"` metadata label alone must not count as recognized Myanmar text.
- Static review found that the primary remote-first Cloudflare Worker calls `@cf/openai/whisper` with only the audio payload; it does not pass a language hint or return language-detection metadata to the backend. This is a plausible investigation lead, not proof of root cause.
- Added this finding and official Cloudflare model-contract links to the acceptance guide. The `whisper-large-v3-turbo` model documents a `language` input, but switching model or changing remote inference behavior can affect cost and output contract. No model switch, live inference, quota use, or deployment was performed.
- The latest code/test commit is `4e571b03e2ded816d2326cb12c8ba154970c07a3`; documentation updates followed. Workflow results for the newest PR head still need confirmation.

## Important limitations

- The script check is a guardrail, not a speech-recognition fix. It does not validate the accuracy or meaning of Burmese text.
- It can still accept incorrect text that happens to contain one or more Myanmar-script characters.
- Local tests and real Burmese-audio inference have not been run because local execution is currently unavailable.
- No Cloudflare inference was run; no quota was consumed by this work.
- No production deployment was triggered. Render auto-deploy remains disabled.

## Work still pending

1. When local execution is available, run the backend test suite and the focused Whisper tests.
2. Test the same Burmese audio with auto-detection and forced Burmese language; compare model outputs and saved language metadata.
3. Confirm transcript retrieval, subtitle timing, output playback, and unchanged source media.
4. Reassess whether a stronger language/quality gate is appropriate after observing real samples. Do not add a heuristic that silently rewrites ASR output.
5. Obtain explicit approval before any quota-consuming remote inference or production deployment.
6. Keep PR #73 in draft and do not merge until real Burmese-audio acceptance checks are complete.
