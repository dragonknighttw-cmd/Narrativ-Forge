# Narrativ Forge — Master Roadmap

> **Single Source of Truth for planned work**
>
> **Last updated:** 2026-10-07
>
> This document is the authoritative execution roadmap. Product requirements, future capabilities, hardening work, business/compliance work, scale work, and live-release gates are consolidated here so implementation never depends on several competing roadmaps.
>
> **Status rule:** code existing is not the same as production-ready. A production claim requires fresh evidence at the applicable live/integration gate.

---

## 0. Product Definition

Narrativ Forge is a private, invite-only Burmese short-form video production workspace.

### Core workflow

`Idea → Structure → Script → Assets → Processing → Subtitle → Review → Approval → Output → Publishing Preparation → Analytics`

### Operating principles

1. Manual Mode validates the production loop and creates useful production data.
2. Auto Mode accelerates the same workflow; it does not bypass human quality control.
3. Human approval is mandatory before final export.
4. The application database is the workflow/version/approval/audit source of truth.
5. Google Drive is an approved-output destination, not the workflow database.
6. Direct TikTok/YouTube/Facebook/Instagram publishing is out of scope for the current product boundary; the system prepares platform-ready metadata/variants and records manual publication results.
7. No real secrets belong in source control or documentation.
8. Heavy FFmpeg/Whisper work belongs in worker infrastructure, not request handlers.
9. Free-first infrastructure is preferred, but production reliability takes precedence over an artificial free-only constraint.
10. Every generated artifact must remain reviewable, versioned, and selectively replaceable.

### Current target output

- Burmese short-form video
- Target duration: 3 minutes
- 9:16
- Target resolution: 1080×1920
- Burmese subtitles
- Output package: video, subtitles, transcript, script, metadata, thumbnail

### Explicit exclusions

- Logixa Flow integration
- Aether Bridge integration
- Public registration
- Public profiles
- Public browsing/comments
- Direct social-platform publishing
- External downstream delivery
- Google Drive as workflow DB
- Any feature that bypasses mandatory human approval

---

# 1. Execution Model

## 1.1 Formal phases

The roadmap has **12 formal phases**. They are the execution backbone:

1. Foundation & Security
2. Core Domain
3. Script Studio
4. Assets & Uploads
5. Processing Engine
6. Subtitle Studio
7. Review & Approval
8. Export & Publishing Preparation
9. Search & Analytics
10. Production Hardening
11. Business & Collaboration
12. Scale & Advanced

The expanded Auto Production workstreams below are **not additional formal phases**. They are scheduled capability tracks that attach to the 12-phase roadmap.

## 1.2 Expanded Auto Production

Workstreams 13–17:

13. Cross-platform export variants
14. Trend integration adapter
15. A/B testing and feedback scoring
16. Series trailer planning
17. Burmese-first translation adapter

## 1.3 Scale / intelligence batches

Batches 18–36 are additional planned capabilities:

18. Multi-platform publishing preparation adapters
19. Live trend providers
20. Experimentation engine
21. AI quality/evaluation
22. NLE / advanced export
23. Storage lifecycle and disaster recovery
24. SRE / compliance
25. Character and style bible automation
26. Hook recommendation and episode scoring
27. Burmese subtitle quality model and Zawgyi/Unicode corpus
28. Selective regeneration with dependency-aware invalidation
29. Batch scheduler with quota-aware parallelism
30. Human-in-the-loop quality learning
31. Yjs collaborative script editing
32. Realtime job/review notifications and presence
33. Usage quotas and plan enforcement
34. Enterprise tenant controls and resource policies
35. Onboarding/demo tenant and support workflow
36. Final production launch gate and external pen-test remediation

These are ordered workstreams, not promises that all are required for MVP launch.

---

# 2. Status Vocabulary

Use these statuses consistently:

- **CODE-DONE** — implementation exists and has appropriate automated evidence.
- **FOUNDATION** — reusable seam/contract/foundation exists, but full product integration remains.
- **VERIFY** — implementation exists but fresh integration/live evidence is required.
- **USER/LIVE** — requires real credentials, external account action, real infrastructure, or human evidence.
- **TODO** — implementation has not been completed.
- **RESERVE** — intentionally deferred or optional future capability.

Never change a VERIFY/USER-LIVE item to Done merely because code exists.

---

# 3. Phase 01 — Foundation & Security

## Scope

Establish the application skeleton, configuration, authentication foundation, security boundaries, migrations, tenant model, and development/production configuration rules.

## Target checklist

- Next.js frontend foundation
- FastAPI backend foundation
- PostgreSQL + Alembic
- Secure session/auth foundation
- Invite-only access model
- Organization/membership model
- Role model
- Production configuration validation
- CORS and trusted-host validation
- Security headers
- OAuth token encryption foundation
- Webhook HTTPS/SSRF protections
- Filename/path safety
- Upload MIME/size validation
- Rate-limit foundation
- Audit-event foundation
- Secret hygiene
- CodeQL / dependency/container security workflow foundations
- CI test markers and unit-test organization

