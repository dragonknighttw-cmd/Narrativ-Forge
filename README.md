# Narrativ Forge

Private, invite-only Burmese short-form video production workspace.

> **Documentation rule:** This README is the source-of-truth map for the current implementation, infrastructure, production blockers, and next work. Whenever a production-relevant change is completed, update this README in the same logical change/commit.

**Last updated:** 2026-10-05 — final code/infrastructure audit pass

---



## Documentation map and completeness status — 2026-10-07

Read this section first when returning to the project:

1. **`README.md`** — current implementation, infrastructure, what is verified, what is blocked, and the current coding/verification state.
2. **`roadmap.md`** — the single authoritative requirements/plan/status/release-gate document. It now contains the consolidated requirement-completeness register so requirements do not disappear when supporting docs are cleaned up.
3. **`docs/07-ui-design.md`** — the canonical detailed UI/design-system reference: actual frontend tools, colors, typography, spacing, card/layout patterns, component/state rules, screen inventory, and implementation-vs-audit status.
4. **`docs/21-master-completion-matrix.md`** — audit/evidence matrix, not another roadmap.
5. **`docs/09-auto-production-expansion.md`** — retained as detailed Auto Production source until final consolidation/removal.
6. **`docs/10-runtime-and-storage-lifecycle-plan.md`** and focused `infra/*` runbooks — implementation/operations detail only.

There is **no `tool.md`** in the repository. UI is not currently defined by a separate tool-specific MD; `docs/07-ui-design.md` is the UI document, while the actual runtime design system lives in `web-platform/frontend/app/globals.css` and `web-platform/frontend/components/ui-primitives.tsx`.

### What is actually finished vs what is still needed

**Implemented/foundation:** core product workflow, auth/security foundations, tenant scoping foundations, script/scene/assets, resumable uploads, processing/Celery foundations, Burmese subtitle pipeline, review/approval, Drive export foundations, hybrid storage, analytics/logging foundations, AI provider routing, orchestration, Auto Production 13–17 coding foundations, semantic UI primitives/tokens, quota/retention/notification/audit/release-gate contracts.

**Still requires real evidence:** real worker/media processing, queue/retry/DLQ/failover drills, real B2/Supabase/Cloudinary lifecycle, real Cloudflare Whisper E2E/fallback, Google OAuth/Drive E2E/recovery, SMTP delivery, Stripe lifecycle, Sentry event/alerts, backup/restore, production auth/tenant E2E, load/performance benchmark, security/container scan evidence, accessibility/responsive audit, legal/compliance review, and final pen-test.

**Still needs product/UI completion or audit:** story ingestion/episode split approval flow, complete hook/SEO/retention/thumbnail/sound/Series Bible/continuity/batch/calendar surfaces, full analytics learning loop, full 33-component adoption, screen-by-screen state coverage, and the final deduplicated screen inventory.

### UI quick reference

- Stack: Next.js 16 + React 19 + TypeScript.
- Icons: lucide-react.
- E2E: Playwright.
- Styling: native CSS custom properties; no Tailwind/shadcn/MUI/Chakra runtime dependency.
- Fonts: Inter + Noto Sans Myanmar.
- Canvas: `#0b0d10`.
- Surface: `#12161b`.
- Elevated: `#181d23`.
- Brand: `#d8ff4f`.
- Semantic: success `#63d38a`, warning `#f2c14e`, danger `#ff6b6b`, info `#65b9ff`.
- Default card: 12px radius, 1px border, 20px padding.
- AppShell: ~250px sidebar + ~84px topbar + ~1400px content max-width.
- 44px minimum interactive target.
- Reduced-motion support is implemented.
- Full screen/state/accessibility adoption is **not yet verified**.


## 1. What Narrativ Forge is

Narrativ Forge is a production workflow application for Burmese short-form video content:

```text
Idea
  → Series
  → Episode
  → Script Studio
  → Scene Breakdown
  → Asset Library
  → Video Project
  → Subtitle Studio
  → Processing Queue
  → Review Center
  → Approval
  → Google Drive Export
  → Publishing Preparation
  → Production Log
  → Hook / Analytics
```

