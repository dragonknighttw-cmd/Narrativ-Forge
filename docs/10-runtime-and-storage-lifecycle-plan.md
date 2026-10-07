# Narrativ Forge — Runtime, Cost & Storage Lifecycle Plan

**Status:** AUTHORITATIVE PLAN  
**Scope:** Local Worker → Paid Worker Migration → Storage / Space Cleanup  
**Rule:** Free-first. No paid runtime until explicitly approved.

This is the single master plan for the three operational areas that must not be lost:
1. Local PC workers now
2. Paid worker infrastructure later
3. Storage/space cleanup and retention

## 1. Current decision

### NOW — Free Local Worker
Keep the current cloud control plane unchanged:

Render FastAPI → Neon PostgreSQL → Upstash Redis → Local Windows Worker(s)

The local worker performs heavy processing with the repository's existing Celery code and local FFmpeg.

### LATER — Paid Worker
When local processing becomes unreliable, slow, or inconvenient, replace/supplement the local worker with an always-on paid host.

The application, Celery tasks, Redis, DB, storage, retry/DLQ behavior, and environment contract must remain the same.

### ALWAYS — Storage Lifecycle
Working/raw/intermediate data is temporary. Approved final output and required metadata are preserved. Cleanup must be reference-safe and retention-based.

## 2. Local PC architecture

Home PC:
- Primary worker
- Optional Beat host
- FFmpeg
- Same repository worker code

Office PC:
- Secondary worker
- Same repository worker code
- No Beat by default

Failover:

Home ON + Office ON → both consume queued work  
Home OFF → Office continues  
Office OFF → Home continues  
Both OFF → jobs remain queued in Upstash

Important: do NOT create a separate worker application folder containing copied worker.py/tasks.py. Both PCs must run the real repository code under web-platform/backend. This prevents local code from diverging from production.

## 3. Local worker requirements

Required:
- Python 3.12-compatible environment
- Git
- FFmpeg
- backend dependencies
- Upstash Redis TLS connection
- production environment variables/secrets supplied locally

Do NOT install local openai-whisper by default.

Reason:
- Cloudflare Whisper is already part of the current architecture.
- Local disk is constrained.
- ML packages/models can consume much more space than the local budget.
- Local Whisper may be enabled later only on a machine with enough disk/RAM.

Windows worker command should use the repository application:

    celery -A app.workers.celery_app:celery_app worker --loglevel=INFO --pool=solo

Machine-specific paths must stay local and must never be committed.

Secrets must never be placed in batch files, source code, Git history, or logs.

## 4. Celery / Beat rules

The existing Celery app already contains durable delivery hardening:
- task tracking
- late acknowledgement
- worker-loss rejection
- prefetch=1
- broker retry on startup
- configured concurrency

Do not create a second routing/task implementation for local workers.

Beat is a scheduler, not a worker. Only one Beat instance should own a schedule unless duplicate scheduling is explicitly made safe.

If the Home PC is the Beat host and it is offline, scheduled maintenance pauses; queued jobs remain in Redis.

## 5. Local Definition of Done

Do not mark the local worker DONE merely because Celery starts.

Required:
- [ ] Home worker connects to Redis
- [ ] Office worker connects to Redis
- [ ] API creates a real processing job
- [ ] Job enters Redis and is consumed
- [ ] Real FFmpeg processing completes
- [ ] DB state changes correctly
- [ ] Required storage output succeeds
- [ ] Retry behavior is verified
- [ ] Worker-loss behavior is verified
- [ ] DLQ/failure handling is verified
- [ ] Two workers can consume queued jobs
- [ ] One-PC-off failover is verified
- [ ] Local cleanup cannot delete needed/unexported assets
- [ ] Logs contain no secrets

Until these pass: VERIFY, not DONE.

## 6. Paid worker plan — later

Paid infrastructure is a migration option, not a current dependency.

### Option A — Render Background Worker
Use when simplicity is preferred and an always-on paid worker is approved.

Use the existing worker runtime/image and the same:
- Celery app
- Redis
- environment contract
- FFmpeg path
- retry/DLQ behavior

Do not create it while the project remains free-only.

### Option B — Paid VPS
Use when monthly cost control and dedicated FFmpeg compute matter.

Run the same repository worker as a service with restart policy, logs, secrets, and enough CPU/RAM/disk.

### Option C — Another always-on host
Accept only if it provides reliable runtime, outbound TLS, sufficient FFmpeg resources, restart behavior, secrets, logs, and predictable cost.

Migration rule:

Local Worker → Paid Worker

Same application. Same tasks. Same queue. Same DB. Same storage. Same failure semantics.

No application rewrite.

## 7. Paid migration gate

