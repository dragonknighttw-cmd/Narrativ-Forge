# Documentation Migration Provenance — 2026-10-08

The legacy Markdown sources below were reconciled into the canonical documentation set. Their unique requirements are preserved in the named destinations; the old paths are not maintained as competing authorities.

- docs/README.md → TOOL.md + canonical README/document map.
- docs/ops/worker-runtime.md → docs/OPERATIONS.md + docs/DEPLOYMENT.md.
- infra/cloudflare-worker/README.md → docs/DEPLOYMENT.md + docs/OPERATIONS.md.
- infra/kaggle/README.md → docs/DEPLOYMENT.md + docs/OPERATIONS.md.
- infra/managed-services.md → docs/DATABASE.md + docs/DEPLOYMENT.md + docs/OPERATIONS.md.
- infra/production-runbook.md → docs/OPERATIONS.md + docs/TROUBLESHOOTING.md.
- web-platform/cloudflare/whisper-worker/README.md → docs/AI_RAG.md + docs/DEPLOYMENT.md + docs/OPERATIONS.md.
- web-platform/docs/architecture.md → docs/ARCHITECTURE.md + docs/STORAGE.md + docs/AI_RAG.md.
- web-platform/docs/foundation-checklist.md → docs/ROADMAP.md + docs/TESTING.md.
- web-platform/docs/runbooks/restore.md → docs/OPERATIONS.md + docs/TROUBLESHOOTING.md.
- web-platform/docs/runbooks/rotate_secrets.md → SECURITY.md + docs/OPERATIONS.md.
- web-platform/docs/runbooks/stuck_job.md → docs/OPERATIONS.md + docs/TROUBLESHOOTING.md.
- mobile/README.md → archive/legacy/mobile-scope.md.

The migration rule is preservation of knowledge, not preservation of duplicate filenames.
