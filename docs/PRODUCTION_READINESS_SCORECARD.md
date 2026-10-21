# Production Readiness Scorecard — 2026-10-21

**Current decision: NOT READY FOR GENERAL PRODUCTION SIGN-OFF.** The 2026-10-17 conditional sign-off below is historical and superseded by the current deployment, database, and security evidence recorded here.

## Current verification addendum — 2026-10-21

- **Public HTTP smoke:** GitHub Actions Production HTTP Smoke runs #29 and #31 passed the frontend health endpoint, frontend homepage, backend health/readiness, and AI usage checks. Run #31 passed after merged commit `69cdeb8f09d3cb254db7589915f6fc1a4862f5fa` was deployed live by Render deployment `dep-dbc7ibo473hc73a3tj3g` at 2026-10-21 08:36:29 UTC. This is external-runner evidence that the checked endpoints responded successfully after the frontend fix.
- **Frontend API configuration:** Render environment now contains the non-secret value `NEXT_PUBLIC_API_BASE_URL=https://narrativ-forge.onrender.com/api/v1`. PR #104 was merged as `69cdeb8f09d3cb254db7589915f6fc1a4862f5fa`, adding a production fallback, documenting the same API URL in `render.yaml`, and routing Brain Soul synthesis through the shared API client. The merged commit is now live, and post-deploy Production HTTP Smoke run #31 passed.
- **Render health-check configuration:** Render dashboard metadata reports the frontend health check path as `/`, while repository `render.yaml` specifies `/api/health`. The frontend homepage redirects to `/dashboard`; align the live Render setting to `/api/health` and confirm a 200 response to avoid relying on a redirect for health checks.
- **Backend readiness:** The production HTTP Smoke workflow passed backend health/readiness and `/api/v1/ai/usage` on the deployed main commit above. Keep rechecking these endpoints after frontend deploys and any environment change.
- **AI usage durability:** The production `/api/v1/ai/usage` endpoint returned success in smoke run #31, but `apps/web-platform/backend/app/services/ai_usage_tracker.py` stores call/error totals in process-local dictionaries. Counters reset on restart/deploy and are not a durable usage or billing ledger. Persist usage/quota events in the database or Redis before relying on the dashboard for audit-grade accounting.
- **Alembic migration head:** The live database query reports `0023_brain_soul_dedupe`. Supabase's migration registry also contains follow-up records through `stamp_alembic_head_0023_brain_soul_dedupe`. The older note that live Alembic was at `0019_series_bible` is stale.
- **Direct client table access:** Current read-only database checks found no table grants and no sequence usage grants for `anon` or `authenticated`. All 43 public tables have RLS enabled and no policies. With client table grants revoked, the no-policy state is restrictive for direct table access, but backend API access and tenant-isolation tests must still pass before sign-off.
- **Default privilege residual:** `supabase_admin` default ACLs still grant table, sequence, and function privileges to `anon`/`authenticated`. The current SQL session is `postgres` and is not a member of `supabase_admin`, so it cannot alter that role's defaults with ordinary `ALTER DEFAULT PRIVILEGES`. Have an authorized database administrator manage those defaults as the owning role, then re-query the ACLs. Current existing public routines have no `anon`/`authenticated` grants, but the default function ACL remains broad.
- **Supabase Auth:** Security Advisor continues to report leaked-password protection as a warning; enable it and verify login/password-reset behavior.
- **Other release gates:** Storage provider acceptance tests, authenticated Cloudflare Whisper end-to-end test, Qdrant dependency/collection confirmation, Telegram token-safe `getMe` check, and tenant-isolation tests remain unverified or require explicit owner-approved deferral.

**Release gate:** Do not grant general production sign-off until the merged frontend deploy is live and the production HTTP smoke checks pass against that commit; the Render health-check path is aligned; default-privilege residuals are closed or formally risk-accepted; leaked-password protection is enabled; and remaining integration/security gates are verified or explicitly deferred with an owner and date.

---

## Historical decision — 2026-10-17 (superseded)

**Decision at that time: PRODUCTION READY — CONDITIONAL SIGN-OFF (OWNER-APPROVED LAUNCH).**  
**Historical conditional sign-off:** based on owner-provided live HTTP evidence and canonical database confirmation; it was not an independent re-run of those external checks. Current evidence above supersedes this historical decision.

## Evidence and scorecard

