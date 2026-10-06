# Execution Roadmap

## P0 — Verification first
1. Real B2 upload/download/delete.
2. Real Supabase Storage lifecycle.
3. Real Cloudinary upload.
4. Hybrid-storage E2E.
5. Cloudflare Whisper: real audio → VTT → Subtitle Studio.
6. Verify Whisper quota guard → Celery fallback.
7. Real Celery worker/runtime smoke test.
8. Retry/DLQ/duplicate-dispatch verification.
9. Google OAuth callback + real Drive export.
10. Idempotent re-export + partial-upload recovery.
11. Stripe webhook lifecycle.
12. SMTP invitation/magic-link delivery.
13. Sentry production event.
14. Full auth E2E.
15. Cross-tenant isolation E2E.
16. Backup/restore drill.

## P1 — Product completion
- Complete UI states.
- Responsive mobile/tablet audit.
- WCAG accessibility audit.
- Final UI polish.
- Verify explicit versioning / selective regeneration / content-extension / character requirements that are actually needed.
- Verify all quality gates and workflow transitions.
- Verify production log + analytics feedback loop.

## P1 — Security / operations
- Final dependency/security scan.
- Artifact/container scan where applicable.
- Pen-test/security review.
- Backup retention + restore drill.
- Incident/runbook drill.
- Monitoring/alert verification.

## P1 — Business / legal
- Terms of Service.
- Privacy Policy.
- DPA/data handling where required.
- Stripe production verification.
- Final business/legal review.

DMCA/reporting and local payment integration are not automatic blockers unless product scope changes.

## Release gate
Production-ready only after real storage, transcription, worker, Drive export/idempotency, auth/tenant E2E, backup/restore, monitoring, security, accessibility, UX, and required business/legal checks pass.

Until then: **Implementation-complete / Verification-pending**.