## Current status

**CODE-DONE / VERIFY**

Live verification still required for production authentication, tenant isolation, credentials, security scans, and deployment evidence.

---

# 4. Phase 02 — Core Domain

## Scope

Build the durable content model and workflow state.

## Domain

- Ideas
- Series
- Seasons
- Episodes
- Scripts
- Script versions
- Scenes
- Assets
- Asset versions
- Processing jobs
- Approvals
- Drive exports
- Publishing preparation state
- Manual production logs
- Hook library
- Subtitle presets
- App analytics
- Social analytics
- Activity/audit logs
- Characters
- Episode versions
- Scene regeneration records
- Content extensions

## Required invariants

- Episode belongs to Series and Season.
- Episode numbering is unique within its intended scope.
- `public_id` remains separate from internal DB identity.
- Asset identity is separate from export identity.
- Assets link to episodes and optionally scenes.
- Historical content versions are immutable.
- Script/Episode edits use optimistic locking.
- Critical transitions use compare-and-set semantics.
- Database state is the durable workflow source of truth.

## Workflow state

`idea → planned → script_draft → script_review → assets_needed → in_production → processing → subtitle_review → needs_approval → approved → exporting → exported → archived`

Failure/revision paths:

- `script_review → script_draft`
- `subtitle_review → in_production`
- `needs_approval → in_production`
- `exporting → failed`
- `failed → processing`

## Current status

**CODE-DONE / VERIFY**

---

# 5. Phase 03 — Script Studio

## Scope

Create a reliable Burmese-first script workflow.

## Target checklist

- Script editor
- Autosave
- Conflict detection
- Optimistic locking
- Immutable script history
- Version comparison
- Script review state
- Scene breakdown
- AI-assisted structure/script generation behind provider adapters
- Provider fallback
- Deterministic mock adapter for development/testing
- Burmese/Zawgyi normalization
- Script quality gates
- Character/style context
- Selective script revision

## AI routing

Configured OpenAI-compatible providers may be routed by priority. Current implementation supports Groq/OpenAI-compatible providers with deterministic mock fallback.

No provider is considered production-ready until real credentials, rate limits, latency, quality, terms, and failure behavior are verified.

## Current status

**CODE-DONE / VERIFY**

---

# 6. Phase 04 — Assets & Uploads

## Scope

Provide safe, resumable, versioned media handling.

## Storage strategy

- Cloudinary: images/previews
- Supabase Storage: small workflow files such as SRT/manifest
- Backblaze B2: raw video/audio/large media
- Google Drive: approved final outputs
- Local disk: temporary processing only

Storage routing must remain explicit and reference-safe.

## Target checklist

- Direct uploads
- Resumable upload sessions
- Chunk offsets
- Chunk checksums
- Provider ETags
- Ownership checks
- Expiry/abort behavior
- Idempotent upload creation
- MIME/size validation
- Filename sanitization
- Asset versioning
- Retention metadata
- Immutable source objects
- Safe download
- Soft-delete/reference checks
- Provider-specific encryption where supported

## Current status

**CODE-DONE / VERIFY**

Real B2, Supabase, Cloudinary, and full routing tests remain live gates.

---

# 7. Phase 05 — Processing Engine

## Scope

Build the reliable asynchronous production engine.

## Architecture

`API → PostgreSQL → Redis → Celery Worker → FFmpeg/Whisper/adapters → Storage → DB`

## Target checklist

- ProcessingJob lifecycle
- Real Celery worker container
- Beat/scheduled recovery
- Guarded dispatch
- Duplicate-dispatch prevention
- Retry scheduling
- Failed-job preservation
- Dead-letter handling
- Worker concurrency bounds
- FFmpeg media processing
- ffprobe validation
- Whisper transcription
- Cloudflare Whisper path
- Celery fallback path
- Progress tracking
- Timeouts
- Abandoned-job recovery
- Queue depth visibility
- Representative real-media smoke test

## Free-first worker strategy

- Render: API/web service
- Upstash Redis: shared broker
- Home Windows PC: primary heavy worker + single Beat
- Office Windows PC: reserve light worker, no Beat
- Kaggle: optional ephemeral free-first worker path
- Future paid worker: same repository worker contract

No second application codebase is permitted for local workers.

## Current status

**FOUNDATION / VERIFY / USER-LIVE**

The worker code/runtime path exists, but real worker execution and representative media processing remain hard production gates.

---

# 8. Phase 06 — Subtitle Studio

## Scope

Burmese subtitle editing, normalization, validation, and output.

## Target checklist

- Transcript import
- VTT/SRT handling
- Burmese Unicode/Zawgyi normalization
- Subtitle pagination
- Subtitle editor
- Timing validation
- Overlap detection
- Duration checks
- Presets
- Approved subtitle immutability
- Revision/version creation
- Cloud Whisper VTT import
- Manual correction
- Quality warnings
- Burmese subtitle evaluation foundation

## Current status