| Layer / Component | Target Service / Endpoint | Expected State | Current Result | Action Needed |
|---|---|---|---|---|
| Backend Runtime | Render API `https://narrativ-forge.onrender.com/api/v1/health` | HTTP 200 and expected JSON | **PASS — OWNER-REPORTED** — HTTP 200; `status=ok`, `service=narrativ-forge-api` | Retain timestamped external ping evidence in the release evidence ledger; this verifier did not independently reproduce the request |
| Database & Cache | Supabase + Upstash / API `/ready` | DB and Redis connected, HTTP 200 | **PASS — OWNER-REPORTED** — HTTP 200; `status=ready`, database and Redis checks `ok`; Upstash direct PING returned `PONG` | Preserve timestamped response evidence and confirm deployed `DATABASE_URL` matches the owner-confirmed canonical project without exposing credentials |
| AI Provider Usage | `/api/v1/ai/usage` | HTTP 200, provider usage/quota tracked | **PASS — OWNER-REPORTED ENDPOINT** — HTTP 200; Gemini, Groq, OpenRouter, Voyage, Cohere, Mistral, and Cloudflare reported as tracked active providers; failover behavior itself was not demonstrated | Run a non-billable or explicitly approved failover contract test and preserve its result |
| Canonical Database & Migrations | Supabase `Narrativ-Forge` (`xrhlefglqwquhvpoevsg`, ap-southeast-1) | Owner-confirmed target; migration head reconciled | **CANONICAL TARGET CONFIRMED BY OWNER.** `Narrativ-Forge-1` is a managed-restore smoke-test target. Migration `0021_revoke_client_grants` is reported prepared; **production application and live revision verification are not evidenced here** | Verify reviewed SQL, backup/rollback path, and exact target before applying; after approved execution, record resulting Alembic revision and test API-mediated access. Do not infer a prepared migration has been applied |
| Tenant Isolation & RLS | Canonical Supabase project and API-mediated access | Client roles cannot bypass tenant boundaries | **OWNER-ACCEPTED RESIDUAL RISK / REVIEW OPEN.** Prior advisor reported 41 RLS-enabled/no-policy findings on the canonical project. Migration `0021_revoke_client_grants` is reported prepared to revoke `anon`/`authenticated` public-schema privileges, but this does not prove it was applied or that tenant-isolation tests pass | Review grants/policies and run tenant-boundary tests. Treat grant revocation as defense-in-depth, not a substitute for tenant-isolation validation; record explicit security acceptance and remediation owner/date if launch proceeds before closure |
| Cloudflare Whisper | `narrativ-forge-whisper` | Deployed, secret-authenticated remote transcription | **PARTIAL** — Worker script exists (last modified 2026-10-12); route and authenticated end-to-end contract not proven | Verify route, configured shared secret and successful authenticated request. Burmese dialect human-reviewed fine-tuning remains a post-launch quality item |
| Multi-Storage | Supabase Storage / B2 / Cloudinary | Upload, object read, signed URLs valid | **UNVERIFIED** — provider config exists in repo; no live upload/signed URL acceptance evidence | Test each configured provider separately with a non-sensitive test asset; validate expiry, access isolation and deletion/replication behavior |
| Upstash Redis | `Narrativ` | PING, queue/cache behavior works | **PASS — connectivity only** — account state active, TLS enabled, `PING` returned `PONG` | Confirm the deployed API/worker uses this database; exercise queue/rate-limit integration |
| Qdrant Vector Search | Qdrant Cloud | Collection initialized and searchable | **UNVERIFIED / NOT FOUND IN CONNECTED PROVIDER INVENTORY** — no Qdrant connection or collection evidence available from the inspected integrations | Confirm Qdrant is an intended dependency; provide connected Qdrant access or run a credential-safe collection health check |
| Telegram Alert Bot | Telegram Bot API `getMe` | HTTP 200 and verified bot identity | **UNVERIFIED** — bot token is a secret not available to this check; no request performed | Run `getMe` securely from an environment holding `TELEGRAM_BOT_TOKEN`; record bot username only, never token |
| Frontend Web Studio | Render `https://narrativ-forge-frontend.onrender.com/` and `/usage` | HTTP 200 and rendered app | **UNVERIFIED** — Render frontend service/deploy is live at current docs commit; direct HTTP page checks were unavailable | Verify both routes externally and run browser/API integration E2E |
| Background media worker | Render worker / Redis queue | Worker heartbeat and real queued job succeeds | **DEFERRED POST-LAUNCH — OWNER APPROVED** | Track worker orchestration as post-launch work; until delivered, do not promise continuous background media processing or queued-job SLAs |
| Release commit sync | Render API + frontend | Intended exact commit live | **PASS — deploy metadata only** — both Render services list live deploys at commit `207c3979b5fdc6216eb31c15bd82ca2470957e0a` (docs checklist commit) | Run exact-head CI and runtime E2E; deployment metadata is not a health test |

