# Narrativ Forge — Current vs Target

**Assessment basis:** current repository `README.md`, `web-platform/docs/architecture.md`, operational runbooks, and `roadmap.md` dated 2026-10-06.

## Status legend

- **DONE** — implementation and the relevant repository evidence support completion.
- **VERIFY** — code/foundation exists but real integration/runtime verification is still required.
- **TODO** — target capability is not yet sufficiently implemented.
- **RESERVE** — explicitly deferred/future.

## Product workflow

| Area | Roadmap target | Current state | Status |
|---|---|---|---|
| Ideas / Series / Seasons / Episodes | Full CRUD + workflow | Implemented | DONE |
| Scripts / versions / autosave | Versioning + conflict handling | Implemented | DONE |
| Scenes / assets | CRUD + upload/version safety | Implemented | DONE |
| Processing | Queue + worker + FFmpeg/Whisper | Queue/Celery foundation and real-job code exist; live runtime still needs verification | VERIFY |
| Subtitle Studio | Burmese edit + validation + SRT/VTT | Implemented foundation | DONE |
| Review / approval | Human gate before export | Implemented foundation | DONE |
| Google Drive | OAuth + approved-only export + idempotency | Foundation exists; real callback/export verification remains | VERIFY |
| Production log / social prep / analytics | Capture and import/entry | Foundation exists | DONE |
| Hook Library | Recommendation/library foundation | Backend foundation exists | DONE |
| Billing | Stripe foundation | Foundation exists; production lifecycle test remains | VERIFY |
| Tenant isolation | Organization scope | Foundation exists; full E2E isolation test remains | VERIFY |
| Notifications/webhooks | Event + delivery foundation | Foundation exists | VERIFY |
| Security | Baseline controls | Many controls implemented; final audit/pen-test remains | VERIFY |
| Backup/restore | Tested DR | Runbook exists; drill remains | VERIFY |

## Storage / infrastructure

| Target | Current | Status |
|---|---|---|
| B2 raw media | Routing implemented | VERIFY real credentials + file lifecycle |
| Supabase Storage | Private bucket + routing | VERIFY real lifecycle |
| Cloudinary | Preview/thumbnail path | VERIFY real upload |
| Redis/Celery | Queue foundation | VERIFY real worker/runtime |
| Cloudflare Whisper | Worker, signed usage keys, VTT path, guardrails | VERIFY real audio E2E + fallback |
| Netlify frontend | Current deployment | DONE |
| Render backend | Current free deployment | DONE |
| Dedicated worker | Code/deployment path exists but free-only deployment decision matters | VERIFY |
| Google Drive | OAuth/export foundation | VERIFY |

## UI / UX

The roadmap defines 26 screens and complete state coverage. The repository has substantial workflow UI, but the final responsive/accessibility/state-completeness audit is still open.

Therefore:
- Core workflow UI: **DONE**
- Full state audit: **TODO**
- Mobile/tablet audit: **TODO**
- WCAG audit: **TODO**
- Final polish: **TODO**

## Data/versioning gap

The roadmap explicitly adds `episode_versions`, `scene_regenerations`, `content_extensions`, and `characters`. These should not be assumed complete merely because base episode/script/asset versioning exists.

Status: **TODO / RESERVE by feature**, unless the repository data model independently proves each one.

## Business/legal gap

The remediation plan contains a much broader SaaS/business scope (billing trials, legal docs, support, local payments, etc.). The product roadmap here only requires the business foundation needed for Narrativ Forge's intended private workflow.

Current:
- Stripe foundation: VERIFY
- Terms / Privacy / DPA: TODO
- DMCA workflow: TODO if public publishing is later introduced
- Local payments: RESERVE unless business direction changes
- Full monetization pilot: TODO

## Key conclusion

The project is **not starting from zero**. The core application workflow is largely implemented. The immediate work is to convert implementation into verified production capability, then close explicit roadmap gaps without importing unnecessary enterprise scope from the remediation plan.
