# Local Burmese Whisper ASR — Exact Execution & Acceptance Guide

**Purpose:** Diagnose and verify the report that Burmese speech about ChatGPT models is sometimes transcribed as Chinese characters.  
**Related PR:** [#73 — fix: reject ASR transcripts without Myanmar script](https://github.com/dragonknighttw-cmd/Narrativ-Forge/pull/73)  
**Code under test:** `web-platform/backend/app/services/real_processing.py`  
**Focused tests:** `web-platform/backend/tests/test_whisper_fallback.py`  
**Status:** Prepared for local execution. This guide has not itself been executed on the user's machine.

---

## 0. Non-negotiable rules

1. Follow this guide in order. Record commands, versions, outputs, and failures; do not silently skip a step.
2. Do **not** merge PR #73, merge PR #72, deploy to production, change production settings, or trigger any production processing job as part of this investigation.
3. Do **not** call the Cloudflare Whisper Worker for these tests. This plan is local-only and must not consume Cloudflare inference quota. If a test unexpectedly selects the remote provider, stop and investigate the configuration before proceeding.
4. Never paste secrets, access tokens, signed URLs, full `.env` files, customer data, or private audio into logs, issues, or the report. Do not print secret environment values to diagnose settings.
5. Preserve the original audio/video. Use a copy of the source media and separate output directories for each test run.
6. Do not automatically translate, rewrite, or “correct” Whisper output to make it look Burmese. Save the raw JSON from both runs and compare it.
7. The Myanmar Unicode check is only a script-presence guard. A few Myanmar characters do not prove that a transcript is correct Burmese.
8. If the exact PR head, the test command, or the provider configuration cannot be verified, stop and document the blocker rather than guessing.

## 1. Confirm repository and exact PR head

Run in **PowerShell** from the repository root:

```powershell
git status --short
git fetch origin
git switch fix/burmese-asr-script-guard
git pull --ff-only origin fix/burmese-asr-script-guard
git rev-parse HEAD
git log -1 --oneline
```

- Confirm the branch is `fix/burmese-asr-script-guard`.
- Open [PR #73](https://github.com/dragonknighttw-cmd/Narrativ-Forge/pull/73) and compare the local `git rev-parse HEAD` with the current PR head SHA shown by GitHub. They must match before testing.
- If the working tree has changes, **do not discard them**. Save/commit/stash them according to the repository owner's normal process before switching branches.
- If the branch is missing, fetch it explicitly; do not create a replacement branch from an unknown commit.
- Record the SHA, OS version, Python version, and Git version in the test report.

```powershell
$PSVersionTable.PSVersion
python --version
git --version
```

## 2. Identify the test audio safely

Use the **same known Burmese-language source recording** that originally produced Chinese characters. The recording is described as Burmese speech discussing ChatGPT models.

- Work on a copy. Do not re-encode or edit the reference source before the comparison.
- Record the file name, container/extension, duration, sample rate/channels if known, and file size. Avoid putting personal information in the filename.
- Calculate and record a SHA-256 hash before testing:

```powershell
Get-FileHash "C:\PATH\TO\burmese-reference-audio.wav" -Algorithm SHA256
```

Replace the example path with the actual local path. Do not commit or upload the audio unless the owner explicitly authorizes that.
- If the original recording is a video, use a separate working copy and extract audio to a temporary test folder. Do not overwrite the source. If the product's normal input is a video, later perform the end-to-end check on a copy of that video too.

Create separate output folders:

```powershell
New-Item -ItemType Directory -Force .\artifacts\asr-burmese\auto | Out-Null
New-Item -ItemType Directory -Force .\artifacts\asr-burmese\forced-my | Out-Null
```

If this repository ignores `artifacts/`, keep test outputs there. Otherwise use a temporary folder outside the repository so audio/transcripts cannot be committed accidentally.

## 3. Prepare Python dependencies

Use the Python version specified by the current CI workflow (currently Python 3.12) and create a dedicated virtual environment. From the backend folder:

```powershell
Set-Location .\web-platform\backend
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

If Python 3.12 is not installed, stop and install the project's required Python version using the machine's approved process; do not silently switch to a different version.

The standard requirements file does not itself install OpenAI Whisper. Only if local inference is part of the approved test, install the optional real-processing dependency:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-real-processing.txt
```

Whisper may also require a working FFmpeg installation and compatible PyTorch/runtime dependencies. Verify these without printing secrets:

```powershell
ffmpeg -version
ffprobe -version
.\.venv\Scripts\python.exe -m whisper --help
```

If a command is not found or dependency installation fails, capture the error and stop at that point. Do not install random global packages or change production runtime configuration to work around it.

## 4. Run regression tests before real inference

From `web-platform/backend`:

```powershell
$env:PYTHONPATH = "."
.\.venv\Scripts\python.exe -m pytest tests/test_whisper_fallback.py -vv
```

Then run the same backend unit/security marker set used by CI:

```powershell
.\.venv\Scripts\python.exe -m pytest -m "unit or security" -vv
```

Record pass/fail counts and the complete failing test names. If a test fails, do not alter expected results simply to make the run pass. Capture the error, stop the acceptance sequence, and diagnose the failure in a separate change.

These tests are code-regression checks; passing them does **not** prove Whisper recognizes Burmese correctly.

## 5. Confirm the local Whisper configuration

Before running inference, inspect the repository's settings definitions and local configuration to determine:
- the actual configured `whisper_command`;
- the configured `whisper_model`;
- how the local Whisper CLI is invoked in this environment;
- whether `whisper_remote_enabled` is disabled for the local-only run.

Read setting names and non-secret values only. Never dump the whole environment or `.env` file.

**Mandatory provider rule:** if the normal processing path would call `_transcribe_cloudflare`, do not start an end-to-end job until you have a verified local-only test configuration. Prefer direct local CLI comparison in Step 6 first. Do not change production settings; any local override must be temporary and clearly documented.

## 6. Compare auto-detect with forced Burmese on the exact same audio

Use the exact same input bytes, the same Whisper model, and separate output directories. Run the command from the backend's active virtual environment. Substitute the actual source path and the exact model value established in Step 5.

**Run A — language auto-detection:**

```powershell
.\.venv\Scripts\python.exe -m whisper "C:\PATH\TO\burmese-reference-audio.wav" --task transcribe --output_format json --output_dir "C:\PATH\TO\asr-burmese\auto" --model MODEL_NAME
```

**Run B — force Burmese language:**

```powershell
.\.venv\Scripts\python.exe -m whisper "C:\PATH\TO\burmese-reference-audio.wav" --task transcribe --output_format json --output_dir "C:\PATH\TO\asr-burmese\forced-my" --model MODEL_NAME --language Burmese
```

Replace `MODEL_NAME` with the exact same model in both commands and replace the example paths with real paths. Do not type the literal placeholder. If the installed Whisper version rejects `--language Burmese`, stop, record the exact CLI error and inspect that version's `--help`; do not guess a language code.

If the original source is a video rather than an audio file, first make one documented, loss-minimizing test audio extraction using the project's supported FFmpeg command, and feed that **same extracted audio file** to both runs. Record the extraction command and hash of the extracted file.

For each run, preserve:
- the raw JSON file;
- command and exit code;
- model name and Whisper/package versions;
- detected `language` metadata (if present);
- transcript `text`;
- segment count, timestamps, and each segment's text;
- elapsed time and any warnings/errors.

Do not overwrite one run with the other. Do not judge the result by script alone: manually review the Burmese text against the source audio, including the discussion of ChatGPT models. Mark unintelligible spans as such in the report rather than inventing words.

## 7. Compare results consistently

Create a table in the report:

| Check | Auto-detect | Forced Burmese |
|---|---|---|
| Command exit code | | |
| Model/version | | |
| Detected language metadata | | |
| Transcript is non-empty | | |
| Myanmar-script text present | | |
| Text matches the spoken Burmese | | |
| Chinese characters unexpectedly present | | |
| Segment timestamps plausible | | |
| Missing/repeated phrases | | |
| Elapsed time | | |

Answer these questions with evidence:
1. Does auto-detect report Chinese (or another unexpected language) while forced Burmese reports Burmese?
2. Does forced Burmese improve actual word-level accuracy, or merely change the script?
3. Are ChatGPT/model names, English technical terms, and Burmese phrases handled sensibly?
4. Are segments in chronological order and do timestamps stay within the source duration?
5. Does either run produce an empty transcript or a transcript unrelated to the audio?

A forced-language result is not automatically the correct result. Compare both against the actual recording. Preserve examples of correct, incorrect, omitted, and hallucinated words without exposing private content.

## 8. Validate the application's transcript guard and processing path

After the direct CLI comparison, validate the application path on a **local test environment and a copy of the media only**.

Expected current guard behavior in `real_processing.py`:
- Non-empty transcript with no Myanmar-script characters in the main text or segments → job fails with `ASR_LANGUAGE_MISMATCH`.
- Empty transcript (e.g. silence/tone smoke fixture) → must **not** be rejected by this script guard alone.
- Myanmar-script characters present → the guard permits the transcript to continue, but this is not proof of accuracy.

Check all of the following:
- [ ] The correct input asset is selected.
- [ ] Local-only configuration is active; no remote Cloudflare request occurs.
- [ ] Chinese-only, non-empty output is rejected before a transcript asset is stored.
- [ ] Empty transcript output is not mislabeled as `ASR_LANGUAGE_MISMATCH`.
- [ ] A Myanmar-script transcript can continue through the expected processing path.
- [ ] Error code/message are visible through the existing job status/API path and do not expose secrets.
- [ ] The source video/audio remains unchanged (compare SHA-256 hashes before and after).
- [ ] Processed video has audio/video streams and is playable.
- [ ] Transcript JSON is retrievable and decodes as UTF-8.
- [ ] Subtitle generation uses the intended transcript; cue timing is plausible, chronological, and within media duration.
- [ ] Existing subtitle review workflow still works.
- [ ] No duplicate, stale, or mismatched transcript asset is attached to the episode.

Do not fake a successful end-to-end run by editing database rows or manually changing job status. If the app requires external credentials/services that are unavailable in local test mode, mark that check **BLOCKED** and record the missing dependency without invoking production services.

## 8.1. Static review of the primary Cloudflare path (no inference run)

The repository's primary provider path is remote-first when `whisper_remote_enabled` and `cloudflare_whisper_worker_url` are configured. The current Worker calls `env.AI.run("@cf/openai/whisper", { audio: [...body] })`; it does not pass a language hint, and the Worker response currently does not preserve language-detection metadata. The local CLI comparison alone therefore does not establish how the primary remote provider behaved.

Before changing this path, review the model contract and cost impact:
- [Cloudflare `@cf/openai/whisper` model documentation](https://developers.cloudflare.com/ai/models/%40cf/openai/whisper/)
- [Cloudflare `@cf/openai/whisper-large-v3-turbo` parameters](https://developers.cloudflare.com/ai/models/%40cf/openai/whisper-large-v3-turbo/), which document a `language` input parameter.
- The current and alternative model IDs are not interchangeable by assumption. A model switch or language-hint change needs contract tests and owner review; it may change accuracy, latency, response shape, and inference cost.

**Diagnostic metadata improvement made in PR #73:** the Worker now forwards provider `language` and `language_probability` fields when available (including nested `transcription_info`) and omits them when the provider does not supply them. The backend already stores the Worker JSON payload. This is a response-metadata pass-through only: it does not force a language, change the model, or prove that the current model returns these fields. A mocked Worker contract test covers the nested metadata case. Exact-head CI remains to be verified.

Do **not** send a live request to Cloudflare during this investigation. Do not switch the production Worker model, change its language behavior, or deploy it as part of this local acceptance procedure. A follow-up code change can add explicit language configuration only after the maintainer confirms the intended source-language policy and reviews the model's supported input schema and quota/cost impact. Where supported, preserve language metadata from the provider so the investigation can distinguish detection from transcription quality.

## 9. Evaluate whether the guard is sufficient

The current check asks only whether at least one character falls in U+1000–U+109F. This is intentionally weak. It can reject legitimate non-Burmese-language content and can accept incorrect text containing one Myanmar character.

Do not expand the heuristic or silently rewrite ASR text during this acceptance run. Based on the samples, propose any stronger language/quality gate as a separate change with tests, and consider the product's intended language scope before enforcing Burmese-only output.

## 10. Acceptance criteria

Mark the investigation **PASS** only when all applicable criteria are evidenced:
- [ ] Focused Whisper regression tests pass.
- [ ] Backend unit/security tests pass.
- [ ] Auto-detect and forced Burmese runs are both captured for the same audio and model.
- [ ] Actual transcript quality is reviewed against the source recording, not just Unicode script.
- [ ] The reason for Chinese output is supported by the language metadata/output comparison or is explicitly left unresolved.
- [ ] Local-only provider routing is verified; no Cloudflare inference/quota was used.
- [ ] Guard behavior for Chinese-only, Myanmar-script, and empty transcript cases is verified.
- [ ] Transcript retrieval, subtitle timing, playback, and source integrity checks pass, or any unavailable end-to-end checks are clearly marked BLOCKED.
- [ ] Results are written to the report template below and reviewed.

If any required test fails, the result is **FAIL**, not PASS. If required local tools/media/credentials are unavailable, the result is **BLOCKED**. Do not merge PR #73 or deploy until the maintainer explicitly reviews the evidence and authorizes the next step.

## 11. Required result report

Create/update `docs/Report/ASR_BURMESE_LOCAL_ACCEPTANCE_RESULTS_YYYY-MM-DD.md` using this structure:

```markdown
# Local Burmese ASR Acceptance Results

- Date/time and timezone:
- Operator:
- Repository branch:
- Tested commit SHA:
- OS / Python / Whisper / FFmpeg versions:
- Source media filename (no private identifiers):
- Source SHA-256:
- Source duration:
- Configured model:
- Local-only routing evidence:
- Cloudflare inference used: NO (required for this plan)

## Regression tests
- Focused Whisper tests: PASS / FAIL / BLOCKED
- Backend unit/security tests: PASS / FAIL / BLOCKED
- Command output / failure summary:

## Same-audio comparison
- Auto-detect command/result:
- Forced-Burmese command/result:
- Detected language metadata for each:
- Transcript quality notes:
- Chinese characters unexpectedly present:
- Segment/timestamp notes:

## Application-path checks
- ASR_LANGUAGE_MISMATCH behavior:
- Empty transcript behavior:
- Transcript retrieval:
- Subtitle timing:
- Processed media playback:
- Source hash unchanged:
- Any BLOCKED checks and reason:

## Conclusion
- Overall status: PASS / FAIL / BLOCKED
- Root cause established or still unknown:
- Evidence paths:
- Follow-up code changes proposed (if any):
- Explicit approval still needed for merge/deployment:
```

Store raw JSON and logs in a local ignored/temp artifact directory. Commit only the sanitized report and appropriate non-sensitive test evidence. Never commit source media, secrets, raw personal audio, or tokens.

---

## 12. Prompt for the local coding agent

Copy and paste this prompt when local execution is available:

> Read and follow `docs/Report/LOCAL_BURMESE_ASR_ACCEPTANCE_GUIDE_2026-10-13.md` from top to bottom. Treat it as the required procedure, not optional suggestions. First verify the current branch and exact PR #73 head SHA. Do not discard local changes. Run the focused Whisper tests and backend unit/security tests; then compare local Whisper auto-detection and forced Burmese on the exact same reference audio and same model, preserving separate raw JSON outputs. Verify local-only routing before any application-path run. Complete the script-guard, empty-transcript, source-integrity, transcript retrieval, subtitle-timing, and playback checks that are possible. Do not call Cloudflare inference, consume quota, change production configuration, deploy, merge any PR, or edit test expectations just to get a pass. Do not translate or rewrite model output. If a step cannot run, mark it BLOCKED with the exact command/error and continue only where safe. Write sanitized results to `docs/Report/ASR_BURMESE_LOCAL_ACCEPTANCE_RESULTS_YYYY-MM-DD.md`, summarize PASS/FAIL/BLOCKED evidence, and stop for maintainer review before proposing or applying further code changes. Do not claim success without logs or artifacts supporting it.



