# Narrativ Forge — Owner Action Checklist

> Last updated: 2026-10-10 (UTC; refreshed after PR #38 merge)  
> Purpose: move from repository/CI foundations to live acceptance without guessing, leaking credentials, or silently creating billable services.

## Latest main snapshot — 2026-10-10 UTC

- Current main SHA: `b75d074ab01b8f9e2ef4058dda03934eb91b3d8a` (PR #38 merge; PR #36 stale-worker recovery and PR #38 retry-exhaustion/DLQ idempotency coverage are included).
- PR #31 merged tenant-isolation negative cases for direct child-resource IDs. PR #32 merged storage lifecycle threshold/deletion-safety boundary tests (`a3ee23467ea2111e18b35523e698464d12c47024`). PR #33 merged a regression test proving asset metadata and audit history are preserved when storage-provider purge fails (`72154ae184f2316ee2c283be3184566edb91fe37`). PR #36 added stale real-processing job recovery tests; PR #38 added retry-exhaustion, failed-job/DLQ persistence, audit-event, and no-duplicate terminal-record coverage.
- PR-head checks for PR #32 and PR #33 passed, including backend, backend integration, E2E, CodeQL, Repository Gate, real-worker CI evidence, security scans, and local/Windows runtime/package smoke checks where present.
- Fresh checks on main merge SHA `b75d074ab01b8f9e2ef4058dda03934eb91b3d8a` passed: CI, Security, CodeQL, Repository Gate, Local Runtime Evidence, Real Worker Evidence, Windows Local Runtime Evidence, and Windows Portable Package Evidence.
- These changes improve automated regression coverage only. They do not establish live external-storage lifecycle/restore acceptance, a persistent production worker, authenticated real-audio Whisper inference, or full production end-to-end acceptance.
- Release status remains **PENDING — NOT PRODUCTION READY**. Do not run quota-consuming inference or provision billable worker capacity without explicit owner approval.

## Latest verified evidence snapshot

### Latest implementation change — cross-tenant negative-case coverage

- PR #29 merged as `04bfedd5a79ee6eb90eaed83517c12c48282feb8`: added integration/security regression coverage that a second tenant cannot read/update another tenant's Series or Episode, read/retry its ProcessingJob, or list its assets/scripts/scenes/subtitles through a foreign Episode ID.
- All PR #29 checks passed on head `dc50efba0fcb91aacee8b352ded5fe12f25deb78`, including [CI/E2E](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/37966621252), [Security scans](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/37966621363), [CodeQL](https://github.com/dragonknighttw-cmd/Narrativ-Forge/runs/113942806678), [Real Worker Evidence](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/37966621352), and [Repository Gate](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/37966621184).
- Fresh main-SHA checks on `04bfedd5a79ee6eb90eaed83517c12c48282feb8` are running and must be refreshed before release acceptance: [CI #1225](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/37967303768), [Security #990](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/37967303785), [CodeQL #597](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/37967303746), [Repository Gate #249](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/37967303857), [Real Worker Evidence #193](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/37967303703), [Windows Local Runtime #32](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/37967303910), and [Windows Portable Package #33](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/37967303824). [Local Runtime #35](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/37967303748) has already passed.
- This is stronger automated tenant-isolation evidence, not a substitute for a full resource-by-resource audit or production browser E2E. Gate G11 remains open until broader role/membership/cross-tenant negative cases are accepted in the target environment.


- Main SHA: `4dd3d4f0b761858c83047263a310dfa5429ab48b` (PR #26 merged). Fresh main checks all passed: [CI #1217](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/37965669315), [Security #982](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/37965669353), [CodeQL #589](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/37965669249), [Repository Gate #241](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/37965669199), [Backup Restore #8](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/37965669190), [Real Worker #191](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/37965669286), [Local Runtime #33](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/37965669461), [Windows Local Runtime #30](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/37965669304), and [Windows Portable Package #31](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/37965669256).
- PR #26 merged as `4dd3d4f`; SQLite restore verifies integrity before replacing the target. The PR's [backup/restore evidence](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/37954212710) passed on the PR SHA; this is isolated CI evidence, not a managed production restore.
- On parent SHA `b231e2d`, main [CI](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/37961092861), [Security](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/37961092885), [CodeQL](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/37961092877), and [Repository Gate](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/37961092923) passed.
- [Real Worker Evidence #190](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/37963422875) passed with synthetic media in isolated CI; no persistent production worker is deployed.
- [Cloudflare Whisper Preflight #2](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/37964550063) passed without audio or inference. Live authenticated transcription and downstream acceptance remain pending.
- [Kaggle Dispatcher #12](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/37962902195) passed config/database checks but found no due jobs and did not launch Kaggle.

**Release status remains PENDING / NOT PRODUCTION READY.**

## Current verified baseline

- Historical baseline: `adeb425185f163775f03b779553a8e148284f363` and its earlier checks are retained below for incident context; use the **Latest verified evidence snapshot** above for current status.
- [Windows portable package persistence gate](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/37889063839) passed on the immediately preceding main SHA `ee448cb82ccd4b68235c9264ac474019c961a994`. It verifies API/UI start-stop-restart and local data persistence only; it is not a standalone installer and does not include Celery/FFmpeg/Whisper.
- [Render API deployment](https://dashboard.render.com/web/srv-davrqtu7bikc73f7isbg) is live at the current main SHA. No separate background worker exists yet.
- [Cloudflare Whisper live evidence workflow](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/workflows/cloudflare-whisper-live-evidence.yml) was run at [run #37907157973](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/37907157973) on merge SHA `adeb425185f163775f03b779553a8e148284f363` and failed before authenticated inference: the unauthenticated request received HTTP 403 with `text/plain`, a Cloudflare `CF-Ray`, and no recognized Worker JSON error. This points to an edge/deployment/access-layer rejection or a different deployed handler; it does not validate or invalidate the shared secret.

**Release is still NOT Production Ready.** Do not treat green CI or a live API as proof that production media processing works end to end.

## Step 1 — Repair and re-run Cloudflare Whisper live acceptance

The latest run [#37907157973](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/37907157973) stopped at the unauthenticated request: HTTP 403 with `text/plain` and a Cloudflare `CF-Ray` was returned where the Worker contract expects HTTP 401. The authenticated request never ran. The redacted artifact now records safe response metadata and a short sanitized preview; do not treat this as a shared-secret failure.

This check uses one synthetic two-second WAV and may consume Workers AI quota. Do not run it until you explicitly approve the inference request.

1. Open **Settings → Environments → production** in the repository. Ensure these are Environment secrets:
   - `CLOUDFLARE_WHISPER_WORKER_URL` = `https://narrativ-forge-whisper.narrativ-forge.workers.dev` (exact host; no frontend URL, query string, or custom path).
   - `CLOUDFLARE_WHISPER_SHARED_SECRET` = a strong secret at least 32 characters long.
2. If the original secret is lost, treat this as a coordinated rotation—not a guess. Generate one new random value locally (for example, 32 random bytes encoded as 64 hexadecimal characters). Never send it in chat or commit it.
3. Set that **same exact value** in the Render API service's environment variable `CLOUDFLARE_WHISPER_SHARED_SECRET`. This is required because the API signs processing tokens. Keep the URL in Render's `CLOUDFLARE_WHISPER_WORKER_URL` as the same workers.dev endpoint.
4. Ensure `CLOUDFLARE_API_TOKEN` and `CLOUDFLARE_ACCOUNT_ID` are available to the protected production deployment job (repository secrets are fine; do not paste their values into logs).
5. First open **Actions → Cloudflare Whisper Preflight → Run workflow** on `main`. This is a non-billable GET-only check: no secret, audio, or Workers AI inference is used. Expected result is Worker JSON HTTP 405 with `error=Method not allowed`. If it returns HTTP 403 `text/plain` with a Cloudflare `CF-Ray`, stop: investigate Cloudflare edge/account controls, the canonical hostname, and the deployed script before attempting inference. Do not rotate secrets based on that response.
6. Open **Actions → Deploy Cloudflare Whisper Worker → Run workflow**. Set `confirm_render_secret_synced` to **true** only after verifying Render API has the exact same shared-secret value. This workflow is intentionally manual-only: it deploys the source, synchronizes `NARRATIV_SHARED_SECRET` from the protected GitHub `production` secret, then runs a non-billable GET smoke check. If Render has not been updated, leave the input false and stop.
7. Only after the preflight/deployment smoke returns the expected Worker JSON 405, open **Actions → Cloudflare Whisper Live Evidence → Run workflow**, select `main`, set `confirm_live_inference` to **true**, and start the run only after approving the possible Workers AI quota use.
8. Inspect the conclusion and download `cloudflare-whisper-live-evidence`. The artifact records safe status/error codes, response metadata, a short sanitized preview, and field-presence checks only; it never stores transcript text, the signed token, or the shared secret. A pass proves only the synthetic endpoint contract—not Burmese quality, production database usage accounting, subtitle persistence, fallback, or release readiness.

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


## Kaggle ephemeral worker — configuration follow-up

The manual dispatcher run [#37958580462](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/37958580462) received the database URL and Kaggle API token but an empty `KAGGLE_KERNEL_ID`. This proves that the value was not available through the workflow's original `vars.KAGGLE_KERNEL_ID` expression for that run; it does not prove the other two credentials are valid.

1. Open [Repository Actions secrets and variables](https://github.com/dragonknighttw-cmd/Narrativ-Forge/settings/secrets/actions).
2. Confirm there is a **repository-level Actions variable** named exactly `KAGGLE_KERNEL_ID` with value `thuwon/narrativ-forge`. If it was added under an Environment instead, it will not be available to a job that does not declare that Environment.
3. The proposed workflow also accepts a repository-level Actions secret named `KAGGLE_KERNEL_ID` as a fallback. Prefer the variable, because the identifier is not secret.
4. Keep `KAGGLE_DISPATCH_DATABASE_URL` and `KAGGLE_API_TOKEN` as Actions **secrets**. Never paste their values into chat or logs.
5. Wait for the multi-file dispatcher fix PR and its required checks before rerunning. The workflow can launch Kaggle compute when due jobs exist; rerun only when you are ready for that possible quota use.
6. Review the log for configuration preflight, database connectivity/query, Kaggle status lookup, and whether a session was actually pushed. A successful workflow or push alone is not proof that a job completed or produced valid media.

Do not run a production media job until the dispatcher configuration passes and quota/provider constraints are understood.
