# Infrastructure and repository audit — 2026-10-15

> Scope: read-only provider inspection plus documentation reconciliation. No secrets were read or copied, and no infrastructure, database, deployment, or production data was modified during the audit.
> Repository: https://github.com/dragonknighttw-cmd/Narrativ-Forge
> Audit date: 2026-10-15 UTC

## Executive status

**Release status: PENDING — NOT PRODUCTION READY.**

The newest repository commit visible during this audit is `d370921054b92bbc89b5cf647680543f714c906d` (2026-10-14 17:17:39 UTC; “feat(ui): add intelligent studio launcher with episode selector to narrativ-forge”). Render's latest visible deploys are still on `3b1b3766f2fb132bf4d80203e7174562f2879d9a` (2026-10-13). Render auto-deploy is disabled for both app services, so the currently inspected hosted services are behind the current repository head.

## Provider inventory

### Render — My Workspace

Workspace ID: `tea-davm5augekts73ek09kg`.

| Service | State observed | Configuration / finding |
|---|---|---|
| `Narrativ-Forge` | Latest listed deploy is `live`; latest deploy event reports success | Free Python web service, Oregon; repo `dragonknighttw-cmd/Narrativ-Forge`, branch `main`; build `pip install -r apps/web-platform/backend/requirements.txt`; start `cd apps/web-platform/backend && alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port $PORT`; auto-deploy disabled; public IP allow-list `0.0.0.0/0`. |
| `narrativ-forge-frontend` | Latest listed deploy is `live`; latest build/deploy events succeeded | Free Node web service, Singapore; same repository/branch; build `cd apps/web-platform/frontend && npm ci && npm run build`; start `cd apps/web-platform/frontend && npm run start`; auto-deploy disabled; public IP allow-list `0.0.0.0/0`. |

- Render deploy records and service events are evidence of successful historical deploys, **not** a fresh end-to-end health check or proof of production readiness.
- The frontend service was created 2026-10-13 and has a successful deploy, but its exact live UI/API integration still needs browser E2E verification.
- No separate Render background worker was listed. Real background media execution remains blocked until a worker/runtime is verified.
- Public IP allow-lists are open to all IPv4 addresses. Confirm that this is intentional and rely on application-level authentication/rate limits; narrow access where operationally feasible.
- The Render deploy records show the app services on commit `3b1b3766f2fb132bf4d80203e7174562f2879d9a`, behind the newest repository commit observed. Do not redeploy blindly; first run exact-head CI and owner-approved release checks.

Service links:
- API: https://dashboard.render.com/web/srv-davrqtu7bikc73f7isbg
- Frontend: https://dashboard.render.com/web/srv-db74h5rl550s73ao9ts0

### Supabase

Two active healthy projects were returned:

| Project | Ref | Region | Migrations returned | Advisor result |
|---|---|---|---|---|
| `Narrativ-Forge` | `xrhlefglqwquhvpoevsg` | `ap-southeast-1` | 3 | Security: 40 RLS-enabled tables without policies reported. Performance: 41 unused-index findings reported. |
| `Narrativ-Forge-1` | `oeqyheycywqkgeeqmpxa` | `ap-northeast-1` | 0 | Security: `public.rls_auto_enable()` is SECURITY DEFINER and executable by `anon` and `authenticated`; RLS-enabled tables `public.alembic_version` and `public.organizations` have no policies. Performance advisor returned no lints. |

Important qualifications and actions:
1. Establish which project is authoritative for the deployed application before applying schema changes. The repository's Render deployment uses `DATABASE_URL`; the presence of Supabase projects does not prove the live API uses either one.
2. For `Narrativ-Forge`, investigate the 40 RLS/no-policy findings table by table. This can be intentional for service-role-only access, but must be backed by grants, application architecture, and tests; do not blindly add permissive policies.
3. For `Narrativ-Forge-1`, review/restrict execution privileges for `public.rls_auto_enable()` and confirm intended access for `organizations` and `alembic_version`.
4. The 41 unused-index findings may reflect low usage or a fresh/reset database. Review query plans and representative workload before dropping any index.
5. Reconcile the repository's Alembic migration head with the selected live database. One project returned no Supabase migration records and the other returned three Supabase migration records; these are not themselves proof of the application's Alembic head.

No schema, policies, grants, or data were modified.

### Cloudflare

The connected account lists two Worker scripts:
- `narrativ-forge-edge` — last modified 2026-10-05; standard usage model; no routes shown in the list response.
- `narrativ-forge-whisper` — last modified 2026-10-12; standard usage model; no routes shown in the list response.

The list response did not expose a current deployment ID for either script. This is not enough to verify route/domain wiring, secret presence, authenticated audio transcription, or production behavior. The account connection is authenticated, but Worker settings/deployments and endpoint contract still need focused read-only inspection and a safe non-secret smoke test. Never print secret values.

### Frontend hosting: Vercel / Netlify

