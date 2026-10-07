# Release Readiness Checklist

Status: OPERATIONAL CHECKLIST / NOT A PRODUCTION-READY CLAIM

## Phase 8 — Production Hardening

### Automated gates
- [ ] CI green on final release SHA
- [ ] Backend unit/integration green
- [ ] Frontend typecheck/build green
- [ ] Playwright E2E green
- [ ] CodeQL green
- [ ] Dependency/security audit green
- [ ] Container scan green

### Security
- [x] Trusted Host middleware
- [x] CORS allow-list
- [x] Secure HttpOnly SameSite session cookie controls
- [x] Baseline auth/upload/default rate limiting
- [x] Security response headers
- [ ] Production auth E2E
- [ ] Cross-tenant isolation E2E
- [ ] External credential rotation drill

### Reliability
- [x] Celery durable delivery settings
- [x] Retry/DLQ code paths
- [x] Idempotency primitives
- [x] Selective regeneration creates immutable script versions
- [ ] Real worker queue → processing → DB/storage smoke test **(USER)**
- [ ] Retry/DLQ live drill **(USER)**
- [ ] Worker failover live drill **(USER)**
- [ ] 15–30 minute video benchmark **(USER)**
- [ ] Backup/restore drill **(USER / provider access)**

### Observability
- [x] Structured HTTP logging
- [x] Metrics endpoint
- [x] Sentry integration code
- [ ] Real Sentry production event **(USER / DSN)**
- [ ] Alert/incident verification **(USER / provider config)**

## Phase 9 — Release Candidate

### External integrations
- [ ] Google OAuth callback + real Drive export **(USER / OAuth credentials)**
- [ ] Idempotent re-export + partial upload recovery **(USER + ASSISTANT)**
- [ ] SMTP real delivery **(USER / SMTP credentials)**
- [ ] Stripe API/webhook lifecycle **(USER / Stripe credentials)**
- [ ] Cloudflare Whisper quota → fallback **(USER quota/config + ASSISTANT code/tests)**
- [ ] Agnes quota enforcement with live provider limits **(USER account limits + ASSISTANT enforcement)**
- [ ] Groq daily quota/fallback with live provider limits **(USER account limits + ASSISTANT enforcement)**

### Product safety
- [x] Human approval remains required before final export
- [x] Approved output protection is part of storage lifecycle policy
- [x] Version history is retained for regeneration
- [ ] Full production workflow E2E **(USER + ASSISTANT)**
- [ ] Final export/re-export recovery drill **(USER + ASSISTANT)**

### Release decision
A release may be labelled **Release Candidate** only after all automated gates are green and every unchecked live gate has an explicit owner and verification plan.

A release may be labelled **Production Ready** only after the real worker runtime, external integrations, recovery drills, and performance gates are verified. Code existing alone is not sufficient.


## Ownership legend — 2026-10-07

**USER** = requires the user's real machine, provider account, credential, mailbox, OAuth consent, or provider-console action.  
**ASSISTANT** = code, tests, documentation, local/static analysis, and integration scaffolding that can be completed without those live credentials/machines.  
**USER + ASSISTANT** = assistant prepares the implementation/tests/runbook; user executes the final real-environment verification.

### Hard release blockers owned by USER

1. Local Home/Office Celery worker runtime with FFmpeg.
2. Real queue → processing → DB/storage → retry/DLQ → failover drill.
3. Production auth/cross-tenant E2E.
4. Google OAuth + Drive export/recovery.
5. SMTP real delivery.
6. Stripe API/webhook lifecycle.
7. Sentry production event/alert verification.
8. Provider backup/restore drill.
9. Live Agnes/Groq quota confirmation.
10. Real 15–30 minute/video benchmark.

### Work that can continue without USER

- Provider adapter/fallback hardening and tests.
- Quota reservation/guard unit and integration coverage.
- Selective regeneration/versioning/content-extension tests.
- Storage cleanup/monitoring safety and tests.
- Magic-link/auth tests and security hardening.
- Tenant isolation/idempotency/retry/DLQ/observability audits.
- 33-component UI/design-system audit and accessibility/responsive states.
- Auto Production code foundations and test coverage.
- Documentation synchronization and release-checklist maintenance.

**Release rule:** do not convert any unchecked live gate to `[x]` merely because its code path exists. Evidence must come from the actual runtime/account/environment.
