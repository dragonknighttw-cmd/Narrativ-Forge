# Windows Local Unicode Runtime Report

**Date:** 2026-10-12 (local time, UTC+06:30)
**Status:** Local synthetic runtime verified within the scope described below; not production verified.
**Report refresh checkpoint:** `main` HEAD `95aa9163cc40383a8c44c3a5f445e4de899116e4` (dirty worktree; historical worker run SHA not recorded)

`LOCAL_RUNTIME_ROOT` is a redacted placeholder for the local runtime data root. Absolute machine-specific paths are intentionally omitted from this shareable report.

## Objective and Unicode-only decision

Run the existing Windows-native Narrativ Forge backend and canonical Celery worker locally without Docker, WSL, PyICU, ICU SDKs, or Visual C++ Build Tools.

The accepted subtitle input contract is Unicode Burmese only. Text is normalized with Python's standard-library NFC implementation. Zawgyi detection and conversion are unsupported; the application does not claim to identify or convert Zawgyi text. The only accepted `SUBTITLE_NORMALIZATION_MODE` is `unicode_nfc_only`.

## Runtime components

| Component | Version / configuration | Location or evidence |
|---|---|---|
| Python venv | CPython 3.12.13 x64 | `LOCAL_RUNTIME_ROOT\venv` |
| Python base executable | Existing user-installed Python, not installed or modified for this task | Under the user's C: profile; the venv executable and packages are on D: |
| FastAPI | 0.143.0 | D-drive venv |
| SQLAlchemy | 2.1.4 | D-drive venv |
| Celery | 5.6.3, solo pool, concurrency 1 | Canonical app worker |
| Redis Python client | 8.1.0 | D-drive venv |
| Whisper | 20250625 | D-drive venv |
| PyTorch | 2.14.1+cpu | D-drive venv |
| Whisper model | multilingual `tiny`, 75,572,083 bytes | `LOCAL_RUNTIME_ROOT\data\cache\whisper\tiny.pt` |
| FFmpeg / ffprobe | n9.0.2 static x64 | `LOCAL_RUNTIME_ROOT\ffmpeg\ffmpeg-n9.0-latest-win64-gpl-9.0\bin` |
| Memurai Developer | 8.2.0, local loopback port 6380 | `LOCAL_RUNTIME_ROOT\memurai`; local data under `LOCAL_RUNTIME_ROOT\data\redis` |
| Micromamba probe | 2.9.0; Python 3.12.15 and ICU 78.3 probe environment | `LOCAL_RUNTIME_ROOT\micromamba` |

Complete `requirements.txt` and `requirements-real-processing.txt` were installed into the D-drive venv using `pip --only-binary=:all:`. The pip cache and `TEMP`/`TMP` were under `LOCAL_RUNTIME_ROOT`. `pip check` reported no broken requirements. PyICU and myanmartools were removed from mandatory requirements; neither was installed. The earlier conda-forge probe confirmed that a Windows ICU package exists but a Windows PyICU package does not. No source build was attempted.

## Disk usage

| Measurement | Before | After |
|---|---:|---:|
| C: free space | 15.408 GiB | 15.412 GiB |
| D: free space | 74.112 GiB | 73.787 GiB |
| `LOCAL_RUNTIME_ROOT` total footprint | 2.048 GiB at the prior runtime checkpoint | 2.239 GiB |

All dependency, pip cache, Whisper cache, SQLite, log, and test-artifact paths used for this work were configured on D:. No Python/packages/cache/temp were installed on C:. The existing base Python executable for the D-drive virtual environment is already located in the user's C: profile; its location was not changed. The small increase in C: free space is an ambient measurement change and is not attributed to this task.

## Runtime artifacts

