# Production Readiness Scorecard — 2026-10-17

**Decision: NO-GO / Production readiness not demonstrated.**  
**Conditional sign-off: NOT GRANTED.** Critical live acceptance evidence is missing and database/security blockers remain. Burmese dialect-specific ASR quality is explicitly deferred post-launch, but the infrastructure/authentication contract still needs verification.

## Evidence and scorecard

| Layer / Component | Target Service / Endpoint | Expected State | Current Result | Action Needed |
|---|---|---|---|---|
| Backend Runtime | Render API `https://narrativ-forge.onrender.com/api/v1/health` | HTTP 200 and expected JSON | **UNVERIFIED** — Render lists service and current deploy as live; HTTP endpoint could not be independently fetched through available verifier | Run direct HTTP GET from an external runner; capture status/body and timestamp |
| Database & Cache | Supabase + Upstash / API `/ready` | DB and Redis connected, HTTP 200 | **PARTIAL** — Upstash database `Narrativ` is active with TLS; direct Redis `PING` returned `PONG`. API `/ready` and live app DB connection unverified | Confirm canonical DB; run external API readiness check and confirm it checks the same DB/Redis |
| AI Failover Router | `/api/v1/ai/usage` | HTTP 200, provider usage/quota tracked | **UNVERIFIED** | Call endpoint and test safe failover/quota behavior for configured providers without burning production quota |
| Canonical Database & Migrations | Supabase projects / `scripts/production_migrate.py` | Confirmed target, Alembic head applied | **BLOCKED** — two projects active; `Narrativ-Forge` shows Alembic `0019_series_bible`; `Narrativ-Forge-1` shows `managed_restore_smoke_v1`. Canonical target not proven | Confirm the live Render `DATABASE_URL` target without disclosing credentials; compare live Alembic revision with repository migration head. Do not run migrations until target is confirmed |
| Tenant Isolation & RLS | Supabase tenant tables | RLS policies and tenant-boundary tests pass | **BLOCKED** — security advisor reported 41 RLS-enabled/no-policy findings on `Narrativ-Forge`; `Narrativ-Forge-1` has two RLS/no-policy findings and exposed `public.rls_auto_enable()` executable by anon/authenticated | Review grants, policies, table access paths, and SECURITY DEFINER privileges; run tenant isolation tests. Do not add permissive policies blindly |
| Cloudflare Whisper | `narrativ-forge-whisper` | Deployed, secret-authenticated remote transcription | **PARTIAL** — Worker script exists (last modified 2026-10-12); route and authenticated end-to-end contract not proven | Verify route, configured shared secret and successful authenticated request. Burmese dialect human-reviewed fine-tuning remains a post-launch quality item |
| Multi-Storage | Supabase Storage / B2 / Cloudinary | Upload, object read, signed URLs valid | **UNVERIFIED** — provider config exists in repo; no live upload/signed URL acceptance evidence | Test each configured provider separately with a non-sensitive test asset; validate expiry, access isolation and deletion/replication behavior |
| Upstash Redis | `Narrativ` | PING, queue/cache behavior works | **PASS — connectivity only** — account state active, TLS enabled, `PING` returned `PONG` | Confirm the deployed API/worker uses this database; exercise queue/rate-limit integration |
| Qdrant Vector Search | Qdrant Cloud | Collection initialized and searchable | **UNVERIFIED / NOT FOUND IN CONNECTED PROVIDER INVENTORY** — no Qdrant connection or collection evidence available from the inspected integrations | Confirm Qdrant is an intended dependency; provide connected Qdrant access or run a credential-safe collection health check |
| Telegram Alert Bot | Telegram Bot API `getMe` | HTTP 200 and verified bot identity | **UNVERIFIED** — bot token is a secret not available to this check; no request performed | Run `getMe` securely from an environment holding `TELEGRAM_BOT_TOKEN`; record bot username only, never token |
| Frontend Web Studio | Render `https://narrativ-forge-frontend.onrender.com/` and `/usage` | HTTP 200 and rendered app | **UNVERIFIED** — Render frontend service/deploy is live at current docs commit; direct HTTP page checks were unavailable | Verify both routes externally and run browser/API integration E2E |
| Background media worker | Render worker / Redis queue | Worker heartbeat and real queued job succeeds | **BLOCKED** — Render service inventory showed only API and frontend; no separate continuous worker service | Provision/confirm worker and demonstrate heartbeat + successful non-mock media job |
| Release commit sync | Render API + frontend | Intended exact commit live | **PASS — deploy metadata only** — both Render services list live deploys at commit `207c3979b5fdc6216eb31c15bd82ca2470957e0a` (docs checklist commit) | Run exact-head CI and runtime E2E; deployment metadata is not a health test |

## Provider evidence observed

- Render workspace `tea-davm5augekts73ek09kg` lists API service `Narrativ-Forge` and frontend service `narrativ-forge-frontend`; latest deploy records are `live` at commit `207c3979b5fdc6216eb31c15bd82ca2470957e0a`.
- Supabase project `Narrativ-Forge` (`xrhlefglqwquhvpoevsg`, ap-southeast-1) and `Narrativ-Forge-1` (`oeqyheycywqkgeeqmpxa`, ap-northeast-1) both report `ACTIVE_HEALTHY`.
- `Narrativ-Forge` has three Supabase migration records; its queried Alembic revision is `0019_series_bible`.
- `Narrativ-Forge-1` has zero Supabase migration records; its queried Alembic revision is `managed_restore_smoke_v1`.
- Supabase security advisor: 41 RLS-enabled/no-policy findings on `Narrativ-Forge`; on `Narrativ-Forge-1`, two RLS-enabled/no-policy findings and one `public.rls_auto_enable()` SECURITY DEFINER function executable by `anon` and `authenticated`.
- Supabase performance advisor reported 41 unused-index findings on `Narrativ-Forge`; treat as review candidates, not instructions to drop indexes.
- Upstash `Narrativ` database is active, TLS enabled; direct `PING` returned `PONG`.
- Cloudflare account lists `narrativ-forge-edge` and `narrativ-forge-whisper`; script existence does not prove public routing or authenticated inference works.
- The external web verifier could not fetch the Render health/readiness/AI-usage endpoints in this run. No endpoint result is claimed.
- No Telegram token was read or exposed; no `getMe` request was made.
- No Qdrant collection was verified.
- No schema, RLS policy, grant, production data, or deployment was modified as part of this verification. GitHub documentation was updated only.

## Release gate / next actions

1. Confirm the canonical production Supabase project and compare it with the deployed API's database target.
2. Review/fix RLS and SECURITY DEFINER exposure with tenant-isolation regression tests.
3. Run direct HTTP checks for API health, readiness, AI usage, frontend `/` and `/usage`.
4. Verify Cloudflare Whisper route + shared-secret authenticated contract.
5. Test configured storage providers, signed URLs and object access boundaries.
6. Confirm Redis use by deployed services and provision/verify a continuous media worker.
7. Verify Qdrant and Telegram only if they are actual product dependencies.
8. Run CI/security/CodeQL/repository gate at exact release SHA and browser/media end-to-end tests.

**Launch decision:** Do not issue “Production Ready — Conditional Sign-Off” yet. Conditional sign-off is inappropriate while canonical database, tenant security, health/readiness, storage acceptance, and worker evidence remain unresolved. Human-reviewed Burmese dialect-specific ASR fine-tuning can remain explicitly deferred after the infrastructure and security gates pass.
