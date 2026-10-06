# Narrativ Forge — Execution Roadmap

## Current position

The project is beyond the original “Month 2/3 build from zero” stage. The repository already reports implementation of most core workflow modules.

Therefore the next sequence should be verification-first, not blind feature-building.

## Track A — Release verification (P0)

1. Verify B2 upload/download/delete with real credentials.
2. Verify Supabase Storage lifecycle with real files.
3. Verify Cloudinary preview/thumbnail upload.
4. Run hybrid-storage E2E.
5. Run Cloudflare Whisper real audio → VTT → Subtitle Studio.
6. Trigger and verify Celery fallback at the configured usage guard.
7. Run real Celery worker/runtime smoke test.
8. Verify retry, failed-job preservation, DLQ behavior, and duplicate-dispatch protection.
9. Verify Google OAuth callback and real Drive export.
10. Verify idempotent re-export and partial-upload recovery.
11. Verify Stripe webhook lifecycle.
12. Verify SMTP invitation/magic-link delivery.
13. Verify Sentry production event.
14. Run full authentication E2E.
15. Run cross-tenant isolation E2E.
16. Run backup/restore drill.

## Track B — Product completion (P1)

1. Complete all missing UI states.
2. Mobile/tablet responsive audit.
3. WCAG accessibility audit.
4. Final UI polish.
5. Complete remaining data/versioning target items that are actually needed:
   - episode versions
   - scene regeneration
   - content extensions
   - character model
6. Confirm selective regeneration can preserve unaffected scene assets.
7. Confirm production log + analytics feedback loop.
8. Confirm all quality gates block/allow the correct transitions.

## Track C — Security / operations (P1)

1. Final dependency/security scan.
2. Container/image scan where applicable to deployed artifacts.
3. Penetration/security review.
4. Backup retention and restore verification.
5. Incident/runbook drill.
6. Verify monitoring/alerting in the deployed environment.

## Track D — Business/legal (P1)

Only implement what matches the actual business direction:

- Terms of Service
- Privacy Policy
- DPA/data handling documentation where required
- Stripe production verification
- Final business/legal review

DMCA/reporting and local PSP work are not required merely because they appear in the broader remediation plan; they become required if the product scope changes toward public publishing or paid external users.

## Track E — Future reserve (P2)

Do not let these block the current release:
- React Native / Expo / Flutter
- local Stable Diffusion / ComfyUI
- advanced video editors
- R2 / S3 / Wasabi / MinIO
- RabbitMQ / Kafka / SQS / Temporal
- Grafana / Prometheus / Datadog / New Relic
- Vault / KMS / Auth0 / Clerk
- Stripe Connect / Paddle / PayPal
- Kubernetes / Terraform / Ansible / Pulumi
- Elasticsearch / Meilisearch / Typesense / Algolia
- feature flags / A/B testing platforms
- advanced marketing integrations

## Release gate

Narrativ Forge should be called production-ready only when:
- real storage lifecycle passes
- real transcription path passes
- real worker/runtime passes
- real Drive export + idempotent retry passes
- auth and tenant E2E passes
- backup/restore drill passes
- monitoring event is observed
- security/accessibility/UX audits are complete
- required business/legal documents are reviewed

Until then, label the state **Implementation-complete / Verification-pending**, not Production-ready.
