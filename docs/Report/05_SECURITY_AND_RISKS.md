# Security and Risk Register
**Date:** 2026-10-12 UTC  
**Release status:** PENDING — NOT PRODUCTION READY

| Risk | Current evidence | Status / action |
|---|---|---|
| Worker credential exposure | Deployment workflow validates credentials without printing values; secret binding exists. | PASS for observed handling; keep secret values out of logs and reports. |
| Oversized request body | Worker code has declared-length rejection and bounded streaming enforcement at 50 MiB. | Deployed according to workflow evidence; full authenticated audio E2E still not run. |
| Public API exposure | Render service IP allow-list is `0.0.0.0/0`; no health-check path is configured in service metadata. | REVIEW REQUIRED: verify application-level auth/rate limiting and endpoint exposure before production. |
| SSO / frontend access | Netlify metadata requires team SSO for all projects. | PASS for observed policy; do not alter without owner approval. |
| Stale frontend | Netlify deploy is ready but references `777fba6ca92ce59e53e741b976bc9ea9692b45c1`, older than current main. | OWNER DECISION: whether to perform one controlled redeploy; preserve SSO. |
| No confirmed persistent media worker | Render service is a free web service running the API command; no dedicated continuous media worker is confirmed. | BLOCKER: assess queue/worker architecture; no paid resource without approval. |
| Production recovery | No managed production backup/restore drill evidenced. | NOT VERIFIED: establish backup policy, restore test, RPO/RTO. |
| Tenant isolation and auth | No new cross-tenant/authenticated E2E evidence captured in this cloud-only review. | NOT VERIFIED: run controlled security tests before release. |
| Privacy / external providers | OAuth/Drive, SMTP, Stripe, Sentry, storage lifecycle, provider fallback and terms not accepted here. | PENDING: verify configuration, data retention, consent, legal/commercial terms. |
| Quota / spend | No inference run and no paid resources created. | PASS for this review; require approval before quota-consuming tests or paid capacity. |

## Safe handling rules
- Never copy tokens, shared secrets, OAuth credentials, or full environment values into reports.
- Use synthetic media and GET-only checks first.
- Use redacted logs; do not include private user media or personal data in evidence.
- Keep changes on a branch until checks pass and deployment/build consequences are understood.
