# Narrativ Forge — Cloud / Local / Packaging Architecture Audit

> Audit checkpoint refreshed: 2026-10-11 UTC  
> Application-code evidence baseline: `e0ce675ea27f3b6d5aa4bb53e8a2bf5bb6698775`  
> Later schema-restore workflow baseline: `e96f26ef3b2f132d46bc95e87b28909de654a3f4`  
> Verified direct-main implementation baseline: `df22942f3482690eae79859670581908df26b360`; CI, Security, CodeQL, Repository Gate, Local Runtime Evidence, and Windows Portable Package Evidence all passed on this SHA.  
> Scope: review existing CI/evidence workflows and current multi-tenant/session implementation; this is not production acceptance.  
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

### A. Production auth / tenant model — implementation improved; live acceptance still open

Current code now supports signed v2 sessions bound to an explicit `organization_id`, resolves the effective role from that organization's membership, and provides a workspace-switch endpoint that issues a new workspace-bound session. Tenant-owned series/episode and child-resource queries have explicit organization scoping, and existing tests cover membership-bound session roles plus cross-tenant resource access.

The new regression test `test_multi_membership_session_scopes_resources_and_role_to_selected_workspace` exercises a single user with owner membership in one workspace and viewer membership in another, checks that resource listing/reads follow the active workspace, and checks that the viewer role cannot mutate resources. This test was added on source commit `8a83f3e5fdb07ab8fd687b8621707ab8af55f670` and its signed-cookie setup was corrected in `f054db675d68e4018a2a63ab0e4a8cd29197a948`; the current run must pass before this regression is considered verified.

Still required before multi-tenant auth can be marked production VERIFIED:

1. Confirm the new regression and the full CI suite pass on the latest SHA.
2. Review all tenant-owned routes and background-job ownership checks, not only HTTP resource routes.
3. Run credentialed staging E2E against the actual deployed auth/session configuration.
4. Keep single-user local mode separate; it must not weaken cloud multi-tenant authorization.

### B. Backup/restore — ephemeral CI drill exists; managed-provider drill is wired but awaiting staging credentials

`scripts/backup_db.py` and `scripts/restore_db.py` support SQLite and PostgreSQL. `.github/workflows/backup-restore-evidence.yml` verifies a disposable GitHub Actions PostgreSQL backup → fresh restore → schema/data/Alembic integrity and uploads a machine-readable manifest. It deliberately sets `production_verified: false`.

`.github/workflows/managed-staging-restore-evidence.yml` now provides a manual, confirmation-gated managed-provider drill. It requires separate source and restore database hosts, creates a custom-format backup from the staging source, restores only to the separately configured disposable destination, checks that the Alembic version matches and expected schema exists, then uploads a machine-readable artifact. It never marks production as verified. The workflow is intentionally manual and requires the GitHub Environment `managed-staging-restore`.

Current account discovery found one active Supabase project (`Narrativ-Forge`) and no Supabase development branches. No new project/branch or billable resource was created. Therefore the managed-provider run is **not yet executed**: an isolated staging source and a separate disposable restore-target database must be provisioned/configured by the owner before credentials can be added. Do not reuse the production database as either target.

Required owner setup before the first live run:

1. In GitHub repository Settings → Environments, create `managed-staging-restore`; configure required reviewers if available.
2. Add environment secrets `STAGING_SOURCE_DATABASE_URL` (staging source) and `STAGING_RESTORE_DATABASE_URL` (separate disposable restore target). Keep both values private; do not paste them into chat or logs.
3. Add environment variables `STAGING_SOURCE_HOST` and `STAGING_RESTORE_HOST`, each set to the exact hostname in its corresponding URL. The workflow refuses to run if hostnames do not match these allowlisted values or are the same.
4. Confirm the target contains no needed data and is safe to overwrite; the restore script runs `pg_restore --clean --if-exists`.
5. Set a documented recovery objective (RPO/RTO) and record the owner approval for this destructive staging restore.
6. Open Actions → Managed Staging Restore Evidence → Run workflow, select `YES` only after verifying the destination. Inspect the uploaded `managed-staging-restore-evidence` artifact and exact-SHA result.

Until that workflow succeeds, managed-provider recovery remains **pending**, and production recovery remains **unverified**.

### C. Windows portable package evidence exists; full desktop installer/runtime remains incomplete

`.github/workflows/windows-portable-package.yml` builds a portable API/UI ZIP on a Windows runner, installs from that exact ZIP, checks API/UI endpoints, tests restart/data persistence, cleans up processes, and uploads evidence. The manifest explicitly says the bundle is not a full installer and does not include the worker, FFmpeg, or Whisper. `.github/workflows/windows-local-runtime-evidence.yml` separately verifies the local API + SQLite runtime. These are useful foundations, not a shippable desktop app.

Recommended next implementation:

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

Deterministic CI covers local PostgreSQL/Redis, worker/media smoke, backup/restore, local API + SQLite, and Windows portable API/UI packaging. These are valuable reproducible checks but do not prove live provider behavior.

Existing opt-in/provider workflows include Cloudflare Whisper preflight/deployment/live-evidence scaffolding, backup/restore evidence, and Kaggle worker dispatch. Confirm each workflow's trigger conditions and latest run before treating it as evidence. Remaining credentialed provider acceptance should be separate and explicitly invoked:

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

Phase 13–84 roadmap coverage remains tracked, but individual features and production acceptance must not be inferred complete from phase numbering or CI green status. These release gates are evidence gates, not automatically satisfied by architecture work.

## 6. Implementation order

### First
- pass the new real-session multi-membership regression and full CI on the latest SHA;
- review all tenant-owned HTTP routes and worker task ownership checks;
- run and inspect the existing backup/restore evidence workflow;
- reconcile all roadmap/status docs with exact-SHA workflow evidence.

### Second
- close credential-free cloud gaps and verify the real worker evidence run;
- finish Windows portable package/local-runtime acceptance, clearly distinguishing a portable API/UI bundle from a full desktop installer;
- add the local worker/media processing runtime only after cloud-side checks are stable.

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
