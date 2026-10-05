# Narrativ Forge

Private, invite-only Burmese short-form video production workspace.

> **Documentation rule:** This README is the source-of-truth map for the current implementation, infrastructure, production blockers, and next work. Whenever a production-relevant change is completed, update this README in the same logical change/commit.

**Last updated:** 2026-10-05

---

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
| Long-running worker | Celery + FFmpeg + Whisper | **not hosted on Render Free yet** |

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

## 5. Current implementation status

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
- [x] Organization/tenant scope foundation
- [x] Webhook + notification foundation
- [x] Stripe billing/webhook foundation
- [x] Hybrid storage routing
- [x] Supabase private storage bucket
- [x] B2 media upload encryption setting
- [x] Render free-only blueprint (no billable worker silently provisioned)
- [x] Production configuration hardening
- [x] CORS / trusted-host validation
- [x] Webhook SSRF protections
- [x] Audit-event organization scoping
- [x] Alembic production migration fix
- [x] Latest storage deployment verified live on Render

### Implemented in code but still needs production verification

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

## 6. What is still blocking a true production-ready release

### P0 — infrastructure / secrets

The code is prepared, but these production values must exist before switching the global storage provider to `hybrid`:

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

### P0 — long-running media worker

Render Free can host the API web service, but it does not provide a free Background Worker.

Therefore:

```text
Render Free Web Service
        = API / short requests

Celery + FFmpeg + Whisper
        = long-running processing
        = requires a real worker runtime
```

The worker code, Celery configuration, tasks, and worker Dockerfile are kept in the repository so the architecture is ready. **Do not create a paid Render worker without explicit approval.**

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

## 7. Production hardening backlog

### Security

- [x] Strong production session secret validation
- [x] Secure session cookie requirement
- [x] CORS allowlist
- [x] Trusted-host validation
- [x] OAuth token encryption foundation
- [x] Webhook HTTPS/SSRF protections
- [x] Filename/path safety
- [x] Upload MIME/size validation
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
- [ ] Prevent redundant queue dispatches with a robust claim/lock strategy
- [ ] Full flaky-network upload test suite
- [ ] Backup/restore drill
- [ ] Operational runbook

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

## 8. Testing gates

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

## 9. Environment configuration

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

## 10. Deployment model

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

## 11. Working rule for future development

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

## 12. Current next sequence

The recommended execution order from the current state is:

```text
1. Add/verify B2 + Supabase production secrets
        ↓
2. Switch storage provider to hybrid
        ↓
3. Deploy + verify all three storage routes
        ↓
4. Verify Google Drive OAuth/export
        ↓
5. Verify Celery task registration + worker runtime
        ↓
6. Fix duplicate dispatch / retry edge cases
        ↓
7. Verify Stripe + SMTP + Sentry
        ↓
8. Run full integration + E2E tests
        ↓
9. Backup/restore + security/accessibility audits
        ↓
10. Final production readiness audit
```

**Important:** A “production-ready” claim should only be made after the real storage integrations, worker runtime, export flow, monitoring, backups, and final tests have been verified—not merely because the code exists.

---

## 13. Development

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

## 14. Security notes

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

## 15. Reference documents

Project planning and remediation documents are maintained alongside this repository/project context. When implementation changes, the README above should be updated to reflect the **actual code and deployment state**, while the planning documents remain the broader roadmap/audit source.