The current product is **single-user first**, while the backend already contains the foundation for organization/tenant isolation and future multi-user operation.

---

## 2. Application structure

### High-level architecture

```text
┌──────────────────────────────────────────────────────────────┐
│                         User Browser                          │
│                    Next.js + React UI                        │
└──────────────────────────────┬───────────────────────────────┘
                               │ HTTPS / JSON
                               ▼
┌──────────────────────────────────────────────────────────────┐
│                    FastAPI Backend API                        │
│  Auth · Episodes · Scripts · Scenes · Assets · Subtitles    │
│  Jobs · Review · Export · Hooks · Analytics · Billing        │
└───────────────┬──────────────────────┬───────────────────────┘
                │                      │
                ▼                      ▼
       PostgreSQL + Redis        Background Processing
       durable app state         Celery task runtime
                                      │
                                      ▼
                              FFmpeg / Whisper
                                      │
              ┌───────────────────────┼────────────────────────┐
              ▼                       ▼                        ▼
        Cloudinary              Supabase Storage          Backblaze B2
        images/previews         SRT/manifest/small        raw video/audio/
                                assets <= 50 MB            large media
              │                       │                        │
              └───────────────────────┴────────────────────────┘
                                      │
                                      ▼
                              Google Drive Export
                         final video / SRT bundle /
                                manifest
```

### Repository layout

```text
Narrativ-Forge/
├── web-platform/
│   ├── frontend/                 # Next.js + React web app
│   │   ├── app/                  # routes/pages and product UI
│   │   ├── lib/                  # API client and frontend helpers
│   │   └── e2e/                  # Playwright end-to-end tests
│   │
│   ├── backend/                  # FastAPI application
│   │   ├── app/
│   │   │   ├── api/routes/       # HTTP API endpoints
│   │   │   ├── core/             # config/security/runtime settings
│   │   │   ├── models/            # SQLAlchemy domain models
│   │   │   ├── services/          # storage and domain services
│   │   │   ├── workers/           # Celery/processing runtime
│   │   │   └── main.py            # FastAPI application entrypoint
│   │   ├── alembic/               # database migrations
│   │   ├── tests/                 # backend tests
│   │   ├── Dockerfile             # API container
│   │   └── Dockerfile.worker      # future dedicated worker container
│   │
│   └── docs/                      # architecture/implementation docs
│
├── mobile/                        # reserved mobile application workspace
├── render.yaml                    # free Render web-service blueprint
└── README.md                      # current project status/source-of-truth
```

---

## 3. Production infrastructure

| Layer | Current role | Provider |
|---|---|---|
| Frontend | Next.js web app | Netlify |
| API | FastAPI web service | Render Free Web Service |
| Database | PostgreSQL via `DATABASE_URL` | production database |
| Queue/cache | Redis | configured external Redis |
| Images/previews | Cloudinary | Cloudinary |
| Small/text assets | Supabase Storage | Supabase |
| Raw video/audio/large media | Backblaze B2 | Backblaze |
| Final exports | User-owned Drive | Google Drive |
| Error monitoring | Sentry SDK integration | Sentry |
| Cloud transcription | Browser ffmpeg.wasm + Cloudflare Workers AI | primary free path |
| Long-running worker | Celery + FFmpeg + Whisper | optional fallback; not hosted on Render Free |

### Current deployment endpoints

- Frontend: `https://harmonious-nasturtium-53a1d6.netlify.app`
- Backend: `https://narrativ-forge.onrender.com`
- Backend API base: `https://narrativ-forge.onrender.com/api/v1`

No custom domain is required for the current setup.

---

## 4. Storage architecture

Storage is intentionally split by file purpose. **Raw video/audio must not be stored in Cloudinary.**

