# Local Runtime Contract

Status: **API + SQLite smoke implemented; full desktop/package runtime pending.**

This document defines the first local-runtime verification boundary. It deliberately does not claim that Narrativ Forge is already a complete offline desktop application.

## Current local-mode inputs

The backend already supports these local defaults/configuration points:

- `APP_ENV=development`
- `DATABASE_URL=sqlite:///./narrativ_forge.db`
- `STORAGE_PROVIDER=local`
- `UPLOAD_DIR=./storage/uploads`
- `REDIS_URL` omitted when a code path does not require Redis
- `FFMPEG_BINARY`, `FFPROBE_BINARY`, and `WHISPER_COMMAND` configurable for future bundled sidecars

Use `apps/web-platform/backend/.env.example` as the reference for all settings. Never copy production credentials into a local .env file or commit secrets.

## Reproducible local API smoke

The GitHub Actions workflow `.github/workflows/local-runtime-evidence.yml` runs against the exact triggering commit in a fresh Ubuntu runner. It:

1. installs the backend's locked-by-range requirements;
2. migrates a fresh SQLite database to the current Alembic head;
3. starts the FastAPI app with local storage selected;
4. checks `/api/v1/health` and `/api/v1/ready`;
5. checks SQLite connectivity and local storage write/read;
6. records commit/run metadata and uploads logs, migration output, HTTP checks, and a JSON manifest;
7. stops the API process even when earlier checks fail.

This is **local-runtime CI evidence**, not proof that a Windows installer works, the media worker runs offline, or production providers work. The manifest intentionally marks `package_installed=false` and `production_verified=false`.

## Local profile versus cloud profile

| Concern | Local profile target | Cloud profile target |
|---|---|---|
| Database | SQLite file under user data | PostgreSQL |
| Asset storage | Local filesystem | Configured provider / object storage |
| API | Bundled or managed local process | Container/service runtime |
| Worker | Local process with media dependencies | Celery worker with Redis and cloud dependencies as configured |
| Secrets | Optional local integrations; never required for local smoke | GitHub Environment / deployment secret store |
| Evidence | Local API, storage, package and media smoke | Provider, tenant, worker, backup/restore E2E |
| Cleanup | Stop child processes; preserve user data | Destroy ephemeral services and revoke temporary resources |

The shared application services should remain common across profiles. Runtime selection should happen through configuration and launch orchestration, not a forked business-logic implementation.

## Remaining package prerequisites

Before calling the local product packaged or offline-capable, implement and verify:

- a Windows build runner and reproducible artifact naming/checksum;
- a desktop shell decision based on a working sidecar prototype (do not assume Tauri/Electron before proving process lifecycle and installer output);
- API + frontend launch/health supervision;
- a local worker process and clean shutdown/restart behavior;
- FFmpeg/ffprobe discovery and licensing/redistribution review;
- Whisper model/runtime policy, download/cache behavior, and offline capability disclosure;
- persistent user-data directory and safe upgrade/migration behavior;
- install -> launch -> E2E -> collect logs -> uninstall/cleanup smoke on a clean Windows runner.

A successful Ubuntu local API smoke is necessary groundwork but cannot substitute for these Windows/package checks.

## Windows runner compatibility smoke

The workflow `.github/workflows/windows-local-runtime-evidence.yml` repeats the API + SQLite + local-filesystem smoke on a clean `windows-latest` runner. It is a Windows runtime compatibility check only: it does not install a desktop package, bundle Python/FFmpeg/Whisper, or prove offline media processing. Its manifest keeps `package_installed=false` and `production_verified=false` until those separate gates exist.

## Docker-free Windows media-runtime prototype

This is a developer prototype for exercising the existing Celery worker on Windows; it is not a packaged/offline product. It uses Python, FFmpeg, Whisper, a Redis-compatible Windows runtime, SQLite, and local files. It does not use Docker, WSL, cloud Whisper, paid inference, or production data.

### Current machine checkpoint — 2026-10-12 (local, UTC+06:30)