- SQLite database, migrated to Alembic revision `0018_tenant_backfill_guard`: `LOCAL_RUNTIME_ROOT\data\narrativ-forge-local-smoke.db`
- Generated input video: `LOCAL_RUNTIME_ROOT\data\worker\smoke-upload-storage\source.mp4`
- Local storage root: `LOCAL_RUNTIME_ROOT\data\uploads\objects`
- Local storage input upload: `LOCAL_RUNTIME_ROOT\data\uploads\objects\episodes\5a307176-245c-4961-8b22-fd800147e2d8\assets\v1\video\source.mp4`
- Worker-processed video: `LOCAL_RUNTIME_ROOT\data\uploads\objects\episodes\5a307176-245c-4961-8b22-fd800147e2d8\assets\v2\processed_video\01bdb06bf4d244769df09c3e7958ad68_final.mp4`
- Whisper transcript asset: `LOCAL_RUNTIME_ROOT\data\uploads\objects\episodes\5a307176-245c-4961-8b22-fd800147e2d8\assets\v3\transcript\1d289ad8fda44c97b4ef728f9f7d043a_transcript.json`
- Deterministic Unicode transcript fixture: `LOCAL_RUNTIME_ROOT\data\worker\unicode-subtitle-fixture\unicode-fixture-transcript.json`
- NFC-normalized SRT fixture: `LOCAL_RUNTIME_ROOT\data\worker\unicode-subtitle-fixture\unicode-fixture.srt`
- Install log: `LOCAL_RUNTIME_ROOT\logs\pip-backend-install.log`
- Preflight JSON: `LOCAL_RUNTIME_ROOT\logs\preflight-unicode-runtime.json`
- Canonical worker output: `LOCAL_RUNTIME_ROOT\logs\worker-smoke-unicode.log`
- Storage-backed canonical worker output: `LOCAL_RUNTIME_ROOT\logs\worker-smoke-upload-storage.log`
- Worker lifecycle log: `LOCAL_RUNTIME_ROOT\logs\celery-local-worker-upload.log`
- SAPI/Whisper probe log: `LOCAL_RUNTIME_ROOT\logs\unicode-whisper-probe.log`

## Checks and results