**CODE-DONE / VERIFY**

Real audio → Whisper → VTT → Subtitle Studio remains a live verification gate.

---

# 9. Phase 07 — Review & Approval

## Scope

Make human quality control explicit and enforceable.

## Target checklist

- Review Center
- Approval Detail
- Video preview
- Script review
- Subtitle review
- Asset completeness checks
- Critical issue blocking
- Approve/reject actions
- Revision loop
- Approval audit events
- Permission enforcement
- Tenant scoping
- Export preconditions

## Hard rule

Final export cannot proceed unless:

1. Episode is approved.
2. Final video asset exists and is valid.
3. Current approved subtitle exists.
4. Required metadata/manifest is valid.
5. User has permission.

## Current status

**CODE-DONE / VERIFY**

---

# 10. Phase 08 — Export & Publishing Preparation

## Scope

Produce approved output packages and platform-ready preparation without direct publishing.

## Target checklist

- Google OAuth
- Narrow `drive.file` scope
- Drive export
- Export manifest
- Video + SRT + transcript + script + metadata + thumbnail package
- Idempotent export/re-export
- Export history
- Partial-progress recovery
- Provider identity reuse
- Export failure state
- Publishing preparation
- Platform metadata validation
- Captions/hashtags
- Format checks
- Manual publication record
- Publication evidence state

## Publishing state

`not_ready → prepared → scheduled_metadata_ready → manually_published → published_recorded`

Never claim publication without evidence.

## Current status

**CODE-DONE / VERIFY / USER-LIVE**

Real Google OAuth/Drive export and recovery remain live gates.

---

# 11. Phase 09 — Search & Analytics

## Scope

Make production history searchable and useful for learning.

## Target checklist

- Global search
- Relevance ranking
- Hook Library
- Manual production log
- App analytics
- Social analytics
- Production time tracking
- Hook/type tracking
- Completion/retention signals
- Shares/engagement signals
- Episode scoring
- Feedback aggregation
- Analytics privacy boundaries

## Current status

**CODE-DONE / VERIFY**

---

# 12. Phase 10 — Production Hardening

## Scope

Close the gap between working code and release-grade operation.

## Security

- Final dependency scan
- CodeQL
- pip-audit
- npm audit
- Trivy/container scan
- Security review
- Penetration testing
- Cross-tenant E2E

## Reliability

- Flaky-network upload tests
- Retry/DLQ verification
- Duplicate dispatch verification
- Worker crash recovery
- Backup/restore drill
- RPO/RTO evidence
- Load/performance test
- Rollback test

## Observability

- Structured logs
- Sentry production event
- Alert thresholds
- Queue/job metrics
- Processing duration metrics
- Export failure metrics
- Incident/runbook verification
- No secrets/PII in logs or metric labels

## UX/accessibility

Every applicable screen must support:

- Empty
- Loading
- Uploading
- Processing
- Completed
- Failed
- Retrying
- Rejected
- Offline/read-only
- Permission denied
- Session expired
- Drive disconnected
- Drive export failed
- Storage warning
- Unsupported file
- Critical quality issue

Also complete:

- Desktop/tablet/mobile responsive audit
- Keyboard audit
- Screen-reader audit
- WCAG 2.2 accessibility audit
- UI polish

## Current status

**FOUNDATION / VERIFY / USER-LIVE**

---

# 13. Phase 11 — Business & Collaboration

## Scope

Prepare the product for multiple users and commercial operation.

## Target checklist

- Organizations
- Memberships
- Owner/editor/viewer roles
- Invitations
- Magic links
- Transactional email
- Usage metering
- Quota enforcement
- Stripe checkout/portal/webhooks
- Subscription lifecycle
- Realtime notifications
- Presence
- Yjs collaboration seam
- Demo tenant/sample seed
- Support/ticket workflow
- Enterprise resource policies

## Legal requirements

- Terms of Service
- Privacy Policy
- DPA/data handling documentation where required
- DMCA/copyright process if public publishing is introduced
- Commercial-use/license review for external generation providers

## Current status

**FOUNDATION / VERIFY / USER-LIVE**

---

# 14. Phase 12 — Scale & Advanced

## Scope

Advanced production intelligence, scale, storage lifecycle, and release governance.

## Target checklist

- Character/style bible
- Hook recommendation
- Episode scoring
- Burmese subtitle quality model
- Selective regeneration
- Batch scheduling
- Quota-aware parallelism
- Human feedback learning
- NLE export formats
- Storage lifecycle automation
- Archive/cold storage
- Disaster recovery
- Cost controls
- SRE controls
- Enterprise controls
- Final launch gate

## Current status

**FOUNDATION / TODO / VERIFY**

---

# 15. Expanded Auto Production — Workstreams 13–17

These workstreams extend the core workflow without becoming separate roadmap phases.

## 15.1 Workstream 13 — Cross-platform export variants

Prepare bounded variants for TikTok, YouTube Shorts, Facebook Reels, and the master output.

Requirements:

