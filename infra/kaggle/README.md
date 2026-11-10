# Kaggle ephemeral worker

The Kaggle kernel is an opt-in, one-job worker. It is not a continuously available production worker.

## Dispatch controls

- Scheduled dispatch runs hourly and requires the repository Actions variable ENABLE_KAGGLE_DISPATCH=true.
- Manual dispatch requires confirm_kaggle_dispatch=true.
- The dispatcher checks for a due real_processing job and an inactive kernel before pushing.
- It injects the exact triggering GitHub SHA into kaggle_worker.py; the kernel verifies that exact checkout before running.
- No paid Render worker is provisioned by this workflow.

## GitHub Actions configuration

- Variable: KAGGLE_KERNEL_ID (owner/kernel-slug format; repository docs currently use thuwon/narrativ-forge as the proposed ID).
- Secret: KAGGLE_DISPATCH_DATABASE_URL (prefer a least-privilege database role that can only inspect due processing jobs).
- Secret: KAGGLE_API_TOKEN.
- Variable: ENABLE_KAGGLE_DISPATCH (leave unset/false until the owner explicitly enables unattended dispatch).

## Kaggle kernel Secrets

- Required: DATABASE_URL for the worker's database operations.
- Required: STORAGE_PROVIDER set to cloudinary, b2, or hybrid; the bootstrap fails closed if durable storage is not configured.
- Cloudinary requires CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, and CLOUDINARY_API_SECRET.
- B2 requires B2_APPLICATION_KEY_ID, B2_APPLICATION_KEY, B2_BUCKET_NAME, and B2_REGION.
- Hybrid requires both Cloudinary and B2 credentials plus SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY, and SUPABASE_STORAGE_BUCKET.
- Optional/feature-dependent: REDIS_URL, storage replica settings, Cloudflare Whisper URL/shared secret, and FFmpeg/Whisper overrides.
- The repository is public; the bootstrap does not require a GitHub token.

Never print secret values. A successful dispatcher run or kernel push does not prove media processing completed. Verify the processing job state, worker outcome, and persisted output asset independently.
