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

Use `web-platform/backend/.env.example` as the reference for all settings. Never copy production credentials into a local .env file or commit secrets.

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
