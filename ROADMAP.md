# Narrativ Forge — Roadmap

> Owner: Project maintainers  
> Update when: requirements, phase status, gates, or release criteria change  
> Last Updated: 2026-10-08  
> Do NOT put here: provider secrets, detailed runbook commands, or unsupported live-health claims

## Authority

This is the **only master execution roadmap**. Supporting documents contain implementation-specific detail. Code existence is not production evidence.

## Completed Phases

| Phase | Scope | Status |
|---|---|---|
| 01 | Foundation & Security | DONE / VERIFY |
| 02 | Core Domain | DONE |
| 03 | Script Studio | DONE / VERIFY |
| 04 | Assets & Uploads | DONE / VERIFY |
| 05 | Processing Engine | FOUNDATION / VERIFY |
| 06 | Subtitle Studio | DONE / VERIFY |
| 07 | Review & Approval | DONE / VERIFY |
| 08 | Export & Publishing Preparation | DONE / VERIFY |
| 09 | Search & Analytics | DONE / VERIFY |
| 10 | Production Hardening | FOUNDATION / VERIFY |
| 11 | Business & Collaboration | FOUNDATION / VERIFY |
| 12 | Scale & Advanced | FOUNDATION / VERIFY |

## Active Phase

**Verification and evidence.**

Priority order:
1. Freeze requirements and documentation ownership.
2. Verify worker/media/storage/Whisper/Drive/SMTP/Stripe/Sentry/PostgreSQL/Redis/backup.
3. Run production/cross-tenant E2E, load, security, accessibility, and responsive audits.
4. Complete UI screen/state/component audit.
5. Finish remaining Auto Production surfaces.
6. Final release audit.

## Future Phases / Workstreams

### Auto Production 13–17
- 13: Cross-platform export preparation.
- 14: Trend integration adapter.
- 15: A/B testing + feedback loop.
- 16: Series trailer planning.
- 17: Burmese-first translation adapter.

### Batches 18–36
18 publishing-preparation adapters/metadata/idempotency; 19 trend connectors; 20 experiment registry; 21 AI quality evaluation/provider ranking; 22 EDL/FCPXML/NLE manifests; 23 storage lifecycle/DR; 24 SRE/incident/compliance foundations; 25 character/style bible; 26 hook recommendation/episode scoring; 27 Burmese subtitle evaluation; 28 selective regeneration; 29 quota-aware scheduling; 30 human-review learning; 31 collaboration seam; 32 realtime notifications/presence; 33 usage quotas; 34 enterprise tenant policy; 35 demo/onboarding/support seam; 36 launch gate/pen-test remediation.

## Backlog / Requirements Completeness

The following must remain visible and are not considered lost during consolidation:

- Story ingestion → AI episode split → human approval.
- Eight hook families: Question, Shock, Mystery, Warning, Personal Story, Contrarian, Cliffhanger, Number.
- First 10 seconds: Hook → Pattern Interrupt → Context → Content.
- SEO/title/caption/hashtag/keyword/posting-time logic.
- Retention, emotional arc, cliffhanger/recap, engagement triggers.
- Thumbnail workflow: 10 candidates → 5 usable → human selection.
- Sound/BGM workflow.
- Subtitle styling.
- LoRA/voice consistency.
- Series Bible and continuity checks.
- Cross-platform preparation: TikTok/YouTube Shorts/Facebook Reels/Instagram Reels; preparation only, no direct publishing.
- Five-episode batch planning/calendar.
- Analytics feedback loop and evidence-based A/B learning.
- Video-generation adapter/fallback and watermark/commercial-use checks.
- Provider quota accounting and live-limit verification.
- Subtitle correction history/metrics/evaluation export.
- Social analytics import.
- Archive/cold-storage and PII purge.
- Backup/restore and rollback.
- Monitoring/incident/on-call.
- Full testing/security/accessibility/legal/pen-test release gates.

## Manual Mode validation gate

Before treating Manual Mode as production-ready, collect human evidence including 15–20 manual videos, production logs, multiple hook types, subtitle styles, production-time measurements, commercial-use review, repeated-problem dataset, and MVP scope freeze.

## Release gate

Production Ready requires fresh evidence for:
- real worker + representative media;
- queue → worker → FFmpeg/Whisper → DB/storage;
- retry/DLQ/failover;
- real OAuth/Drive export/recovery;
- SMTP;
- Stripe;
- Sentry;
- backup/restore;
- live provider limits/terms;
- production auth/tenant E2E;
- full E2E;
- load/performance;
- security scan;
- accessibility/responsive;
- legal/compliance;
- external penetration testing.

## Deferred

- Direct social publishing.
- Full mobile client.
- Paid always-on worker unless needed.
- Production LoRA/video-generation pipeline until provider/legal/runtime evidence exists.

## Blocked

Anything requiring user/provider credentials, a real worker machine, real media, provider consoles, or external legal/security sign-off remains VERIFY/PENDING until evidence exists.

## Evidence rule

Never promote code-configured to VERIFIED from credentials alone. Never promote a live integration from unit tests alone.
