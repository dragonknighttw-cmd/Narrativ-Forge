# Deployment

> Owner: Platform maintainers  
> Update when: deployment targets, runtime services, or environment configuration changes  
> Last Updated: 2026-10-08  
> Do NOT put here: secret values

## Current target

- Frontend: Netlify.
- API: Render Free Web Service.
- Database: managed PostgreSQL via `DATABASE_URL`.
- Redis/delivery: external managed service where enabled.
- Approved output: user-owned Google Drive.

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
