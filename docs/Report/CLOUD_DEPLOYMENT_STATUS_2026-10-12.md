# Cloud Deployment Status — 2026-10-12 UTC

**Release status: PENDING — NOT PRODUCTION READY**  
**Evidence checkpoint:** main SHA `95aa9163cc40383a8c44c3a5f445e4de899116e4`

## Verified

### Cloudflare Whisper Worker

- **PASS — deployment workflow:** [Deploy Cloudflare Whisper Worker run #38260359375](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/38260359375) completed with `conclusion=success`.
- All substantive steps succeeded: credential validation without printing values, Node setup, Wrangler install, Worker source deploy, matching secret binding configuration, and handler verification without AI inference.
- **PASS — read-only deployment metadata:** Worker `narrativ-forge-whisper` has a 100%-traffic deployment version `304d7bbf-66a3-4d5a-b9ee-8615b7c1cc9c`, created at `2026-10-12T14:05:52Z`.
- **PASS — binding presence only:** `AI`, `ALLOWED_ORIGIN`, and `NARRATIV_SHARED_SECRET` bindings are present. Secret values were not retrieved or printed.
- The current deployed source includes the 50 MiB request-body limit hardening inherited from `6c53f953747d7ec3c18cf4872b85b96164c897b7`: reject oversized declared `Content-Length` and enforce a bounded streaming read for chunked requests.
- The deployment smoke is a handler/method-guard test. It is **not** an authenticated audio transcription test.

### Render API

- **PASS — deployment state:** Render service `Narrativ-Forge` is not suspended and its latest deployment `dep-db69upmk1f9s73f3ve0g` is live on `95aa9163cc40383a8c44c3a5f445e4de899116e4`.
- **PASS — startup log evidence:** the latest deploy logs show application startup complete, Uvicorn listening on port 10000, and `GET /` returning HTTP 200.
- **Configuration rechecked after owner change:** Render plan `free`, one instance; `autoDeploy=no` / trigger `off`. Render event history records `auto_deploy_disabled` at `2026-10-12T15:30:53Z`. The latest live deployment remains on main SHA `95aa9163cc40383a8c44c3a5f445e4de899116e4`. No new deploy was triggered.
- **NOT VERIFIED:** fresh GET-only probes to `/api/v1/health` and `/api/v1/ready`. Attempts from the available web/probe environment could not access the URLs, and Render request-log query returned no entries; endpoint status remains unknown. Startup logs showing `GET /` HTTP 200 do not establish health/readiness.

## Report directory audit

At this checkpoint, `docs/Report/` contains these two reports:
- [Burmese sample technical preflight](./BURMESE_SAMPLE_PREFLIGHT_2026-10-12.md) — technical media preflight passed; speech-quality acceptance remains pending.
- [Windows local Unicode runtime report](./LOCAL_WINDOWS_UNICODE_RUNTIME_REPORT.md) — historical local synthetic runtime evidence with explicit limitations; no new local tests were run during this cloud-only continuation.

This file is being added as the cloud deployment status report. No Windows/local work was performed as part of this update.

### Netlify frontend and access policy

- **PASS — deploy object state:** current published deploy `6ac4f8aba9c7aa00082031dc` is `ready`, but its source commit is `777fba6ca92ce59e53e741b976bc9ea9692b45c1` (2026-10-06), behind current main SHA `95aa9163cc40383a8c44c3a5f445e4de899116e4`.
- **PASS — SSO policy observed:** project access requires team SSO for all projects. No access-policy change was made.
- **OWNER ACTION REQUIRED:** decide whether to schedule a one-time frontend redeploy. Since the user has been minimizing build usage, do not trigger it automatically; preserve SSO and stop automatic builds again if that is the chosen operating procedure.

## Not verified / blocked

| Gate | Status | Why |
|---|---|---|
| Authenticated real-audio Whisper inference | NOT RUN | Would consume AI/provider quota; requires explicit owner approval |
| Burmese transcription quality / reference WER | NOT VERIFIED | No reviewed transcript/reference transcript in this cloud check |
| Persistent media worker | BLOCKED | Render has an API web service; no continuously running background worker is confirmed |
| Live retry / DLQ / failover drill | NOT RUN | Requires the intended live worker/queue environment |
| Managed production backup/restore | NOT VERIFIED | Ephemeral CI restore evidence is not a production recovery drill |
| Netlify frontend freshness | STALE DEPLOY VERIFIED | Current published deploy is ready but still points to old commit `777fba6ca92ce59e53e741b976bc9ea9692b45c1` from 2026-10-06, not current main SHA |
| Production integrations and acceptance | PENDING | OAuth/Drive, SMTP, Stripe, Sentry, storage lifecycle, load/performance, accessibility, legal/privacy, and external security review remain open |

## Safe next actions

1. Run GET-only probes for Render `/api/v1/health` and `/api/v1/ready` from a trusted runner that can resolve the service hostname; record status codes and redacted readiness fields only. This environment could not verify either endpoint.
2. Keep the current Cloudflare deployment in place; do not run authenticated inference until the owner explicitly approves possible quota use and confirms the protected shared-secret setup.
3. Decide separately whether a persistent media worker is worth the paid capacity. Do not create or scale paid resources without explicit approval.
4. Keep documentation changes on a branch and review via PR. Render auto-deploy is now disabled, so commits to `main` should not trigger automatic Render deployments; use Manual Deploy only when intentionally releasing.

## Cost, privacy, and release boundary

- No paid resources were created or changed.
- No secret values were read, copied, or printed.
- No production data was mutated.
- No AI inference or quota-consuming audio request was sent.
- No SSO or visitor-access policy was changed.
- **Release remains PENDING — NOT PRODUCTION READY.**