| Asset | Storage | Rule |
|---|---|---|
| Video thumbnails | Cloudinary | <= 10 MB |
| Cover images | Cloudinary | <= 10 MB |
| SRT previews | Cloudinary | <= 10 MB |
| SRT files | Supabase Storage | <= 50 MB |
| Manifest | Supabase Storage | <= 50 MB |
| Small assets | Supabase Storage | <= 50 MB |
| Raw video | Backblaze B2 | always B2 |
| Audio | Backblaze B2 | always B2 |
| Large media | Backblaze B2 | > 50 MB |
| Final video export | Google Drive | user-owned Drive |
| SRT bundle | Google Drive | export destination |
| Export manifest | Google Drive | export destination |

### Routing behavior

The backend now has `storage_provider_for_asset()` routing:

```text
video/audio or video/* / audio/*
        → B2

thumbnail / cover / image / srt_preview <= 10 MB
        → Cloudinary

other assets <= 50 MB
        → Supabase Storage

anything larger than 50 MB not handled above
        → B2
```

Supabase bucket:

- bucket: `narrativ-forge`
- private
- max object size: 50 MB

B2 uploads explicitly request server-side encryption.

---

## 5. Cloud processing architecture

The primary free processing path moves heavy media work away from Render:

```text
Browser
  └─ ffmpeg.wasm → extract 16 kHz mono audio
        └─ Cloudflare Worker → Workers AI @cf/openai/whisper
              └─ VTT + text → Narrativ API → Subtitle Studio
```

Cloudflare Workers AI currently provides a 10,000-neuron/day free allocation. `@cf/openai/whisper` is currently listed at 41.14 neurons/audio-minute, so the raw allocation is roughly 243 audio minutes/day before other account/model constraints. This is a planning estimate, not a guaranteed minute quota. Cloudflare says limits reset daily at 00:00 UTC and requests fail after the daily free allocation is exhausted. Therefore this is **free within the daily allocation, not unlimited free inference**.

Security:
- Browser never receives the shared Worker secret.
- Backend mints a short-lived signed token scoped to the episode.
- Worker verifies the token and allowed origin before invoking Whisper.
- Extracted audio is limited to 50 MB per request.

Repository implementation:
- `web-platform/cloudflare/whisper-worker/` — Worker source + Wrangler config
- `web-platform/frontend/lib/cloud-whisper.ts` — browser ffmpeg/Whisper client
- `web-platform/backend/app/api/routes/cloud_processing.py` — signed token API
- `web-platform/backend/app/api/routes/subtitles.py` — Cloud VTT import

### Cloudflare setup status

The Worker source is committed and the production Worker deployment has been verified successfully. GitHub Actions deploy run #4 completed the Worker deploy and `NARRATIV_SHARED_SECRET` configuration. After deployment, Render must use:

```text
CLOUDFLARE_WHISPER_WORKER_URL=https://<worker>.workers.dev
CLOUDFLARE_WHISPER_SHARED_SECRET=<same secret used by the Worker>
CLOUDFLARE_WHISPER_TOKEN_TTL_SECONDS=300
```

The Worker can use the Cloudflare `workers.dev` subdomain; no custom domain is required.

For automated deployment, `.github/workflows/cloudflare-whisper.yml` deploys the Worker when its source changes. GitHub repository Actions secrets required:
- `CLOUDFLARE_API_TOKEN` — Workers Scripts Write permission
- `CLOUDFLARE_ACCOUNT_ID`
- `CLOUDFLARE_WHISPER_SHARED_SECRET` — same value configured in Render

## Current coding-track checkpoint — 2026-10-07

- Formal execution roadmap: **12 phases** (01–12).
- Expanded Auto Production add-on: **17 workstreams**; these are not additional formal phases.
- Phase 01–06 hardening batch is now merged to main.
- AI text-provider routing now supports configured Groq/OpenAI-compatible providers with priority/fallback and deterministic mock fallback.
- Dependency-aware episode orchestration plan is implemented with unit coverage.
- New AI/orchestration tests are explicitly included in the `unit` CI marker set.
- Production/live verification remains separate from code completion; no live credential or real-media gate is being falsely marked complete.

