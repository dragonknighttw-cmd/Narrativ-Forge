# Narrativ Forge

[![Repository Gate](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/workflows/repository-gate.yml/badge.svg)](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/workflows/repository-gate.yml)\n
Private, invite-only Burmese short-form video production workspace.

> Owner: Project maintainers  
> Update when: project boundary, current implementation, deployment topology, or release blockers change  
> Last Updated: 2026-10-08  
> Do NOT put here: detailed domain specifications, full runbooks, or duplicate roadmaps

## What it is

Narrativ Forge supports:

`Idea → Series → Episode → Script → Scenes → Assets → Processing → Subtitles → Review → Approval → Google Drive Export → Publishing Preparation → Analytics`

Human approval is mandatory before final export. Google Drive is an approved-output destination, not the workflow database.

## Boundaries

- Invite-only/private.
- No public registration/profiles/browsing/comments.
- No Logixa Flow or Aether Bridge.
- No direct TikTok/YouTube/Facebook/Instagram publishing.
- Publishing preparation and manual publication records are allowed.

## Current implementation

Implemented/foundation work includes the core Next.js/FastAPI workflow, authentication/security foundations, tenant scoping, scripts/scenes/assets, upload safety, processing/Celery foundations, Burmese subtitles, review/approval, Drive export foundations, hybrid storage, analytics, billing/webhooks, AI routing/orchestration, Auto Production 13–17 foundations, and reusable UI primitives/tokens.

## Current deployment model

| Layer | Current target |
|---|---|
| Frontend | Netlify |
| API | Render Free Web Service |
| Database | PostgreSQL via `DATABASE_URL` |
| Queue/delivery | External Redis/delivery services where configured |
| Raw/large media | Backblaze B2 |
| Small workflow files | Supabase Storage |
| Images/previews | Cloudinary |
| Approved exports | User-owned Google Drive |
| Transcription | Cloudflare Workers AI Whisper path + worker fallback |

The current Render blueprint intentionally provisions the API web service only. A paid Render Background Worker is not silently provisioned.

## Storage routing

- Raw video/audio/large media → B2.
- Small images/thumbnails/previews → Cloudinary.
- SRT/manifests/small workflow files → Supabase Storage.
- Temporary development files → local storage.
- Approved final output → Google Drive.

Application routing code is authoritative over simplified legacy documentation.

## AI

Current text-provider architecture supports Groq/OpenAI-compatible providers with deterministic Mock fallback. Cloudflare Workers AI Whisper is a separate transcription path.

**Code-configured is not live-verified.** Provider health, limits, terms, quality, commercial-use status, and real-media behavior require evidence.

## Production status

**Not Production Ready.**

The main blockers are:
- real worker + representative media;
- queue → worker → FFmpeg/Whisper → DB/storage;
- retry/DLQ/failover;
- real B2/Supabase/Cloudinary lifecycle;
- real Whisper/fallback;
- Google OAuth/Drive export/recovery;
- SMTP;
- Stripe;
- Sentry;
- backup/restore;
- production auth/tenant E2E;
- full E2E;
- load/performance;
- security/container scans;
- accessibility/responsive review;
- legal/compliance;
- external penetration testing.

## Documentation

Read in this order:

1. `README.md` — concise project map.
2. `CURRENT_STATE.md` — current status/evidence.
3. `ROADMAP.md` — master requirements and execution plan.
4. `UI_DESIGN_SYSTEM.md` — UI rules.
5. `TOOL.md` — engineering/documentation workflow.
6. `SECURITY.md` — security policy.
7. `docs/*` — domain references.

Canonical domain documents:

- `docs/ARCHITECTURE.md`
- `docs/DEVELOPMENT.md`
- `docs/TESTING.md`
- `docs/DEPLOYMENT.md`
- `docs/OPERATIONS.md`
- `docs/DATABASE.md`
- `docs/API.md`
- `docs/AI_RAG.md`
- `docs/STORAGE.md`
- `docs/TROUBLESHOOTING.md`

## Development

Frontend:

```bash
cd web-platform/frontend
npm install
npm run dev
npm run typecheck
npm run build
npm run e2e
```

Backend:

```bash
cd web-platform/backend
python -m venv .venv
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
pytest
```

Exact environment requirements belong in deployment/development documentation. Never commit credentials.

## Evidence rule

- DONE = repository implementation evidence.
- VERIFIED = fresh environment/provider evidence.
- VERIFY/PENDING/BLOCKED = evidence or dependency remains.
- DEFERRED = intentionally postponed.
- NEXT = next execution target.

Never claim provider health from credentials alone. Never claim live integration from unit tests alone.
