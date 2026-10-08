# Narrativ Forge — Cloud / Local / Packaging Architecture Audit

> Audit checkpoint: 2026-10-09  
> Repository head audited: `55d99dac9ab668a7f27bd944e6cfe3bacfcd5edd`  
> Purpose: define the safest path to make the repository reproducibly build, verify, package, and run both in ephemeral cloud CI and locally without removing existing features.

## 1. Executive finding

The repository is already much closer to the proposed architecture than a rewrite would suggest.

The strongest existing boundary is:

- Next.js frontend
- FastAPI backend
- Celery worker
- PostgreSQL
- Redis
- storage provider abstraction
- FFmpeg + Whisper processing
- GitHub Actions evidence workflows
- provider-specific adapters/configuration

Therefore the preferred path is **incremental runtime/packaging extraction**, not a destructive rewrite.

Target shape:

```
Shared application code
        |
   +----+-------------------+
   |                        |
Cloud verification       Local package
API + DB + Redis         API + local DB
Worker + media           Worker + media
real providers           local storage
   |                        |
   +---------- CI ----------+
          build -> test -> evidence -> cleanup
```

## 2. What is already reusable

### Backend / worker

- `web-platform/backend/Dockerfile` already produces a non-root API runtime.
- `Dockerfile.worker` already installs FFmpeg, Whisper dependencies and PyICU.
- Celery/Redis/PostgreSQL processing is already separated from the API process.
- `worker-evidence.yml` already builds the worker, runs migrations, performs storage preflight, runs integration tests, prewarms Whisper, starts the real Celery worker and executes deterministic media smoke.
- Local storage is already an explicit provider.
- Cloud storage is already abstracted behind a provider protocol and hybrid routing.

**Conclusion:** no need to invent a second processing engine for desktop mode. The same processing services should be made runtime-configurable.

### Frontend

- Next.js 16 + React 19.
- Playwright E2E already exists.
- The app already uses `NEXT_PUBLIC_API_BASE_URL`, which is the key seam needed for local packaged API vs cloud API.

**Conclusion:** desktop packaging can wrap the existing frontend rather than create a second UI.

### CI/CD

Existing workflows cover:

- CI
- Repository Gate
- Worker Evidence
- Security
- CodeQL
- Cloudflare Whisper deployment
- optional Kaggle ephemeral worker dispatcher

The repository is therefore already suited to adding **credentialed verification workflows** without replacing the existing CI.

## 3. Important gaps discovered during audit

### A. Production auth / tenant model needs hardening before live E2E

The current authentication session carries a user-global role, while `get_current_membership()` selects the user's first organization membership.

The E2E test proves isolation for two separate users, but it does not prove a user who belongs to multiple organizations cannot retain or escalate the wrong organization context.

This must be addressed before calling multi-tenant production auth VERIFIED.

Required code work:

1. Make organization/tenant context explicit in authenticated requests.
2. Resolve role from the selected organization membership, not only `users.role`.
3. Ensure every tenant-owned resource query is scoped through the authenticated organization.
4. Add multi-membership E2E coverage.
5. Keep single-user local mode as a separate local-runtime convenience; it must not silently weaken cloud multi-tenant verification.

### B. Backup/restore exists, but verification orchestration is missing

`scripts/backup_db.py` and `scripts/restore_db.py` already exist for SQLite and PostgreSQL.

Missing:

- reproducible CI backup/restore drill;
- fresh PostgreSQL restore target;
- schema/data integrity assertions after restore;
- artifact/evidence recording;
- optional provider-specific managed backup/restore drill.

This is a good candidate for immediate code-only CI work.

### C. Desktop/package runtime does not exist yet

There is no Electron/Tauri/package/installer layer in the current repository.

Recommended implementation:

