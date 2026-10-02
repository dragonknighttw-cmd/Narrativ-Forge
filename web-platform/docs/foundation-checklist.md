# Phase 1 — Foundation Exit Checklist

## Repository and architecture

- [x] Root structure separated from application code
- [x] Frontend/backend/docs/mobile boundaries created
- [x] Next.js frontend shell created
- [x] FastAPI backend created
- [x] SQLite + PostgreSQL-compatible ORM foundation created
- [x] Heavy-work boundary kept outside the API/frontend
- [x] Mock-first integration boundary documented

## Access and security foundation

- [x] Invite-only development login boundary
- [x] Backend authentication dependency
- [x] Reusable backend role guard
- [x] httpOnly session cookie
- [x] No client-side token storage
- [x] CORS origin allowlist
- [x] Environment examples separated from source code
- [x] Production secrets/OAuth deferred until the appropriate hardening/integration phase

## Application shell

- [x] Protected workspace shell
- [x] Login loading/error states
- [x] Session-check loading state
- [x] Responsive base layout
- [x] Foundation dashboard without fake production metrics
- [x] Reserved routes for later workflow modules

## API and verification

- [x] Health endpoint
- [x] Login/logout/me endpoints
- [x] Ideas API skeleton
- [x] Episodes API skeleton
- [x] Backend foundation test suite added
- [x] Frontend typecheck command added
- [ ] Real local dependency installation + test/build execution
- [ ] CI execution of backend tests and frontend typecheck

The last two items are environment/CI verification gates rather than code-completion blockers; this environment does not provide a connected local checkout/runtime for the repository.

## Phase 2 implementation status

- [x] Ideas list/create/update
- [x] Series list/create/detail/update
- [x] Season list/create under a series
- [x] Episode list/create/detail/update
- [x] Episode → series relationship validation
- [x] Season → series relationship validation
- [x] Duplicate season number protection per series
- [x] Duplicate episode number protection per season
- [x] Target duration validation
- [x] Public episode ID generation
- [x] Backend status-transition state machine
- [x] Current workflow step follows episode status
- [x] Empty/loading/error states in domain UI
- [x] Episode status transition UI
- [x] Phase 2 backend integration tests

## Phase 2 entry condition

Do not add real media, AI, Google Drive, or production storage integrations yet.

Next: build Ideas → Series → Seasons → Episodes as a complete vertical slice:

`DB → API → UI → validation → empty/loading/error states → tests`


## Phase 2/3 audit closure

- [x] Script CRUD + explicit version creation
- [x] Scene CRUD + reorder validation
- [x] Asset upload + MIME/extension allow-list
- [x] Upload size limit + filename sanitization
- [x] Asset versioning; originals are never overwritten
- [x] Scene/episode/script ownership validation
- [x] Mock processing job + retry endpoint and queue UI
- [x] Production workspace links from Episode Detail
- [x] Backend vertical-slice tests for script, scene, asset upload
- [x] Frontend typecheck/build CI workflow added
- [ ] Real local test/build execution from a connected runtime — pending environment access


## Phase 4 — Processing Engine

- [x] Processing job lifecycle: queued → running → completed/failed
- [x] Local mock worker entrypoint
- [x] Mock media output is stored as a separate asset version
- [x] Mock Burmese transcript JSON is generated as a separate asset
- [x] Source asset is never overwritten
- [x] Missing input and missing source-file failures are preserved on the job
- [x] Retry endpoint only retries failed jobs and increments retry count
- [x] Episode status can advance from in_production → processing → subtitle_review
- [x] Episode status is marked failed when an active processing job fails
- [x] Processing Queue UI
- [x] Error/retry UI
- [x] Backend processing lifecycle tests
- [x] CI runs backend tests and frontend typecheck/build
- [ ] Real FFmpeg/Whisper integration — intentionally deferred to the integration phase after mock-first validation


## Phase 5 — Subtitle

- [x] Versioned subtitle model with current-version tracking
- [x] Transcript asset → subtitle cue generation
- [x] Burmese subtitle editing API and Studio UI
- [x] Subtitle presets: default and compact
- [x] Timing validation: missing text, overlap, invalid timing, 1–7 second default display window
- [x] Burmese text and preset line-length validation
- [x] SRT generation
- [x] VTT generation
- [x] Human quality gate blocks subtitle approval when validation errors remain
- [x] Approved subtitle version becomes immutable through the edit API
- [x] Episode Detail → Subtitle Studio workspace link
- [x] Backend subtitle lifecycle/export tests
- [x] CI remains the verification gate for backend tests and frontend typecheck/build


## Phase 6 — Review / Approval / Drive Export

- [x] Review Center with approval checklist
- [x] Critical issue blocking
- [x] Request revision returns episode to production
- [x] Final approval requires checklist completion and approved subtitle
- [x] Approved processed video is marked final without overwriting the source asset
- [x] Mock Drive export with manifest
- [x] Mock Drive export is idempotent
- [x] Google OAuth start/status/callback boundary
- [x] OAuth tokens stored server-side with application-level encryption
- [x] Narrow Google Drive drive.file scope
- [x] Real Google Drive export uploads video, SRT, and export manifest
- [x] Drive failures are preserved and reported as retryable failures
- [x] Review/export integration tests


## Phase 7 — Hook / Manual Log / Analytics / Social Preparation

- [x] Hook Library model and CRUD API
- [x] Supported hook types: question, shock, mystery, warning, personal_story, contrarian, cliffhanger
- [x] Manual Production Log model and create/list API
- [x] Publishing Preparation with caption, hashtags, schedule metadata, and manual publishing states
- [x] Social analytics manual record/import boundary
- [x] App analytics summary API and screen
- [x] Production intelligence integration test
- [x] Human-controlled hook default flag; performance data does not automatically change defaults

## Phase 8 — Hardening / Production Readiness

- [x] Upload filename sanitization and MIME/extension validation regression tests
- [x] Upload size limit remains enforced server-side
- [x] Keyboard-visible focus states and responsive analytics UI
- [x] Google Drive retry persists remote IDs and reuses existing child files by deterministic name
- [ ] Real production deployment credentials and infrastructure verification — environment-dependent
- [ ] Backup/restore against a production PostgreSQL instance — environment-dependent
- [ ] Full live Google Drive E2E test — requires configured OAuth credentials
- [ ] Real FFmpeg/Whisper worker integration — intentionally deferred from mock-first foundation
