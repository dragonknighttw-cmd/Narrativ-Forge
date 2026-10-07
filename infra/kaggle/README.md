# Narrativ Forge — Kaggle Ephemeral Worker

Kaggle is an ephemeral execution backend, not a 24/7 Celery worker.

Architecture:
Render API / Neon DB / Upstash Redis -> queued ProcessingJob -> Kaggle kernel session -> atomic DB claim -> FFmpeg + Whisper + storage -> completed/failed job.

Kaggle CPU/GPU notebook sessions currently support up to 12 hours, and the Kaggle Public API/CLI supports pushing and running kernels programmatically.

First-time setup:
1. Create a private Kaggle Script named Narrativ Forge Worker.
2. Add Kaggle Secrets under Add-ons -> Secrets. Kaggle documents UserSecretsClient for reading notebook secrets.
3. Add GITHUB_TOKEN with read access to the private repository, DATABASE_URL, STORAGE_PROVIDER and the selected storage credentials, Cloudflare Whisper settings, and FFmpeg/Whisper settings as needed.
4. Copy web-platform/backend/scripts/kaggle_worker.py into the Kaggle kernel.
5. Run it manually once with a queued test job.
6. Only after the manual run succeeds, automate kernel pushes with the Kaggle CLI.

Safety:
- Keep the Kaggle kernel private.
- Never put production secrets in kernel-metadata.json.
- PostgreSQL remains the source of truth.
- A session ending is not success; recovery/lease handling must be verified before production use.
- Local Windows worker remains the fallback.

Production gate:
queued -> Kaggle session -> atomic claim -> FFmpeg -> storage -> DB completion -> retry/DLQ -> recovery
must pass with a real media job before Kaggle is marked production-ready.
