# Project Structure & File Inventory

> **Purpose:** A repository-grounded map of the current Narrativ Forge source tree, its major subsystems, and every tracked file visible in the Git tree. This document describes repository contents, not a guarantee that every component is deployed or operational.

## Snapshot and scope

- Repository: [`dragonknighttw-cmd/Narrativ-Forge`](https://github.com/dragonknighttw-cmd/Narrativ-Forge)
- Branch/ref inspected: `main`
- Git tree commit: `bb6cc426d47661d6353bc38dcfaf1e6185a78b59`
- Snapshot date: 2026-10-15
- Git tree completeness: **not truncated** by GitHub's recursive tree endpoint.
- Tracked entries in this snapshot: **433** (68 directories and 365 files).
- This inventory covers paths tracked in this Git tree. It does **not** include ignored/untracked local files, secret values, generated runtime files, remote database objects, or deployment-provider settings that are not stored in the repository.
- File-purpose notes are intentionally conservative: names and paths provide navigation hints; exact behavior must be confirmed by reading each file and its callers.

## Quick orientation

| Area | Observed role |
|---|---|
| `.github/workflows/` | CI, security scanning, evidence collection, deployment/preflight and packaging automation. |
| `docs/` | Project, architecture, API, database, deployment, operations, testing, acceptance and report documentation. |
| `archive/legacy/` | Historical documentation and legacy material; not assumed to be active runtime. |
| `infra/` | Infrastructure-specific assets and runbooks, including Cloudflare Worker and Kaggle-related areas. |
| `scripts/` | Maintenance, backup/restore, load-test and Windows portable-package helpers. |
| `apps/web-platform/backend/` | Backend application source and supporting assets. Inspect its package/module structure for authoritative implementation details. |
| `apps/web-platform/cloudflare/` | Cloudflare/edge integration and related deployment assets. |
| `apps/web-platform/frontend/` | Next.js/TypeScript frontend, App Router pages, shared components, API helpers and end-to-end tests. |
| `apps/mobile/` | Mobile-related scope/documentation area; current contents should be checked before assuming a shipped mobile application exists. |
| Root Markdown files | Project entry point, current-state notes, roadmap, security/tooling instructions, UI system and audit/phase records. |
| Root deployment/config files | Render, Netlify, OpenCode and repository ignore/configuration settings. |

## Root-level layout

```text
Narrativ-Forge/
├── .github/
│   └── workflows/
│       ├── application-schema-restore-evidence.yml
│       ├── backup-restore-evidence.yml
│       ├── ci.yml
│       ├── cloudflare-whisper-live-evidence.yml
│       ├── cloudflare-whisper-preflight.yml
│       ├── cloudflare-whisper.yml
│       ├── codeql.yml
│       ├── free-provider-smoke-evidence.yml
│       ├── kaggle-worker.yml
│       ├── local-runtime-evidence.yml
│       ├── managed-staging-restore-evidence.yml
│       ├── openrouter-free-model-evidence.yml
│       ├── render-live-health-ai-fallback.yml
│       ├── repository-gate.yml
│       ├── security.yml
│       ├── windows-local-runtime-evidence.yml
│       ├── windows-portable-package.yml
│       └── worker-evidence.yml
├── .gitignore
├── .opencode/
│   └── agents/
│       └── reviewer.md
├── .trivyignore
├── AGENTS.md
├── archive/
│   └── legacy/
│       ├── docs/
│       │   ├── 01-product.md
│       │   ├── 02-stack.md
│       │   ├── 03-architecture.md
│       │   ├── 04-current-vs-target.md
│       │   ├── 07-ui-design.md
│       │   ├── 08-manual-mode.md
│       │   ├── 09-auto-production-expansion.md
│       │   └── 10-runtime-and-storage-lifecycle-plan.md
│       ├── documentation-migration-provenance.md
│       ├── mobile-scope.md
│       ├── release-readiness-source.md
│       ├── roadmap.md
│       └── status-matrix-source.md
├── CURRENT_STATE.md
├── docs/
│   ├── 01-product.md
│   ├── 02-stack.md
│   ├── 03-architecture.md
│   ├── 04-current-vs-target.md
│   ├── 07-ui-design.md
│   ├── 08-manual-mode.md
│   ├── 09-auto-production-expansion.md
│   ├── 10-runtime-and-storage-lifecycle-plan.md
│   ├── 11-release-readiness-checklist.md
│   ├── 21-master-completion-matrix.md
│   ├── AI_PROVIDER_ACCEPTANCE_MATRIX.md
│   ├── AI_RAG.md
│   ├── API.md
│   ├── ARCHITECTURE.md
│   ├── BURMESE_MEDIA_ACCEPTANCE.md
│   ├── CLOUD_LOCAL_PACKAGING_AUDIT.md
│   ├── DATABASE.md
│   ├── DEPLOYMENT.md
│   ├── DEVELOPMENT.md
│   ├── FREE_FIRST_READINESS_CHECKPOINT.md
│   ├── LOCAL_RUNTIME_FOLLOW_UP.md
│   ├── LOCAL_RUNTIME.md
│   ├── MANAGED_STAGING_RESTORE_SMOKE.md
│   ├── MASTER_REMAINING_WORK.md
│   ├── master_result all
│   ├── OPENCODE_FREE_MODELS.md
│   ├── OPENROUTER_FREE_MODEL_AUDIT.md
│   ├── OPERATIONS.md
│   ├── ops/
│   │   └── worker-runtime.md
│   ├── OWNER_ACTION_CHECKLIST.md
│   ├── README.md
│   ├── Report/
│   │   ├── 00_EXECUTIVE_SUMMARY.md
│   │   ├── 01_TEST_RESULTS.md
│   │   ├── 02_CODE_CHANGES.md
│   │   ├── 03_WINDOWS_LOCAL_TEST.md
│   │   ├── 04_CLOUD_DEPLOYMENT_STATUS.md
│   │   ├── 05_SECURITY_AND_RISKS.md
│   │   ├── 06_REMAINING_WORK_AND_OWNER_ACTIONS.md
│   │   ├── 07_EVIDENCE_INDEX.md
│   │   ├── ASR_BURMESE_LOCAL_ACCEPTANCE_RESULTS_2026-10-13.md
│   │   ├── ASR_BURMESE_LOCAL_FREE_WORK_2026-10-13.md
│   │   ├── BURMESE_SAMPLE_PREFLIGHT_2026-10-12.md
│   │   ├── CLOUD_DEPLOYMENT_STATUS_2026-10-12.md
│   │   ├── LOCAL_BURMESE_ASR_ACCEPTANCE_GUIDE_2026-10-13.md
│   │   ├── LOCAL_WINDOWS_UNICODE_RUNTIME_REPORT.md
│   │   └── RENDER_FRONTEND_LIVE_CHECKPOINT_2026-10-13.md
│   ├── STORAGE.md
│   ├── TELEGRAM_INTEGRATION.md
│   ├── TESTING.md
│   ├── TROUBLESHOOTING.md
│   └── WINDOWS_PORTABLE_PACKAGE.md
├── infra/
│   ├── cloudflare-worker/
│   │   ├── package.json
│   │   ├── README.md
│   │   ├── src/
│   │   │   └── index.ts
│   │   └── wrangler.toml
│   ├── kaggle/
│   │   ├── dispatch.py
│   │   ├── kaggle_worker.py
│   │   ├── kernel-metadata.json
│   │   ├── README.md
│   │   └── test_dispatch.py
│   ├── managed-services.md
│   └── production-runbook.md
├── INFRASTRUCTURE_AUDIT.md
├── apps/mobile/
│   └── README.md
├── netlify.toml
├── opencode.json
├── PHASE_EXECUTION.md
├── PROJECT_OVERVIEW.md
├── README.md
├── render.worker.yaml
├── render.yaml
├── ROADMAP.md
├── scripts/
│   ├── backup_db.py
│   ├── phase-load-test.py
│   ├── restore_db.py
│   └── windows-portable/
│       ├── Start-NarrativForge.ps1
│       └── Stop-NarrativForge.ps1
├── SECURITY.md
├── TOOL.md
├── UI_DESIGN_SYSTEM.md
└── apps/web-platform/
    ├── backend/
    │   ├── .env.example
    │   ├── alembic/
    │   │   ├── env.py
    │   │   ├── script.py.mako
    │   │   └── versions/
    │   │       ├── 0001_bootstrap.py
    │   │       ├── 0002_asset_storage_metadata.py
    │   │       ├── 0003_scene_script_scope.py
    │   │       ├── 0004_processing_retry_dlq.py
    │   │       ├── 0005_resumable_uploads.py
    │   │       ├── 0006_idempotency_keys.py
    │   │       ├── 0007_optimistic_locking.py
    │   │       ├── 0008_storage_replicas.py
    │   │       ├── 0009_phase4_foundations.py
    │   │       ├── 0010_tenant_content_scope.py
    │   │       ├── 0011_webhook_secret.py
    │   │       ├── 0012_stripe_webhook_events.py
    │   │       ├── 0013_tenant_scope_integrations.py
    │   │       ├── 0014_security_performance_hardening.py
    │   │       ├── 0015_revoke_public_table_grants.py
    │   │       ├── 0016_scene_constraint_repair.py
    │   │       ├── 0017_asset_deleted_at.py
    │   │       ├── 0017_release_maturity.py
    │   │       ├── 0018_tenant_backfill_guard.py
    │   │       └── 0019_series_bible.py
    │   ├── alembic.ini
    │   ├── app/
    │   │   ├── __init__.py
    │   │   ├── api/
    │   │   │   ├── __init__.py
    │   │   │   ├── dependencies.py
    │   │   │   ├── router.py
    │   │   │   └── routes/
    │   │   │       ├── __init__.py
    │   │   │       ├── assets.py
    │   │   │       ├── audit.py
    │   │   │       ├── auth.py
    │   │   │       ├── auto_mode.py
    │   │   │       ├── cloud_processing.py
    │   │   │       ├── episodes.py
    │   │   │       ├── export.py
    │   │   │       ├── google_drive.py
    │   │   │       ├── health.py
    │   │   │       ├── hooks.py
    │   │   │       ├── ideas.py
    │   │   │       ├── jobs.py
    │   │   │       ├── phase4.py
    │   │   │       ├── production_intelligence.py
    │   │   │       ├── production_pipeline.py
    │   │   │       ├── review.py
    │   │   │       ├── scenes.py
    │   │   │       ├── scripts.py
    │   │   │       ├── search.py
    │   │   │       ├── series.py
    │   │   │       ├── subtitles.py
    │   │   │       ├── telegram.py
    │   │   │       └── uploads.py
    │   │   ├── core/
    │   │   │   ├── __init__.py
    │   │   │   └── config.py
    │   │   ├── db.py
    │   │   ├── infrastructure/
    │   │   │   ├── __init__.py
    │   │   │   └── redis.py
    │   │   ├── main.py
    │   │   ├── metrics.py
    │   │   ├── middleware/
    │   │   │   ├── __init__.py
    │   │   │   └── idempotency.py
    │   │   ├── models/
    │   │   │   ├── __init__.py
    │   │   │   ├── core.py
    │   │   │   └── phase4.py
    │   │   ├── observability.py
    │   │   ├── services/
    │   │   │   ├── __init__.py
    │   │   │   ├── ai_adapter.py
    │   │   │   ├── ai_usage_tracker.py
    │   │   │   ├── asset_gc.py
    │   │   │   ├── audit.py
    │   │   │   ├── auto_mode.py
    │   │   │   ├── batch_generator.py
    │   │   │   ├── code_completion.py
    │   │   │   ├── content_quality.py
    │   │   │   ├── email.py
    │   │   │   ├── expanded_production.py
    │   │   │   ├── future_foundations.py
    │   │   │   ├── hook_engineering.py
    │   │   │   ├── operating_maturity.py
    │   │   │   ├── orchestration.py
    │   │   │   ├── passwords.py
    │   │   │   ├── phase_52_60.py
    │   │   │   ├── phase_61_68.py
    │   │   │   ├── phase_69_76.py
    │   │   │   ├── phase_77_84.py
    │   │   │   ├── phase_continuation.py
    │   │   │   ├── processing.py
    │   │   │   ├── production_pipeline.py
    │   │   │   ├── production_scale.py
    │   │   │   ├── provider_fallback.py
    │   │   │   ├── provider_quota.py
    │   │   │   ├── provider_registry.py
    │   │   │   ├── rag_embeddings.py
    │   │   │   ├── real_processing.py
    │   │   │   ├── release_maturity_store.py
    │   │   │   ├── release_maturity.py
    │   │   │   ├── selective_regeneration.py
    │   │   │   ├── series_continuity.py
    │   │   │   ├── storage_lifecycle.py
    │   │   │   ├── storage.py
    │   │   │   ├── subtitles.py
    │   │   │   ├── telegram.py
    │   │   │   └── thumbnail_candidate.py
    │   │   └── workers/
    │   │       ├── __init__.py
    │   │       ├── celery_app.py
    │   │       ├── concurrency.py
    │   │       ├── kaggle_job_runner.py
    │   │       ├── mock_worker.py
    │   │       ├── real_worker.py
    │   │       └── tasks.py
    │   ├── Dockerfile
    │   ├── Dockerfile.worker
    │   ├── pytest.ini
    │   ├── requirements-real-processing.txt
    │   ├── requirements.txt
    │   ├── scripts/
    │   │   ├── __init__.py
    │   │   ├── backup_db.py
    │   │   ├── bootstrap_admin.py
    │   │   ├── final_production_gate.py
    │   │   ├── free_provider_smoke.py
    │   │   ├── kaggle_worker.py
    │   │   ├── local_media_preflight.py
    │   │   ├── openrouter_free_model_smoke.py
    │   │   ├── production_smoke.py
    │   │   ├── restore_db.py
    │   │   ├── seed_e2e_tenant.py
    │   │   ├── verify_postgres_backup.py
    │   │   └── worker_smoke.py
    │   └── tests/
    │       ├── client_utils.py
    │       ├── conftest.py
    │       ├── test_ai_adapter.py
    │       ├── test_asset_gc.py
    │       ├── test_batch_generator.py
    │       ├── test_checksum_dedupe.py
    │       ├── test_cloud_processing_security.py
    │       ├── test_code_completion.py
    │       ├── test_content_quality.py
    │       ├── test_database_config.py
    │       ├── test_expanded_production.py
    │       ├── test_foundation.py
    │       ├── test_free_provider_smoke.py
    │       ├── test_health_and_search.py
    │       ├── test_hybrid_storage.py
    │       ├── test_idempotency_postgres.py
    │       ├── test_infrastructure_integration.py
    │       ├── test_local_media_preflight.py
    │       ├── test_magic_link.py
    │       ├── test_metrics.py
    │       ├── test_migrations.py
    │       ├── test_observability.py
    │       ├── test_openrouter_free_model_smoke.py
    │       ├── test_operating_maturity.py
    │       ├── test_optimistic_locking.py
    │       ├── test_orchestration.py
    │       ├── test_orm_relationships.py
    │       ├── test_passwords.py
    │       ├── test_phase_52_60.py
    │       ├── test_phase_61_68.py
    │       ├── test_phase_69_76.py
    │       ├── test_phase_77_84.py
    │       ├── test_phase_continuation.py
    │       ├── test_phase0_security.py
    │       ├── test_phase4_membership.py
    │       ├── test_production_foundations.py
    │       ├── test_production_intelligence.py
    │       ├── test_production_pipeline.py
    │       ├── test_production_scale.py
    │       ├── test_provider_quota.py
    │       ├── test_provider_registry.py
    │       ├── test_rag_embeddings.py
    │       ├── test_real_processing_subprocess.py
    │       ├── test_redis_config.py
    │       ├── test_release_maturity_store.py
    │       ├── test_release_maturity.py
    │       ├── test_resumable_uploads.py
    │       ├── test_root_restore_db.py
    │       ├── test_script_scene_api_security.py
    │       ├── test_security_config.py
    │       ├── test_security_hardening.py
    │       ├── test_security_observability.py
    │       ├── test_selective_regeneration.py
    │       ├── test_series_bible.py
    │       ├── test_series_continuity.py
    │       ├── test_storage_lifecycle.py
    │       ├── test_storage_provider.py
    │       ├── test_storage_routing.py
    │       ├── test_subtitle_api_security.py
    │       ├── test_subtitle_normalization.py
    │       ├── test_supabase_auth.py
    │       ├── test_tasks_celery.py
    │       ├── test_tenant_isolation.py
    │       ├── test_thumbnail_candidate.py
    │       ├── test_whisper_fallback.py
    │       └── test_worker_concurrency.py
    ├── cloudflare/
    │   └── whisper-worker/
    │       ├── README.md
    │       ├── src/
    │       │   └── index.ts
    │       ├── test/
    │       │   └── worker.test.mjs
    │       └── wrangler.jsonc
    ├── docs/
    │   ├── architecture.md
    │   ├── foundation-checklist.md
    │   └── runbooks/
    │       ├── restore.md
    │       ├── rotate_secrets.md
    │       └── stuck_job.md
    └── frontend/
        ├── .env.example
        ├── app/
        │   ├── [...module]/
        │   │   └── page.tsx
        │   ├── analytics/
        │   │   └── page.tsx
        │   ├── auth/
        │   │   └── magic-link/
        │   │       └── page.tsx
        │   ├── auto-mode/
        │   │   └── page.tsx
        │   ├── dashboard/
        │   │   └── page.tsx
        │   ├── episodes/
        │   │   ├── [id]/
        │   │   │   ├── assets/
        │   │   │   │   └── page.tsx
        │   │   │   ├── export/
        │   │   │   │   └── page.tsx
        │   │   │   ├── page.tsx
        │   │   │   ├── review/
        │   │   │   │   └── page.tsx
        │   │   │   ├── scenes/
        │   │   │   │   └── page.tsx
        │   │   │   ├── script/
        │   │   │   │   └── page.tsx
        │   │   │   └── subtitle/
        │   │   │       └── page.tsx
        │   │   └── page.tsx
        │   ├── globals.css
        │   ├── hooks/
        │   │   └── page.tsx
        │   ├── ideas/
        │   │   └── page.tsx
        │   ├── invite/
        │   │   └── page.tsx
        │   ├── layout.tsx
        │   ├── login/
        │   │   └── page.tsx
        │   ├── manual-log/
        │   │   └── page.tsx
        │   ├── page.tsx
        │   ├── processing/
        │   │   └── page.tsx
        │   ├── production-intelligence/
        │   │   └── page.tsx
        │   ├── publishing-prep/
        │   │   └── page.tsx
        │   ├── series/
        │   │   ├── [id]/
        │   │   │   └── page.tsx
        │   │   └── page.tsx
        │   └── usage/
        │       └── page.tsx
        ├── components/
        │   ├── app-shell.tsx
        │   ├── auth-guard.tsx
        │   ├── domain-forms.tsx
        │   ├── toast.tsx
        │   └── ui-primitives.tsx
        ├── e2e/
        │   ├── cross-tenant-isolation.spec.ts
        │   ├── phase4-foundation.spec.ts
        │   ├── production-flow.spec.ts
        │   └── series-bible-persistence.spec.ts
        ├── lib/
        │   ├── api.ts
        │   ├── cloud-whisper.ts
        │   └── workflow-states.ts
        ├── next-env.d.ts
        ├── next.config.ts
        ├── package-lock.json
        ├── package.json
        ├── playwright.config.ts
        └── tsconfig.json
```

## Subsystem guide

### 1. Repository governance and automation

- `.github/workflows/`: automated CI and evidence workflows. The filenames indicate separate concerns such as CI, CodeQL/security, repository gates, restore evidence, runtime checks, provider checks and Windows packaging. Read each workflow before relying on its name to infer its triggers or success criteria.
- `.opencode/agents/`: agent-specific instruction files.
- `AGENTS.md`: repository-level instructions for contributors/agents.
- `.gitignore`, `.trivyignore`: local-file exclusions and scanner suppressions. Scanner exceptions should be reviewed rather than treated as proof that a finding is harmless.

### 2. Documentation and project records

- `README.md`: starting point for the repository.
- `PROJECT_OVERVIEW.md`, `CURRENT_STATE.md`, `ROADMAP.md`, `PHASE_EXECUTION.md`: overview, status, planned direction and phase tracking.
- `INFRASTRUCTURE_AUDIT.md`, `SECURITY.md`: infrastructure and security notes.
- `UI_DESIGN_SYSTEM.md`, `TOOL.md`: UI and tooling conventions.
- `docs/`: product, stack, architecture, API, database, storage, deployment, development, operations, testing, troubleshooting, AI/RAG, provider acceptance, local runtime, Windows packaging, Telegram integration and release-readiness documentation.
- `docs/Report/`: dated or scoped evidence reports. Treat these as snapshots; check their dates and evidence links before using them as current deployment truth.
- `archive/legacy/`: explicitly historical content. Do not treat archived plans as current implementation without confirming source code.

### 3. Web platform

- `apps/web-platform/frontend/app/`: route-oriented UI. The tracked tree includes routes for analytics, auth/magic-link, auto mode, dashboard, episodes and episode sub-pages (assets, export, review, scenes, script, subtitle), hooks, ideas, invite, login, manual log, processing, production intelligence, publishing prep, series and usage.
- `apps/web-platform/frontend/components/`: shared shell, auth guard, domain forms, toast and UI primitives.
- `apps/web-platform/frontend/lib/`: API client, Cloud Whisper integration and workflow-state helpers.
- `apps/web-platform/frontend/e2e/`: Playwright tests, including cross-tenant isolation, production flow and series-bible persistence coverage.
- `apps/web-platform/frontend/package.json`, `package-lock.json`, `tsconfig.json`, `next.config.ts`, `playwright.config.ts`: package scripts/dependencies and build/test configuration. Consult these files for exact commands and versions.
- `apps/web-platform/backend/`: backend code. The per-file inventory below records every tracked path; inspect backend entry points, route registration, models and tests to determine actual request/data flow.
- `apps/web-platform/cloudflare/`: edge worker integration/configuration. Confirm bindings, environment variables and routing from source and provider settings.

### 4. Infrastructure, workers and operational scripts

- `infra/cloudflare-worker/`: Cloudflare Worker assets.
- `infra/kaggle/`: Kaggle worker/runtime assets.
- `infra/managed-services.md`, `infra/production-runbook.md`: infrastructure/service and operations references.
- `scripts/backup_db.py`, `scripts/restore_db.py`: database backup/restore helper scripts (review configuration and safety behavior before execution).
- `scripts/phase-load-test.py`: load-test helper.
- `scripts/windows-portable/`: Windows portable package tooling.
- `render.yaml`, `render.worker.yaml`, `netlify.toml`: deployment configuration tracked in the repository; these files alone cannot prove live services match the configuration.

### 5. Authentication, data and external services

The repository includes documentation areas for API, database, storage, deployment and operations, plus frontend API/auth-related source and backend modules. The exact runtime topology, Supabase schema/policies, identity provisioning behavior, Cloudflare bindings and Render service state must be verified against the corresponding source/configuration and provider consoles. **Do not infer production readiness from the existence of a config file or a documentation statement alone.**

### 6. Tests and quality gates

- Workflow files under `.github/workflows/` define automation; read their actual YAML to learn what is required, what runs on each event, and which failures block changes.
- `apps/web-platform/frontend/e2e/` contains tracked browser-level tests.
- The full inventory below includes all tracked test-related paths visible in this snapshot; tests not named here may be colocated with implementation files.

## Complete file inventory

Every tracked file in the inspected tree is listed below. Descriptions are navigation hints based on the path/filename, not a substitute for code review.

- `.github/workflows/application-schema-restore-evidence.yml` — GitHub Actions workflow; inspect triggers, permissions, secrets, and artifacts in the file.
- `.github/workflows/backup-restore-evidence.yml` — GitHub Actions workflow; inspect triggers, permissions, secrets, and artifacts in the file.
- `.github/workflows/ci.yml` — GitHub Actions workflow; inspect triggers, permissions, secrets, and artifacts in the file.
- `.github/workflows/cloudflare-whisper-live-evidence.yml` — GitHub Actions workflow; inspect triggers, permissions, secrets, and artifacts in the file.
- `.github/workflows/cloudflare-whisper-preflight.yml` — GitHub Actions workflow; inspect triggers, permissions, secrets, and artifacts in the file.
- `.github/workflows/cloudflare-whisper.yml` — GitHub Actions workflow; inspect triggers, permissions, secrets, and artifacts in the file.
- `.github/workflows/codeql.yml` — GitHub Actions workflow; inspect triggers, permissions, secrets, and artifacts in the file.
- `.github/workflows/free-provider-smoke-evidence.yml` — GitHub Actions workflow; inspect triggers, permissions, secrets, and artifacts in the file.
- `.github/workflows/kaggle-worker.yml` — GitHub Actions workflow; inspect triggers, permissions, secrets, and artifacts in the file.
- `.github/workflows/local-runtime-evidence.yml` — GitHub Actions workflow; inspect triggers, permissions, secrets, and artifacts in the file.
- `.github/workflows/managed-staging-restore-evidence.yml` — GitHub Actions workflow; inspect triggers, permissions, secrets, and artifacts in the file.
- `.github/workflows/openrouter-free-model-evidence.yml` — GitHub Actions workflow; inspect triggers, permissions, secrets, and artifacts in the file.
- `.github/workflows/render-live-health-ai-fallback.yml` — GitHub Actions workflow; inspect triggers, permissions, secrets, and artifacts in the file.
- `.github/workflows/repository-gate.yml` — GitHub Actions workflow; inspect triggers, permissions, secrets, and artifacts in the file.
- `.github/workflows/security.yml` — GitHub Actions workflow; inspect triggers, permissions, secrets, and artifacts in the file.
- `.github/workflows/windows-local-runtime-evidence.yml` — GitHub Actions workflow; inspect triggers, permissions, secrets, and artifacts in the file.
- `.github/workflows/windows-portable-package.yml` — GitHub Actions workflow; inspect triggers, permissions, secrets, and artifacts in the file.
- `.github/workflows/worker-evidence.yml` — GitHub Actions workflow; inspect triggers, permissions, secrets, and artifacts in the file.
- `.gitignore` — Git ignore rules.
- `.opencode/agents/reviewer.md` — OpenCode agent instruction/configuration.
- `.trivyignore` — Trivy vulnerability-scan exceptions; review every exception.
- `AGENTS.md` — Repository agent/developer instructions.
- `CURRENT_STATE.md` — Current project state/status record.
- `INFRASTRUCTURE_AUDIT.md` — Infrastructure audit findings and evidence.
- `PHASE_EXECUTION.md` — Phase execution plan/status.
- `PROJECT_OVERVIEW.md` — High-level project overview.
- `README.md` — Repository entry point and quick-start documentation.
- `ROADMAP.md` — Project roadmap.
- `SECURITY.md` — Security policy/guidance.
- `TOOL.md` — Tooling guidance.
- `UI_DESIGN_SYSTEM.md` — UI design-system notes.
- `archive/legacy/docs/01-product.md` — Archived/legacy material; historical reference, not assumed to be active runtime code.
- `archive/legacy/docs/02-stack.md` — Archived/legacy material; historical reference, not assumed to be active runtime code.
- `archive/legacy/docs/03-architecture.md` — Archived/legacy material; historical reference, not assumed to be active runtime code.
- `archive/legacy/docs/04-current-vs-target.md` — Archived/legacy material; historical reference, not assumed to be active runtime code.
- `archive/legacy/docs/07-ui-design.md` — Archived/legacy material; historical reference, not assumed to be active runtime code.
- `archive/legacy/docs/08-manual-mode.md` — Archived/legacy material; historical reference, not assumed to be active runtime code.
- `archive/legacy/docs/09-auto-production-expansion.md` — Archived/legacy material; historical reference, not assumed to be active runtime code.
- `archive/legacy/docs/10-runtime-and-storage-lifecycle-plan.md` — Archived/legacy material; historical reference, not assumed to be active runtime code.
- `archive/legacy/documentation-migration-provenance.md` — Archived/legacy material; historical reference, not assumed to be active runtime code.
- `archive/legacy/mobile-scope.md` — Archived/legacy material; historical reference, not assumed to be active runtime code.
- `archive/legacy/release-readiness-source.md` — Archived/legacy material; historical reference, not assumed to be active runtime code.
- `archive/legacy/roadmap.md` — Archived/legacy material; historical reference, not assumed to be active runtime code.
- `archive/legacy/status-matrix-source.md` — Archived/legacy material; historical reference, not assumed to be active runtime code.
- `docs/01-product.md` — Project documentation; see this file for its authoritative topic and scope.
- `docs/02-stack.md` — Project documentation; see this file for its authoritative topic and scope.
- `docs/03-architecture.md` — Project documentation; see this file for its authoritative topic and scope.
- `docs/04-current-vs-target.md` — Project documentation; see this file for its authoritative topic and scope.
- `docs/07-ui-design.md` — Project documentation; see this file for its authoritative topic and scope.
- `docs/08-manual-mode.md` — Project documentation; see this file for its authoritative topic and scope.
- `docs/09-auto-production-expansion.md` — Project documentation; see this file for its authoritative topic and scope.
- `docs/10-runtime-and-storage-lifecycle-plan.md` — Project documentation; see this file for its authoritative topic and scope.
- `docs/11-release-readiness-checklist.md` — Project documentation; see this file for its authoritative topic and scope.
- `docs/21-master-completion-matrix.md` — Project documentation; see this file for its authoritative topic and scope.
- `docs/AI_PROVIDER_ACCEPTANCE_MATRIX.md` — Project documentation; see this file for its authoritative topic and scope.
- `docs/AI_RAG.md` — Project documentation; see this file for its authoritative topic and scope.
- `docs/API.md` — Project documentation; see this file for its authoritative topic and scope.
- `docs/ARCHITECTURE.md` — Project documentation; see this file for its authoritative topic and scope.
- `docs/BURMESE_MEDIA_ACCEPTANCE.md` — Project documentation; see this file for its authoritative topic and scope.
- `docs/CLOUD_LOCAL_PACKAGING_AUDIT.md` — Project documentation; see this file for its authoritative topic and scope.
- `docs/DATABASE.md` — Project documentation; see this file for its authoritative topic and scope.
- `docs/DEPLOYMENT.md` — Project documentation; see this file for its authoritative topic and scope.
- `docs/DEVELOPMENT.md` — Project documentation; see this file for its authoritative topic and scope.
- `docs/FREE_FIRST_READINESS_CHECKPOINT.md` — Project documentation; see this file for its authoritative topic and scope.
- `docs/LOCAL_RUNTIME.md` — Project documentation; see this file for its authoritative topic and scope.
- `docs/LOCAL_RUNTIME_FOLLOW_UP.md` — Project documentation; see this file for its authoritative topic and scope.
- `docs/MANAGED_STAGING_RESTORE_SMOKE.md` — Project documentation; see this file for its authoritative topic and scope.
- `docs/MASTER_REMAINING_WORK.md` — Project documentation; see this file for its authoritative topic and scope.
- `docs/OPENCODE_FREE_MODELS.md` — Project documentation; see this file for its authoritative topic and scope.
- `docs/OPENROUTER_FREE_MODEL_AUDIT.md` — Project documentation; see this file for its authoritative topic and scope.
- `docs/OPERATIONS.md` — Project documentation; see this file for its authoritative topic and scope.
- `docs/OWNER_ACTION_CHECKLIST.md` — Project documentation; see this file for its authoritative topic and scope.
- `docs/README.md` — Project documentation; see this file for its authoritative topic and scope.
- `docs/Report/00_EXECUTIVE_SUMMARY.md` — Operational/test/deployment evidence report; see report content for scope and date.
- `docs/Report/01_TEST_RESULTS.md` — Operational/test/deployment evidence report; see report content for scope and date.
- `docs/Report/02_CODE_CHANGES.md` — Operational/test/deployment evidence report; see report content for scope and date.
- `docs/Report/03_WINDOWS_LOCAL_TEST.md` — Operational/test/deployment evidence report; see report content for scope and date.
- `docs/Report/04_CLOUD_DEPLOYMENT_STATUS.md` — Operational/test/deployment evidence report; see report content for scope and date.
- `docs/Report/05_SECURITY_AND_RISKS.md` — Operational/test/deployment evidence report; see report content for scope and date.
- `docs/Report/06_REMAINING_WORK_AND_OWNER_ACTIONS.md` — Operational/test/deployment evidence report; see report content for scope and date.
- `docs/Report/07_EVIDENCE_INDEX.md` — Operational/test/deployment evidence report; see report content for scope and date.
- `docs/Report/ASR_BURMESE_LOCAL_ACCEPTANCE_RESULTS_2026-10-13.md` — Operational/test/deployment evidence report; see report content for scope and date.
- `docs/Report/ASR_BURMESE_LOCAL_FREE_WORK_2026-10-13.md` — Operational/test/deployment evidence report; see report content for scope and date.
- `docs/Report/BURMESE_SAMPLE_PREFLIGHT_2026-10-12.md` — Operational/test/deployment evidence report; see report content for scope and date.
- `docs/Report/CLOUD_DEPLOYMENT_STATUS_2026-10-12.md` — Operational/test/deployment evidence report; see report content for scope and date.
- `docs/Report/LOCAL_BURMESE_ASR_ACCEPTANCE_GUIDE_2026-10-13.md` — Operational/test/deployment evidence report; see report content for scope and date.
- `docs/Report/LOCAL_WINDOWS_UNICODE_RUNTIME_REPORT.md` — Operational/test/deployment evidence report; see report content for scope and date.
- `docs/Report/RENDER_FRONTEND_LIVE_CHECKPOINT_2026-10-13.md` — Operational/test/deployment evidence report; see report content for scope and date.
- `docs/STORAGE.md` — Project documentation; see this file for its authoritative topic and scope.
- `docs/TELEGRAM_INTEGRATION.md` — Project documentation; see this file for its authoritative topic and scope.
- `docs/TESTING.md` — Project documentation; see this file for its authoritative topic and scope.
- `docs/TROUBLESHOOTING.md` — Project documentation; see this file for its authoritative topic and scope.
- `docs/WINDOWS_PORTABLE_PACKAGE.md` — Project documentation; see this file for its authoritative topic and scope.
- `docs/master_result all` — Project documentation; see this file for its authoritative topic and scope.
- `docs/ops/worker-runtime.md` — Project documentation; see this file for its authoritative topic and scope.
- `infra/cloudflare-worker/README.md` — Cloudflare Worker infrastructure/configuration.
- `infra/cloudflare-worker/package.json` — Cloudflare Worker infrastructure/configuration.
- `infra/cloudflare-worker/src/index.ts` — Cloudflare Worker infrastructure/configuration.
- `infra/cloudflare-worker/wrangler.toml` — Cloudflare Worker infrastructure/configuration.
- `infra/kaggle/README.md` — Kaggle worker/runtime support files.
- `infra/kaggle/dispatch.py` — Kaggle worker/runtime support files.
- `infra/kaggle/kaggle_worker.py` — Kaggle worker/runtime support files.
- `infra/kaggle/kernel-metadata.json` — Kaggle worker/runtime support files.
- `infra/kaggle/test_dispatch.py` — Kaggle worker/runtime support files.
- `infra/managed-services.md` — Infrastructure configuration or operations runbook.
- `infra/production-runbook.md` — Infrastructure configuration or operations runbook.
- `apps/mobile/README.md` — Mobile scope documentation or implementation placeholder; verify README and contents.
- `netlify.toml` — Netlify build/deployment configuration.
- `opencode.json` — OpenCode project configuration.
- `render.worker.yaml` — Render deployment/service configuration; verify against live dashboard.
- `render.yaml` — Render deployment/service configuration; verify against live dashboard.
- `scripts/backup_db.py` — Python maintenance, test, backup/restore, or load-test script; inspect before execution.
- `scripts/phase-load-test.py` — Python maintenance, test, backup/restore, or load-test script; inspect before execution.
- `scripts/restore_db.py` — Python maintenance, test, backup/restore, or load-test script; inspect before execution.
- `scripts/windows-portable/Start-NarrativForge.ps1` — Windows portable packaging/build helper.
- `scripts/windows-portable/Stop-NarrativForge.ps1` — Windows portable packaging/build helper.
- `apps/web-platform/backend/.env.example` — Backend configuration, documentation, or support asset.
- `apps/web-platform/backend/Dockerfile` — Backend configuration, documentation, or support asset.
- `apps/web-platform/backend/Dockerfile.worker` — Backend configuration, documentation, or support asset.
- `apps/web-platform/backend/alembic.ini` — Backend configuration, documentation, or support asset.
- `apps/web-platform/backend/alembic/env.py` — Python backend source, task, test, or utility; exact role depends on module.
- `apps/web-platform/backend/alembic/script.py.mako` — Backend configuration, documentation, or support asset.
- `apps/web-platform/backend/alembic/versions/0001_bootstrap.py` — Python backend source, task, test, or utility; exact role depends on module.
- `apps/web-platform/backend/alembic/versions/0002_asset_storage_metadata.py` — Python backend source, task, test, or utility; exact role depends on module.
- `apps/web-platform/backend/alembic/versions/0003_scene_script_scope.py` — Python backend source, task, test, or utility; exact role depends on module.
- `apps/web-platform/backend/alembic/versions/0004_processing_retry_dlq.py` — Python backend source, task, test, or utility; exact role depends on module.
- `apps/web-platform/backend/alembic/versions/0005_resumable_uploads.py` — Python backend source, task, test, or utility; exact role depends on module.
- `apps/web-platform/backend/alembic/versions/0006_idempotency_keys.py` — Python backend source, task, test, or utility; exact role depends on module.
- `apps/web-platform/backend/alembic/versions/0007_optimistic_locking.py` — Python backend source, task, test, or utility; exact role depends on module.
- `apps/web-platform/backend/alembic/versions/0008_storage_replicas.py` — Python backend source, task, test, or utility; exact role depends on module.
- `apps/web-platform/backend/alembic/versions/0009_phase4_foundations.py` — Python backend source, task, test, or utility; exact role depends on module.
- `apps/web-platform/backend/alembic/versions/0010_tenant_content_scope.py` — Python backend source, task, test, or utility; exact role depends on module.
- `apps/web-platform/backend/alembic/versions/0011_webhook_secret.py` — Python backend source, task, test, or utility; exact role depends on module.
- `apps/web-platform/backend/alembic/versions/0012_stripe_webhook_events.py` — Python backend source, task, test, or utility; exact role depends on module.
- `apps/web-platform/backend/alembic/versions/0013_tenant_scope_integrations.py` — Python backend source, task, test, or utility; exact role depends on module.
- `apps/web-platform/backend/alembic/versions/0014_security_performance_hardening.py` — Python backend source, task, test, or utility; exact role depends on module.
- `apps/web-platform/backend/alembic/versions/0015_revoke_public_table_grants.py` — Python backend source, task, test, or utility; exact role depends on module.
- `apps/web-platform/backend/alembic/versions/0016_scene_constraint_repair.py` — Python backend source, task, test, or utility; exact role depends on module.
- `apps/web-platform/backend/alembic/versions/0017_asset_deleted_at.py` — Python backend source, task, test, or utility; exact role depends on module.
- `apps/web-platform/backend/alembic/versions/0017_release_maturity.py` — Python backend source, task, test, or utility; exact role depends on module.
- `apps/web-platform/backend/alembic/versions/0018_tenant_backfill_guard.py` — Python backend source, task, test, or utility; exact role depends on module.
- `apps/web-platform/backend/alembic/versions/0019_series_bible.py` — Python backend source, task, test, or utility; exact role depends on module.
- `apps/web-platform/backend/app/__init__.py` — Python backend source, task, test, or utility; exact role depends on module.
- `apps/web-platform/backend/app/api/__init__.py` — Python backend source, task, test, or utility; exact role depends on module.
- `apps/web-platform/backend/app/api/dependencies.py` — Python backend source, task, test, or utility; exact role depends on module.
- `apps/web-platform/backend/app/api/router.py` — Python backend source, task, test, or utility; exact role depends on module.
- `apps/web-platform/backend/app/api/routes/__init__.py` — Python backend source, task, test, or utility; exact role depends on module.
- `apps/web-platform/backend/app/api/routes/assets.py` — Python backend source, task, test, or utility; exact role depends on module.
- `apps/web-platform/backend/app/api/routes/audit.py` — Python backend source, task, test, or utility; exact role depends on module.
- `apps/web-platform/backend/app/api/routes/auth.py` — Python backend source, task, test, or utility; exact role depends on module.
- `apps/web-platform/backend/app/api/routes/auto_mode.py` — Python backend source, task, test, or utility; exact role depends on module.
- `apps/web-platform/backend/app/api/routes/cloud_processing.py` — Python backend source, task, test, or utility; exact role depends on module.
- `apps/web-platform/backend/app/api/routes/episodes.py` — Python backend source, task, test, or utility; exact role depends on module.
- `apps/web-platform/backend/app/api/routes/export.py` — Python backend source, task, test, or utility; exact role depends on module.
- `apps/web-platform/backend/app/api/routes/google_drive.py` — Python backend source, task, test, or utility; exact role depends on module.
- `apps/web-platform/backend/app/api/routes/health.py` — Python backend source, task, test, or utility; exact role depends on module.
- `apps/web-platform/backend/app/api/routes/hooks.py` — Python backend source, task, test, or utility; exact role depends on module.
- `apps/web-platform/backend/app/api/routes/ideas.py` — Python backend source, task, test, or utility; exact role depends on module.
- `apps/web-platform/backend/app/api/routes/jobs.py` — Python backend source, task, test, or utility; exact role depends on module.
- `apps/web-platform/backend/app/api/routes/phase4.py` — Python backend source, task, test, or utility; exact role depends on module.
- `apps/web-platform/backend/app/api/routes/production_intelligence.py` — Python backend source, task, test, or utility; exact role depends on module.
- `apps/web-platform/backend/app/api/routes/production_pipeline.py` — Python backend source, task, test, or utility; exact role depends on module.
- `apps/web-platform/backend/app/api/routes/review.py` — Python backend source, task, test, or utility; exact role depends on module.
- `apps/web-platform/backend/app/api/routes/scenes.py` — Python backend source, task, test, or utility; exact role depends on module.
- `apps/web-platform/backend/app/api/routes/scripts.py` — Python backend source, task, test, or utility; exact role depends on module.
- `apps/web-platform/backend/app/api/routes/search.py` — Python backend source, task, test, or utility; exact role depends on module.
- `apps/web-platform/backend/app/api/routes/series.py` — Python backend source, task, test, or utility; exact role depends on module.
- `apps/web-platform/backend/app/api/routes/subtitles.py` — Python backend source, task, test, or utility; exact role depends on module.
- `apps/web-platform/backend/app/api/routes/telegram.py` — Python backend source, task, test, or utility; exact role depends on module.
- `apps/web-platform/backend/app/api/routes/uploads.py` — Python backend source, task, test, or utility; exact role depends on module.
- `apps/web-platform/backend/app/core/__init__.py` — Python backend source, task, test, or utility; exact role depends on module.
- `apps/web-platform/backend/app/core/config.py` — Python backend source, task, test, or utility; exact role depends on module.
- `apps/web-platform/backend/app/db.py` — Python backend source, task, test, or utility; exact role depends on module.
- `apps/web-platform/backend/app/infrastructure/__init__.py` — Python backend source, task, test, or utility; exact role depends on module.
- `apps/web-platform/backend/app/infrastructure/redis.py` — Python backend source, task, test, or utility; exact role depends on module.
- `apps/web-platform/backend/app/main.py` — Python backend source, task, test, or utility; exact role depends on module.
- `apps/web-platform/backend/app/metrics.py` — Python backend source, task, test, or utility; exact role depends on module.
- `apps/web-platform/backend/app/middleware/__init__.py` — Python backend source, task, test, or utility; exact role depends on module.
- `apps/web-platform/backend/app/middleware/idempotency.py` — Python backend source, task, test, or utility; exact role depends on module.
- `apps/web-platform/backend/app/models/__init__.py` — Python backend source, task, test, or utility; exact role depends on module.
- `apps/web-platform/backend/app/models/core.py` — Python backend source, task, test, or utility; exact role depends on module.
- `apps/web-platform/backend/app/models/phase4.py` — Python backend source, task, test, or utility; exact role depends on module.
- `apps/web-platform/backend/app/observability.py` — Python backend source, task, test, or utility; exact role depends on module.
- `apps/web-platform/backend/app/services/__init__.py` — Python backend source, task, test, or utility; exact role depends on module.
- `apps/web-platform/backend/app/services/ai_adapter.py` — Python backend source, task, test, or utility; exact role depends on module.
- `apps/web-platform/backend/app/services/ai_usage_tracker.py` — Python backend source, task, test, or utility; exact role depends on module.
- `apps/web-platform/backend/app/services/asset_gc.py` — Python backend source, task, test, or utility; exact role depends on module.
- `apps/web-platform/backend/app/services/audit.py` — Python backend source, task, test, or utility; exact role depends on module.
- `apps/web-platform/backend/app/services/auto_mode.py` — Python backend source, task, test, or utility; exact role depends on module.
- `apps/web-platform/backend/app/services/batch_generator.py` — Python backend source, task, test, or utility; exact role depends on module.
- `apps/web-platform/backend/app/services/code_completion.py` — Python backend source, task, test, or utility; exact role depends on module.
- `apps/web-platform/backend/app/services/content_quality.py` — Python backend source, task, test, or utility; exact role depends on module.
- `apps/web-platform/backend/app/services/email.py` — Python backend source, task, test, or utility; exact role depends on module.
- `apps/web-platform/backend/app/services/expanded_production.py` — Python backend source, task, test, or utility; exact role depends on module.
- `apps/web-platform/backend/app/services/future_foundations.py` — Python backend source, task, test, or utility; exact role depends on module.
- `apps/web-platform/backend/app/services/hook_engineering.py` — Python backend source, task, test, or utility; exact role depends on module.
- `apps/web-platform/backend/app/services/operating_maturity.py` — Python backend source, task, test, or utility; exact role depends on module.
- `apps/web-platform/backend/app/services/orchestration.py` — Python backend source, task, test, or utility; exact role depends on module.
- `apps/web-platform/backend/app/services/passwords.py` — Python backend source, task, test, or utility; exact role depends on module.
- `apps/web-platform/backend/app/services/phase_52_60.py` — Python backend source, task, test, or utility; exact role depends on module.
- `apps/web-platform/backend/app/services/phase_61_68.py` — Python backend source, task, test, or utility; exact role depends on module.
- `apps/web-platform/backend/app/services/phase_69_76.py` — Python backend source, task, test, or utility; exact role depends on module.
- `apps/web-platform/backend/app/services/phase_77_84.py` — Python backend source, task, test, or utility; exact role depends on module.
- `apps/web-platform/backend/app/services/phase_continuation.py` — Python backend source, task, test, or utility; exact role depends on module.
- `apps/web-platform/backend/app/services/processing.py` — Python backend source, task, test, or utility; exact role depends on module.
- `apps/web-platform/backend/app/services/production_pipeline.py` — Python backend source, task, test, or utility; exact role depends on module.
- `apps/web-platform/backend/app/services/production_scale.py` — Python backend source, task, test, or utility; exact role depends on module.
- `apps/web-platform/backend/app/services/provider_fallback.py` — Python backend source, task, test, or utility; exact role depends on module.
- `apps/web-platform/backend/app/services/provider_quota.py` — Python backend source, task, test, or utility; exact role depends on module.
- `apps/web-platform/backend/app/services/provider_registry.py` — Python backend source, task, test, or utility; exact role depends on module.
- `apps/web-platform/backend/app/services/rag_embeddings.py` — Python backend source, task, test, or utility; exact role depends on module.
- `apps/web-platform/backend/app/services/real_processing.py` — Python backend source, task, test, or utility; exact role depends on module.
- `apps/web-platform/backend/app/services/release_maturity.py` — Python backend source, task, test, or utility; exact role depends on module.
- `apps/web-platform/backend/app/services/release_maturity_store.py` — Python backend source, task, test, or utility; exact role depends on module.
- `apps/web-platform/backend/app/services/selective_regeneration.py` — Python backend source, task, test, or utility; exact role depends on module.
- `apps/web-platform/backend/app/services/series_continuity.py` — Python backend source, task, test, or utility; exact role depends on module.
- `apps/web-platform/backend/app/services/storage.py` — Python backend source, task, test, or utility; exact role depends on module.
- `apps/web-platform/backend/app/services/storage_lifecycle.py` — Python backend source, task, test, or utility; exact role depends on module.
- `apps/web-platform/backend/app/services/subtitles.py` — Python backend source, task, test, or utility; exact role depends on module.
- `apps/web-platform/backend/app/services/telegram.py` — Python backend source, task, test, or utility; exact role depends on module.
- `apps/web-platform/backend/app/services/thumbnail_candidate.py` — Python backend source, task, test, or utility; exact role depends on module.
- `apps/web-platform/backend/app/workers/__init__.py` — Python backend source, task, test, or utility; exact role depends on module.
- `apps/web-platform/backend/app/workers/celery_app.py` — Python backend source, task, test, or utility; exact role depends on module.
- `apps/web-platform/backend/app/workers/concurrency.py` — Python backend source, task, test, or utility; exact role depends on module.
- `apps/web-platform/backend/app/workers/kaggle_job_runner.py` — Python backend source, task, test, or utility; exact role depends on module.
- `apps/web-platform/backend/app/workers/mock_worker.py` — Python backend source, task, test, or utility; exact role depends on module.
- `apps/web-platform/backend/app/workers/real_worker.py` — Python backend source, task, test, or utility; exact role depends on module.
- `apps/web-platform/backend/app/workers/tasks.py` — Python backend source, task, test, or utility; exact role depends on module.
- `apps/web-platform/backend/pytest.ini` — Backend configuration, documentation, or support asset.
- `apps/web-platform/backend/requirements-real-processing.txt` — Backend configuration, documentation, or support asset.
- `apps/web-platform/backend/requirements.txt` — Backend configuration, documentation, or support asset.
- `apps/web-platform/backend/scripts/__init__.py` — Python backend source, task, test, or utility; exact role depends on module.
- `apps/web-platform/backend/scripts/backup_db.py` — Python backend source, task, test, or utility; exact role depends on module.
- `apps/web-platform/backend/scripts/bootstrap_admin.py` — Python backend source, task, test, or utility; exact role depends on module.
- `apps/web-platform/backend/scripts/final_production_gate.py` — Python backend source, task, test, or utility; exact role depends on module.
- `apps/web-platform/backend/scripts/free_provider_smoke.py` — Python backend source, task, test, or utility; exact role depends on module.
- `apps/web-platform/backend/scripts/kaggle_worker.py` — Python backend source, task, test, or utility; exact role depends on module.
- `apps/web-platform/backend/scripts/local_media_preflight.py` — Python backend source, task, test, or utility; exact role depends on module.
- `apps/web-platform/backend/scripts/openrouter_free_model_smoke.py` — Python backend source, task, test, or utility; exact role depends on module.
- `apps/web-platform/backend/scripts/production_smoke.py` — Python backend source, task, test, or utility; exact role depends on module.
- `apps/web-platform/backend/scripts/restore_db.py` — Python backend source, task, test, or utility; exact role depends on module.
- `apps/web-platform/backend/scripts/seed_e2e_tenant.py` — Python backend source, task, test, or utility; exact role depends on module.
- `apps/web-platform/backend/scripts/verify_postgres_backup.py` — Python backend source, task, test, or utility; exact role depends on module.
- `apps/web-platform/backend/scripts/worker_smoke.py` — Python backend source, task, test, or utility; exact role depends on module.
- `apps/web-platform/backend/tests/client_utils.py` — Python backend source, task, test, or utility; exact role depends on module.
- `apps/web-platform/backend/tests/conftest.py` — Python backend source, task, test, or utility; exact role depends on module.
- `apps/web-platform/backend/tests/test_ai_adapter.py` — Python backend source, task, test, or utility; exact role depends on module.
- `apps/web-platform/backend/tests/test_asset_gc.py` — Python backend source, task, test, or utility; exact role depends on module.
- `apps/web-platform/backend/tests/test_batch_generator.py` — Python backend source, task, test, or utility; exact role depends on module.
- `apps/web-platform/backend/tests/test_checksum_dedupe.py` — Python backend source, task, test, or utility; exact role depends on module.
- `apps/web-platform/backend/tests/test_cloud_processing_security.py` — Python backend source, task, test, or utility; exact role depends on module.
- `apps/web-platform/backend/tests/test_code_completion.py` — Python backend source, task, test, or utility; exact role depends on module.
- `apps/web-platform/backend/tests/test_content_quality.py` — Python backend source, task, test, or utility; exact role depends on module.
- `apps/web-platform/backend/tests/test_database_config.py` — Python backend source, task, test, or utility; exact role depends on module.
- `apps/web-platform/backend/tests/test_expanded_production.py` — Python backend source, task, test, or utility; exact role depends on module.
- `apps/web-platform/backend/tests/test_foundation.py` — Python backend source, task, test, or utility; exact role depends on module.
- `apps/web-platform/backend/tests/test_free_provider_smoke.py` — Python backend source, task, test, or utility; exact role depends on module.
- `apps/web-platform/backend/tests/test_health_and_search.py` — Python backend source, task, test, or utility; exact role depends on module.
- `apps/web-platform/backend/tests/test_hybrid_storage.py` — Python backend source, task, test, or utility; exact role depends on module.
- `apps/web-platform/backend/tests/test_idempotency_postgres.py` — Python backend source, task, test, or utility; exact role depends on module.
- `apps/web-platform/backend/tests/test_infrastructure_integration.py` — Python backend source, task, test, or utility; exact role depends on module.
- `apps/web-platform/backend/tests/test_local_media_preflight.py` — Python backend source, task, test, or utility; exact role depends on module.
- `apps/web-platform/backend/tests/test_magic_link.py` — Python backend source, task, test, or utility; exact role depends on module.
- `apps/web-platform/backend/tests/test_metrics.py` — Python backend source, task, test, or utility; exact role depends on module.
- `apps/web-platform/backend/tests/test_migrations.py` — Python backend source, task, test, or utility; exact role depends on module.
- `apps/web-platform/backend/tests/test_observability.py` — Python backend source, task, test, or utility; exact role depends on module.
- `apps/web-platform/backend/tests/test_openrouter_free_model_smoke.py` — Python backend source, task, test, or utility; exact role depends on module.
- `apps/web-platform/backend/tests/test_operating_maturity.py` — Python backend source, task, test, or utility; exact role depends on module.
- `apps/web-platform/backend/tests/test_optimistic_locking.py` — Python backend source, task, test, or utility; exact role depends on module.
- `apps/web-platform/backend/tests/test_orchestration.py` — Python backend source, task, test, or utility; exact role depends on module.
- `apps/web-platform/backend/tests/test_orm_relationships.py` — Python backend source, task, test, or utility; exact role depends on module.
- `apps/web-platform/backend/tests/test_passwords.py` — Python backend source, task, test, or utility; exact role depends on module.
- `apps/web-platform/backend/tests/test_phase0_security.py` — Python backend source, task, test, or utility; exact role depends on module.
- `apps/web-platform/backend/tests/test_phase4_membership.py` — Python backend source, task, test, or utility; exact role depends on module.
- `apps/web-platform/backend/tests/test_phase_52_60.py` — Python backend source, task, test, or utility; exact role depends on module.
- `apps/web-platform/backend/tests/test_phase_61_68.py` — Python backend source, task, test, or utility; exact role depends on module.
- `apps/web-platform/backend/tests/test_phase_69_76.py` — Python backend source, task, test, or utility; exact role depends on module.
- `apps/web-platform/backend/tests/test_phase_77_84.py` — Python backend source, task, test, or utility; exact role depends on module.
- `apps/web-platform/backend/tests/test_phase_continuation.py` — Python backend source, task, test, or utility; exact role depends on module.
- `apps/web-platform/backend/tests/test_production_foundations.py` — Python backend source, task, test, or utility; exact role depends on module.
- `apps/web-platform/backend/tests/test_production_intelligence.py` — Python backend source, task, test, or utility; exact role depends on module.
- `apps/web-platform/backend/tests/test_production_pipeline.py` — Python backend source, task, test, or utility; exact role depends on module.
- `apps/web-platform/backend/tests/test_production_scale.py` — Python backend source, task, test, or utility; exact role depends on module.
- `apps/web-platform/backend/tests/test_provider_quota.py` — Python backend source, task, test, or utility; exact role depends on module.
- `apps/web-platform/backend/tests/test_provider_registry.py` — Python backend source, task, test, or utility; exact role depends on module.
- `apps/web-platform/backend/tests/test_rag_embeddings.py` — Python backend source, task, test, or utility; exact role depends on module.
- `apps/web-platform/backend/tests/test_real_processing_subprocess.py` — Python backend source, task, test, or utility; exact role depends on module.
- `apps/web-platform/backend/tests/test_redis_config.py` — Python backend source, task, test, or utility; exact role depends on module.
- `apps/web-platform/backend/tests/test_release_maturity.py` — Python backend source, task, test, or utility; exact role depends on module.
- `apps/web-platform/backend/tests/test_release_maturity_store.py` — Python backend source, task, test, or utility; exact role depends on module.
- `apps/web-platform/backend/tests/test_resumable_uploads.py` — Python backend source, task, test, or utility; exact role depends on module.
- `apps/web-platform/backend/tests/test_root_restore_db.py` — Python backend source, task, test, or utility; exact role depends on module.
- `apps/web-platform/backend/tests/test_script_scene_api_security.py` — Python backend source, task, test, or utility; exact role depends on module.
- `apps/web-platform/backend/tests/test_security_config.py` — Python backend source, task, test, or utility; exact role depends on module.
- `apps/web-platform/backend/tests/test_security_hardening.py` — Python backend source, task, test, or utility; exact role depends on module.
- `apps/web-platform/backend/tests/test_security_observability.py` — Python backend source, task, test, or utility; exact role depends on module.
- `apps/web-platform/backend/tests/test_selective_regeneration.py` — Python backend source, task, test, or utility; exact role depends on module.
- `apps/web-platform/backend/tests/test_series_bible.py` — Python backend source, task, test, or utility; exact role depends on module.
- `apps/web-platform/backend/tests/test_series_continuity.py` — Python backend source, task, test, or utility; exact role depends on module.
- `apps/web-platform/backend/tests/test_storage_lifecycle.py` — Python backend source, task, test, or utility; exact role depends on module.
- `apps/web-platform/backend/tests/test_storage_provider.py` — Python backend source, task, test, or utility; exact role depends on module.
- `apps/web-platform/backend/tests/test_storage_routing.py` — Python backend source, task, test, or utility; exact role depends on module.
- `apps/web-platform/backend/tests/test_subtitle_api_security.py` — Python backend source, task, test, or utility; exact role depends on module.
- `apps/web-platform/backend/tests/test_subtitle_normalization.py` — Python backend source, task, test, or utility; exact role depends on module.
- `apps/web-platform/backend/tests/test_supabase_auth.py` — Python backend source, task, test, or utility; exact role depends on module.
- `apps/web-platform/backend/tests/test_tasks_celery.py` — Python backend source, task, test, or utility; exact role depends on module.
- `apps/web-platform/backend/tests/test_tenant_isolation.py` — Python backend source, task, test, or utility; exact role depends on module.
- `apps/web-platform/backend/tests/test_thumbnail_candidate.py` — Python backend source, task, test, or utility; exact role depends on module.
- `apps/web-platform/backend/tests/test_whisper_fallback.py` — Python backend source, task, test, or utility; exact role depends on module.
- `apps/web-platform/backend/tests/test_worker_concurrency.py` — Python backend source, task, test, or utility; exact role depends on module.
- `apps/web-platform/cloudflare/whisper-worker/README.md` — Cloudflare Worker/edge integration or configuration; verify bindings and deployment settings.
- `apps/web-platform/cloudflare/whisper-worker/src/index.ts` — Cloudflare Worker/edge integration or configuration; verify bindings and deployment settings.
- `apps/web-platform/cloudflare/whisper-worker/test/worker.test.mjs` — Cloudflare Worker/edge integration or configuration; verify bindings and deployment settings.
- `apps/web-platform/cloudflare/whisper-worker/wrangler.jsonc` — Cloudflare Worker/edge integration or configuration; verify bindings and deployment settings.
- `apps/web-platform/docs/architecture.md` — Web-platform-specific documentation.
- `apps/web-platform/docs/foundation-checklist.md` — Web-platform-specific documentation.
- `apps/web-platform/docs/runbooks/restore.md` — Web-platform-specific documentation.
- `apps/web-platform/docs/runbooks/rotate_secrets.md` — Web-platform-specific documentation.
- `apps/web-platform/docs/runbooks/stuck_job.md` — Web-platform-specific documentation.
- `apps/web-platform/frontend/.env.example` — Frontend app support file; inspect source for exact responsibility.
- `apps/web-platform/frontend/app/[...module]/page.tsx` — Next.js App Router page or route UI; verify actual behavior in source.
- `apps/web-platform/frontend/app/analytics/page.tsx` — Next.js App Router page or route UI; verify actual behavior in source.
- `apps/web-platform/frontend/app/auth/magic-link/page.tsx` — Next.js App Router page or route UI; verify actual behavior in source.
- `apps/web-platform/frontend/app/auto-mode/page.tsx` — Next.js App Router page or route UI; verify actual behavior in source.
- `apps/web-platform/frontend/app/dashboard/page.tsx` — Next.js App Router page or route UI; verify actual behavior in source.
- `apps/web-platform/frontend/app/episodes/[id]/assets/page.tsx` — Next.js App Router page or route UI; verify actual behavior in source.
- `apps/web-platform/frontend/app/episodes/[id]/export/page.tsx` — Next.js App Router page or route UI; verify actual behavior in source.
- `apps/web-platform/frontend/app/episodes/[id]/page.tsx` — Next.js App Router page or route UI; verify actual behavior in source.
- `apps/web-platform/frontend/app/episodes/[id]/review/page.tsx` — Next.js App Router page or route UI; verify actual behavior in source.
- `apps/web-platform/frontend/app/episodes/[id]/scenes/page.tsx` — Next.js App Router page or route UI; verify actual behavior in source.
- `apps/web-platform/frontend/app/episodes/[id]/script/page.tsx` — Next.js App Router page or route UI; verify actual behavior in source.
- `apps/web-platform/frontend/app/episodes/[id]/subtitle/page.tsx` — Next.js App Router page or route UI; verify actual behavior in source.
- `apps/web-platform/frontend/app/episodes/page.tsx` — Next.js App Router page or route UI; verify actual behavior in source.
- `apps/web-platform/frontend/app/globals.css` — Frontend route asset/source.
- `apps/web-platform/frontend/app/hooks/page.tsx` — Next.js App Router page or route UI; verify actual behavior in source.
- `apps/web-platform/frontend/app/ideas/page.tsx` — Next.js App Router page or route UI; verify actual behavior in source.
- `apps/web-platform/frontend/app/invite/page.tsx` — Next.js App Router page or route UI; verify actual behavior in source.
- `apps/web-platform/frontend/app/layout.tsx` — Next.js App Router page or route UI; verify actual behavior in source.
- `apps/web-platform/frontend/app/login/page.tsx` — Next.js App Router page or route UI; verify actual behavior in source.
- `apps/web-platform/frontend/app/manual-log/page.tsx` — Next.js App Router page or route UI; verify actual behavior in source.
- `apps/web-platform/frontend/app/page.tsx` — Next.js App Router page or route UI; verify actual behavior in source.
- `apps/web-platform/frontend/app/processing/page.tsx` — Next.js App Router page or route UI; verify actual behavior in source.
- `apps/web-platform/frontend/app/production-intelligence/page.tsx` — Next.js App Router page or route UI; verify actual behavior in source.
- `apps/web-platform/frontend/app/publishing-prep/page.tsx` — Next.js App Router page or route UI; verify actual behavior in source.
- `apps/web-platform/frontend/app/series/[id]/page.tsx` — Next.js App Router page or route UI; verify actual behavior in source.
- `apps/web-platform/frontend/app/series/page.tsx` — Next.js App Router page or route UI; verify actual behavior in source.
- `apps/web-platform/frontend/app/usage/page.tsx` — Next.js App Router page or route UI; verify actual behavior in source.
- `apps/web-platform/frontend/components/app-shell.tsx` — Reusable frontend UI component.
- `apps/web-platform/frontend/components/auth-guard.tsx` — Reusable frontend UI component.
- `apps/web-platform/frontend/components/domain-forms.tsx` — Reusable frontend UI component.
- `apps/web-platform/frontend/components/toast.tsx` — Reusable frontend UI component.
- `apps/web-platform/frontend/components/ui-primitives.tsx` — Reusable frontend UI component.
- `apps/web-platform/frontend/e2e/cross-tenant-isolation.spec.ts` — Playwright end-to-end test.
- `apps/web-platform/frontend/e2e/phase4-foundation.spec.ts` — Playwright end-to-end test.
- `apps/web-platform/frontend/e2e/production-flow.spec.ts` — Playwright end-to-end test.
- `apps/web-platform/frontend/e2e/series-bible-persistence.spec.ts` — Playwright end-to-end test.
- `apps/web-platform/frontend/lib/api.ts` — Frontend library/API/state helper.
- `apps/web-platform/frontend/lib/cloud-whisper.ts` — Frontend library/API/state helper.
- `apps/web-platform/frontend/lib/workflow-states.ts` — Frontend library/API/state helper.
- `apps/web-platform/frontend/next-env.d.ts` — Frontend TypeScript configuration/source.
- `apps/web-platform/frontend/next.config.ts` — Frontend TypeScript configuration/source.
- `apps/web-platform/frontend/package-lock.json` — Frontend package/configuration or lockfile.
- `apps/web-platform/frontend/package.json` — Frontend package/configuration or lockfile.
- `apps/web-platform/frontend/playwright.config.ts` — Frontend TypeScript configuration/source.
- `apps/web-platform/frontend/tsconfig.json` — Frontend package/configuration or lockfile.

## Accuracy, limitations and maintenance

1. **Snapshot-bound:** this map represents Git tree `bb6cc426d47661d6353bc38dcfaf1e6185a78b59` on `main`. It will become stale when paths change.
2. **Tracked-only:** untracked/ignored files and generated artifacts are not visible in a Git tree listing.
3. **No secret values:** environment variable values and secret contents must never be copied into this document. Document variable *names* only when confirmed from source/configuration and safe to disclose.
4. **Configuration versus reality:** checked-in Render/Netlify/Cloudflare settings may differ from live provider settings.
5. **Names are not proof:** an item described as a backup, migration, test or worker must be checked for implementation, invocation and current use before relying on it.
6. **Archived content:** `archive/legacy/` is historical unless the active code explicitly references it.
7. **Recommended refresh:** regenerate the tree and review this document whenever a directory is added/removed, a subsystem is reorganized, or a major deployment/runtime change is merged.

## Rebuild the tree locally

From the repository root, use a tracked-file listing so the output reflects Git rather than arbitrary build artifacts:

```bash
git ls-tree -r --name-only HEAD
```

For a directory-oriented tree (if `tree` is installed):

```bash
tree -a -I '.git|node_modules|.next|__pycache__|.venv|dist|build'
```

The second command may include untracked/generated local files and therefore will not necessarily match the tracked snapshot above.