- **DONE — Unicode-only normalization contract:** subtitle normalization is fixed to `unicode_nfc_only` in application configuration and uses Python's standard-library NFC. The API includes this contract in subtitle metadata. `PyICU` and `myanmartools` have been removed from mandatory backend requirements because they were only used for the unsupported Zawgyi detection/conversion path. The legacy Zawgyi helper/threshold now raises an explicit unsupported-format error; no detection or conversion is claimed.
- **DONE — D-drive backend environment:** Python 3.12.13 venv at `D:\NarrativForge\venv`; FastAPI 0.143.0, SQLAlchemy 2.1.4, Celery 5.6.3, Redis client 8.1.0, OpenAI Whisper 20250625, and CPU PyTorch 2.14.1. Complete `requirements.txt` plus `requirements-real-processing.txt` installed with `--only-binary=:all:` using `D:\NarrativForge\pip-cache` and `D:\NarrativForge\tmp`; no ICU/Visual C++ build, Docker, or WSL was used. The venv and packages are on D:, while its pre-existing base Python executable is under the C: user profile; no Python or package was installed on C: during this work.
- **DONE — native components:** FFmpeg/ffprobe n9.0.2, Whisper multilingual `tiny` model (75,572,083 bytes), Micromamba 2.9.0 probe tooling, and signed Memurai Developer 8.2.0 remain under `D:\NarrativForge`. Memurai stayed on loopback port 6380; the existing Redis port 6379 was untouched.
- **VERIFIED — preflight/migrations:** all seven preflight checks passed; JSON evidence is `D:\NarrativForge\logs\preflight-unicode-runtime.json`. Alembic migrated the disposable D-drive SQLite database through revision `0018_tenant_backfill_guard`.
- **VERIFIED — canonical worker smoke, local synthetic scope only:** existing `scripts\worker_smoke.py` uploaded its generated video through the local storage provider, queued `narrativ.process_real_job` on the existing Celery worker, and completed Memurai, FFmpeg rendering, local Whisper tiny, transcript storage, and processed-video storage. ProcessingJob `ffe5abb2-193c-47a3-a976-110ca18d54e8` is completed at 100%; the uploaded input, processed output, and transcript assets all exist under `D:\NarrativForge\data\uploads`. The generated tone fixture contains no speech: local Whisper produced an empty transcript (0 segments), and the worker-created draft subtitle has 0 cues. A separate deterministic Unicode transcript fixture was processed by the canonical subtitle service into subtitle version 2 with NFC cue U+1026 and no validation errors; its transcript/SRT are under `D:\NarrativForge\data\worker\unicode-subtitle-fixture`. The API integration test also verified Unicode subtitle generation/export and the returned normalization metadata.
- **VERIFIED — tests:** focused subtitle, local-preflight, and subtitle API integration tests: 10 passed. Full backend unit suite: 260 passed, 5 skipped, 103 deselected, 1 failed due to the existing Windows SQLite restore test retaining a file handle during `Path.replace` (`tests/test_root_restore_db.py::test_sqlite_restore_replaces_target_only_after_integrity_check`). That unrelated restore-test issue was not changed. `pip check` passed.
- **VERIFY — quality/production scope:** synthetic silence and the English-only installed Windows SAPI voices do not verify Burmese speech recognition accuracy. No production/provider, real-media, packaged worker, or long-running service verification is claimed. Worker process shut down after the run; Memurai remains available as the user's existing local service process.

At the latest measurement, `D:\NarrativForge` occupies approximately **2.239 GiB**. Free space changed from **C: 15.408 GiB / D: 74.112 GiB before** to **C: 15.412 GiB / D: 73.787 GiB after**. All package cache and TEMP/TMP paths used for this work were under D:; the small increase in reported C: free space is not attributable to this task. No runtime files were cleaned up. Exact evidence and safe cleanup guidance are in [docs/Report/LOCAL_WINDOWS_UNICODE_RUNTIME_REPORT.md](./Report/LOCAL_WINDOWS_UNICODE_RUNTIME_REPORT.md).

### One-time prerequisites

