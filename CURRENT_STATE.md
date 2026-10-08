# Narrativ Forge — Current State

> Owner: Project maintainers
> Last Updated: 2026-10-08
> Status evidence is environment-specific. Code/config alone never promotes a gate to VERIFIED.

## 1. Release status

**PENDING / not Production Ready.**

The live Render API is healthy and ready, and the Cloudflare Whisper Worker is deployed. The production release is still blocked by the absence of a continuously provisioned media worker and by external/live evidence gates.

## 2. VERIFIED

### Render API
**VERIFIED — 2026-10-08**

- Health: https://narrativ-forge.onrender.com/api/v1/health
- Readiness: https://narrativ-forge.onrender.com/api/v1/ready
- Live application SHA at checkpoint: `1369d9a3e4d8896cf6024fa45fa6810cc3cee890`
- Render service: https://dashboard.render.com/web/srv-davrqtu7bikc73f7isbg

Readiness returned database=`ok`, redis=`ok`.

### Cloudflare Whisper deployment
**VERIFIED — 2026-10-08**

- Worker: https://narrativ-forge-whisper.narrativ-forge.workers.dev
- Cloudflare account/deployment evidence confirms a 100% production version.
- `NARRATIV_SHARED_SECRET` binding exists.

**Scope:** deployment/reachability only. Authenticated real-audio transcription, VTT correctness, Subtitle Studio integration, quota/fallback behavior remain unverified.

## 3. WORKER BLOCKER

**BLOCKED — deployment capacity, not missing worker code.**

Repository worker implementation is present:

- Docker image: `web-platform/backend/Dockerfile.worker`
- Entrypoint: `celery -A app.workers.celery_app:celery_app worker --loglevel=INFO --beat` (configured concurrency defaults to 1 via `WORKER_MAX_CONCURRENCY`)
- Broker: Redis via `REDIS_URL`
- Durable job state: PostgreSQL
- Media tools: FFmpeg + OpenAI Whisper
- Worker task registration: `web-platform/backend/app/workers/tasks.py`
- Failure recovery: late ACK, worker-lost rejection, retries, DLQ publication, stale-job recovery.

Current Render service evidence:
- service type = `web_service`
- plan = `free`
- instances = 1
- no background worker service exists in the connected Render workspace.

Render's current documentation says Free instances are available for web services, Postgres, and Key Value; private/background-worker compute plans start at paid tiers. citeturn0search1turn0search0

**Owner action:** provision a paid Render Background Worker or an equivalent external worker runtime. Do not convert the API web service into a fake worker.

Prepared configuration: `render.worker.yaml`.

## 4. RELEASE GATE MATRIX

| Gate | Status | Evidence / exact blocker |
|---|---|---|
| 1. Real media → FFmpeg → Whisper → DB/storage | BLOCKED | No continuously running worker. Worker code exists; live execution evidence cannot be produced until worker runtime exists. |
| 2. Retry / DLQ / duplicate-dispatch / failover | BLOCKED | Requires live worker/queue failure-injection drill. |
| 3. B2 / Supabase / Cloudinary lifecycle | PENDING | Provider routing exists, but no fresh live upload/download/delete/archive evidence for every configured provider. |
| 4. Whisper + fallback E2E | BLOCKED | Cloudflare Worker deployment is verified; authenticated real-audio E2E and fallback drill require worker/media execution. |
| 5. Google OAuth / Drive export / recovery | PENDING | Code defines `/api/v1/drive/google/start` and `/callback`; no authenticated production OAuth/export/recovery evidence. |
| 6. SMTP | PENDING | Render blueprint declares SMTP variables, but available Render tooling does not expose secret values. No real mailbox delivery evidence. |
| 7. Stripe | PENDING | Checkout/webhook code and Render variables exist; no live test-mode checkout/webhook evidence. |
| 8. Sentry | PENDING | Sentry initialization/code exists; DSN value and live event/alert evidence are not accessible through current tooling. |
| 9. Exact live Alembic head | VERIFY | Connected Render account has no Render-managed Postgres instance. Live `DATABASE_URL` points to an external provider, but current tooling cannot query that database or reveal the secret value. |
| 10. Backup / restore | PENDING | Backup/restore scripts exist; no real managed-Postgres restore drill has been completed. |
| 11. Production auth / cross-tenant E2E | PENDING | Playwright cross-tenant tests exist, but no fresh live production browser evidence. |
| 12. Full E2E / load / performance | BLOCKED | Full release E2E depends on worker/media path; no fresh representative load benchmark. |
| 13. Security / dependency / container scans | EXTERNAL ACTION | CI workflow exists for pip-audit, npm audit, CodeQL and Trivy, but no fresh scan artifacts tied to the release checkpoint are available. |
| 14. Accessibility / responsive / WCAG | EXTERNAL ACTION | No fresh automated + manual release audit artifact. |
| 15. Legal / privacy / compliance | EXTERNAL ACTION | Requires owner/legal sign-off; tooling cannot provide external approval. |
| 16. External penetration test | EXTERNAL ACTION | Requires independent tester/report/remediation evidence. |
| 17. Provider limits / terms / commercial use | EXTERNAL ACTION | Requires account-specific provider review; code defaults are not proof of current limits/terms/watermark/commercial rights. |

## 5. AUTOMATED EVIDENCE PREPARED

Latest automated gate execution: GitHub Actions worker-evidence run is executing against main SHA `cb584aa1800dfc8992819be850bc4fd31a964bcd`. CI, Security, and CodeQL are also queued/running for that same SHA. These remain **UNVERIFIED** until the runs finish successfully.

Whisper fallback implementation was corrected against the deployed `narrativ-forge-whisper` Worker contract: signed Bearer token, episode binding, WAV input, and usage idempotency are now covered in code/tests. Live Burmese transcription quality remains unverified.

A CI evidence gate has been added on the worker branch/PR:

- Builds the real worker Docker image.
- Applies Alembic migrations against PostgreSQL.
- Runs retry/DLQ integration tests against PostgreSQL + Redis.
- Starts the real Celery worker.
- Generates deterministic media with FFmpeg.
- Runs the real Whisper CLI.
- Verifies processed video, transcript, DB completion, storage output, and current subtitle creation.

This does not replace production-provider/live evidence. The gate remains **execution pending** until its CI run produces a passing result.

## 6. PENDING

- Gates 3, 5, 6, 7, 8, 10, 11.
- Final UI/state audit and remaining Auto Production surfaces.

## 7. BLOCKED

- Gates 1, 2, 4, 12 are blocked directly or indirectly by the missing live worker.
- Gate 9 is blocked from verification by lack of access to the external production PostgreSQL instance.
- Production Ready is blocked until all applicable gates have fresh evidence.

## 8. EXTERNAL ACTION

- Gate 13: execute/attach release-SHA security scan artifacts.
- Gate 14: execute/attach automated + manual WCAG/responsive audit.
- Gate 15: obtain legal/privacy/compliance sign-off.
- Gate 16: obtain external penetration-test report and remediation evidence.
- Gate 17: perform account-specific provider terms/limits/commercial-use review.

## 9. NEXT

1. Owner provisions the worker using `render.worker.yaml` on a paid Render Background Worker or equivalent runtime.
2. Configure worker secrets/variables.
3. Run representative real-media E2E.
4. Run retry/DLQ/failover and Whisper fallback drills.
5. Execute remaining provider/recovery/security/accessibility/external gates.

## 10. Evidence rule

**Do not mark a gate VERIFIED from configuration, credentials, source code, unit tests, or a deployment manifest alone.**

Repository head and live deployment head must be tracked separately.