- Platform-safe dimensions
- Duration checks
- Metadata constraints
- Caption/hashtag preparation
- Deterministic variant manifests
- No direct publishing

Status: **FOUNDATION / VERIFY**

## 15.2 Workstream 14 — Trend integration adapter

Build provider-neutral trend signals with:

- Provider adapter contract
- Cache/TTL
- Expiry handling
- Attribution
- Rate-limit/backoff behavior
- Graceful degradation
- Ranking inputs

Status: **FOUNDATION / VERIFY**

## 15.3 Workstream 15 — A/B testing and feedback scoring

Build:

- Variant registry
- Allocation rules
- Outcome recording
- Views
- Completions
- Shares
- Guardrails
- Deterministic winner/ranking logic
- Confidence-aware future experimentation seam

Status: **FOUNDATION / VERIFY**

## 15.4 Workstream 16 — Series trailer planning

Build duration-budgeted trailer planning with:

- Segment selection
- Hook preference
- Duration budget
- Story coverage
- Deterministic plan output

Status: **FOUNDATION / VERIFY**

## 15.5 Workstream 17 — Burmese-first translation adapter

Build:

- Translation request contract
- Burmese-first validation
- Line-break preservation
- Subtitle-safe output
- Provider-neutral adapter boundary

Status: **FOUNDATION / VERIFY**

---

# 16. Production Intelligence & Scale — Batches 18–24

## 18. Multi-platform publishing preparation adapters

- Provider-neutral preparation contracts
- Idempotent preparation attempts
- Platform-specific metadata validation
- Publication evidence model
- No direct publishing

Status: **FOUNDATION**

## 19. Live trend providers

- Pluggable connectors
- Cache/TTL
- Attribution
- Rate limits
- Backoff
- Provider failure isolation
- Graceful degradation

Status: **FOUNDATION**

## 20. Experimentation engine

- Variant registry
- Experiment lifecycle
- Allocation
- Outcomes
- Winner selection
- Confidence/guardrails
- Safe stopping rules

Status: **FOUNDATION**

## 21. AI quality and evaluation

- Burmese script evaluation sets
- Burmese subtitle evaluation sets
- Provider quality scores
- Regression tests
- Cost tracking
- Latency tracking
- Capability routing
- Provider comparison

Status: **FOUNDATION**

## 22. NLE / advanced export

- EDL
- FCPXML
- Premiere XML
- Timeline validation
- Asset mapping
- Export manifests
- Round-trip validation

Status: **FOUNDATION**

## 23. Storage lifecycle and disaster recovery

- Reference-safe retention
- Storage thresholds at 80/90/95%
- Cleanup planning
- Archive/cold storage
- Restore drills
- RPO/RTO
- Cost controls
- Lifecycle automation

Status: **FOUNDATION / VERIFY / USER-LIVE**

## 24. SRE / compliance

- Alert rules
- Incident automation
- Access reviews
- Audit evidence
- Deletion verification
- Privacy controls
- DMCA/copyright process
- Security evidence
- Release evidence

Status: **FOUNDATION / VERIFY / USER-LIVE**

---

# 17. Product Intelligence — Batches 25–30

## 25. Character/style bible automation

- Character profiles
- Style profiles
- Continuity context
- Prompt templates
- Character consistency checks

Status: **FOUNDATION**

## 26. Hook recommendation and episode scoring

- Hook families
- Episode quality score
- Retention-oriented inputs
- Historical performance signals
- Recommendation contract

Status: **FOUNDATION**

## 27. Burmese subtitle quality model

- Burmese evaluation corpus
- Zawgyi/Unicode cases
- Normalization cases
- Timing/readability checks
- Quality scoring
- Regression corpus

Status: **FOUNDATION**

## 28. Selective regeneration

- Dependency graph
- Change impact analysis
- Regeneration plan
- Asset preservation
- Version retention
- Scene-level regeneration
- Downstream invalidation only where necessary

Status: **FOUNDATION / VERIFY**

## 29. Batch scheduler

- Batch jobs
- Quota-aware planning
- Concurrency limits
- Priority
- Retry semantics
- Provider capacity awareness

Status: **FOUNDATION**

## 30. Human-in-the-loop quality learning

- Review learning events
- Approval/rejection signals
- Quality model updates
- Safe feedback aggregation
- No automatic publication from learned scores

Status: **FOUNDATION**

---

# 18. Collaboration & Commercial Scale — Batches 31–36

## 31. Yjs collaborative script editing

- Shared document model
- Conflict-free editing
- Presence
- Permission enforcement
- Version snapshots
- Recovery

Status: **FOUNDATION**

## 32. Realtime notifications and presence

- Job notifications
- Review notifications
- Export notifications
- Presence leases
- Reconnect behavior
- Permission-aware delivery

Status: **FOUNDATION / VERIFY**

## 33. Usage quotas and plan enforcement

- Usage metering
- Quotas
- Token/provider cost tracking
- Storage quotas
- Processing quotas
- Rate limits
- Graceful quota errors

