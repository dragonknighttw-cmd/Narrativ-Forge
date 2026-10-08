# Narrativ Forge — Current State

> Owner: Project maintainers  
> Update when: a status/evidence item changes  
> Last Updated: 2026-10-08  
> Do NOT put here: long-form implementation tutorials or future requirements without status

## 1. Current Release

**Status: PENDING / not Production Ready.**

The repository is deployed on Render and the current `main` release is live at the API layer, with PostgreSQL and Redis readiness confirmed. Production readiness is still blocked by real worker/media execution, external integrations, recovery, performance, security, accessibility, legal, and final E2E evidence.

## 2. Current Phase

**Verification and evidence phase after Phases 01–12 and Auto Production 13–17 coding foundations.**

## 3. Status Definitions

- DONE = repository implementation evidence exists.
- VERIFIED = fresh runtime/provider evidence exists.
- PENDING = required work/evidence remains.
- BLOCKED = dependency prevents completion.
- DEFERRED = intentionally postponed.
- NEXT = next execution target.
- VERIFY = evidence is required before promotion.

## 4. COMPLETED

- Core Next.js/FastAPI application foundation.
- Ideas/Series/Seasons/Episodes.
- Script/version/autosave foundations.
- Scene and asset workflows.
- Upload validation, resumable-upload foundations, original preservation.
- Processing job/Celery foundations.
- Burmese subtitle workflow and validation.
- Review/approval foundation.
- Google Drive export foundation.
- Hybrid storage routing foundation.
- Tenant scoping/security hardening foundations.
- Billing/webhook foundation.
- Search/analytics foundations.
- AI adapter/provider routing and orchestration foundations.
- Auto Production 13–17 coding foundations.
- Reusable UI design-token/primitives foundation.
- Operational runbooks and release-gate contracts.

## 5. VERIFIED

### 5.1 Render API deployment
**VERIFIED — 2026-10-08.**

Render service `Narrativ-Forge` is configured from the repository `dragonknighttw-cmd/Narrativ-Forge`, branch `main`, and the latest live deploy is commit `1369d9a3e4d8896cf6024fa45fa6810cc3cee890`. The live API returned HTTP 200 from both health and readiness endpoints.

Evidence:
- Live health: https://narrativ-forge.onrender.com/api/v1/health
- Live readiness: https://narrativ-forge.onrender.com/api/v1/ready
- Release commit: https://github.com/dragonknighttw-cmd/Narrativ-Forge/commit/1369d9a3e4d8896cf6024fa45fa6810cc3cee890
- Render service: https://dashboard.render.com/web/srv-davrqtu7bikc73f7isbg

### 5.2 PostgreSQL and Redis runtime connectivity
**VERIFIED — 2026-10-08.**

The live readiness endpoint returned `{"status":"ready","checks":{"database":"ok","redis":"ok"}}`. Render logs also show PostgreSQL Alembic startup and Uvicorn application startup on the live instance.

Evidence:
- Readiness: https://narrativ-forge.onrender.com/api/v1/ready
- Render service logs/runtime: https://dashboard.render.com/web/srv-davrqtu7bikc73f7isbg

**Scope limit:** this verifies live connectivity/readiness only. Exact live Alembic head, backup/restore, and production data-integrity drills remain VERIFY.

### 5.3 Cloudflare Whisper Worker deployment
**VERIFIED — 2026-10-08.**

Cloudflare account evidence shows Worker `narrativ-forge-whisper` exists, was deployed from Wrangler, and has a 100% production deployment version created 2026-10-07. The Worker has the required `NARRATIV_SHARED_SECRET` secret binding and its workers.dev subdomain is enabled. A live request to the Worker returned the expected HTTP-method guard response.

Evidence:
- Live Worker: https://narrativ-forge-whisper.narrativ-forge.workers.dev
- Cloudflare Worker deployment: https://dash.cloudflare.com/

**Scope limit:** deployment/configuration is verified; authenticated real audio → Whisper → VTT → Subtitle Studio E2E and fallback behavior remain VERIFY.

## 6. VERIFY / BLOCKERS