### Next execution sequence

The coding track has advanced through the Phase 07–12 hardening/foundation work and Auto Production workstreams 13–17 foundations. The next priority is **verification and evidence**, not another blind feature-building pass:

1. Reconcile and freeze the master requirement set.
2. Run the consolidated live integration gates: worker/media, storage, Whisper, Drive, SMTP, Stripe, Sentry, Redis/PostgreSQL, backup/restore.
3. Run production E2E, cross-tenant E2E, load/performance, security/container scans, accessibility, and responsive audits.
4. Complete the UI screen/state/component adoption audit.
5. Complete the remaining Auto Production product surfaces that are still TODO/FOUNDATION.
6. Perform the final documentation/roadmap checkpoint and only then call the release state Production Ready if all required evidence is green.

## 6. Current implementation status

### Completed / implemented

- [x] Next.js frontend foundation
- [x] FastAPI backend foundation
- [x] Authentication/session security foundation
- [x] PostgreSQL models + Alembic migrations
- [x] Ideas / Series / Episodes
- [x] Scripts / versions / optimistic locking
- [x] Scene breakdown
- [x] Asset management
- [x] Direct and resumable upload foundation
- [x] Processing job model and Celery task foundation
- [x] Dedicated worker image runs the actual Celery worker + beat runtime
- [x] Real-job dispatch lock, retry re-dispatch, and periodic queued-job recovery
- [x] Retry / failed-job preservation / queue foundation
- [x] Burmese/Zawgyi normalization pipeline
- [x] Subtitle foundation and pagination
- [x] Script autosave + conflict handling
- [x] Global search
- [x] Review / approval foundation
- [x] Google Drive OAuth/export foundation
- [x] Export idempotency/status transition foundation
- [x] Production log / social preparation / analytics foundation
- [x] Hook Library backend foundation
- [x] Usage metering foundation
- [x] Cloudflare Whisper daily usage guard (80% warning / 95% fallback guardrail)
- [x] Organization/tenant scope foundation
- [x] Webhook + notification foundation
- [x] Stripe billing/webhook foundation
- [x] Hybrid storage routing
- [x] Processed-video/transcript outputs use explicit hybrid storage routing
- [x] Cloudflare 95% safety guard automatically queues Celery fallback
- [x] Supabase private storage bucket
- [x] B2 media upload encryption setting
- [x] Render free-only blueprint (no billable worker silently provisioned)
- [x] Production configuration hardening
- [x] Supabase Storage object endpoint/path handling hardened
- [x] Cloudflare Worker rejects disallowed browser origins
- [x] Supabase public `anon`/`authenticated` table CRUD grants revoked; backend remains the database access boundary
- [x] Whisper usage keys are signed and bound to the requested user/episode/duration
- [x] Worker enforces the signed Whisper audio-duration bound
- [x] CORS / trusted-host validation
- [x] Webhook SSRF protections
- [x] Audit-event organization scoping
- [x] Alembic production migration fix
- [x] Latest storage deployment verified live on Render
- [x] CodeQL security analysis workflow
- [x] Whisper usage-key security regression tests
- [x] Supabase security advisor reviewed and public table grants hardened
- [x] Hybrid storage and Whisper guardrail regression tests
- [x] Operational runbooks for stuck jobs, secret rotation, and database restore
- [x] Alembic revision identifiers kept within PostgreSQL version-table length limits
- [x] Resumable-upload E2E test corrected to extract the upload session ID from the actual chunk URL

### Cloudflare Whisper status

- [x] Worker source + signed-token flow
- [x] Browser ffmpeg.wasm extraction
- [x] VTT import into Subtitle Studio
- [x] Daily usage metering and 80%/95% guardrails
- [x] GitHub Actions Worker deployment with real Cloudflare credentials
- [x] Worker shared secret configured in Cloudflare
- [ ] Render Worker URL/shared-secret configuration verification (Worker URL configured; secret presence cannot be read back from Render connector)
- [ ] Real audio → Whisper → VTT → Subtitle Studio verification
- [ ] Verify Celery fallback on a real quota-exhaustion/95% guard condition