Status: **CODE-DONE / VERIFY**

## 34. Enterprise tenant controls

- Resource policies
- Tenant-level limits
- Role policies
- Retention policies
- Audit requirements
- Isolation verification

Status: **FOUNDATION**

## 35. Onboarding, demo tenant and support

- Demo/sample seed
- First-run onboarding
- Empty-state guidance
- Support/ticket workflow
- Troubleshooting links
- Operational support boundaries

Status: **FOUNDATION**

## 36. Final production launch gate

Release only after all applicable evidence exists.

Required evidence includes:

- Production auth
- Tenant isolation
- Real worker
- Real representative media
- Queue → Worker → FFmpeg/Whisper → DB/storage
- Retry/DLQ/failover
- Real storage providers
- Google OAuth/Drive export/re-export/recovery
- SMTP invite/magic link
- Stripe lifecycle/webhooks
- Sentry event/alert
- Backup/restore
- Full E2E
- Load/performance
- Security scans
- Accessibility/responsive audit
- Legal/compliance documents
- External penetration test where required
- Final documentation audit

Status: **USER/LIVE**

---

# 19. Manual Mode Validation Gate

Manual Mode is not a side project. It is the evidence loop used to validate what automation should optimize.

## Required validation

Produce **15–20 videos** and record:

- Hook type
- Title variant
- Thumbnail choice
- Subtitle style
- Production time
- Revision effort
- Retention/engagement signals where available
- Commercial-use/licensing observations

Test at least:

- 3 distinct hook families
- 2 subtitle styles

The expanded Auto plan has an 8-family hook library target; manual validation should cover those families where practical before changing automation defaults.

## Exit gate

- Manual production log exists.
- Initial Hook Library exists.
- Production time is measured.
- Commercial-use risk is reviewed.
- Repeated problems are captured as automation requirements.
- MVP scope is frozen before unnecessary expansion.

Status: **USER/LIVE**

---

# 20. UI / Design System Track

The target baseline is **26 screens** and **33 reusable component categories**, but counts are coverage targets, not proof of completion.

## Core screens

- Login
- Logout
- Dashboard
- Ideas
- Series
- Series Detail
- Episodes
- Episode Detail
- Script Studio
- Scene Breakdown
- Asset Library
- Video Project
- Subtitle Studio
- Thumbnail Studio
- Processing Queue
- Review Center
- Approval Detail
- Drive Export
- Publishing Preparation
- Hook Library
- Manual Production Log
- App Analytics
- Social Analytics
- Settings
- Usage & Limits
- Activity Log

Expanded Auto requirements may be represented as tabs/panels rather than automatically creating new screens.

## Design requirements

- Production-first UI
- Keyboard-friendly
- Responsive desktop/tablet/mobile
- Accessible/WCAG-oriented
- State-complete
- Burmese typography support
- Shared semantic design tokens
- Reusable accessible primitives
- Focus-visible behavior
- Reduced-motion support
- Minimum interactive target sizing

Status: **FOUNDATION / VERIFY**

---

# 21. Runtime, Storage & Infrastructure Track

## Current target

- Netlify: frontend
- Render: API/web service
- Managed PostgreSQL: production DB
- Upstash Redis: shared broker/cache where selected
- Cloudinary: image/preview layer
- Supabase Storage: small workflow files
- Backblaze B2: raw/large media
- Google Drive: approved exports
- Cloudflare Workers AI: primary free-first Whisper path
- Celery + FFmpeg: long-running worker
- Sentry: error monitoring

## Local worker profile

### Home PC

- Primary heavy worker
- `heavy_queue`
- Single Beat
- FFmpeg
- Cloudflare Whisper by default
- Local Whisper optional

### Office PC

- Reserve light worker
- `light_queue`
- No Beat
- No heavy Whisper/video workload by default

Both use the same repository worker contract and shared Redis broker.

## Storage lifecycle

- Temporary local files expire quickly.
- Raw/intermediate media is retained according to reference-safe policy.
- Approved final outputs are protected from cleanup.
- Cleanup must never remove objects still referenced by durable workflow records.
- Storage pressure thresholds: 80% warning, 90% urgent, 95% safety/fallback guard.
- Archive/cold storage and deletion require retention-policy checks.

Status: **FOUNDATION / VERIFY / USER-LIVE**

---

# 22. Cross-Cutting Engineering Contracts

These are implementation foundations that support multiple phases.

## State contract

Shared workflow states are defined in backend/frontend code and must remain synchronized.

## Version contract

Historical content versions are immutable and checksummed where applicable.

## Regeneration contract

Changes invalidate only dependent downstream artifacts.

## Quota contract

Provider and processing usage is bounded by explicit quota decisions.

## Storage contract

Cleanup is reference-safe and threshold-aware.

## Alert contract

Operational alerts use bounded, non-sensitive metadata.

## Audit contract

Audit metadata is redacted and organization-scoped.

## Presence contract

Presence uses expiring leases rather than durable stale records.

## Notification contract

