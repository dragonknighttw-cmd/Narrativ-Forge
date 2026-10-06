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
- [ ] Real worker queue → processing → DB/storage smoke test
- [ ] Retry/DLQ live drill
- [ ] Worker failover live drill
- [ ] 15–30 minute video benchmark
- [ ] Backup/restore drill

### Observability
- [x] Structured HTTP logging
- [x] Metrics endpoint
- [x] Sentry integration code
- [ ] Real Sentry production event
- [ ] Alert/incident verification

## Phase 9 — Release Candidate

### External integrations
- [ ] Google OAuth callback + real Drive export
- [ ] Idempotent re-export + partial upload recovery
- [ ] SMTP real delivery
- [ ] Stripe API/webhook lifecycle
- [ ] Cloudflare Whisper quota → fallback
- [ ] Agnes quota enforcement with live provider limits
- [ ] Groq daily quota/fallback with live provider limits

### Product safety
- [x] Human approval remains required before final export
- [x] Approved output protection is part of storage lifecycle policy
- [x] Version history is retained for regeneration
- [ ] Full production workflow E2E
- [ ] Final export/re-export recovery drill

### Release decision
A release may be labelled **Release Candidate** only after all automated gates are green and every unchecked live gate has an explicit owner and verification plan.

A release may be labelled **Production Ready** only after the real worker runtime, external integrations, recovery drills, and performance gates are verified. Code existing alone is not sufficient.