The Whisper workstream is **not Done** until the remaining real-credential and end-to-end verification gates are passed.

### Implemented in code but still needs production verification

The final code audit has been completed without running the requested real-media/live integration tests. The remaining unchecked items below are intentionally verification gates, not claims of completion.

- [ ] Real B2 upload/download/delete against production credentials
- [ ] Real Supabase Storage upload/download/delete against production credentials
- [ ] Real Cloudinary thumbnail/preview upload verification
- [ ] End-to-end storage routing test with real files
- [ ] Google OAuth callback + real Drive export verification
- [ ] Stripe webhook lifecycle verification
- [ ] SMTP invitation/magic-link delivery verification
- [ ] Sentry production event verification
- [ ] Full E2E authentication flow verification
- [ ] Cross-tenant isolation E2E correction and execution
- [ ] Full processing task/worker smoke test
- [ ] Retry/DLQ and duplicate-dispatch verification
- [ ] Backup/restore drill

---

## 7. What is still blocking a true production-ready release

### P0 — infrastructure / secrets

The production deployment is configured for `STORAGE_PROVIDER=hybrid`, and the latest Render deployment passed the application's production configuration validation. The connector cannot read secret values back, so the exact secret contents are intentionally not documented or exposed here.

Required production configuration remains:

```text
B2_APPLICATION_KEY_ID
B2_APPLICATION_KEY
B2_BUCKET_NAME
B2_REGION
B2_ENDPOINT_URL        # only if required by the configured B2 provider path

SUPABASE_URL
SUPABASE_SERVICE_ROLE_KEY
SUPABASE_STORAGE_BUCKET=narrativ-forge
```

Keep all secrets outside Git.

### P0 — Cloudflare real end-to-end verification

The GitHub Actions Cloudflare credentials are now working and the Worker deploy/secret configuration has been verified. The remaining gate is the real audio → Whisper → VTT → Subtitle Studio test, plus verification that the Render environment points at the deployed Worker with the same shared secret. Do not mark Whisper Offload done before that test passes.

### P0 — long-running media worker

The repository now contains a real Celery worker container, including beat scheduling, guarded job dispatch, retry re-dispatch, and periodic recovery. The worker image is ready for a real worker runtime.

Render Free can host the API web service, but the current free deployment intentionally does not provision that long-running worker.

Therefore:

```text
Render Free Web Service
        = API / short requests

Celery + FFmpeg + Whisper
        = long-running processing
        = requires a real worker runtime
```

The worker code, Celery configuration, tasks, dispatch recovery, and worker Dockerfile are kept in the repository and now form a complete worker runtime path. Celery remains the long-running fallback and the runtime for scheduled/batch processing. The current Render Free service does not host that worker. **Do not create a paid Render worker without explicit approval.**

For a genuinely production-grade video-processing system, a dedicated worker host/runtime is still required.

### P1 — final verification

After secrets are available:

1. Deploy.
2. Upload a small SRT → verify Supabase.
3. Upload a thumbnail → verify Cloudinary.
4. Upload a real video → verify B2.
5. Download each asset through the API.
6. Delete/soft-delete and verify behavior.
7. Process a real job through Celery/worker.
8. Generate/edit Burmese subtitles.
9. Review → approve.
10. Export final video/SRT/manifest to Google Drive.
11. Verify export history and idempotent retry.
12. Verify Sentry, email, Stripe and audit events.

---

## 8. Production hardening backlog

### Security

- [x] Strong production session secret validation
- [x] Secure session cookie requirement
- [x] CORS allowlist
- [x] Trusted-host validation
- [x] OAuth token encryption foundation
- [x] Webhook HTTPS/SSRF protections
- [x] Filename/path safety
- [x] Upload MIME/size validation
- [x] Add CodeQL security analysis workflow
- [ ] Run final dependency/security scan
- [ ] Run Docker image vulnerability scan
- [ ] Final penetration/security review

