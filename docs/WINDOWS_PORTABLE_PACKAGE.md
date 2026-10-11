# Windows Portable Runtime Bundle

Status: prototype bundle gate; not a standalone installer or offline desktop release.

The Windows workflow builds the existing Next.js frontend in standalone mode, bundles the FastAPI source and launch/stop scripts, zips the result, extracts that exact ZIP into a clean temporary directory, installs API dependencies, applies SQLite migrations, starts both processes, checks API/UI health, stops and verifies process cleanup, restarts the package, and verifies that user data persists across shutdown/restart. It collects runtime logs as evidence.

## Runtime requirements

- Windows 10/11 x64
- Python 3.12 on PATH
- Node.js 20 on PATH
- Internet access on first launch to install Python dependencies

Launch the extracted bundle by running Start-NarrativForge.ps1 in PowerShell. Stop the runtime with Stop-NarrativForge.ps1. Stopping processes preserves the user's data directory.

The bundle uses SQLite and local filesystem storage. Burmese subtitle input is Unicode-only and uses Python's standard-library NFC normalization; Zawgyi detection/conversion is unsupported. This Unicode normalization contract does not by itself verify media processing or subtitle quality in the portable bundle.

## Explicit limitations

- This is a portable API/UI runtime bundle, not an MSI/EXE installer.
- Python and Node.js are prerequisites; they are not embedded.
- The Celery worker, Redis, FFmpeg, Whisper model, and offline media processing are not included.
- Cloud provider credentials and integrations are not configured by the bundle.
- The bundle is not production verified.
- A later package phase must resolve Windows media dependencies, worker lifecycle, upgrades, data migration/backup, installer/uninstaller, signing, licensing/redistribution, and full install -> media E2E -> cleanup. The current package smoke verifies API health/readiness and the frontend login route over HTTP; it does not automate a browser login or prove complete user workflows.

The workflow uploads the portable ZIP, JSON manifest, checksum, and runtime logs as evidence. Its SHA and production_verified=false marker identify exactly what was tested.
