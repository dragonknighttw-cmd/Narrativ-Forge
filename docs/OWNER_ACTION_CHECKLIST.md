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
- [Cloudflare Whisper live evidence workflow](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/workflows/cloudflare-whisper-live-evidence.yml) was run at [run #37895020420](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/37895020420) and failed before authenticated inference: the unauthenticated request received HTTP 403 instead of the expected 401. The redacted artifact records the status only; the shared secret has not yet been validated by that run.

**Release is still NOT Production Ready.** Do not treat green CI or a live API as proof that production media processing works end to end.

## Step 1 — Repair and re-run Cloudflare Whisper live acceptance

The previous run [#37895020420](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/37895020420) stopped at the unauthenticated request: HTTP 403 was returned where the Worker contract expects HTTP 401. The authenticated request never ran, so this is not yet evidence that the shared secret is wrong or right.

This check uses one synthetic two-second WAV and may consume Workers AI quota. Do not run it until you explicitly approve the inference request.

1. Open **Settings → Environments → production** in the repository. Ensure these are Environment secrets:
   - `CLOUDFLARE_WHISPER_WORKER_URL` = `https://narrativ-forge-whisper.narrativ-forge.workers.dev` (exact host; no frontend URL, query string, or custom path).
   - `CLOUDFLARE_WHISPER_SHARED_SECRET` = a strong secret at least 32 characters long.
2. If the original secret is lost, treat this as a coordinated rotation—not a guess. Generate one new random value locally (for example, 32 random bytes encoded as 64 hexadecimal characters). Never send it in chat or commit it.
3. Set that **same exact value** in the Render API service's environment variable `CLOUDFLARE_WHISPER_SHARED_SECRET`. This is required because the API signs processing tokens. Keep the URL in Render's `CLOUDFLARE_WHISPER_WORKER_URL` as the same workers.dev endpoint.
4. Ensure `CLOUDFLARE_API_TOKEN` and `CLOUDFLARE_ACCOUNT_ID` are available to the protected production deployment job (repository secrets are fine; do not paste their values into logs).
5. Open **Actions → Deploy Cloudflare Whisper Worker → Run workflow**. Set `confirm_render_secret_synced` to **true** only after verifying Render API has the exact same value. This workflow is intentionally manual-only: it deploys the source and synchronizes `NARRATIV_SHARED_SECRET` from the protected GitHub `production` secret. Wait for success before continuing. If you have not updated Render, leave the input false and stop.
6. The live-evidence workflow validates the exact Worker hostname and sends the configured allowed Origin from `web-platform/cloudflare/whisper-worker/wrangler.jsonc`; it does not follow redirects. Open **Actions → Cloudflare Whisper Live Evidence → Run workflow**, select `main`, set `confirm_live_inference` to **true**, and start the run only after approving the possible Workers AI quota use.
7. Inspect the conclusion and download `cloudflare-whisper-live-evidence`. The artifact records safe status/error codes and field-presence checks only; it never stores transcript text, the signed token, or the shared secret. A pass proves only the synthetic endpoint contract—not Burmese quality, production database usage accounting, subtitle persistence, fallback, or release readiness.

If you cannot set the Render API secret yet, stop after code/config review and do not run authenticated inference. Do not share secret values in screenshots; redact them.

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


## OpenRouter free-only AI setup

1. In Render's Narrativ-Forge API service, add OPENROUTER_API_KEY using the secret manager (never paste the value into chat, source control, or logs).
2. Set OPENROUTER_BASE_URL=https://openrouter.ai/api/v1.
3. Optionally set OPENROUTER_MODELS to a comma-separated list of chat-capable free IDs from [the model audit](OPENROUTER_FREE_MODEL_AUDIT.md). Keep the :free suffix and use only IDs on the vetted allowlist; the application blocks arbitrary model IDs even if they end in :free.
4. Leave GROQ_API_KEY / OPENAI_API_KEY unused for this content-plan route; remove them from Render only after checking no other service requires them. The route itself will not call those providers.
5. After deployment, verify a single controlled content-plan request returns success and the reported provider/model is a configured free ID. Record only provider/model/status; never log the API key or prompt. Check OpenRouter key usage/limits in its dashboard.
6. Do not run a paid model as a fallback. If free endpoints are rate-limited, keep Mock fallback or retry later.

Do not mark the key verified until a real authenticated request succeeds. A configured environment variable is not proof that the key is valid or that production is using it.