### Reliability

- [x] Optimistic locking
- [x] Idempotency foundations
- [x] Retryable jobs
- [x] Failed-job preservation
- [x] Export state transition protection
- [x] Resumable upload foundation
- [x] Prevent redundant queue dispatches with a Redis dispatch lock plus database claim guard
- [ ] Full flaky-network upload test suite
- [ ] Backup/restore drill
- [x] Operational runbooks for stuck jobs, secret rotation, and database restore

### Product / UX

- [x] Core production workflow
- [x] Script autosave
- [x] Subtitle normalization
- [x] Review/approval foundation
- [ ] Full empty/loading/uploading/processing/error/offline states audit
- [ ] Mobile/tablet responsive audit
- [ ] WCAG/accessibility audit
- [ ] Final UI polish pass

### Business / legal

- [x] Billing foundation
- [x] Usage metering foundation
- [ ] Production Stripe verification
- [ ] Terms of Service
- [ ] Privacy Policy
- [ ] DPA / data handling documentation if required
- [ ] DMCA/copyright process if publishing publicly
- [ ] Final business/legal review

---

## 9. Testing gates

### Integration test

```text
Create episode
→ Upload fixture
→ Create processing job
→ Generate transcript
→ Edit Burmese subtitles
→ Apply subtitle preset
→ Validate
→ Approve
→ Export to Mock Drive
→ Save production log
```

### Production E2E target

```text
Login
→ Create series
→ Create episode
→ Upload video
→ Process transcript
→ Edit subtitle issue
→ Review
→ Approve
→ Export to Google Drive
→ View export history
→ Record social analytics
```

Required UI states:

```text
Empty
Loading
Uploading
Processing
Completed
Failed
Retrying
Rejected
Offline / read-only
Permission denied
Session expired
Drive disconnected
Drive export failed
Storage warning
Unsupported file
Critical quality issue
```

---

## 10. Environment configuration

Production configuration is environment-only. Never commit real credentials.

Important production variables include:

```text
APP_ENV=production
SESSION_SECRET=<secret>
SESSION_COOKIE_SECURE=true
CORS_ORIGINS=<frontend-origin>
TRUSTED_HOSTS=<backend-host>

DATABASE_URL=<postgres>
REDIS_URL=<redis>

CLOUDINARY_CLOUD_NAME=<secret>
CLOUDINARY_API_KEY=<secret>
CLOUDINARY_API_SECRET=<secret>

B2_APPLICATION_KEY_ID=<secret>
B2_APPLICATION_KEY=<secret>
B2_BUCKET_NAME=<bucket>
B2_REGION=<region>

SUPABASE_URL=<project-url>
SUPABASE_SERVICE_ROLE_KEY=<secret>
SUPABASE_STORAGE_BUCKET=narrativ-forge

GOOGLE_CLIENT_ID=<secret>
GOOGLE_CLIENT_SECRET=<secret>
GOOGLE_REDIRECT_URI=<backend-callback>
OAUTH_ENCRYPTION_KEY=<secret>

SENTRY_DSN=<secret>

CLOUDFLARE_WHISPER_WORKER_URL=<worker-url>
CLOUDFLARE_WHISPER_SHARED_SECRET=<secret>
CLOUDFLARE_WHISPER_TOKEN_TTL_SECONDS=300

STRIPE_SECRET_KEY=<secret>
STRIPE_WEBHOOK_SECRET=<secret>
STRIPE_PRICE_PRO=<price-id>
STRIPE_PRICE_BUSINESS=<price-id>
```

When all hybrid-storage credentials are confirmed, set:

```text
STORAGE_PROVIDER=hybrid
```

Do not switch this until B2 and Supabase production credentials are actually available.

---

## 11. Deployment model

### Current free deployment

