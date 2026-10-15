# Local Runtime Follow-up — 2026-10-12

## Purpose

Track the handoff from the recent Windows local synthetic runtime test to the next verification steps. This document records scope and sequencing; it does not claim production acceptance.

## Latest local checkpoint

Commit: [`5d292e9584b70614608da58829da3ec13cf5f3eb`](https://github.com/dragonknighttw-cmd/Narrativ-Forge/commit/5d292e9584b70614608da58829da3ec13cf5f3eb)

- **Verified within local synthetic scope:** Unicode-only subtitle normalization using `unicode_nfc_only` and standard-library NFC; Windows/D-drive backend environment; seven preflight checks; disposable SQLite migration through `0018_tenant_backfill_guard`; canonical Celery worker task using Memurai, FFmpeg, Whisper `tiny`, and local storage; generated input/output/transcript assets persisted; deterministic Unicode transcript fixture exported to SRT.
- **Focused tests:** 10 passed.
- **Backend unit selection at the original local checkpoint:** 260 passed, 5 skipped, 103 deselected, 1 failed.
- **Follow-up resolved:** the Windows SQLite restore file-lock failure was fixed and the dedicated regression test subsequently passed on a Windows Server 2025 GitHub Actions runner. See the Windows SQLite restore section below.
- **Speech-quality limit:** the worker smoke media is a tone fixture with no speech. Its empty Whisper transcript is expected for that fixture and does not verify Burmese speech recognition. The deterministic Unicode transcript fixture verifies subtitle normalization/export only.
- **Not verified:** production provider use, real Burmese audio quality, packaged/offline desktop runtime, persistent worker operations, or full production acceptance.

## Free-tier provider smoke evidence — 2026-10-12

- [Free-tier Provider Smoke Evidence run #38198919646](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/38198919646) completed successfully on main commit `15c2db7937c0d56aa66deb6948b39ef8137eaa18`.
- Provider/model: Groq / `openai/gpt-oss-120b`.
- Result: HTTP 2xx; smoke assertion `success: true`; elapsed time 3008 ms.
- [Redacted evidence artifact](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/38198919646/artifacts/11724098077).
- Scope limit: this verifies one synthetic provider request only. It does not verify Burmese speech transcription, quality, production Render configuration, sustained capacity, or full application acceptance. Keep production provider flags disabled unless the owner separately approves a production change.

## Windows SQLite restore regression — 2026-10-12

- Root cause: `sqlite3.Connection` context-manager usage does not close the connection handle. On Windows, an open handle can block `Path.replace`.
- Fix in [`scripts/restore_db.py`](https://github.com/dragonknighttw-cmd/Narrativ-Forge/blob/main/scripts/restore_db.py): explicitly close the temporary SQLite connection before replacing the destination.
- Test fixture fix in [`test_root_restore_db.py`](https://github.com/dragonknighttw-cmd/Narrativ-Forge/blob/main/apps/web-platform/backend/tests/test_root_restore_db.py): close source/target fixture connections and provide `close()` on the integrity-check mock.
- Added the restore regression test to the Windows API + SQLite smoke workflow.
- [Windows Local Runtime Evidence run #38199416863](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/38199416863) passed on commit `644f4346f59d03b7185531e8621b26a989e502fb`, including the new Windows restore regression step.
- [Windows Portable Package Evidence run #38199416864](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/38199416864) also passed on that commit.
- [Real Worker Evidence run #38199416934](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/38199416934) passed on that commit, covering the repository's ephemeral real-worker integration workflow. This is not proof of a continuously running production worker or live provider/media quality.

## CI checks for the restore fix

On commit `644f4346f59d03b7185531e8621b26a989e502fb`:
- [CI #38199416954](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/38199416954) — passed (backend, backend integration, frontend, E2E).
- [Security #38199417025](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/38199417025) — passed.
- [CodeQL #38199416987](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/38199416987) — passed.
- [Backup Restore Evidence #38199417034](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/38199417034) — passed.
- [Application Schema Restore Evidence #38199275727](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/38199275727) — passed on the preceding restore-fix commit `576138c2aeb01080b2d02456fc802aa1a4b7b196`.
- [Local Runtime Evidence #38199416923](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/38199416923) — passed.
- [Repository Gate #38199417001](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/38199417001) — passed.
- [Real Worker Evidence #38199416934](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/38199416934) — passed.

## Next steps — free-first

1. Keep the successful Groq request as provider smoke evidence; do not repeat requests unnecessarily or infer Burmese transcription quality from this smoke.
2. The restore-fix commit and documentation commit checks passed as recorded in the links above; the latest documentation-only commit was separately checked by CI, Repository Gate, Security, and CodeQL.
3. Test a real, owner-approved Burmese speech sample and perform human quality review without uploading private material unintentionally.
4. Continue packaged Windows runtime install/launch/shutdown verification and end-to-end processing with explicitly configured storage.
5. Keep production Render provider flags disabled unless the owner explicitly approves production configuration changes. GitHub Actions secrets do not configure Render.
6. Continue remaining operational/recovery, OAuth/Drive, SMTP, Stripe, Sentry, load/performance, accessibility, legal/compliance, and external security acceptance gates.

## Unicode policy

Narrativ Forge uses Unicode Burmese only. Use standard Unicode text and NFC normalization where applicable. Zawgyi detection and conversion are unsupported; do not introduce Zawgyi conversion dependencies or claim that Zawgyi input is automatically detected or converted.

## Release status

**PENDING — NOT PRODUCTION READY.** Local synthetic worker evidence is useful progress, but it is not a substitute for the remaining live-provider, real-media, package, operational, security, and acceptance gates.


## Security hardening follow-up — 2026-10-12

Latest application-code checkpoint: [`b374df9e1e455e35eaa9847d78fb7c9af70f2393`](https://github.com/dragonknighttw-cmd/Narrativ-Forge/commit/b374df9e1e455e35eaa9847d78fb7c9af70f2393).

- [CI #38201576482](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/38201576482), [Security #38201576514](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/38201576514), [CodeQL #38201576494](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/38201576494), and [Repository Gate #38201576503](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/38201576503) passed on that exact SHA.
- [Real Worker Evidence #38201576538](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/38201576538), [Windows Portable Package Evidence #38201576528](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/38201576528), [Windows Local Runtime Evidence #38201576459](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/38201576459), and [Local Runtime Evidence #38201576477](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/38201576477) also passed.
- Whisper Worker inference errors are now generic to clients; contract tests verify provider diagnostics are not exposed and invalid processing tokens are rejected before inference.
- Webhook destination validation now rejects malformed ports, URL-embedded credentials, DNS resolution errors or empty answers, and non-global addresses among resolved results. This reduces exposure to unsafe destinations but is not full DNS-rebinding protection because the HTTP connection is not pinned to the validated IP.
- These are source/CI checks only. They do not verify real Burmese audio quality, continuous production worker uptime, or managed production disaster recovery.

## Remaining acceptance gates — unchanged

- Human review of an owner-approved real Burmese speech sample.
- Continuous worker monitoring/recovery and managed storage/database restore drill.
- OAuth/Drive, SMTP, Stripe, Sentry, load/performance, accessibility, legal/privacy and external security acceptance.
- Production provider flags remain disabled unless the owner explicitly approves a change.

**Release status: PENDING — NOT PRODUCTION READY.**