Before paying for a worker:
- [ ] Local runtime benchmark measured
- [ ] 15–30 min/video target measured on representative processing
- [ ] CPU/RAM/disk requirement measured
- [ ] Local reliability problem identified
- [ ] Monthly cost ceiling approved
- [ ] Paid host selected
- [ ] Migration smoke test passed
- [ ] Rollback to local worker tested

Pay only for the bottleneck, not everything at once.

Likely first paid upgrade: worker compute if local processing becomes the bottleneck.

## 8. Storage tiers

| Tier | Service | Purpose | Default policy |
|---|---|---|---|
| Hot | Local PC | working/temp files | short retention |
| Warm | B2 | raw/intermediate media | temporary |
| Asset | Cloudinary | images/previews | retention-based |
| Workflow | Supabase | SRT/manifest/small files | preserve as required |
| Final | Google Drive | approved outputs | preserve |
| Source of truth | Neon | metadata/workflow state | preserve + backup |

Provider free limits are planning values and must be verified live before hard-coded enforcement.

## 9. Cleanup policy

Never automatically delete:
- approved final video
- required subtitle
- required metadata
- workflow/audit records
- the only verified copy of an approved export

Cleanup candidates:
- local temp files
- intermediate FFmpeg files
- stale partial downloads
- duplicate images
- failed-job artifacts after the investigation window
- raw media after verified final export and retention expiry
- old worker logs

Before deleting referenced raw/intermediate media, check the DB/workflow state.

## 10. Initial retention defaults

| Data | Retention | Action |
|---|---:|---|
| Local working files | 7 days | delete after successful completion |
| Local temp files | 1–3 days | delete |
| B2 raw media | 30 days | delete only after export/reference check |
| Cloudinary unused previews | 90 days | delete |
| Failed-job artifacts | 7 days | delete after review window |
| Final approved output | indefinite | preserve in Drive |
| Required subtitle/metadata | indefinite where required | preserve |
| Workflow/analytics history | product policy | preserve |

These are operational defaults, not permission to delete immediately. Cleanup jobs require the corresponding reference checks and tests.

## 11. Storage thresholds

80% → warning  
90% → high warning  
95% → emergency cleanup / block non-essential temporary work

Dashboard should show:
- B2 used / limit
- Supabase used / limit
- Cloudinary used / limit
- Drive used / limit
- Local worker disk used / free

A full provider must not silently cause data loss.

## 12. Cleanup order

1. Expired local temp files
2. Stale failed/partial artifacts
3. Duplicate/intermediate images
4. Exported raw media past retention
5. Explicitly supported archive/compression
6. Warning/block non-essential generation

Never begin cleanup by deleting final approved output.

## 13. Operational phases

### Phase A — Free Local
Render API + Neon + Upstash + Home Worker + optional Office Worker + FFmpeg + Cloudflare Whisper + B2/Supabase/Cloudinary + Google Drive.

### Phase B — Free Local + Verified Overflow
Only add another free worker if its runtime is genuinely reliable and has been tested. A free tier alone is not enough.

### Phase C — Paid Worker
Render Background Worker, paid VPS, or another verified always-on host.

### Phase D — Paid Scale
Scale worker compute, storage, and generation providers independently according to the measured bottleneck.

## 14. Storage Definition of Done

- [ ] Usage collection
- [ ] 80/90/95% warnings
- [ ] Retention jobs
- [ ] DB/reference safety checks
- [ ] Local cleanup
- [ ] B2 cleanup
- [ ] Cloudinary cleanup
- [ ] Failed-job cleanup
- [ ] Archive path
- [ ] Cleanup history/audit
- [ ] Emergency procedure tests

## 15. Documentation rule

This file is the single authoritative plan for:
- local worker deployment
- future paid worker migration
- storage/space cleanup

Do not create another competing Local Worker or Storage master plan.

Other docs remain authoritative for their own domains:
- 02-stack.md — stack/constraints
- 03-architecture.md — architecture
- 04-current-vs-target.md — status
- 05-execution-roadmap.md — execution/release gates
- 06-future-reserve.md — deferred technology
- 09-auto-production-expansion.md — Auto Production requirements

## 16. Release rule

Production-ready is NOT declared until the real worker runtime, processing path, retry/DLQ behavior, and storage lifecycle safety tests pass.


## Current execution ownership — 2026-10-07

This document remains the authoritative runtime/storage plan. The current split is:

### User gate
- Run the real Home/Office Windows worker with repository code + FFmpeg.
- Prove queue → worker → FFmpeg → DB/storage → retry/DLQ → failover.
- Execute the real storage cleanup/emergency drill after the worker path is available.
- Approve any paid worker migration only when the documented migration gates are met.

### Assistant track
- Keep worker code, Celery delivery semantics, storage lifecycle code, cleanup safety, tests, and runbooks hardened.
- Keep retention rules reference-safe and protect the only approved final output.
- Keep this plan synchronized with the release checklist; no code-only change can mark the real worker or cleanup drill DONE.