1. Install 64-bit Python 3.12. Keep the virtual environment and working data on the desired drive; the example below uses `D:\NarrativForge`.
2. Download a Windows x64 FFmpeg build from the [FFmpeg download page](https://ffmpeg.org/download.html), extract it, and add its `bin` directory to `PATH`. `ffmpeg.exe` and `ffprobe.exe` must both be available.
3. Install a currently supported Windows-native Redis-compatible server. [Memurai](https://www.memurai.com/) can run natively without Docker or WSL; the current verified local config binds to loopback on port 6380 and writes its data/logs under `D:\NarrativForge`. Start the extracted process (no Windows service registration):

```powershell
$root = "D:\NarrativForge"
$memurai = "$root\memurai\Memurai\memurai.exe"
if (-not (Get-Process memurai -ErrorAction SilentlyContinue)) {
  $process = Start-Process -FilePath $memurai -ArgumentList "$root\data\memurai-local.conf" -PassThru -WindowStyle Hidden
  $process.Id | Set-Content -Encoding ascii "$root\data\memurai.pid"
}
& "$root\memurai\Memurai\memurai-cli.exe" -h 127.0.0.1 -p 6380 ping
```

A system service installation needs administrator permission. Memurai Developer is only for development/testing and must not be used in production or redistributed without license review.
4. Use a Python 3.12 environment rooted on D:. Subtitle inputs are Unicode Burmese only; NFC normalization uses the Python standard library, and Zawgyi detection/conversion is unsupported. Install the complete requirements with wheel-only mode so a missing binary package cannot trigger a source build:

```powershell
Set-Location D:\Project\dragonknight.tw@gmail.com\Narrativ-Forge\apps/web-platform\backend
$root = "D:\NarrativForge"
$env:TEMP = "$root\tmp"
$env:TMP = "$root\tmp"
$env:PIP_CACHE_DIR = "$root\pip-cache"
$env:XDG_CACHE_HOME = "$root\data\cache"
$env:TORCH_HOME = "$root\data\cache\torch"
$env:PYTHONIOENCODING = "utf-8"
& "$root\venv\Scripts\python.exe" -m pip install --only-binary=:all: --cache-dir "$root\pip-cache" -r requirements.txt -r requirements-real-processing.txt
```

PyTorch/Whisper are part of the real-processing runtime; the CPU-only PyTorch and `tiny` weights are installed/cached separately. The first dependency/model download needs internet. Do not install ICU SDKs, Visual C++ Build Tools, Docker, or WSL for this Unicode-only runtime.

### Configure D-drive data and fetch the smoke model

The current Memurai process is configured on `127.0.0.1:6380`. Confirm it responds with `PONG`; do not change the existing Windows Redis service on port 6379 or expose Memurai to the network:

```powershell
& "D:\NarrativForge\memurai\Memurai\memurai-cli.exe" -h 127.0.0.1 -p 6380 ping
```

In the activated PowerShell session, set FFmpeg's actual extracted path and local paths:

```powershell
$env:PATH = "D:\NarrativForge\ffmpeg\ffmpeg-n9.0-latest-win64-gpl-9.0\bin;D:\NarrativForge\venv\Scripts;$env:PATH"
$data = "D:\NarrativForge\data"
New-Item -ItemType Directory -Force -Path $data, "$data\uploads", "$data\worker", "$data\cache" | Out-Null
$env:DATABASE_URL = "sqlite:///" + (Join-Path $data "narrativ-forge-local-smoke.db").Replace("\", "/")
$env:REDIS_URL = "redis://127.0.0.1:6380/0"
$env:STORAGE_PROVIDER = "local"
$env:UPLOAD_DIR = "$data\uploads"
$env:XDG_CACHE_HOME = "$data\cache"
$env:WHISPER_REMOTE_ENABLED = "false"
$env:WHISPER_MODEL = "tiny"
$env:WORKER_EVIDENCE_QUEUE = "local_media"

python -c "import os, whisper; whisper.load_model('tiny', download_root=os.path.join(os.environ['XDG_CACHE_HOME'], 'whisper'))"
python scripts\local_media_preflight.py --require-model --model tiny --whisper-cache-dir "$data\cache\whisper" --work-dir "$data\worker"
```

`tiny` is only for the generated smoke fixture. The application's default is multilingual `small`, so replace `tiny` consistently only after checking model disk/RAM needs. The preflight does not install packages, download model weights, start Redis/the worker, or process user media. It checks FFmpeg/ffprobe/Whisper CLI, Redis reachability (redacting credentials), writable disk space, and the selected model cache. A preflight failure is an actionable local prerequisite failure, not provider-health evidence.

For this machine's local runtime, use `D:\NarrativForge\venv\Scripts\python.exe`; set `PATH` to include `D:\NarrativForge\venv\Scripts` and `D:\NarrativForge\ffmpeg\ffmpeg-n9.0-latest-win64-gpl-9.0\bin`; set `TEMP`/`TMP` to `D:\NarrativForge\tmp`, `PIP_CACHE_DIR` to `D:\NarrativForge\pip-cache`, `XDG_CACHE_HOME` to `D:\NarrativForge\data\cache`, `TORCH_HOME` to `D:\NarrativForge\data\cache\torch`, `PYTHONIOENCODING=utf-8`, `REDIS_URL=redis://127.0.0.1:6380/0`, `WHISPER_REMOTE_ENABLED=false`, `WHISPER_MODEL=tiny`, and `SUBTITLE_NORMALIZATION_MODE=unicode_nfc_only`. The disposable SQLite URL is `sqlite:///D:/NarrativForge/data/narrativ-forge-local-smoke.db`.

## Local deterministic worker smoke

Once preflight passes, the existing `scripts/worker_smoke.py` exercises the same canonical Celery task used by cloud worker evidence. Keep the Memurai process running. In PowerShell, set the environment variables above, set `PYTHONPATH` to the backend directory, and run the migration and existing worker with Windows' supported solo pool:

```powershell
$env:PYTHONPATH = (Get-Location).Path
& "$root\venv\Scripts\python.exe" -m alembic upgrade head
& "$root\venv\Scripts\python.exe" -m celery -A app.workers.celery_app:celery_app worker --loglevel=INFO --queues=local_media --pool=solo --concurrency=1
```

In a second terminal with the same environment, run `& "$root\venv\Scripts\python.exe" scripts\worker_smoke.py --work-dir "$data\worker\smoke"`. This creates generated synthetic media and local smoke records only. Stop the worker using Celery's remote `shutdown` control (or Ctrl+C); this does not stop or delete Memurai or its data. The checked-in smoke's tone contains no speech, so its Whisper transcript/subtitle may have no cues. Use a deterministic Unicode transcript fixture to separately verify NFC subtitle generation; do not present that fixture as a Burmese speech-recognition result. Local synthetic evidence is not provider, production, or packaged-worker verification.