```text
GitHub main
   │
   ├──→ Netlify
   │      └── Next.js frontend
   │
   └──→ Render Free
          └── FastAPI backend
                 ├── PostgreSQL
                 ├── Redis
                 ├── Cloudinary
                 ├── Supabase Storage
                 └── Backblaze B2

Google Drive
   └── user-owned export destination
```

The Render blueprint intentionally does **not** declare a background worker because the current deployment must remain free-only.

---

## 12. Operational runbooks

The repository now includes:

- `web-platform/docs/runbooks/stuck_job.md`
- `web-platform/docs/runbooks/rotate_secrets.md`
- `web-platform/docs/runbooks/restore.md`

These document recovery procedures without exposing production secrets.

---

## 13. Working rule for future development

For each meaningful production change:

```text
Inspect
→ Implement
→ Test
→ Commit
→ Deploy
→ Verify
→ Update README
→ Continue to next blocker
```

The README should be updated whenever any of these changes:

- architecture
- storage routing
- environment variables
- deployment topology
- production readiness status
- security posture
- completed workstream
- remaining blocker
- test/verification status

This prevents the project documentation from drifting away from the actual code.

---

## 14. Current next sequence

The remaining sequence is verification and release hardening; the requested real-media/live tests are intentionally not being run in this code-audit pass.

```text
1. Verify production storage credentials without exposing them
        ↓
   Supabase public table grants: verified revoked
        ↓
2. Run real B2 / Supabase / Cloudinary storage verification
        ↓
3. Run real Cloudflare Whisper → VTT → Subtitle Studio verification
        ↓
4. Run a real Celery worker/runtime smoke test
        ↓
5. Verify Google Drive export + idempotent retry
        ↓
6. Verify Stripe + SMTP + Sentry + audit events
        ↓
7. Complete backup/restore, dependency, Docker, accessibility and security audits
        ↓
8. Run the full integration/E2E suite
        ↓
9. Final production readiness decision
```

**Important:** A “production-ready” claim should only be made after the real storage integrations, worker runtime, export flow, monitoring, backups, and final tests have been verified—not merely because the code exists.

---

## 15. Development

Frontend:

```bash
cd web-platform/frontend
npm install
npm run dev
```

Backend:

