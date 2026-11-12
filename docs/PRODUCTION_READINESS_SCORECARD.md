# Current release decision — 2026-11-12 (supersedes historical sections below)

**Decision: NOT READY FOR GENERAL PRODUCTION RELEASE.** The production API and frontend are live on Render Free, and the current main-branch verification suite is green. Several owner-gated provider integrations and real production workflows still lack end-to-end evidence. Do not describe them as complete until the evidence listed below is obtained.

## Current main and verification

- Main commit: `22d5198b3ffe582fe6ead1ce59fc5d07d88ce8ab` (PR #142, squash-merged).
- PR #142 fixes the Cloudflare Whisper live-evidence client by adding a descriptive application User-Agent to both POST requests. Cloudflare documents that the default Python urllib User-Agent is blocked by Browser Integrity Check on `workers.dev`; the application-specific User-Agent is the documented remediation.
- Main-commit GitHub runs all passed:
  - CI: [43182865101](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/43182865101)
  - Production Quality & Verification Pipeline: [43182864931](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/43182864931)
  - Production HTTP Smoke: [43182865187](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/43182865187)
  - CodeQL: [43182865026](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/43182865026)
  - Security (SAST, dependency audit, container scan): [43182865308](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/43182865308)
  - Repository Gate: [43182865126](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/43182865126)
- PR #132 (`security/phase1-production-release-20261110`) is closed without merging because it was conflicted and reintroduced unrelated Telegram topic routing. PR #142 is merged. No application-code PRs are open; documentation refresh PR #143 is in progress. A merged/closed branch may remain because the connected GitHub tools do not expose branch deletion.
- GitHub branch protection remains intentionally skipped per owner instruction.

## Render production services

- API `Narrativ-Forge`: service `srv-davrqtu7bikc73f7isbg`, Free plan, one instance, auto-deploy on `main`, latest live application commit `ced3cb8e05bf88159995a2c40470db032b86bb26`.
- Frontend `narrativ-forge-frontend`: service `srv-db74h5rl550s73ao9ts0`, Free plan, one instance, auto-deploy on `main`, latest live application commit `ced3cb8e05bf88159995a2c40470db032b86bb26`.
- PR #142 changes only the GitHub evidence workflow, not application runtime source; no Render redeploy was needed for that documentation/workflow-only merge.
- API Render logs repeatedly show `GET /api/v1/ready` returning HTTP 200. Frontend build and Next.js server startup completed successfully. Production HTTP Smoke on main commit 22d5198 passed.
- Render connector does not expose service environment-variable values. Do not claim secret values are verified from the connector; verify presence privately in the Render Dashboard.

## Current provider and database posture

- Supabase project `xrhlefglqwquhvpoevsg`: Health Advisor has 0 findings. Security Advisor has 44 informational RLS-enabled/no-policy findings and the accepted Free-plan leaked-password-protection warning. Performance Advisor has 42 unused-index suggestions. All 44 public tables have RLS enabled; prior direct-grant audit found zero direct anon/authenticated public table grants. Keep the no-policy posture deny-by-default; do not add blanket policies or drop unused-index candidates without workload evidence.
- Upstash Redis `Narrativ`: Free, active in `ap-southeast-1`, TLS enabled, ACL enabled, auto-upgrade disabled; live `PING` returned `PONG`.
- Cloudinary: Free plan; 64 resources, approximately 177.5 MB storage, 0.17 of 25 credits used (0.68%). The prior temporary authenticated-upload test was deleted. Future app-managed assets use authenticated delivery and signed URLs.
- Cloudflare `narrativ-forge-edge`: latest deployment 2026-11-12 05:55 UTC; exact frontend `ALLOWED_ORIGIN` and API `API_ORIGIN` bindings; preview URLs disabled.
- Cloudflare `narrativ-forge-whisper`: AI binding, encrypted `NARRATIV_SHARED_SECRET` binding, exact frontend origin, preview URLs disabled. Its latest live deployment is still version 17 from 2026-10-17; the source has not been redeployed through the protected workflow.
- The non-billable Whisper preflight run [43179737455](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/43179737455) succeeded previously and reached the Worker handler. This is not proof of authenticated inference.
- The updated live-inference workflow has not been run. It requires a manual `confirm_live_inference=true` input and consumes a small amount of Workers AI Free quota. The protected deployment workflow separately requires `confirm_render_secret_synced=true`. The GitHub connector cannot inspect GitHub Environment secret values, and Render environment values are not readable through the Render connector. Owner must privately verify the production GitHub secret presence/value alignment before dispatching the deployment workflow.
- Cloudflare account-level 2FA enforcement remains deferred per owner instruction.

## Telegram and AI

- Narrativ Forge Telegram routing remains restricted to chat `-1003992125718`, topic `6`; do not add the other projects' topics.
- `/start` and `/ai_status` were previously verified live in topic 6. Unit/integration tests for webhook authorization, topic isolation, callback idempotency, and script approval passed in current CI.
- Live `/ai_test`, Approve/Reject callback execution, and cross-account Telegram authorization still require an actual topic-6 bot interaction; do not claim these are live-verified.
- OpenRouter remains the configured AI provider with the application's Free-model allowlist. An authenticated app-level `/ai_test` remains pending. Do not enable paid fallbacks or paid overage.

## Remaining owner-gated release work

1. Verify the GitHub `production` environment contains `CLOUDFLARE_WHISPER_WORKER_URL` and `CLOUDFLARE_WHISPER_SHARED_SECRET`, and that the shared secret matches the existing Render and Cloudflare values. Then manually dispatch the protected Cloudflare Whisper deployment workflow with `confirm_render_secret_synced=true`.
2. Manually dispatch Cloudflare Whisper Live Evidence with `confirm_live_inference=true` only when ready to consume one small Free Workers AI request. Confirm the artifact records unauthenticated HTTP 401 and authenticated HTTP 200 with matching episode identity. Until then, authenticated Whisper remains unverified.
3. Register `https://narrativ-forge.onrender.com/api/v1/drive/google/callback` in Google Cloud Console and complete OAuth. Current `google_drive_connections` count is 0.
4. Supply B2 credentials privately if B2 is intended, then complete upload/download/checksum/restore tests. Current `storage_replicas` count is 0; do not claim B2 lifecycle acceptance.
5. In Telegram topic 6, live-test `/ai_test` and one Approve/Reject callback. Keep all other topics ignored.
6. Complete an authenticated app-level OpenRouter Free-model smoke. Do not enable paid providers.
7. Keep Cloudflare 2FA deferred and GitHub branch protection disabled as explicitly requested. Keep the Supabase Free-plan leaked-password-protection warning documented.

## Release boundary

CI, static analysis, security scans, production HTTP smoke, Render Free service health, Supabase health, Upstash PING, and Cloudinary Free usage are verified. Full production acceptance is still blocked by owner-controlled OAuth/secret configuration and live provider workflows. The application should not be advertised as fully production-ready until those gates have current evidence.

---

# Production Readiness Scorecard — 2026-11-12

## Final status update — 2026-11-12

### Completed and live
- GitHub branch protection remains intentionally skipped per owner instruction; issue #123 is closed as not planned.
- Supabase project-owned database security review is complete: zero direct anon/authenticated public table grants, all 44 public tables RLS-enabled and postgres-owned, postgres default ACLs restricted, private Storage bucket. The 44 no-policy advisor findings are intentional deny-by-default; leaked-password protection remains the documented Free-plan exception; supabase_admin default ACLs are vendor-managed.
- Telegram PR #135 is merged. The current Telegram integration, tests, docs, and project overview contain only the Narrativ Forge topic route. Render API env is set to the configured group and topic 6. Startup logs confirm the Telegram webhook, command menu, and menu button were configured successfully.
- Cloudflare Edge Worker is live with strict HTTPS origin allowlisting, credentialed CORS, the frontend's Idempotency-Key header, security response headers, and explicit Render API/frontend bindings. Preview URLs are disabled for both Workers; workers.dev production endpoints remain enabled.
- Render API and frontend services are both Free plan and live on commit 4da425cf36ee987e63fcb863993d9b56634b285c. API /api/v1/ready and /api/v1/health returned HTTP 200; unauthenticated /api/v1/ai/usage returned 401. No error/fatal application logs were observed after rollout.
- Render API environment was updated with the production Google OAuth callback, frontend base URL, frontend CORS origin, Telegram group/topic 6 settings, and Free-only AI provider flags.
- Cloudinary PR #138 is merged and live on the API service. Future app assets use authenticated delivery and signed URLs, with correct image/video/raw resource types. A temporary authenticated upload test succeeded on the Cloudinary Free account and was deleted.
- Upstash Redis Narrativ database is Free, active in ap-southeast-1, TLS and ACL enabled, auto-upgrade disabled; PING returned PONG and DBSIZE returned 0.
- One Cloudflare Workers AI free-tier smoke succeeded using 0.2776 Neurons. Cloudflare's Free allocation is 10,000 Neurons/day; daily limit exhaustion on Workers Free returns a rate-limit error rather than silently upgrading to paid usage.

### Pending owner-gated work
- Cloudflare account-level 2FA enforcement remains off because the sole member has not enrolled 2FA. Owner must enable authenticator/security-key 2FA first.
- Whisper Worker source/tests/config are merged, but live redeployment is withheld until the owner confirms the Render and GitHub production shared secrets match. The manual workflow requires that explicit confirmation.
- Google Drive connection table contains 0 connected accounts. Render callback is configured as https://narrativ-forge.onrender.com/api/v1/drive/google/callback; owner must register that exact URI in Google Cloud Console and complete OAuth connection.
- B2 upload/download/checksum/restore lifecycle has not been live-verified. Render environment values are not exposed through the connected Render tools, so do not claim B2 credentials or Render-to-Upstash wiring are verified.
- Chat-provider flags for Groq, Gemini, Mistral, Cohere, NVIDIA, and Cloudflare AI are disabled until account-level Free eligibility is verified. OpenRouter remains the configured provider with the application's free-model allowlist; an authenticated app-level /ai_test is still required.
- PR #140 is open and its live Edge Worker change is already deployed. It adds the Idempotency-Key and credentialed CORS contract to source and regression tests; merge only after all required checks pass.
- Telegram forum topics and their historical messages were not deleted. The Narrativ bot ignores all topics except topic 6. Telegram command-menu scopes are group-level rather than per forum topic, so the Narrativ command menu may remain visible in other topics even though commands there are ignored.

### Remaining release actions
1. Owner enables Cloudflare member 2FA; then account enforcement can be enabled.
2. Owner confirms Render and GitHub Whisper shared secrets match; then the protected Whisper deployment can proceed.
3. Owner registers the Google OAuth redirect URI and connects Drive.
4. Owner tests /start, /ai_status, and /ai_test in Telegram topic 6; commands outside topic 6 must be ignored.
5. Merge PR #140 after all checks pass.
6. Complete a live B2 lifecycle and backup/restore test, plus authenticated app-level Cloudinary upload/download verification.
7. Keep GitHub branch protection skipped and do not upgrade any service to a paid plan.

---

## Live verification addendum — after topic and Cloudflare hardening

### GitHub
- The owner explicitly chose to skip main branch protection. Issue #123 is closed as not planned; no protection settings were changed.
- PR #135 (Telegram topic isolation) and PR #137 (Cloudflare CORS hardening) are merged to main.
- PR #138 (authenticated Cloudinary delivery) is open with all core CI/security checks passed; the final Real Worker Evidence check is still running.

### Supabase database and Storage
- Project xrhlefglqwquhvpoevsg remains on the Free plan.
- Direct anon/authenticated public table grants: 0. All 44 public tables have RLS enabled and are postgres-owned. There are 2 postgres-owned sequences and 1 postgres-owned public function.
- No public RLS policies exist. This is intentional deny-by-default for the backend-mediated app; do not add blanket policies.
- Supabase Security Advisor reports 44 informational rls_enabled_no_policy findings and the expected Free-plan leaked-password-protection warning. Health Advisor has no findings. The leaked-password warning remains an accepted Free-plan exception.
- supabase_admin default ACLs are vendor-managed; current project objects are postgres-owned and project postgres defaults are restricted. Issue #98 is closed with the official Supabase KB explanation.
- Storage bucket narrativ-forge is private; no Storage policies are present, so direct Data API access remains denied.

### Cloudflare
- Edge Worker narrativ-forge-edge is live with explicit HTTPS API_ORIGIN and ALLOWED_ORIGIN bindings, strict exact-origin CORS, and security response headers.
- Preview URLs are disabled for both Edge and Whisper Workers. Production workers.dev endpoints remain enabled because no custom routes were found and disabling them could break the gateway.
- Whisper Worker source, tests, and Wrangler origin config are merged. Its live deployment is intentionally withheld until the owner confirms Render CLOUDFLARE_WHISPER_SHARED_SECRET matches the GitHub production secret; the manual workflow enforces that confirmation.
- Account-level two-factor enforcement is still off because the sole account member has not enrolled 2FA. Owner enrollment is required before enabling enforcement.
- A direct Workers AI free-tier smoke returned OK using 0.2776 Neurons. Cloudflare documents 10,000 Neurons/day free on Workers Free; exceeding the daily limit on Free causes requests to fail rather than requiring paid usage. Do not upgrade.

### Telegram
- PR #135 is merged. The Telegram webhook route is permanently bound to Narrativ Forge topic 6; the multi-project routing table and retired project names were removed from the route, regression tests, integration guide, and project overview.
- The bot ignores unconfigured topics before authorization, command handling, callback handling, or project-data access.
- Render API environment is set to the Narrativ group chat and topic 6 only. After rollout, startup logs confirm the Telegram webhook and command menu were configured successfully for the Narrativ Forge group.
- Telegram forum topics and historical messages in the group were not deleted; only Narrativ Forge bot routing/configuration was removed.

### Render
- API and frontend services are both Free plan, one instance each, and are live on main commit 121723812b1df06a1ff31cec621be16db0192e4f.
- API /api/v1/ready and /api/v1/health returned HTTP 200 after rollout. The protected /api/v1/ai/usage endpoint returned 401 without authentication.
- No error/fatal application logs were observed in the reviewed rollout window.
- API environment was updated with the production Google OAuth callback, frontend base URL, frontend CORS origin, Telegram group/topic 6 settings, and conservative Free-only AI provider flags.

### Storage, Google Drive, Redis, and AI
- Cloudinary is on Free: 64 listed objects, approximately 177.5 MB storage, and 0.17 of 25 credits used. The returned existing assets were Cloudinary sample/demo assets; none of the listed assets used the app's episodes/... key namespace.
- A temporary 1x1 PNG upload using type=authenticated succeeded on the Cloudinary Free account and was deleted successfully. PR #138 changes future app-managed uploads to authenticated delivery, uses signed URLs, and correctly routes images/videos/raw files. No existing sample assets were modified.
- Upstash Redis database Narrativ is Free, active in ap-southeast-1, TLS enabled, ACL enabled, auto-upgrade disabled. Read-only smoke: PING=PONG, DBSIZE=0. Render-to-Upstash wiring is not independently verified because Render does not expose environment-variable values through this connector.
- Google Drive connection table currently contains 0 connected accounts. Render now has the production callback URI https://narrativ-forge.onrender.com/api/v1/drive/google/callback and frontend base URL; the owner must register the exact redirect URI in Google Cloud Console and complete OAuth consent/connection.
- Chat provider use is restricted to OpenRouter free-model allowlisting; Groq, Gemini, Mistral, Cohere, NVIDIA, and Cloudflare chat-provider flags were set false until their account-level Free eligibility is verified. Cloudflare Whisper remains a separate Workers AI binding.
- B2 live upload/download/checksum/restore lifecycle is not yet verified. Do not claim full hybrid-storage acceptance until real B2, Cloudinary, and Supabase round trips have evidence.

## Remaining owner / release actions
1. Enable 2FA on the Cloudflare account member; then account-level enforcement can be enabled.
2. Confirm the Render and GitHub production Whisper shared secrets match; then run the manual Whisper Worker deployment workflow.
3. Register the production Google OAuth callback in Google Cloud Console and connect the owner's Drive account.
4. Wait for the latest Render API/frontend deployments to finish, then verify /api/v1/ready, /api/health, and test Telegram /start, /ai_status, and /ai_test in topic 6.
5. Merge PR #138 only after every required check, including Real Worker Evidence, passes; then verify authenticated Cloudinary app upload/download.
6. Complete live B2 lifecycle and storage backup/restore evidence.
7. Complete one authenticated app-level OpenRouter free-model smoke. Do not enable paid fallbacks.
8. Keep GitHub branch protection skipped per owner instruction and the Free-plan leaked-password exception documented.

---

**Current decision: NOT READY FOR GENERAL PRODUCTION RELEASE.** Supabase public-schema access is restrictive. Telegram is being reduced to the single Narrativ Forge topic. Both Render services are live on the latest main commit and remain on Free plans. Cloudflare edge CORS and preview exposure have been hardened; account MFA and owner-side Google Drive/provider acceptance remain open. GitHub branch protection is intentionally skipped at the owner's request.

## Current verification addendum — 2026-11-12

### Supabase database security — verified posture

- Canonical project `xrhlefglqwquhvpoevsg` is ACTIVE_HEALTHY on PostgreSQL 17.11.
- Direct grants to `anon` and `authenticated` on public tables: **0**.
- Public schema objects observed: 44 tables, 2 sequences, and 1 function; all are owned by `postgres`. No current public object is owned by `supabase_admin`.
- All 44 public tables have RLS enabled. No public RLS policies exist. This is intentionally deny-by-default for Data API roles in the backend-mediated architecture; do not add blanket policies.
- `postgres` default ACLs in `public` restrict future tables, sequences, and functions to `postgres` and `service_role`.
- `supabase_admin` default ACL entries still include Data API roles. Supabase documents these as reserved platform defaults that cannot be changed by the project `postgres` role; they apply to objects created by `supabase_admin`, not objects created by the project's `postgres` role. Supabase states its services do not create user tables/views/functions in `public` as `supabase_admin`. Current public objects are all postgres-owned. Treat this as vendor-managed platform behavior, not an actionable project ACL change. Reference: https://supabase.com/kb/troubleshooting/cant-change-the-default-privileges-of-supabase_admin-in-the-public-schema-448af9
- Supabase Storage bucket `narrativ-forge` exists and is private, with a 50 MiB file-size limit. No Storage policies were found; this remains deny-by-default for direct client access. Backend service-role access must continue to be used for private objects.
- Google Drive connection rows: **0**. OAuth implementation exists, but no account is currently connected.
- Leaked Password Protection remains excluded per the owner's Free-plan constraint.

### Cloudflare security — verified account and worker state

- Account-level `enforce_twofactor` is false; the sole account member currently has 2FA disabled. Do not enable account enforcement until the owner enables 2FA on the account first.
- `narrativ-forge-whisper` has the AI binding, an encrypted secret binding, and the exact Render frontend origin in `ALLOWED_ORIGIN`. Preview URLs are disabled.
- `narrativ-forge-edge` was redeployed on 2026-11-12 with explicit HTTPS API and frontend origin bindings. It rejects non-allowlisted browser Origins, handles preflight only for the exact frontend origin, and emits allowlisted CORS headers on actual responses. Preview URLs are disabled. The workers.dev endpoint remains enabled because no custom Worker route was found; disabling it could break the live gateway.
- Cloudflare account-level two-factor enforcement remains off because the sole account member has not yet enabled 2FA. The owner must enroll an authenticator/security key before account enforcement can be safely enabled.
- Workers AI has a Free allocation of 10,000 Neurons/day; do not enable paid overage or upgrade. See https://developers.cloudflare.com/workers-ai/platform/pricing/

### Telegram — pending release

- PR #135 is being hardened so the bot is permanently bound to the Narrativ Forge topic only. Retired project names and multi-topic routing are removed from the Telegram route, tests, integration guide, and project overview. A generic unconfigured-topic regression test remains.
- PR #135 is not merged; CI is still running. Telegram forum topics and their historical messages are not deleted.

### Remaining release gates

1. GitHub branch protection is intentionally skipped per the owner's explicit instruction and is not part of this release work.
2. Complete Cloudflare owner MFA enrollment, then enable account-level two-factor enforcement.
3. Verify both Render services' health endpoints and current error logs, then verify secret environment-variable presence from the Render Dashboard (values must not be copied into source or chat).
4. Complete owner-side Google Drive OAuth connection and free-provider live acceptance where credentials/consent are required.
5. Merge PR #135 only after CI passes; then verify the single-topic commands and callback actions on the live Telegram bot.
6. Keep the Free-plan leaked-password-protection exception documented.

---

# Historical Production Readiness Scorecard — 2026-11-10

**Current decision: NOT READY FOR GENERAL PRODUCTION RELEASE.** PR #131 was merged to `main` as `498560ed04b3c5ea9fa30d049079b7444e4c889c`. Both free Render services are live on that commit. The post-deploy smoke check was corrected and passed in PR #134; final CI on PR #134 is pending.

## Current verification addendum — 2026-11-10

### Repository and candidate evidence

- **Current main commit:** `498560ed04b3c5ea9fa30d049079b7444e4c889c` (merged PR #131).
- **Consolidated PR:** [#131 — Security hardening: production safeguards and free Kaggle worker](https://github.com/dragonknighttw-cmd/Narrativ-Forge/pull/131), merged. Its Nov 9 evidence addendum is preserved in this scorecard. Earlier duplicate PRs #125–#130 were closed as superseded.
- **Local backend non-integration suite:** 384 passed, 78 deselected.
- **Focused backend security/unit suite:** 351 passed, 3 skipped, 108 deselected.
- **Kaggle dispatcher tests:** 8 passed. Frontend TypeScript check, Playwright test discovery, production build, Python compileall, and git diff --check passed locally.
- **GitHub checks on the exact candidate head `26a3de25cb2b1a1564a3caf2d6696269f3851d35`:** CI backend, backend integration, frontend, Cloudflare Whisper contract tests, and E2E passed; SAST, dependency audit, container scan, CodeQL, Repository Gate, application schema restore, backup/restore, Linux and Windows runtime evidence, Windows portable package, and Production HTTP Smoke passed. Real Worker Evidence run #475 also passed through worker image build, migration test, shared storage checks, retry/DLQ and tenant integration, worker startup, real-media smoke, and redacted evidence collection. A duplicate run was cancelled; the successful exact-head run is #475.

### Render production deployment boundary

- **API service:** Narrativ-Forge, free plan, autoDeploy enabled, live deploy `dep-dbpdhafavr4c73eja61g` on commit `498560ed04b3c5ea9fa30d049079b7444e4c889c`.
- **Frontend service:** narrativ-forge-frontend, free plan, autoDeploy enabled, live deploy `dep-dbpdhafavr4c73eja840` on the same commit.
- The API start command runs Uvicorn directly; it does not run Alembic migrations. Migration 0025 was applied and verified before this deployment.
- Post-deploy Render application logs contained no error/fatal entries in the checked window. Production HTTP Smoke run #162 passed the live frontend/API checks, including the anonymous AI-usage 401 guard.

### Supabase schema and security boundary

- **Project:** xrhlefglqwquhvpoevsg, active/healthy, PostgreSQL 17.11.
- **Live Alembic revision:** `0025_usage_event_org_idempotency`, applied and verified on 2026-11-10.
- **Supabase migration ledger:** entry `20261110083526` (`usage_event_org_idempotency_0025`) is present.
- **Current usage_events uniqueness:** `uq_usage_event_org_idempotency` enforces `UNIQUE (organization_id, idempotency_key)`; the former global key constraint is absent.
- **Current usage_events rows:** 0 at migration time; the pre-migration duplicate organization/idempotency-pair check returned 0.
- **Security advisor:** 44 public tables have RLS enabled but no policies (INFO); prior grant review found no direct anon/authenticated table or function grants. Do not add blanket client policies.
- **Performance advisor:** 43 unused-index candidates. Do not drop indexes without workload and query-plan evidence.
- **Leaked Password Protection:** remains excluded from this project's P0 scope per the owner's Free-plan constraint.
- **Supabase admin default ACL remediation (issue #98) remains open; no privileged ACL changes were attempted.

### Free worker decision

- No paid Render worker or paid resource was created.
- The selected free path is the opt-in hourly Kaggle one-job worker, not a continuously available worker.
- The dispatcher pins the exact triggering Git SHA; the kernel verifies that checkout, clones the public repository without a GitHub token, installs pinned real-processing dependencies, checks ffmpeg/ffprobe, and requires durable Cloudinary, B2, or hybrid storage.
- No production Kaggle dispatch was launched. GitHub Actions variables/secrets and Kaggle kernel Secrets were not verified or changed; owner-side configuration is still required before enabling dispatch.

### Remaining release gates

1. Complete all PR #134 checks after its final workflow fixes, then merge it. Its changes update the smoke test to assert the anonymous AI usage endpoint returns 401, fix invalid YAML in the legacy production pipeline, and fix two Flake8 findings.
2. Enable and verify GitHub `main` branch protection/required checks through an authorized repository administrator; the connected GitHub actions do not expose a branch-protection write operation.
3. Resolve Supabase `supabase_admin` default ACLs through a supported owner/admin route. Current `postgres` connection is neither superuser nor a member of `supabase_admin`; all 44 public tables are owned by `postgres`, and no current public functions are owned by `supabase_admin`. Do not attempt ownership bypasses or protected-catalog edits.
4. Complete owner-side Telegram topic/action tests, storage acceptance, Google Drive OAuth, and provider smoke tests.
5. Configure GitHub Actions variables/secrets and Kaggle kernel Secrets through the owner UI; production Kaggle dispatch remains disabled until verified and explicitly enabled. No paid Render worker or paid resource was created.
6. Cloudflare account `enforce_twofactor` is false, and the sole account member currently has 2FA disabled. Enable MFA on that member before enabling account enforcement to avoid lockout. The live edge Worker is workers.dev-enabled, has permissive Origin reflection and a hard-coded upstream; repository config still has a placeholder API origin. The live Whisper Worker allows the Render frontend origin, while its repository config still lists the old Netlify origin. Source/config reconciliation and a controlled Worker deployment remain open.
7. Keep the Supabase Free-plan leaked-password-protection exception documented and risk-accepted.

**Current decision remains NOT READY for general production sign-off.** The primary security release is merged and both Render services are live, but branch governance, Cloudflare account MFA/Worker drift, owner-side acceptance, and free Kaggle production secrets remain open.

---

# Historical Production Readiness Scorecard — 2026-11-09

**Current decision: NOT READY FOR GENERAL PRODUCTION SIGN-OFF.** The app deployment and repository CI are green, but security ownership, branch governance, and several live provider acceptance gates remain open.

## Historical verification addendum — 2026-11-09

### Deployment and repository evidence

- **Main commit:** `9067494e7eb56c7aba3e0b582563616453459f31` (PR #120, Character Studio durable registry).
- **GitHub CI:** all 18 check runs on this exact commit completed successfully, including backend, backend integration, frontend, E2E, dependency audit, SAST, container scan, PostgreSQL backup/restore, application schema restore, real-worker E2E, public frontend/API smoke, and Repository Gate.
- **Render API:** service `Narrativ-Forge` deploy for the exact commit is `live`; configured health path is `/api/v1/ready`.
- **Render frontend:** service `narrativ-forge-frontend` deploy for the exact commit is `live`; configured health path is `/api/health`.
- **Render configuration review:** both services use the expected `apps/web-platform` root. The API runtime/start command and frontend standalone Next.js start script were checked against the repository configuration. No production service settings were changed during this review.
- **Render log window:** from 2026-11-09 09:00 UTC through approximately 10:02 UTC, the queried API/frontend app error/fatal logs and HTTP 5xx request logs returned no matching entries. This is a bounded log observation, not a load or availability guarantee.
- **Open PRs:** none were returned by the connected repository query. Open follow-ups are tracked in issues [#98](https://github.com/dragonknighttw-cmd/Narrativ-Forge/issues/98) and [#123](https://github.com/dragonknighttw-cmd/Narrativ-Forge/issues/123).

### Supabase production database and access boundary

- **Canonical project:** `xrhlefglqwquhvpoevsg`.
- **Alembic revision:** `0024_character_registry`.
- **Character Studio registry:** `public.character_registry` exists; the current row count is 0, matching the owner's confirmation that no old Character Studio records needed preservation.
- **Registry security:** RLS is enabled. Direct table grants to `anon` and `authenticated` are absent.
- **Public schema direct grants:** current queries returned 0 direct `anon`/`authenticated` table grants, 0 function grants, and 0 sequence grants.
- **RLS advisor:** 44 public tables have RLS enabled and no policies. This is an INFO finding in this backend-mediated architecture; do not add blanket client policies. Continue table-by-table authorization review.
- **Default ACL residual — OPEN, issue #98:** `postgres` defaults for tables, sequences, and functions are restricted to `postgres` and `service_role`. However, `supabase_admin` defaults still include `anon` and `authenticated` privileges for tables (`r`), sequences (`S`), and functions (`f`). The live session is `postgres`, not a member of `supabase_admin`; no supported owner-role path is available through this connection. Do not attempt ownership bypasses or protected-catalog edits. Obtain Supabase-supported owner/admin remediation or Support guidance, then verify the ACLs and rerun auth/API regression checks.
- **Leaked Password Protection:** remains excluded from this project's P0 scope per the owner's Free-plan constraint.
- **Performance advisor:** reports unused-index candidates. Do not drop indexes solely from advisor output; collect representative workload and query-plan evidence first.

### Repository governance — OPEN, issue #123

- GitHub branch metadata reports `main` as unprotected, with required status checks disabled.
- The connected GitHub integration does not expose a branch-protection write action; the branch-protection API read was denied. No repository settings were changed.
- An authorized GitHub admin should enable a ruleset for `main`: require PRs, require the successful current CI checks, block force pushes and deletion, and verify the ruleset with a test PR.

### Remaining production acceptance gates

1. Resolve Supabase `supabase_admin` default ACLs through an authorized owner/admin route; verify table, sequence, and function defaults afterward.
2. Enable and verify GitHub `main` branch protection / required checks through an authorized repository-admin route.
3. Complete owner-side live Telegram smoke tests: `/start`, `/status`, and `/ai_status` in topics 2, 5, 18, and 7; verify full Narrativ commands and approval callbacks only in topic 6. Automated handler tests and deployment are not a substitute for a real Telegram interaction.
4. Verify storage provider upload/download, signed URL expiry, access isolation, and deletion behavior with non-sensitive test assets.
5. Verify authenticated Cloudflare Whisper end-to-end behavior only under an owner-approved, quota-aware test. Do not trigger live inference or paid resources without explicit approval.
6. Keep background media-worker orchestration outside production guarantees until a persistent worker and a real queued-job acceptance test exist; current Render topology has only API and frontend free services.
7. Preserve the limitation that AI usage counters are process-local until usage/quota events are durably stored; do not treat those counters as an audit-grade billing ledger.
8. Complete any required AI failover, OAuth/Drive, SMTP, Stripe, accessibility, load, rollback, and independent security testing before general production sign-off.

**Historical Nov 9 decision:** the app commit recorded in this snapshot was merged and its 18/18 checks were green. General production sign-off remained **NOT READY** until the security, governance, and provider acceptance gates were verified or explicitly risk-accepted.

---

# Production Readiness Scorecard — historical baseline (2026-10-21)

**Current decision: NOT READY FOR GENERAL PRODUCTION SIGN-OFF.** The 2026-10-17 conditional sign-off below is historical and superseded by the current deployment, database, and security evidence recorded here.

## Current verification addendum — 2026-10-21

- **Public HTTP smoke:** GitHub Actions Production HTTP Smoke runs #29 and #31 passed the frontend health endpoint, frontend homepage, backend health/readiness, and AI usage checks. Run #31 passed after merged commit `69cdeb8f09d3cb254db7589915f6fc1a4862f5fa` was deployed live by Render deployment `dep-dbc7ibo473hc73a3tj3g` at 2026-10-21 08:36:29 UTC. This is external-runner evidence that the checked endpoints responded successfully after the frontend fix.
- **Frontend/API Auth configuration:** Render frontend now has `NEXT_PUBLIC_API_BASE_URL=https://narrativ-forge.onrender.com/api/v1`, the canonical Supabase project URL, and its active public anon key configured. Backend Render now has `CORS_EXTRA_ORIGINS=https://narrativ-forge-frontend.onrender.com` and `FRONTEND_BASE_URL` set to the same frontend origin. Frontend deployment `dep-dbc7ko7avr4c73f4jegg` went live at 2026-10-21 08:41:39 UTC; backend deployment `dep-dbc7lbbbc2fs73biqscg` went live at 08:42:28 UTC. These values are public client/configuration values; no service-role key was changed.
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


## Production follow-up evidence — 2026-10-21 (after PR #106)

### Authentication and runtime

- **PR #106 merged:** commit `891aa8b14f93daeff3402df266b1afc682017ce0`, changing production session-cookie SameSite behavior to `None` while retaining the configured Secure flag. This addresses the cross-site frontend/API cookie issue.
- **Render API deployment:** `dep-dbc8baek1f9s73bse8a0` is `live`; Render build logs report successful build and service live at 2026-10-21 09:29:28 UTC.
- **Render frontend deployment:** service became live at 2026-10-21 09:29:45 UTC. Its live health-check path is `/api/health`; runtime logs show Next.js standalone server startup.
- **Post-deploy request evidence:** API logs recorded `POST /api/v1/auth/supabase-login` HTTP 200 at 09:30:15 UTC, followed by `GET /api/v1/auth/me` HTTP 200 at 09:30:17 UTC and repeated `/auth/me` HTTP 200 responses through 09:31:02 UTC. `GET /api/v1/brain/soul/status` also returned HTTP 200 at 09:30:20 UTC. The owner subsequently confirmed that Dashboard access now works.
- **Scope boundary:** these logs establish successful login/session validation and a dashboard-related API call; they do not independently prove every dashboard feature or every provider integration works.

### Canonical Supabase state rechecked

- Live Alembic revision is `0023_brain_soul_dedupe`.
- Read-only grant query returned no existing `public` table privileges for `anon` or `authenticated`.
- Security Advisor currently reports 43 tables with RLS enabled and no policies. With current direct table grants absent, this is restrictive for direct client access, but it does not replace backend authorization and tenant-isolation regression tests.
- **Open security residuals:** `supabase_admin` default ACLs still grant table, sequence, and function privileges to `anon`/`authenticated`; the current SQL session cannot alter those defaults because it is not a member of `supabase_admin`. Supabase Auth leaked-password protection is still disabled (Security Advisor warning). These require an authorized administrator/configuration change and a follow-up verification.
- Performance Advisor lists 44 unused-index candidates. Do not drop them without workload review and query-plan evidence.

### Remaining release gates

1. Add and run API-level tenant-isolation tests, including cross-organization reads/writes and unauthorized resource IDs.
2. Have the owning database administrator remediate `supabase_admin` default ACLs, then re-query the resulting ACLs; enable leaked-password protection and test login/reset flows.
3. Verify storage upload/download/signed URL expiry and access isolation for each configured provider; verify authenticated Cloudflare Whisper end-to-end behavior.
4. Demonstrate AI provider failover with an approved, controlled test. The current usage tracker remains process-local, so usage totals reset on restart and are not an audit-grade billing ledger.
5. Confirm whether Qdrant and Telegram are required production dependencies; if yes, perform credential-safe live checks.
6. Reconcile Render API live settings with repository `render.yaml` before changing them; do not blindly overwrite a currently working deployment. The frontend is live and configured with `/api/health` as its health check.
7. Keep continuous background media-worker orchestration and the explicitly deferred post-launch items out of production guarantees until a worker and acceptance evidence exist.

**Updated decision:** Authentication/session flow is now evidenced working in production logs and the owner confirms Dashboard access. This does **not** clear the remaining security and integration gates above; general production sign-off remains conditional until they are verified or explicitly risk-accepted with an owner and date.
