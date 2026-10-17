# Production Environment Checklist

Last reviewed: 2026-10-17 UTC. This checklist is based on the repository configuration and the infrastructure audit. It is not proof that production is healthy.

## Release gate: do these before deploying

- [ ] Run CI, security, CodeQL, and repository-gate workflows against the exact commit intended for release.
- [ ] Confirm the canonical frontend host. The current infrastructure audit did not verify that the connected Netlify project belongs to Narrativ Forge.
- [ ] Confirm the production PostgreSQL target and compare its live Alembic revision with the repository. Two Supabase projects were found; do not guess which is canonical.
- [ ] Confirm managed Redis is configured if queue/background processing is expected. Do not use `redis://127.0.0.1:6379/0` for a separate service.
- [ ] Confirm the API and frontend are deployed from the intended commit. The 2026-10-15 audit observed Render services behind repository main, with auto-deploy disabled.
- [ ] Verify the authenticated Cloudflare Whisper request contract and Worker route/secret configuration.
- [ ] Do not call the system production-ready until upload, authentication, AI, database, and background processing have passed end-to-end checks.

## Render — API service

The checked-in `render.yaml` is the source for defaults. Set the following in the Render dashboard; values marked external must come from the actual provider/domain.

| Variable | Required value / action |
|---|---|
| `APP_ENV` | `production` |
| `DATABASE_URL` | External: confirmed production PostgreSQL URL |
| `REDIS_URL` | External: managed Redis URL, if Redis-backed features are enabled |
| `SESSION_SECRET` | Generate a unique, high-entropy secret; never commit it |
| `SESSION_COOKIE_SECURE` | `true` |
| `CORS_ORIGINS` | Exact canonical frontend origin(s), not example domains |
| `TRUSTED_HOSTS` | Actual API host(s); remove localhost from production unless deliberately required |
| `FRONTEND_BASE_URL` | Exact canonical frontend URL |
| `SENTRY_DSN` | Optional; set only if Sentry is configured |
| `STORAGE_PROVIDER` | Keep aligned with the selected storage implementation; current blueprint says `hybrid` |
| `UPLOAD_DIR` | Blueprint uses `/var/lib/narrativ-forge/uploads`; ensure persistent disk is attached if local files must survive restarts |
| `SUPABASE_URL` | External: URL for the confirmed canonical project |
| `SUPABASE_ANON_KEY` | External: public anon key |
| `SUPABASE_SERVICE_ROLE_KEY` | External secret; never expose to frontend |
| `SUPABASE_OWNER_USER_ID` / `SUPABASE_OWNER_EMAIL` | Real owner identity, not dummy placeholders |
| `SUPABASE_STORAGE_BUCKET` | Confirm the bucket exists; blueprint default is `narrativ-forge` |
| `CLOUDINARY_CLOUD_NAME` / `CLOUDINARY_API_KEY` / `CLOUDINARY_API_SECRET` | Required only if Cloudinary is part of the chosen hybrid storage path |
| `B2_APPLICATION_KEY_ID` / `B2_APPLICATION_KEY` / `B2_BUCKET_NAME` / `B2_REGION` / `B2_ENDPOINT_URL` | Required only if B2 is actually used |
| `OPENROUTER_API_KEY` | Configure if OpenRouter is the selected AI route |
| `GROQ_API_KEY`, `GEMINI_API_KEY`, `MISTRAL_API_KEY`, `COHERE_API_KEY`, `NVIDIA_API_KEY`, `OPENAI_API_KEY` | Configure only the provider(s) intentionally used; unused keys can remain absent |
| `CLOUDFLARE_ACCOUNT_ID` / `CLOUDFLARE_API_TOKEN` | Required only for Cloudflare Workers AI; token must have minimum necessary permissions |
| `CLOUDFLARE_WHISPER_WORKER_URL` / `CLOUDFLARE_WHISPER_SHARED_SECRET` | Required only when remote Whisper is enabled and the Worker contract has been verified |
| `OAUTH_ENCRYPTION_KEY` | Generate/configure securely if encrypted OAuth credentials are used |
| `GOOGLE_CLIENT_ID` / `GOOGLE_CLIENT_SECRET` / `GOOGLE_REDIRECT_URI` | Required only for Google OAuth/Drive; redirect URI must exactly match provider configuration |
| `SMTP_HOST` / `SMTP_PORT` / `SMTP_USERNAME` / `SMTP_PASSWORD` / `SMTP_FROM_EMAIL` | Required only if outbound email is enabled |
| `STRIPE_SECRET_KEY` / `STRIPE_WEBHOOK_SECRET` / `STRIPE_PRICE_PRO` / `STRIPE_PRICE_BUSINESS` | Required only if billing is enabled |
| `SINGLE_USER_MODE` / `SINGLE_USER_EMAIL` | Confirm intended access mode; do not leave single-user mode enabled unintentionally |