- The repository's deployment documentation says Vercel was removed from the intended deployment path and requires explicit owner authorization before re-enabling it.
- The connected Netlify account returned one project, `harmonious-nasturtium-53a1d6`, whose name does not identify it as Narrativ Forge and which requires team SSO. Do **not** assume it is the project's production site without confirming repository/build settings and ownership.
- Render currently has an explicitly named `narrativ-forge-frontend` service. Confirm which public frontend URL is canonical before changing DNS or provider configuration.
- No Vercel project was verified through the available connected provider access in this audit.

## Repository / documentation findings

- The latest repository commit observed is newer than the commits shown in the Render deploy history.
- `CURRENT_STATE.md` and `ROADMAP.md` contain checkpoints dated 2026-10-14, but the leading authoritative checkpoint predates the newest UI commits and does not include the latest hosting/provider audit.
- `docs/DEPLOYMENT.md` is dated 2026-10-09 and `docs/OPERATIONS.md` is dated 2026-10-10; both need current provider state reconciled.
- GitHub code search for `TODO` and `FIXME` returned no matches, but this is not a complete task inventory: open issues/PRs, tests, CI workflow status, and code-level acceptance gaps must also be checked.
- No `docs/SECURITY.md` file was found at that path. The repository has a root `SECURITY.md` (per the engineering workflow read order); ensure the canonical location and links remain consistent.

## Prioritized remaining work

### P0 — Before any production release
- [ ] Run exact-current-head CI, security/CodeQL, repository gate, frontend build/typecheck, backend unit/integration, and E2E; record exact SHA and results.
- [ ] Decide canonical frontend hosting/domain and canonical database/project. Document the mapping without exposing secrets.
- [ ] Resolve the Render deployment drift only after release checks and owner approval; verify frontend and API deploy the intended SHA.
- [ ] Confirm the production API's actual `DATABASE_URL` target via safe configuration metadata (never print its value), then reconcile live Alembic revision and schema.
- [ ] Review Supabase RLS/no-policy findings and the callable `SECURITY DEFINER` function; add focused least-privilege tests before making changes.
- [ ] Provision/verify a continuous real-processing worker, then prove worker heartbeat, broker connectivity, real task completion, output integrity, and PostgreSQL job-state correctness.
- [ ] Run authenticated non-mock real-media E2E including provider behavior, processing failures, retry/DLQ, and fallback behavior.
- [ ] Keep Burmese ASR unaccepted until a dialect-specific reference transcript and human quality review pass.
- [ ] Complete backup/restore drill, accessibility review, privacy/legal/commercial-use sign-off, and independent security sign-off.

### P1 — Hosting / operations hardening
- [ ] Review open IPv4 access lists and add appropriate application-layer controls or narrower allow-lists where possible.
- [ ] Verify Cloudflare Worker deployments, routes/custom domains, safe secret-binding metadata, usage limits, and authenticated Whisper contract without revealing secrets.
- [ ] Confirm whether the Netlify project is unrelated or an intended environment; do not modify it until ownership is confirmed.
- [ ] Confirm alerting, deploy notifications, logs, retention, quotas, and rollback instructions across Render, Cloudflare, and the selected frontend provider.
- [ ] Review the unused-index findings against real workload and query plans before any index removals.
- [ ] Verify storage lifecycle, OAuth/Google Drive, and other external integrations with live evidence.

### P2 — Documentation / maintenance
- [ ] Keep CURRENT_STATE and ROADMAP synchronized with exact-head CI and provider evidence.
- [ ] Keep DEPLOYMENT and OPERATIONS aligned with actual Render services and the selected frontend/database providers.
- [ ] Ensure README links to the canonical status, roadmap, deployment guide, and this audit.
- [ ] Inspect open issues/PRs and workflow runs for incomplete tasks not visible through TODO/FIXME search.
- [ ] Revisit feature acceptance for Studio launcher and other UI commits after frontend E2E.

## Evidence limits

This audit is based on provider API inventory, deployment/event metadata, Supabase advisor and migration responses, repository commit search, and documentation reads on 2026-10-15. It did not read secret values, alter resources, run migrations, redeploy services, perform production-data writes, or establish a complete real-media production acceptance. Items not explicitly tested remain pending/verify.


## Cloudflare detailed settings follow-up — 2026-10-15

Read-only settings/deployment inspection adds these findings:

- `narrativ-forge-whisper` has a latest listed 100% deployment created 2026-10-12, Workers subdomain enabled, and one secret binding named `NARRATIV_SHARED_SECRET`. Secret values were not retrieved or logged.
- Whisper's `ALLOWED_ORIGIN` plain-text binding is `https://harmonious-nasturtium-53a1d6.netlify.app`, which matches the unverified Netlify site returned by the connected account. This does **not** match the named Render frontend URL. Confirm the canonical frontend and update CORS origin only through a reviewed, owner-approved change after identifying the intended site; do not change it during a read-only audit.
- `narrativ-forge-edge` has a latest listed 100% deployment created 2026-10-03, Workers subdomain enabled, and no secret bindings returned. Its script settings returned no bindings. Confirm this is expected for the edge worker and verify its endpoint contract.
- Both Workers have `logpush=false`; assess whether available observability and alerting are sufficient for release.
- Public URL requests through the available web inspection path could not be fetched, so no fresh HTTP health/endpoint result is claimed here. Use an authenticated, safe smoke test in the runtime or provider logs.
