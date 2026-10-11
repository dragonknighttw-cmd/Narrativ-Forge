# Local Runtime Follow-up — 2026-10-12

## Purpose

Track the handoff from the recent Windows local synthetic runtime test to the next verification steps. This document records scope and sequencing; it does not claim production acceptance.

## Latest local checkpoint

Commit: [`5d292e9584b70614608da58829da3ec13cf5f3eb`](https://github.com/dragonknighttw-cmd/Narrativ-Forge/commit/5d292e9584b70614608da58829da3ec13cf5f3eb)

- **Verified within local synthetic scope:** Unicode-only subtitle normalization using `unicode_nfc_only` and standard-library NFC; Windows/D-drive backend environment; seven preflight checks; disposable SQLite migration through `0018_tenant_backfill_guard`; canonical Celery worker task using Memurai, FFmpeg, Whisper `tiny`, and local storage; generated input/output/transcript assets persisted; deterministic Unicode transcript fixture exported to SRT.
- **Focused tests:** 10 passed.
- **Backend unit selection:** 260 passed, 5 skipped, 103 deselected, 1 failed.
- **Known interrupted/deferred item:** `tests/test_root_restore_db.py::test_sqlite_restore_replaces_target_only_after_integrity_check` reported Windows `WinError 32` because a SQLite file handle remained open during `Path.replace`. Keep this tracked as a separate follow-up; do not treat it as fixed by the local runtime work.
- **Speech-quality limit:** the worker smoke media is a tone fixture with no speech. Its empty Whisper transcript is expected for that fixture and does not verify Burmese speech recognition. The deterministic Unicode transcript fixture verifies subtitle normalization/export only.
- **Not verified:** production provider use, real Burmese audio quality, packaged/offline desktop runtime, persistent worker operations, or full production acceptance.

## Current GitHub Actions status for this commit

At the last check, the following were still running:
- [Real worker E2E](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/38161178749)
- [Repository Gate](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/38161178716)

The other reported checks on this SHA had completed successfully, including backend, frontend, backend integration, E2E, security scans, CodeQL, Windows API + SQLite smoke, package smoke, schema-restore smoke, and local API + SQLite smoke. Recheck the exact commit checks before describing the full gate as green.

## Next steps — free-first

1. **Owner action:** add `GROQ_API_KEY` as a GitHub Actions repository secret using GitHub Settings → Secrets and variables → Actions. Create the key in the official [Groq console](https://console.groq.com/keys). Never put the key in a commit, issue, artifact, or chat.
2. Confirm the intended smoke model is currently available to the account on a free tier before selecting the workflow's free-tier confirmation. A model name or an API key alone does not guarantee free usage.
3. Once the free-tier eligibility is confirmed and the manual workflow is available on the default branch, run exactly one Groq smoke request. Inspect the redacted result artifact; do not log the key or generated response text.
4. Keep production Render provider flags disabled until the controlled smoke succeeds and the owner explicitly approves any production configuration change. The GitHub Actions secret does not configure Render.
5. After provider smoke, resume the remaining acceptance work in separate gates: real Burmese speech sample and human quality review; packaged Windows runtime/install/launch/shutdown; full end-to-end processing with real configured storage; and operational/recovery checks.
6. Revisit the Windows SQLite restore file-lock failure separately. It is not a blocker to documenting the local worker smoke, but it remains an open test failure.

## Unicode policy

Narrativ Forge uses Unicode Burmese only. Use standard Unicode text and NFC normalization where applicable. Zawgyi detection and conversion are unsupported; do not introduce Zawgyi conversion dependencies or claim that Zawgyi input is automatically detected or converted.

## Release status

**PENDING — NOT PRODUCTION READY.** Local synthetic worker evidence is useful progress, but it is not a substitute for the remaining live-provider, real-media, package, operational, security, and acceptance gates.