Notification identity is deterministic/idempotent.

## Legal contract

Release blockers are explicit and cannot be bypassed by a code-only status.

## Release evidence contract

A production release is a set of verifiable evidence, not a checklist of code files.

---

# 23. Testing Strategy

## Unit

- Backend domain/services
- AI adapters
- Orchestration
- State/version/quota/storage contracts
- Production intelligence contracts

## Integration

- PostgreSQL
- Redis
- Storage adapters
- Worker dispatch
- Processing lifecycle
- OAuth/Drive adapters where testable

## E2E

Canonical production workflow:

`Login → Series → Episode → Upload → Processing → Transcript → Burmese subtitle edit → Review → Approval → Drive export → Production log`

## Failure-path E2E

- Session expired
- Permission denied
- Tenant mismatch
- Upload interruption
- Upload resume
- Duplicate request
- Duplicate dispatch
- Worker retry
- DLQ
- Storage provider failure
- Whisper quota exhaustion
- Drive disconnect
- Drive export failure
- Browser offline/read-only

## Release verification

Run fresh evidence against the exact release SHA. Never infer current CI health from an older run.

---

# 24. Production Release Gate

A release may be called production-ready only when every applicable requirement is:

- **CODE-DONE + automated evidence**, or
- **VERIFY + fresh live evidence**, or
- **RESERVE by explicit product decision**.

## Hard blockers

The following cannot be waived by documentation:

1. Real worker + representative media
2. Queue → Worker → FFmpeg/Whisper → DB/storage
3. Retry/DLQ/failover evidence
4. Real B2/Supabase/Cloudinary storage verification
5. Real Google OAuth/Drive export/re-export/recovery
6. Real SMTP invitation/magic-link delivery
7. Stripe lifecycle/webhook verification
8. Sentry production event/alert verification
9. Backup/restore drill
10. Production auth/tenant E2E
11. Full integration/E2E suite
12. Load/performance benchmark
13. Security scan on release SHA
14. Accessibility/responsive audit
15. Legal/compliance documents
16. External penetration test where required
17. Manual Mode evidence where the product decision requires it

---

# 25. Consolidated Verification Window

Implementation should be completed in batches first. Live verification should then be consolidated as much as practical.

Recommended final sequence:

1. Build/test code-only gaps.
2. Complete UI/state coverage.
3. Complete versioning/regeneration wiring.
4. Complete storage cleanup/monitoring wiring.
5. Complete auth/error-path coverage.
6. Complete Auto Production integration seams.
7. Reconcile README and roadmap.
8. Provision/confirm required external credentials.
9. Run real storage tests.
10. Run real worker/media processing.
11. Run Whisper + subtitle E2E.
12. Run review/approval.
13. Run Google Drive export/re-export/recovery.
14. Run SMTP invitation/magic link.
15. Run Stripe lifecycle/webhooks.
16. Run Sentry event/alert.
17. Run backup/restore.
18. Run full browser E2E.
19. Run load/performance.
20. Run security scans and accessibility/responsive audit.
21. Complete legal/compliance review.
22. Perform final repository/documentation audit.
23. Only then declare production readiness.

---

# 26. Documentation Governance

This roadmap is the **only master execution roadmap**.

### Root README

`README.md` = current implementation, infrastructure, deployment state, verified blockers, and links to authoritative supporting documents.

### This roadmap

`roadmap.md` = desired target, complete future work, execution order, status, gates, and release criteria.

### Completion matrix

`docs/21-master-completion-matrix.md` = detailed evidence/status matrix. It is a supporting audit artifact, not a competing roadmap.

### Supporting documents

Keep detailed documents only when they contain information that cannot be usefully maintained in the roadmap:

- Product definition
- Architecture
- UI/design system
- Manual Mode
- Auto Production specification
- Runtime/storage lifecycle
- Release readiness
- Production runbook
- Managed services
- Security policy

### Cleanup rule

Do not delete or merge a document until:

1. Its unique requirements have been mapped into the master roadmap or an authoritative supporting document.
2. Internal links are updated.
3. No requirement/status/evidence is lost.
4. Duplicate or obsolete wording is removed.
5. The repository contains one obvious source of truth for each category.

---

# 27. Execution Order From Here

Unless a new blocker or user decision changes priority, execute in this order:

1. Finish remaining code-only TODOs and foundation wiring.
2. Complete screen/state/component coverage and accessibility foundations.
3. Complete versioning, content-extension, and selective-regeneration integration.
4. Complete storage cleanup, retention, and monitoring implementation.
5. Complete authentication, invitation, and error-path coverage.
6. Complete expanded Auto Production schema/API/worker/UI wiring.
7. Complete remaining Phase 10–12 foundations.
8. Reconcile documentation and remove duplicated roadmap content.
9. Start the consolidated live verification window.
10. Fix evidence failures.
11. Repeat failed gates.
12. Final release audit.
13. Production-ready decision.

**Do not jump to later intelligence/commercial features while a hard production blocker remains unless explicitly chosen as a parallel track.**