| Item | Status | Exact blocker / required evidence |
|---|---|---|
| Real worker → representative media → FFmpeg/Whisper → DB/storage | VERIFY | No live background media worker is provisioned in Render; current Render service is API-only. Need a real worker runtime or approved ephemeral worker plus representative media evidence. |
| Retry / DLQ / duplicate-dispatch / failover | VERIFY | No live failure-injection drill evidence. |
| Real B2 / Supabase / Cloudinary lifecycle | VERIFY | No fresh live upload/download/delete/archive lifecycle evidence for each configured provider. |
| Real Whisper + fallback | VERIFY | Whisper Worker deployment is verified, but no authenticated real-audio E2E or fallback drill has been evidenced. |
| Google OAuth / Drive export / re-export / recovery | VERIFY | No fresh authenticated OAuth/export/recovery evidence. |
| SMTP delivery | VERIFY | No real mailbox delivery evidence. |
| Stripe lifecycle / webhooks | VERIFY | No live checkout/subscription/webhook lifecycle evidence. |
| Sentry event / alert verification | VERIFY | No fresh production event and alert-delivery evidence. |
| Exact live Alembic migration head | VERIFY | Runtime PostgreSQL connectivity and `alembic upgrade head` startup are evidenced, but the exact live revision has not been queried independently. |
| Backup / restore drill | VERIFY | No completed restore drill against the live managed PostgreSQL environment. |
| Production auth / cross-tenant E2E | VERIFY | No fresh browser E2E proving invite/auth/session and cross-tenant isolation in the live environment. |
| Full browser E2E / load / performance | VERIFY | No fresh full production E2E suite or representative load benchmark evidence. |
| Security / dependency / container scans | VERIFY | No fresh scan artifacts tied to release SHA `1369d9a3e4d8896cf6024fa45fa6810cc3cee890`. |
| Accessibility / responsive / WCAG review | VERIFY | No fresh automated + manual audit evidence for the release UI. |
| Legal / privacy / compliance | VERIFY | No external approval/sign-off evidence. |
| External penetration test | VERIFY | No external pen-test report/remediation evidence. |
| Live provider limits / terms / commercial use | VERIFY | Code/configuration is present, but account-specific limits, current terms, watermark behavior, and commercial-use conditions are not evidenced for all planned providers. |

## 7. PENDING

- Final UI screen inventory and state coverage.
- Remaining Auto Production product surfaces.
- Evidence-backed release audit.
- Legal/compliance documents.
- External penetration testing.

## 8. BLOCKED

Production-ready release is blocked until the applicable VERIFY gates above have fresh evidence. Code existence, deployment manifests, credentials, or unit tests alone cannot unblock a live gate.

## 9. DEFERRED

- Direct social publishing remains out of scope.
- Full mobile client remains reserved.
- Character/LoRA production pipeline remains target/reserve until the complete training → storage → generation → consistency path is evidenced.
- Paid always-on worker is reserved unless free/local/ephemeral execution is insufficient.

## 10. REMAINING RELEASE GATES

1. Worker → real media → DB/storage completion.
2. Retry/DLQ/duplicate-dispatch/failover.
3. Real B2/Supabase/Cloudinary lifecycle.
4. Real Whisper and fallback.
5. Google Drive OAuth/export/re-export/recovery.
6. SMTP.
7. Stripe.
8. Sentry.
9. Exact live PostgreSQL migration head.
10. Backup/restore.
11. Production auth/tenant E2E.
12. Full E2E + load/performance.
13. Security/container scans.
14. Accessibility/responsive/WCAG review.
15. Legal/compliance.
16. External pen-test.
17. Live provider limits/terms/commercial-use verification.

## 11. LAST VERIFIED

**2026-10-08 live verification checkpoint.**

Verified at this checkpoint:
- Render API live on release SHA `1369d9a3e4d8896cf6024fa45fa6810cc3cee890`.
- PostgreSQL readiness = `ok`.
- Redis readiness = `ok`.
- Cloudflare Whisper Worker deployment and workers.dev reachability.

## 12. NEXT ACTION

Run the remaining live verification gates in dependency order, starting with an approved real worker/media execution path and authenticated Whisper E2E. Do not label the release Production Ready until every applicable gate has evidence.