```bash
cd web-platform/backend
python -m venv .venv
# activate the environment
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Frontend checks:

```bash
npm run typecheck
npm run build
npm run e2e
```

Backend tests:

```bash
pytest
```

The GitHub Actions e2e workflow requires the repository secret `BOOTSTRAP_ADMIN_PASSWORD`. Configure it in GitHub repository Settings → Secrets and variables → Actions before relying on the e2e job.

---

## 16. Security notes

- Never commit production secrets.
- Never expose Supabase `service_role` credentials to the frontend.
- Never put OAuth access/refresh tokens in browser localStorage.
- Keep Google OAuth tokens server-side and encrypted.
- Keep raw media in B2 rather than Cloudinary.
- Preserve original assets; processing outputs must not overwrite originals.
- Prefer soft-delete and explicit garbage collection.
- Keep failed processing jobs for diagnosis/retry.
- Keep export operations idempotent.
- Review tenant scope before adding any new content route.

---

## 17. Reference documents

### Reconciled project docs

The target roadmap and implementation state are reconciled in `docs/`:

- `docs/README.md`
- `docs/01-product.md`
- `docs/02-stack.md`
- `docs/03-architecture.md`
- `docs/04-current-vs-target.md`
- `docs/05-execution-roadmap.md`
- `docs/06-future-reserve.md`

Use `04-current-vs-target.md` to distinguish implemented code from unverified production integrations, and `05-execution-roadmap.md` for the current release sequence.

Project planning/remediation documents remain the broader planning source; this README continues to represent actual repository state.



### Expanded Auto Production 13–17 coding status

- [x] 13 — Cross-platform export variant planning + validation foundation
- [x] 14 — Trend adapter contract + expiry-aware ranking foundation
- [x] 15 — A/B outcome scoring/ranking foundation
- [x] 16 — Series trailer planning foundation
- [x] 17 — Burmese-first translation request/validation foundation

External platform/trend/translation integrations and real trailer rendering remain verification/integration gates.


## Current implementation checkpoint — Phase 07–12

Formal phases 07–12 have been hardened on `main` across review/approval, export/publishing, search/analytics, production hardening, business/collaboration foundations, and scale/advanced foundations. The codebase also contains the Expanded Auto Production workstreams 13–17.

### Preplanned next coding batches
- **18–24:** publishing adapters → live trend providers → experimentation → AI evaluation/routing → NLE export → storage/DR → SRE/compliance completion.
- **25–30:** character/style intelligence → hook recommendation → Burmese subtitle quality → selective regeneration → quota-aware batch scheduler → review-learning loop.
- **31–36:** Yjs collaboration → realtime events → quota enforcement → enterprise controls → onboarding/support → final launch gate.

Live credentials, external OAuth, Stripe/SMTP accounts, real worker capacity, real media, backup/restore drills, and third-party API limits remain environment-level verification gates.


## Coding-track update — Batch 18–36 foundations — 2026-10-07

The coding track has now prebuilt the dependency-light foundations for the next scale batches.

### Batch 18–24
- [x] 18 — Provider-neutral multi-platform publishing contract, platform metadata validation, deterministic idempotency key, publish ledger foundation.
- [x] 19 — Trend connector contract, TTL cache, rate-limit/failure fallback.
- [x] 20 — Experiment lifecycle primitives, allocation validation, guarded winner selection with Wilson lower-bound confidence logic.
- [x] 21 — AI evaluation cases, provider quality/latency/cost ranking, stable evaluation fingerprints.
- [x] 22 — Timeline validation plus deterministic EDL/NLE manifest foundation.
- [x] 23 — Reference-safe storage lifecycle policy and DR target contracts.
- [x] 24 — Alert rules, incident event contract, compliance gate.

### Batch 25–36 prebuilt foundations
- [x] 25 — Character/style profile contracts.
- [x] 26 — Episode scoring model foundation.
- [x] 27 — Burmese subtitle evaluation case/fingerprint + quality scoring foundation.
- [x] 28 — Dependency-aware selective regeneration planning.
- [x] 29 — Quota-aware batch planning.
- [x] 30 — Human review learning event aggregation.
- [x] 31 — Collaboration presence contract foundation.
- [x] 32 — Realtime-oriented presence model foundation.
- [x] 33 — Usage quota enforcement contract.
- [x] 34 — Enterprise resource-policy validation foundation.
- [x] 35 — Demo tenant/sample seed foundation.
- [x] 36 — Launch-gate evaluation contract.

These are coding foundations and unit-tested contracts. They do not claim live platform publishing, live trend APIs, real A/B traffic, NLE application import, backup/restore, OAuth, Stripe, SMTP, or external pen-test completion.


## Master reconciliation — 2026-10-07

The repository roadmap, prior master/remediation plans, formal Phases 01–12, Expanded Auto Production 13–17, and Batches 18–36 are reconciled in **docs/21-master-completion-matrix.md**.

That matrix is the execution status map: code/foundation work may be completed autonomously, while real worker, credentials, provider accounts, production recovery, E2E, performance, accessibility, legal, and pen-test gates remain explicitly evidence-bound.


## Code-completion checkpoint — 2026-10-07

The latest autonomous code pass adds shared completion contracts for:
- all required workflow UI states and blocking-state semantics;
- immutable content-version creation/retention;
- dependency-aware selective regeneration;
- token-bucket rate limiting and quota decisions;
- storage archive/delete planning with 80/90/95% thresholds;
- alert evaluation and secret-safe audit metadata;
- realtime presence leases and deterministic notification keys;
- legal release blockers and release-evidence gating;
- the production E2E evidence sequence.

These are code-level contracts only. Real providers, worker runtime, media processing, OAuth/Drive, SMTP, Stripe, Sentry, backup/restore, accessibility, load/security scans, legal documents, and external penetration testing remain verification/user gates.
