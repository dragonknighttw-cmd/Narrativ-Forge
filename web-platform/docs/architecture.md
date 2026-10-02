# Narrativ Forge Foundation

## Source of truth

The implementation follows Narrativ Forge Final Master Plan v4.0.

Core workflow:

`Idea → Structure → Script → Assets → Processing → Subtitle → Review → Output`

Human approval is required before Drive export.

## Repository boundaries

```
web-platform/
├── frontend/   # Next.js UI
├── backend/    # FastAPI API + domain/data foundation
└── docs/       # implementation documentation
mobile/         # reserved mobile workspace
```

## Foundation decisions

- Frontend: Next.js
- Backend: FastAPI
- Local database: SQLite with SQLAlchemy models designed for PostgreSQL migration
- Heavy work: worker boundary reserved; not executed inside frontend/API
- Storage: local filesystem adapter comes later
- AI/transcription/media/Drive: mock-first integration points before real providers
- Authentication: invite-only development session using an httpOnly cookie
- Authorization: backend dependency includes a reusable role guard; production roles and invite management are hardening work
- CORS: explicit origin allowlist with credentials enabled for the development frontend
- Client token storage: not used

## Current API

- GET /api/v1/health
- POST /api/v1/auth/login
- POST /api/v1/auth/logout
- GET /api/v1/auth/me
- GET/POST /api/v1/ideas
- GET/POST /api/v1/episodes

## Verification

Backend foundation tests live in `backend/tests/test_foundation.py` and cover health, login cookie behavior, authentication rejection, and authenticated identity.

Frontend has an explicit `typecheck` script. Runtime installation/build verification still needs to be run in a real developer/CI environment with Node and Python dependencies installed.

## Phase 2 — Content structure

The second vertical slice now covers Ideas → Series → Seasons → Episodes. FastAPI owns validation and status transitions; Next.js owns forms, lists, detail views, and user-facing error/empty states.

Episode structure enforces the source requirements: an episode must reference an existing series; an optional season must belong to that series; target duration is required; and episode numbers cannot duplicate within a season. Status transitions follow the documented workflow and revision transitions.

## Phase boundary

Phase 1 establishes the application boundary, development auth/session pattern, database/API foundation, protected workspace shell, configuration examples, and verification scaffolding.

Phase 2 begins the real content workflow: Ideas → Series → Seasons → Episodes CRUD end-to-end.
