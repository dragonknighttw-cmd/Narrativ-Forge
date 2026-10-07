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


## Dual-PC Windows worker profile

The free-first local fallback is now explicitly a **dual-PC setup**:

| Machine | Role | Queue | Beat | Default heavy media |
|---|---|---|---|---|
| Home PC, ~16 GB | Primary heavy worker | `heavy_queue` | Yes | FFmpeg; Cloudflare Whisper by default; local Whisper optional |
| Office PC, 4–8 GB | Reserve light worker | `light_queue` | No | HTTP/API/DB/export/cleanup tasks |

Both use the same repository worker implementation and Upstash Redis TLS broker. Queue ownership is deliberate: the reserve office machine must not accidentally receive heavy Whisper/video jobs merely because the home machine is offline.

The proposed standalone `worker/` folders and `.bat` launchers are local deployment wrappers, not a second application. The repository's canonical requirements and Celery configuration remain authoritative.

The previously stated ~200 MB local-space constraint is incompatible with installing PyTorch + openai-whisper + the `small` model. Therefore local Whisper is optional on Home; Cloudflare Whisper remains the default and Office does not install local Whisper.

See `docs/10-runtime-and-storage-lifecycle-plan.md` §17 for the authoritative dual-PC runtime contract.
