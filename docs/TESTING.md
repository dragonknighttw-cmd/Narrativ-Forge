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