## Owner-provided live evidence and decisions (2026-10-17)

- Owner reports direct external `GET https://narrativ-forge.onrender.com/api/v1/health` returned HTTP 200 with `{"status":"ok","service":"narrativ-forge-api"}`.
- Owner reports direct external `GET https://narrativ-forge.onrender.com/api/v1/ready` returned HTTP 200 with `{"status":"ready","checks":{"database":"ok","redis":"ok"}}`.
- Owner reports `GET https://narrativ-forge.onrender.com/api/v1/ai/usage` returned HTTP 200 and tracked Gemini, Groq, OpenRouter, Voyage, Cohere, Mistral, and Cloudflare as active providers. This proves endpoint response/provider tracking as reported, not tested failover correctness or successful inference for every provider.
- Owner confirms Supabase `Narrativ-Forge` (`xrhlefglqwquhvpoevsg`, ap-southeast-1) is canonical production DB; `Narrativ-Forge-1` is a managed-restore smoke-test target.
- Owner reports Alembic migration `0021_revoke_client_grants` is prepared to revoke public-schema privileges from `anon` and `authenticated`. Its live application status was not supplied; do not describe it as applied.
- Explicitly deferred post-launch: continuous background media worker orchestration; human-reviewed dialect-specific Burmese ASR fine-tuning; Qdrant collection scaling and deep RAG ontology.
- Evidence boundary: HTTP responses are owner-provided external-ping results, not independently reproduced by this verifier in this update. Conditional sign-off is a governance/risk-acceptance status, not a claim that every technical gate has independently passed.

## Provider evidence observed

- Render workspace `tea-davm5augekts73ek09kg` lists API service `Narrativ-Forge` and frontend service `narrativ-forge-frontend`; latest deploy records are `live` at commit `207c3979b5fdc6216eb31c15bd82ca2470957e0a`.
- Supabase project `Narrativ-Forge` (`xrhlefglqwquhvpoevsg`, ap-southeast-1) and `Narrativ-Forge-1` (`oeqyheycywqkgeeqmpxa`, ap-northeast-1) both report `ACTIVE_HEALTHY`.
- `Narrativ-Forge` has three Supabase migration records; its queried Alembic revision is `0019_series_bible`.
- `Narrativ-Forge-1` has zero Supabase migration records; its queried Alembic revision is `managed_restore_smoke_v1`.
- Supabase security advisor: 41 RLS-enabled/no-policy findings on `Narrativ-Forge`; on `Narrativ-Forge-1`, two RLS-enabled/no-policy findings and one `public.rls_auto_enable()` SECURITY DEFINER function executable by `anon` and `authenticated`.
- Supabase performance advisor reported 41 unused-index findings on `Narrativ-Forge`; treat as review candidates, not instructions to drop indexes.
- Upstash `Narrativ` database is active, TLS enabled; direct `PING` returned `PONG`.
- Cloudflare account lists `narrativ-forge-edge` and `narrativ-forge-whisper`; script existence does not prove public routing or authenticated inference works.
- Earlier, the external verifier could not fetch the Render endpoints; this update records the owner-provided HTTP 200 evidence separately and does not misrepresent it as independently reproduced.
- No Telegram token was read or exposed; no `getMe` request was made.
- No Qdrant collection was verified.
- No schema, RLS policy, grant, production data, or deployment was modified as part of this verification. GitHub documentation was updated only.

## Conditional sign-off conditions and follow-up

1. Preserve timestamped evidence for owner-reported API health/readiness/AI-usage checks; verify frontend `/` and `/usage` routes separately.
2. Verify the deployed API database target matches canonical Supabase `xrhlefglqwquhvpoevsg`; migration `0021_revoke_client_grants` is prepared, but production application is not evidenced here.
3. Review RLS/table grants and run tenant-isolation regression tests. RLS advisor findings remain a visible security follow-up and are not considered resolved by the migration being prepared.
4. Verify Cloudflare Whisper's authenticated end-to-end contract and test configured storage providers, signed URLs, and object access boundaries.
5. Verify Qdrant and Telegram only if they are intended production dependencies.
6. Run exact-release-SHA CI/security/CodeQL/repository gates and browser/media E2E checks.
7. Post-launch backlog: continuous background media worker orchestration; human-reviewed dialect-specific Burmese ASR fine-tuning; Qdrant collection scaling/deep RAG ontology. Until the worker exists, continuous background processing is not a supported guarantee.

