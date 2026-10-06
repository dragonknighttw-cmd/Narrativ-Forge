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

## Feedback loop

```
Manual Data → Hook Library → Auto Defaults → Human Approve
```

### Rule
Do not optimize from one video's views alone.

Wait until at least **5–10 content pieces** exist, then compare:
- Hook performance.
- Retention/engagement signals.
- Production effort/time.
- Subtitle style results.
- Other available content-quality signals.

The purpose is to turn manual production data into better defaults while keeping human approval in the loop.

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


## P0.5 — CI / repository health
Before feature expansion, keep the repository green:
1. Cancel stale/in-progress historical GitHub Actions runs.
2. Confirm concurrency cancellation keeps only the newest run per workflow/ref.
3. Confirm docs-only changes do not trigger CI/CodeQL/Security.
4. Run the latest CI, CodeQL, and Security workflows on the repaired main commit.
5. Fix failures from newest runs only; do not chase obsolete cancelled runs.

## P1 — Expanded Auto Production
After foundation verification, implement in this order:
1. Story ingestion + AI episode split review.
2. Series Bible + character/voice profile foundations.
3. Hook Library + hook generation + performance fields.
4. Script/retention/emotional-arc/pacing quality analysis.
5. SEO metadata + engagement triggers.
6. Thumbnail pipeline + visual variety.
7. Sound design + music matching.
8. Video generation adapter + provider fallback + quota tracking.
9. Watermark/commercial-use quality gates.
10. Selective regeneration integrated with episode/scene versions.
11. Batch generation + daily-limit-aware queue.
12. Series calendar + publishing preparation.
13. Cross-platform export variants.
14. Trend integration adapter.
15. A/B testing + feedback loop.
16. Series trailer.
17. Translation only after Burmese-first workflow is stable.

## Scope rule for the expanded plan
Do not build all new tables/screens blindly. For each capability: schema → API/service → worker job if needed → UI → tests → real integration check → audit/approval behavior. A feature is DONE only after its end-to-end path works.

## Revised release order
Repository Green → Real Infrastructure Verification → Core Workflow E2E → Expanded Auto Production → UX/A11y/Security Hardening → Business/Legal → Release Gate.
