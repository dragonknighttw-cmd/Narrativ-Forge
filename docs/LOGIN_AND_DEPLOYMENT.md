# Narrativ Forge login and Render deployment checklist

## Where to sign in

Open the frontend login page:

- https://narrativ-forge-frontend.onrender.com/login

Use the email and password belonging to the invited Supabase Auth account. The application exchanges the Supabase access token with the backend and then sets an HTTP-only application session cookie. Do not share passwords or service-role keys in chat, issues, logs, or repository files.

## Important current-state note

The Render services were last inspected on 2026-10-16. Their dashboard settings still use the old `web-platform/backend` and `web-platform/frontend` paths, while the current repository paths are under `apps/web-platform/`. The services have auto-deploy disabled, and the deployed commits lag behind `main`. Therefore, the URL is the intended login location, but successful production login has not been verified.

This document and the Render blueprint changes do not deploy or modify live services.

## Required Render configuration

The blueprint declares these values as `sync: false`; set them in the Render dashboard for the matching service, without committing secrets:

### API service

- `APP_ENV=production`
- `DATABASE_URL` — the confirmed canonical production database only
- `SESSION_SECRET` — strong random secret, at least 32 characters
- `SESSION_COOKIE_SECURE=true`
- `OAUTH_ENCRYPTION_KEY` — valid Fernet key
- `CORS_ORIGINS=https://narrativ-forge-frontend.onrender.com`
- `TRUSTED_HOSTS=narrativ-forge.onrender.com`
- `FRONTEND_BASE_URL=https://narrativ-forge-frontend.onrender.com`
- `SUPABASE_URL`
- `SUPABASE_ANON_KEY`
- `SUPABASE_SERVICE_ROLE_KEY` — secret; never expose to the browser
- `SUPABASE_OWNER_USER_ID` and `SUPABASE_OWNER_EMAIL` — match the intended confirmed Supabase Auth owner identity
- Required storage provider credentials for the configured `STORAGE_PROVIDER`

### Frontend service

- `NEXT_PUBLIC_API_BASE_URL=https://narrativ-forge.onrender.com/api/v1`
- `NEXT_PUBLIC_SUPABASE_URL`
- `NEXT_PUBLIC_SUPABASE_ANON_KEY`

Only the Supabase URL and anon/publishable key belong in frontend build variables. Never put the Supabase service-role key in a `NEXT_PUBLIC_*` variable.

## Safe release sequence

1. Review and merge the code/configuration PRs only after required checks pass.
2. Confirm which Supabase project is canonical and confirm the Render database URL points to it; do not run migrations against an unconfirmed project.
3. Compare the existing Render services with `render.yaml` before syncing the blueprint. Confirm the service names match so syncing does not accidentally create duplicate services.
4. Set and verify required environment variables without exposing secret values.
5. Deploy to a preview/staging target first and verify `/api/v1/health`, Supabase login, first-owner provisioning, cookie persistence, and dashboard access.
6. Deploy production only after explicit approval and a tested rollback/backup plan.

## Login troubleshooting

- If the page is unavailable, check the frontend Render service status and build logs.
- If sign-in reports a generic failure, check frontend `NEXT_PUBLIC_SUPABASE_URL` and `NEXT_PUBLIC_SUPABASE_ANON_KEY`, API `SUPABASE_URL` and `SUPABASE_ANON_KEY`, API availability, CORS origin, and the configured owner UUID/email.
- The first Owner is provisioned only when the confirmed Supabase Auth UUID and email match the server-side configuration and the configured organization exists.
- Never disable email confirmation or weaken the owner UUID/email check to work around a login issue.