| Check | Result |
|---|---|
| Unicode normalization unit tests | Passed |
| Local media preflight unit tests | Passed |
| Subtitle API generation/export integration test | Passed; response reports `unicode_nfc_only` and export contains Unicode Burmese |
| Combined focused subtitle/preflight/API tests | **10 passed** |
| Full backend unit selection (`pytest -m unit`) | **Historical result: 260 passed, 5 skipped, 103 deselected, 1 failed** |
| Historical full-suite failure | `tests/test_root_restore_db.py::test_sqlite_restore_replaces_target_only_after_integrity_check` failed on Windows with a SQLite file-handle lock. The issue was fixed later; see Windows Local Runtime Evidence run [#38199416863](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/38199416863) on commit `644f4346f59d03b7185531e8621b26a989e502fb`. |
| Dependency consistency (`pip check`) | Passed |
| Local media preflight | **7/7 passed**: ffmpeg, ffprobe, Whisper CLI, Memurai/Redis reachability, writable D: work directory, free space, cached tiny model |
| Alembic migration | Passed through `0018_tenant_backfill_guard` on the disposable local SQLite database |
| Canonical Celery worker smoke | **Passed**: generated input was uploaded through the local storage provider, the task queued through Memurai, and FFmpeg rendering, local Whisper, transcript asset, processed-video asset, and subtitle row were created; ProcessingJob completed at 100% |
| Unicode subtitle service fixture | Passed: deterministic Unicode transcript generated subtitle version 2, normalized its Myanmar cue to U+1026 (`ဦ`), had no validation errors, and wrote an SRT artifact |
| Worker shutdown | Celery remote shutdown received; worker process no longer running. The background PowerShell worker session reported exit code 1 after shutdown, while its log recorded the shutdown and the targeted PID was absent; the canonical smoke command itself returned 0 and the queued task succeeded. Memurai was left running as the pre-existing local runtime component. |
| `git diff --check` | Passed |

An initial local rerun of `tests/test_real_processing_subprocess.py` on 2026-10-12 reported 5 passed, 1 failed, 2 skipped because the process-tree timeout test's 0.2-second window expired before the child PID file appeared. The isolated test passed. The test-only startup window was increased to 2 seconds, then the full file passed: **6 passed, 2 skipped in 4.41s**. Production timeout behavior was not changed. These runs used a dirty worktree based on HEAD `95aa9163cc40383a8c44c3a5f445e4de899116e4`; no commit contains the tested edits.

The final storage-backed worker smoke job ID was `ffe5abb2-193c-47a3-a976-110ca18d54e8`. Its generated tone media contained no speech. Whisper returned zero segments, so the worker-created draft subtitle has zero cues. The separately persisted Unicode transcript fixture verifies the actual subtitle service and local SRT output, but it is not evidence that Whisper recognized spoken Burmese.

## What the evidence proves

- The edited backend requirements can install as binary packages in the existing D-drive virtual environment without PyICU or native source compilation.
- Unicode NFC normalization and the explicit Unicode-only status are exercised in tests and exposed in subtitle API metadata.
- On this Windows host, the existing canonical Celery task can process generated media through local Memurai, FFmpeg, Whisper tiny, local storage, and SQLite, then persist its job/assets/subtitle record.
- The subtitle service can read a Unicode transcript fixture from local storage, normalize it, persist subtitle cues, and render a Unicode SRT.

## What it does not prove / remaining limitations

- It is not production, cloud-provider, packaged-product, or long-running Windows-service verification.
- The generated worker audio was a tone, not Burmese speech. Burmese Whisper accuracy, subtitle quality, and human-language review remain **VERIFY**.
- The SAPI voices installed on this host are English-only; an offline speech probe did not produce a Unicode Burmese Whisper transcript.
- Zawgyi is not detected or converted. Inputs must already be Unicode Burmese; no conversion compatibility is promised.
- Memurai Developer is only for development/testing and has its own restart/license limitations; it is not approved for production use.

## Latest fix and verification (2026-10-12)

A Windows-specific subprocess issue was found during the local worker run: child-process stdout/stderr were decoded with the Windows default codepage, which produced a `UnicodeDecodeError` while Whisper output was being read. This was fixed by setting `encoding="utf-8"` and `errors="backslashreplace"` inside the repository's real-processing subprocess wrapper.

Evidence:
- Targeted regression test: `tests/test_real_processing_subprocess.py`
- Fresh final run result: `6 passed, 2 skipped in 4.41s` after increasing the test-only Windows startup window
- Local sample run after the fix: `SAMPLE_WORKER_OK`, `status=completed`, `progress=100`, `output_exists=True`, `transcript_exists=True`, `input_unchanged=True`

This confirms the Windows CP1252 decode issue is addressed without changing the repository's local runtime contract. The sample processing was local synthetic-runtime verification only; real Burmese speech-quality and production-provider acceptance are still pending. The exact source commit used for the earlier worker sample run was not captured, so that historical run cannot be tied to an exact source SHA.
- The D-drive venv's existing base Python executable resides under the C: user profile even though the venv, packages, caches, and runtime data are on D:. No Python installation or package cache was added to C:.

## Safe cleanup guidance

No cleanup was performed. The following are task-created synthetic test artifacts and can be removed **only after confirming they are no longer needed**:

- `LOCAL_RUNTIME_ROOT\data\worker\smoke-unicode-only\` — generated tone/video input for the worker smoke.
- `LOCAL_RUNTIME_ROOT\data\worker\smoke-upload-storage\` — generated tone/video input for the final storage-backed worker smoke.
- `LOCAL_RUNTIME_ROOT\data\worker\unicode-audio-probe\` — generated English SAPI/Whisper diagnostic.
- `LOCAL_RUNTIME_ROOT\data\worker\unicode-subtitle-fixture\` — deterministic transcript/SRT fixture.
- `LOCAL_RUNTIME_ROOT\data\uploads\objects\episodes\5a307176-245c-4961-8b22-fd800147e2d8\` — exact episode subtree generated for the final storage-backed smoke, including input/output/transcript assets.
- `LOCAL_RUNTIME_ROOT\data\uploads\objects\episodes\35d5dd91-d594-4c53-b688-ab11f3410d54\` — earlier generated pipeline test episode that also contains the Unicode fixture asset.

The SQLite database contains smoke job/episode rows and a Unicode fixture asset reference. Keep both episode subtrees unless you intentionally discard their related rows/assets together; deleting files alone would leave dangling database references. Do not delete the database, general `uploads`/`data`/`redis` folders, Whisper model, virtual environment, FFmpeg, Memurai, Micromamba, or installers as part of test cleanup. Database-row cleanup or removal of any shared runtime component requires a separate confirmation. Preserve the logs until the report/evidence is no longer needed.
