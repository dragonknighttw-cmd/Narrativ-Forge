# Narrativ Forge — Owner Action Checklist

> Last updated: 2026-10-09  
> Purpose: move from repository/CI foundations to live acceptance without guessing, leaking credentials, or silently creating billable services.

## Current verified baseline

- Repository main at the latest checkpoint: `b67d4620038cb9207180a737815fc0a1213ee6ca`.
- Current-head GitHub CI, Security, CodeQL, and Repository Gate are green:
  - [CI](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/37889515865)
  - [Security](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/37889515817)
  - [CodeQL](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/37889515813)
  - [Repository Gate](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/37889515819)
- [Windows portable package persistence gate](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/37889063839) passed on the immediately preceding main SHA `ee448cb82ccd4b68235c9264ac474019c961a994`. It verifies API/UI start-stop-restart and local data persistence only; it is not a standalone installer and does not include Celery/FFmpeg/Whisper.
- [Render API deployment](https://dashboard.render.com/web/srv-davrqtu7bikc73f7isbg) is live at the current main SHA. No separate background worker exists yet.
- [Cloudflare Whisper live evidence workflow](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/workflows/cloudflare-whisper-live-evidence.yml) is manual-only and has not been run at this checkpoint.

**Release is still NOT Production Ready.** Do not treat green CI or a live API as proof that production media processing works end to end.

## Step 1 — Run the Cloudflare Whisper live acceptance check

This step uses one synthetic two-second WAV and may consume Workers AI quota. Run it only when you approve that cost.

1. Open the repository: https://github.com/dragonknighttw-cmd/Narrativ-Forge
2. Go to **Settings → Environments → production**. Create the environment if it does not exist.
3. Add these as **Environment secrets** (not repository files, not Actions variables):
   - `CLOUDFLARE_WHISPER_WORKER_URL` — `https://narrativ-forge-whisper.narrativ-forge.workers.dev`
   - `CLOUDFLARE_WHISPER_SHARED_SECRET` — the exact shared secret configured as the Cloudflare Worker's `NARRATIV_SHARED_SECRET` secret.
4. Never paste the secret into chat, an issue, a commit, a workflow log, or this document. Do not rotate the live Worker secret only for this test unless you also update the matching API/worker configuration.
5. Open **Actions → Cloudflare Whisper Live Evidence → Run workflow**.
6. Select branch `main`, set `confirm_live_inference` to **true**, and start the run.
7. Open the run and download the `cloudflare-whisper-live-evidence` artifact. Check the run conclusion and that the manifest records a matching provider/episode and successful unauthenticated rejection. The workflow intentionally does not save the transcript, signed token, or secret.
8. Record the run URL and tested SHA in the release evidence ledger. A pass proves only the signed endpoint contract with synthetic audio—not Burmese quality, production database usage accounting, subtitle persistence, fallback, or release readiness.

If the secret is not available to you, stop here and retrieve it from the Cloudflare secret manager/dashboard. Do not generate a replacement blindly.

## Step 2 — Decide how to host the continuous media worker

The API web service and Celery worker are separate processes. The existing Render API service is free and must not be converted into a fake worker.

### Option A: paid Render Background Worker

Only do this after you explicitly approve ongoing compute charges.

1. Open the [Render dashboard](https://dashboard.render.com/web/srv-davrqtu7bikc73f7isbg) and the connected workspace.
2. Use the repository's `render.worker.yaml` as the configuration reference. The blueprint is deliberately separate from the free-only `render.yaml`.
3. Create a separate **Background Worker** service from repository `dragonknighttw-cmd/Narrativ-Forge`, branch `main`, root directory `web-platform/backend`, Dockerfile `Dockerfile.worker`.
4. Choose a plan with enough RAM/disk for FFmpeg and the selected Whisper model. Do not assume the lowest plan can run `WHISPER_MODEL=small`; verify resource usage first. Begin with one worker and concurrency 1.
5. Configure at least:
   - `APP_ENV`
   - `DATABASE_URL` — same production/staging PostgreSQL target as the API, never a local/CI URL
   - `REDIS_URL` — reachable persistent Redis/queue endpoint
   - `SESSION_SECRET` if required by the shared settings loader
   - storage provider and credentials for the provider selected for real job inputs/outputs
   - `CLOUDFLARE_WHISPER_WORKER_URL` and `CLOUDFLARE_WHISPER_SHARED_SECRET` only if Cloudflare fallback is enabled
   - any other environment variables for features you actually enable
6. Keep credentials in the Render environment settings. Do not commit a populated YAML file.
7. Before submitting real user media, check worker logs for a successful Redis connection and Celery `ready` state, confirm PostgreSQL access, and verify that storage can write/read an object.
8. Run a small controlled media job, then test retries/DLQ and cleanup. Save exact deployment ID, SHA, log/evidence URL, and timestamp.

### Option B: defer paid compute

If you want to stay free-only, do not create the Render worker yet. Use the existing local/ephemeral worker evidence workflow for code/runtime verification, and treat production asynchronous processing as blocked. Kaggle or another ephemeral runner is not equivalent to a continuously available production worker unless its dispatch, credentials, shutdown, retries, and recovery behavior have been explicitly verified.

## Step 3 — Verify backup/restore evidence

1. Open [Backup Restore Evidence](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/workflows/backup-restore-evidence.yml).
2. Run it manually on `main` if no fresh run exists for the SHA you are accepting.
3. Confirm it passes and download the `backup-restore-evidence` artifact.
4. This test uses an ephemeral PostgreSQL 16 service. It is not a restore drill against the real managed production database. A production/staging restore drill needs a separately approved target, access, retention plan, and rollback/cleanup procedure.

## Step 4 — Verify the Windows portable package

1. Open [Windows Portable Package Evidence](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/workflows/windows-portable-package.yml).
2. Run it on `main` after package/workflow changes and inspect the uploaded `windows-portable-package-evidence` artifact.
3. Confirm the artifact SHA matches the accepted commit. The package still requires Python 3.12, Node.js 20, and internet access for first-time dependency installation.
4. Do not distribute it as an installer. The current ZIP excludes the background worker, FFmpeg/Whisper, and ICU-dependent Burmese processing.

## Step 5 — Close the remaining release gates in order

1. Continuous worker + real media pipeline.
2. Retry, DLQ, duplicate dispatch, worker-loss recovery.
3. Authenticated Whisper + VTT correctness + fallback + subtitle persistence.
4. Live storage lifecycle for each enabled provider (upload, download, delete/archive).
5. Production/staging multi-tenant browser E2E.
6. Managed-database backup/restore and exact Alembic head.
7. SMTP, Google Drive OAuth/export/recovery, Stripe test checkout/webhook, and Sentry event/alert—each in its own controlled test.
8. Security/dependency/container scans, load/performance, accessibility/WCAG, legal/privacy review, independent penetration test, and provider terms/commercial-use review.
9. Only after evidence is attached should a gate be marked VERIFIED. Record the exact SHA, run/deploy ID, environment, scope, result, timestamp, and artifact.

## Safe handling rules

- Never send secret values in chat or commit them.
- Do not run quota-consuming or billable steps without owner approval.
- Do not test destructive operations against production data.
- Do not mark a code-only test as a live-provider pass.
- Keep `production_verified: false` on synthetic/local evidence.