- Windows-first desktop shell.
- Reuse the existing Next.js UI.
- Bundle a local API runtime and worker runtime.
- Bundle/ship FFmpeg.
- Bundle the selected Whisper runtime/model only where licensing/redistribution permits.
- Use local PostgreSQL-compatible storage strategy appropriate for desktop; SQLite is already supported by configuration and is the natural default for local single-machine mode.
- Keep Redis optional for local mode where the processing abstraction permits; otherwise package a small local Redis-compatible runtime/container strategy.
- Build the package on a Windows GitHub runner and smoke-test the installed artifact.

A Tauri-style shell with sidecar processes is preferable for footprint, but the final choice must follow the actual sidecar/FFmpeg/Python/Whisper packaging constraints. Do not commit to a desktop framework until the first reproducible Windows package build is proven.

### D. Cloud verification should be credentialed and ephemeral

Current CI mostly uses local services. That is good for deterministic tests but cannot prove provider behavior.

Add separate, explicitly invoked credentialed workflows:

- production/staging auth + tenant E2E;
- real storage lifecycle;
- real Whisper + fallback;
- Google Drive OAuth/export/recovery;
- SMTP delivery;
- Stripe test-mode checkout/webhook;
- Sentry event/alert;
- backup/restore.

These workflows must use GitHub Secrets/Environments and must never print secret values.

Where possible:

```
provision/prepare -> test -> collect evidence -> destroy/cleanup
```

Do not replace the existing deterministic CI with provider-dependent tests.

## 4. Cloud vs local capability matrix

| Capability | Local package | Ephemeral cloud CI | Production cloud |
|---|---|---|---|
| UI | yes | yes | yes |
| API | yes | yes | yes |
| Worker | yes | yes | yes |
| FFmpeg | bundled | image | image/runtime |
| Whisper | bundled/optional | CI image | worker/Cloudflare fallback |
| PostgreSQL | local-mode substitute | CI service | managed/external |
| Redis | local runtime | CI service | managed/external |
| Local storage | yes | yes | no/limited |
| B2 | optional | credentialed | yes |
| Supabase | optional | credentialed | yes |
| Cloudinary | optional | credentialed | yes |
| Google Drive | optional | credentialed | yes |
| SMTP | optional | credentialed | yes |
| Stripe | optional | credentialed test mode | yes |
| Sentry | optional | credentialed | yes |

## 5. Existing release gates remain in force

This architecture does **not** delete or replace the existing release gates.

Still required:

1. real media -> FFmpeg -> Whisper -> DB/storage
2. retry/DLQ/duplicate-dispatch/failover
3. B2/Supabase/Cloudinary lifecycle
4. authenticated Whisper/VTT/fallback
5. Google OAuth/Drive export/recovery
6. SMTP
7. Stripe
8. Sentry
9. exact live Alembic head
10. backup/restore
11. production auth/cross-tenant E2E
12. full E2E/load/performance
13. security/dependency/container scans
14. accessibility/responsive/WCAG
15. legal/privacy/compliance
16. external penetration test
17. provider limits/terms/commercial-use review

Code-only implementation through Phase 84 remains complete. These release gates are evidence gates, not automatically satisfied by the architecture work.

## 6. Implementation order

### First
- tenant-context/auth hardening;
- backup/restore CI drill;
- reusable verification harness;
- credentialed workflow scaffolding;
- packaging/runtime configuration abstraction.

### Second
- Windows package build;
- install-and-run smoke test;
- local worker/media E2E;
- package artifact upload.

### Third
- credentialed provider E2E;
- backup/restore against the real production/staging database path;
- full production auth/tenant E2E;
- load/performance.

### Final
- human/legal/accessibility/pen-test/provider acceptance gates.

## 7. Evidence rule

A green package build is not production verification.

A green local E2E is not provider verification.

A successful credentialed CI run can become VERIFIED only when the evidence records:

- exact repository SHA;
- exact workflow/run;
- environment/provider;
- test scope;
- result;
- timestamp;
- artifact/log reference.

## 8. Cost/safety rule

The existing free-only Render blueprint remains unchanged.

No paid worker or other billable service should be provisioned automatically.

Ephemeral/credentialed verification should be opt-in and cleanup-first.
