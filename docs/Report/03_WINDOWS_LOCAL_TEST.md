# Windows Local Test

**Generated:** 2026-10-12  
**Inspected repository checkpoint:** `main`, HEAD `95aa9163cc40383a8c44c3a5f445e4de899116e4`  
**Execution host:** Real Windows host, not WSL or a container, for the local subprocess test and recorded local worker smoke. The exact source SHA for the earlier worker smoke was not recorded.

## Observed prerequisites

The existing local runtime report records CPython 3.12.13 x64 in a D-drive virtual environment, FFmpeg/ffprobe, OpenAI Whisper 20250625, CPU PyTorch, the Whisper `tiny` cache, and Memurai on loopback port 6380. This describes the test machine only, not a supported packaged product or production topology.

## Safe inventory

The handoff diagnostic is outside the repository and does not read environment-file contents:

```powershell
$HandoffFolder = 'PATH_TO_HANDOFF_FOLDER'
Set-ExecutionPolicy -Scope Process Bypass
& (Join-Path $HandoffFolder 'Check-NarrativForge-Local.ps1')
```

The script may offer an optional fetch-only prompt. Review output for private paths before sharing it. Do not provide `.env` contents, tokens, cookies, or keys.

## Focused subprocess test

From the repository root:

```powershell
$RepoRoot = (git rev-parse --show-toplevel).Trim()
$LocalRoot = 'PATH_TO_LOCAL_RUNTIME_ROOT'
Set-Location (Join-Path $RepoRoot 'apps/web-platform\backend')
& (Join-Path $LocalRoot 'venv\Scripts\python.exe') -m pytest tests\test_real_processing_subprocess.py -q
```

The final full-file run passed: `6 passed, 2 skipped in 4.41s`. Before that run, the process-tree timeout test raced because its 0.2-second limit could expire before the child PID file was written. The test-only window is now 2 seconds; production processing timeouts are unchanged.

## Local media runtime evidence

The historical Windows run reports the canonical Celery task completed using local storage, SQLite, FFmpeg, Whisper, and loopback Redis-compatible service. The source SHA was not captured, so treat the result as historical evidence without exact-commit attribution. The current `tiny` transcript is not acceptable as Burmese. The original sample remained outside Git.

The previous runtime report contains a seven-check preflight and a synthetic worker smoke. Its historical logs remain in the machine-local runtime area and were not copied into this report folder.

## Not run / still needed

- Exact-SHA repeat of the canonical Windows worker run with a completed and reviewable transcript artifact.
- CI/workflows for the current edits on a committed exact SHA.
- Burmese-speaker/reference transcript review and subtitle playback review.
- Packaged offline worker/media acceptance; existing Windows package evidence is not proof of that product capability.
