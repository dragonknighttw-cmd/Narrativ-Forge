# Testing

> Owner: Engineering/QA  
> Update when: test suites, release gates, or evidence requirements change  
> Last Updated: 2026-10-08  
> Do NOT put here: unsupported live claims

## Test layers

1. Backend unit tests.
2. Backend integration tests.
3. Frontend typecheck/build.
4. Frontend component/unit tests where adopted.
5. Browser E2E with Playwright.
6. Cross-tenant E2E.
7. Representative real-media worker E2E.
8. Load/performance benchmark.
9. Security/dependency/container scanning.
10. Accessibility automated + manual review.

## Required release evidence

- CI green on the exact release SHA.
- Real queue → worker → FFmpeg/Whisper → DB/storage.
- Retry/DLQ/duplicate-dispatch/failover.
- Real storage lifecycle.
- Drive OAuth/export/recovery.
- SMTP, Stripe, Sentry.
- Backup/restore.
- Production auth and tenant isolation.
- 15–30 minute representative benchmark.
- Accessibility/responsive review.
- Legal/security sign-off as applicable.

## Evidence rule

Unit tests prove code behavior, not provider health or production deployment. Live claims require fresh environment evidence.

## UI state coverage

Where applicable test loading, empty, uploading, processing, completed, failed, retrying, rejected, offline/read-only, permission denied, session expired, Drive disconnected, Drive export failed, storage warning, unsupported file, and critical quality issue.

## Manual Mode evidence gate

Before production-ready Manual Mode, collect 15–20 manual videos, production logs, multiple hook types, subtitle styles, production-time measurements, commercial-use review, and a repeated-problem dataset.

## Media release verification procedures

### Gate 1 — real media E2E

Use one representative Burmese audio/video asset that is safe to process.

1. Upload asset through the real API.
2. Confirm a `ProcessingJob` is created.
3. Confirm Redis/Celery dispatch.
4. Confirm worker accepts `narrativ.process_real_job`.
5. Confirm FFmpeg output exists.
6. Confirm Whisper output exists.
7. Confirm DB job state becomes completed.
8. Confirm output object exists in the configured storage provider.
9. Verify checksum/reference consistency.
10. Record worker logs, job ID, timestamps and final state.

### Gate 2 — retry/DLQ/failover

1. Dispatch a disposable processing job.
2. Inject one deterministic worker failure.
3. Verify retry count and backoff.
4. Inject failures until retry exhaustion.
5. Verify `FailedJob` and DLQ publication.
6. Re-run with a healthy worker and verify recovery.
7. Submit duplicate dispatch and verify the dispatch lock prevents duplicate execution.

### Gate 4 — Whisper fallback

1. Run a representative audio file through Cloudflare Whisper.
2. Record successful transcription/VTT.
3. Simulate cloud failure or exceed configured fallback threshold.
4. Verify local Whisper executes.
5. Verify final subtitle state records the successful source.
6. Confirm no duplicate finalization.

### Gate 10 — backup/restore

1. Create a production-consistent backup using the managed DB provider.
2. Restore into an isolated database.
3. Verify Alembic history and critical tables.
4. Verify tenant isolation and storage references.
5. Run application smoke checks against the isolated target.
6. Record restore timestamp and result.

### Gate 12 — load/performance

Use representative API and media-job volumes. Record p50/p95 latency, worker processing time, CPU, memory, queue depth and failure rate. The 15–30 minute MVP processing target is a product target, not evidence until measured.
