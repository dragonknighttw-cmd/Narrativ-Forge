# Narrativ Forge — Engineering & Documentation Workflow

> Owner: Project maintainers  
> Update when: repository workflow, evidence rules, or tool conventions change  
> Last Updated: 2026-10-08  
> Do NOT put here: product requirements or detailed domain implementation

## 1. Read order

1. `README.md`
2. `CURRENT_STATE.md`
3. `ROADMAP.md`
4. `UI_DESIGN_SYSTEM.md` for UI work
5. `SECURITY.md` for security-sensitive work
6. Relevant `docs/*.md`
7. Source code/tests
8. Runbooks for operational work

## 2. Git workflow

- Work directly on `main` when explicitly requested.
- Do not create branches unless the task explicitly requires them.
- Keep commits logically scoped.
- Never put secrets in source, documentation, fixtures, or logs.
- Preserve historical knowledge when consolidating documents.
- A rename/archive must preserve the complete source content.

## 3. Phase completion protocol

1. Read the authoritative source documents.
2. Inspect the relevant implementation.
3. Make the smallest complete change.
4. Run applicable automated checks.
5. Inspect the resulting diff/state.
6. Reconcile documentation ownership/status.
7. Record evidence separately from assumptions.
8. Stop promoting status when evidence is missing.

## 4. Documentation update protocol

Update documentation in the same logical change when a production-relevant fact changes.

| Trigger | Required update |
|---|---|
| Architecture change | PROJECT_OVERVIEW + ARCHITECTURE |
| Current status/evidence change | CURRENT_STATE |
| VERIFY resolution or blocker change | CURRENT_STATE + affected domain doc + ROADMAP when a release gate changes |
| Requirement/phase/gate change | ROADMAP |
| UI token/component/state change | UI_DESIGN_SYSTEM |
| Security control/incident change | SECURITY |
| Deployment/runtime change | DEPLOYMENT + OPERATIONS |
| DB/schema/migration change | DATABASE |
| API contract change | API |
| AI/provider/RAG change | AI_RAG |
| Storage/routing/retention change | STORAGE |
| Failure/recovery procedure change | TROUBLESHOOTING |

### Session start

Read README → CURRENT_STATE → ROADMAP, then the relevant domain doc.

### Session end

Confirm code status, tests/evidence, current-state status, roadmap impact, and links.

### Documentation drift rule

If a supporting document conflicts with canonical ownership, reconcile it rather than creating another competing source.

## 5. Tools matrix

| Need | Preferred source/tool |
|---|---|
| Repository code/history | Git/GitHub repository |
| Current docs | canonical Markdown |
| Tests | repository test suites / CI |
| UI behavior | frontend source + Playwright |
| DB schema | models + Alembic |
| API contract | routes/schemas/tests |
| Live provider evidence | provider/runtime environment |
| External docs | official provider documentation |

## 6. Definition of Done

A code change is not production-ready merely because it compiles.

DOD requires, as applicable:
- implementation;
- tests;
- typecheck/build;
- integration/E2E evidence;
- security review;
- documentation ownership;
- live verification for external/runtime claims.

## 7. Evidence rules

Use:
- DONE for repository implementation evidence.
- VERIFIED only for fresh environment/provider evidence.
- PENDING/BLOCKED/NEXT/DEFERRED/VERIFY where appropriate.

Never claim provider health from credentials alone. Never claim live integration from unit tests alone.

Separate:
- repository migration head vs live database head;
- code-configured provider vs live provider;
- deployment manifest vs actual deployment;
- test pass vs production behavior.

## 8. Safety

Preserve original assets and approved outputs. Do not silently alter approved content. Never expose secrets. Do not bypass provider watermark/commercial-use restrictions.

## Release gate trigger table

| Trigger | Required status/evidence update |
|---|---|
| Worker provisioned/deprovisioned | CURRENT_STATE + DEPLOYMENT + OPERATIONS + ROADMAP |
| Real media E2E passes/fails | CURRENT_STATE + TESTING + AI_RAG + STORAGE |
| Retry/DLQ/failover drill | CURRENT_STATE + TESTING + OPERATIONS + TROUBLESHOOTING |
| Storage lifecycle verified | CURRENT_STATE + STORAGE |
| OAuth/Drive verified | CURRENT_STATE + DEPLOYMENT/API |
| SMTP/Stripe/Sentry live-tested | CURRENT_STATE + affected operational doc |
| Live Alembic head verified | CURRENT_STATE + DATABASE |
| Backup/restore drill | CURRENT_STATE + DATABASE + OPERATIONS |
| Browser E2E/load/security/a11y evidence | CURRENT_STATE + TESTING |
| Legal/pen-test/provider terms signed off | CURRENT_STATE + ROADMAP + SECURITY as applicable |

**Evidence rule:** VERIFIED requires a fresh link, log, screenshot, query result, or dated provider/runtime artifact. Configuration alone remains DONE/PENDING/VERIFY.
