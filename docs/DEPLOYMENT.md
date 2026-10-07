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

The current Render blueprint intentionally provisions the API web service only. It does not silently add a paid Render Background Worker.

## Worker options

The repository contains a Celery worker path and an ephemeral Kaggle worker path. A local Windows worker is also a documented free-first fallback.

Paid Render Background Worker/VPS is reserved for future use unless explicitly approved.

## Free-first deployment decisions

- `CELERY_ENABLED=false` is the documented free-first deployment default.
- Celery/Redis is optional in the free-first API deployment.
- QStash durable delivery is used where configured.
- Vercel override has been removed from the intended deployment path; any re-enable requires explicit owner authorization.

## Cloudflare Whisper

The Whisper Worker is deployed separately. Render must point to the deployed Worker URL and shared-secret configuration. Real audio E2E remains a release gate.

## Environment

Protected configuration belongs in the deployment secret manager. Never document secret values.

## Deployment verification

Verify exact deployment target, health/readiness, database migration state, Redis/delivery connectivity, worker runtime if enabled, storage, external integrations, and rollback/smoke/full-content checks.

A manifest is not proof of a live deployment.
