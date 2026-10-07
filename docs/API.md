# API

> Owner: Backend maintainers  
> Update when: routes, request/response schemas, auth contracts, or integration adapters change  
> Last Updated: 2026-10-08  
> Do NOT put here: provider credentials

## Boundary

FastAPI owns authentication, authorization, validation, domain mutations, workflow transitions, storage access, AI gates, and external integration orchestration.

## Core endpoint areas

- Auth/session.
- Ideas, series, seasons, episodes.
- Scripts and versions.
- Scenes.
- Assets/uploads.
- Processing jobs and retry.
- Subtitles.
- Review/approval.
- Google Drive export.
- Hooks.
- Publishing preparation.
- Analytics.
- Billing/webhooks.
- Cloudflare Whisper signed-token/import flow.
- Auto Production foundations.

## Contract rules

- Organization/tenant scope is enforced server-side.
- Approved export requires human approval.
- Original assets are not overwritten.
- Retry must preserve processing-job identity and avoid duplicate dispatch.
- External provider calls must classify retryable/non-retryable failures.
- Idempotent operations should reuse known remote identities/manifests.

## Auto Production API scope

Target contracts include story ingestion, episode split proposals, hook candidates, SEO metadata, retention/pacing analysis, thumbnail candidates, sound/BGM planning, Series Bible/continuity, platform preparation, batch/calendar planning, A/B variants, provider adapters, and analytics feedback.

These are foundation contracts unless CURRENT_STATE contains fresh verification evidence.
