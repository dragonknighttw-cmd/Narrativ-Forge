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

Previous automated gate execution reached the worker Docker build/migration stage but did not produce a passing VERIFIED result. Subsequent release-maturity commits have changed `main`, so no older run is treated as evidence for the current head. The GitHub connector available here exposes PR-associated workflow runs only; push-run completion is therefore not claimed from stale data.

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

## 2026-10-08 continuation update

- Phase 15–36 continuation contracts/tests are present on `main`.
- Phase 37–45 operating-maturity contracts/tests are now present on `main` in `web-platform/backend/app/services/operating_maturity.py` and `test_operating_maturity.py`.
- The latest known worker evidence attempt reached Docker image build and migrations, then failed during the integration test collection on an `orchestration.py` SyntaxError. The checked `main` source at the recorded SHA currently contains valid `ExecutionPlan.task_names` syntax; the failed attempt has been re-run and is currently in progress. Therefore the worker gate remains **NOT VERIFIED** until that rerun completes successfully.
- Local test execution from this environment was unavailable because outbound GitHub network resolution is blocked.
- Live credentials/provider/manual acceptance remain deferred as planned.
## 2026-10-08 execution continuation — A–D pass

- Phase 15–36 continuation tests were strengthened for deterministic export keys, NLE adjacency, and launch waiver handling.
- Phase 37–45 operating-maturity contracts remain implemented with unit coverage.
- Phase 46–51 were pre-staged in `PHASE_EXECUTION.md` for evidence ledger, provider acceptance matrix, production E2E rehearsal, billing reconciliation, release freeze, and post-launch watch.
- Worker evidence remains **NOT VERIFIED** until the rerun completes successfully. The last observed rerun was still `in_progress` at the time of this update.
- No production credentials were requested or fabricated; live-provider/manual gates remain deferred.


## 2026-10-08 Phase 46–51 implementation continuation

- **Phase 46:** persistent evidence ledger + database checks; VERIFIED requires commit SHA, workflow run, evidence reference, owner, and verification timestamp.
- **Phase 47:** persistent provider acceptance matrix; secrets remain outside the repository.
- **Phase 48:** release rehearsal/freeze/watch contracts and persistence store are implemented; live staging rehearsal still depends on the continuous worker runtime.
- **Phase 49:** persistent billing reconciliation with webhook-event and tenant/idempotency uniqueness.
- **Phase 50:** persistent release-candidate freeze record with migration/environment/rollback/evidence/checklist references.
- **Phase 51:** persistent post-launch watch events plus launch eligibility contract that refuses unfrozen or unsupported gates.
- Repository-level status workflow `.github/workflows/repository-gate.yml` now produces a single **Repository Gate** check on every `main` push/PR so the commit page can show green/red without opening Actions.
- Phases **52–60** are pre-staged in `PHASE_EXECUTION.md` and `ROADMAP.md` for trailer planning, Burmese translation, sound/BGM, thumbnails, LoRA/voice consistency, social analytics import, archive/PII purge, Manual Mode validation, and final UI/state audit.

**Current release status remains NOT Production Ready.** No live/provider/manual gate is promoted by these code-only changes.


## 2026-10-08 Phase 52–60 continuation

- Code-only contracts and tests now cover trailer planning, Burmese translation/subtitle normalization, BGM/audio rights and cueing, thumbnail shortlist selection, LoRA/voice consistency, social analytics idempotency, archive/PII purge protection, Manual Mode evidence, and UI/state/accessibility audit.
- Backend CI explicitly runs `unit or security` tests, while the PostgreSQL/Redis integration job remains separate; CodeQL runs Python and JavaScript/TypeScript analysis. Repository Gate aggregates the checks into one green/red status for the commit page.
- Phase 61–68 have been pre-staged in `PHASE_EXECUTION.md` and `ROADMAP.md`: performance/cost, worker autoscaling, provenance, enterprise audit, provider adapters, localization operations, monetization expansion, and post-launch SLO/error-budget operations.
- The new Phase 52–60 tests are marked `unit`, so they are included in the normal CI unit/security check. No separate live credential is required for these foundations.

**Evidence status:** code/test foundations are implemented; live worker, provider, billing, legal, accessibility and human acceptance gates remain unverified until fresh evidence exists.


## CI/test visibility hardening — 2026-10-08

- Backend CI now runs `unit or security` with `-vv`, so individual store/release/product regression tests are visible in the job log instead of being silently omitted by marker selection.
- Backend unit/security and PostgreSQL/Redis integration jobs each publish a JUnit XML artifact on every run.
- Previously unmarked backend regression suites were classified explicitly as `unit`, including content quality, magic links, production foundations/intelligence, provider quota/registry, resumable uploads, selective regeneration, and subtitle normalization.
- CodeQL remains a separate Python + JavaScript/TypeScript security check; Real Worker Evidence remains the real-media/Celery gate; Repository Gate aggregates all checks into the commit-level green/red surface.


## 2026-10-08 Phase 61–68 foundation continuation

Code-only contracts/tests are now staged for performance/cost budgets, worker autoscaling, provenance/lineage, enterprise audit, provider capability/circuit-breaker, localization QA, monetization ledgers, and SLO/error-budget operations. Live telemetry/providers/billing/enterprise acceptance remain unverified.


## Phase 61–68 code-foundation progress — 2026-10-08

Code-only foundations are now staged in `web-platform/backend/app/services/phase_61_68.py` with unit coverage in `tests/test_phase_61_68.py`: performance/cost budgets, worker autoscaling policy, provenance lineage, enterprise permissions, provider capability discovery, localization quality thresholds, billing metering validation, SLO budgets and incident/rollback policy. Live telemetry, billing, provider, enterprise and post-launch acceptance remain external gates.
