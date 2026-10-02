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


## Phase 3 domain slice

The script/scene/asset slice follows the master data model:

- scripts: version records per episode with one current version.
- scenes: ordered per episode, optionally linked to an episode script.
- assets: local upload records with version, MIME type, size, copyright state, and optional scene mapping.
- Processing remains adapter-ready: Phase 2's mock job closes the Month 2 exit gate; real FFmpeg/Whisper workers remain later integration work.

Upload safety is enforced server-side with MIME + extension allow-lists, a configurable size limit, sanitized filenames, and episode/scene ownership checks. Original files are stored separately from future processing outputs.


## Phase 4 — Processing Engine

Week 8 closes the processing boundary with a local mock worker before real FFmpeg/Whisper integration. A processing job is persisted independently from the API request, moves through queued/running/completed or failed, and preserves error codes/messages for retry. The worker copies the source into a separate processing output asset and emits a mock Burmese transcript JSON asset. The source asset is never overwritten.

The API exposes job creation, listing, detail, and retry. The frontend Processing Queue surfaces progress, failure, and retry states. Real FFmpeg/Whisper adapters remain a later integration step, consistent with the source plan's mock-first approach.


## Phase 5 — Subtitle Studio

Week 9/10 closes the subtitle boundary around the transcript produced by the processing layer. The current transcript asset is converted into a versioned subtitle record with editable cues, Burmese language metadata, and a selected preset.

Subtitle validation checks missing cue text, invalid or overlapping timing, the default 1–7 second display window, Burmese text presence, line count, and preset character limits. Draft subtitles may contain validation issues for editing, but approval is blocked until the current version passes the quality gate. Approved versions cannot be edited in place.

SRT and VTT are generated from the same cue data so exports remain deterministic. The Subtitle Studio exposes generation, cue editing, save, validation, approval, and SRT/VTT export actions. Real Whisper transcription remains behind the existing processing integration boundary; Phase 5 consumes the transcript asset without replacing the mock-first worker prematurely.


## Phase 6 — Review, Approval, and Drive Export

The Review Center is the human quality gate between subtitle review and final output. The checklist covers full-video review, audio, subtitle timing, and thumbnail presence; unresolved critical issues or subtitle validation errors block approval. Requesting revision moves the episode back to production. Final approval marks the latest processed video as the final asset while preserving the original/source asset.

Drive export has two providers. Mock Drive is the deterministic local integration used for development and tests; it writes to isolated mock storage and records an export manifest. Google Drive is a real provider boundary using OAuth with the narrow drive.file scope. Refresh/access tokens are stored server-side in encrypted form and are never returned to the frontend. Real export creates an episode folder and uploads the final video, SRT subtitle, and JSON export manifest. Existing completed exports are returned without duplicating files.

Google credentials and the OAuth encryption key are environment-only settings. If they are not configured, the UI exposes the Drive connection as disconnected rather than pretending export is available.


## Phase 7 — Production Intelligence

Hook Library, Manual Production Log, Publishing Preparation, and Social Analytics are first-class application data. The Hook Library records reusable hook text/type and observed performance fields. Manual logs preserve the manual workflow as structured learning data. Publishing preparation stores captions, hashtags, schedule metadata, platform-format status, and explicit publishing states; the application never claims a platform publication without a user-provided publication record.

Social analytics are recorded separately from publishing preparation so imported/manual metrics remain attributable to a publication. App Analytics summarizes production and social records without automatically changing hook defaults. This keeps the feedback loop human-controlled as required by the source plan.

## Phase 8 — Hardening Boundary

Upload validation remains server-side with MIME/extension checks, bounded streaming writes, filename sanitization, and path-safe storage names. Frontend controls expose keyboard focus states and responsive analytics cards.

Google Drive export now persists remote folder/video IDs before subsequent uploads and checks for existing files inside the episode folder by deterministic names. A retry can therefore resume previously completed remote steps instead of blindly creating another folder/file set. Production deployment, real OAuth E2E, database backup/restore, and real media-worker verification remain environment-dependent gates and are not represented as completed locally.
