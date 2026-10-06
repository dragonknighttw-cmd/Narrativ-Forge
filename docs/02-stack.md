[object Object]

## Worker hosting strategy

The project is **free-first** for runtime compute.

### Current free plan
- Render remains the FastAPI web/API host.
- Upstash Redis remains the shared Celery broker.
- One or two Windows PCs may run the repository's existing Celery worker.
- FFmpeg runs on the worker machine.
- Cloudflare Whisper remains the default transcription integration.
- No Docker or WSL is required.

### Future paid plan
If local compute becomes the bottleneck, the worker can move to a paid Render Background Worker, paid VPS, or another verified always-on host.

The paid host must run the same repository worker contract. Do not redesign the application merely to change worker hosts.

Detailed plan: `docs/10-runtime-and-storage-lifecycle-plan.md`.

## Storage lifecycle strategy

- Local disk: short-lived working/temp data.
- B2: raw/intermediate media with retention.
- Supabase: small workflow files such as subtitles/manifests.
- Cloudinary: images/previews with retention.
- Google Drive: approved final outputs.
- Neon: workflow/database source of truth.

Cleanup must be reference-safe. Approved final output and required metadata are not disposable cleanup targets.

Detailed retention, thresholds, cleanup order, and paid-storage migration are defined in `docs/10-runtime-and-storage-lifecycle-plan.md`.