---

# 28. Mandatory Roadmap Checkpoints

After every major milestone, and at minimum after Phases **03, 06, 09, and 12**:

1. STOP implementation.
2. Update this `roadmap.md`.
3. Update `README.md`.
4. Move verified work into the completed/status sections.
5. Remove obsolete roadmap statements.
6. Reconcile `docs/21-master-completion-matrix.md`.
7. Review the next three execution units.
8. Confirm no requirement was lost.

This checkpoint is mandatory so the project never returns to fragmented planning.


---

# Requirement Completeness Register — 2026-10-07

This register is part of the master roadmap. It exists to prevent requirements from being lost when legacy/supporting documents are consolidated. It does not create a second roadmap.

## A. Source-of-truth reconciliation

The roadmap has been checked against:
- Final Master Plan v4.0 / implementation packet
- Comprehensive Remediation Plan
- Burmese remaining-work master checklist
- Auto Production expansion specification
- Current-vs-target and completion matrix
- UI/design specifications
- runtime/storage/release-readiness documents
- legacy `narratic/docs/*` product documents
- current frontend package, design tokens, primitives, and app structure

No requirement is considered complete merely because code exists. Status remains **CODE-DONE**, **FOUNDATION**, **VERIFY**, **USER/LIVE**, **TODO**, or **RESERVE** according to evidence.

## B. Product and content intelligence requirements that must remain visible

### Story ingestion and episode planning
- Full story/story-idea ingestion.
- AI-assisted episode split proposal: episode count, duration, scenes, characters, emotional arc, cliffhangers, and publish schedule.
- Human approval/modification before generation.
- Story ingestion job and episode split plan records.
- Expanded flow: Story Upload → AI Analysis → Episode Split Review → User Approve/Modify → Script.

### Hook engineering
- Eight hook families: Question, Shock, Mystery, Warning, Personal Story, Contrarian, Cliffhanger, Number.
- Hook library fields include hook text/type/topic/emotion/usage/performance/default state.
- Candidate workflow: generate three candidates → human selection → measure performance → promote only after evidence.
- First-10-second structure: 0:00–0:03 Hook → 0:03–0:05 Pattern Interrupt → 0:05–0:10 Context → 0:10+ Content.
- Default changes require multi-content evidence; never promote from a single video.

### Discovery / SEO
- Title optimization.
- Keyword-aware title/caption.
- Hashtag groups.
- Caption structure.
- Keyword research adapter.
- Posting-time recommendation.
- SEO metadata is persisted separately from free-form copy.

### Retention / emotional pacing
- Emotional arc model.
- Curious → Tense → Satisfied + Curious pattern where appropriate.
- Cliffhanger/recap triggers.
- Question/poll/follow/share/save engagement triggers.
- Pacing/retention analysis.
- Approved content must not be silently altered; warnings should be surfaced when a recommendation conflicts with approved content.

### Thumbnail / visual selection
- Generate 10 candidate frames.
- Reduce to 5 usable candidates.
- Human selects the final thumbnail.
- Candidate variety should cover close-up, wide, text overlay, stock/illustrative, and animation-style options where applicable.

### Sound / subtitle styling
- Sound-design workflow: logo intro, hook impact, whoosh, climax/tension music, soft outro, emotion-based BGM.
- Subtitle style requirements include hook/normal/important emphasis and animation guidance.
- Music library and commercial-use metadata remain explicit.

### Character / voice / Series Bible
- Main-character consistency target.
- Stable voice profiles.
- Background/temporary character prompt templates and voice pools.
- LoRA visual consistency is not considered done until training → storage → generation → consistency verification is evidenced.
- Series Bible fields: series_id, title, genre, characters, world_setting, tone, visual_style, continuity_rules.
- Continuity checks: character, timeline, location, props.

### Batch and calendar
- Five-episode batch planning.
- Human approval before batch generation.
- Daily-limit-aware scheduling.
- Weekly queue.
- Calendar dates/times/scheduling metadata.
- Collision validation.

## C. Platform/export requirements

Preparation only; no direct social publishing is part of the product boundary.

- TikTok: 9:16, target duration ≤ 3 min.
- YouTube Shorts: 9:16, target duration ≤ 60 sec.
- Facebook Reels: 9:16, target duration ≤ 90 sec.
- Instagram Reels: 9:16, target duration ≤ 90 sec.
- Master export remains available.
- Platform metadata validation and preparation are idempotent.
- Actual publication is recorded only from user/provider evidence.

## D. Provider abstraction and commercial-use checks

Video generation remains adapter-based:
`VideoGenerationAdapter → Provider → Job → Asset → Quality/Watermark Check`.

Provider-specific capabilities, limits, API/auth behavior, commercial terms, watermark behavior, quality, rate limits, retry semantics, and fallback behavior require live verification before being marked production-ready.

Watermark/commercial-use policy must:
- record provider/license evidence,
- block unsafe commercial use,
- never bypass or remove provider watermarks by circumvention.

