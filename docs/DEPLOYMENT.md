# Deployment

> Owner: Platform maintainers  
> Update when: deployment targets, runtime services, or environment configuration changes  
> Last Updated: 2026-10-09  
> Do NOT put here: secret values

## Current target

- Frontend: Netlify.
- API: Render Free Web Service.
- Database: managed PostgreSQL via `DATABASE_URL`.
- Redis/delivery: external managed service where enabled.
- Approved output: user-owned Google Drive.

### Current repository/deployment checkpoint — 2026-10-09

- Repository main SHA: `b67d4620038cb9207180a737815fc0a1213ee6ca`.
- Render deployment `dep-db47rg0ae00c739pgs90` is live at that SHA: [Render deploy](https://dashboard.render.com/web/srv-davrqtu7bikc73f7isbg).
- Current-head GitHub checks are green: [CI](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/37889515865), [Security](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/37889515817), [CodeQL](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/37889515813), and [Repository Gate](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/37889515819).
- Windows portable package persistence passed on the immediately preceding main SHA `ee448cb82ccd4b68235c9264ac474019c961a994`; it is still a prototype API/UI bundle, not an installer or media-worker package.
- No separately provisioned continuous background worker exists. Production media processing remains blocked.
- Cloudflare Whisper live evidence run [#37895020420](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/37895020420) failed before authenticated inference: the unauthenticated POST returned HTTP 403 instead of the expected 401. Treat the endpoint contract as unverified until a fresh run passes.
- Owner steps and secret-handling instructions: [Owner Action Checklist](OWNER_ACTION_CHECKLIST.md).

The 2026-10-08 live health/readiness observations below are historical evidence for that date; do not treat them as a fresh HTTP probe of every later deployment.

### Live evidence checkpoint — 2026-10-08

The Render service `Narrativ-Forge` is live from `main` and its latest live deploy is commit `1369d9a3e4d8896cf6024fa45fa6810cc3cee890`.

- API: https://narrativ-forge.onrender.com
- Health: https://narrativ-forge.onrender.com/api/v1/health
- Readiness: https://narrativ-forge.onrender.com/api/v1/ready
- Render service: https://dashboard.render.com/web/srv-davrqtu7bikc73f7isbg
- Release commit: https://github.com/dragonknighttw-cmd/Narrativ-Forge/commit/1369d9a3e4d8896cf6024fa45fa6810cc3cee890

At verification time, health returned HTTP 200 with `status=ok`. Readiness returned HTTP 200 with database=`ok` and redis=`ok`. Render logs also show the live instance running `alembic upgrade head` against PostgreSQL followed by successful Uvicorn startup.

The exact live Alembic revision is still VERIFY because startup connectivity/logs do not independently report the final revision.

## Worker options

The repository contains a Celery worker path and an ephemeral Kaggle worker path. A local Windows worker is also a documented free-first fallback.

Paid Render Background Worker/VPS is reserved for future use unless explicitly approved.

The current Render account has one Narrativ Forge web service and no separately provisioned Render Background Worker. Therefore API deployment is verified, but real background media execution remains a release gate.

## Free-first deployment decisions

- `CELERY_ENABLED=false` is the documented free-first deployment default.
- Celery/Redis is optional in the free-first API deployment.
- QStash durable delivery is used where configured.
- Vercel override has been removed from the intended deployment path; any re-enable requires explicit owner authorization.

## Cloudflare Whisper

The Whisper Worker is deployed separately.

Live verification on 2026-10-08 confirmed:
- Worker name: `narrativ-forge-whisper`.
- Wrangler deployment exists with a 100% production version created 2026-10-07.
- `NARRATIV_SHARED_SECRET` is bound as a Worker secret.
- workers.dev subdomain is enabled.
- Live endpoint: https://narrativ-forge-whisper.narrativ-forge.workers.dev
- A live request without POST/authentication returned the expected method guard response.

Real authenticated audio → Whisper → VTT → Subtitle Studio E2E and fallback behavior remain VERIFY.

## Environment

Protected configuration belongs in the deployment secret manager. Never document secret values.

## Deployment verification

Verify exact deployment target, health/readiness, database migration state, Redis/delivery connectivity, worker runtime if enabled, storage, external integrations, and rollback/smoke/full-content checks.

A manifest is not proof of a live deployment.

## Background worker close-out — 2026-10-08

**Status: BLOCKED pending owner provisioning.**

The repository worker is deployable as a Docker background worker:

- Dockerfile: `web-platform/backend/Dockerfile.worker`
- Command: `celery -A app.workers.celery_app:celery_app worker --loglevel=INFO --beat` (concurrency is configured by `WORKER_MAX_CONCURRENCY`, default `1`)
- Broker: `REDIS_URL`
- State: `DATABASE_URL`
- Media runtime: FFmpeg + OpenAI Whisper
- Concurrency default: 1

The connected Render service is currently a **Free web service**. Render documents Free instances for web services/Postgres/Key Value, while background-worker compute is a paid service type. citeturn0search1turn0search0turn0search4

Prepared, intentionally non-auto-provisioning blueprint:
`render.worker.yaml`

Required owner action:
1. Create a paid Render Background Worker named `narrativ-forge-worker`.
2. Use `web-platform/backend/Dockerfile.worker`.
3. Set the variables in `render.worker.yaml`.
4. Keep concurrency at 1 for the first real-media verification.
5. Verify Celery worker heartbeat/queue consumption before sending production media.

Render background workers are explicitly designed for queue-based asynchronous media processing and support Celery. citeturn0search6

### Alternative runtime: Railway

Railway can deploy a GitHub repository or Dockerfile as an independent service. citeturn0search9turn0search15

Exact worker setup:
- Source: `dragonknighttw-cmd/Narrativ-Forge`, branch `main`
- Root directory: `web-platform/backend`
- Dockerfile: `Dockerfile.worker`
- Start command: `celery -A app.workers.celery_app:celery_app worker --loglevel=INFO --concurrency=1 --beat`
- Required runtime variables: `DATABASE_URL`, `REDIS_URL`, storage credentials, Cloudflare Whisper variables, and any enabled notification/provider credentials.
- Verification: service logs show Celery worker connected to Redis and accepting tasks.

### Alternative runtime: Fly.io

Fly supports separate process groups and explicitly documents Celery workers as a worker process group. citeturn1search1

Exact worker setup:
- Build the same `Dockerfile.worker`.
- Define a `worker` process group with the Celery command.
- Provide `DATABASE_URL` and `REDIS_URL` plus enabled storage/provider secrets.
- Run one worker first; scale only after media E2E evidence.
- Keep HTTP routing limited to the web process group.

Fly charges provisioned compute by usage; this is not a free-only assumption. citeturn1search7

 
## Cloudflare Whisper live acceptance and secret rotation

The manual workflow `.github/workflows/cloudflare-whisper-live-evidence.yml` verifies the signed-token contract with one synthetic two-second WAV. It checks the canonical workers.dev hostname, sends the allowed Origin configured in `web-platform/cloudflare/whisper-worker/wrangler.jsonc`, does not follow redirects, checks unauthenticated rejection, then performs one authenticated inference. The inference may consume Workers AI quota, so run it only with explicit owner approval.

**Latest observed result:** [run #37895020420](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/37895020420) failed at the first unauthenticated request with HTTP 403 instead of 401. Authenticated inference was not reached; the shared secret was not tested by that run.

These three values must match for production token signing/verification:
- GitHub Environment secret `production/CLOUDFLARE_WHISPER_SHARED_SECRET`
- Cloudflare Worker secret `NARRATIV_SHARED_SECRET`
- Render API environment variable `CLOUDFLARE_WHISPER_SHARED_SECRET`

The original Worker secret cannot be recovered from the binding list. If lost, generate one new strong value and set it consistently in GitHub `production` and the Render API service, then manually run **Deploy Cloudflare Whisper Worker** with `confirm_render_secret_synced=true` to synchronize the Worker secret from the protected GitHub environment. Do not confirm until Render API is updated. That deploy workflow is manual-only to prevent an ordinary source/workflow push from silently rotating production credentials. Keep `CLOUDFLARE_WHISPER_WORKER_URL` set to `https://narrativ-forge-whisper.narrativ-forge.workers.dev` in both GitHub and Render.

The evidence artifact stores safe status/error codes, provider/model metadata, the synthetic fixture hash, and field-presence checks. It does not save transcript text, the signed token, or secret values. A pass verifies only the synthetic endpoint contract—not Burmese transcription quality, full video processing, production database usage accounting, fallback, subtitle persistence, or release readiness.


## AI text generation — free-only OpenRouter

The content-plan route is intentionally configured to use only OpenRouter free model variants. Set OPENROUTER_API_KEY on the Render API service and keep OPENROUTER_BASE_URL=https://openrouter.ai/api/v1. OPENROUTER_MODELS accepts a comma-separated ordered fallback list, but runtime filtering allows only an explicit allowlist of vetted chat-capable IDs from the owner’s list or exactly openrouter/free; arbitrary IDs ending in :free are rejected too. The route does not call Groq or OpenAI even if those keys remain configured. With no OpenRouter key or no allowed models, it uses deterministic Mock AI rather than a paid provider.

Default list: google/gemma-4-31b-it:free,cohere/north-mini-code:free,nvidia/nemotron-3-super-120b-a12b:free,liquid/lfm-2.5-2.6b:free. The dynamic openrouter/free router is allowed only when explicitly configured because it can choose a different free model at runtime.

Free endpoints can be rate-limited or unavailable; failover is only across the explicitly configured free IDs. A :free model endpoint is zero-priced according to OpenRouter's current listing, but provider terms/privacy may permit prompt logging or training. Do not send credentials, secrets, personal data, or confidential production content to trial/free models. Free status and model availability can change, so re-check OpenRouter's official model page before changing the allowlist.

The current production key's validity and runtime behavior are **not verified by code inspection alone**. After the change is merged and OPENROUTER_API_KEY is set in Render, run a controlled health/AI smoke test that records only status, model ID, and success—not the key or prompt contents. Do not add paid model IDs to recover from rate limits.
