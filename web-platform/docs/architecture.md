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
- Authentication: development-only session skeleton; production auth/RBAC is a hardening phase

## Current API

- GET /api/v1/health
- POST /api/v1/auth/login
- GET /api/v1/auth/me
- GET/POST /api/v1/ideas
- GET/POST /api/v1/episodes

The API surface will expand in the phase order from the master plan.