**Launch decision:** **Production Ready — Conditional Sign-Off (Owner-approved launch with explicitly deferred post-launch work).** This is based on owner-reported live HTTP evidence and explicit owner risk acceptance. It is not independent verification of all production gates; canonical DB is owner-confirmed, while migration application, RLS/tenant-isolation closure, frontend/storage acceptance, and authenticated Whisper acceptance still require recorded evidence.


## Render production log audit addendum — 2026-10-17 UTC

This addendum records an independent read-only inspection of the Render workspace services, deployment events, and available application logs. It does not change the owner-approved conditional sign-off decision above, but it narrows what the available evidence supports.

- **Current service inventory:** Render lists the API web service `srv-davrqtu7bikc73f7isbg` (Oregon, free plan, one instance) and frontend web service `srv-db74h5rl550s73ao9ts0` (Singapore, free plan, one instance). No dedicated continuous background worker service was present. Repository `render.yaml` explicitly says long-running Celery/FFmpeg/Whisper workers are intentionally not declared because Render Background Workers are not free. Therefore continuous background media processing remains deferred/unavailable unless an alternate worker path is independently demonstrated.
- **Latest observed deployment events:** API deployment `dep-db9poeqjnfac73d6i0q0` succeeded at 2026-10-17 16:04:37 UTC; frontend deployment `dep-db9pl2brjlhs73fn5k7g` succeeded at 2026-10-17 15:57:24 UTC. The API log included a successful `GET /` (200) after startup and a `GET /api/v1/health` (200) at 16:27:36 UTC.
- **Readiness route discrepancy:** an observed request to `/ready` returned 404 at 16:27:37 UTC. The source defines readiness under the `/api/v1` router, so this does not prove `/api/v1/ready` is failing. A direct HTTP response for `/api/v1/ready` was not independently obtained during this audit; retain the owner's earlier result as owner-reported only.
- **Readiness implementation caveat:** `apps/web-platform/backend/app/api/routes/health.py` marks Redis as `disabled` when `REDIS_URL` is absent and considers `disabled` ready. In an environment where Redis is required for production queues/rate limits, a missing Redis URL could therefore produce a misleading ready state. Verify actual production dependency expectations and configuration; do not infer Redis integration from a green readiness status alone.
- **Previous failed deploys:** Render events show failed API build/deploy attempts on 2026-10-16 at approximately 09:50 UTC and a failed deploy at approximately 10:08 UTC. An error log reports `Could not open requirements file: [Errno 2] No such file or directory: 'web-platform/backend/requirements.txt'`. Later API builds/deploys succeeded. Treat this as a historical path/configuration failure, not proof of a current outage.
- **Runtime configuration drift to reconcile:** Render's live service metadata reports the API runtime as Python, root directory `apps/web-platform`, build command `pip install -r backend/requirements.txt`, start command `cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT`; frontend metadata reports build `cd frontend && npm ci && npm run build` and start `cd frontend && npm run start`. The repository `render.yaml` describes a Docker API service and a standalone-output frontend start command `node .next/standalone/server.js`. This is material deployment-configuration drift. Do not change production settings blindly; reconcile the desired source of truth, then validate a safe deployment plan.
- **Frontend warning:** available logs show Next.js warning that `next start` is not compatible with `output: standalone`; repository `render.yaml` already specifies the standalone server command, but the live Render service metadata still shows `npm run start`. The latest frontend deploy became live, yet this mismatch should be resolved.
- **Historical application responses:** one Google Drive callback request returned 422 and `/favicon.ico` returned 404. These isolated responses do not establish a systemic backend failure.
- **CI evidence:** GitHub combined commit status for the deployed SHA `207c3979b5fdc6216eb31c15bd82ca2470957e0a` returned no status checks. This is absence of check evidence, not a pass.
- **Security boundary:** this audit only read Render/GitHub metadata and logs. It did not update Render settings, deploy, restart services, run migrations, or modify production data/secrets. The canonical Supabase migration and RLS/grant findings remain unresolved until separately verified.

### Required follow-up before stronger sign-off

1. Confirm whether Redis is a mandatory production dependency and, if so, make readiness fail when it is absent or unreachable; add tests for missing URL and failed PING.
2. Reconcile live Render service settings with the intended `render.yaml` and repository layout, especially API root/build path and frontend standalone startup. Apply changes only with a reviewed rollback plan.
3. Verify `/api/v1/ready` and `/api/v1/ai/usage` through a direct external HTTP check and preserve timestamped response bodies with secrets removed.
4. Add or confirm CI checks for the exact deployed commit; no combined status checks were returned for that SHA.
5. Keep the worker, migration, tenant-isolation, storage acceptance, Cloudflare Whisper contract, and Qdrant checks as explicit gates/backlog until evidence is captured.
