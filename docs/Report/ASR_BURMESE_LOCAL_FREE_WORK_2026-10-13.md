# Burmese ASR — Local-Free Work Log

**Date:** 2026-10-13  
**Branch:** `fix/burmese-asr-script-guard`  
**Pull request:** [#73](https://github.com/dragonknighttw-cmd/Narrativ-Forge/pull/73)  
**Latest exact-head CI verification at time of this update:** `50ea2d811084344ec4ae5640af301ced90e0a598`

## Completed without local execution

- Reviewed the production processing path in `web-platform/backend/app/services/real_processing.py`.
- Added a defensive check before transcript assets are persisted. If neither the transcript's main text nor its segments contain any Myanmar-script characters, processing fails with `ASR_LANGUAGE_MISMATCH` rather than treating likely Chinese/other-script ASR output as a Burmese transcript.
- Added unit tests for Chinese-only output, Myanmar text in segments, and empty transcript payloads.
- The first version of the guard incorrectly rejected the generated tone/silence media used by Real Worker Evidence because Whisper returned an empty transcript. Updated the guard to reject only **non-empty** output without Myanmar-script characters, while allowing empty output for silence/tone fixtures.
- Verified code head `4c8e7835f2f17a270ebb1ebbc07368a0ce9dc284`: all eight workflows passed, including the Real Worker Evidence `real-worker-e2e` job and real-media smoke step.
- Verified guide/code head `5323c19ded5f7049babb205e292e90ac6a59bfd5`: all eight workflows passed.
- **Latest exact-head verification:** all eight GitHub Actions workflows passed on `50ea2d811084344ec4ae5640af301ced90e0a598`: CI, Repository Gate, Real Worker Evidence, Local Runtime Evidence, Windows Local Runtime Evidence, Windows Portable Package Evidence, CodeQL, and Security. This is CI/fixture evidence, not validation of actual Burmese speech accuracy.

## Additional non-local review

- Added regression tests for Myanmar script in the main transcript text, whitespace-only transcript payloads, and the rule that a `language: "my"` metadata label alone must not count as recognized Myanmar text.
- Added a Worker response pass-through for provider `language` and `language_probability` metadata when present at the top level or under `transcription_info`, with a mocked contract test. The backend persists the response JSON already, so these fields can reach the transcript artifact when the provider supplies them. This does not force Burmese or change the model/inference cost.
- Static review found that the primary remote-first Cloudflare Worker calls `@cf/openai/whisper` with only the audio payload; it does not pass a language hint or return language-detection metadata to the backend before this change. This is a plausible investigation lead, not proof of root cause.
- Added this finding and official Cloudflare model-contract links to the acceptance guide. The `whisper-large-v3-turbo` model documents a `language` input, but switching model or changing remote inference behavior can affect cost and output contract. No model switch, live inference, quota use, or deployment was performed.

## Important limitations

- The script check is a guardrail, not a speech-recognition fix. It does not validate the accuracy or meaning of Burmese text.
- It can still accept incorrect text that happens to contain one or more Myanmar-script characters.
- Local tests and real Burmese-audio inference have not been run because local execution is currently unavailable.
- No Cloudflare inference was run; no quota was consumed by this work.
- No production deployment was triggered. Render auto-deploy remains disabled.
- PR #73 remains draft and must not be merged until real Burmese-audio acceptance checks are complete.

## Work still pending

1. When local execution is available, run the backend test suite and the focused Whisper tests.
2. Test the same Burmese audio with auto-detection and forced Burmese language; compare model outputs and saved language metadata.
3. Confirm transcript retrieval, subtitle timing, output playback, and unchanged source media.
4. Reassess whether a stronger language/quality gate is appropriate after observing real samples. Do not add a heuristic that silently rewrites ASR output.
5. Obtain explicit approval before any quota-consuming remote inference or production deployment.
6. Keep PR #73 in draft and do not merge until real Burmese-audio acceptance checks are complete.

## Independent isolated-box regression verification — 2026-10-13

- Checked out exact PR #73 head `8dbfe74473fa6e3b3555a1d752dae424ef9787bf` in an isolated repository workspace. No user Windows machine, original media, secrets, provider credentials, or cloud inference were accessed.
- Backend focused tests: `cd web-platform/backend && PYTHONPATH=. pytest -q tests/test_whisper_fallback.py` — **9 passed**.
- Backend unit/security selection: `cd web-platform/backend && PYTHONPATH=. pytest -m 'unit or security' -q` — **303 passed, 3 skipped, 84 deselected**; three existing deprecation warnings were emitted.
- Cloudflare Whisper Worker contract tests: `cd web-platform/cloudflare/whisper-worker && node --experimental-strip-types --test test/worker.test.mjs` — **5 passed** (Node 25.9.0 in the isolated box; repository CI pins Node 22).
- `git status` was clean before recording these results. These results establish regression behavior for the exact checked-out source only; they do **not** establish Burmese speech accuracy, Windows user-machine acceptance, live provider behavior, or production readiness.