## Render — frontend service

The checked-in blueprint builds the Next.js standalone output. Set these in the frontend service, not as backend secrets:

| Variable | Required value / action |
|---|---|
| `NEXT_PUBLIC_API_BASE_URL` | Actual public API URL plus `/api/v1` |
| `NEXT_PUBLIC_SUPABASE_URL` | URL of the confirmed canonical Supabase project, if frontend Supabase access is used |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | Public anon key only; never use the service-role key here |

The audit found a Render frontend service named `narrativ-forge-frontend`. Netlify is documented as a target, but the connected Netlify project was not verified as the Narrativ Forge site. Pick one canonical frontend deployment and configure DNS only after confirming ownership and build settings.

## Background worker

The checked-in `render.yaml` intentionally does not create a background worker. A live worker is therefore an explicit deployment dependency for long-running media jobs.

If/when a worker service is provisioned, configure the same confirmed `DATABASE_URL` and `REDIS_URL`, plus the required storage credentials and processing settings:

- `FFMPEG_BINARY`, `FFPROBE_BINARY`, `WHISPER_COMMAND`, `WHISPER_MODEL`
- `WORKER_MAX_CONCURRENCY`, `PROCESSING_TIMEOUT_SECONDS`, `PROCESSING_TIMEOUT_GRACE_SECONDS`
- Storage provider credentials required by the chosen storage path
- Whisper/AI provider configuration required by the actual job pipeline

Do not mark background processing verified until a real worker heartbeat and a successful queued job have been observed.

## Cloudflare Workers

Set Worker-specific values in the relevant Worker dashboard/Wrangler configuration, not blindly in every Render service. Review the actual source/config for each Worker before adding variables. Expected configuration may include:

- Whisper Worker: allowed origin and its authentication/shared-secret configuration.
- Edge Worker: API origin and the intended route/domain.
- Workers AI: account ID, API token, and model settings if that feature is used.

Never print secret values in logs or audit documents. Confirm routes, deployed version, and a safe authenticated smoke test.

## GitHub Actions

- [ ] Review workflow YAML to identify the secrets actually referenced.
- [ ] Configure `E2E_EMAIL` and `E2E_PASSWORD` only if the authenticated E2E workflow requires them.
- [ ] Add Cloudflare deploy credentials only if a workflow performs Worker deployment.
- [ ] Do not copy every Render runtime secret into GitHub Actions.

## Mobile / Expo

- [ ] Set `EXPO_PUBLIC_API_URL` to the real reachable API base URL for the production build.
- [ ] Never use localhost as the API hostname in a device build.
- [ ] Remember `EXPO_PUBLIC_*` values are bundled into the client and are not secrets.

## Security rules

- Never commit real credentials or production `.env` files.
- Never put service-role keys, database URLs, session secrets, or provider API keys into `NEXT_PUBLIC_*` or `EXPO_PUBLIC_*` variables.
- Remove example domains, dummy UUIDs, and `REPLACE_WITH_...` placeholders before production.
- Review Render's public IP allow-list (the infrastructure audit observed `0.0.0.0/0`) and ensure application authentication/rate limits are intentional.
- Do not blindly add permissive Supabase RLS policies or drop indexes based only on advisor warnings; review access paths and query plans first.

## Known external blockers from the last infrastructure audit

- Canonical frontend deployment/domain needs confirmation.
- Canonical database/Supabase project needs confirmation.
- Render services were observed behind repository main; auto-deploy was disabled.
- No separate continuous Render background worker was listed.
- Cloudflare Worker route/deployment/authenticated media behavior was not verified.

These are verification tasks, not values that can be safely guessed in this file.
