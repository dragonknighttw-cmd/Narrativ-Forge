# Narrativ Forge — Project Overview

> Owner: Project maintainers  
> Update when: product boundary, architecture, or primary runtime changes  
> Last Updated: 2026-10-08  
> Do NOT put here: detailed operational runbooks, test evidence, or the execution backlog

## What this is

Narrativ Forge is a private, invite-only Burmese short-form video production workspace. It supports Manual + Auto production with mandatory human review/approval and Google Drive export.

Core workflow:

`Idea → Series → Episode → Script Studio → Scene Breakdown → Asset Library → Video Project → Subtitle Studio → Processing Queue → Review → Approval → Google Drive Export → Publishing Preparation → Production Log → Hook / Analytics`

The application database is the workflow/version/subtitle/approval/analytics/audit source of truth. Google Drive is an approved-output destination, not the workflow database.

## Product boundaries

- Private/invite-only.
- No public registration, public profiles, public browsing/comments.
- No Logixa Flow or Aether Bridge.
- No direct TikTok/YouTube/Facebook/Instagram publishing.
- Publishing preparation, captions, hashtags, schedule metadata, format checks, manual publication records, and analytics are allowed.
- Human approval remains mandatory before final export.

## System architecture

```
Next.js + React
      ↓
FastAPI
      ↓
PostgreSQL
      ↓
Redis / delivery layer
      ↓
Worker boundary (when enabled)
  ├─ FFmpeg
  ├─ Whisper / Cloudflare Whisper
  ├─ AI adapters
  └─ export/storage adapters
      ↓
B2 / Supabase Storage / Cloudinary
      ↓
Google Drive approved-output export
```

The repository contains a Celery/Redis worker path, but production worker execution is an explicit live gate. The current free-only Render deployment does not silently provision a paid Background Worker.

## Current technology

- Frontend: Next.js 16.x line, React 19.x, TypeScript.
- UI: native CSS custom properties and reusable React primitives.
- Icons: lucide-react.
- Browser E2E: Playwright.
- Backend: FastAPI + SQLAlchemy.
- Database: PostgreSQL-compatible deployment via `DATABASE_URL`.
- Schema migrations: Alembic.
- Queue/runtime: Redis + Celery code path; deployment/runtime status is documented separately.
- AI text: Groq/OpenAI-compatible routing with deterministic Mock fallback.
- Transcription: Cloudflare Workers AI Whisper path plus worker fallback path.
- Storage: hybrid B2/Supabase/Cloudinary routing.
- Approved exports: Google Drive.
- Monitoring: Sentry integration.

Exact dependency resolution and live provider health are verification items; this document must not imply live health from credentials or code presence alone.

## Source-of-truth map

- `README.md`: concise project/current implementation map.
- `CURRENT_STATE.md`: authoritative current state and evidence status.
- `ROADMAP.md`: authoritative requirements, phases, gates, backlog, and release criteria.
- `UI_DESIGN_SYSTEM.md`: UI construction rules.
- `TOOL.md`: engineering/documentation workflow.
- `SECURITY.md`: security policy and controls.
- `docs/*`: domain-specific implementation/reference material.