## E. Performance and quota targets

- MVP processing target: **15–30 minutes** for representative content.
- Optimized target: **7–15 minutes**.
- Agnes/Groq/free-provider numbers are planning baselines only until live limits are verified.
- Quota accounting tracks used/remaining/retries/reset/fallback.
- Failed/retry jobs count toward provider quota where the provider bills/limits them that way.
- Queue scheduling must be quota-aware and prevent over-allocation.

## F. Subtitle quality requirements

- Burmese/Zawgyi normalization.
- Zawgyi detection target: **>95% detection quality** for the agreed evaluation set.
- Subtitle correction history.
- Correction metrics.
- Training/evaluation export for subtitle quality cases.
- Reading-speed and timing validation.
- Approved subtitle versions immutable.
- Burmese quality regressions require a fixed evaluation corpus and regression tests.

## G. Analytics and learning loop

Required loop:
Manual Data → Hook Library → Auto Defaults → Human Approve → Performance Data → Rule Refinement.

- Manual/social analytics import boundary.
- Compare title, hook, and thumbnail performance.
- Multi-signal experiment evidence.
- A/B outcome scoring and winner selection with guardrails.
- Do not alter defaults from one video; use evidence windows appropriate to the experiment (for example 5–10 content pieces when the rule requires it).
- Analytics must remain attributable to the publication/version that produced the result.

## H. Storage, privacy, and recovery

- Archive/cold-storage execution, not only a planning contract.
- Retention and deletion jobs must be observable and safe.
- User/data deletion pipeline: DB PII purge, storage purge, required audit-log treatment/anonymization, and verification evidence.
- Backup creation plus restore drill.
- Recovery must include database records and referenced media.
- Rollback must preserve approved output artifacts and record irreversible migrations.

## I. Production infrastructure verification

Final release evidence must cover:
- managed PostgreSQL health and migration head;
- managed Redis health and TLS configuration;
- DNS/HTTPS;
- exact CORS/trusted-host configuration;
- protected environment/secrets configuration;
- API readiness;
- real worker runtime;
- queue → worker → FFmpeg/Whisper → DB/storage;
- retry/DLQ/duplicate-dispatch recovery;
- monitoring/alerts;
- rollback and smoke/full-content verification.

## J. Testing and quality gates

The release evidence set must include:
- backend unit/integration tests;
- frontend typecheck/build;
- frontend Vitest/unit coverage where the project adopts it;
- full browser E2E;
- cross-tenant E2E;
- representative media/worker E2E;
- load/performance benchmark;
- dependency/security/container scanning;
- accessibility automated + manual audit;
- responsive desktop/tablet/mobile audit;
- security review / pen-test before final production sign-off.

## K. UI/design-system completeness

The canonical UI design specification is `docs/07-ui-design.md`. The README contains the current UI implementation summary; the roadmap owns requirements and status.

The UI specification must document:
- actual stack/tooling used;
- color tokens and semantic state mapping;
- typography and Burmese font strategy;
- spacing/radius/shadow tokens;
- desktop grid and responsive breakpoints;
- AppShell/sidebar/topbar/content layout;
- card/KPI/list/table/form/modal/tab patterns;
- button/input/badge/alert/progress/loading/empty/error primitives;
- focus/keyboard/screen-reader/touch-target rules;
- reduced-motion behavior;
- screen inventory and state matrix;
- what is implemented vs target vs still needing audit.

Current implementation tooling:
- Next.js 16 + React 19 + TypeScript.
- `lucide-react` for icons.
- Playwright for browser E2E.
- Native CSS design tokens and reusable React primitives; no Tailwind, shadcn/ui, Material UI, Chakra, or Figma-generated runtime dependency is currently declared in `package.json`.
- Inter + Noto Sans Myanmar are the current font stack.

## L. Screen-count reconciliation

There are three different historical counts and they must not be conflated:
1. **23 original MVP screens** from the Final Master Plan.
2. **26-screen design-system baseline** from `docs/07-ui-design.md`.
3. **Expanded Auto Production candidate screens** from the Auto Production specification.

The final implementation must publish one canonical screen inventory after deduplicating tabs/panels that do not need standalone routes. Until that audit is complete, screen coverage remains **FOUNDATION/VERIFY**, not “26 screens complete”.

## M. Legacy-document consolidation rule

Legacy documents may be removed only after their unique requirements are represented in this roadmap, README, UI specification, completion matrix, or focused operational runbook.

Do not maintain competing roadmaps. Supporting docs should contain implementation-specific detail, not alternate status or conflicting provider architecture.

## N. Final two-pass audit requirement

Before calling the documentation set complete:
1. Pass 1: requirement-by-requirement reconciliation against every source.
2. Pass 2: independent reverse check from the consolidated roadmap back against every source and repository directory, specifically searching for orphaned requirements, duplicate/conflicting documents, stale provider names, stale status claims, missing UI states, and unrepresented screens/components.
3. Only after both passes pass may legacy duplicates be deleted.
